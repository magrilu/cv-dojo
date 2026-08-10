# Computer Vision Dojo

*a geometric way*

![](https://raw.githubusercontent.com/magrilu/cv-dojo/main/images/cv_dojo.jpg)

Hands-on notebooks in 3D computer vision — projective geometry, multiple-view
relations, camera calibration, reconstruction, robust fitting.

**→ [magrilu.github.io/cv-dojo](https://magrilu.github.io/cv-dojo/)** — the
notebooks are meant to be read there. Some of it is written, some is still in
preparation.

Each notebook runs top to bottom with no manual input, and opens in Colab with
one click. Most examples are built around a small origami house folded from one
sheet of paper: every dimension follows from the size of the sheet, so the
reconstructions can be checked against a ground truth you can fold yourself.

By [Luca Magri](https://magrilu.github.io/), Politecnico di Milano.

## Layout

```
notebooks/    one folder per topic
data/         images, annotations, and the metric model of the origami house
matlab/       the original scripts from the Politecnico exercise sessions
images/       illustrations used on the site
```

## Running the notebooks

```bash
git clone https://github.com/magrilu/cv-dojo.git
cd cv-dojo
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

## Building the site

Requires [Quarto](https://quarto.org). The virtual environment must be active,
or Quarto will fall back to the system Python and fail to find Jupyter:

```bash
source .venv/bin/activate
quarto render
quarto publish gh-pages
```

Notebooks are committed without outputs; the rendered results live in
`_freeze/`, which is tracked on purpose so the site can be built without
rerunning any code.

## Contributing

Corrections are welcome — mistakes, unclear passages, a derivation that does not
hold. Open an issue or write to me.

## License

Code MIT; text and figures CC BY-NC-ND 4.0. See `LICENSE.md`, and `CITATION.cff`
if you would like to cite this work.
