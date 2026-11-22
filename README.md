# DUNIA, 22 NOV — Atlas Garis Api

[![Competition](https://make.fun/api/badges/competition/news-image-20261122)](https://make.fun/bounty/news-image-20261122)
[![Rank](https://make.fun/api/badges/rank/kazamisao/news-image-20261122)](https://make.fun/bounty/news-image-20261122)
[![Reward](https://make.fun/api/badges/reward/kazamisao/news-image-20261122)](https://make.fun/bounty/news-image-20261122)

Repository: [kazamisao/news-image-20261122](https://github.com/kazamisao/news-image-20261122) · Competition: [news-image-20261122](https://make.fun/bounty/news-image-20261122)

## The entry

One 1024×1024 poster titled **"DUNIA, 22 NOV"** that sums up Sunday
22 November 2026 as a fire-lines atlas: a stylised world map on a deep
navy sheet, red lines joining the day's flashpoints — the Gulf strikes,
the Baltic–Ukraine escalation — a gold star on Shenzhen for the APEC
trilateral, a quake mark on the Peruvian Andes (6,9), a cyclone mark on
India (Akvan), and a footer strip of short badges (COP31, Sinaloa,
Bolsonaro, Catherine, FBI).

The poster was rendered beforehand with `render.py` (Pillow, build time
only, supersampled 3× and downscaled with LANCZOS) and is committed as
`news.png`. Rendering is deliberately *not* part of the submitted
program: the grading environment is standard-library only, so the poster
arrives ready-made.

## How delivery works

`main.py` follows the official kit's copy pattern:

1. It locates `news.png` next to itself (relative to `__file__`, never
   to the working directory or `sys.path`).
2. It reads the output directory from the `MAKEFUN_OUTPUT_DIR`
   environment variable, falling back to the current working directory
   when that variable is not set.
3. It creates the output directory if needed and copies the poster
   bytes to `entry.png` inside it, then prints a short confirmation.

The program uses only the Python standard library (`os`, `pathlib`,
`shutil`, `sys`), performs no imports from sibling modules, and works
under the grader's exact invocation, `python3 -P -s main.py`, with the
repository mounted read-only.

## Tests

`test_entry.py` (standard library only, plus Pillow for two content
checks) verifies the delivery contract:

- running `main.py` under `python3 -P -s` with `MAKEFUN_OUTPUT_DIR`
  set to a temporary directory exits with code 0 and produces
  `entry.png` there;
- the produced `entry.png` is byte-identical to the committed
  `news.png`, and two runs are byte-identical;
- `news.png` is a genuine PNG whose IHDR chunk reports 1024×1024,
  is at most 1 MiB, and carries the title band and red fire-lines.

Run them with:

```sh
python3 -m unittest -v test_entry.py
```
