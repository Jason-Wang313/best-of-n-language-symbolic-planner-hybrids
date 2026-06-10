# Final Audit

## Main Thesis

Best-of-N selection in language-planner / symbolic-planner hybrids can concentrate rare semantic-symbolic loopholes: plans that satisfy a symbolic checker or surrogate simulator while failing hidden execution semantics.

## Genuine Novelty

The first-pass novelty is mechanism-level, not architectural. Prior work covers LLM-to-PDDL translation, language agents, tool use, affordance filtering, verifier reranking, and reward hacking. This repo isolates the specific finite-N selection pressure created when language-generated plans are compiled into symbolic actions, scored by a checker/simulator, and then judged by a stricter executor.

## Literature Coverage

The repo includes:

- `docs/related_work_matrix.csv` with 120 entries.
- `docs/literature_map.md` with the 100-paper sweep, 30-paper serious skim set, and 20-25-paper deep-read threat set.
- `docs/hostile_prior_work.md` with 10 hostile prior-work threats.
- `docs/novelty_decision.md` documenting why the semantic-symbolic loophole concentration angle was chosen.

## Proof Status

The formal claim is a simple two-type finite-N proposition. If loopholes occur independently with probability `p > 0`, every loophole receives higher proxy score than every grounded candidate, and loopholes have lower true utility, then proxy Best-of-N selects a loophole with probability `1 - (1-p)^N`, so expected true utility decreases monotonically to the loophole utility. The proof is exact under those assumptions and intentionally narrow.

## Strongest Empirical Result

In the full local run at `N=128`, symbolic Best-of-N and simulator Best-of-N both select loophole plans 100.0% of the time and have mean true utility `15.9`, while the repaired selectors reach mean true utility `84.6`.

## Strongest Diagnostic Result

The clearest diagnostic is selected loophole occupancy: symbolic/simulator Best-of-N rise to 100.0% selected loopholes, and the mean proxy-true gap for symbolic Best-of-N at `N=128` is `109.828`.

## Strongest Repair Result

The controlled repairs `calibrated_bon`, `adversarial_gate`, and `uncertainty_lcb` all reach 100.0% execution success and 0.0% loophole occupancy at `N=128` in this toy setting.

## Biggest Weaknesses

- The domains are synthetic and intentionally small.
- The language generator is stochastic templates, not a frontier LLM.
- The simulator and hidden executor are handcrafted to expose the mechanism.
- The repairs use privileged knowledge of the abstraction gap.
- The result should not be generalized to deployed robotics or arbitrary verifiers without new evidence.

## Paper-Readiness Judgment

Paper-worthy v1 as a controlled mechanism submission draft. The PDF is anonymous and uses the official-style `iclr2027_conference.sty` template with `\iclrfinalcopy` commented out. It is not benchmark-complete or deployment-ready.

## Verification

- `pytest`: 6 passed.
- Full experiment: `python -m experiments.run_suite --preset full`.
- Claim audit: `python scripts/run_claim_audit.py --preset full`.
- Paper build: `python scripts/build_paper.py`.

## Final PDF Path

`C:\Users\wangz\Downloads\best-of-n-language-symbolic-planner-hybrids.pdf`

## GitHub Repo URL

`https://github.com/Jason-Wang313/best-of-n-language-symbolic-planner-hybrids`
