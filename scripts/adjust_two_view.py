"""
Adjust the two-view correspondences by dragging them into place.

The points start where the idealized model projects into each photograph, which
is already close, so this is a matter of nudging rather than clicking from
scratch.

    source .venv/bin/activate
    python scripts/adjust_two_view.py

Controls
--------
    click a marker      select it (it turns solid)
    drag                move it
    arrow keys          nudge by 1 pixel
    shift + arrows      nudge by 0.2 pixel
    tab                 next point
    z                   toggle the magnifier follow mode
    s                   save and quit
    q                   quit without saving

The magnifier at the bottom shows the neighbourhood of the selected point in
both views at once, which is where the actual precision comes from: zoom in,
then nudge with the arrow keys until the cross sits on the corner.

Luca Magri - Politecnico di Milano
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
for _backend in ("macosx", "TkAgg", "QtAgg"):
    try:
        matplotlib.use(_backend)
        break
    except Exception:
        continue
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

ACCENT, SEL = "#F46D43", "#3288BD"

# Points to annotate. The house vertices are seeded by projecting the model;
# the door corners have no 3D counterpart, so they start from a rough guess.
HOUSE = {
    "X0": "front-left-bottom corner",
    "X1": "front-right-bottom corner",
    "X4": "front-left eave",
    "X5": "front-right eave",
    "X8": "left ridge end",
    "X9": "right ridge end",
}
DOOR = {
    "D0": "door top-left",
    "D1": "door top-right",
    "D2": "door bottom-right",
    "D3": "door bottom-left",
}
DOOR_SEED = {
    "IMG_4331.jpeg": {"D0": (686, 1464), "D1": (764, 1448),
                      "D2": (772, 1528), "D3": (694, 1546)},
    "IMG_4337.jpeg": {"D0": (709, 1381), "D1": (806, 1342),
                      "D2": (812, 1452), "D3": (711, 1490)},
}


def repo_root() -> Path:
    here = Path.cwd().resolve()
    for p in [here, *here.parents]:
        if (p / "data" / "dojo_house" / "ideal_house.json").exists():
            return p
    raise SystemExit("Run this from inside the repository.")


class Adjuster:
    def __init__(self, root: Path):
        self.root = root
        ann = root / "data" / "dojo_house" / "annotations"
        self.ann_dir = ann
        cams = json.loads((ann / "two_view_cameras.json").read_text())
        model = json.loads((root / "data" / "dojo_house" / "ideal_house.json").read_text())

        self.views = cams["images"]
        self.P = [np.array(p, float) for p in cams["P"]]
        self.images = [np.asarray(Image.open(
            root / "data" / "dojo_house" / "selected" / v)) for v in self.views]

        self.ids = list(HOUSE) + list(DOOR)
        self.labels = {**HOUSE, **DOOR}

        # seed: project the model, then override the door with the rough guess
        self.pts = []
        for view, P in zip(self.views, self.P):
            d = {}
            for k in HOUSE:
                X = np.array(model["vertices"][k] + [1.0])
                q = P @ X
                d[k] = q[:2] / q[2]
            for k, v in DOOR_SEED[view].items():
                d[k] = np.array(v, float)
            self.pts.append(d)

        # if a previous session exists, start from it instead
        prev = ann / "two_view_matches.json"
        if prev.exists():
            old = json.loads(prev.read_text())
            have = {m["id"]: m for m in old.get("matches", [])}
            for k in self.ids:
                if k in have:
                    self.pts[0][k] = np.array(have[k]["x"], float)
                    self.pts[1][k] = np.array(have[k]["xp"], float)
            print(f"starting from the existing {prev.name}")

        self.sel = 0            # index into self.ids
        self.drag = None        # (view index, id) while dragging
        self.follow = True
        self._build()

    # ---------------------------------------------------------------- figure
    def _build(self):
        self.fig = plt.figure(figsize=(15, 10))
        gs = self.fig.add_gridspec(2, 2, height_ratios=[3, 2], hspace=0.08)
        self.ax = [self.fig.add_subplot(gs[0, i]) for i in range(2)]
        self.mag = [self.fig.add_subplot(gs[1, i]) for i in range(2)]

        self.marks, self.texts = [], []
        for i, (ax, im, view) in enumerate(zip(self.ax, self.images, self.views)):
            ax.imshow(im)
            m, t = {}, {}
            for k in self.ids:
                p = self.pts[i][k]
                m[k], = ax.plot(*p, marker="+", ms=13, mew=2,
                                color=ACCENT, picker=12, zorder=5)
                t[k] = ax.text(p[0] + 11, p[1] - 11, k, fontsize=9, color=SEL,
                               bbox=dict(fc="white", alpha=.7, ec="none", pad=1))
            self.marks.append(m)
            self.texts.append(t)
            P = np.array([self.pts[i][k] for k in self.ids])
            ax.set_xlim(P[:, 0].min() - 160, P[:, 0].max() + 160)
            ax.set_ylim(P[:, 1].max() + 160, P[:, 1].min() - 160)
            ax.set_title(view, fontsize=10)
            ax.set_xticks([]); ax.set_yticks([])

        self.fig.canvas.mpl_connect("pick_event", self.on_pick)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_move)
        self.fig.canvas.mpl_connect("button_release_event", self.on_release)
        self.fig.canvas.mpl_connect("key_press_event", self.on_key)
        self._refresh()

    def _refresh(self):
        cur = self.ids[self.sel]
        for i in range(2):
            for k in self.ids:
                p = self.pts[i][k]
                self.marks[i][k].set_data([p[0]], [p[1]])
                self.marks[i][k].set_color(SEL if k == cur else ACCENT)
                self.marks[i][k].set_markersize(18 if k == cur else 13)
                self.texts[i][k].set_position((p[0] + 11, p[1] - 11))
            if self.follow:
                p = self.pts[i][cur]
                r = 26
                self.mag[i].clear()
                self.mag[i].imshow(self.images[i])
                self.mag[i].set_xlim(p[0] - r, p[0] + r)
                self.mag[i].set_ylim(p[1] + r, p[1] - r)
                self.mag[i].plot(*p, "+", ms=22, mew=1.4, color=SEL)
                self.mag[i].set_xticks([]); self.mag[i].set_yticks([])
        self.fig.suptitle(
            f"{cur} — {self.labels[cur]}      "
            f"[{self.sel + 1}/{len(self.ids)}]      "
            "tab: next   arrows: nudge   shift+arrows: fine   s: save   q: quit",
            fontsize=11)
        self.fig.canvas.draw_idle()

    # ----------------------------------------------------------------- events
    def on_pick(self, event):
        if self.fig.canvas.toolbar and self.fig.canvas.toolbar.mode:
            return
        for i in range(2):
            for k, art in self.marks[i].items():
                if art is event.artist:
                    self.sel = self.ids.index(k)
                    self.drag = (i, k)
                    self._refresh()
                    return

    def on_move(self, event):
        if self.drag is None or event.xdata is None:
            return
        i, k = self.drag
        if event.inaxes is not self.ax[i]:
            return
        self.pts[i][k] = np.array([event.xdata, event.ydata], float)
        self._refresh()

    def on_release(self, _event):
        self.drag = None

    def on_key(self, event):
        cur = self.ids[self.sel]
        step = 0.2 if (event.key or "").startswith("shift+") else 1.0
        key = (event.key or "").replace("shift+", "")
        delta = {"left": (-step, 0), "right": (step, 0),
                 "up": (0, -step), "down": (0, step)}.get(key)
        if delta is not None:
            i = 0 if plt.get_current_fig_manager() else 0
            # nudge in whichever view the mouse last hovered, default the left
            i = getattr(self, "_last_view", 0)
            self.pts[i][cur] = self.pts[i][cur] + np.array(delta)
            self._refresh()
        elif key == "tab":
            self.sel = (self.sel + 1) % len(self.ids)
            self._refresh()
        elif key == "z":
            self.follow = not self.follow
            self._refresh()
        elif key == "1":
            self._last_view = 0; self._refresh()
        elif key == "2":
            self._last_view = 1; self._refresh()
        elif key == "s":
            self.save(); plt.close(self.fig)
        elif key == "q":
            print("quit without saving"); plt.close(self.fig)

    # ------------------------------------------------------------------ save
    def save(self):
        matches = [{"id": k, "label": self.labels[k],
                    "x": [round(float(c), 1) for c in self.pts[0][k]],
                    "xp": [round(float(c), 1) for c in self.pts[1][k]]}
                   for k in self.ids]
        out = {
            "name": "two_view_matches",
            "description": (
                "Correspondences between the two photographs of the Origami "
                "House, placed by hand starting from the projection of the "
                "idealized model. They carry ordinary annotation noise of a few "
                "pixels, which is the point: the synthetic correspondences used "
                "earlier in the same notebook are exact, these are not."),
            "images": {"view": self.views[0], "view_prime": self.views[1]},
            "image_size_px": {"width": 1536, "height": 2048},
            "coordinate_frame": "pixels in the uploaded JPEGs, origin at top-left",
            "matches": matches,
        }
        path = self.ann_dir / "two_view_matches.json"
        path.write_text(json.dumps(out, indent=2) + "\n")
        print(f"written {path}  ({len(matches)} correspondences)")


if __name__ == "__main__":
    print(f"matplotlib backend: {matplotlib.get_backend()}")
    a = Adjuster(repo_root())
    # remember which view the mouse is over, so the arrow keys act there
    def _track(ev):
        for i, ax in enumerate(a.ax):
            if ev.inaxes is ax:
                a._last_view = i
    a.fig.canvas.mpl_connect("motion_notify_event", _track)
    a._last_view = 0
    plt.show()
