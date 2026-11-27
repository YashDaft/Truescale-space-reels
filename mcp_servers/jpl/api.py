"""Asks JPL's Solar System Dynamics API and caches the answers.

API documentation: https://ssd-api.jpl.nasa.gov/doc/
"""

from urllib.parse import urlencode

import httpx

from mcp_servers.cache import Cache

SBDB_URL = "https://ssd-api.jpl.nasa.gov/sbdb.api"  # Small-Body Database
CAD_URL = "https://ssd-api.jpl.nasa.gov/cad.api"  # Close-Approach Data


class JplError(Exception):
    pass


def fetch(base_url: str, params: dict, cache: Cache) -> dict:
    """Returns {"url", "fetched_at", "data"} for a query, from the cache if it's fresh."""
    url = f"{base_url}?{urlencode(params)}"
    cached = cache.get(url)
    if cached is not None:
        return cached

    try:
        response = httpx.get(url, timeout=30)
    except httpx.HTTPError as error:
        raise JplError(f"Couldn't reach JPL: {error}") from None

    # 300 is how the SBDB answers "several objects match", with a list of them
    if response.status_code not in (200, 300):
        raise JplError(f"JPL answered with HTTP {response.status_code} for {url}")
    data = response.json()

    # Answers that are only an error message (like "not found") have no
    # signature. They aren't cached, so a newly found object shows up at once.
    if "signature" not in data:
        return {"url": url, "fetched_at": None, "data": data}

    # JPL asks clients to check the version, as the format may change.
    # A new major version could mean the numbers are read wrongly, so stop.
    version = data["signature"].get("version", "")
    if not version.startswith("1."):
        raise JplError(f"JPL's API is now version {version}; this server was written for version 1")

    return cache.put(url, data)
