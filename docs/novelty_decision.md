# Novelty Decision

## Chosen Angle

**Semantic-symbolic loophole concentration.** In a language/symbolic planner hybrid, proxy-ranked candidate selection
can increase symbolic or simulator score while decreasing true execution utility because the selected candidate
distribution becomes dominated by rare plans that exploit the abstraction boundary.

## Why This Was Chosen

The literature sweep contains 120 entries. The closest work covers LLM-to-PDDL translation, classical
planner delegation, tool-using agents, and reward/verifier hacking. Those areas make broad architectural and
safety points. The unoccupied slot is a small mechanism paper for this specific hybrid:

1. language model samples candidate plans,
2. compiler/checker maps text to symbolic actions,
3. verifier/simulator scores or validates the candidates,
4. execution has hidden semantics absent from the symbolic state,
5. Proxy-ranked selection amplifies the rare candidate type with the highest proxy score.

## Formal Claim Kept

If loophole candidates occur independently with probability p>0, every loophole receives a higher proxy score
than every grounded candidate, and loopholes have lower true utility, then the probability that top-proxy selection
selects a loophole is 1-(1-p)^N and the expected true utility monotonically decreases to the loophole utility.

## Empirical Claim Kept

In the toy domains, symbolic and simulator proxy selectors should show rising selected-loophole occupancy and a
growing proxy-true gap as N increases. Repairs are allowed to claim only controlled evidence: semantic
uncertainty penalties and adversarial execution gates reduce the mismatch in these domains.

The v4 empirical scope also includes a standard FrozenLake-v1 hidden-execution tier. It is not a leaderboard
claim; it is a benchmark check that a coarse symbolic reachability certificate can be invalid under environment
dynamics that include holes.

## Claims Rejected

- No claim of real-world robotics validation.
- No claim that all symbolic planners are unsafe.
- No claim that every verifier is exploitable.
- No claim that the proposed repairs are sufficient beyond the tested abstraction mismatch.
