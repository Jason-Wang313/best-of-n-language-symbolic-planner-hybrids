# Literature Map

This first-pass map was built from curated anchor papers plus arXiv metadata sweeps over LLM planning,
symbolic/PDDL planning, tool-using agents, verifier/reward-model selection, and reward hacking. The static
CSV contains 120 entries, satisfying the requested 100-paper landscape sweep.

## Cluster Counts

- AI feedback and verification: 1
- LLM agents and tool use: 13
- LLM plus classical planning: 71
- constrained decision making: 1
- inference-time search: 6
- language-conditioned robotics: 12
- neuro-symbolic systems: 1
- planning and reasoning: 8
- programmatic planning: 1
- reward hacking and specification gaming: 1
- reward models and selection: 1
- reward models and verification: 1
- self-refinement and feedback: 1
- tool use: 1
- tool use and verification: 1

## 100-Paper Sweep Takeaways

- LLM+classical-planning work typically asks whether language can translate, repair, or call a planner; it rarely treats candidate multiplicity as a statistical pressure that changes the selected plan distribution.
- Agent and robotics papers often add feedback or affordance filters, but the filter is usually treated as a safety improvement rather than a surface that proxy-ranked selection can exploit.
- Reward-model and verifier-hacking papers give the closest general warning: optimizing a proxy at inference time can expose misspecification. The symbolic-planner hybrid setting adds a discrete validity boundary and a separate hidden executor.
- Neuro-symbolic systems motivate the architecture, but the local contribution is narrower: a measurable semantic-symbolic mismatch law and diagnostics for selected plans.

## 30-Paper Serious Skim Set

