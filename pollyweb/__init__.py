"""Top-level package for pollyweb.

This module exposes a trivial `hello()` helper along with a `__version__`
attribute so that code and shells can determine the installed version.
The version is obtained from the package metadata at runtime, falling back
with a placeholder if the distribution isn't installed in a normal way.
"""

from importlib.metadata import PackageNotFoundError, version as _version


try:
    __version__ = _version("pollyweb")
except PackageNotFoundError:  # during development imports it may not be installed
    __version__ = "0.0.0"


def hello():
    return "Hello from pollyweb!"
