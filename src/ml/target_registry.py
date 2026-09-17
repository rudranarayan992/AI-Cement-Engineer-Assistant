"""Target registry for supported engineering targets and blocked-model policy."""

from __future__ import annotations

from typing import Dict, List

TARGET_REGISTRY: Dict[str, Dict[str, str | List[str] | bool]] = {
    "compressive_strength": {
        "family": "concrete_benchmark",
        "unit": "MPa",
        "status": "AVAILABLE_BENCHMARK",
        "notes": "Concrete benchmark target is valid only for downstream concrete-strength benchmarking, not clinker prediction.",
    },
    "Free CaO": {
        "family": "clinker_quality",
        "unit": "%",
        "status": "BLOCKED",
        "notes": "Qualified measured clinker labels required before a real model can be trained.",
    },
    "C3S": {
        "family": "clinker_phase",
        "unit": "%",
        "status": "BLOCKED",
        "notes": "Qualified measured clinker labels required before a real model can be trained.",
    },
    "C2S": {
        "family": "clinker_phase",
        "unit": "%",
        "status": "BLOCKED",
        "notes": "Qualified measured clinker labels required before a real model can be trained.",
    },
    "C3A": {
        "family": "clinker_phase",
        "unit": "%",
        "status": "BLOCKED",
        "notes": "Qualified measured clinker labels required before a real model can be trained.",
    },
    "C4AF": {
        "family": "clinker_phase",
        "unit": "%",
        "status": "BLOCKED",
        "notes": "Qualified measured clinker labels required before a real model can be trained.",
    },
}


def get_registered_targets() -> List[str]:
    return list(TARGET_REGISTRY.keys())


def get_target_entry(target: str) -> Dict[str, str | List[str] | bool]:
    key = (target or "").strip()
    aliases = {
        "free_cao": "Free CaO",
        "free cao": "Free CaO",
        "compressive-strength": "compressive_strength",
        "compressive strength": "compressive_strength",
        "c3s": "C3S",
        "c2s": "C2S",
        "c3a": "C3A",
        "c4af": "C4AF",
    }
    resolved = aliases.get(key.lower(), key)
    if resolved not in TARGET_REGISTRY:
        raise ValueError(f"Target '{target}' is not registered in the repository target registry.")
    return TARGET_REGISTRY[resolved]
