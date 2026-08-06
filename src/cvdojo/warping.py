"""
Image warping under a planar homography.

MATLAB's `imwarp` silently computes an output canvas large enough to hold the
warped image and shifts it into view. `skimage.transform.warp` does not: it
keeps the original canvas, so a rectified image usually lands mostly outside
it. `warp_image` below restores the MATLAB behaviour.

Luca Magri - Politecnico di Milano
"""

from __future__ import annotations

import numpy as np
from skimage.transform import ProjectiveTransform, warp

__all__ = ["image_corners", "fit_to_canvas", "warp_image"]


def image_corners(shape: tuple[int, ...]) -> np.ndarray:
    """The four image corners in homogeneous coordinates, as a (3, 4) array."""
    h, w = shape[:2]
    return np.array(
        [[0.0, w, w, 0.0],
         [0.0, 0.0, h, h],
         [1.0, 1.0, 1.0, 1.0]]
    )


def fit_to_canvas(H, shape, roi=None, max_side=1200, margin=0.05):
    """
    Post-multiply H by a similarity so the warped image fits a sensible canvas.

    A rectifying homography is defined up to a similarity (Section 1.2.1), so we
    are free to translate and scale the result. Here we pick the similarity that
    puts the warped content in the positive quadrant and sets its longest side
    to `max_side`.

    Parameters
    ----------
    roi : (N, 2) array, optional
        Region of interest in the *input* image. When given, the canvas is
        fitted to these points instead of the four image corners. Fitting to
        the corners is usually a poor choice: affine rectification pushes the
        far corners a long way out, and the object of interest ends up as a
        small patch in a mostly empty frame.

    Returns
    -------
    H_fitted : (3, 3) array
    out_shape : (rows, cols)
    """
    H = np.asarray(H, dtype=float)

    # Fix the overall sign so the image centre keeps a positive third
    # coordinate; otherwise the whole warp comes out rotated by 180 degrees.
    h, w = shape[:2]
    centre = np.array([w / 2.0, h / 2.0, 1.0])
    if (H @ centre)[2] < 0:
        H = -H

    if roi is None:
        corners = H @ image_corners(shape)
    else:
        roi = np.atleast_2d(np.asarray(roi, dtype=float))
        corners = H @ np.vstack([roi.T, np.ones(roi.shape[0])])

    # A vanishing line crossing the image sends some points behind the camera;
    # those flip sign in the third coordinate and must be dropped.
    valid = np.abs(corners[2]) > 1e-9
    if valid.sum() < 3:
        raise ValueError(
            "The homography degenerates on this image: the vanishing line "
            "probably cuts through it. Pick segments whose vanishing points "
            "lie further from the image."
        )
    pts = corners[:2, valid] / corners[2, valid]

    x0, y0 = pts.min(axis=1)
    x1, y1 = pts.max(axis=1)
    pad = margin * max(x1 - x0, y1 - y0)
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    width, height = x1 - x0, y1 - y0

    # H is defined up to a similarity (Section 1.2.1), so we are free to
    # rescale: an affine rectification often shrinks the image drastically.
    s = max_side / max(width, height)
    S = np.array([[s, 0.0, -s * x0],
                  [0.0, s, -s * y0],
                  [0.0, 0.0, 1.0]])

    out_shape = (int(np.ceil(s * height)), int(np.ceil(s * width)))
    return S @ H, out_shape


def warp_image(img, H, roi=None, max_side=1200):
    """
    Apply a homography to an image, auto-sizing the output canvas.

    Note the inverse: skimage's `warp` pulls each output pixel from the input,
    so it wants the inverse map. Forgetting this is the classic way to get a
    rectified image that looks *more* distorted.
    """
    H_fitted, out_shape = fit_to_canvas(H, img.shape, roi=roi, max_side=max_side)
    tform = ProjectiveTransform(matrix=np.linalg.inv(H_fitted))
    return warp(img, tform, output_shape=out_shape, order=1, preserve_range=False)
