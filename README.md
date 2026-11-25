# Truescale

Space reels where every number is checked against official sources before it reaches the screen.

You give it a topic. Agents research the facts from sources like NASA's fact sheets, write short on-screen text, and lay out a storyboard from a library of animated scenes. The text is checked against the sources, the reel is rendered, and you approve it before it's posted. No voiceover: animation, text, sound effects and music.

Work in progress.

## How it's built

| Part | Status |
|---|---|
| `renderer/`: storyboard + fact sheet → video (Remotion, Three.js), with validation | Done |
| Fact sheet builder and schema (Python) | Next |
| MCP servers for each data source | Planned |
| LangGraph pipeline: research → fact sheet → text → storyboard → verify → render → review | Planned |
| Langfuse tracing and an evaluation of how many planted errors the checks catch | Planned |

Design decisions and the reasons for them are in [docs/decisions.md](docs/decisions.md).

## License

Apache 2.0. See [LICENSE](LICENSE).
