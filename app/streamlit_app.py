"""AI Cement Engineer frontend.

This Streamlit app intentionally exposes only the chemistry-aware engineering
capabilities currently validated in the repository:
- raw-material assay inspection
- raw-mix recipe calculation
- LSF / SM / AM chemistry checks
- deterministic scenario analysis
- engineering copilot guidance
- transparent provenance and blocked-model status

It does not claim clinker ML or synthetic clinker predictions as real results.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from src.llm.engineering_copilot import EngineeringCopilot
from src.optimization.raw_mix_scenarios import (
    DEFAULT_BASELINE_RECIPE,
    calculate_raw_mix_scenario,
    check_engineering_constraints,
    compare_scenarios,
    deterministic_sensitivity_analysis,
)

RAW_MATERIALS_PATH = PROJECT_ROOT / "data" / "raw_materials" / "raw_materials_database.csv"
MODEL_DIR = PROJECT_ROOT / "models"

PROJECT_STATUS = {
    "HYBRID ENGINEERING SYSTEM": "ACTIVE",
    "RAW MATERIALS": "AVAILABLE",
    "ENGINEERING CALCULATIONS": "AVAILABLE",
    "CLINKER ML": "BLOCKED UNTIL VALIDATED DATA",
    "CEMENT QUALITY": "STAGED",
    "CONCRETE PERFORMANCE": "STAGED",
    "HISTORICAL MEMORY": "ACTIVE",
    "MODEL MONITORING": "ACTIVE",
    "LLM ADVISOR": "CONSTRAINED",
}

BADGE_COLORS = {
    "ACTIVE": "#ecfdf5",
    "AVAILABLE": "#eff6ff",
    "REFERENCE": "#eef2ff",
    "SYNTHETIC": "#fff7ed",
    "BENCHMARK": "#f5f3ff",
    "BLOCKED": "#fef2f2",
    "UNAVAILABLE": "#f3f4f6",
    "REQUIRED": "#fef3c7",
    "VALID": "#ecfdf5",
    "WARNING": "#fff7ed",
    "FAIL": "#fef2f2",
    "STAGED": "#e0f2fe",
    "CONSTRAINED": "#f5f3ff",
}


def _badge(label: str) -> str:
    color = BADGE_COLORS.get(str(label).upper(), "#f3f4f6")
    return (
        f"<span style='display:inline-block;padding:0.25rem 0.6rem;border-radius:999px;"
        f"font-size:0.72rem;font-weight:700;letter-spacing:0.03em;"
        f"background:{color};color:#111827;border:1px solid rgba(17,24,39,0.08);'>"
        f"{str(label).upper()}</span>"
    )


def _status_card(title: str, value: str, detail: str = "") -> None:
    st.markdown(
        f"""
        <div style="padding: 1rem 1rem 0.9rem; border: 1px solid #e5e7eb; border-radius: 0.9rem; background: #f9fafb; min-height: 120px; margin-bottom: 0.5rem;">
            <div style="font-size: 0.7rem; color: #6b7280; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;">{title}</div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #111827; margin-top: 0.5rem;">{value}</div>
            <div style="font-size: 0.8rem; color: #4b5563; margin-top: 0.45rem;">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _callout(message: str, kind: str = "info") -> None:
    if kind == "warning":
        st.warning(message)
    elif kind == "error":
        st.error(message)
    elif kind == "success":
        st.success(message)
    else:
        st.info(message)


@st.cache_data
def load_material_library() -> pd.DataFrame:
    if not RAW_MATERIALS_PATH.exists():
        raise FileNotFoundError(f"Raw material database not found: {RAW_MATERIALS_PATH}")
    return pd.read_csv(RAW_MATERIALS_PATH)


def compute_recipe_result(materials: pd.DataFrame | None, recipe: Dict[str, float]) -> Dict[str, Any]:
    materials_df = materials if materials is not None else load_material_library()
    try:
        return calculate_raw_mix_scenario(materials_df, recipe)
    except Exception as exc:  # pragma: no cover - defensive only
        return {
            "valid": False,
            "errors": [str(exc)],
            "warnings": [],
            "chemistry": {},
            "moduli": {"LSF": None, "SM": None, "AM": None},
            "provenance": {"source_dataset": str(RAW_MATERIALS_PATH), "input_data_status": "MEASURED INPUT"},
            "mass_balance_ok": False,
        }


