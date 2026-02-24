import os
import tempfile
import pytest

from pollyweb.demo import setup


def test_setup_cli(tmp_path, capsys):
    pub = tmp_path / "pub.key"
    pub.write_text("dummy")

    # call main with key=value syntax
    setup.main([f"dkim={pub}", "id=key1"])
    captured = capsys.readouterr()
    assert "https://api.pollyweb.org/demo/setup" in captured.out

    # also support colon separator
    setup.main([f"dkim:{pub}", "id:key2"])
    captured = capsys.readouterr()
    assert "https://api.pollyweb.org/demo/setup" in captured.out


def test_setup_missing_file(tmp_path):
    # missing 'dkim' parameter yields usage error
    with pytest.raises(SystemExit) as exc:
        grab.main(["id=x"])
    assert "usage" in str(exc.value)

    # non-existent file still reported
    with pytest.raises(SystemExit) as exc:
        grab.main(["dkim=doesnotexist", "id=x"])
    assert "file not found" in str(exc.value)
