#!/usr/bin/env python3
"""Post-processing and acceptance checks for images generated with Codex.

Run with: uv run --with pillow scripts/codex_image.py <subcommand> ...
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path

from PIL import GifImagePlugin, Image, ImageChops

ALPHA_THRESHOLD = 128
SHEET_COLUMNS = 4
MIN_FRAMES, MAX_FRAMES = 2, 16
TEMPLATE_PIXELS_PER_DOT = 10
DOT_SIZE_TOLERANCE = 0.10  # estimated dot size may differ from the expected one by this fraction
MAX_STAND_DIFFERENCE = 0.05  # share of top-left dots allowed to differ from the stand
COLOUR_DIFFERENCE = 60  # summed RGB difference above which two opaque dots differ
CORNER_FRACTION = 0.02  # side of the corner squares that must be clear, as a share of each edge
RATIO_TOLERANCE = 0.05  # a web raw's aspect ratio may differ from the size's by this fraction
PREVIEW_SIDE = 256  # a preview frame is enlarged by whole steps to about this many pixels
PREVIEW_BACKGROUND = (200, 200, 200, 255)
PEAK_CORRELATION = 0.3  # how far a repeating edge spacing must rise above the dip before it
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


def save_image(image, path, **options):
    try:
        image.save(path, **options)
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


def animation_inputs(series, frames, stand_path):
    """Validate an animation request and return the stand; the sheet rules only fit transparent pixel sprites."""
    check_frames(frames)
    if series["kind"] != "pixel" or not series["transparent"]:
        raise InputError("--frames needs a series with kind: pixel and transparent: true")
    if stand_path is None:
        raise InputError("--frames needs --stand, the adopted stand image of the character")
    stand = load_stand(stand_path)
    if stand.width != series["canvas_dots"]:
        raise InputError(
            f"the stand image is {stand.width} dots wide but the series has canvas_dots: {series['canvas_dots']}"
        )
    return harden_alpha(stand)


def cell_box(index, dots):
    left = (index % SHEET_COLUMNS) * dots
    top = (index // SHEET_COLUMNS) * dots
    return (left, top, left + dots, top + dots)


def opaque_rows(cell):
    """Indices of the rows that hold at least one opaque pixel, top to bottom."""
    alpha = cell.getchannel("A")
    return [y for y in range(cell.height) if alpha.crop((0, y, cell.width, y + 1)).getbbox()]


def ground_shifts(sheet, dots, frames):
    """How far each frame must move down so its feet sit on the stand's feet.

    Returns (shifts, overflowing): shifts maps frame index to rows to move down (negative is up);
    overflowing lists the frame numbers (1-based) whose body would leave the top of the cell.
    """
    stand_rows = opaque_rows(sheet.crop(cell_box(0, dots)))
    if not stand_rows:
        raise InputError("the stand image has no opaque dot to find its feet")
    ground = stand_rows[-1]
    shifts, overflowing = {}, []
    for index in range(1, frames):
        rows = opaque_rows(sheet.crop(cell_box(index, dots)))
        if not rows:
            continue
        shift = ground - rows[-1]
        if rows[0] + shift < 0:
            overflowing.append(index + 1)
        shifts[index] = shift
    return shifts, overflowing


def apply_shifts(sheet, dots, shifts):
    out = sheet.copy()
    for index, shift in shifts.items():
        box = cell_box(index, dots)
        cell = sheet.crop(box)
        moved = Image.new("RGBA", (dots, dots), (0, 0, 0, 0))
        moved.paste(cell, (0, shift))
        out.paste(moved, box[:2])
    return out


def sample_sheet(raw, dots, frames):
    """The raw sheet picked on the expected dot grid, with alpha made fully opaque or transparent."""
    return harden_alpha(sample_grid(raw, dots * SHEET_COLUMNS, dots * sheet_rows(frames)))


def assemble_sheet(sampled, dots, frames, stand):
    """Put the original stand back in the top-left cell and clear the cells after the last frame."""
    sheet = sampled.copy()
    sheet.paste(stand, (0, 0))
    empty = Image.new("RGBA", (dots, dots), (0, 0, 0, 0))
    for index in range(frames, SHEET_COLUMNS * sheet_rows(frames)):
        sheet.paste(empty, cell_box(index, dots)[:2])
    return sheet


def overflow_message(overflowing):
    return (
        "aligning the feet would push frame "
        + ", frame ".join(str(n) for n in overflowing)
        + " above the top of its cell"
    )


def process_sheet(series, raw, frames, stand, align_feet):
    dots = series["canvas_dots"]
    sheet = assemble_sheet(sample_sheet(raw, dots, frames), dots, frames, stand)
    if not align_feet:
        return sheet
    shifts, overflowing = ground_shifts(sheet, dots, frames)
    if overflowing:
        raise InputError(
            overflow_message(overflowing)
            + "; regenerate the sheet, or pass --no-ground if the motion leaves the ground"
        )
    return apply_shifts(sheet, dots, shifts)


def edge_profile(image, axis):
    """Summed colour and alpha change between neighbouring columns (axis 0) or rows (axis 1)."""
    if axis == 1:
        image = image.transpose(Image.TRANSPOSE)
    width, height = image.size
    if width < 2:
        return []
    change = ImageChops.difference(image.crop((1, 0, width, height)), image.crop((0, 0, width - 1, height)))
    profile = [0.0] * (width - 1)
    for band in change.split():
        means = band.convert("F").resize((width - 1, 1), Image.BOX)
        for x in range(width - 1):
            profile[x] += means.getpixel((x, 0))
    return profile


def autocorrelation(profile):
    mean = sum(profile) / len(profile)
    centred = [value - mean for value in profile]
    variance = sum(value * value for value in centred)
    if variance <= 1e-9:
        return None
    return [
        sum(centred[i] * centred[i + lag] for i in range(len(centred) - lag)) / variance
        for lag in range(len(centred) // 2 + 2)
    ]


def strongest_near(correlation, lag):
    """The highest correlation within one lag of lag: an uneven dot size spreads a peak over neighbours."""
    if lag + 1 >= len(correlation):
        return None
    return max(correlation[lag - 1 : lag + 2])


def estimate_dot_size(image, axis):
    """The spacing of repeating edges along the axis in pixels, or None when no spacing repeats.

    A spacing counts when its autocorrelation rises clearly above the dip before it and repeats
    at twice the spacing; a smooth outline correlates at every short lag and never dips.
    """
    profile = edge_profile(image, axis)
    correlation = autocorrelation(profile) if len(profile) >= 8 else None
    if correlation is None:
        return None
    for lag in range(2, len(correlation) - 1):
        value = correlation[lag]
        if value < correlation[lag - 1] or value < correlation[lag + 1]:
            continue
        if value - min(correlation[lag // 2 : lag]) < PEAK_CORRELATION:
            continue
        harmonic = strongest_near(correlation, 2 * lag)
        if harmonic is None or harmonic < PEAK_CORRELATION / 2:
            continue
        lags = (lag - 1, lag, lag + 1)
        weights = [max(correlation[l], 0.0) for l in lags]
        return sum(w * l for w, l in zip(weights, lags)) / sum(weights)
    return None


def judge_dot_size(raw, dots, columns, rows):
    """Reasons the dot size fails, what could not be estimated, and the estimates as measures."""
    reasons, undetermined, measures = [], [], {}
    for axis, name, length, count in ((0, "horizontal", raw.width, dots * columns), (1, "vertical", raw.height, dots * rows)):
        expected = length / count
        estimate = estimate_dot_size(raw, axis)
        measures["dot_size_x" if axis == 0 else "dot_size_y"] = estimate
        if estimate is None:
            undetermined.append(f"the {name} dot size could not be estimated (expected {expected:.1f} px)")
        elif abs(estimate - expected) > DOT_SIZE_TOLERANCE * expected:
            reasons.append(
                f"the {name} dot size is about {estimate:.1f} px, expected {expected:.1f} px within 10%"
            )
    return reasons, undetermined, measures


def dots_differ(a, b):
    opaque_a, opaque_b = a[3] >= ALPHA_THRESHOLD, b[3] >= ALPHA_THRESHOLD
    if opaque_a != opaque_b:
        return True
    return opaque_a and sum(abs(x - y) for x, y in zip(a[:3], b[:3])) > COLOUR_DIFFERENCE


def judge_stand(sampled, stand, dots):
    """Reasons the top-left frame fails against the stand, and the share of its dots that differ."""
    top_left = sampled.crop(cell_box(0, dots))
    differing = sum(
        dots_differ(top_left.getpixel((x, y)), stand.getpixel((x, y))) for y in range(dots) for x in range(dots)
    )
    share = differing / (dots * dots)
    if share > MAX_STAND_DIFFERENCE:
        return [f"the top-left frame differs from the stand in {share:.1%} of its dots (at most 5% allowed)"], share
    return [], share


def opaque_corners(cell):
    """Names of the cell's corner dots that are opaque."""
    right, bottom = cell.width - 1, cell.height - 1
    corners = {"top-left": (0, 0), "top-right": (right, 0), "bottom-left": (0, bottom), "bottom-right": (right, bottom)}
    return [name for name, xy in corners.items() if cell.getpixel(xy)[3] >= ALPHA_THRESHOLD]


