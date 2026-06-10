# Best-of-N Language/Symbolic Planner Hybrids

This repo studies a narrow failure mode in language-planner / symbolic-planner hybrids:

> Best-of-N selection can concentrate rare plans that satisfy a symbolic checker or simulator while violating hidden execution semantics. The selected plan looks increasingly valid to the proxy as N grows, but execution validity collapses.

The first-pass contribution is intentionally scoped: a finite-N mechanism proposition, controlled toy domains, diagnostics for semantic-symbolic mismatch, and repair baselines based on semantic uncertainty and adversarial execution gates.

## Quickstart

```powershell
cd "$HOME\Downloads\best-of-n-language-symbolic-planner-hybrids"
python -m pip install -e .
pytest
.\scripts\run_smoke.ps1
```

For the full local evidence package and PDF:

```powershell
.\scripts\run_all.ps1
```

The final paper PDF is copied to:

```text
~/Downloads/best-of-n-language-symbolic-planner-hybrids.pdf
```

## What Is Implemented

- A language-like candidate generator with grounded, invalid, and loophole plan modes.
- A compiler from natural-language plan steps to symbolic actions.
- A coarse symbolic checker with an intentional abstraction hole.
- A hidden-semantics executor that scores physical success.
- Best-of-N selectors using language prior, symbolic proxy, simulator proxy, calibrated penalty, adversarial gate, and uncertainty lower confidence bound.
- Diagnostics for selected-plan utility, proxy-true gap, symbolic-valid-but-semantically-bad rate, loophole occupancy, and N-scaling.

## Repo Layout

- `src/bon_symbolic/`: domains, compiler, checker, executor, scoring, selection, and finite-N law.
- `experiments/`: reproducible suite for smoke/full experiments.
- `scripts/`: literature build, smoke/full runs, claim audit, paper build.
- `tests/`: parser, checker/executor mismatch, deterministic selection, and diagnostic tests.
- `docs/`: literature map, hostile prior work, novelty decision, related-work matrix, claim/final audits.
- `figures/`: generated paper figures.
- `results/`: generated CSV/JSON experiment outputs.
- `paper/`: anonymous ICLR-style paper source.

## Paper

The paper source is `paper/main.tex`. It uses the anonymous ICLR 2027 template style file `paper/iclr2027_conference.sty` with `\iclrfinalcopy` commented out. Build it with:

```powershell
python scripts\build_paper.py
```

## Claim Boundary

The repo supports controlled-mechanism claims only. It does not claim robotics validation, universal verifier failure, or a general safety fix. The strongest supported statement is that, in these language/symbolic hybrid domains, proxy Best-of-N selection amplifies semantic-symbolic loopholes and repair gates can reduce that controlled mismatch.
