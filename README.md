# Truescale

Space reels where every number is checked against official sources before it reaches the screen.

You give it a topic. Agents research the facts from sources like NASA's fact sheets, write short on-screen text, and lay out a storyboard from a library of animated scenes. The text is checked against the sources, the reel is rendered, and you approve it before it's posted. No voiceover: animation, text, sound effects and music.

Work in progress.

## How it's built

| Part | Status |
|---|---|
| `renderer/`: storyboard + fact sheet → video (Remotion, Three.js), with validation | Done |
| `factsheet/`: fact sheet schema and builder (Python, Pydantic), with tests | Done |
| MCP server for NASA's planetary fact sheets | Next |
| MCP servers for the other data sources | Planned |
| LangGraph pipeline: research → fact sheet → text → storyboard → verify → render → review | Planned |
| Langfuse tracing and an evaluation of how many planted errors the checks catch | Planned |

Design decisions and the reasons for them are in [docs/decisions.md](docs/decisions.md).

## Running the Python tests

You need [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pytest
```

How to run the renderer is in [renderer/README.md](renderer/README.md).

## License

Copyright (c) 2026 Yash Daftari. All rights reserved.

The code is public to read, but it isn't licensed for reuse. Please ask if you'd like to use any of it.
