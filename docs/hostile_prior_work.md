# Hostile Prior Work

These are the papers a skeptical reviewer is most likely to use to compress this project into "already known."
The distinction we preserve is narrow: candidate language plans are compiled into symbolic actions, selected by
a checker/simulator/verifier, and then judged by a hidden executor whose semantics are stricter than the symbols.

## 1. LLM+P: Empowering Large Language Models with Optimal Planning Proficiency

- Link: https://arxiv.org/abs/2304.11477
- Reviewer attack: This already combines language models, planning, and external evaluation.
- Why it does not subsume this project: Closest architectural ancestor; it does not study candidate-pool selection pressure over verifier-compatible loopholes.

## 2. Tree of Thoughts: Deliberate Problem Solving with Large Language Models

- Link: https://arxiv.org/abs/2305.10601
- Reviewer attack: This already combines language models, planning, and external evaluation.
- Why it does not subsume this project: Relevant candidate-search ancestor; it is not about symbolic planners or execution-validity collapse.

## 3. Self-Consistency Improves Chain of Thought Reasoning in Language Models

- Link: https://arxiv.org/abs/2203.11171
- Reviewer attack: This already combines language models, planning, and external evaluation.
- Why it does not subsume this project: Canonical sample-more inference; it lacks an external symbolic verifier and hidden executor.

## 4. On the Planning, Search, and Memorization Capabilities of Large Language Models

- Link: http://arxiv.org/abs/2309.01868v1
- Reviewer attack: This already combines language models, planning, and external evaluation.
- Why it does not subsume this project: Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.

## 5. Large Language Models as Planning Domain Generators

- Link: http://arxiv.org/abs/2405.06650v1
- Reviewer attack: This already combines language models, planning, and external evaluation.
- Why it does not subsume this project: Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.

## 6. A Survey on Large Language Models for Automated Planning

- Link: http://arxiv.org/abs/2502.12435v1
- Reviewer attack: This already combines language models, planning, and external evaluation.
- Why it does not subsume this project: Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.

## 7. NL2Plan: Robust LLM-Driven Planning from Minimal Text Descriptions

- Link: http://arxiv.org/abs/2405.04215v2
- Reviewer attack: This already combines language models, planning, and external evaluation.
- Why it does not subsume this project: Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.

## 8. On The Planning Abilities of OpenAI's o1 Models: Feasibility, Optimality, and Generalizability

- Link: http://arxiv.org/abs/2409.19924v4
- Reviewer attack: This already combines language models, planning, and external evaluation.
- Why it does not subsume this project: Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.

## 9. Exploring and Benchmarking the Planning Capabilities of Large Language Models

- Link: http://arxiv.org/abs/2406.13094v2
- Reviewer attack: This already combines language models, planning, and external evaluation.
- Why it does not subsume this project: Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.

## 10. Bootstrapping Object-level Planning with Large Language Models

- Link: http://arxiv.org/abs/2409.12262v4
- Reviewer attack: This already combines language models, planning, and external evaluation.
- Why it does not subsume this project: Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.

## Bottom Line

The hostile set motivates a modest contribution. The paper should not claim that symbolic verification is bad,
that LLM planning is broadly unsafe, or that the repair is general. It can claim a controlled, reproducible
failure mode: proxy-optimal candidate selection over language-generated symbolic plans can make execution
validity worse as N grows when loophole plans have higher verifier score than grounded plans. The v4
FrozenLake tier strengthens external validity by reproducing the same boundary-contract failure on a standard
Gymnasium environment, but it still does not replace trained language-planner or robotics evidence.
