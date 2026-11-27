"""The JPL server as an agent sees it: through an MCP client. JPL itself is replaced by saved answers."""

import asyncio
import json
from pathlib import Path

import pytest
from mcp.client import Client

from mcp_servers.cache import Cache
from mcp_servers.jpl import api, server

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "jpl"


class FakeResponse:
    def __init__(self, fixture, status_code=200):
        self.status_code = status_code
        self._data = json.loads((FIXTURES / fixture).read_text())

    def json(self):
        return self._data


@pytest.fixture
def jpl(monkeypatch, tmp_path):
    """Answers JPL calls from saved files and records which URLs were asked for."""
    asked = []
    answers = {}

    def fake_get(url, timeout):
        asked.append(url)
        for start, response in answers.items():
            if url.startswith(start):
                return response
        raise AssertionError(f"unexpected URL {url}")

    monkeypatch.setattr(api.httpx, "get", fake_get)
    monkeypatch.setattr(server, "sbdb_cache", Cache(tmp_path / "sbdb", max_age_seconds=60))
    monkeypatch.setattr(server, "cad_cache", Cache(tmp_path / "cad", max_age_seconds=60))
    return answers, asked


def call(tool, arguments):
    async def run():
        async with Client(server.server) as client:
            return await client.call_tool(tool, arguments)

    return asyncio.run(run())


def result_json(result):
    assert not result.is_error, result.content[0].text
    return json.loads(result.content[0].text)


def test_lists_both_tools():
    async def run():
        async with Client(server.server) as client:
            return await client.list_tools()

    assert sorted(tool.name for tool in asyncio.run(run()).tools) == ["close_approaches", "small_body"]


def test_small_body(jpl):
    answers, asked = jpl
    answers[api.SBDB_URL] = FakeResponse("sbdb_eros.json")

    eros = result_json(call("small_body", {"name": "Eros"}))

    assert asked == ["https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=Eros&phys-par=1&full-prec=1"]
    assert eros["name"] == "433 Eros"
    assert eros["fetched_at"] is not None


def test_second_ask_comes_from_the_cache(jpl):
    answers, asked = jpl
    answers[api.SBDB_URL] = FakeResponse("sbdb_eros.json")

    first = result_json(call("small_body", {"name": "Eros"}))
    second = result_json(call("small_body", {"name": "Eros"}))

    assert len(asked) == 1
    assert second == first


def test_not_found_answers_are_not_cached(jpl):
    answers, asked = jpl
    answers[api.SBDB_URL] = FakeResponse("sbdb_not_found.json")

    call("small_body", {"name": "notarealasteroidxyz"})
    result = call("small_body", {"name": "notarealasteroidxyz"})

    assert result.is_error
    assert "not found" in result.content[0].text
    assert len(asked) == 2


def test_several_matches_come_back_as_an_error_the_agent_can_act_on(jpl):
    answers, _ = jpl
    answers[api.SBDB_URL] = FakeResponse("sbdb_141p_several.json", status_code=300)

    result = call("small_body", {"name": "141P"})

    assert result.is_error
    assert "Ask again with one of these designations" in result.content[0].text


def test_jpl_failure_is_an_error(jpl):
    answers, _ = jpl
    answers[api.SBDB_URL] = FakeResponse("sbdb_not_found.json", status_code=503)

    result = call("small_body", {"name": "Eros"})

    assert result.is_error
    assert "HTTP 503" in result.content[0].text


def test_a_new_api_version_is_refused(jpl):
    answers, _ = jpl
    response = FakeResponse("sbdb_eros.json")
    response._data["signature"]["version"] = "2.0"
    answers[api.SBDB_URL] = response

    result = call("small_body", {"name": "Eros"})

    assert result.is_error
    assert "version 2.0" in result.content[0].text


def test_close_approaches(jpl):
    answers, asked = jpl
    answers[api.CAD_URL] = FakeResponse("cad_close_approaches.json")

    result = result_json(call("close_approaches", {"date_min": "2026-11-26", "date_max": "2027-01-31"}))

    assert asked == [
        "https://ssd-api.jpl.nasa.gov/cad.api?dist-max=10LD&date-min=2026-11-26&date-max=2027-01-31&diameter=true&fullname=true"
    ]
    assert result["count"] == 12


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ({"date_min": "2027-01-01", "date_max": "2026-01-01"}, "before date_min"),
        ({"date_min": "2026-01-01", "date_max": "2028-01-01"}, "at most a year"),
        ({"date_min": "next week", "date_max": "2027-01-01"}, "date_min"),
        ({"date_min": "2026-01-01", "date_max": "2026-02-01", "max_distance_ld": 0}, "max_distance_ld"),
    ],
)
def test_bad_close_approach_questions_are_refused(jpl, arguments, message):
    _, asked = jpl
    result = call("close_approaches", arguments)

    assert result.is_error
    assert message in result.content[0].text
    assert asked == []
