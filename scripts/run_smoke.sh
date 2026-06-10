#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m experiments.run_suite --preset smoke
python scripts/run_claim_audit.py --preset smoke
