"""Reading JPL's answers. The fixtures are real answers saved from the API in November 2026."""

import json
from pathlib import Path

import pytest

from factsheet import FactSheetBuilder
from mcp_servers.jpl import parse
from mcp_servers.jpl.api import JplError

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "jpl"
SBDB_URL = "https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=Eros&phys-par=1&full-prec=1"
CAD_URL = "https://ssd-api.jpl.nasa.gov/cad.api?dist-max=10LD&date-min=2026-11-26&date-max=2027-01-31&diameter=true&fullname=true"


def record(fixture, url):
    data = json.loads((FIXTURES / fixture).read_text())
    return {"url": url, "fetched_at": "2026-11-26T12:00:00+00:00", "data": data}


def facts_by_key(result):
    return {fact["key"]: fact for fact in result["facts"]}


def test_eros_physical_facts():
    eros = parse.small_body(record("sbdb_eros.json", SBDB_URL))
    assert eros["name"] == "433 Eros"
    assert eros["orbit_class"] == "Amor"
    assert eros["near_earth_object"] is True

    diameter = facts_by_key(eros)["433_eros_diameter"]
    assert diameter == {
        "key": "433_eros_diameter",
        "value": 16.84,
        "unit": "km",
        "title": "diameter",
        "uncertainty": 0.06,
        "reference": "Yeomans et al. (2000) Science v.289,pp.2085-2088",
        "source": SBDB_URL,
        "level": "measured data",
    }
    assert facts_by_key(eros)["433_eros_rot_per"]["value"] == 5.27


def test_eros_orbit_facts_at_full_precision():
    facts = facts_by_key(parse.small_body(record("sbdb_eros.json", SBDB_URL)))
    assert facts["433_eros_a"]["value"] == 1.458243716760167
    assert facts["433_eros_e"]["value"] == 0.2228779627700761  # sent by JPL as ".2228779627700761"
    assert facts["433_eros_per"]["unit"] == "d"
    assert facts["433_eros_moid"]["value"] == 0.148798


def test_values_that_are_not_one_number_are_kept_as_text():
    eros = parse.small_body(record("sbdb_eros.json", SBDB_URL))
    assert eros["text_values"]["extent"] == "34.4x11.2x11.2"
    assert eros["text_values"]["spec_T"] == "S"
    assert "433_eros_extent" not in facts_by_key(eros)


def test_several_matches_are_listed():
    with pytest.raises(JplError, match=r"Several objects match: 141P \(141P/Machholz 2\), 141P-A"):
        parse.small_body(record("sbdb_141p_several.json", SBDB_URL))


def test_not_found():
    with pytest.raises(JplError, match="specified object was not found"):
        parse.small_body(record("sbdb_not_found.json", SBDB_URL))


def test_close_approaches():
    result = parse.close_approaches(record("cad_close_approaches.json", CAD_URL))
    assert result["count"] == 12

    first = result["approaches"][0]
    assert first["designation"] == "2026 VQ19"
    assert first["name"] == "(2026 VQ19)"  # JPL pads names with spaces
    assert first["time_tdb"] == "2026-Nov-26 10:15"
    facts = facts_by_key(first)
    assert facts["2026_vq19_20261126_dist"]["value"] == 0.0101245921477465
    assert facts["2026_vq19_20261126_v_rel"]["unit"] == "km/s"
    assert facts["2026_vq19_20261126_dist"]["source"] == CAD_URL
    # No measured diameter for this one, so there is no diameter fact
    assert "2026_vq19_20261126_diameter" not in facts


def test_no_approaches():
    empty = {"signature": {"version": "1.5", "source": "NASA/JPL SBDB Close Approach Data API"}, "count": 0}
    result = parse.close_approaches({"url": CAD_URL, "fetched_at": None, "data": empty})
    assert result["count"] == 0
    assert result["approaches"] == []


def test_every_fact_goes_into_a_fact_sheet_as_it_is():
    # The facts' shape must fit the fact sheet builder without any changes
    builder = FactSheetBuilder()
    eros = parse.small_body(record("sbdb_eros.json", SBDB_URL))
    approaches = parse.close_approaches(record("cad_close_approaches.json", CAD_URL))
    facts = eros["facts"] + [fact for approach in approaches["approaches"] for fact in approach["facts"]]
    for fact in facts:
        builder.add_source_fact(fact["key"], fact["value"], fact["source"], fact["level"])

    sheet = builder.build()
    assert len(sheet.facts) == len(facts)
    assert sheet.facts["433_eros_diameter"].value == 16.84


@pytest.mark.parametrize(
    ("text", "expected"),
    [(".2228", 0.2228), ("4.463e-04", 4.463e-04), ("S", None), ("34.4x11.2x11.2", None), (None, None), ("nan", None)],
)
def test_number(text, expected):
    assert parse.number(text) == expected


def test_make_key():
    assert parse.make_key("433 Eros") == "433_eros"
    assert parse.make_key("141P/Machholz 2") == "141p_machholz_2"
    assert parse.make_key("BV") == "bv"
