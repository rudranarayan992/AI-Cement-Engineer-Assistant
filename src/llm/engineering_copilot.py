"""Engineering Copilot for cement plant quality control, process troubleshooting, and ASTM/EN standards advisory."""

from __future__ import annotations

from typing import Any, Dict, List

from src.chemistry.chemistry_engine import calculate_lsf, calculate_sm, calculate_am
from src.future_ml.cement_ml_architecture import (
    LLMToolRequest,
    LLMToolResponse,
    validate_phase_prediction,
)

class EngineeringCopilot:
    """Domain-expert copilot providing engineering explanations, standards advice, and root-cause analysis."""

    def __init__(self, model_name: str = "AI Cement Expert Copilot v2.0"):
        self.model_name = model_name

    def calculate_raw_mix(self, raw_materials: Dict[str, Dict[str, float]], proportions: Dict[str, float], basis: str = "as_received") -> Dict[str, Any]:
        """Route raw-mix calculations to the established deterministic chemistry engine."""
        from src.chemistry.chemistry_engine import calculate_raw_mix_chemistry
        return calculate_raw_mix_chemistry(raw_materials, proportions, basis=basis)

    def calculate_lsf(self, cao: float, sio2: float, al2o3: float, fe2o3: float) -> float:
        return calculate_lsf(float(cao), float(sio2), float(al2o3), float(fe2o3), basis="ignited")

    def calculate_sm(self, sio2: float, al2o3: float, fe2o3: float) -> float:
        return calculate_sm(float(sio2), float(al2o3), float(fe2o3), basis="ignited")

    def calculate_am(self, al2o3: float, fe2o3: float) -> float:
        return calculate_am(float(al2o3), float(fe2o3), basis="ignited")

    def validate_physics(self, phases: Dict[str, float]) -> Dict[str, Any]:
        return validate_phase_prediction(phases).__dict__

    def check_ood(self, sample: Dict[str, float], reference: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder interface: OOD checks require a real fitted reference distribution."""
        return {
            "status": "requires_fitted_reference",
            "sample": sample,
            "reference": reference,
            "warning": "OOD detection must be calibrated on real industrial data before deployment.",
        }

    def route_tool(self, request: LLMToolRequest) -> LLMToolResponse:
        """Execute a deterministic tool request using the validated engineering stack."""
        tool_name = request.tool_name
        args = request.arguments

        if tool_name == "calculate_raw_mix":
            result = self.calculate_raw_mix(args.get("raw_materials", {}), args.get("proportions", {}), args.get("basis", "as_received"))
        elif tool_name == "calculate_LSF":
            result = {"LSF": self.calculate_lsf(args["cao"], args["sio2"], args["al2o3"], args["fe2o3"])}
        elif tool_name == "calculate_SM":
            result = {"SM": self.calculate_sm(args["sio2"], args["al2o3"], args["fe2o3"])}
        elif tool_name == "calculate_AM":
            result = {"AM": self.calculate_am(args["al2o3"], args["fe2o3"])}
        elif tool_name == "validate_physics":
            result = self.validate_physics(args.get("phases", {}))
        else:
            result = {"status": "unsupported_tool", "tool_name": tool_name}

        warnings: List[str] = []
        if result.get("status") == "requires_fitted_reference":
            warnings.append("OOD detection requires calibrated future industrial training data.")
        return LLMToolResponse(tool_name=tool_name, result=result, warnings=warnings)

    def answer_question(self, question: str, context: Dict[str, Any] | None = None) -> str:
        """Answer engineering questions using plant prediction context and standards rules."""
        q_lower = question.lower().strip()

        if context is None:
            context = {}

        free_cao = context.get("prediction", {}).get("prediction", 1.2) if isinstance(context.get("prediction"), dict) else 1.2
        lsf = context.get("prediction", {}).get("lsf", 0.96) if isinstance(context.get("prediction"), dict) else 0.96

        # 1. High Free CaO / Unburnt Lime
        if "free cao" in q_lower or "unburnt lime" in q_lower or "high cao" in q_lower:
            return (
                f"### Root-Cause Analysis for Free CaO ({free_cao:.2f}%):\n"
                f"1. **Lime Saturation Factor (LSF = {lsf:.3f})**: If LSF > 0.98, the raw meal contains excess CaO relative to available SiO₂/Al₂O₃/Fe₂O₃, making complete combination in the burning zone difficult.\n"
                f"2. **Burning Zone Temperature**: Verify kiln burning zone temperature is maintained between 1400°C - 1450°C. Temperature < 1380°C drastically slows down C₃S formation.\n"
                f"3. **Raw Meal Fineness**: Check residue on 90µm sieve. Coarse quartz or calcite (> 14%) prevents solid-state diffusion during clinkerization.\n"
                f"4. **Corrective Action**: Reduce LSF by adjusting limestone proportion in raw meal, increase secondary air temperature, or improve raw meal grinding."
            )

        # 2. Compressive Strength Optimization
        if "strength" in q_lower or "compressive" in q_lower or "28 day" in q_lower or "3 day" in q_lower:
            return (
                f"### Cement Compressive Strength Advisory:\n"
                f"1. **Early Strength (3-Day & 7-Day)**: Driven primarily by Alite ($C_3S$) mineralogy (target > 56%), $C_3A$ content (6-9%), and Blaine fineness (> 3600 cm²/g).\n"
                f"2. **Late Strength (28-Day)**: Driven by Belite ($C_2S$) hydration and total Alite ($C_3S$).\n"
                f"3. **Quality Standards (ASTM C150 / EN 197-1)**:\n"
                f"   - **52.5N Grade**: Requires 28d strength $\\ge 52.5$ MPa. Keep W/C $\\le 0.44$, Blaine $\\ge 3800$ cm²/g, $C_3S \\ge 60\\%$.\n"
                f"   - **42.5N Grade**: Requires 28d strength $\\ge 42.5$ MPa. Standard Portland Cement formulation."
            )

        # 3. LSF / Moduli Explanation
        if "lsf" in q_lower or "silica modulus" in q_lower or "am" in q_lower or "moduli" in q_lower:
            return (
                f"### Clinker Chemical Ratios Guidance:\n"
                f"- **Lime Saturation Factor (LSF)**: Target 0.94 - 0.98. Higher LSF increases early strength but increases fuel consumption and Free CaO risk.\n"
                f"- **Silica Modulus (SM = $SiO_2 / (Al_2O_3 + Fe_2O_3)$)**: Target 2.2 - 2.6. Higher SM improves late strength but reduces liquid phase, making clinker hard to burn.\n"
                f"- **Alumina Modulus (AM = $Al_2O_3 / Fe_2O_3$)**: Target 1.5 - 2.0. Determines liquid viscosity at burning zone temperatures (~1450°C)."
            )

        # 4. Recipe / Optimization
        if "blend" in q_lower or "recipe" in q_lower or "cost" in q_lower or "co2" in q_lower or "optimize" in q_lower:
            return (
                f"### Raw Mix Recipe Optimization Strategy:\n"
                f"To reduce carbon footprint (CO₂ per ton clinker) and raw meal cost:\n"
                f"1. Target LSF = 0.95 to reduce limestone thermal calcination emissions ($CaCO_3 \\rightarrow CaO + CO_2$).\n"
                f"2. Use iron ore or alternative correctives to maintain AM ~ 1.7 to lower clinkering temperature.\n"
                f"3. Maximize supplementary cementitious materials (Fly Ash / Slag) downstream in cement grinding."
            )

        # Default Response
        return (
            f"### AI Cement Engineering Copilot:\n"
            f"Current batch telemetry: Predicted Free CaO = {free_cao:.2f}%, LSF = {lsf:.3f}.\n"
            f"For process troubleshooting, ask specifically about: Free CaO reduction, Compressive Strength optimization, Raw Mix recipes, or ASTM C150 / EN 197-1 quality standards."
        )

    def compare_candidates(self, candidate_a: Dict[str, Any], candidate_b: Dict[str, Any]) -> str:
        """Compare two raw mix candidate recipes from an engineering standpoint."""
        cost_a = candidate_a.get("cost_per_ton", 0.0)
        cost_b = candidate_b.get("cost_per_ton", 0.0)
        co2_a = candidate_a.get("co2_per_ton", 0.0)
        co2_b = candidate_b.get("co2_per_ton", 0.0)
        lsf_a = candidate_a.get("predicted_lsf", 0.96)
        lsf_b = candidate_b.get("predicted_lsf", 0.96)

        best_cost = "Candidate A" if cost_a < cost_b else "Candidate B"
        best_co2 = "Candidate A" if co2_a < co2_b else "Candidate B"

        return (
            f"### Recipe Candidate Comparison Analysis:\n"
            f"- **Cost Winner**: {best_cost} (${min(cost_a, cost_b):.2f}/ton vs ${max(cost_a, cost_b):.2f}/ton)\n"
            f"- **Decarbonization Winner**: {best_co2} ({min(co2_a, co2_b):.1f} kg CO₂/ton vs {max(co2_a, co2_b):.1f} kg CO₂/ton)\n"
            f"- **Chemical Ratios**: Blend A (LSF={lsf_a:.3f}) vs Blend B (LSF={lsf_b:.3f}).\n"
            f"**Recommendation**: Run full XRF and burnability test in laboratory before approving commercial kiln trial."
        )
