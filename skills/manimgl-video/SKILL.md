---
name: manimgl-video
description: >-
  Writes math explainer animation code with ManimGL — 3Blue1Brown's own Manim
  (`pip install manimgl`, `from manimlib import *`). Use when the user wants
  animated equations, function graphs and coordinate systems, geometric
  constructions, or ValueTracker-driven continuous change, and when the project
  targets manimgl / manimlib / 3b1b's engine. Do NOT use for Manim Community
  Edition (`pip install manim`, `from manim import *`) — the two libraries share
  class names with different meanings; use the manim-video skill for CE work.
---

# ManimGL Video

ManimGL is 3Blue1Brown's personal rendering engine. It is **not** Manim Community
Edition. Both are called "Manim", both define a class named `Tex`, and the two
mean opposite things. Confirm which engine the project uses before writing a line.

Detect the engine from the project:

- `from manimlib import *` / `manimgl` CLI / `custom_config.yml` → **ManimGL, this skill**
- `from manim import *` / `manim -ql` CLI / `manim.cfg` → **Manim CE, stop and use `manim-video`**

## Do not confuse with Manim CE

Every row below was verified against manimlib source. The `Tex` row is the
dangerous one: the name exists in both engines, so the wrong choice raises no
error — it silently renders text as math or math as text.

| | ManimGL (this skill) | Manim CE (different tool) |
|---|---|---|
| install | `pip install manimgl` | `pip install manim` |
| import | `from manimlib import *` | `from manim import *` |
| CLI | `manimgl file.py Scene -w -l` | `manim -ql file.py Scene` |
| **math mode** | **`Tex("x^2")`** | `MathTex("x^2")` |
| **text mode (LaTeX)** | **`TexText("hello")`** | `Tex("hello")` |
| draw a shape | `ShowCreation(mob)` | `Create(mob)` |
| default background | `#333333` | `#000000` |

**These CE names do not exist in manimlib** — using them is an immediate
`NameError`: `Create`, `MathTex`, `Unwrite`, `AddTextLetterByLetter`, `Angle`,
`RightAngle`, `Star`, `Axes3D`.

## Minimal scene

```python
from manimlib import *


class Demo(Scene):
    def construct(self):
        title = Text("Pythagoras", font_size=48)
        eq = Tex(R"a^2 + b^2 = c^2", font_size=60)
        eq.next_to(title, DOWN, buff=LARGE_BUFF)

        self.play(Write(title))
        self.play(FadeIn(eq, shift=UP))
        self.wait()
```

```bash
manimgl file.py Demo        # interactive window, no file written
manimgl file.py Demo -w -l  # write low-quality mp4
```

Every scene subclasses `Scene`, `InteractiveScene`, or `ThreeDScene` and defines
`construct(self)`. 3b1b's own video code overwhelmingly uses `InteractiveScene`
(it adds mouse selection and editing in the preview window); plain `Scene` is
correct for headless rendering and is the safer default when writing code for
someone else to render.

## Workflow

1. Write the scene outline in prose first — one thing proved per scene. Do not
   open an editor until the beats are decided.
2. Run `manimgl file.py Scene` with **no** `-w`. The interactive window is the
   fast feedback loop; writing a file on every iteration wastes minutes.
3. Add `self.embed()` at the point of interest to drop into an IPython shell with
   the scene live. Inspect and nudge mobjects there instead of re-rendering.
4. Once composition is settled, `-w -l` for a low-quality file to judge timing.
5. Fixing a late beat? `-n <index>` starts at animation N instead of replaying
   everything from the top.
6. Only after timing is final, render `--hd` or `--uhd`.

Tighten typography, color, and spacing after motion works — not before.

## On-screen text

The animation carries the argument. A sentence that narrates what the viewer is
already watching competes with the visual for attention and duplicates whatever a
narrator would say over it.

**The test: if a narrator could speak the line, it does not belong on screen.**

Cut — prose that restates the motion:

- "읽는 순서대로 한 줄로 편다" over a grid that is visibly unrolling into a row
- "이게 없으면 패치를 섞어도 결과가 똑같다"
- "12개 블록을 지나며 전체 패치의 정보를 모았다"

