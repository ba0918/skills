import json

import pytest

from conftest import blank


def _is_json(text):
    try:
        json.loads(text)
    except ValueError:
        return False
    return True


@pytest.mark.parametrize(
    "fields, missing",
    [
        ({"kind": "pixel", "transparent": "true"}, "canvas_dots"),
        ({"kind": "illustration", "size": "1024x1024"}, "transparent"),
    ],
)
def test_check_rejects_series_missing_a_required_field_without_json(
    run, write_series, save_png, fields, missing
):
    series = write_series(**fields)
    raw = save_png(blank(320, 320), "raw.png")

    result = run("check", "--series", series, "--raw", raw)

    assert result.returncode != 0
    assert not _is_json(result.stdout)
    assert missing in result.stderr
