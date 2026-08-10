"""Small plotting helpers, so the notebooks stay about the geometry."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

__all__ = ["show", "draw_segment", "draw_line"]


def show(img, ax=None, title=None, figsize=(7, 5)):
    """Display an image with no axes."""
    if ax is None:
        _, ax = plt.subplots(figsize=figsize)
    ax.imshow(np.clip(img, 0, 1))
    ax.set_axis_off()
    if title:
        ax.set_title(title)
    return ax


def draw_segment(ax, seg, color="tab:red", lw=2.5, label=None):
    """Draw a segment given as [[x1, y1], [x2, y2]]."""
    seg = np.asarray(seg, dtype=float).reshape(2, 2)
    ax.plot(seg[:, 0], seg[:, 1], color=color, lw=lw, label=label)


def draw_line(ax, l, xlim=None, color="tab:green", lw=2, ls="-", label=None):
    """Draw the homogeneous line l = (l1, l2, l3) across the current x range."""
    l = np.asarray(l, dtype=float)
    if xlim is None:
        xlim = ax.get_xlim()
    xs = np.array(xlim, dtype=float)
    if abs(l[1]) < 1e-12:          # vertical line: l1 x + l3 = 0
        x = -l[2] / l[0]
        ax.plot([x, x], ax.get_ylim(), color=color, lw=lw, ls=ls, label=label)
        return
    ys = -(l[0] * xs + l[2]) / l[1]
    ax.plot(xs, ys, color=color, lw=lw, ls=ls, label=label)


# ---------------------------------------------------------------------------
# Image-plane helpers for two-view geometry.
#
# `draw_line` above extends a line across the current x range, which is right
# for a plot. On a photograph we want the line clipped to the image rectangle
# instead, so that epipolar lines stop at the border.
# ---------------------------------------------------------------------------

ACCENT = "#F46D43"

__all__ += ["ACCENT", "clip_line_to_image", "draw_line_in_image",
            "pairwise_intersections", "show_matches"]


def clip_line_to_image(line, width, height):
    """
    Clip the line l1 x + l2 y + l3 = 0 to a width x height rectangle.

    Returns the two endpoints of the visible segment, or None if the line
    misses the rectangle entirely.
    """
    a, b, c = np.asarray(line, dtype=float)
    pts = []
    if abs(b) > 1e-12:
        for xx in (0.0, width - 1.0):
            yy = -(a * xx + c) / b
            if 0 <= yy <= height - 1:
                pts.append([xx, yy])
    if abs(a) > 1e-12:
        for yy in (0.0, height - 1.0):
            xx = -(b * yy + c) / a
            if 0 <= xx <= width - 1:
                pts.append([xx, yy])
    if len(pts) < 2:
        return None
    pts = np.asarray(pts)
    best, dist = None, -1.0
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            d = np.linalg.norm(pts[i] - pts[j])
            if d > dist:
                best, dist = np.vstack([pts[i], pts[j]]), d
    return best


def draw_line_in_image(ax, line, width, height, **kwargs):
    """Draw a homogeneous line on `ax`, clipped to the image rectangle."""
    seg = clip_line_to_image(line, width, height)
    if seg is not None:
        ax.plot(seg[:, 0], seg[:, 1], **kwargs)


def pairwise_intersections(lines):
    """
    All pairwise intersections of a set of homogeneous lines, in Cartesian
    coordinates. Pairs meeting at infinity are dropped.

    For a pencil the points collapse onto the epipole; for a full-rank F they
    scatter. That contrast is the visual content of the rank-two constraint.
    """
    pts = []
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            p = np.cross(lines[i], lines[j])
            if abs(p[2]) > 1e-10:
                pts.append(p[:2] / p[2])
    return np.asarray(pts)


def show_matches(I, Ip, x, xp, ids=None, title="", crop=None, figsize=(13, 7)):
    """Two views side by side, with the correspondences marked and labelled."""
    if ids is None:
        ids = np.arange(len(x))
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    for ax, im, pts, prime in [(axes[0], I, x, False), (axes[1], Ip, xp, True)]:
        ax.imshow(im)
        ax.scatter(pts[ids, 0], pts[ids, 1], s=55,
                   facecolors="none", edgecolors=ACCENT, linewidths=2)
        for i in ids:
            lab = (rf"$\mathbf{{x}}_{{{i + 1}}}'$" if prime
                   else rf"$\mathbf{{x}}_{{{i + 1}}}$")
            ax.text(pts[i, 0] + 12, pts[i, 1] - 12, lab, fontsize=10,
                    bbox=dict(facecolor="white", alpha=0.75,
                              edgecolor="none", pad=1.5))
        if crop is not None:
            x0, x1, y0, y1 = crop
            ax.set_xlim(x0, x1)
            ax.set_ylim(y1, y0)
        ax.set_axis_off()
    if title:
        fig.suptitle(title)
    plt.tight_layout()
    plt.show()
