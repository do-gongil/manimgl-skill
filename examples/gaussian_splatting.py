"""3D Gaussian Splatting explainer (ManimGL, Text-only: no LaTeX needed).

    python -m manimlib gaussian_splatting.py GaussianSplatting          # preview
    python -m manimlib gaussian_splatting.py GaussianSplatting -w -l    # 480p mp4
    python -m manimlib gaussian_splatting.py GaussianSplatting -w --hd  # 1080p

The alpha-compositing numbers in beat 5 are computed, not typed: the same
front-to-back formula the rasterizer uses, run in numpy on the splats drawn.
"""

import sys

import numpy as np

from manimlib import *

FONT = {"win32": "Segoe UI", "darwin": "Helvetica Neue"}.get(sys.platform, "DejaVu Sans")
RNG = np.random.default_rng(7)

# (color, alpha) of the three splats a ray passes through in beat 5, front to back.
RAY_SPLATS = [(RED_C, 0.45), (GREEN_C, 0.60), (BLUE_C, 0.80)]


def txt(s, **kw):
    return Text(s, font=FONT, **kw)


def composite(splats):
    """Front-to-back alpha compositing. Returns (per-splat weights, transmittance)."""
    T, weights = 1.0, []
    for _, a in splats:
        weights.append(a * T)
        T *= 1 - a
    return np.array(weights), T


def gaussian_blob(color, w, h, angle=0.0, alpha=1.0, rings=6):
    """A soft ellipse: nested ellipses whose opacity follows exp(-r^2/2)."""
    blob = VGroup()
    for k in range(rings, 0, -1):
        r = k / rings * 2.5          # radius in sigmas
        e = Ellipse(width=w * r / 2.5, height=h * r / 2.5)
        e.set_stroke(width=0).set_fill(color, opacity=alpha * float(np.exp(-r * r / 2)) * 1.6)
        blob.add(e)
    return blob.rotate(angle)


def camera_icon(color=GREY_B):
    body = Rectangle(0.5, 0.32, color=color).set_fill(color, 0.3)
    lens = Triangle(color=color).set_fill(color, 0.3).rotate(-PI / 2).set_width(0.22)
    lens.next_to(body, RIGHT, buff=0)
    return VGroup(body, lens)


