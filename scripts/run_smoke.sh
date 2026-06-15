#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m experiments.run_suite --preset smoke
python -m experiments.run_frozenlake_benchmark --quick --output results/tmp_frozenlake_quick --figure figures/tmp_frozenlake_quick.png
python scripts/run_claim_audit.py --preset smoke
