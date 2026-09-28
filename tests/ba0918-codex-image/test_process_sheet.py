from PIL import Image

from conftest import figure, pixels, place, sheet

DOTS = 16
BODY = figure(6, 10)  # feet on the tenth row of the body
STAND = place(BODY, 5, 4, DOTS)  # feet on row 13 of the cell
DRIFT = [(2, 2), (3, 3), (4, 5), (6, 6), (7, 1), (8, 3), (1, 4)]  # (left, top) of frames 2..8


def animation_series(write_series):
    return write_series(kind="pixel", canvas_dots=DOTS, transparent="true")


def run_sheet_process(run, write_series, save_png, tmp_path, raw_cells, frames, *extra):
    out = tmp_path / "final.png"
    result = run(
        "process",
        "--series", animation_series(write_series),
        "--raw", save_png(sheet(raw_cells, DOTS, scale=10), "raw.png"),
        "--out", out,
        "--frames", frames,
        "--stand", save_png(STAND, "stand.png"),
        *extra,
    )
    return result, out


def test_sheet_process_restores_the_stand_and_aligns_every_foot_to_it_without_moving_sideways(
    run, write_series, save_png, tmp_path
):
    distorted_stand = place(figure(6, 10, seed=9), 4, 3, DOTS)
    raw_cells = [distorted_stand] + [place(BODY, left, top, DOTS) for left, top in DRIFT]

    result, out = run_sheet_process(run, write_series, save_png, tmp_path, raw_cells, 8)

    assert result.returncode == 0, result.stderr
    expected = sheet([STAND] + [place(BODY, left, 4, DOTS) for left, _ in DRIFT], DOTS)
    assert pixels(Image.open(out).convert("RGBA")) == pixels(expected)


def test_sheet_process_with_no_ground_keeps_each_frame_at_its_drawn_height(
    run, write_series, save_png, tmp_path
):
    raw_cells = [STAND] + [place(BODY, left, top, DOTS) for left, top in DRIFT]

    result, out = run_sheet_process(run, write_series, save_png, tmp_path, raw_cells, 8, "--no-ground")

    assert result.returncode == 0, result.stderr
    assert pixels(Image.open(out).convert("RGBA")) == pixels(sheet(raw_cells, DOTS))


def test_sheet_process_clears_the_cells_after_the_last_frame(run, write_series, save_png, tmp_path):
    raw_cells = [STAND] + [place(BODY, 5, 4, DOTS) for _ in range(7)]  # cells 7 and 8 drawn anyway

    result, out = run_sheet_process(run, write_series, save_png, tmp_path, raw_cells, 6)

    assert result.returncode == 0, result.stderr
    final = Image.open(out).convert("RGBA")
    empty_cells = final.crop((2 * DOTS, DOTS, 4 * DOTS, 2 * DOTS))
    assert all(a == 0 for (_, _, _, a) in pixels(empty_cells))
    assert final.crop((DOTS, DOTS, 2 * DOTS, 2 * DOTS)).getpixel((5, 13))[3] == 255  # frame 6 kept


def test_sheet_process_refuses_a_sheet_whose_frame_would_rise_above_the_cell_top(
    run, write_series, save_png, tmp_path
):
    tall = place(figure(6, DOTS, seed=4), 5, 0, DOTS)  # fills the cell top to bottom; feet on row 15
    raw_cells = [STAND, tall] + [place(BODY, 5, 4, DOTS) for _ in range(6)]

    result, out = run_sheet_process(run, write_series, save_png, tmp_path, raw_cells, 8)

    assert result.returncode != 0
    assert not out.exists()
