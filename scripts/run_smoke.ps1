$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
python -m experiments.run_suite --preset smoke
python -m experiments.run_frozenlake_benchmark --quick --output results\tmp_frozenlake_quick --figure figures\tmp_frozenlake_quick.png
python scripts/run_claim_audit.py --preset smoke
