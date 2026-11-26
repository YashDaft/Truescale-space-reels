"""Builds examples/fact_sheet.json, the fact sheet used by the example reels.

Source values are copied by hand from NASA's fact sheets, with a link to each.
Every other number, and all the text that shows numbers on screen, is worked
out by the fact sheet builder (factsheet/ at the top of the repo).

Run from the top of the repo:
    uv run python renderer/examples/make_example_fact_sheet.py
An optional path writes the file somewhere else (the tests use this).
"""

import json
import sys
from pathlib import Path

from factsheet import FactSheetBuilder

EARTH_URL = "https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html"
JUPITER_URL = "https://nssdc.gsfc.nasa.gov/planetary/factsheet/jupiterfact.html"
PLANETS_URL = "https://nssdc.gsfc.nasa.gov/planetary/factsheet/index.html"
SPEED_OF_LIGHT_URL = "https://physics.nist.gov/cgi-bin/cuu/Value?c"
MEASURED = "measured data"


def build() -> FactSheetBuilder:
    sheet = FactSheetBuilder()

    # --- Source facts (checked by hand on 24-25 Nov 2026) ---
    sheet.add_source_fact("earth_sun_km", 149.598e6, EARTH_URL, MEASURED)  # Earth's semimajor axis
    sheet.add_source_fact("speed_of_light_km_s", 299792.458, SPEED_OF_LIGHT_URL, MEASURED)  # exact by definition
    sheet.add_source_fact("jupiter_volume_ratio", 1321.33, JUPITER_URL, MEASURED)  # Jupiter volume / Earth volume
    sheet.add_source_fact("jupiter_radius_ratio", 10.973, JUPITER_URL, MEASURED)  # Jupiter mean radius / Earth mean radius

    planets = {
        "mercury": {"period_days": 88.0, "distance_mkm": 57.9},
        "venus": {"period_days": 224.7, "distance_mkm": 108.2},
        "earth": {"period_days": 365.2, "distance_mkm": 149.6},
        "mars": {"period_days": 687.0, "distance_mkm": 228.0},
    }
    for name, planet in planets.items():
        sheet.add_source_fact(f"{name}_period_days", planet["period_days"], PLANETS_URL, MEASURED)
        sheet.add_source_fact(f"{name}_distance_mkm", planet["distance_mkm"], PLANETS_URL, MEASURED)

    # --- Worked out by code ---
    sheet.add_worked_out("light_seconds", "earth_sun_km / speed_of_light_km_s")
    sheet.add_worked_out("mercury_laps", "earth_period_days / mercury_period_days")
    sheet.add_worked_out("mars_share", "earth_period_days / mars_period_days")

    # --- Ready-to-show text, so the video never rounds a number itself ---
    sheet.add_display("light_time", "light_seconds", format="minutes_seconds")
    sheet.add_display("earth_sun_mkm", "earth_sun_km", decimals=1, scale="million", unit="km")
    sheet.add_display("jupiter_volume_ratio", "jupiter_volume_ratio")
    sheet.add_display("mercury_laps", "mercury_laps", format="count", unit="laps")
    sheet.add_display("mars_share", "mars_share", format="percent")

    return sheet


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "fact_sheet.json"
    fact_sheet = build().save(out)
    print(json.dumps(fact_sheet.display, indent=2))
