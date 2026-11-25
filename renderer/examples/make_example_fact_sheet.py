"""Builds examples/fact_sheet.json, the fact sheet used by the example reels.

This is a stand-in until the Python pipeline builds fact sheets itself.
Source values are copied by hand from NASA's fact sheets, with a link to each.
Every other number is worked out here by code, and its formula is saved with it.

Run from the renderer folder:  python3 examples/make_example_fact_sheet.py
"""

import json
from pathlib import Path

EARTH_URL = "https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html"
JUPITER_URL = "https://nssdc.gsfc.nasa.gov/planetary/factsheet/jupiterfact.html"
PLANETS_URL = "https://nssdc.gsfc.nasa.gov/planetary/factsheet/index.html"
SPEED_OF_LIGHT_URL = "https://physics.nist.gov/cgi-bin/cuu/Value?c"

facts = {}


def source_fact(key, value, url):
    """A number copied from an official source."""
    facts[key] = {"value": value, "source": url, "level": "measured data"}


def worked_out(key, value, formula):
    """A number calculated from source facts."""
    facts[key] = {"value": value, "formula": formula}


# --- Source facts (checked by hand on 24-25 Nov 2026) ---
source_fact("earth_sun_km", 149.598e6, EARTH_URL)  # Earth's semimajor axis
source_fact("speed_of_light_km_s", 299792.458, SPEED_OF_LIGHT_URL)  # exact by definition
source_fact("jupiter_volume_ratio", 1321.33, JUPITER_URL)  # Jupiter volume / Earth volume
source_fact("jupiter_radius_ratio", 10.973, JUPITER_URL)  # Jupiter mean radius / Earth mean radius

planets = {
    "mercury": {"period_days": 88.0, "distance_mkm": 57.9},
    "venus": {"period_days": 224.7, "distance_mkm": 108.2},
    "earth": {"period_days": 365.2, "distance_mkm": 149.6},
    "mars": {"period_days": 687.0, "distance_mkm": 228.0},
}
for name, planet in planets.items():
    source_fact(f"{name}_period_days", planet["period_days"], PLANETS_URL)
    source_fact(f"{name}_distance_mkm", planet["distance_mkm"], PLANETS_URL)

# --- Worked out by code ---
light_seconds = facts["earth_sun_km"]["value"] / facts["speed_of_light_km_s"]["value"]
worked_out("light_seconds", light_seconds, "earth_sun_km / speed_of_light_km_s")

mercury_laps = planets["earth"]["period_days"] / planets["mercury"]["period_days"]
worked_out("mercury_laps", mercury_laps, "earth_period_days / mercury_period_days")

mars_share = planets["earth"]["period_days"] / planets["mars"]["period_days"]
worked_out("mars_share", mars_share, "earth_period_days / mars_period_days")

# --- Ready-to-show text, so the video never rounds a number itself ---
minutes, seconds = divmod(round(light_seconds), 60)
display = {
    "light_time": f"{minutes} minutes {seconds} seconds",
    "earth_sun_mkm": f"{facts['earth_sun_km']['value'] / 1e6:.1f} million km",
    "jupiter_volume_ratio": f"{facts['jupiter_volume_ratio']['value']:,.0f}",
    "mercury_laps": f"{int(mercury_laps)} laps",
    "mars_share": f"{mars_share * 100:.0f}%",
}

out = Path(__file__).resolve().parent / "fact_sheet.json"
out.write_text(json.dumps({"facts": facts, "display": display}, indent=2) + "\n")
print(json.dumps(display, indent=2))
