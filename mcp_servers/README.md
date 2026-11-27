# MCP servers

Each server wraps one family of official data sources and gives agents tools that return **source facts**: numbers copied from the source by code, each with its link and level, ready for the fact sheet builder.

```python
builder.add_source_fact(fact["key"], fact["value"], fact["source"], fact["level"])
```

## jpl: asteroids and comets from NASA/JPL

Uses JPL's [Solar System Dynamics API](https://ssd-api.jpl.nasa.gov/doc/), which returns JSON. No key is needed.

| Tool | What it returns |
|---|---|
| `small_body(name)` | One asteroid or comet from the [Small-Body Database](https://ssd-api.jpl.nasa.gov/doc/sbdb.html): its orbit (size of orbit, period, closest possible distance to Earth's orbit…) and physical data (diameter, rotation period, albedo…). |
| `close_approaches(date_min, date_max, max_distance_ld=10)` | Asteroids and comets passing Earth between two dates, from [Close-Approach Data](https://ssd-api.jpl.nasa.gov/doc/cad.html). |

Each fact looks like this:

```json
{
  "key": "433_eros_diameter",
  "value": 16.84,
  "unit": "km",
  "title": "diameter",
  "uncertainty": 0.06,
  "reference": "Yeomans et al. (2000) Science v.289,pp.2085-2088",
  "source": "https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=Eros&phys-par=1&full-prec=1",
  "level": "measured data"
}
```

Values that aren't a single number, such as a shape (`34.4x11.2x11.2`) or a spectral type (`S`), come back separately in `text_values`.

If a name matches several objects, the tool answers with an error that lists them, so the agent can ask again with one designation.

### Running it

```bash
uv run python -m mcp_servers.jpl
```

To try it in Claude Desktop, add this to its MCP settings, with your own path to the repo:

```json
{
  "mcpServers": {
    "truescale-jpl": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/Truescale-space-reels", "python", "-m", "mcp_servers.jpl"]
    }
  }
}
```

### Cache

Answers are saved in `.cache/jpl/` at the top of the repo, with the URL and the time they were fetched: small-body data for 7 days, close approaches for 1 day. Answers that are only an error message, like "not found", aren't saved.
