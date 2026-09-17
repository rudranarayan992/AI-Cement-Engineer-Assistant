"""Engineering interpretation layer that explains prediction drivers without claiming causality."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping


def interpret_prediction(target: str, prediction: Any, drivers: Iterable[Mapping[str, Any]], ood_status: str, physics_status: str) -> str:
    driver_list = list(drivers)
    if not driver_list:
        return (
            "Qualified measured clinker labels with traceable sample/process/laboratory provenance are required for real clinker ML. "
            "Until then, no real clinker prediction should be presented as operational guidance."
        )

    top = driver_list[0]
    top_feature = top.get("feature", "key process variable")
    note = (
        f"Model association: {top_feature} is the dominant driver of the {target} estimate. "
        f"This does not prove causality; it indicates the model learned a statistical association in the available data. "
        f"Engineering interpretation should be validated against measured process and chemistry evidence."
    )

    if str(ood_status).upper() in {"OUT-OF-DISTRIBUTION", "OOD"}:
        note += " Prediction should be treated cautiously because the current input is outside the model training distribution."
    if str(physics_status).upper() not in {"OK", "PASS"}:
        note += " Physics validation is not clean; engineering recommendation should be withheld until constraints are satisfied."

    return note
