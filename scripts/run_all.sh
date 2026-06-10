#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python scripts/build_literature_docs.py
python -m experiments.run_suite --preset full
python scripts/run_claim_audit.py --preset full
python scripts/build_paper.py
