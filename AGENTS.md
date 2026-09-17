# AGENTS.md

For agents that read this file instead of Claude Code's plugin manifest (Codex,
Cursor, Copilot and similar). The content lives in one place; this file only
says where.

## What to read

- `skills/manimgl-video/SKILL.md` — the instructions. Read it in full before
  writing any ManimGL code. It disambiguates ManimGL from Manim Community
  Edition, sets the workflow, and lists the footguns.
- `skills/manimgl-video/references/` — open on demand, as SKILL.md's table says:
  `api-core.md`, `api-graphs.md`, `animations.md`, `cli-config.md`, `patterns.md`.
- `skills/manimgl-video/assets/` — runnable scripts, all stdlib-only:
  `doctor.py` (environment check, `--write-config`), `snapshot.py` (frame PNGs
  at chosen animation indices), `smoke_test.py`, `equation_graph.py`,
  `templates/` (project `common.py` and `CLAUDE.md`).

## To use it in another project

Copy `skills/manimgl-video/` next to that project, or reference it by absolute
path, and add to the project's own AGENTS.md:

```
ManimGL work: follow <path>/skills/manimgl-video/SKILL.md.
Before handing over a scene, run <path>/skills/manimgl-video/assets/snapshot.py
on it and look at the frames.
```

`commands/init.md` describes the project scaffold as a Claude Code command;
the five steps in it are plain shell and file operations and apply to any agent.

## Do not

- Use `from manim import *`, `Create`, `MathTex`, or any other Manim CE name.
  The two libraries share class names with different meanings.
- Paste scenes from `3b1b/videos` (CC BY-NC-SA, not standalone). Write fresh
  code against the API.