def get_blocked_models() -> List[Dict[str, str]]:
    return [
        {"model": "Free CaO", "status": "BLOCKED", "reason": "No verified measured clinker target dataset."},
        {"model": "C3S", "status": "BLOCKED", "reason": "No verified measured clinker target dataset."},
        {"model": "C2S", "status": "BLOCKED", "reason": "No verified measured clinker target dataset."},
        {"model": "C3A", "status": "BLOCKED", "reason": "No verified measured clinker target dataset."},
        {"model": "C4AF", "status": "BLOCKED", "reason": "No verified measured clinker target dataset."},
    ]


def get_model_center_summary() -> List[Dict[str, str]]:
    available = [{
        "model": "Concrete strength benchmark",
        "status": "AVAILABLE",
        "category": "DOWNSTREAM CONCRETE BENCHMARK",
        "reason": "Actual concrete benchmark pathway is available; no fabricated clinker predictions are shown.",
    }]
    return available + get_blocked_models()


def get_data_provenance_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Dataset": "raw_materials_database.csv",
                "Type": "REAL / ASSAY REFERENCE",
                "Status": "VALID FOR RAW-MATERIAL CHEMISTRY",
                "Provenance": "Measured assay library for chemistry calculations",
                "Allowed use": "Raw-material chemistry, moduli, recipe engineering",
            },
            {
                "Dataset": "raw_meal_samples.csv",
                "Type": "SYNTHETIC",
                "Status": "NOT VALID FOR REAL CLINKER ML",
                "Provenance": "Repository-generated synthetic chemistry batch table",
                "Allowed use": "Demonstration only; not a real clinker target dataset",
            },
            {
                "Dataset": "cement_master_dataset.csv",
                "Type": "SYNTHETIC",
                "Status": "NOT VALID FOR CLINKER ML",
                "Provenance": "Generated demo chain in repository scripts",
                "Allowed use": "Synthetic engineering demonstration only",
            },
            {
                "Dataset": "Concrete_Data.xls",
                "Type": "REAL CONCRETE BENCHMARK",
                "Status": "VALID ONLY FOR CONCRETE STRENGTH MODELING",
                "Provenance": "Concrete benchmark data downstream of clinker chemistry",
                "Allowed use": "Concrete strength benchmarking only",
            },
            {
                "Dataset": "clinker targets",
                "Type": "NO VERIFIED REAL DATA",
                "Status": "BLOCKED",
                "Provenance": "No measured clinker target dataset has been accepted",
                "Allowed use": "Unavailable; real clinker ML remains blocked",
            },
        ]
    )


def get_research_status_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"Step": "STEP 1", "Status": "COMPLETED", "Note": "Project baseline and repository structure"},
            {"Step": "STEP 2", "Status": "COMPLETED", "Note": "Data inventory and scientific framing"},
            {"Step": "STEP 3", "Status": "COMPLETED", "Note": "Engineering requirements and constraints"},
            {"Step": "STEP 4", "Status": "COMPLETED", "Note": "Chemistry basis and validation"},
            {"Step": "STEP 5", "Status": "COMPLETED", "Note": "Raw-material library and assays"},
            {"Step": "STEP 6", "Status": "COMPLETED", "Note": "Raw-mix chemistry calculations"},
            {"Step": "STEP 7", "Status": "COMPLETED", "Note": "Physics validation and feasibility checks"},
            {"Step": "STEP 8", "Status": "COMPLETED", "Note": "Scenario analysis tooling"},
            {"Step": "STEP 9", "Status": "COMPLETED", "Note": "Research-readiness boundary"},
            {"Step": "STEP 10", "Status": "COMPLETED", "Note": "AI engineering copilot and explainability"},
            {"Step": "STEP 11", "Status": "COMPLETED", "Note": "Prepared real-data gate and target taxonomy"},
            {"Step": "STEP 12", "Status": "BLOCKED", "Note": "No verified measured clinker dataset"},
            {"Step": "STEP 13", "Status": "BLOCKED — REAL CLINKER DATA REQUIRED", "Note": "Clinker supervised ML remains intentionally disabled"},
        ]
    )


