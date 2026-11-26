"""The JPL MCP server: asteroid and comet facts from NASA/JPL.

Run it with:  uv run python -m mcp_servers.jpl
"""

from datetime import date
from pathlib import Path
from typing import Annotated

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

from mcp_servers.cache import Cache
from mcp_servers.jpl import parse
from mcp_servers.jpl.api import CAD_URL, SBDB_URL, JplError, fetch

DAY = 24 * 60 * 60
CACHE_FOLDER = Path(__file__).resolve().parents[2] / ".cache" / "jpl"

# Orbits and sizes change rarely. Close approaches change as new asteroids are found.
sbdb_cache = Cache(CACHE_FOLDER / "sbdb", max_age_seconds=7 * DAY)
cad_cache = Cache(CACHE_FOLDER / "cad", max_age_seconds=1 * DAY)

server = MCPServer(
    "truescale-jpl",
    instructions=(
        "Facts about asteroids and comets from NASA/JPL. Every fact has a key, a value, "
        "a unit, a source link and a level, ready to copy into a fact sheet. "
        "Copy values exactly; never round or retype them."
    ),
)

Day = Annotated[date, Field(description="A date, YYYY-MM-DD")]


@server.tool()
def small_body(
    name: Annotated[str, Field(min_length=1, description='A name ("Eros"), number ("433") or designation ("2015 AB")')],
) -> dict:
    """One asteroid or comet from JPL's Small-Body Database: its orbit and physical data,
    such as diameter, rotation period and albedo. If several objects match, the error
    lists them; ask again with one of their designations."""
    try:
        record = fetch(SBDB_URL, {"sstr": name, "phys-par": 1, "full-prec": 1}, sbdb_cache)
        return parse.small_body(record)
    except JplError as error:
        raise ToolError(str(error)) from None


@server.tool()
def close_approaches(
    date_min: Day,
    date_max: Day,
    max_distance_ld: Annotated[
        float, Field(gt=0, le=100, description="Only approaches closer than this, in lunar distances (Earth-Moon distances)")
    ] = 10,
) -> dict:
    """Asteroids and comets passing close to Earth between two dates (at most a year apart),
    from JPL's Close-Approach Data."""
    if date_max < date_min:
        raise ToolError("date_max is before date_min")
    if (date_max - date_min).days > 366:
        raise ToolError("Ask for at most a year at a time")
    params = {
        "dist-max": f"{max_distance_ld:g}LD",
        "date-min": date_min.isoformat(),
        "date-max": date_max.isoformat(),
        "diameter": "true",
        "fullname": "true",
    }
    try:
        return parse.close_approaches(fetch(CAD_URL, params, cad_cache))
    except JplError as error:
        raise ToolError(str(error)) from None
