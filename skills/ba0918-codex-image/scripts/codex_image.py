#!/usr/bin/env python3
"""Post-processing and acceptance checks for images generated with Codex.

Run with: uv run --with pillow scripts/codex_image.py <subcommand> ...
"""

import argparse
import math
import re
import sys
from pathlib import Path

from PIL import Image

ALPHA_THRESHOLD = 128
SHEET_COLUMNS = 4
MIN_FRAMES, MAX_FRAMES = 2, 16
TEMPLATE_PIXELS_PER_DOT = 10
KINDS = ("pixel", "illustration", "web")
REQUIRED_FIELDS = {
    "pixel": ("canvas_dots", "transparent"),
    "illustration": ("size", "transparent"),
    "web": ("size",),
}


class InputError(Exception):
    """An input the script cannot work with; reported on stderr with a non-zero exit."""


def read_front_matter(path):
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise InputError(f"cannot read series definition {path}: {error}")
    if not lines or lines[0].strip() != "---":
        raise InputError(f"{path}: the series definition must start with a '---' front matter block")
    fields = {}
    for number, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            return fields
        if not line.strip():
            continue
        match = re.fullmatch(r"([a-z_]+):[ ]*(\S+)[ ]*", line)
        if not match:
            raise InputError(f"{path}:{number}: expected 'key: value', got {line!r}")
        fields[match.group(1)] = match.group(2)
    raise InputError(f"{path}: the front matter block is not closed with '---'")


def parse_series(path):
    fields = read_front_matter(path)
    kind = fields.get("kind")
    if kind not in KINDS:
        raise InputError(f"{path}: kind must be one of {', '.join(KINDS)}, got {kind!r}")
    for key in REQUIRED_FIELDS[kind]:
        if key not in fields:
            raise InputError(f"{path}: kind {kind} requires {key}, which is missing")
    series = {"kind": kind}
    if "canvas_dots" in REQUIRED_FIELDS[kind]:
        value = fields["canvas_dots"]
        if not re.fullmatch(r"[1-9][0-9]*", value):
            raise InputError(f"{path}: canvas_dots must be a positive integer, got {value!r}")
        series["canvas_dots"] = int(value)
    if "size" in REQUIRED_FIELDS[kind]:
        value = fields["size"]
        match = re.fullmatch(r"([1-9][0-9]*)x([1-9][0-9]*)", value)
        if not match:
            raise InputError(f"{path}: size must be WIDTHxHEIGHT in pixels, got {value!r}")
        series["size"] = (int(match.group(1)), int(match.group(2)))
    if "transparent" in REQUIRED_FIELDS[kind]:
        value = fields["transparent"]
        if value not in ("true", "false"):
            raise InputError(f"{path}: transparent must be true or false, got {value!r}")
        series["transparent"] = value == "true"
    return series


def load_image(path):
    try:
        with Image.open(path) as image:
            return image.convert("RGBA")
    except OSError as error:
        raise InputError(f"cannot read image {path}: {error}")


def save_image(image, path):
    try:
        image.save(path)
    except OSError as error:
        raise InputError(f"cannot write {path}: {error}")