def answer_engineering_question(question: str, context: Dict[str, Any] | None = None) -> str:
    q = (question or "").strip()
    q_lower = q.lower()
    context = context or {}

    if any(keyword in q_lower for keyword in ["predict free cao", "free cao", "predict c3s", "predict c2s", "predict c3a", "predict c4af", "clinker prediction"]) and "not" not in q_lower:
        return (
            "### BLOCKED: Clinker ML is currently unavailable\n\n"
            "Clinker ML is currently unavailable because the project does not contain a qualified measured clinker dataset. "
            "The repository does not include a verified measured clinker target dataset, and synthetic or generated phase values are not valid measured targets. "
            "No numerical clinker prediction should be generated until a traceable measured clinker dataset is accepted."
        )

    if "predict free cao" in q_lower or ("free cao" in q_lower and "predict" in q_lower):
        return (
            "### BLOCKED: Free CaO prediction is unavailable\n\n"
            "The repository does not contain a verified measured clinker target dataset. "
            "The available `Free_CAO` values are synthetic/generated and cannot be treated as real measured labels. "
            "Until a traceable clinker dataset with lab-validated targets is supplied, the model remains unavailable."
        )

    if "what data do i need for clinker ml" in q_lower or ("clinker ml" in q_lower and "data" in q_lower):
        return (
            "### Required dataset for future clinker ML\n\n"
            "- measured clinker target values\n"
            "- measurement method (XRD/Rietveld or equivalent lab protocol)\n"
            "- sample IDs and clinker IDs\n"
            "- timestamps and sampling dates\n"
            "- raw-material linkage\n"
            "- kiln/process linkage\n"
            "- temporal alignment between feed, kiln conditions, and clinker sample\n"
            "- provenance and lab QA/QC metadata"
        )

    copilot = EngineeringCopilot()
    response = copilot.answer_question(q, context)
    return (
        response
        + "\n\n---\n\n"
        + "**Hybrid-system rule:** The LLM is not an independent predictor. It should use calculations, ML predictions, historical cases, uncertainty, SHAP/XAI results, and engineering constraints to support a recommendation for engineer approval."
    )


def render_overview() -> None:
    st.title("AI CEMENT ENGINEER")
    st.caption("Hybrid Physics-Informed, Explainable, Historical-Memory Decision Support System")

    st.info(
        "The LLM is a constrained engineering advisor. It receives calculations, predictions, historical cases, uncertainty, XAI/SHAP explanations, and constraints; it does not replace the numerical models."
    )

    st.markdown(
        """
        AI CEMENT ENGINEER
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
 ENGINEERING             ML               MEMORY
 CALCULATIONS        PREDICTIONS        + CASES
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                    DIAGNOSTICS
                           │
                           ▼
                     UNCERTAINTY
                           │
                           ▼
                         XAI
                           │
                           ▼
                    RECOMMENDATION
                           │
                           ▼
                         LLM
                           │
                           ▼
                   ENGINEER APPROVAL
                           │
                           ▼
                    ACTUAL LAB DATA
                           │
                           ▼
                  MODEL MONITORING
                           │
                           ▼
                  CONTROLLED RETRAINING
        """,
        unsafe_allow_html=False,
    )

    st.markdown("---")
    st.subheader("Engineering status")
    cols = st.columns(len(PROJECT_STATUS))
    for idx, (label, status) in enumerate(PROJECT_STATUS.items()):
        with cols[idx]:
            _status_card(label, status, "")

    st.markdown("---")
    st.subheader("17-module architecture")
    modules = [
        "AI Command Center",
        "Raw Materials",
        "Raw Mix / Raw Meal",
        "Kiln / Process",
        "Clinker",
        "Cement Blending",
        "Cement Quality",
        "Concrete Mix",
        "Multi-Age Strength",
        "Failure Detection",
        "Likely Contributing Factors",
        "Historical Memory",
        "XAI / SHAP",
        "Uncertainty / OOD",
        "What-If / Optimization",
        "Actual vs Predicted",
        "Model Center / Retraining",
    ]
    cols = st.columns(3)
    for idx, module_name in enumerate(modules):
        with cols[idx % 3]:
            _module_card(module_name)

    st.markdown("---")
    st.subheader("Multi-stage system logic")
    st.code(
        "Raw Materials\n  ↓\nChemistry / Mass Balance\n  ↓\nRaw Mix / LSF / SM / AM\n  ↓\nKiln / Process\n  ↓\nClinker\n  ↓\nCement Quality\n  ↓\nConcrete Performance\n  ↓\nFailure Detection -> Likely Factors -> Historical Memory -> XAI + Uncertainty\n  ↓\nRecommendation -> Engineer Approval -> Actual Lab Result -> Retraining",
        language="text",
    )
    st.caption("This matches the hybrid architecture: deterministic engineering first, ML only in validated domains, then diagnostics, uncertainty, explanations, historical memory, and controlled retraining.")


