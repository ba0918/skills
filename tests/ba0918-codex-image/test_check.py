import json
import random

import pytest
from PIL import Image

from conftest import blank, figure, place, sheet, sprite


def dot_grid(width, height, pitch_x, pitch_y, seed=3):
    """An image of random-coloured opaque dots, each pitch_x by pitch_y pixels."""
    rng = random.Random(seed)
    image = Image.new("RGBA", (width, height))
    columns = -(-width // pitch_x)
    rows = -(-height // pitch_y)
    for j in range(rows):
        for i in range(columns):
            colour = (rng.randrange(256), rng.randrange(256), rng.randrange(256), 255)
            image.paste(colour, (i * pitch_x, j * pitch_y, (i + 1) * pitch_x, (j + 1) * pitch_y))
    return image


def verdict(result):
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def check_pixel(run, write_series, save_png, raw):
    series = write_series(kind="pixel", canvas_dots=32, transparent="true")
    return verdict(run("check", "--series", series, "--raw", save_png(raw, "raw.png")))


@pytest.mark.parametrize("pitch", [20, 21, 19])
def test_check_passes_a_dot_size_at_or_within_ten_percent_of_the_expected_size(
    run, write_series, save_png, pitch
):
    # 640 px / 32 dots: 20 px per dot expected
    assert check_pixel(run, write_series, save_png, dot_grid(640, 640, pitch, pitch)) == {
        "result": "pass",
        "reasons": [],
    }


@pytest.mark.parametrize("pitch", [24, 16])
def test_check_fails_a_dot_size_outside_ten_percent_of_the_expected_size(
    run, write_series, save_png, pitch
):
    outcome = check_pixel(run, write_series, save_png, dot_grid(640, 640, pitch, pitch))

    assert outcome["result"] == "fail"
    assert outcome["reasons"]


def test_check_fails_when_only_the_vertical_dot_size_is_off(run, write_series, save_png):
    outcome = check_pixel(run, write_series, save_png, dot_grid(640, 640, 20, 24))

    assert outcome["result"] == "fail"
    assert any("vertical" in reason for reason in outcome["reasons"])
    assert not any("horizontal" in reason for reason in outcome["reasons"])


DOTS = 16


def flip_to_transparent(cell, count):
    """Make the first count opaque dots of the cell transparent."""
    out = cell.copy()
    flipped = 0
    for y in range(DOTS):
        for x in range(DOTS):
            if flipped < count and out.getpixel((x, y))[3] == 255:
                out.putpixel((x, y), (0, 0, 0, 0))
                flipped += 1
    return out


def check_sheet(run, write_series, save_png, raw, stand, frames, *extra):
    series = write_series(kind="pixel", canvas_dots=DOTS, transparent="true")
    raw_path = save_png(raw, "raw.png")
    before = raw_path.read_bytes()
    result = run(
        "check", "--series", series, "--raw", raw_path,
        "--frames", frames, "--stand", save_png(stand, "stand.png"), *extra,
    )
    assert raw_path.read_bytes() == before
    return verdict(result)


@pytest.mark.parametrize("flipped, expected", [(8, "pass"), (20, "fail")])  # 3.1% and 7.8% of 256 dots
def test_check_judges_the_top_left_frame_against_the_stand_at_five_percent_without_touching_the_raw(
    run, write_series, save_png, flipped, expected
):
    stand = sprite(DOTS)
    cells = [flip_to_transparent(stand, flipped)] + [sprite(DOTS, seed=s) for s in (5, 6, 7)]

    outcome = check_sheet(run, write_series, save_png, sheet(cells, DOTS, scale=10), stand, 4)

    assert outcome["result"] == expected


def monochrome_disc(dots, radius, colour=(40, 90, 200, 255)):
    image = blank(dots, dots)
    centre = dots / 2
    for y in range(dots):
        for x in range(dots):
            if (x + 0.5 - centre) ** 2 + (y + 0.5 - centre) ** 2 <= radius ** 2:
                image.putpixel((x, y), colour)
    return image


def smooth_disc(size, radius, colour=(40, 90, 200, 255)):
    """The same disc drawn at full resolution, so it has no dot grid to measure."""
    image = blank(size, size)
    centre = size / 2
    for y in range(size):
        for x in range(size):
            if (x + 0.5 - centre) ** 2 + (y + 0.5 - centre) ** 2 <= radius ** 2:
                image.putpixel((x, y), colour)
    return image


@pytest.mark.parametrize("draw_stand, expected", [(False, "fail"), (True, "undetermined")])
def test_check_on_a_sheet_without_a_measurable_dot_size_follows_the_top_left_frame(
    run, write_series, save_png, draw_stand, expected
):
    stand = monochrome_disc(DOTS, 6)
    raw = blank(DOTS * 10 * 4, DOTS * 10 * 2)  # one flat (transparent) colour
    if draw_stand:
        raw.paste(smooth_disc(DOTS * 10, 60), (0, 0))

    outcome = check_sheet(run, write_series, save_png, raw, stand, 8)

    assert outcome["result"] == expected
    assert outcome["reasons"]


def overflowing_sheet():
    body = figure(6, 10)
    stand = place(body, 5, 4, DOTS)
    tall = place(figure(6, DOTS, seed=4), 5, 0, DOTS)
    cells = [stand, tall] + [place(body, 5, 4, DOTS) for _ in range(6)]
    return sheet(cells, DOTS, scale=10), stand


def test_check_fails_a_sheet_whose_frame_would_rise_above_the_cell_top_when_feet_are_aligned(
    run, write_series, save_png
):
    raw, stand = overflowing_sheet()

    outcome = check_sheet(run, write_series, save_png, raw, stand, 8)

    assert outcome["result"] == "fail"
    assert any("frame 2" in reason for reason in outcome["reasons"])


def test_check_with_no_ground_does_not_judge_rising_above_the_cell_top(run, write_series, save_png):
    raw, stand = overflowing_sheet()

    outcome = check_sheet(run, write_series, save_png, raw, stand, 8, "--no-ground")

    assert outcome == {"result": "pass", "reasons": []}
