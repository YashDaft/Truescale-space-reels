# Decisions

Each entry: what was decided, what else was considered, and why.

## 1. The AI can't type numbers

**Decided:** On-screen text may only contain numbers through `{placeholders}` that point at the fact sheet. Text with a typed digit is refused before rendering.

**Considered:** Letting the model write numbers and checking them afterwards against the sources.

**Why:** Checking afterwards depends on the checker catching every mistake. Making typed numbers impossible removes the whole class of mistake. The fact sheet's numbers are copied from sources or worked out by code, never by a model. The same applies inside scenes: animated numbers such as counters and lap counts are calculated by code from the fact sheet's values.

## 2. Agents choose and fill in scenes; they don't write animation code

**Decided:** Animation code is written once per scene and reviewed. A storyboard only picks scenes from `scene_catalog.json` and fills in their settings.

**Considered:** Having a model write new Remotion code for every reel, as many "AI reel" tools do.

**Why:** Generated code can break or draw something wrong in a different way every time, and the visuals couldn't be checked. Fixed scenes with known settings can be checked; for example, `volume_fill` provably draws Jupiter at its real size ratio. Variety comes from combining scenes and adding new ones.

## 3. Scenes and styles are separate

**Decided:** A scene decides what is drawn. A style decides how text looks and moves, and can add an overlay such as film grain.

**Why:** More styles are planned. Keeping text and overlays out of the scenes means a new style doesn't require rewriting every scene.

## 4. The renderer receives its data instead of containing it

**Decided:** The storyboard and fact sheet are passed in as one JSON file (`--props`). The examples are just files.

**Why:** The Python pipeline will write these files and call the renderer. The renderer stays a tool that knows nothing about any particular reel.

## 5. One catalog for both sides

**Decided:** `scene_catalog.json` describes every scene, style, sound and parameter rule. The renderer validates against it, and the storyboard agent will read it to know what it can use.

**Why:** One source of truth, so the agent can't be told about a scene the renderer doesn't have. On startup the renderer also checks that the catalog and the code list the same scenes and styles.

## 6. Every problem is reported at once

**Decided:** The validator collects all problems before failing.

**Why:** The pipeline will send these errors back to the agent to fix. Getting all of them at once means one retry instead of one per mistake.

## 7. Cinematic pictures aren't to scale

**Decided:** The cinematic style shows mood, not proportions; its numbers live in the text. The flat and line styles are drawn to scale.

**Why:** A to-scale Sun-to-Earth flight would show nothing but black for most of the video. Saying this openly is better than implying an accuracy the picture doesn't have.

## 8. Langfuse for tracing and evaluation

**Decided:** Langfuse, self-hosted, rather than LangSmith.

**Considered:** LangSmith, already used in an earlier project.

**Why:** It's open source and can run locally in Docker, it isn't tied to one framework (it builds on OpenTelemetry), and it covers tracing, cost per reel, datasets and experiments. Using it here also adds a second tool to the portfolio.
