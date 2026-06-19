# Final Audit

## Main Thesis

Proxy-ranked candidate selection in language-planner / symbolic-planner hybrids
can concentrate rare boundary loopholes: plans that satisfy a symbolic checker
or surrogate simulator while failing hidden execution semantics.

## v4 Novelty

The v4 paper is no longer a short mechanism wrapper. It is framed as a
boundary-contract audit for language-to-symbolic planning: plans that pass the
interface but do not execute. The central contribution is the audit protocol and
evidence package around compiler loss, checker visibility, simulator fidelity,
selected-tail calibration, and hidden-executor evaluation.
The v4 pass adds a standard Gymnasium FrozenLake-v1 tier so the evidence is no
longer synthetic-only.

## Literature Coverage

The repo includes:

- `docs/related_work_matrix.csv` with 120 entries.
- `docs/literature_map.md` with the 100-paper sweep, 30-paper serious skim set,
  and 20-25-paper deep-read threat set.
- `docs/hostile_prior_work.md` with 10 hostile prior-work threats.
- `docs/novelty_decision.md` documenting why the semantic-symbolic loophole
  concentration angle was chosen.

## Proof Status

The formal claim is a narrow two-type finite-pool proposition. If loopholes
occur independently with probability `p > 0`, every loophole receives higher
proxy score than every grounded candidate, and loopholes have lower true
utility, then top-proxy selection chooses a loophole with probability
`1 - (1-p)^N`, so expected true utility decreases monotonically to the loophole
utility. The proof is exact under those assumptions and is not used to claim
universal verifier failure.

## v4 Empirical Result

The expansion suite raises the stress budget to `N=512`. At that budget,
symbolic-proxy and simulator-proxy selectors both reach true utility `15.9`,
execution success `0.0%`, and selected-loophole rate `100.0%`. Boundary-aware
controls recover utility `84.6` in the controlled domains.

The FrozenLake-v1 tier uses the standard 8x8 map. Symbolic proxy selection
drops from hidden utility `40.1` at `N=1` to `0.0` at `N=128`, with `100.0%`
hole entry. The hazard-aware gate and uncertainty LCB recover utility `93.0`
and success `100.0%`.

## v4 Diagnostic Result

Candidate-level diagnostics show a selected-tail mismatch: proxy-high plans are
not hidden-utility-high plans. Across the expansion candidate pool, the proxy /
true Spearman correlation is low, and the exported failure cases show paperwork,
service-elevator, and simulator-lure plans passing the interface while failing
execution semantics.

## v4 Repair Result

Single-feature repairs are insufficient in the ablation suite. Penalties aimed
only at marks or shortcuts leave failure modes active, while packing penalties,
full-boundary penalties, strict-boundary proxies, adversarial gates, and
uncertainty lower-confidence selection recover execution success in the
synthetic domains.

## Biggest Remaining Weaknesses

- The main domains are synthetic and intentionally controlled.
- FrozenLake is a standard benchmark, but still a toy-text environment rather
  than a robot or learned simulator.
- The language generator is stochastic templates, not a frontier LLM.
- The simulator and hidden executor are handcrafted to expose the mechanism.
- The repairs use controlled knowledge of the abstraction gap.
- The result should not be generalized to deployed robotics, arbitrary symbolic
  verifiers, or production tool-use systems without new domain evidence.

## Submission-Readiness Judgment

Submission-ready v4 as a controlled mechanism and audit-protocol paper. The
manuscript is a 26-page anonymous PDF with substantial experiments, figures,
appendices, failure-case exports, and a local claim audit that rejects stale
short builds.

## Verification

- `python -m pytest -q`: 10 passed.
- `python -m compileall src tests experiments scripts -q`: passed.
- Expansion experiment: `python experiments\run_expansion_suite.py --mode full --output results\expansion`.
- FrozenLake benchmark: `python -m experiments.run_frozenlake_benchmark`.
- Claim audit: `python scripts\run_claim_audit.py`.
- Paper build: `python scripts\build_paper.py`.
- Final PDF page count: 26 pages.
- Final PDF SHA256:
  `EE2CBCAF42F24C5D2E3DBC135BF0F9BC04E5C32DBEDD6A697C927A82865AE1C3`
- PDF annotation audit found 31 link annotations: 26 green citation boxes and
  5 red internal-reference boxes. All annotations use 1pt visible borders
  matching the VLA role-model profile.
- Visual QA inspected rendered pages 1, 4, 6, 7, 8, 9, 20, and 26.

## Final PDF Path

`C:\Users\wangz\OneDrive\Desktop\best-of-n-language-symbolic-planner-hybrids-v4.pdf`

## GitHub Repo URL

`https://github.com/Jason-Wang313/best-of-n-language-symbolic-planner-hybrids`
