import os
import tempfile
import pytest

from pollyweb.demo import grab


def test_grab_cli(tmp_path, capsys):
    pub = tmp_path / "pub.key"
    pub.write_text("dummy")

    # call main with valid args
    grab.main([str(pub), "foo"])
    captured = capsys.readouterr()
    assert "https://api.pollyweb.org/demo/grab" in captured.out


def test_grab_missing_file(tmp_path):
    with pytest.raises(SystemExit) as exc:
        grab.main([str(tmp_path / "doesnotexist"), "x"])
    assert "file not found" in str(exc.value)
