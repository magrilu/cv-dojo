"""Computer Vision Dojo - helper library for the notebooks."""

from .geometry import (
    homogeneous, cartesian, seg_to_line, meet, join,
    normalize_line, H_from_vanishing_line,
)
from .warping import warp_image, fit_to_canvas, image_corners
from .data import load_facade, synthetic_facade, DEFAULT_SEGMENTS
from .plotting import draw_segment, draw_line, show

__version__ = "0.1.0"
