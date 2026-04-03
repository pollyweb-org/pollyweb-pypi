#!/usr/bin/env sh

set -eu

REPO_ROOT="$(git rev-parse --show-toplevel)"
PYTHON_BIN="python3"
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

PYTHON_BINDIR="$(dirname "$PYTHON_BIN")"
DETECT_SECRETS_HOOK="$PYTHON_BINDIR/detect-secrets-hook"
SEMGREP_IMAGE="semgrep/semgrep:latest"
SEMGREP_CONFIG="p/default"

require_python_module() {
  MODULE_NAME="$1"
  PACKAGE_NAME="$2"

  if ! "$PYTHON_BIN" -m "$MODULE_NAME" --help >/dev/null 2>&1; then
    echo ""
    echo "Security scan blocked: $PACKAGE_NAME is not installed for $PYTHON_BIN."
    echo "Install it with: $PYTHON_BIN -m pip install -e '.[dev]'"
    exit 1
  fi
}

echo "Running dependency security audit..."

require_python_module "pip_audit" "pip-audit"

if ! (cd "$REPO_ROOT" && "$PYTHON_BIN" -m pip_audit --progress-spinner off .); then
  echo ""
  echo "Security scan blocked: dependency vulnerabilities are pending."
  exit 1
fi

echo "Running Bandit static analysis..."

require_python_module "bandit" "bandit"

if ! (cd "$REPO_ROOT" && "$PYTHON_BIN" -m bandit -c pyproject.toml -r pollyweb); then
  echo ""
  echo "Security scan blocked: Bandit reported findings."
  exit 1
fi

echo "Running detect-secrets baseline check..."

if [ ! -f "$REPO_ROOT/.secrets.baseline" ]; then
  echo ""
  echo "Security scan blocked: .secrets.baseline is missing."
  echo "Create it with: $PYTHON_BIN -m detect_secrets scan \$(git ls-files) > .secrets.baseline"
  exit 1
fi

if [ ! -x "$DETECT_SECRETS_HOOK" ]; then
  echo ""
  echo "Security scan blocked: detect-secrets is not installed for $PYTHON_BIN."
  echo "Install it with: $PYTHON_BIN -m pip install -e '.[dev]'"
  exit 1
fi

if ! (
  cd "$REPO_ROOT" &&
  "$DETECT_SECRETS_HOOK" --baseline .secrets.baseline $(git ls-files)
); then
  echo ""
  echo "Security scan blocked: detect-secrets found untracked secrets."
  exit 1
fi

echo "Running Semgrep static analysis..."

if command -v semgrep >/dev/null 2>&1; then
  if ! (cd "$REPO_ROOT" && semgrep scan --config "$SEMGREP_CONFIG" --error --metrics=off pollyweb tests); then
    echo ""
    echo "Security scan blocked: Semgrep reported findings."
    exit 1
  fi
elif "$PYTHON_BIN" -m semgrep --help >/dev/null 2>&1; then
  if ! (cd "$REPO_ROOT" && "$PYTHON_BIN" -m semgrep scan --config "$SEMGREP_CONFIG" --error --metrics=off pollyweb tests); then
    echo ""
    echo "Security scan blocked: Semgrep reported findings."
    exit 1
  fi
elif command -v pipx >/dev/null 2>&1; then
  echo "Falling back to pipx for Semgrep..."

  if ! (
    cd "$REPO_ROOT" &&
    pipx run --spec semgrep semgrep scan --config "$SEMGREP_CONFIG" --error --metrics=off pollyweb tests
  ); then
    echo ""
    echo "Security scan blocked: Semgrep reported findings."
    exit 1
  fi
elif command -v docker >/dev/null 2>&1; then
  echo "Falling back to Docker for Semgrep..."

  if ! (
    cd "$REPO_ROOT" &&
    docker run --rm \
      -v "${REPO_ROOT}:/src" \
      -w /src \
      "$SEMGREP_IMAGE" \
      semgrep scan --config "$SEMGREP_CONFIG" --error --metrics=off pollyweb tests
  ); then
    echo ""
    echo "Security scan blocked: Semgrep reported findings."
    exit 1
  fi
else
  echo ""
  echo "Security scan blocked: semgrep is unavailable for $PYTHON_BIN and Docker is not installed."
  echo "Install Semgrep in a supported interpreter or install Docker."
  exit 1
fi

echo "Local Python security scans passed."
