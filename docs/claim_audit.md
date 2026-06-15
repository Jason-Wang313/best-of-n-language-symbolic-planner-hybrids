# Claim Audit

Version: `v4`. Baseline preset: `full`. Baseline max N: `128`. Expansion max N: `512`. FrozenLake max N: `128`.

## Expansion Checks

- symbolic_proxy_collapses_at_512: True
- simulator_proxy_collapses_at_512: True
- repairs_restore_execution: True
- rare_loopholes_are_amplified: True
- strict_boundary_control_recovers: True
- proxy_tail_mismatch_visible: True

## Expansion Key Numbers

- max_n: 512
- symbolic_proxy_utility: 15.9
- symbolic_proxy_loophole: 1.0
- symbolic_proxy_success: 0.0
- simulator_proxy_utility: 15.9
- adversarial_gate_utility: 84.6
- uncertainty_lcb_utility: 84.6
- rare_prior_symbolic_loophole: 1.0
- strict_boundary_success: 1.0
- loophole_proxy_advantage: 68.987
- grounded_utility_advantage: 60.61

## FrozenLake Checks

- frozenlake_symbolic_enters_holes: True
- frozenlake_simulator_enters_holes: True
- frozenlake_true_utility_drops: True
- frozenlake_hazard_gate_recovers: True
- frozenlake_lcb_recovers: True
- frozenlake_proxy_tail_mismatch: True

## FrozenLake Key Numbers

- max_n: 128
- n1_symbolic_utility: 40.106
- symbolic_utility: 0.0
- symbolic_success: 0.0
- symbolic_enters_hole: 1.0
- simulator_utility: 0.0
- hazard_gate_utility: 93.0
- hazard_gate_success: 1.0
- uncertainty_lcb_utility: 93.0
- uncertainty_lcb_success: 1.0
- hazard_proxy_advantage: 22.137
- safe_utility_advantage: 93.0

## Baseline Supported Checks

- symbolic_proxy_concentrates_loopholes: True
- simulator_proxy_concentrates_loopholes: True
- repairs_reduce_loopholes: True
- repairs_restore_execution_success: True

## Baseline Key Numbers

- symbolic_proxy_true_utility: 15.9
- symbolic_proxy_loophole_rate: 100.0%
- symbolic_proxy_proxy_true_gap: 109.828
- simulator_proxy_true_utility: 15.9
- simulator_proxy_loophole_rate: 100.0%
- adversarial_gate_true_utility: 84.6
- uncertainty_lcb_true_utility: 84.6
- best_repair: calibrated_boundary
- best_repair_true_utility: 84.6
- best_repair_success_rate: 100.0%
- best_repair_loophole_rate: 0.0%

## Unsupported

- real-robot safety claims
- claims about arbitrary external verifiers
- claims that symbolic planning is intrinsically unsafe
- claims that semantic uncertainty penalties are a complete solution

## Final PDF Targets

- repository: `C:\Users\wangz\Downloads\best-of-n-language-symbolic-planner-hybrids\paper\final\best-of-n-language-symbolic-planner-hybrids-v4.pdf`
- desktop: `C:\Users\wangz\OneDrive\Desktop\best-of-n-language-symbolic-planner-hybrids-v4.pdf`
- minimum pages: 25
