# Symbolic-Boundary Audits for Language Planner Hybrids

This repo studies a narrow failure mode in language-planner / symbolic-planner
hybrids:

> Candidate-pool selection can concentrate plans that satisfy a symbolic checker
> or surrogate simulator while violating hidden execution semantics at the
> language-to-action boundary.

The contribution is intentionally scoped: a finite-pool mechanism proposition,
controlled toy domains, diagnostics for semantic-symbolic mismatch, and repair
baselines based on semantic uncertainty, strict boundary controls, and
adversarial execution gates. The v3 package expands the evidence to high-budget
candidate-pool stress at `N=512`, loophole-prior sweeps, repair ablations,
candidate-level calibration, and failure-case exports.

## Quickstart

```powershell
cd "$HOME\Downloads\best-of-n-language-symbolic-planner-hybrids"
python -m pip install -e .
python -m pytest -q
.\scripts\run_smoke.ps1
```

For the full local evidence package and PDF:

```powershell
.\scripts\run_all.ps1
python experiments\run_expansion_suite.py --mode full --output results\expansion
python scripts\build_paper.py
python scripts\run_claim_audit.py
```

The final v3 paper PDF is copied to both the repository and the visible
Desktop:

```text
paper\final\best-of-n-language-symbolic-planner-hybrids-v3.pdf
C:\Users\wangz\OneDrive\Desktop\best-of-n-language-symbolic-planner-hybrids-v3.pdf
```

## What Is Implemented

- A language-like candidate generator with grounded, invalid, paperwork, shortcut,
  and simulator-lure plan modes.
- A compiler from natural-language plan steps to symbolic actions.
- A coarse symbolic checker with intentional abstraction holes.
- A hidden-semantics executor that scores physical success.
- Proxy and repair selectors using language prior, symbolic score, simulator
  score, calibrated boundary penalties, adversarial gates, and uncertainty lower
  confidence bounds.
- Diagnostics for selected-plan utility, proxy-true gap, checker-valid but
  semantically bad plans, loophole occupancy, and candidate-budget scaling.
- A v3 expansion suite with `N=512` stress, rare-loophole priors, strict
  checker controls, repair ablations, proxy calibration, and selected failure
  cases.

## Repo Layout

- `src/boundary_planner/`: domains, compiler, checker, executor, scoring,
  selection, and finite-pool law.
- `experiments/`: reproducible suite for smoke/full experiments plus the v3
  expansion suite.
- `scripts/`: literature build, smoke/full runs, claim audit, paper build.
- `tests/`: parser, checker/executor mismatch, deterministic selection, and
  diagnostic tests.
- `docs/`: literature map, hostile prior work, novelty decision, related-work
  matrix, claim/final audits.
- `figures/`: generated paper figures, including v3 expansion plots.
- `results/`: generated CSV/JSON experiment outputs.
- `paper/`: anonymous ICLR-style paper source.

## Paper

The paper source is `paper/main.tex`. It uses the anonymous ICLR 2027 template
style file `paper/iclr2027_conference.sty` with `\iclrfinalcopy` commented out.
Build it with:

```powershell
python scripts\build_paper.py
```

## Claim Boundary

The repo supports controlled-mechanism claims only. It does not claim robotics
validation, universal verifier failure, or a general safety fix. The strongest
supported statement is that, in these language/symbolic hybrid domains, proxy
selection over larger candidate pools amplifies semantic-symbolic boundary
loopholes, while boundary-aware repair gates reduce that controlled mismatch.
At `N=512`, symbolic and simulator proxy selection both collapse to hidden
execution utility `15.9` with selected-loophole rate `100.0%`, while the
boundary-aware controls recover utility `84.6` in this synthetic setting.