class GaussianSplatting(Scene):
    def construct(self):
        self.opening()
        self.point_cloud()
        self.one_gaussian()
        self.splatting()
        self.compositing()
        self.optimization()
        self.closing()

    # ------------------------------------------------------------------ 1
    def opening(self):
        title = txt("3D Gaussian Splatting", font_size=56)
        sub = txt("a radiance field made of millions of soft ellipsoids", font_size=26).set_color(GREY_B)
        sub.next_to(title, DOWN, buff=MED_LARGE_BUFF)
        self.play(Write(title))
        self.play(FadeIn(sub, shift=UP * 0.3))
        self.wait(1.5)
        self.play(FadeOut(sub), title.animate.scale(36 / 56).to_edge(UP, buff=0.35))
        self.title = title

    def set_title(self, s):
        new = txt(s, font_size=36).to_edge(UP, buff=0.35)
        self.play(Transform(self.title, new))

    # ------------------------------------------------------------------ 2
    def point_cloud(self):
        self.set_title("1. Input: photos + a sparse point cloud")
        pts = np.clip(RNG.normal(0, 1, (120, 2)), -2.2, 2.2) * [1.1, 0.75]
        cloud = VGroup(*[Dot(np.array([x, y, 0]), radius=0.04, color=GREY_A) for x, y in pts])
        cams = VGroup()
        for ang in np.linspace(0, TAU, 8, endpoint=False):
            c = camera_icon().rotate(ang + PI)
            c.move_to(3.4 * np.array([np.cos(ang), 0.8 * np.sin(ang), 0]))
            cams.add(c)
        cam_label = txt("N photos (known poses)", font_size=24).next_to(cams, DOWN, buff=0.3)
        sfm_label = txt("SfM points", font_size=24).set_color(GREY_A).next_to(cloud, UP, buff=0.15)
        self.play(LaggedStartMap(FadeIn, cams, lag_ratio=0.15), FadeIn(cam_label))
        self.play(LaggedStartMap(GrowFromCenter, cloud, lag_ratio=0.01, run_time=2), FadeIn(sfm_label))
        self.wait()
        self.play(FadeOut(cams), FadeOut(cam_label), FadeOut(sfm_label))
        self.cloud = cloud

    # ------------------------------------------------------------------ 3
    def one_gaussian(self):
        self.set_title("2. Every point becomes a 3D Gaussian")
        keep = self.cloud[0]
        others = VGroup(*self.cloud[1:])
        self.play(others.animate.set_opacity(0.15), keep.animate.set_color(YELLOW).scale(2))
        self.play(keep.animate.move_to(LEFT * 3))

        blob = gaussian_blob(YELLOW, 3.2, 1.7, angle=0.5).move_to(LEFT * 3)
        self.play(ReplacementTransform(keep, blob), run_time=1.5)
        self.remove(others)

        params = VGroup(
            txt("μ   position (3)", font_size=28),
            txt("Σ   covariance = scale (3) + rotation (4)", font_size=28),
            txt("c   color, view-dependent (SH, 48)", font_size=28),
            txt("α   opacity (1)", font_size=28),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).next_to(blob, RIGHT, buff=0.9)
        params.set_width(min(params.get_width(), 7.0))
        self.play(LaggedStartMap(FadeIn, params, shift=RIGHT * 0.3, lag_ratio=0.3))
        self.wait()

        # each parameter is demonstrated on the blob itself
        self.play(Indicate(params[0]), blob.animate.shift(UP * 0.6))
        self.play(Indicate(params[1]), blob.animate.rotate(-0.9).stretch(1.4, 0))
        self.play(Indicate(params[2]), blob.animate.set_color(TEAL))
        self.play(Indicate(params[3]), blob.animate.set_opacity(0.35))
        self.wait(0.5)
        self.play(FadeOut(params), FadeOut(blob))

    # ------------------------------------------------------------------ 4
    def splatting(self):
        self.set_title("3. Splat: project each ellipsoid onto the image")
        cam = camera_icon(GREY_B).scale(1.4).move_to(LEFT * 5.5 + DOWN * 0.5)
        plane = Rectangle(3.2, 2.2, color=GREY_B).move_to(LEFT * 2.2 + DOWN * 0.5)
        plane_label = txt("image plane", font_size=22).set_color(GREY_B).next_to(plane, DOWN, buff=0.15)
        self.play(FadeIn(cam), ShowCreation(plane), FadeIn(plane_label))

        specs = [(RED_C, 1.6, 0.9, 0.4, RIGHT * 2.2 + UP * 0.9),
                 (GREEN_C, 1.2, 1.2, 0.0, RIGHT * 3.4 + DOWN * 0.9),
                 (BLUE_C, 2.0, 0.8, -0.6, RIGHT * 4.6 + UP * 0.2)]
        blobs = VGroup(*[gaussian_blob(c, w, h, a, alpha=0.9).move_to(p) for c, w, h, a, p in specs])
        world = txt("3D Gaussians", font_size=22).set_color(GREY_B).next_to(blobs, DOWN, buff=0.3)
        self.play(LaggedStartMap(FadeIn, blobs, lag_ratio=0.3), FadeIn(world))

        # projection: shrink each blob onto the plane, as a flat 2D ellipse
        targets = VGroup()
        for b, (c, w, h, a, p) in zip(blobs, specs):
            t = gaussian_blob(c, w * 0.45, h * 0.45, a * 0.5, alpha=0.9)
            t.move_to(plane.get_center() + (p - RIGHT * 3.4) * 0.35)
            targets.add(t)
        rays = VGroup(*[DashedLine(cam.get_right(), b.get_center(), stroke_width=1.5, color=GREY_C)
                        for b in blobs])
        self.play(ShowCreation(rays))
        self.play(*[TransformFromCopy(b, t) for b, t in zip(blobs, targets)], run_time=2)
        note = txt("3D covariance  →  2D covariance", font_size=24).next_to(plane, UP, buff=0.35)
        self.play(FadeIn(note))
        self.wait(1.5)
        self.play(*map(FadeOut, [cam, plane, plane_label, blobs, world, rays, targets, note]))

    # ------------------------------------------------------------------ 5
    def compositing(self):
        self.set_title("4. Blend front-to-back, sorted by depth")
        # three splats stacked along one pixel ray, front (left) to back (right)
        xs = [-3.2, -0.8, 1.6]
        blobs = VGroup(*[gaussian_blob(c, 1.4, 2.2, alpha=a).move_to(RIGHT * x + DOWN * 0.3)
                         for (c, a), x in zip(RAY_SPLATS, xs)])
        ray = Arrow(LEFT * 6, RIGHT * 4, buff=0, stroke_width=3, color=WHITE).shift(DOWN * 0.3)
        pix = txt("pixel ray", font_size=22).next_to(ray.get_start(), UP, buff=0.15).shift(RIGHT * 0.6)
        self.play(GrowArrow(ray), FadeIn(pix))
        self.play(LaggedStartMap(FadeIn, blobs, lag_ratio=0.3))

        alphas = VGroup(*[txt(f"α = {a:.2f}", font_size=24).next_to(b, UP, buff=0.2)
                          for (c, a), b in zip(RAY_SPLATS, blobs)])
        self.play(LaggedStartMap(FadeIn, alphas, lag_ratio=0.3))

        formula = txt("C = Σ  cᵢ · αᵢ · Tᵢ        Tᵢ = Π (1 − αⱼ),  j in front of i", font_size=26)
        formula.to_edge(DOWN, buff=1.2)
        self.play(FadeIn(formula))
        self.wait()

        # computed weights: what fraction of the pixel each splat finally owns
        weights, T_rest = composite(RAY_SPLATS)
        wlabels = VGroup(*[txt(f"weight {w:.2f}", font_size=24).set_color(c).next_to(b, DOWN, buff=0.2)
                           for w, (c, _), b in zip(weights, RAY_SPLATS, blobs)])
        self.play(LaggedStartMap(FadeIn, wlabels, lag_ratio=0.4))

        bar = VGroup()
        x0 = -4.0
        for w, (c, _) in zip(weights, RAY_SPLATS):
            seg = Rectangle(8 * w, 0.4, color=c).set_fill(c, 0.9).set_stroke(width=1)
            seg.move_to(RIGHT * (x0 + 4 * w) + DOWN * 3.2)
            bar.add(seg)
            x0 += 8 * w
        rest = Rectangle(8 * T_rest, 0.4, color=GREY_D).set_fill(GREY_D, 0.6).set_stroke(width=1)
        rest.move_to(RIGHT * (x0 + 4 * T_rest) + DOWN * 3.2)
        bar_label = txt(f"pixel = {weights[0]:.2f} red + {weights[1]:.2f} green + {weights[2]:.2f} blue"
                        f"   (unclaimed {T_rest:.2f})", font_size=22).next_to(bar, DOWN, buff=0.12)
        self.play(FadeOut(formula), LaggedStartMap(GrowFromEdge, bar, edge=LEFT, lag_ratio=0.3),
                  FadeIn(rest), FadeIn(bar_label))
        self.wait(2)
        self.play(*map(FadeOut, [ray, pix, blobs, alphas, wlabels, bar, rest, bar_label]))

    # ------------------------------------------------------------------ 6
    def optimization(self):
        self.set_title("5. Optimize by gradient descent on the photos")
        render = Rectangle(3.4, 2.4, color=GREY_B).move_to(LEFT * 3.2 + UP * 0.6)
        photo = Rectangle(3.4, 2.4, color=GREY_B).move_to(RIGHT * 3.2 + UP * 0.6)
        r_label = txt("render", font_size=24).next_to(render, UP, buff=0.15)
        p_label = txt("photo", font_size=24).next_to(photo, UP, buff=0.15)
        # the "image" content: a few blobs, the photo version tighter and better placed
        rb = VGroup(gaussian_blob(RED_C, 1.6, 1.0, 0.6, 0.8).shift(LEFT * 0.4),
                    gaussian_blob(BLUE_C, 1.0, 1.4, -0.3, 0.8).shift(RIGHT * 0.7 + DOWN * 0.3)).move_to(render)
        pb = VGroup(gaussian_blob(RED_C, 1.2, 0.8, 0.2, 0.9).shift(LEFT * 0.5 + UP * 0.2),
                    gaussian_blob(BLUE_C, 0.8, 1.1, 0.1, 0.9).shift(RIGHT * 0.6 + DOWN * 0.4)).move_to(photo)
        self.play(ShowCreation(render), ShowCreation(photo), FadeIn(r_label), FadeIn(p_label))
        self.play(FadeIn(rb), FadeIn(pb))

        loss = txt("L = (1 − λ)·L1 + λ·D-SSIM", font_size=28).move_to(DOWN * 1.4)
        arrow = Arrow(photo.get_left(), render.get_right(), buff=0.15, color=YELLOW)
        grad = txt("∂L/∂(μ, Σ, c, α)", font_size=24).set_color(YELLOW).next_to(arrow, UP, buff=0.1)
        self.play(FadeIn(loss))
        self.play(GrowArrow(arrow), FadeIn(grad))
        # render moves toward the photo: same blobs, transformed to the photo's shapes
        target = pb.copy().move_to(render)
        self.play(Transform(rb, target), run_time=2)
        self.wait(0.5)

        # adaptive density: split, clone, prune
        self.play(*map(FadeOut, [arrow, grad, loss]))
        steps = VGroup(
            txt("split   large Gaussians with big gradients", font_size=24),
            txt("clone   small ones that under-cover", font_size=24),
            txt("prune   α below threshold", font_size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(DOWN * 2.2)
        self.play(LaggedStartMap(FadeIn, steps, lag_ratio=0.3))

        big = gaussian_blob(RED_C, 1.6, 0.9, 0.0, 0.9).move_to(render)
        self.play(FadeOut(rb), FadeIn(big), Indicate(steps[0]))
        halves = VGroup(gaussian_blob(RED_C, 0.9, 0.7, 0.0, 0.9).move_to(render.get_center() + LEFT * 0.5),
                        gaussian_blob(RED_C, 0.9, 0.7, 0.0, 0.9).move_to(render.get_center() + RIGHT * 0.5))
        self.play(ReplacementTransform(big, halves))
        clone = halves[1].copy().shift(DOWN * 0.5)
        self.play(Indicate(steps[1]), TransformFromCopy(halves[1], clone))
        faint = gaussian_blob(GREY_C, 0.7, 0.7, 0.0, 0.25).move_to(render.get_center() + UP * 0.7)
        self.play(FadeIn(faint))
        self.play(Indicate(steps[2]), FadeOut(faint, scale=0.3))
        self.wait()
        self.play(*map(FadeOut, [render, photo, r_label, p_label, pb, halves, clone, steps]))

    # ------------------------------------------------------------------ 7
    def closing(self):
        self.set_title("3D Gaussian Splatting")
        facts = VGroup(
            txt("explicit:  1–5 M Gaussians, no neural network at render time", font_size=28),
            txt("rasterized, not ray-marched:  30+ FPS at 1080p", font_size=28),
            txt("trained in ~30 min per scene on one GPU", font_size=28),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        cite = txt("Kerbl, Kopanas, Leimkühler, Drettakis — SIGGRAPH 2023", font_size=22).set_color(GREY_B)
        cite.to_edge(DOWN, buff=0.6)
        self.play(LaggedStartMap(FadeIn, facts, shift=UP * 0.3, lag_ratio=0.4))
        self.play(FadeIn(cite))
        self.wait(3)


if __name__ == "__main__":
    # Pure-math check, runs without manimgl: python gaussian_splatting.py
    w, T = composite(RAY_SPLATS)
    assert abs(w.sum() + T - 1.0) < 1e-9, "weights and leftover transmittance must sum to 1"
    assert w[0] == RAY_SPLATS[0][1], "front splat keeps its full alpha"
    print("ok", np.round(w, 3), round(T, 3))
