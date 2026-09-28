from PIL import Image

from conftest import blank, figure, pixels, sprite


def add_soft_fringe(image, scale):
    """Blur every dot boundary with semi-transparent pixels, keeping each cell's centre intact."""
    out = image.copy()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = image.getpixel((x, y))
            on_boundary = x % scale in (0, scale - 1) or y % scale in (0, scale - 1)
            if on_boundary and a == 255:
                out.putpixel((x, y), (r, g, b, 90))
            elif on_boundary and a == 0:
                out.putpixel((x, y), (200, 200, 200, 60))
    return out


def test_pixel_process_recovers_the_original_dots_from_an_upscaled_image_with_soft_edges(
    run, write_series, save_png, tmp_path
):
    original = sprite(32)
    raw = add_soft_fringe(original.resize((320, 320), Image.NEAREST), 10)
    series = write_series(kind="pixel", canvas_dots=32, transparent="true")
    out = tmp_path / "final.png"

    result = run("process", "--series", series, "--raw", save_png(raw, "raw.png"), "--out", out)

    assert result.returncode == 0, result.stderr
    final = Image.open(out).convert("RGBA")
    assert final.size == (32, 32)
    assert pixels(final) == pixels(original)


def stripes(width, height):
    """Vertical colour bands, so a crop shows which horizontal range survived."""
    image = Image.new("RGBA", (width, height))
    for x in range(width):
        colour = (x * 255 // (width - 1), 80, 160, 255)
        for y in range(height):
            image.putpixel((x, y), colour)
    return image


def assert_centre_crop_of_stripes(final):
    """The 1100x540 stripes cropped to 960x540 from the centre, then scaled to 640x360."""
    assert final.size == (640, 360)
    assert final.mode == "RGB"
    assert abs(final.getpixel((0, 180))[0] - 70 * 255 // 1099) <= 3  # starts 70 px in from the left
    assert abs(final.getpixel((639, 180))[0] - 1029 * 255 // 1099) <= 3  # ends 70 px in from the right


def test_web_process_crops_an_off_ratio_image_from_the_centre_to_exactly_the_size(
    run, write_series, save_png, tmp_path
):
    raw = stripes(1100, 540)  # a little wider than 16:9 (960x540)
    series = write_series(kind="web", size="640x360")
    out = tmp_path / "final.png"

    result = run("process", "--series", series, "--raw", save_png(raw, "raw.png"), "--out", out)

    assert result.returncode == 0, result.stderr
    assert_centre_crop_of_stripes(Image.open(out))


def soft_disc(width, height):
    """An opaque disc whose rim fades out over 40 px, on a fully transparent background."""
    image = blank(width, height)
    cx, cy, radius = width / 2, height / 2, min(width, height) * 0.4
    for y in range(height):
        for x in range(width):
            distance = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if distance <= radius:
                image.putpixel((x, y), (220, 90, 40, 255))
            elif distance <= radius + 40:
                alpha = round(255 * (radius + 40 - distance) / 40)
                image.putpixel((x, y), (220, 90, 40, alpha))
    return image


def test_transparent_illustration_process_fits_the_size_and_keeps_semi_transparent_edges(
    run, write_series, save_png, tmp_path
):
    raw = soft_disc(600, 400)
    series = write_series(kind="illustration", size="300x300", transparent="true")
    out = tmp_path / "final.png"

    result = run("process", "--series", series, "--raw", save_png(raw, "raw.png"), "--out", out)

    assert result.returncode == 0, result.stderr
    final = Image.open(out).convert("RGBA")
    assert final.size == (300, 300)
    alphas = [a for (_, _, _, a) in pixels(final)]
    assert any(0 < a < 255 for a in alphas)
    assert final.getpixel((150, 150))[3] == 255
    assert all(final.getpixel((x, 0))[3] == 0 for x in range(300))  # padding above the fitted image



def test_transparent_illustration_process_centres_a_raw_smaller_than_the_size_without_enlarging_it(
    run, write_series, save_png, tmp_path
):
    raw = figure(100, 60)
    series = write_series(kind="illustration", size="300x200", transparent="true")
    out = tmp_path / "final.png"

    result = run("process", "--series", series, "--raw", save_png(raw, "raw.png"), "--out", out)

    assert result.returncode == 0, result.stderr
    final = Image.open(out).convert("RGBA")
    assert final.size == (300, 200)
    assert pixels(final.crop((100, 70, 200, 130))) == pixels(raw)  # centred at its own size
    assert sum(1 for (_, _, _, a) in pixels(final) if a) == 100 * 60  # transparent everywhere else

def test_opaque_illustration_process_crops_from_the_centre_to_exactly_the_size(
    run, write_series, save_png, tmp_path
):
    raw = stripes(1100, 540)
    series = write_series(kind="illustration", size="640x360", transparent="false")
    out = tmp_path / "final.png"

    result = run("process", "--series", series, "--raw", save_png(raw, "raw.png"), "--out", out)

    assert result.returncode == 0, result.stderr
    assert_centre_crop_of_stripes(Image.open(out))
