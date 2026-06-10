$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
python -m experiments.run_suite --preset smoke
python scripts/run_claim_audit.py --preset smoke
