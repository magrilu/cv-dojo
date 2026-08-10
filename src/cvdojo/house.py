"""
The Origami House dataset.

Locating and loading the photographs, the hand-made annotations, and the
idealized metric model. Paths are resolved by walking up from the current
directory until the data folder is found, so a notebook behaves the same
whether it runs in place, from the repository root, or from a Colab clone.

Luca Magri - Politecnico di Milano
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .geometry import homogeneous

__all__ = [
    "repo_root", "data_dir", "find_image", "load_image",
    "load_model", "load_annotation", "load_two_view_matches",
]

_MARKER = Path("data") / "dojo_house" / "ideal_house.json"


def repo_root(start: Path | None = None) -> Path:
    """Walk up from `start` until the directory holding the data is found."""
    here = Path(start or Path.cwd()).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / _MARKER).exists():
            return candidate
    raise FileNotFoundError(
        "Could not locate the repository root: no "
        f"data/dojo_house/ideal_house.json found above {here}."
    )


def data_dir() -> Path:
    return repo_root() / "data" / "dojo_house"


def find_image(name: str) -> Path:
    """Absolute path of one of the selected photographs."""
    path = data_dir() / "selected" / name
    if not path.exists():
        raise FileNotFoundError(f"{name} not found in {path.parent}")
    return path


def load_image(name: str) -> np.ndarray:
    """One of the selected photographs, as a uint8 array."""
    from PIL import Image
    return np.asarray(Image.open(find_image(name)))


def load_model() -> dict:
    """The idealized metric model: vertices, edges, dimensions in centimetres."""
    return json.loads((data_dir() / "ideal_house.json").read_text())


def load_annotation(name: str) -> dict:
    """One annotation file from data/dojo_house/annotations/."""
    if not name.endswith(".json"):
        name += ".json"
    return json.loads((data_dir() / "annotations" / name).read_text())


def load_two_view_matches():
    """
    The hand-annotated correspondences between IMG_4331 and IMG_4337.

    Returns
    -------
    x, xp : (8, 3) arrays
        Homogeneous image points in the first and second view.
    labels : list of str
        What each correspondence is: an eave, a door corner, a ridge endpoint.
    """
    ann = load_annotation("two_view_matches")
    x = homogeneous([m["x"] for m in ann["matches"]])
    xp = homogeneous([m["xp"] for m in ann["matches"]])
    return x, xp, [m["label"] for m in ann["matches"]]


def load_two_view_cameras():
    """
    The two camera matrices for IMG_4331 and IMG_4337.

    They come from a COLMAP reconstruction, aligned by a similarity to the
    frame of ideal_house.json, so they map centimetres in the model directly
    to pixels in the uploaded photographs. Within the accuracy of that
    alignment they are the true cameras, and everything derived from them —
    synthetic views, the fundamental matrix, the epipoles — is ground truth.

    Returns
    -------
    P, Pp : (3, 4) arrays
    """
    ann = load_annotation("two_view_cameras")
    P, Pp = (np.asarray(M, float) for M in ann["P"])
    return P, Pp


def project(P, X):
    """Project 3D points (n, 3) or (3,) through P, returning pixel coordinates."""
    X = np.atleast_2d(np.asarray(X, float))
    q = (P @ np.c_[X, np.ones(len(X))].T).T
    return q[:, :2] / q[:, 2, None]


def model_points(ids=None):
    """Vertices of the idealized model, as an (n, 3) array of centimetres."""
    V = load_model()["vertices"]
    ids = list(V) if ids is None else list(ids)
    return np.array([V[i] for i in ids], float), ids