def judge_corners(sampled, dots, frames=None):
    """Reasons a transparent sprite, or each frame of a sheet, has an opaque corner dot."""
    if frames is None:
        corners = opaque_corners(sampled)
        return [f"the {', '.join(corners)} corner dot is opaque, expected transparent"] if corners else []
    reasons = []
    for index in range(frames):
        corners = opaque_corners(sampled.crop(cell_box(index, dots)))
        if corners:
            reasons.append(f"frame {index + 1}: the {', '.join(corners)} corner dot is opaque, expected transparent")
    return reasons


def check_pixel(series, raw):
    dots = series["canvas_dots"]
    reasons, undetermined, measures = judge_dot_size(raw, dots, 1, 1)
    if series["transparent"]:
        reasons += judge_corners(sample_grid(raw, dots, dots), dots)
    return verdict(reasons, undetermined, measures)


def check_sheet(series, raw, frames, stand, align_feet):
    dots = series["canvas_dots"]
    reasons, undetermined, measures = judge_dot_size(raw, dots, SHEET_COLUMNS, sheet_rows(frames))
    sampled = sample_sheet(raw, dots, frames)
    stand_reasons, measures["top_left_diff"] = judge_stand(sampled, stand, dots)
    reasons += stand_reasons
    reasons += judge_corners(sampled, dots, frames)
    if align_feet:
        _, overflowing = ground_shifts(assemble_sheet(sampled, dots, frames, stand), dots, frames)
        if overflowing:
            reasons.append(overflow_message(overflowing))
    return verdict(reasons, undetermined, measures)


