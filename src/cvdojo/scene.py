"""Synthetic camera scenes for three-dimensional schematics.

These build the 3D diagrams that accompany the derivations: they place a
camera looking at a target, draw its image plane, and keep the axes to scale.
"""

from __future__ import annotations

import numpy as np


def skew(v):
    """The 3x3 matrix with skew(v) @ w == cross(v, w)."""
    a, b, c = np.asarray(v, float)
    return np.array([[0, -c, b], [c, 0, -a], [-b, a, 0]])


def look_at(C, target, up=(0.0, 0.0, 1.0)):
    """Rotation and translation of a camera at C looking towards `target`."""
    C = np.asarray(C, float)
    target = np.asarray(target, float)
    up = np.asarray(up, float)
    z = target - C
    z /= np.linalg.norm(z)
    xaxis = np.cross(z, up)
    if np.linalg.norm(xaxis) < 1e-9:
        xaxis = np.cross(z, np.array([0.0, 1.0, 0.0]))
    xaxis /= np.linalg.norm(xaxis)
    yaxis = np.cross(z, xaxis)
    R = np.vstack([xaxis, yaxis, z])
    return R, -R @ C


def camera_center(R, t):
    """The camera centre in world coordinates."""
    return -R.T @ t


def project_normalized(R, t, X):
    """Project world points through a camera with unit intrinsics."""
    X = np.atleast_2d(np.asarray(X, float))
    q = (R @ X.T + t[:, None]).T
    return q[:, :2] / q[:, 2, None]


def image_plane_world(R, t, depth=0.75, half=0.8):
    """The four corners of a camera's image plane, in world coordinates."""
    C = camera_center(R, t)
    q = np.array([[-half, -half * 0.72, depth], [half, -half * 0.72, depth],
                  [half, half * 0.72, depth], [-half, half * 0.72, depth]])
    return (R.T @ q.T).T + C


def image_uv_to_world(R, t, uv, depth=0.75):
    """Lift a normalized image point onto the drawn image plane."""
    C = camera_center(R, t)
    q = np.array([depth * uv[0], depth * uv[1], depth])
    return R.T @ q + C


def set_axes_equal(ax):
    """Equal aspect ratio for a 3D axis, which matplotlib does not do itself."""
    lim = np.array([ax.get_xlim3d(), ax.get_ylim3d(), ax.get_zlim3d()], float)
    ctr = lim.mean(1)
    r = 0.53 * np.max(lim[:, 1] - lim[:, 0])
    ax.set_xlim(ctr[0] - r, ctr[0] + r)
    ax.set_ylim(ctr[1] - r, ctr[1] + r)
    ax.set_zlim(ctr[2] - r, ctr[2] + r)
    ax.set_box_aspect((1, 1, 1))
