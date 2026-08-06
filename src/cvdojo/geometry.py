"""
Projective geometry primitives for the plane P^2.

Notation follows the book (Computer Vision Dojo, Ch. 1):
  - points and lines are 3-vectors in homogeneous coordinates
  - a line through two points:      l = x cross y
  - the intersection of two lines:  x = l cross m

Luca Magri - Politecnico di Milano
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "homogeneous",
    "cartesian",
    "seg_to_line",
    "meet",
    "join",
    "normalize_line",
    "H_from_vanishing_line",
]


def homogeneous(pts: np.ndarray) -> np.ndarray:
    """Cartesian (N, 2) -> homogeneous (N, 3) by appending a column of ones."""
    pts = np.atleast_2d(np.asarray(pts, dtype=float))
    return np.hstack([pts, np.ones((pts.shape[0], 1))])


def cartesian(pts: np.ndarray) -> np.ndarray:
    """Homogeneous (N, 3) -> Cartesian (N, 2). Points at infinity give inf/nan."""
    pts = np.atleast_2d(np.asarray(pts, dtype=float))
    with np.errstate(divide="ignore", invalid="ignore"):
        return pts[:, :2] / pts[:, [2]]


def seg_to_line(seg: np.ndarray) -> np.ndarray:
    """
    Line through the two endpoints of a segment.

    Parameters
    ----------
    seg : (2, 2) array
        Endpoints as [[x1, y1], [x2, y2]] in pixel coordinates.

    Returns
    -------
    (3,) array
        The homogeneous line, normalised so that (l1, l2) is a unit vector.

    Equivalent to segToLine.m in the MATLAB exercises.
    """
    seg = np.asarray(seg, dtype=float).reshape(2, 2)
    a, b = homogeneous(seg)
    return normalize_line(np.cross(a, b))


def meet(l: np.ndarray, m: np.ndarray) -> np.ndarray:
    """Intersection point of two lines."""
    return np.cross(np.asarray(l, float), np.asarray(m, float))


def join(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Line through two points."""
    return np.cross(np.asarray(x, float), np.asarray(y, float))


def normalize_line(l: np.ndarray) -> np.ndarray:
    """
    Scale a line so that its normal part (l1, l2) has unit norm.

    This is line 3 of Algorithm 1. Without it the third row of H_P can carry
    values several orders of magnitude away from the first two, which makes
    the warp numerically fragile.
    """
    l = np.asarray(l, dtype=float)
    n = np.linalg.norm(l[:2])
    return l / n if n > 0 else l


def H_from_vanishing_line(l_inf: np.ndarray) -> np.ndarray:
    """
    Affine-rectifying homography H_P (Algorithm 1, line 4).

    Maps the image of the line at infinity to its canonical position
    (0 : 0 : 1), restoring parallelism.

        H_P = [[1, 0, 0],
               [0, 1, 0],
               [l1, l2, l3]]

    Parameters
    ----------
    l_inf : (3,) array
        Image of the line at infinity, l'_inf.

    Returns
    -------
    (3, 3) array
    """
    l = normalize_line(l_inf)
    H = np.eye(3)
    H[2, :] = l
    return H
