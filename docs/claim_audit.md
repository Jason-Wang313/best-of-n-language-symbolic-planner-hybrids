# Claim Audit

Preset: `full`. Max N: `128`.

## Supported

- symbolic_bon_concentrates_loopholes: True
- simulator_bon_concentrates_loopholes: True
- repairs_reduce_loopholes: True
- repairs_restore_execution_success: True

## Key Numbers

- symbolic_bon_true_utility: 15.9
- symbolic_bon_loophole_rate: 100.0%
- symbolic_bon_proxy_true_gap: 109.828
- simulator_bon_true_utility: 15.9
- simulator_bon_loophole_rate: 100.0%
- adversarial_gate_true_utility: 84.6
- uncertainty_lcb_true_utility: 84.6
- best_repair: calibrated_bon
- best_repair_true_utility: 84.6
- best_repair_success_rate: 100.0%
- best_repair_loophole_rate: 0.0%

## Unsupported

- real-robot safety claims
- claims about arbitrary external verifiers
- claims that symbolic planning is intrinsically unsafe
- claims that semantic uncertainty penalties are a complete solution
