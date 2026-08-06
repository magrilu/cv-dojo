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