def render_placeholder_module(title: str, body: str) -> None:
    st.title(title)
    st.markdown(f"{_badge('STAGED')} {_badge('HYBRID')} {_badge('ENGINEERING')}")
    st.info(body)
    st.code(
        "Inputs\n  ↓\nValidated engineering calculations\n  ↓\nDomain-specific model or rule-based assessment\n  ↓\nDiagnostics / XAI / Uncertainty / Recommendation",
        language="text",
    )


def render_raw_materials() -> None:
    st.title("Raw Materials")
    st.markdown(f"{_badge('AVAILABLE')} {_badge('REFERENCE')} {_badge('MEASURED')} ")
    materials = load_material_library()
    search = st.text_input("Search material or type")
    material_type = st.selectbox("Material type", ["All"] + sorted(materials["Material_Type"].unique().tolist()))

    if material_type != "All":
        materials = materials[materials["Material_Type"] == material_type]
    if search:
        search_value = search.lower()
        materials = materials[
            materials["Sample_ID"].astype(str).str.lower().str.contains(search_value)
            | materials["Material_Type"].astype(str).str.lower().str.contains(search_value)
        ]

    st.caption("Data source: `data/raw_materials/raw_materials_database.csv`.")
    if materials.empty:
        st.info("No raw materials match the active filter.")
        return

    st.dataframe(materials, use_container_width=True, hide_index=True)

    if not materials.empty:
        oxide_cols = ["CaO", "SiO2", "Al2O3", "Fe2O3", "MgO", "SO3", "LOI"]
        summary = materials[oxide_cols].mean().round(2)
        st.subheader("Averaged chemistry summary")
        st.dataframe(summary.to_frame(name="Mean wt%"), use_container_width=True)


def render_raw_mix_engineer() -> None:
    st.title("Raw Mix Engineer")
    st.markdown(f"{_badge('CALCULATED')} {_badge('AVAILABLE')} {_badge('REFERENCE')}")
    materials = load_material_library()

    if "raw_mix_recipe" not in st.session_state:
        st.session_state.raw_mix_recipe = {
            "LS_001": 78.0,
            "CLAY_001": 14.0,
            "SAND_001": 5.0,
            "IRON_001": 3.0,
        }

    recipe = {}
    for material_id, label in {
        "LS_001": "Limestone (%)",
        "CLAY_001": "Clay (%)",
        "SAND_001": "Sand (%)",
        "IRON_001": "Iron Corrective (%)",
    }.items():
        recipe[material_id] = st.number_input(
            label,
            min_value=0.0,
            max_value=100.0,
            value=float(st.session_state.raw_mix_recipe.get(material_id, 0.0)),
            key=f"recipe_{material_id}",
        )
    st.session_state.raw_mix_recipe = recipe

    total = sum(recipe.values())
    c1, c2 = st.columns([2, 1])
    with c1:
        st.caption(f"Recipe total: {total:.2f}%")
    with c2:
        if abs(total - 100.0) <= 1.0:
            st.success("Recipe within acceptable tolerance")
        else:
            st.warning("Recipe is outside ±1% tolerance")

    if abs(total - 100.0) > 1.0:
        _callout("Recipe must sum to 100% within ±1%. Adjust the percentages before calculation.", kind="warning")
        return

    if st.button("Calculate raw-meal chemistry", type="primary"):
        result = compute_recipe_result(materials, recipe)
        if not result.get("valid", False):
            _callout("Recipe rejected by validation: " + "; ".join(result.get("errors", ["Unknown validation error"])), kind="error")
            return

        chemistry = result["chemistry"]
        moduli = result["moduli"]

        st.subheader("Calculated raw-meal oxides")
        oxide_df = pd.DataFrame([{"Oxide": k, "wt%": round(float(v), 3)} for k, v in chemistry.items()])
        st.dataframe(oxide_df, use_container_width=True, hide_index=True)

        st.subheader("Calculated moduli")
        c1, c2, c3 = st.columns(3)
        c1.metric("LSF", f"{moduli.get('LSF', float('nan')):.3f}")
        c2.metric("SM", f"{moduli.get('SM', float('nan')):.3f}")
        c3.metric("AM", f"{moduli.get('AM', float('nan')):.3f}")

        st.caption("Source: measured raw-material assay table; output is CALCULATED and intentionally not a clinker target.")

        validation_cols = st.columns(2)
        with validation_cols[0]:
            st.markdown(f"**Mass balance:** {_badge('VALID' if result.get('mass_balance_ok') else 'FAIL')}")
        with validation_cols[1]:
            st.markdown(f"**Source dataset:** `{RAW_MATERIALS_PATH.name}`")

        if result.get("warnings"):
            st.warning("Validation warnings: " + "; ".join(result.get("warnings", [])))