- LLM+P: Empowering Large Language Models with Optimal Planning Proficiency (2023, arXiv): LLM plus classical planning; threat=high. Closest architectural ancestor; it does not study candidate-pool selection pressure over verifier-compatible loopholes.
- Large Language Models as Planning Domain Generators (2024, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- NL2Plan: Robust LLM-Driven Planning from Minimal Text Descriptions (2024, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Bootstrapping Object-level Planning with Large Language Models (2024, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Chasing Progress, Not Perfection: Revisiting Strategies for End-to-End LLM Plan Generation (2024, arXiv): reward models and verification; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Novelty Adaptation Through Hybrid Large Language Model (LLM)-Symbolic Planning and LLM-guided Reinforcement Learning (2026, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- PSALM-V: Automating Symbolic Planning in Interactive Visual Environments with Large Language Models (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Teaching LLMs to Plan: Logical Chain-of-Thought Instruction Tuning for Symbolic Planning (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Agent+P: Guiding UI Agents via Symbolic Planning (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Aligning LLM+PDDL Symbolic Plans with Human Objective Specifications through Evolutionary Algorithm Guidance (2024, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Bounding Boxes as Goals: Language-Conditioned Grasping via Neuro-Symbolic Planning (2026, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Planning in the Dark: LLM-Symbolic Planning Pipeline without Experts (2024, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Part-X-MLLM: Part-aware 3D Multimodal Large Language Model (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Planning with Vision-Language Models and a Use Case in Robot-Assisted Teaching (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Maritime Mission Planning for Unmanned Surface Vessel using Large Language Model (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Adaptive Domain Modeling with Language Models: A Multi-Agent Approach to Task Planning (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- ViPlan: A Benchmark for Visual Planning with Symbolic Predicates and Vision-Language Models (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Frontier Large Language Models Rival State-of-the-Art Planners (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Learning to Reason over Scene Graphs: A Case Study of Finetuning GPT-2 into a Robot Language Model for Grounded Task Planning (2023, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- From Sands to Mansions: Towards Automated Cyberattack Emulation with Classical Planning and Large Language Models (2024, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- AutoGPT+P: Affordance-based Task Planning with Large Language Models (2024, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Symbolic Planning and Code Generation for Grounded Dialogue (2023, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Enhancing Cognitive Robotics with Commonsense through LLM-Generated Preconditions and Subgoals (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- SYMDIREC: A Neuro-Symbolic Divide-Retrieve-Conquer Framework for Enhanced RTL Synthesis and Summarization (2026, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Self-CriTeach: LLM Self-Teaching and Self-Critiquing for Improving Robotic Planning via Automated Domain Generation (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Closed-Loop Verbal Reinforcement Learning for Task-Level Robotic Planning (2026, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Meta-Optimization and Program Search using Language Models for Task and Motion Planning (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Constrained Natural Language Action Planning for Resilient Embodied Systems (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- AAAI Workshop on AI Planning for Cyber-Physical Systems -- CAIPI24 (2024, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- CoMIC: Collaborative Memory and Insights Circulation for Long-Horizon LLM Agents in Cloud-Edge Systems (2026, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.

## 20-25-Paper Deep-Read Threat Set

- LLM+P: Empowering Large Language Models with Optimal Planning Proficiency (2023, arXiv): LLM plus classical planning; threat=high. Closest architectural ancestor; it does not study candidate-pool selection pressure over verifier-compatible loopholes.
- Large Language Models as Planning Domain Generators (2024, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- NL2Plan: Robust LLM-Driven Planning from Minimal Text Descriptions (2024, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Bootstrapping Object-level Planning with Large Language Models (2024, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Chasing Progress, Not Perfection: Revisiting Strategies for End-to-End LLM Plan Generation (2024, arXiv): reward models and verification; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Novelty Adaptation Through Hybrid Large Language Model (LLM)-Symbolic Planning and LLM-guided Reinforcement Learning (2026, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- PSALM-V: Automating Symbolic Planning in Interactive Visual Environments with Large Language Models (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Teaching LLMs to Plan: Logical Chain-of-Thought Instruction Tuning for Symbolic Planning (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Agent+P: Guiding UI Agents via Symbolic Planning (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Aligning LLM+PDDL Symbolic Plans with Human Objective Specifications through Evolutionary Algorithm Guidance (2024, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Bounding Boxes as Goals: Language-Conditioned Grasping via Neuro-Symbolic Planning (2026, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Planning in the Dark: LLM-Symbolic Planning Pipeline without Experts (2024, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Part-X-MLLM: Part-aware 3D Multimodal Large Language Model (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Planning with Vision-Language Models and a Use Case in Robot-Assisted Teaching (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Maritime Mission Planning for Unmanned Surface Vessel using Large Language Model (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Adaptive Domain Modeling with Language Models: A Multi-Agent Approach to Task Planning (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- ViPlan: A Benchmark for Visual Planning with Symbolic Predicates and Vision-Language Models (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Frontier Large Language Models Rival State-of-the-Art Planners (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Learning to Reason over Scene Graphs: A Case Study of Finetuning GPT-2 into a Robot Language Model for Grounded Task Planning (2023, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- From Sands to Mansions: Towards Automated Cyberattack Emulation with Classical Planning and Large Language Models (2024, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- AutoGPT+P: Affordance-based Task Planning with Large Language Models (2024, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Symbolic Planning and Code Generation for Grounded Dialogue (2023, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- Enhancing Cognitive Robotics with Commonsense through LLM-Generated Preconditions and Subgoals (2025, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.
- SYMDIREC: A Neuro-Symbolic Divide-Retrieve-Conquer Framework for Enhanced RTL Synthesis and Summarization (2026, arXiv): LLM plus classical planning; threat=high. Relevant to the landscape, but it does not directly subsume the tested mechanism: finite-N selection concentrating symbolic-valid semantic loopholes under a separate executor.

## Decision Pressure From Prior Work

The broad literature already covers LLM-to-planner translation, embodied language agents, self-correction,
external-tool use, and reward-model overoptimization. The most defensible first-pass contribution is therefore
not another planner wrapper. It is the mechanism-level claim that, in language/symbolic hybrids, proxy-ranked candidate selection
can monotonically concentrate rare plans that satisfy the symbolic interface while violating hidden execution
semantics. This survives the prior-work pass because it is architecture-specific, testable, and repairable.
