#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python scripts/build_literature_docs.py
python -m experiments.run_suite --preset full
python -m experiments.run_expansion_suite --mode full --output results/expansion
python -m experiments.run_frozenlake_benchmark
python scripts/build_paper.py
python scripts/run_claim_audit.py --preset full
