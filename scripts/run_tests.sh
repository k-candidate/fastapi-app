#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-all}"
export PYTHONDONTWRITEBYTECODE=1
PYTEST=(uv run pytest -v -p no:cacheprovider)

run_unit_tests() {
  "${PYTEST[@]}" tests/unit
}

run_integration_tests() {
  cleanup() {
    docker compose down
  }

  trap cleanup EXIT

  docker compose up -d --build
  "${PYTEST[@]}" tests/integration
}

case "$MODE" in
  unit)
    run_unit_tests
    ;;
  integration)
    run_integration_tests
    ;;
  all)
    run_unit_tests
    run_integration_tests
    ;;
  *)
    echo "Usage: $0 [unit|integration|all]" >&2
    exit 1
    ;;
esac