def check_illustration(series, raw):
    if not series["transparent"]:
        return verdict([], [])
    corner_width = math.ceil(raw.width * CORNER_FRACTION)
    corner_height = math.ceil(raw.height * CORNER_FRACTION)
    alpha = raw.getchannel("A")
    corners = {
        "top-left": (0, 0),
        "top-right": (raw.width - corner_width, 0),
        "bottom-left": (0, raw.height - corner_height),
        "bottom-right": (raw.width - corner_width, raw.height - corner_height),
    }
    reasons = [
        f"the {name} corner ({corner_width}x{corner_height} px) is not fully transparent"
        for name, (left, top) in corners.items()
        if alpha.crop((left, top, left + corner_width, top + corner_height)).getextrema()[1] > 0
    ]
    return verdict(reasons, [])


def check_web(series, raw):
    width, height = series["size"]
    difference = (raw.width / raw.height) / (width / height) - 1
    if abs(difference) > RATIO_TOLERANCE:
        return verdict(
            [
                f"the aspect ratio {raw.width}x{raw.height} is {difference:+.1%} off {width}x{height}"
                " (within 5% allowed), so the centre crop would cut too much"
            ],
            [],
        )
    return verdict([], [])


CHECKERS = {
    "pixel": check_pixel,
    "illustration": check_illustration,
    "web": check_web,
}