def render_chemistry_constraints() -> None:
    st.title("Chemistry / Constraints")
    st.markdown(f"{_badge('AVAILABLE')} {_badge('CALCULATED')} {_badge('VALID')}")
    materials = load_material_library()
    recipe = DEFAULT_BASELINE_RECIPE.copy()
    result = compute_recipe_result(materials, recipe)

    if not result.get("valid", False):
        _callout("Unable to calculate chemistry: " + "; ".join(result.get("errors", ["Unknown error"])), kind="error")
        return

    moduli = result["moduli"]
    checks = check_engineering_constraints(
        result,
        lsf_min=0.90,
        lsf_max=1.05,
        sm_min=2.00,
        sm_max=3.00,
        am_min=1.40,
        am_max=2.20,
    )

    st.subheader("Engineering modulus checks")
    metrics = [
        ("LSF", moduli.get("LSF"), 0.90, 1.05),
        ("SM", moduli.get("SM"), 2.00, 3.00),
        ("AM", moduli.get("AM"), 1.40, 2.20),
    ]
    for name, value, lower, upper in metrics:
        if value is None:
            status = "FAIL"
        elif lower <= float(value) <= upper:
            status = "PASS"
        else:
            status = "WARNING" if abs(float(value) - lower) < 0.1 or abs(float(value) - upper) < 0.1 else "FAIL"
        st.markdown(f"**{name}**: {value:.3f} | Range: {lower} - {upper} | Status: {_badge(status)}")

    st.subheader("Mass balance and chemistry checks")
    st.json({
        "mass_balance_ok": result.get("mass_balance_ok"),
        "mass_balance_sum": round(float(result.get("mass_balance_sum", float("nan"))), 3),
        "constraint_status": checks.get("overall_status"),
        "checks": checks.get("checks", {}),
    })


