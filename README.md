# Computer Vision Dojo

Hands-on notebooks in geometric computer vision — projective geometry of the
plane, homography estimation, rectification, robust fitting, matching.

**→ [magrilu.github.io/cv-dojo](https://magrilu.github.io/cv-dojo/)**

Each notebook is paired with an algorithm from the accompanying notes, runs top
to bottom with no manual input, and opens in Colab with one click. Interactive
point selection is available as an optional cell, for use during lectures.

By [Luca Magri](https://magrilu.github.io/), Politecnico di Milano.

## Contents

| Topic | Notebook |
|---|---|
| Affine rectification | [`notebooks/rectification/affine.ipynb`](notebooks/rectification/affine.ipynb) |

The original MATLAB scripts from the Politecnico exercise sessions are kept
under [`matlab/`](matlab/).

## Running locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

To build the website (requires [Quarto](https://quarto.org)):

```bash
quarto preview              # live reload
quarto publish gh-pages     # build and deploy
```

## Course tracks

- [IACV — Politecnico di Milano](https://magrilu.github.io/cv-dojo/tracks/iacv.html)
- [Bocconi](https://magrilu.github.io/cv-dojo/tracks/bocconi.html)

## License

Text and figures CC BY 4.0; code MIT. Attribution appreciated — see
`CITATION.cff`.
