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
