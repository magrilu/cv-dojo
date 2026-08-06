"""
Sample data.

`load_facade` returns a real photograph if one is present in data/, and
otherwise synthesises a facade seen under a known homography. The synthetic
case is useful in its own right: since the ground-truth transformation is
known, the rectification can be checked against it.

Luca Magri - Politecnico di Milano
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

__all__ = ["synthetic_facade", "load_facade", "DEFAULT_SEGMENTS"]

# Endpoints [[x1, y1], [x2, y2]] of four segments on the synthetic facade:
# the first two come from one family of parallel world lines, the last two
# from a second family. Used so the notebook runs without any clicking.
DEFAULT_SEGMENTS = {
    "a": [[141.0, 148.0], [536.0, 214.0]],
    "c": [[128.0, 377.0], [548.0, 372.0]],
    "b": [[141.0, 148.0], [128.0, 377.0]],
    "d": [[536.0, 214.0], [548.0, 372.0]],
}


def _facade_texture(size: int = 512) -> np.ndarray:
    """A frontal facade: brick courses plus a grid of windows."""
    rng = np.random.default_rng(0)
    img = np.full((size, size, 3), 0.80)

    # brick courses
    course = size // 16
    for i in range(0, size, course):
        img[i:i + 2, :, :] = 0.62
        offset = 0 if (i // course) % 2 == 0 else course
        for j in range(offset, size, 2 * course):
            img[i:i + course, j:j + 2, :] = 0.62

    # windows on a 3 x 3 grid
    m = size // 9
    for r in range(3):
        for c in range(3):
            y = m + r * 3 * m
            x = m + c * 3 * m
            img[y:y + int(1.6 * m), x:x + int(1.2 * m)] = (0.13, 0.18, 0.28)
            img[y:y + 3, x:x + int(1.2 * m)] = 0.95
            img[y + int(1.6 * m) - 3:y + int(1.6 * m), x:x + int(1.2 * m)] = 0.95

    img += rng.normal(0.0, 0.012, img.shape)
    return np.clip(img, 0.0, 1.0)


def synthetic_facade(size: int = 512, out_shape: tuple[int, int] = (520, 700)):
    """
    A facade under a known projective distortion.

    Returns
    -------
    img : (H, W, 3) float array in [0, 1]
    H_gt : (3, 3) array
        The ground-truth homography mapping the frontal texture into the image.
    """
    from skimage.transform import ProjectiveTransform, warp

    tex = _facade_texture(size)

    src = np.array([[0, 0], [size, 0], [size, size], [0, size]], dtype=float)
    dst = np.array([[140, 150], [540, 215], [548, 372], [128, 378]], dtype=float)

    tf = ProjectiveTransform.from_estimate(src, dst)
    if not tf:
        raise RuntimeError("could not estimate the synthetic homography")

    img = warp(tex, tf.inverse, output_shape=out_shape, order=1, cval=0.96)
    return img, np.asarray(tf.params)


def load_facade(path: str | Path = "data/facade.jpg"):
    """
    Load `path` if it exists, otherwise fall back to the synthetic facade.

    Returns
    -------
    img : (H, W, 3) float array in [0, 1]
    H_gt : (3, 3) array or None
        None when a real photograph is used, since no ground truth is available.
    """
    from skimage.io import imread
    from skimage.util import img_as_float

    p = Path(path)
    if p.exists():
        return img_as_float(imread(p))[..., :3], None
    return synthetic_facade()