def render_scenario_analysis() -> None:
    st.title("Scenario Analysis")
    st.markdown(f"{_badge('CALCULATED')} {_badge('AVAILABLE')} {_badge('BENCHMARK')}")
    st.caption("DETERMINISTIC CHEMISTRY SCENARIO ANALYSIS — NOT AI OPTIMIZATION")
    materials = load_material_library()
    baseline_recipe = DEFAULT_BASELINE_RECIPE.copy()
    baseline = compute_recipe_result(materials, baseline_recipe)

    if not baseline.get("valid", False):
        _callout("Baseline scenario is invalid: " + "; ".join(baseline.get("errors", ["Unknown error"])), kind="error")
        return

    scenario_a = {"LS_001": 80.0, "CLAY_001": 12.0, "SAND_001": 5.0, "IRON_001": 3.0}
    scenario_b = {"LS_001": 75.0, "CLAY_001": 16.0, "SAND_001": 5.0, "IRON_001": 4.0}
    scenario_c = {"LS_001": 70.0, "CLAY_001": 18.0, "SAND_001": 7.0, "IRON_001": 5.0}

    scenario_records = {
        "Scenario A": compute_recipe_result(materials, scenario_a),
        "Scenario B": compute_recipe_result(materials, scenario_b),
        "Scenario C": compute_recipe_result(materials, scenario_c),
    }

    st.subheader("Baseline vs candidate recipes")
    comparison_rows = []
    for label, result in scenario_records.items():
        if result.get("valid"):
            comparison_rows.append({
                "Scenario": label,
                "CaO": round(float(result["chemistry"].get("CaO", 0.0)), 3),
                "SiO2": round(float(result["chemistry"].get("SiO2", 0.0)), 3),
                "Al2O3": round(float(result["chemistry"].get("Al2O3", 0.0)), 3),
                "Fe2O3": round(float(result["chemistry"].get("Fe2O3", 0.0)), 3),
                "LSF": round(float(result["moduli"].get("LSF", 0.0)), 3),
                "SM": round(float(result["moduli"].get("SM", 0.0)), 3),
                "AM": round(float(result["moduli"].get("AM", 0.0)), 3),
            })
    st.dataframe(pd.DataFrame(comparison_rows), use_container_width=True)

    sensitivity = deterministic_sensitivity_analysis(materials, baseline_recipe)
    st.subheader("Sensitivity overview")
    if sensitivity.get("valid"):
        for item in sensitivity["sensitivity_by_material"][:6]:
            result = item["result"]
            st.markdown(
                f"**{item['material_id']} / {item['direction']}** — "
                f"LSF {result['moduli'].get('LSF', float('nan')):.3f}, "
                f"SM {result['moduli'].get('SM', float('nan')):.3f}, "
                f"AM {result['moduli'].get('AM', float('nan')):.3f}"
            )


def render_ai_copilot() -> None:
    st.title("AI Cement Engineer Copilot")
    st.markdown(f"{_badge('AVAILABLE')} {_badge('REFERENCE')} {_badge('CALCULATED')}")
    st.caption("Use the project calculations and provenance to reason about chemistry and process constraints.")

    question = st.text_input("Ask an engineering question", value="What data do I need for clinker ML?")
    if question:
        response = answer_engineering_question(question, {"prediction": {"prediction": 1.2, "lsf": 0.96}})
        st.markdown(response)

    st.subheader("Accepted question examples")
    for example in [
        "Why is my LSF low?",
        "What happens if I increase limestone?",
        "Why is SM outside the target range?",
        "Compare these two raw-mix scenarios.",
        "Explain the chemistry calculation.",
        "What data do I need for clinker ML?",
    ]:
        st.write("- " + example)


def render_data_provenance() -> None:
    st.title("Data & Provenance")
    st.markdown(f"{_badge('REFERENCE')} {_badge('SYNTHETIC')} {_badge('BLOCKED')}")
    st.dataframe(get_data_provenance_table(), use_container_width=True, hide_index=True)

    st.subheader("Provenance guidance")
    st.markdown(
        "- Measured raw-material assays are valid for raw-mix chemistry and engineering checks.\n"
        "- Calculated raw-meal chemistry is a derived output and must be labeled as CALCULATED.\n"
        "- Synthetic clinker targets are not valid for real clinker ML and must not be used as measured outcomes.\n"
        "- Concrete benchmark data are separate from clinker prediction and remain labeled as CONCRETE BENCHMARK.\n"
        "- Real clinker ML remains blocked until a measured and traceable dataset is accepted."
    )


def render_model_center() -> None:
    st.title("Model Center")
    st.markdown(f"{_badge('AVAILABLE')} {_badge('BENCHMARK')} {_badge('BLOCKED')}")
    st.subheader("A. AVAILABLE MODELS")
    st.markdown("**Concrete strength benchmark**")
    st.markdown("**CATEGORY:** DOWNSTREAM CONCRETE BENCHMARK")
    model_files = [p.name for p in MODEL_DIR.iterdir() if p.is_file()] if MODEL_DIR.exists() else []
    if model_files:
        st.write("Available model artifacts: " + ", ".join(model_files))
    else:
        st.info("No model artifacts were found in `models/` for the current repository copy.")

    st.markdown("---")
    st.subheader("B. FUTURE / BLOCKED MODELS")
    for item in get_blocked_models():
        st.error(f"{item['model']}: BLOCKED — {item['reason']}")

    st.warning("Synthetic phase values are not presented as real clinker predictions. Bogue-style phase outputs are not treated as measured clinker targets.")


