"""Top-level package for pollyweb.

This module exposes a trivial `hello()` helper along with a `__version__`
attribute so that code and shells can determine the installed version.
The version is obtained from the package metadata at runtime, falling back
with a placeholder if the distribution isn't installed in a normal way.

It also supports lazy symbol access so users can write:

    import pollyweb as pw
    pw.SOME_CLASS

without wildcard imports.
"""

from importlib import import_module
from importlib.metadata import PackageNotFoundError, version as _version
from pathlib import Path

from .utils.LOG import LOG
from .utils.STRUCT import STRUCT
from .utils.TESTS import TESTS
from .utils.UTILS import UTILS


_SYMBOL_CACHE = {}
_MODULE_NAMES = None
_PACKAGE_ROOT = Path(__file__).resolve().parent


try:
    __version__ = _version("pollyweb")
except PackageNotFoundError:  # during development imports it may not be installed
    __version__ = "0.0.0"


def hello():
    return "Hello from pollyweb!"


def _get_module_names() -> list[str]:
    global _MODULE_NAMES
    if _MODULE_NAMES is None:
        modules = []
        for py_file in _PACKAGE_ROOT.rglob("*.py"):
            if "__pycache__" in py_file.parts:
                continue
            if py_file.name == "__init__.py":
                continue
            relative = py_file.relative_to(_PACKAGE_ROOT).with_suffix("")
            module_parts = ".".join(relative.parts)
            modules.append(f"{__name__}.{module_parts}")
        _MODULE_NAMES = sorted(set(modules))
    return _MODULE_NAMES


def _candidate_modules(symbol_name: str):
    suffix = f".{symbol_name}"
    for module_name in _get_module_names():
        if module_name.endswith(suffix):
            yield module_name


def __getattr__(name: str):
    if name in _SYMBOL_CACHE:
        return _SYMBOL_CACHE[name]
    if name.startswith("_"):
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    matches = []
    for module_name in _candidate_modules(name):
        module = import_module(module_name)
        if hasattr(module, name):
            matches.append((module_name, getattr(module, name)))
            continue
        if module_name.rsplit(".", 1)[-1] == name:
            matches.append((module_name, module))

    if not matches:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    unique_values = {id(value) for _, value in matches}
    if len(unique_values) > 1:
        modules = ", ".join(module_name for module_name, _ in matches)
        raise AttributeError(
            f"Ambiguous symbol '{name}' found in multiple modules: {modules}"
        )

    resolved = matches[0][1]
    _SYMBOL_CACHE[name] = resolved
    return resolved


def __dir__():
    names = set(globals())
    names.update(module_name.rsplit(".", 1)[-1] for module_name in _get_module_names())
    names.update(_SYMBOL_CACHE.keys())
    return sorted(names)


__all__ = [
    "__version__",
    "hello",
    "STRUCT",
    "LOG",
    "UTILS",
    "TESTS",
]
