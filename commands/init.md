---
description: Scaffold a ManimGL explainer project in the current directory — custom_config.yml, helpers, CLAUDE.md
argument-hint: '[project description, e.g. "Fourier series explainer in Korean"]'
---

Set up the current directory as a ManimGL (3Blue1Brown's Manim, `from manimlib
import *`) explainer project. Do not run this in a Manim Community Edition
project (`from manim import *`).

Locate the skill's assets directory first: it is `skills/manimgl-video/assets/`
under this plugin's root (the directory containing `.claude-plugin/plugin.json`).
Call it `$ASSETS` below.

1. **Environment.** Run `python $ASSETS/doctor.py --write-config`. If a
   `custom_config.yml` already exists, run without `--write-config` and report the
   result instead of overwriting. Show the user every FAIL line and its fix before
   continuing; a WARN about LaTeX means `Text`-only scenes until it is installed.

2. **Helpers.** Copy `$ASSETS/templates/common.py` to `./common.py` unless one
   exists. Every scene file imports `txt` and `tex` from it instead of calling
   `Text`/`Tex` directly.

3. **CLAUDE.md.** Write `./CLAUDE.md` from `$ASSETS/templates/CLAUDE.md`,
   filling in the project description from `$ARGUMENTS` (ask if empty) and the
   on-screen language (English unless the user said otherwise). If a CLAUDE.md
   exists, append the "ManimGL" section only.

4. **Ignore render output.** Append `videos/`, `frames/`, `images/`, `Tex/`,
   `__pycache__/` and `custom_config.yml` to `.gitignore` (create it if absent;
   skip lines already present).

5. **Prove it.** Run `python $ASSETS/snapshot.py $ASSETS/smoke_test.py SmokeTest 2`
   and open `frames/SmokeTest_002.png`. A title and three outlined shapes means
   the install renders. Remove `frames/` afterwards.

Report what was created and what was skipped. Do not write a scene yet — that
is the `manimgl-video` skill's job once the user describes one.