def verdict(reasons, undetermined, measures=None):
    """Any failed item fails the whole; otherwise any item that could not be judged leaves it undetermined."""
    measures = {} if measures is None else measures
    if reasons:
        return {"result": "fail", "reasons": reasons + undetermined, "measures": measures}
    if undetermined:
        return {"result": "undetermined", "reasons": undetermined, "measures": measures}
    return {"result": "pass", "reasons": [], "measures": measures}


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


def preview_frames(sheet, frames):
    """The frames of a finished sheet, enlarged and laid on a plain background, in reading order."""
    dots = sheet.width // SHEET_COLUMNS
    if sheet.width % SHEET_COLUMNS or sheet.height != dots * sheet_rows(frames):
        raise InputError(
            f"a sheet of {frames} frames must be 4 cells wide and {sheet_rows(frames)} cells tall, "
            f"got {sheet.width}x{sheet.height}"
        )
    scale = max(1, PREVIEW_SIDE // dots)
    images = []
    for index in range(frames):
        cell = sheet.crop(cell_box(index, dots)).resize((dots * scale, dots * scale), Image.NEAREST)
        backdrop = Image.new("RGBA", cell.size, PREVIEW_BACKGROUND)
        images.append(Image.alpha_composite(backdrop, cell).convert("RGB"))
    return images


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
    check.add_argument("--no-ground", action="store_true")

    preview = sub.add_parser("preview")
    preview.add_argument("--sheet", required=True)
    preview.add_argument("--frames", type=int, required=True)
    preview.add_argument("--out", required=True)
    preview.add_argument("--ms", type=int, default=120)

    return parser


def run_preview(args):
    check_frames(args.frames)
    if args.ms <= 0:
        raise InputError(f"--ms must be a positive number of milliseconds, got {args.ms}")
    images = preview_frames(load_image(args.sheet), args.frames)
    write_gif(images, args.out, args.ms)
    return 0


def write_gif(images, path, ms):
    """An endlessly looping GIF with one frame per image, each lasting ms.

    Not Image.save(save_all=True): it merges identical consecutive frames into one longer frame,
    so an animation that holds a pose would lose frames.
    """
    frames = [image.convert("P", palette=Image.Palette.ADAPTIVE) for image in images]
    chunks, _ = GifImagePlugin.getheader(frames[0], info={"loop": 0, "duration": ms})
    for frame in frames:
        chunks += GifImagePlugin.getdata(frame, duration=ms, include_color_table=True)
    chunks.append(b";")
    try:
        Path(path).write_bytes(b"".join(chunks))
    except OSError as error:
        raise InputError(f"cannot write {path}: {error}")


def run_template(args):
    if args.frames is not None:
        check_frames(args.frames)
    stand = load_stand(args.stand)
    save_image(make_template(stand, args.frames), args.out)
    return 0


def run_process(args):
    series = parse_series(args.series)
    stand = None if args.frames is None else animation_inputs(series, args.frames, args.stand)
    raw = load_image(args.raw)
    if stand is None:
        final = PROCESSORS[series["kind"]](series, raw)
    else:
        final = process_sheet(series, raw, args.frames, stand, align_feet=not args.no_ground)
    save_image(final, args.out)
    return 0


def run_check(args):
    series = parse_series(args.series)
    stand = None if args.frames is None else animation_inputs(series, args.frames, args.stand)
    raw = load_image(args.raw)
    if stand is not None:
        outcome = check_sheet(series, raw, args.frames, stand, align_feet=not args.no_ground)
    else:
        outcome = CHECKERS[series["kind"]](series, raw)
    print(json.dumps(outcome, ensure_ascii=False))
    return 0


COMMANDS = {
    "template": run_template,
    "process": run_process,
    "check": run_check,
    "preview": run_preview,
}


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return COMMANDS[args.command](args)
    except InputError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
