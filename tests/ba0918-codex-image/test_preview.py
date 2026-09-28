import pytest
from PIL import Image

from conftest import figure, place, sheet

DOTS = 16


def six_frame_sheet():
    """Six distinct frames, with cells 7 and 8 drawn as well to show they are left out."""
    cells = [place(figure(6, 10, seed=seed), 5, 4, DOTS) for seed in range(8)]
    return sheet(cells, DOTS)


def frame_durations(path):
    gif = Image.open(path)
    durations = []
    for index in range(gif.n_frames):
        gif.seek(index)
        durations.append(gif.info["duration"])
    return durations


@pytest.mark.parametrize("extra, duration", [([], 120), (["--ms", 80], 80)])
def test_preview_makes_a_gif_of_the_frames_only_at_the_given_speed(save_png, run, tmp_path, extra, duration):
    out = tmp_path / "preview.gif"

    result = run("preview", "--sheet", save_png(six_frame_sheet(), "final.png"), "--frames", 6, "--out", out, *extra)

    assert result.returncode == 0, result.stderr
    assert frame_durations(out) == [duration] * 6
