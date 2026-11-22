"""Deliver the pre-rendered news poster to the grader output directory.

The poster image (news.png) was rendered beforehand with render.py
(Pillow, build time only) and is committed alongside this script. At
grading time the environment is standard library only and the
repository is mounted read-only, so this program does no rendering:
it simply copies the committed poster to $MAKEFUN_OUTPUT_DIR/entry.png,
following the kit's copy pattern.
"""

import os
import shutil
import sys
from pathlib import Path


def find_poster() -> Path:
    """Return the path of the poster stored next to this script."""
    return Path(__file__).resolve().parent / "news.png"


def resolve_output_dir() -> Path:
    """Return the directory the grader expects the entry in.

    Uses MAKEFUN_OUTPUT_DIR when the grader provides it and falls
    back to the current working directory for local runs.
    """
    raw = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if raw:
        return Path(raw)
    return Path.cwd()


def main() -> int:
    poster = find_poster()
    if not poster.is_file():
        print(f"error: poster not found next to script: {poster}", file=sys.stderr)
        return 1

    output_dir = resolve_output_dir()
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(poster, output_dir / "entry.png")
    except OSError as exc:
        print(f"error: cannot write entry.png: {exc}", file=sys.stderr)
        return 1

    print(f"wrote entry.png ({poster.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
