import json
import subprocess
import sys
from pathlib import Path

import pytest

from factsheet import FactSheetBuilder, FactSheetError, load

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "renderer" / "examples" / "fact_sheet.json"
URL = "https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html"


def test_builds_a_fact_sheet():
    builder = FactSheetBuilder()
    builder.add_source_fact("earth_sun_km", 149.598e6, URL, "measured data")
    builder.add_source_fact("speed_of_light_km_s", 299792.458, URL, "measured data")
    builder.add_worked_out("light_seconds", "earth_sun_km / speed_of_light_km_s")
    builder.add_display("light_time", "light_seconds", format="minutes_seconds")

    fact_sheet = builder.build()

    light = fact_sheet.facts["light_seconds"]
    assert light.value == 149.598e6 / 299792.458
    assert light.formula == "earth_sun_km / speed_of_light_km_s"
    assert light.source is None
    assert fact_sheet.display == {"light_time": "8 minutes 19 seconds"}


def test_every_problem_is_reported_at_once():
    builder = FactSheetBuilder()
    builder.add_source_fact("a", 1.0, URL, "rumour")  # not a level
    builder.add_source_fact("b", 2.0, URL, "measured data")
    builder.add_source_fact("b", 3.0, URL, "measured data")  # added twice
    builder.add_source_fact("Bad-Key", 1.0, URL, "measured data")
    builder.add_worked_out("c", "b * 2")  # typed number
    builder.add_worked_out("d", "b / missing")
    builder.add_display("e", "missing")
    builder.add_display("f", "b", unit="km in 2024")  # number in the unit

    with pytest.raises(FactSheetError) as caught:
        builder.build()

    problems = caught.value.problems
    assert len(problems) == 7
    assert "The fact sheet has 7 problem(s)" in str(caught.value)
    expected = [
        "a, level",
        '"b" was added twice',
        '"Bad-Key": a key may only use',
        "c: the number 2 is typed into the formula",
        'd: "missing" is not a fact defined before this one',
        'e: "missing" is not in the fact sheet',
        'f: Value error, the unit "km in 2024" contains a number',
    ]
    for problem, start in zip(problems, expected):
        assert problem.startswith(start), problem


def test_save_writes_json_the_schema_accepts(tmp_path):
    builder = FactSheetBuilder()
    builder.add_source_fact("jupiter_volume_ratio", 1321.33, URL, "measured data")
    builder.add_display("jupiter_volume_ratio", "jupiter_volume_ratio")

    out = tmp_path / "fact_sheet.json"
    builder.save(out)

    assert load(out).display == {"jupiter_volume_ratio": "1,321"}


def test_example_script_rebuilds_the_renderers_fact_sheet_exactly(tmp_path):
    # The renderer's examples use this file, so the Python side and the
    # renderer side must agree on it to the byte.
    out = tmp_path / "fact_sheet.json"
    subprocess.run(
        [sys.executable, str(ROOT / "renderer" / "examples" / "make_example_fact_sheet.py"), str(out)],
        check=True,
        capture_output=True,
    )
    assert out.read_text() == EXAMPLE.read_text()
    assert json.loads(out.read_text())["display"]["light_time"] == "8 minutes 19 seconds"
