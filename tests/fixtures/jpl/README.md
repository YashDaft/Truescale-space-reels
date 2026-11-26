# JPL test answers

Real answers from JPL's API, saved on 26 Nov 2026 so the tests don't need the network. Only the formatting was changed (indented), with one exception: the long reference list in the rotation period's `notes` in `sbdb_eros.json` was shortened.

| File | Query |
|---|---|
| `sbdb_eros.json` | `sbdb.api?sstr=Eros&phys-par=1&full-prec=1` |
| `sbdb_141p_several.json` | `sbdb.api?sstr=141P&phys-par=1` (HTTP 300: several objects match) |
| `sbdb_not_found.json` | `sbdb.api?sstr=notarealasteroidxyz&phys-par=1` |
| `cad_close_approaches.json` | `cad.api?dist-max=10LD&date-min=2026-11-26&date-max=2027-01-31&diameter=true&fullname=true` |
