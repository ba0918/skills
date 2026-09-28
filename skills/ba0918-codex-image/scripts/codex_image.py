#!/usr/bin/env python3
"""Post-processing and acceptance checks for images generated with Codex.

Run with: uv run --with pillow scripts/codex_image.py <subcommand> ...
"""

import argparse
import re
import sys
from pathlib import Path

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


def run_check(args):
    parse_series(args.series)
    return 0


COMMANDS = {
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
