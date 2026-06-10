"""Coarse symbolic checker for compiled plans."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Set


@dataclass(frozen=True)
class CheckResult:
    valid: bool
    delivered: bool
    violations: Sequence[str]
    state: Dict[str, object]


def symbolic_check(actions: Sequence[str]) -> CheckResult:
    loc = "start"
    inventory: Set[str] = set()
    unlocked = False
    delivered = False
    violations: List[str] = []

    def require(cond: bool, message: str) -> bool:
        if not cond:
            violations.append(message)
            return False
        return True

    for i, action in enumerate(actions):
        prefix, _, arg = action.partition(":")
        at = f"step_{i + 1}:{action}"
        if prefix == "go":
            if arg == "lab" and not require(unlocked, at + ":lab_locked"):
                continue
            loc = arg
        elif prefix == "take":
            if arg == "key":
                if require(loc == "toolroom", at + ":key_not_at_location"):
                    inventory.add("key")
            elif arg == "permit":
                if require(loc == "office", at + ":permit_not_at_location"):
                    inventory.add("permit")
            elif arg == "ppe":
                if require(loc == "prep", at + ":ppe_not_at_location"):
                    inventory.add("ppe")
            elif arg == "cold_pack":
                if require(loc == "prep", at + ":carrier_not_at_location"):
                    inventory.add("cold_pack")
            else:
                violations.append(at + ":unknown_take")
        elif prefix == "unlock":
            if require(loc == "labdoor", at + ":not_at_labdoor") and require(
                "key" in inventory, at + ":missing_key"
            ):
                unlocked = True
        elif prefix == "shortcut":
            if require("permit" in inventory, at + ":shortcut_requires_permit"):
                # The abstraction treats the shortcut as a certified transition.
                loc = "lab"
                unlocked = True
        elif prefix == "pickup":
            if require(loc == "lab", at + ":sample_not_accessible") and require(
                unlocked, at + ":lab_not_unlocked"
            ):
                inventory.add("sample")
        elif prefix == "pack":
            if require("sample" in inventory, at + ":no_sample_to_pack") and require(
                "cold_pack" in inventory, at + ":no_carrier"
            ):
                inventory.add("packed")
        elif prefix == "deliver":
            if require(loc == "goal", at + ":not_at_goal") and require(
                "sample" in inventory, at + ":no_sample_to_deliver"
            ):
                delivered = True
        elif prefix == "mark":
            if require("permit" in inventory, at + ":paperwork_requires_permit"):
                # The checker has a semantic hole: records can satisfy the goal.
                delivered = True
        elif prefix == "declare":
            inventory.add("declared_safe")
        else:
            violations.append(at + ":unknown_action")

    valid = delivered and not violations
    state: Dict[str, object] = {
        "loc": loc,
        "inventory": sorted(inventory),
        "unlocked": unlocked,
        "delivered": delivered,
    }
    return CheckResult(valid=valid, delivered=delivered, violations=tuple(violations), state=state)
