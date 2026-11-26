import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from factsheet import FactSheet, load

EXAMPLE = Path(__file__).resolve().parents[1] / "renderer" / "examples" / "fact_sheet.json"
URL = "https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html"


def sheet(facts, display=None):
    return FactSheet.model_validate({"facts": facts, "display": display or {}})


def source(value):
    return {"value": value, "source": URL, "level": "measured data"}


def test_the_renderers_example_is_valid():
    fact_sheet = load(EXAMPLE)
    assert fact_sheet.display["jupiter_volume_ratio"] == "1,321"


def test_saved_json_has_the_same_shape_the_renderer_reads():
    fact_sheet = load(EXAMPLE)
    assert json.loads(fact_sheet.to_json()) == json.loads(EXAMPLE.read_text())


def test_a_value_changed_by_hand_is_caught():
    data = json.loads(EXAMPLE.read_text())
    data["facts"]["light_seconds"]["value"] = 480.0
    with pytest.raises(ValidationError, match="doesn't match its formula"):
        FactSheet.model_validate(data)


@pytest.mark.parametrize(
    ("fact", "message"),
    [
        ({"value": 1.0}, "a source link and a level, or a formula"),
        ({"value": 1.0, "source": URL}, "a source link and a level, or a formula"),
        ({**source(1.0), "formula": "a"}, "formula only"),
        ({"value": 1.0, "source": URL, "level": "news"}, "measured data"),
        ({"value": 1.0, "source": "nasa.gov", "level": "measured data"}, "pattern"),
        ({"value": float("inf"), "source": URL, "level": "measured data"}, "finite"),
        ({**source(1.0), "note": "extra"}, "Extra inputs"),
    ],
)
def test_bad_facts_are_refused(fact, message):
    with pytest.raises(ValidationError, match=message):
        sheet({"x": fact})


def test_a_formula_can_only_use_facts_listed_before_it():
    with pytest.raises(ValidationError, match='"b" is not a fact defined before this one'):
        sheet({"a": {"value": 2.0, "formula": "b * b"}, "b": source(1.0)})


def test_keys_must_work_as_renderer_placeholders():
    with pytest.raises(ValidationError, match="pattern"):
        sheet({"Earth-Sun": source(1.0)})
    with pytest.raises(ValidationError, match="pattern"):
        sheet({"a": source(1.0)}, {"Light Time": "8 minutes"})


def test_empty_display_text_is_refused():
    with pytest.raises(ValidationError, match="at least 1 character"):
        sheet({"a": source(1.0)}, {"a": ""})
