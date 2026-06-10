"""Deterministic language-like plan generator."""

from __future__ import annotations

from typing import Dict, List

import numpy as np

from .domain import Plan, TASKS, compile_plan, render_plan


TEMPLATES: Dict[str, List[str]] = {
    "robust_grounded": [
        "Go to the permit desk",
        "Take the permit",
        "Go to the toolroom",
        "Take the key",
        "Go to the prep room",
        "Take PPE",
        "Take the cold carrier",
        "Go to the lab door",
        "Unlock the lab",
        "Go to the lab",
        "Take the sample",
        "Pack the sample in the cold carrier",
        "Go to the receiving dock",
        "Deliver the sample",
    ],
    "lean_grounded": [
        "Go to the toolroom",
        "Take the key",
        "Go to the lab door",
        "Unlock the lab",
        "Go to the lab",
        "Take the sample",
        "Go to the receiving dock",
        "Deliver the sample",
    ],
    "paperwork_loophole": [
        "Go to the permit desk",
        "Take the permit",
        "Submit the delivery form in the database",
    ],
    "elevator_loophole": [
        "Go to the permit desk",
        "Take the permit",
        "Use the service elevator shortcut",
        "Take the sample",
        "Go to the receiving dock",
        "Deliver the sample",
    ],
    "simulator_lure": [
        "Go to the permit desk",
        "Take the permit",
        "Use the maintenance elevator shortcut",
        "Take the sample",
        "Declare the sample safe",
        "Go to the receiving dock",
        "Deliver the sample",
    ],
    "redundant_safe": [
        "Go to the office",
        "Take the permit",
        "Go to the toolroom",
        "Take the key",
        "Go to the prep room",
        "Take PPE",
        "Take the cold carrier",
        "Go to the lab door",
        "Unlock the lab",
        "Go to the lab",
        "Take the sample",
        "Pack the sample in the cold carrier",
        "Go to the receiving dock",
        "Deliver the sample",
        "Submit the delivery form in the database",
    ],
    "invalid_missing_key": [
        "Go to the lab door",
        "Unlock the lab",
        "Go to the lab",
        "Take the sample",
        "Go to the receiving dock",
        "Deliver the sample",
    ],
    "invalid_unmoved": [
        "Go to the permit desk",
        "Take the permit",
        "Go to the receiving dock",
        "Deliver the sample",
    ],
}


BASE_PROBS: Dict[str, float] = {
    "robust_grounded": 0.22,
    "lean_grounded": 0.21,
    "paperwork_loophole": 0.12,
    "elevator_loophole": 0.10,
    "simulator_lure": 0.08,
    "redundant_safe": 0.07,
    "invalid_missing_key": 0.11,
    "invalid_unmoved": 0.09,
}


LANG_PRIOR: Dict[str, float] = {
    "robust_grounded": -1.7,
    "lean_grounded": -0.7,
    "paperwork_loophole": -0.35,
    "elevator_loophole": -0.55,
    "simulator_lure": -0.75,
    "redundant_safe": -2.2,
    "invalid_missing_key": -0.8,
    "invalid_unmoved": -0.6,
}


def _task_probs(task_name: str) -> np.ndarray:
    task = TASKS[task_name]
    probs = BASE_PROBS.copy()
    loophole_mass = task.loophole_rate
    current = probs["paperwork_loophole"] + probs["elevator_loophole"]
    scale = loophole_mass / current
    probs["paperwork_loophole"] *= scale
    probs["elevator_loophole"] *= scale
    total = sum(probs.values())
    modes = list(probs)
    return np.array([probs[m] / total for m in modes])


def sample_plan(task_name: str, rng: np.random.Generator, sample_id: int = 0) -> Plan:
    modes = list(BASE_PROBS)
    mode = str(rng.choice(modes, p=_task_probs(task_name)))
    steps = list(TEMPLATES[mode])

    # Domain-specific lexical variation without changing compiled symbols.
    if task_name == "sterile_restock":
        steps = [
            s.replace("sample", "kit")
            .replace("receiving dock", "sterile shelf")
            .replace("lab", "isolation room")
            for s in steps
        ]
    elif task_name == "archival_handoff":
        steps = [
            s.replace("sample", "box")
            .replace("receiving dock", "archivist")
            .replace("cold carrier", "archive carrier")
            .replace("lab", "archive room")
            for s in steps
        ]

    logprob = LANG_PRIOR[mode] + float(rng.normal(0.0, 0.08))
    text = render_plan(steps)
    return Plan(
        task=task_name,
        text=text,
        actions=compile_plan(text),
        mode=mode,
        language_logprob=logprob,
        sample_id=sample_id,
    )


def generate_pool(task_name: str, n: int, seed: int) -> List[Plan]:
    rng = np.random.default_rng(seed)
    return [sample_plan(task_name, rng, i) for i in range(n)]