def sample_grid(image, columns, rows):
    """Pick the colour at the centre of each cell of a columns x rows grid laid over the image."""
    width, height = image.size
    xs = [(2 * i + 1) * width // (2 * columns) for i in range(columns)]
    ys = [(2 * j + 1) * height // (2 * rows) for j in range(rows)]
    source = image.load()
    out = Image.new("RGBA", (columns, rows))
    target = out.load()
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            target[i, j] = source[x, y]
    return out


def harden_alpha(image):
    """Make each pixel fully opaque or fully transparent (0, 0, 0, 0) at the alpha threshold."""
    out = image.copy()
    pixels = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = pixels[x, y]
            pixels[x, y] = (r, g, b, 255) if a >= ALPHA_THRESHOLD else (0, 0, 0, 0)
    return out


def process_pixel(series, raw):
    dots = series["canvas_dots"]
    final = sample_grid(raw, dots, dots)
    if series["transparent"]:
        return harden_alpha(final)
    return final.convert("RGB")


def sheet_rows(frames):
    return math.ceil(frames / SHEET_COLUMNS)


def check_frames(frames):
    if not MIN_FRAMES <= frames <= MAX_FRAMES:
        raise InputError(f"--frames must be between {MIN_FRAMES} and {MAX_FRAMES}, got {frames}")


def load_stand(path):
    stand = load_image(path)
    if stand.width != stand.height:
        raise InputError(f"the stand image {path} must be square, got {stand.width}x{stand.height}")
    return stand


def make_template(stand, frames):
    """The stand enlarged to 10 px per dot; with frames, placed in the top-left cell of an empty sheet."""
    cell = stand.width * TEMPLATE_PIXELS_PER_DOT
    large = stand.resize((cell, cell), Image.NEAREST)
    if frames is None:
        return large
    sheet = Image.new("RGBA", (cell * SHEET_COLUMNS, cell * sheet_rows(frames)), (0, 0, 0, 0))
    sheet.paste(large, (0, 0))
    return sheet


def crop_to_ratio(image, size):
    """Cut the largest centred region with the same aspect ratio as size."""
    width, height = image.size
    target_width, target_height = size
    if width * target_height > height * target_width:
        crop_width = round(height * target_width / target_height)
        left = (width - crop_width) // 2
        return image.crop((left, 0, left + crop_width, height))
    crop_height = round(width * target_height / target_width)
    top = (height - crop_height) // 2
    return image.crop((0, top, width, top + crop_height))


def cover_opaque(image, size):
    """Crop the centre to the ratio of size, scale it to exactly size, and drop the alpha channel."""
    return crop_to_ratio(image, size).resize(size, Image.LANCZOS).convert("RGB")


def process_web(series, raw):
    return cover_opaque(raw, series["size"])


def fit_within(image, size):
    """Scale the whole image to fit inside size and centre it on a transparent canvas."""
    width, height = image.size
    target_width, target_height = size
    scale = min(target_width / width, target_height / height)
    scaled_size = (max(1, round(width * scale)), max(1, round(height * scale)))
    scaled = image.resize(scaled_size, Image.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    canvas.paste(scaled, ((target_width - scaled_size[0]) // 2, (target_height - scaled_size[1]) // 2))
    return canvas


def process_illustration(series, raw):
    if series["transparent"]:
        return fit_within(raw, series["size"])
    return cover_opaque(raw, series["size"])


PROCESSORS = {
    "illustration": process_illustration,
    "pixel": process_pixel,
    "web": process_web,
}


def build_parser():
    parser = argparse.ArgumentParser(prog="codex_image.py")
    sub = parser.add_subparsers(dest="command", required=True)

    template = sub.add_parser("template")
    template.add_argument("--stand", required=True)
    template.add_argument("--frames", type=int)
    template.add_argument("--out", required=True)

    process = sub.add_parser("process")
    process.add_argument("--series", required=True)
    process.add_argument("--raw", required=True)
    process.add_argument("--out", required=True)
    process.add_argument("--frames", type=int)
    process.add_argument("--stand")
    process.add_argument("--no-ground", action="store_true")

    check = sub.add_parser("check")
    check.add_argument("--series", required=True)
    check.add_argument("--raw", required=True)
    check.add_argument("--frames", type=int)
    check.add_argument("--stand")

    preview = sub.add_parser("preview")
    preview.add_argument("--sheet", required=True)
    preview.add_argument("--frames", type=int, required=True)
    preview.add_argument("--out", required=True)
    preview.add_argument("--ms", type=int, default=120)

    return parser


def run_template(args):
    if args.frames is not None:
        check_frames(args.frames)
    stand = load_stand(args.stand)
    save_image(make_template(stand, args.frames), args.out)
    return 0


def run_process(args):
    series = parse_series(args.series)
    raw = load_image(args.raw)
    final = PROCESSORS[series["kind"]](series, raw)
    save_image(final, args.out)
    return 0


def run_check(args):
    parse_series(args.series)
    return 0


COMMANDS = {
    "template": run_template,
    "process": run_process,
    "check": run_check,
}


def main(argv=None):
    args = build_parser().parse_args(argv)
    handler = COMMANDS.get(args.command)
    if handler is None:
        print(f"{args.command} is not implemented", file=sys.stderr)
        return 2
    try:
        return handler(args)
    except InputError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
