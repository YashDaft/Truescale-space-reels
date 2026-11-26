import json

from mcp_servers.cache import Cache

URL = "https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=Eros"


def test_returns_what_was_saved(tmp_path):
    cache = Cache(tmp_path, max_age_seconds=60)
    saved = cache.put(URL, {"answer": 1})

    record = cache.get(URL)
    assert record == saved
    assert record["url"] == URL
    assert record["data"] == {"answer": 1}
    assert record["fetched_at"].endswith("+00:00")  # UTC


def test_unknown_url_is_a_miss(tmp_path):
    assert Cache(tmp_path, max_age_seconds=60).get(URL) is None


def test_old_answers_are_not_used(tmp_path):
    cache = Cache(tmp_path, max_age_seconds=60)
    cache.put(URL, {"answer": 1})
    # Make the saved answer two days old
    path = next(tmp_path.iterdir())
    record = json.loads(path.read_text())
    record["fetched_at"] = "2020-01-01T00:00:00+00:00"
    path.write_text(json.dumps(record))

    assert cache.get(URL) is None
