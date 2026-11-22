"""Tests for the news-image-20261122 entry delivery contract.

Standard library only. The entry program (main.py) copies the
pre-rendered poster (news.png, 1024x1024, <= 1 MiB) to
$MAKEFUN_OUTPUT_DIR/entry.png, byte for byte, and must do so
deterministically under the grader's exact invocation
(python3 -P -s main.py, repository read-only).
"""

import hashlib
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
POSTER = HERE / "news.png"
MAIN = HERE / "main.py"


def png_dimensions(path: Path) -> tuple[int, int]:
    """Read width/height from a PNG IHDR chunk (no Pillow needed)."""
    with open(path, "rb") as fh:
        header = fh.read(33)
    assert header[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG file"
    assert header[12:16] == b"IHDR", "first chunk is not IHDR"
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def run_main(out_dir: Path) -> subprocess.CompletedProcess:
    """Run main.py the way the grader does: -P -s, fresh env var."""
    env = dict(os.environ)
    env["MAKEFUN_OUTPUT_DIR"] = str(out_dir)
    return subprocess.run(
        [sys.executable, "-P", "-s", str(MAIN)],
        cwd=str(HERE),
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


class TestPosterFile(unittest.TestCase):
    def test_poster_is_png_1024x1024(self):
        """news.png exists and its IHDR reports exactly 1024x1024."""
        self.assertTrue(POSTER.is_file(), "news.png missing")
        self.assertEqual(png_dimensions(POSTER), (1024, 1024))

    def test_poster_under_1_mib(self):
        """news.png is at most 1 MiB (the gate limit)."""
        self.assertLessEqual(POSTER.stat().st_size, 1048576)

    def test_poster_is_opaque_rgb(self):
        """news.png is colour type 2 (RGB) or 6 (RGBA) with 8-bit depth."""
        with open(POSTER, "rb") as fh:
            header = fh.read(33)
        bit_depth = header[24]
        colour_type = header[25]
        self.assertEqual(bit_depth, 8)
        self.assertIn(colour_type, (2, 6))


class TestDelivery(unittest.TestCase):
    def test_main_runs_and_writes_entry_png(self):
        """main.py exits 0 and writes entry.png to MAKEFUN_OUTPUT_DIR."""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            result = run_main(out)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((out / "entry.png").is_file())

    def test_output_is_byte_identical_to_poster(self):
        """The delivered entry.png is byte for byte the committed poster."""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            result = run_main(out)
            self.assertEqual(result.returncode, 0, result.stderr)
            produced = (out / "entry.png").read_bytes()
            self.assertEqual(
                hashlib.sha256(produced).hexdigest(),
                hashlib.sha256(POSTER.read_bytes()).hexdigest(),
            )

    def test_two_runs_are_deterministic(self):
        """Two runs of main.py produce byte-identical output."""
        with tempfile.TemporaryDirectory() as tmp:
            out1, out2 = Path(tmp) / "a", Path(tmp) / "b"
            out1.mkdir()
            out2.mkdir()
            self.assertEqual(run_main(out1).returncode, 0)
            self.assertEqual(run_main(out2).returncode, 0)
            self.assertEqual(
                (out1 / "entry.png").read_bytes(),
                (out2 / "entry.png").read_bytes(),
            )

    def test_output_png_is_1024x1024(self):
        """The delivered entry.png itself reports 1024x1024."""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self.assertEqual(run_main(out).returncode, 0)
            self.assertEqual(png_dimensions(out / "entry.png"), (1024, 1024))


class TestPosterContent(unittest.TestCase):
    def test_key_labels_present_as_pixels(self):
        """The poster is not blank: the dark atlas carries a bright
        title band and bright label text on top of it."""
        from PIL import Image

        img = Image.open(POSTER).convert("L")
        title_band = img.crop((0, 0, 1024, 140))
        bright_title = sum(title_band.histogram()[200:])
        self.assertGreater(bright_title, 5000,
                           "title band has no bright pixels")
        hist = img.histogram()
        dark = sum(hist[:60])
        light = sum(hist[200:])
        total = 1024 * 1024
        self.assertGreater(dark, total * 0.15, "poster looks empty/flat")
        self.assertGreater(light, total * 0.02, "no bright title/labels")

    def test_poster_has_red_fire_lines(self):
        """Red 'fire line' pixels exist (the atlas arcs are drawn).
        The core line colour is (255, 120, 100); count those pixels."""
        from PIL import Image

        img = Image.open(POSTER).convert("RGB")
        px = img.load()
        reds = 0
        for y in range(0, 1024, 4):
            for x in range(0, 1024, 4):
                r, g, b = px[x, y]
                if r > 200 and g < 140 and b < 120:
                    reds += 1
        self.assertGreater(reds, 200, "no red fire-line pixels found")


if __name__ == "__main__":
    unittest.main()