Keep — anything the picture cannot state on its own:

- labels and names: axis titles, `LayerNorm`, `Q`, `K`, `V`
- counts, units, and specs: `4×4 = 16개 패치`, `224×224 → 16×16 패치 196개`
- formulas: `Attn = softmax(QK^T/√d)V`
- emphasis: color coding, a highlighted element, `Indicate`, `FlashAround`

Emphasis is not narration — keep every bit of it. Marking one patch red and
tracking it across scenes explains more than a caption would.

Prefer noun phrases to sentences, including for section titles: `1. 패치 분할`
over `1. 이미지를 패치로 자른다`. Where a scene seems to need a sentence, the
usual fix is a clearer visual, not a longer caption.

## Reference files

Open only what the current task needs; do not preload all four.

| File | Open when |
|------|-----------|
| [references/api-core.md](references/api-core.md) | Tex/Text, geometry shapes, VGroup, positioning, colors |
| [references/api-graphs.md](references/api-graphs.md) | Axes, NumberPlane, function graphs, ValueTracker, updaters |
| [references/animations.md](references/animations.md) | Which animation class to use, timing, lag_ratio, rate functions |
| [references/cli-config.md](references/cli-config.md) | CLI flags, custom_config.yml, reproducing the 3b1b look |

Runnable starting points, verified against manimlib source:

- [assets/smoke_test.py](assets/smoke_test.py) — geometry and `Text` only, **no LaTeX required**. Use this first to prove the install works.
- [assets/equation_graph.py](assets/equation_graph.py) — `Tex` + `Axes` + `ValueTracker`. Requires a working LaTeX install.

## Footguns

**`Tex` takes multiple strings.** `Tex("a", "+", "b")` splits into indexable
submobjects. To reliably address a substring, pass `isolate=[...]` and retrieve
with `get_part_by_tex` / `get_parts_by_tex`, or color via `t2c={...}`. Indexing a
`Tex` by raw integer position breaks the moment the LaTeX changes.

**LaTeX is required for `Tex`, `TexText`, and `Brace`.** `Text` and `Code` render
through Pango and need no LaTeX. When LaTeX is unavailable, a scene can still be
built entirely from `Text` plus geometry — say so rather than letting the render
fail.

**`ShowCreation`, not `Create`.** The most common CE reflex, and it fails loudly.

**Never `Write` CJK text.** `Write` traces glyph outlines, and a Hangul or Han
syllable is several independent contours, so every in-progress glyph renders as
disconnected strokes — illegible for the whole animation. Changing the font does
not help: regular and thin weights mangle identically. Use `FadeIn`, or
`AddTextWordByWord` when progressive reveal is wanted. Keep `Write` for Latin
text and `Tex`.

**Updaters must be removed.** A mobject with `add_updater` keeps mutating for the
rest of the scene. Call `clear_updaters()` when the effect is over, or the object
will drift during later beats.

**`always_redraw(func)` rebuilds the mobject every frame.** It is the correct tool
for something whose *shape* depends on a tracker, and the wrong tool for something
that merely moves — use `add_updater` or `f_always` for that. Rebuilding complex
mobjects each frame is the usual cause of a slow preview.

**`self.play()` needs an animation, not a mobject.** To animate a method call use
the `.animate` syntax: `self.play(square.animate.shift(RIGHT))`.

**Background is `#333333` by default**, noticeably lighter than CE's black. 3b1b's
production config overrides it to `#000000`; see `references/cli-config.md`.

## Attribution and licensing

- `3b1b/manim` (the engine) is **MIT**. Deriving code from `manimlib` and
  `example_scenes.py` is unrestricted.
- `3b1b/videos` (the per-video scene code) is **CC BY-NC-SA 4.0** — non-commercial
  and share-alike. Do not copy scenes from it into user projects without telling
  the user about the license. It also depends on `manim_imports_ext.py` and the
  repo's `custom/` package (pi creatures, backdrops), so it does not run standalone.

Write fresh code modeled on the API. Do not paste from `3b1b/videos`.
