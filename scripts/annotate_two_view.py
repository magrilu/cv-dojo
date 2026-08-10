"""
Click the door corners in the two views and write the correspondence file.

Run it from the repository root with the virtual environment active:

    source .venv/bin/activate
    python scripts/annotate_two_view.py

A window opens on the first photograph, zoomed to the door. Click the four
corners in this order:

    D0  top-left
    D1  top-right
    D2  bottom-right
    D3  bottom-left

Use the magnifier in the toolbar to zoom in before clicking; the clicks are
recorded in full-resolution coordinates whatever the zoom. A wrong click can
be undone with the right mouse button. Middle-click, or press enter, when the
four are in. The second photograph follows.

The six house vertices are taken from the COLMAP session already recorded in
triangulation.json, so they are not clicked again.

Luca Magri - Politecnico di Milano
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("TkAgg")          # an interactive backend is required
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

DOOR = [
    ("D0", "door top-left"),
    ("D1", "door top-right"),
    ("D2", "door bottom-right"),
    ("D3", "door bottom-left"),
]
VIEWS = ["IMG_4331.jpeg", "IMG_4337.jpeg"]
HOUSE_IDS = ["X0", "X1", "X4", "X5", "X8", "X9"]
LABELS = {
    "X0": "front-left-bottom corner", "X1": "front-right-bottom corner",
    "X4": "front-left eave", "X5": "front-right eave",
    "X8": "left ridge end", "X9": "right ridge end",
}


def repo_root() -> Path:
    here = Path.cwd().resolve()
    for p in [here, *here.parents]:
        if (p / "data" / "dojo_house" / "ideal_house.json").exists():
            return p
    raise FileNotFoundError("run this from inside the repository")


def click_door(path: Path, zoom_hint=None) -> np.ndarray:
    img = np.asarray(Image.open(path))
    fig, ax = plt.subplots(figsize=(11, 9))
    ax.imshow(img)
    ax.set_title(f"{path.name}\nclick: " + ", ".join(k for k, _ in DOOR),
                 fontsize=11)
    if zoom_hint is not None:
        u, v, r = zoom_hint
        ax.set_xlim(u - r, u + r)
        ax.set_ylim(v + r, v - r)
    print(f"\n{path.name}: click {', '.join(k for k, _ in DOOR)}"
          "  (right-click undoes, enter finishes)")
    pts = plt.ginput(n=len(DOOR), timeout=0, show_clicks=True)
    plt.close(fig)
    if len(pts) != len(DOOR):
        raise SystemExit(f"got {len(pts)} clicks, expected {len(DOOR)}")
    return np.array(pts, float)


def main() -> None:
    root = repo_root()
    ann = root / "data" / "dojo_house" / "annotations"
    tri = json.loads((ann / "triangulation.json").read_text())

    scale = tri["display_to_colmap_mapping"]["uniform_scale"]
    W = tri["display_to_colmap_mapping"]["uploaded_size"][0]

    def to_display(xc, yc):
        return [W - yc / scale, xc / scale]

    house = {
        v: {i: to_display(*tri["images"][v]["observations_original_colmap_pixels"][i])
            for i in HOUSE_IDS}
        for v in VIEWS
    }

    # a rough centre for the initial zoom, so the door is on screen
    hints = {VIEWS[0]: (730, 1500, 220), VIEWS[1]: (760, 1420, 220)}
    door = {v: click_door(root / "data" / "dojo_house" / "selected" / v, hints[v])
            for v in VIEWS}

    matches = []
    for i in HOUSE_IDS:
        matches.append({"id": i, "label": LABELS[i],
                        "x": [round(c, 1) for c in house[VIEWS[0]][i]],
                        "xp": [round(c, 1) for c in house[VIEWS[1]][i]]})
    for k, (name, label) in enumerate(DOOR):
        matches.append({"id": name, "label": label,
                        "x": [round(float(c), 1) for c in door[VIEWS[0]][k]],
                        "xp": [round(float(c), 1) for c in door[VIEWS[1]][k]]})

    out = {
        "name": "two_view_matches",
        "description": (
            "Hand-clicked correspondences between the two photographs of the "
            "Origami House. The six house vertices come from the COLMAP session "
            "used for the triangulation notebook; the four door corners were "
            "clicked separately. They carry ordinary annotation noise, a few "
            "pixels each — which is the point: the synthetic correspondences in "
            "the same notebook are exact, these are not."
        ),
        "images": {"view": VIEWS[0], "view_prime": VIEWS[1]},
        "image_size_px": {"width": 1536, "height": 2048},
        "coordinate_frame": "pixels in the uploaded JPEGs, origin at top-left",
        "matches": matches,
    }
    path = ann / "two_view_matches.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nwritten {path}  ({len(matches)} correspondences)")
    print("Check them with:  python scripts/annotate_two_view.py --check")


if __name__ == "__main__":
    import sys
    if "--check" in sys.argv:
        root = repo_root()
        ann = json.loads(
            (root / "data" / "dojo_house" / "annotations" / "two_view_matches.json").read_text())
        fig, axes = plt.subplots(1, 2, figsize=(15, 9))
        for ax, key, side in zip(axes, ("x", "xp"), ("view", "view_prime")):
            name = ann["images"][side]
            ax.imshow(np.asarray(Image.open(
                root / "data" / "dojo_house" / "selected" / name)))
            p = np.array([m[key] for m in ann["matches"]])
            ax.scatter(p[:, 0], p[:, 1], s=70, facecolors="none",
                       edgecolors="#F46D43", lw=2)
            for m, q in zip(ann["matches"], p):
                ax.text(q[0] + 12, q[1] - 12, m["id"], fontsize=10,
                        bbox=dict(fc="white", alpha=.75, ec="none", pad=1.5))
            ax.set_xlim(p[:, 0].min() - 140, p[:, 0].max() + 140)
            ax.set_ylim(p[:, 1].max() + 140, p[:, 1].min() - 140)
            ax.set_title(name)
            ax.axis("off")
        plt.tight_layout()
        plt.show()
    else:
        main()
