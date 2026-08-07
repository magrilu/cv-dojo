# Setup, step by step

Everything below is run once. Replace `~/repos` with wherever
`magrilu.github.io` already lives.

## 1. Create the repository on GitHub

Go to https://github.com/new
- Repository name: `cv-dojo`
- Public
- Do **not** tick "Add a README" / .gitignore / licence — the folder already
  has them, and an initialised repo would conflict.

## 2. Put this folder next to your site

    cd ~/repos
    # unzip cv-dojo.zip here, so you end up with ~/repos/cv-dojo

Check it is *beside* `magrilu.github.io`, not inside it.

## 3. First push

    cd ~/repos/cv-dojo
    git init
    git add .
    git commit -m "Initial commit: affine rectification notebook + scaffolding"
    git branch -M main
    git remote add origin git@github.com:magrilu/cv-dojo.git
    git push -u origin main

Reload the repo page on GitHub — the files should be there.

## 4. Python environment

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

Check the notebook runs:

    jupyter lab notebooks/rectification/affine.ipynb

## 5. Quarto

Install from https://quarto.org/docs/get-started/ (a .deb / .pkg, one minute).

    quarto preview

This opens a browser with live reload. Iterate here.

## 6. Publish

    quarto publish gh-pages

First run asks for confirmation, then creates the `gh-pages` branch, pushes the
built site, and adds `.nojekyll` (without which GitHub would run the output
through Jekyll and drop every `_`-prefixed folder — the classic "site with no
CSS" failure).

Then check on GitHub: Settings → Pages → source is `gh-pages` / `(root)`.

Wait a couple of minutes: https://magrilu.github.io/cv-dojo/

From now on, publishing is just `quarto publish gh-pages`. Your source lives on
`main`; `gh-pages` is machine-written and never edited by hand — the same split
you already have between `source` and `master` on the site repo.

## 7. Look at it next to your site

Now decide whether the visual gap bothers you. If it does, open
`assets/custom.scss` and copy in the real values from your al-folio
`_sass/_themes.scss` (`--global-theme-color`) and `_sass/_variables.scss`.

## 8. Menu entry on magrilu.github.io

In the site repo, on the `source` branch, find the page that generates the
`teaching` dropdown in `_pages/` and copy its pattern:

    - title: CV Dojo
      permalink: https://magrilu.github.io/cv-dojo/

An absolute URL works fine as a permalink. Then:

    ./bin/deploy --user

(The exact YAML key differs between al-folio versions — follow whatever your
existing dropdown does rather than the snippet above.)

## 9. Zenodo

https://zenodo.org → log in with GitHub → enable the toggle for `cv-dojo`.
Then on GitHub: Releases → Create a new release → tag `v0.1.0`. The DOI is
minted automatically, and again on every later release.

## Troubleshooting

**`git push` permission denied** — your SSH key is not set up. Quick fix: use
`git remote set-url origin https://github.com/magrilu/cv-dojo.git` and
authenticate with a personal access token instead.

**Site published but unstyled** — `.nojekyll` is missing from `gh-pages`, or
Pages is pointing at the wrong branch.

**Colab badge 404** — the branch in the badge URL must match yours (`main`),
and the repository must be public.
