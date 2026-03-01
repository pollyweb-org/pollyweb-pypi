#!/usr/bin/env python3
# USAGE: python3 scripts/deploy.py

import re, subprocess, sys, shutil, pathlib, time, json
from typing import Union
from urllib import request as _urlrequest
from urllib import error as _urlerror

# --- Config ---
PACKAGE_NAME = "pollyweb"   # project.name in pyproject.toml
IMPORT_CHECK  = "import pollyweb; print(pollyweb.hello())"
HELLO_PATHS = [
    pathlib.Path("pollyweb/__init__.py"),
]
PYPROJECT = pathlib.Path("pyproject.toml")
DIST_DIR = pathlib.Path("dist")

RETRY_ATTEMPTS = 6        # total tries incl. first install (e.g., ~1 minute of retries)
RETRY_DELAY_SEC = 10      # seconds between retries (with countdown)

# --- Utils ---
def read(path): return path.read_text(encoding="utf-8")
def write(path, s): path.write_text(s, encoding="utf-8")

def sh(*args):
    print("+", " ".join(args))
    subprocess.check_call(args)

def python_exe() -> str:
    venv_py = pathlib.Path(".venv/bin/python")
    if venv_py.exists():
        return str(venv_py)
    return sys.executable

def bump_patch(v: str) -> str:
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", v.strip())
    if not m: raise ValueError(f"Version not semver patch format: {v}")
    major, minor, patch = map(int, m.groups())
    return f"{major}.{minor}.{patch+1}"

def version_exists_on_pypi(pkg: str, version: str) -> bool:
    url = f"https://pypi.org/pypi/{pkg}/json"
    try:
        with _urlrequest.urlopen(url, timeout=10) as resp:  # nosec B310
            data = json.loads(resp.read().decode("utf-8"))
    except _urlerror.HTTPError as e:
        if e.code == 404:
            return False
        raise RuntimeError(f"PyPI lookup failed for {pkg}: {e}") from e
    except Exception as e:
        raise RuntimeError(f"PyPI lookup failed for {pkg}: {e}") from e
    releases = data.get("releases", {})
    return version in releases and len(releases[version]) > 0

def update_pyproject():
    txt = read(PYPROJECT)
    m = re.search(r'(?m)^\s*version\s*=\s*"([^"]+)"\s*$', txt)
    if not m: raise RuntimeError("version not found in pyproject.toml")
    old = m.group(1)
    new = bump_patch(old)
    bumped = 0
    while version_exists_on_pypi(PACKAGE_NAME, new):
        new = bump_patch(new)
        bumped += 1
    if bumped:
        print(f"[version] PyPI already had version; bumped {bumped} extra time(s).")
    txt = txt[:m.start(1)] + new + txt[m.end(1):]
    write(PYPROJECT, txt)
    print(f"[version] {old} -> {new} in pyproject.toml")
    return old, new

def update_hello(new_version: str):
    hello_path = next((p for p in HELLO_PATHS if p.exists()), None)
    if not hello_path:
        print("[warn] hello target not found; skipping hello() string sync")
        return
    txt = read(hello_path)
    new_txt = re.sub(
        r'(?m)^\s*__version__\s*=\s*"\d+\.\d+\.\d+"\s*$',
        f'__version__ = "{new_version}"',
        txt,
        count=1,
    )
    if new_txt != txt:
        write(hello_path, new_txt)
        print(f"[{hello_path}] synced embedded version -> {new_version}")
    else:
        print(f"[warn] did not update {hello_path} (__version__ assignment not found)")

def ensure_tools():
    sh(python_exe(), "-m", "pip", "install", "--upgrade", "build", "twine")

def clean_dist():
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
        print("[clean] removed dist/")

def build():
    sh(python_exe(), "-m", "build")

def upload_testpypi():
    sh("twine", "upload", "--verbose",
       #"--repository", "testpypi",
       "dist/*")

def countdown(seconds: int, prefix: str = "Waiting"):
    for i in range(seconds, 0, -1):
        print(f"{prefix}: {i}s", end="\r", flush=True)
        time.sleep(1)
    print(" " * 40, end="\r")

def installed_version(pkg: str) -> Union[str, None]:
    try:
        # Python 3.8+: importlib.metadata
        try:
            from importlib.metadata import version, PackageNotFoundError  # type: ignore
        except Exception:  # pragma: no cover
            from importlib_metadata import version, PackageNotFoundError  # backport
        return version(pkg)
    except Exception:
        return None

def pip_install_from_testpypi():
    sh(python_exe(), "-m", "pip", "install", "--no-cache-dir", "--force-reinstall",
       #"-i", "https://test.pypi.org/simple/",
       PACKAGE_NAME)

def run_import_check():
    sh(sys.executable, "-c", IMPORT_CHECK)

def main():
    if not PYPROJECT.exists():
        print("pyproject.toml not found. Run from the project root.")
        sys.exit(1)

    old, new = update_pyproject()
    update_hello(new)

    ensure_tools()
    clean_dist()
    build()
    upload_testpypi()

    print("\nUpload complete!")
    print(f"Target version: {new}")
    print("Next: install & test in 10 seconds...\n")
    countdown(10, prefix="Starting")

    # Try initial install + check, then retries if mismatch
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        print(f"[attempt {attempt}/{RETRY_ATTEMPTS}] Installing from TestPyPI…")
        pip_install_from_testpypi()

        iv = installed_version(PACKAGE_NAME)
        print(f"Installed version detected: {iv!r}")

        if iv == new:
            print("[ok] Installed version matches uploaded version.")
            run_import_check()
            break

        if attempt < RETRY_ATTEMPTS:
            print(f"[wait] Version {iv!r} != {new!r}. "
                  f"Repository index may not be consistent yet.")
            countdown(RETRY_DELAY_SEC, prefix=f"Retrying in")
        else:
            print(f"[fail] Gave up after {RETRY_ATTEMPTS} attempts. "
                  f"Installed {iv!r}, expected {new!r}.")
            sys.exit(2)

if __name__ == "__main__":
    main()