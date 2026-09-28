import pytest
from PIL import Image

from conftest import blank, pixels, sprite


@pytest.mark.parametrize("frames, size", [(4, (1280, 320)), (6, (1280, 640)), (16, (1280, 1280))])
def test_template_places_the_stand_in_the_top_left_cell_of_a_four_column_sheet(
    run, save_png, tmp_path, frames, size
):
    stand = sprite(32)
    out = tmp_path / "template.png"

    result = run("template", "--stand", save_png(stand, "stand.png"), "--frames", frames, "--out", out)

    assert result.returncode == 0, result.stderr
    template = Image.open(out).convert("RGBA")
    assert template.size == size
    top_left = template.crop((0, 0, 320, 320))
    assert pixels(top_left) == pixels(stand.resize((320, 320), Image.NEAREST))
    rest = template.copy()
    rest.paste(blank(320, 320), (0, 0))
    assert all(a == 0 for (_, _, _, a) in pixels(rest))


def test_template_without_frames_enlarges_the_stand_to_ten_pixels_per_dot(run, save_png, tmp_path):
    stand = sprite(32)
    out = tmp_path / "reference-large.png"

    result = run("template", "--stand", save_png(stand, "stand.png"), "--out", out)

    assert result.returncode == 0, result.stderr
    large = Image.open(out).convert("RGBA")
    assert large.size == (320, 320)
    for y in range(320):
        for x in range(320):
            assert large.getpixel((x, y)) == stand.getpixel((x // 10, y // 10))


@pytest.mark.parametrize(
    "stand_size, frames",
    [((32, 24), None), ((32, 32), 1), ((32, 32), 17)],
)
def test_template_rejects_a_non_square_stand_or_a_frame_count_outside_two_to_sixteen(
    run, save_png, tmp_path, stand_size, frames
):
    stand = save_png(blank(*stand_size, (10, 20, 30, 255)), "stand.png")
    extra = [] if frames is None else ["--frames", frames]

    result = run("template", "--stand", stand, *extra, "--out", tmp_path / "out.png")

    assert result.returncode != 0
    assert not (tmp_path / "out.png").exists()
