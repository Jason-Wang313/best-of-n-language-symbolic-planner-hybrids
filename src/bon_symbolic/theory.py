"""Small finite-N calculations for the paper's mechanism proposition."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TwoTypeLaw:
    p_loophole: float
    utility_good: float
    utility_loophole: float

    def loophole_selected_probability(self, n: int) -> float:
        """If every loophole has higher proxy score than every good plan."""

        return 1.0 - (1.0 - self.p_loophole) ** n

    def expected_true_utility(self, n: int) -> float:
        p = self.loophole_selected_probability(n)
        return p * self.utility_loophole + (1.0 - p) * self.utility_good

    def utility_drop(self, n: int) -> float:
        return self.utility_good - self.expected_true_utility(n)
