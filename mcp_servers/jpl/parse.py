"""Turns JPL's answers into source facts for a fact sheet.

Every number is copied from JPL's answer by code. Each fact carries the API
link it came from and the level "measured data", ready for
FactSheetBuilder.add_source_fact(key, value, source, level).
"""

import math
import re
from datetime import datetime

from mcp_servers.jpl.api import JplError

LEVEL = "measured data"

CLOSE_APPROACH_FIELDS = {
    # field: (unit, title)
    "dist": ("au", "nominal distance from Earth at closest approach"),
    "dist_min": ("au", "smallest possible distance at closest approach (3-sigma)"),
    "dist_max": ("au", "largest possible distance at closest approach (3-sigma)"),
    "v_rel": ("km/s", "speed relative to Earth at closest approach"),
    "v_inf": ("km/s", "speed relative to Earth, ignoring Earth's gravity"),
    "h": (None, "absolute magnitude (brightness, a rough guide to size)"),
    "diameter": ("km", "diameter"),
}


def small_body(record: dict) -> dict:
    """Facts about one asteroid or comet, from an SBDB answer."""
    data = record["data"]
    if "list" in data:
        matches = ", ".join(f'{item["pdes"]} ({item["name"]})' for item in data["list"])
        raise JplError(f"Several objects match: {matches}. Ask again with one of these designations.")
    if "object" not in data:
        raise JplError(f"JPL: {data.get('message', 'no object in the answer')}")

    body = data["object"]
    name = body.get("shortname") or body["fullname"]
    prefix = make_key(name)
    facts = []
    text_values = {}

    def add(item: dict) -> None:
        value = number(item["value"])
        if value is None:
            # Not a single number, e.g. a shape "34.4x11.2x11.2" or a type "S"
            text_values[item["name"]] = item["value"]
            return
        facts.append(
            {
                "key": f"{prefix}_{make_key(item['name'])}",
                "value": value,
                "unit": item.get("units"),
                "title": item.get("title") or item["name"],
                "uncertainty": number(item.get("sigma")),
                "reference": item.get("ref"),
                "source": record["url"],
                "level": LEVEL,
            }
        )

    orbit = data.get("orbit", {})
    for element in orbit.get("elements", []):
        add(element)
    if orbit.get("moid") is not None:
        add({"name": "moid", "value": orbit["moid"], "units": "au", "title": "closest possible distance between its orbit and Earth's"})
    for parameter in data.get("phys_par", []):
        add(parameter)

    return {
        "name": name,
        "full_name": body["fullname"],
        "designation": body["des"],
        "orbit_class": body["orbit_class"]["name"],
        "near_earth_object": body["neo"],
        "potentially_hazardous": body["pha"],
        "source": record["url"],
        "fetched_at": record["fetched_at"],
        "facts": facts,
        "text_values": text_values,
    }


def close_approaches(record: dict) -> dict:
    """Close approaches to Earth, from a Close-Approach Data answer."""
    data = record["data"]
    fields = data.get("fields", [])
    approaches = []

    for row in data.get("data", []):
        item = dict(zip(fields, row))
        when = datetime.strptime(item["cd"], "%Y-%b-%d %H:%M")  # e.g. "2026-Dec-12 04:55"
        prefix = f"{make_key(item['des'])}_{when:%Y%m%d}"
        facts = []
        for field, (unit, title) in CLOSE_APPROACH_FIELDS.items():
            value = number(item.get(field))
            if value is None:  # e.g. most small asteroids have no measured diameter
                continue
            facts.append(
                {
                    "key": f"{prefix}_{field}",
                    "value": value,
                    "unit": unit,
                    "title": title,
                    "uncertainty": number(item.get("diameter_sigma")) if field == "diameter" else None,
                    "reference": None,
                    "source": record["url"],
                    "level": LEVEL,
                }
            )
        approaches.append(
            {
                "designation": item["des"],
                "name": (item.get("fullname") or item["des"]).strip(),
                "time_tdb": item["cd"],
                "time_uncertainty": item.get("t_sigma_f"),
                "facts": facts,
            }
        )

    return {
        "source": record["url"],
        "fetched_at": record["fetched_at"],
        "count": len(approaches),
        "approaches": approaches,
    }


def number(text) -> float | None:
    """JPL sends numbers as text, e.g. ".2228" or "4.463e-04". None if it isn't one number."""
    if text is None:
        return None
    try:
        value = float(text)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def make_key(text: str) -> str:
    """A fact-sheet key from a name, e.g. "433 Eros" -> "433_eros", "rot_per" -> "rot_per"."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
