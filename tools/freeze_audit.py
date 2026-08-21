"""Report figures in _freeze that no rendered result refers to.

Run from the repository root.  Nothing is deleted unless --delete is passed.
"""

import argparse
import json
import re
from pathlib import Path

FIGURE_REF = re.compile(r"figure-html/([^\"')\s]+\.(?:png|svg|jpg|jpeg|pdf))")


def referenced_figures(freeze_dir):
    """Every figure filename mentioned by any execute-results file."""
    names = set()
    for result in (freeze_dir / "execute-results").glob("*.json"):
        payload = json.loads(result.read_text())
        names.update(FIGURE_REF.findall(json.dumps(payload)))
    return names


def notebook_for(freeze_dir, root):
    """The source document a freeze directory belongs to, if it still exists."""
    relative = freeze_dir.relative_to(root / "_freeze")
    for suffix in (".ipynb", ".qmd", ".md"):
        candidate = root / relative.with_suffix(suffix)
        if candidate.exists():
            return candidate
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--delete", action="store_true", help="actually remove the orphans")
    parser.add_argument("--root", default=".", help="repository root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    freeze = root / "_freeze"

    if not freeze.exists():
        print("no _freeze directory here - are you in the repository root?")
        return

    total_orphans = 0
    total_bytes = 0

    for results in sorted(freeze.rglob("execute-results")):
        entry = results.parent
        figures = entry / "figure-html"

        source = notebook_for(entry, root)
        label = str(entry.relative_to(freeze))

        if source is None:
            print(f"\n{label}")
            print("  !! no source document - the whole freeze entry is stale")
            continue

        if not figures.exists():
            continue

        keep = referenced_figures(entry)
        on_disk = {p.name for p in figures.iterdir() if p.is_file()}
        orphans = sorted(on_disk - keep)
        missing = sorted(keep - on_disk)

        if not orphans and not missing:
            print(f"\n{label}: {len(on_disk)} figures, all referenced")
            continue

        print(f"\n{label}: {len(on_disk)} on disk, {len(keep)} referenced")

        for name in missing:
            print(f"  !! referenced but absent: {name}")

        for name in orphans:
            path = figures / name
            size = path.stat().st_size
            total_orphans += 1
            total_bytes += size
            print(f"  orphan  {name}  ({size/1024:.0f} kB)")
            if args.delete:
                path.unlink()

    verb = "removed" if args.delete else "found"
    print(f"\n{verb} {total_orphans} orphan figures, {total_bytes/1024/1024:.1f} MB")
    if total_orphans and not args.delete:
        print("re-run with --delete to remove them")


if __name__ == "__main__":
    main()
