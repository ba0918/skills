import math
import random
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "ba0918-codex-image"
    / "scripts"
    / "codex_image.py"
)


def run_script(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *[str(a) for a in args]],
        capture_output=True,
        text=True,
    )


@pytest.fixture
def run():
    return run_script


@pytest.fixture
def write_series(tmp_path):
    def write(**fields):
        lines = ["---"] + [f"{key}: {value}" for key, value in fields.items()] + ["---", ""]
        path = tmp_path / "series.md"
        path.write_text("\n".join(lines) + "Style notes.\n", encoding="utf-8")
        return path

    return write


@pytest.fixture
def save_png(tmp_path):
    def save(image, name):
        path = tmp_path / name
        image.save(path)
        return path

    return save


def blank(width, height, color=(0, 0, 0, 0)):
    return Image.new("RGBA", (width, height), color)


def pixels(image):
    return [image.getpixel((x, y)) for y in range(image.height) for x in range(image.width)]


def sprite(dots, seed=1):
    """A dots x dots sprite: an opaque random-coloured disc on a fully transparent background."""
    rng = random.Random(seed)
    image = blank(dots, dots)
    centre = (dots - 1) / 2
    for y in range(dots):
        for x in range(dots):
            if (x - centre) ** 2 + (y - centre) ** 2 <= (dots * 0.4) ** 2:
                image.putpixel((x, y), (rng.randrange(256), rng.randrange(256), rng.randrange(256), 255))
    return image


def figure(width, height, seed=2):
    """A fully opaque block of random colours, used as a character in sheet tests."""
    rng = random.Random(seed)
    image = Image.new("RGBA", (width, height))
    for y in range(height):
        for x in range(width):
            image.putpixel((x, y), (rng.randrange(256), rng.randrange(256), rng.randrange(256), 255))
    return image


def place(character, left, top, dots):
    """A dots x dots transparent cell with the character pasted at (left, top)."""
    cell = blank(dots, dots)
    cell.paste(character, (left, top))
    return cell


def sheet(cells, dots, scale=1):
    """Lay the cells out four to a row, then enlarge by scale with nearest-neighbour."""
    rows = math.ceil(len(cells) / 4)
    image = blank(dots * 4, dots * rows)
    for index, cell in enumerate(cells):
        image.paste(cell, ((index % 4) * dots, (index // 4) * dots))
    return image.resize((image.width * scale, image.height * scale), Image.NEAREST)
