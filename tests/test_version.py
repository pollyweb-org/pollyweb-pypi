import pollyweb
import pytest


def test_version_string():
    # __version__ should be a non-empty string
    assert isinstance(pollyweb.__version__, str)
    assert pollyweb.__version__ != ""
