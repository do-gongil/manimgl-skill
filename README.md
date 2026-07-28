# manimgl-skill

An agent skill for **ManimGL** — 3Blue1Brown's own Manim engine.

> **This is not Manim Community Edition.** The two libraries are both called
> "Manim", share class names, and give some of those names *opposite* meanings.
> If your project uses `from manim import *`, this skill is the wrong one.

## Demo

A Vision Transformer explainer scene, written with this skill and rendered with
`manimgl`:

https://github.com/user-attachments/assets/deaefc64-6e75-4a4c-86d7-c8dabcf4b996

## Which Manim do you have?

| | ManimGL (this skill) | Manim CE |
|---|---|---|
| install | `pip install manimgl` | `pip install manim` |
| import | `from manimlib import *` | `from manim import *` |
| CLI | `manimgl file.py Scene -w -l` | `manim -ql file.py Scene` |
| **math mode** | **`Tex("x^2")`** | `MathTex("x^2")` |
| **text mode (LaTeX)** | **`TexText("hi")`** | `Tex("hi")` |
| draw a shape | `ShowCreation(mob)` | `Create(mob)` |
| default background | `#333333` | `#000000` |

`Tex` exists in both and means the opposite thing, so choosing wrong raises no
error — it silently renders math as text or text as math. These CE names do not
exist in manimlib at all: `Create`, `MathTex`, `Unwrite`, `Angle`, `RightAngle`,
`Star`, `Axes3D`.

## Install

```
/plugin marketplace add do-gongil/manimgl-skill
/plugin install manimgl@manimgl-skill
/reload-plugins
```

The skill then shows up as `manimgl:manimgl-video`. You normally will not type
that — it activates on its own when the work is ManimGL-shaped.

To use it without the plugin system, copy `skills/manimgl-video/` into
`~/.claude/skills/`. It is then `/manimgl-video`, without the plugin namespace.

## Usage

Most of the time you do not name the skill. It activates on its own once the work
is ManimGL-shaped:

> Make a scene showing how a Riemann sum converges to an integral.

> This repo uses manimgl — add a scene for the chain rule.

To invoke it explicitly:

```
/manimgl:manimgl-video Fourier transform of a mixed waveform
/manimgl:manimgl-video eigenvectors staying on their span
/manimgl:manimgl-video the epsilon-delta definition of a limit
/manimgl:manimgl-video why a matrix determinant is a signed area
```

You get a scene outline first, then the ManimGL code, then the command to render
it. Iterating in the preview window (`manimgl file.py Scene`, no `-w`) is the fast
loop; writing a file is the last step, not the first.

### Language

On-screen text is English by default — conversing in another language does not
change that. Ask if you want otherwise:

```
/manimgl:manimgl-video the Fourier transform, with Korean labels
```

Non-Latin scripts need a platform-specific font and a different reveal animation
(`Write` traces glyph outlines, which turns Hangul and Han characters into
scribbles while it runs). The skill handles both; see
[`references/api-core.md`](skills/manimgl-video/references/api-core.md).

## What is in it

```
skills/manimgl-video/
├─ SKILL.md                  entry point: CE/GL disambiguation, workflow, footguns
├─ references/
│  ├─ api-core.md            Tex/Text, geometry, VGroup, positioning, colors, CJK
│  ├─ api-graphs.md          Axes, NumberPlane, function graphs, ValueTracker, updaters
│  ├─ animations.md          animation catalog, timing, lag_ratio, rate functions
│  └─ cli-config.md          CLI flags, custom_config.yml, install traps per platform
└─ assets/
   ├─ smoke_test.py          geometry + Text only — no LaTeX needed
   └─ equation_graph.py      Tex + Axes + ValueTracker
```

## How it was built

API signatures were extracted from `manimlib` source with an AST pass, not from
memory. Every class, function and method named in the reference files was checked
against `manimlib`'s actual export surface.

Both assets were then rendered. That caught what static checking could not:
`get_tangent_line()` takes no `color` kwarg, `add_coordinate_labels` defaults to
zero decimal places so a `0.5` tick prints as `0`, and `ReplacementTransform`
leaves its target in the scene. The install traps in `cli-config.md` — MiKTeX
rejecting manimlib's `-no-pdf`, `manimpango` shipping no Linux wheels, `audioop`
removed in Python 3.13 — all came from hitting them.

## Requirements

- Python 3.7+, `pip install manimgl`
- FFmpeg (only for writing files; preview does not need it)
- OpenGL
- LaTeX — only for `Tex`, `TexText`, `Brace`. `smoke_test.py` runs without it.

Platform-specific setup, including headless Linux without root, is in
[`skills/manimgl-video/references/cli-config.md`](skills/manimgl-video/references/cli-config.md).

## Credits and licensing

This skill documents [3b1b/manim](https://github.com/3b1b/manim) (ManimGL),
which is MIT licensed. The skill itself is MIT — see [LICENSE](LICENSE).

No code was copied from [3b1b/videos](https://github.com/3b1b/videos). That
repository is CC BY-NC-SA 4.0, and its scenes also depend on its own `custom/`
package, so they do not run standalone. It was consulted only to observe which
APIs appear most in production use; every example here was written fresh.