def render_research_status() -> None:
    st.title("Research Status")
    st.markdown(f"{_badge('BLOCKED')} {_badge('REQUIRED')} {_badge('AVAILABLE')}")
    st.dataframe(get_research_status_table(), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.warning(
        "The current repository supports chemistry-aware raw-material and raw-mix engineering. Supervised clinker ML is intentionally disabled until traceable measured clinker data become available."
    )

    st.subheader("Required future data")
    for item in [
        "measured clinker target",
        "measurement method",
        "sample IDs",
        "timestamps",
        "raw-material linkage",
        "process linkage",
        "temporal alignment",
        "provenance",
    ]:
        st.write("- " + item)


def _module_card(module_name: str) -> None:
    st.markdown(
        f"""
        <div style="padding: 0.8rem 0.9rem; border: 1px solid #e5e7eb; border-radius: 0.8rem; background: #f9fafb; min-height: 86px; margin-bottom: 0.45rem;">
            <div style="font-size: 0.68rem; color: #6b7280; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase;">MODULE</div>
            <div style="font-size: 1rem; font-weight: 800; color: #111827; margin-top: 0.35rem;">{module_name}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="AI Cement Engineer", page_icon="🏭", layout="wide")

    st.sidebar.title("AI Cement Engineer")
    st.sidebar.caption("Hybrid engineering + AI decision support system")
    pages = {
        "AI Command Center": render_overview,
        "Raw Materials": render_raw_materials,
        "Raw Mix / Raw Meal": render_raw_mix_engineer,
        "Kiln / Process": render_chemistry_constraints,
        "Clinker": lambda: render_placeholder_module("Clinker", "Measured clinker phase and free-CaO model work should only be enabled after validated plant data exist."),
        "Cement Blending": lambda: render_placeholder_module("Cement Blending", "This stage combines clinker, gypsum, SCMs, and grinding variables to estimate cement quality."),
        "Cement Quality": lambda: render_placeholder_module("Cement Quality", "This stage predicts fineness, setting, soundness, and strength from measured cement properties and process variables."),
        "Concrete Mix": lambda: render_placeholder_module("Concrete Mix", "Concrete design inputs include cement, SCM, w/b, aggregates, admixtures, and curing conditions."),
        "Multi-Age Strength": lambda: render_placeholder_module("Multi-Age Strength", "Use a multi-age model across 3/7/14/21/28/56/90 day outputs and check physical consistency."),
        "Failure Detection": lambda: render_placeholder_module("Failure Detection", "Flag underperformance and investigate across raw materials, clinker, fineness, SCM, curing, and mix variables."),
        "Likely Contributing Factors": lambda: render_placeholder_module("Likely Contributing Factors", "Rank likely contributors using SHAP, historical evidence, process knowledge, and engineering checks."),
        "Historical Memory": lambda: render_placeholder_module("Historical Memory", "Search exact and similar past cases to compare process conditions, measured strengths, failures, and prior recommendations."),
        "XAI / SHAP": lambda: render_placeholder_module("XAI / SHAP", "Explain prediction drivers, but use careful wording: likely contributing factors rather than confirmed root causes."),
        "Uncertainty / OOD": lambda: render_placeholder_module("Uncertainty / OOD", "Flag out-of-distribution behaviour and prediction risk using calibrated uncertainty methods before recommending action."),
        "What-If / Optimization": lambda: render_placeholder_module("What-If / Optimization", "Compare scenario changes in gypsum, SCM, w/b, and raw meal to understand likely quality outcomes under constraints."),
        "Actual vs Predicted": lambda: render_placeholder_module("Actual vs Predicted", "Compare measured lab results with predicted performance to quantify error and support monitoring and retraining."),
        "Model Center / Retraining": render_model_center,
    }

    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "AI Command Center"
    selected = st.sidebar.radio("Navigation", list(pages.keys()), index=list(pages.keys()).index(st.session_state.selected_page))
    st.session_state.selected_page = selected
    pages[selected]()


if __name__ == "__main__":
    main()
