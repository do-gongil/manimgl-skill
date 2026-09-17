"""Snapshot a ManimGL scene at chosen beats so the frames can be inspected as images.

    python snapshot.py file.py Scene --list     # run once (skipped) and number every play/wait as it happens
    python snapshot.py file.py Scene 3 7 12     # frames after animations 3, 7 and 12
    python snapshot.py file.py Scene            # final frame only
    python snapshot.py file.py Scene 3 7 --hd   # 1080p instead of the default 480p

Each frame is `manimgl file.py Scene -s -w -n 0,K`: construct() runs with every
animation skipped (end states applied instantly) and stops right before animation
K, then the frame is saved. Index K counts self.play() AND self.wait() calls from
0, in the order they execute. Output: frames/<Scene>_<K>.png, or <Scene>_final.png.

Stdlib only; runs manimlib through the current interpreter, so the `manimgl`
script does not need to be on PATH.
"""

import argparse
import os
import re
import subprocess
import sys

TRACE = """
import inspect, sys
sys.argv = ["manimgl", {file!r}, {scene!r}, "-s", "-w", "-l", "--video_dir", {tmp!r}, "--file_name", "_trace"]
import manimlib
from manimlib.scene.scene import Scene
_orig = Scene.pre_play
def pre_play(self):
    for fr in inspect.stack()[1:]:
        if fr.filename.replace("\\\\", "/").endswith({file!r}.replace("\\\\", "/")):
            src = fr.code_context[0].strip() if fr.code_context else ""
            print(f"SNAP {{self.num_plays:3d}}  L{{fr.lineno:<4d}} {{src}}")
            break
    _orig(self)
Scene.pre_play = pre_play
from manimlib.__main__ import main
main()
"""


def list_calls(scene_file, scene):
    """Runtime numbering: run the scene with every animation skipped and hook
    Scene.pre_play, so helper methods called from several beats are counted
    each time they run (a source-order grep gets that wrong)."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        code = TRACE.format(file=scene_file, scene=scene, tmp=tmp)
        p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    lines = [ln[5:] for ln in p.stdout.splitlines() if ln.startswith("SNAP ")]
    if p.returncode != 0 or not lines:
        tail = "\n".join((p.stdout + p.stderr).strip().splitlines()[-15:])
        raise SystemExit(f"trace run failed:\n{tail}")
    return lines


def render(scene_file, scene, index, out_dir, quality):
    name = f"{scene}_{index:03d}" if index is not None else f"{scene}_final"
    cmd = [sys.executable, "-m", "manimlib", scene_file, scene, "-s", "-w", quality,
           "--video_dir", out_dir, "--file_name", name]
    if index is not None:
        cmd += ["-n", f"0,{index}"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = os.path.join(out_dir, name + ".png")
    if p.returncode != 0 or not os.path.exists(out):
        tail = "\n".join((p.stdout + p.stderr).strip().splitlines()[-15:])
        raise SystemExit(f"render failed for {name}:\n{tail}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scene_file")
    ap.add_argument("scene")
    ap.add_argument("indices", nargs="*", type=int, help="animation indices to stop before")
    ap.add_argument("--list", action="store_true", help="number the play/wait calls and exit")
    ap.add_argument("--out", default="frames", help="output directory (default: frames)")
    ap.add_argument("--hd", action="store_true", help="1080p frames instead of 480p")
    args = ap.parse_args()

    with open(args.scene_file, encoding="utf-8") as f:
        if not re.search(rf"^class {re.escape(args.scene)}\(", f.read(), re.M):
            # manimgl silently falls back to another scene when the name is unknown
            raise SystemExit(f"no `class {args.scene}(` in {args.scene_file}")

    if args.list:
        print("\n".join(list_calls(args.scene_file, args.scene)))
        return

    targets = args.indices or [None]
    quality = "--hd" if args.hd else "-l"
    for k in targets:
        print(render(args.scene_file, args.scene, k, args.out, quality))


if __name__ == "__main__":
    main()
