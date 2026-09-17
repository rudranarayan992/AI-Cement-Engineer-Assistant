"""Traceability and explainability engine for cement production.

This module enables backward causality analysis: tracing why a cement has
certain strength properties based on its complete production history.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from src.data_lineage import (
    RawMaterial,
    RawMix,
    KilnRun,
    Clinker,
    CementBatch,
    StrengthTest,
    LineageTrace,
)


class InfluenceFactor(Enum):
    """Factors that influence cement strength."""
    RAW_MIX_LSF = "raw_mix_lsf"           # Lime Saturation Factor
    RAW_MIX_SM = "raw_mix_sm"             # Silica Modulus
    RAW_MIX_COMPOSITION = "raw_mix_composition"
    CLINKER_C3S = "clinker_c3s"           # Alite content (drives early/late strength)
    CLINKER_FREE_CAO = "clinker_free_cao" # Free lime (affects durability)
    KILN_TEMPERATURE = "kiln_temperature"
    CEMENT_FINENESS = "cement_fineness"
    CEMENT_TYPE = "cement_type"
    CONCRETE_W_C_RATIO = "concrete_w_c_ratio"
    CURING_CONDITIONS = "curing_conditions"


@dataclass
class CausalFactor:
    """Represents a single causal factor in the production chain."""
    
    factor: InfluenceFactor
    stage: str  # "raw_materials", "raw_mix", "kiln", "clinker", "cement", "concrete"
    value: float
    unit: str
    acceptable_range: Tuple[float, float]
    impact_on_strength: str  # "positive", "negative", "neutral"
    
    def is_within_specification(self) -> bool:
        """Check if factor is within acceptable range."""
        return self.acceptable_range[0] <= self.value <= self.acceptable_range[1]
    
    def get_impact_description(self) -> str:
        """Describe how this factor impacts strength."""
        status = "✓ Normal" if self.is_within_specification() else "✗ Out of spec"
        direction = "↑ increases" if self.impact_on_strength == "positive" else "↓ decreases"
        return f"{self.factor.value}: {self.value} {self.unit} ({status}) - {direction} strength"


class StrengthExplainer:
    """Explains cement/concrete strength based on production lineage."""
    
    # Typical strength contribution percentages
    STRENGTH_FACTOR_WEIGHTS = {
        InfluenceFactor.CLINKER_C3S: 0.30,           # Alite is ~30% of strength driver
        InfluenceFactor.CEMENT_FINENESS: 0.20,       # Fineness ~20%
        InfluenceFactor.CONCRETE_W_C_RATIO: 0.25,    # W/C ratio ~25%
        InfluenceFactor.CLINKER_FREE_CAO: -0.10,     # Free lime negative ~10%
        InfluenceFactor.CURING_CONDITIONS: 0.15,     # Curing ~15%
    }
    
    # Typical specification ranges
    SPECIFICATION_RANGES = {
        InfluenceFactor.RAW_MIX_LSF: (0.95, 1.05),              # LSF for OPC
        InfluenceFactor.RAW_MIX_SM: (2.3, 3.0),                 # Silica Modulus
        InfluenceFactor.CLINKER_C3S: (50, 70),                  # 50-70% alite typical
        InfluenceFactor.CLINKER_FREE_CAO: (0, 2.5),             # <2.5% free CaO
        InfluenceFactor.KILN_TEMPERATURE: (1450, 1500),         # °C
        InfluenceFactor.CEMENT_FINENESS: (2500, 4000),          # cm²/g
        InfluenceFactor.CONCRETE_W_C_RATIO: (0.35, 0.65),       # w/c ratio
    }
    
    def __init__(self, trace: LineageTrace):
        """Initialize explainer with a complete lineage trace."""
        self.trace = trace
        self.causal_factors: List[CausalFactor] = []
        self._extract_factors()
    
    def _extract_factors(self):
        """Extract causal factors from the lineage trace."""
        
        # From raw mix
        if self.trace.raw_mix:
            if self.trace.raw_mix.lsf is not None:
                self.causal_factors.append(
                    CausalFactor(
                        factor=InfluenceFactor.RAW_MIX_LSF,
                        stage="raw_mix",
                        value=self.trace.raw_mix.lsf,
                        unit="",
                        acceptable_range=self.SPECIFICATION_RANGES[InfluenceFactor.RAW_MIX_LSF],
                        impact_on_strength="positive",
                    )
                )
            
            if self.trace.raw_mix.sm is not None:
                self.causal_factors.append(
                    CausalFactor(
                        factor=InfluenceFactor.RAW_MIX_SM,
                        stage="raw_mix",
                        value=self.trace.raw_mix.sm,
                        unit="",
                        acceptable_range=self.SPECIFICATION_RANGES[InfluenceFactor.RAW_MIX_SM],
                        impact_on_strength="positive",
                    )
                )
        
        # From kiln run
        if self.trace.kiln_run:
            if self.trace.kiln_run.maximum_temperature_celsius > 0:
                self.causal_factors.append(
                    CausalFactor(
                        factor=InfluenceFactor.KILN_TEMPERATURE,
                        stage="kiln",
                        value=self.trace.kiln_run.maximum_temperature_celsius,
                        unit="°C",
                        acceptable_range=self.SPECIFICATION_RANGES[InfluenceFactor.KILN_TEMPERATURE],
                        impact_on_strength="positive",
                    )
                )
        
        # From clinker
        if self.trace.clinker:
            if self.trace.clinker.c3s_percent is not None:
                self.causal_factors.append(
                    CausalFactor(
                        factor=InfluenceFactor.CLINKER_C3S,
                        stage="clinker",
                        value=self.trace.clinker.c3s_percent,
                        unit="%",
                        acceptable_range=self.SPECIFICATION_RANGES[InfluenceFactor.CLINKER_C3S],
                        impact_on_strength="positive",
                    )
                )
            
            if self.trace.clinker.free_cao_percent > 0:
                self.causal_factors.append(
                    CausalFactor(
                        factor=InfluenceFactor.CLINKER_FREE_CAO,
                        stage="clinker",
                        value=self.trace.clinker.free_cao_percent,
                        unit="%",
                        acceptable_range=self.SPECIFICATION_RANGES[InfluenceFactor.CLINKER_FREE_CAO],
                        impact_on_strength="negative",
                    )
                )
        
        # From cement batch
        if self.trace.cement_batch:
            if self.trace.cement_batch.fineness_cm2_g is not None:
                self.causal_factors.append(
                    CausalFactor(
                        factor=InfluenceFactor.CEMENT_FINENESS,
                        stage="cement",
                        value=self.trace.cement_batch.fineness_cm2_g,
                        unit="cm²/g",
                        acceptable_range=self.SPECIFICATION_RANGES[InfluenceFactor.CEMENT_FINENESS],
                        impact_on_strength="positive",
                    )
                )
        
        # From strength tests
        for test in self.trace.strength_tests:
            if test.w_c_ratio > 0:
                self.causal_factors.append(
                    CausalFactor(
                        factor=InfluenceFactor.CONCRETE_W_C_RATIO,
                        stage="concrete",
                        value=test.w_c_ratio,
                        unit="",
                        acceptable_range=self.SPECIFICATION_RANGES[InfluenceFactor.CONCRETE_W_C_RATIO],
                        impact_on_strength="negative",
                    )
                )
    
    def explain_strength_result(self, observed_strength_mpa: float) -> str:
        """Generate a natural language explanation for strength results."""
        
        explanation = "=" * 70 + "\n"
        explanation += "CEMENT STRENGTH CAUSALITY ANALYSIS\n"
        explanation += "=" * 70 + "\n\n"
        
        explanation += f"Observed 28-day Strength: {observed_strength_mpa:.1f} MPa\n\n"
        
        # Contributing factors
        explanation += "Contributing Factors:\n"
        explanation += "-" * 70 + "\n"
        
        positive_factors = [f for f in self.causal_factors if f.impact_on_strength == "positive"]
        negative_factors = [f for f in self.causal_factors if f.impact_on_strength == "negative"]
        
        if positive_factors:
            explanation += "\n✓ POSITIVE FACTORS (increase strength):\n"
            for factor in positive_factors:
                explanation += f"  • {factor.get_impact_description()}\n"
        
        if negative_factors:
            explanation += "\n✗ NEGATIVE FACTORS (decrease strength):\n"
            for factor in negative_factors:
                explanation += f"  • {factor.get_impact_description()}\n"
        
        # Causal chain narrative
        explanation += "\n" + "=" * 70 + "\n"
        explanation += "CAUSAL CHAIN NARRATIVE\n"
        explanation += "=" * 70 + "\n\n"
        explanation += self._build_causal_narrative()
        
        return explanation
    
    def _build_causal_narrative(self) -> str:
        """Build a narrative explaining the causal chain."""
        narrative = ""
        
        # Stage 1: Raw materials → Raw mix quality
        if self.trace.raw_materials and self.trace.raw_mix:
            narrative += "1. RAW MATERIAL SELECTION\n"
            narrative += "-" * 40 + "\n"
            
            # Describe raw materials
            for material in self.trace.raw_materials:
                narrative += f"   • {material.name} ({material.material_type})\n"
                narrative += f"     CaO: {material.cao_percent:.1f}%, SiO2: {material.sio2_percent:.1f}%\n"
            
            # Raw mix composition
            lsf_factor = next((f for f in self.causal_factors if f.factor == InfluenceFactor.RAW_MIX_LSF), None)
            if lsf_factor:
                lsf_status = "✓ Good" if lsf_factor.is_within_specification() else "⚠ Out of spec"
                narrative += f"\n   → Raw mix LSF: {lsf_factor.value:.2f} ({lsf_status})\n"
                narrative += f"     Effect: Controls phase composition and burnability\n"
            
            narrative += "\n"
        
        # Stage 2: Kiln performance → Clinker quality
        if self.trace.kiln_run and self.trace.clinker:
            narrative += "2. KILN PERFORMANCE & CLINKERIZATION\n"
            narrative += "-" * 40 + "\n"
            
            temp_factor = next((f for f in self.causal_factors if f.factor == InfluenceFactor.KILN_TEMPERATURE), None)
            if temp_factor:
                narrative += f"   • Maximum temperature: {temp_factor.value:.0f}°C\n"
                if temp_factor.is_within_specification():
                    narrative += f"     ✓ Within spec - optimal phase formation\n"
                else:
                    narrative += f"     ⚠ Out of spec - may affect phase composition\n"
            
            c3s_factor = next((f for f in self.causal_factors if f.factor == InfluenceFactor.CLINKER_C3S), None)
            if c3s_factor:
                narrative += f"\n   • Clinker alite (C3S) content: {c3s_factor.value:.1f}%\n"
                if c3s_factor.value >= 60:
                    narrative += f"     ✓ High alite - STRONG early strength expected\n"
                elif c3s_factor.value >= 50:
                    narrative += f"     ✓ Normal alite - balanced strength\n"
                else:
                    narrative += f"     ⚠ Low alite - reduced early strength\n"
            
            free_cao = next((f for f in self.causal_factors if f.factor == InfluenceFactor.CLINKER_FREE_CAO), None)
            if free_cao and free_cao.value > 2.0:
                narrative += f"\n   • Free CaO: {free_cao.value:.2f}%\n"
                narrative += f"     ⚠ Elevated - may affect durability and volume stability\n"
            
            narrative += "\n"
        
        # Stage 3: Cement milling
        if self.trace.cement_batch:
            narrative += "3. CEMENT GRINDING & COMPOSITION\n"
            narrative += "-" * 40 + "\n"
            
            fineness = next((f for f in self.causal_factors if f.factor == InfluenceFactor.CEMENT_FINENESS), None)
            if fineness:
                narrative += f"   • Cement fineness: {fineness.value:.0f} cm²/g\n"
                if fineness.value >= 3500:
                    narrative += f"     ✓ High fineness - INCREASED hydration rate\n"
                elif fineness.value >= 2800:
                    narrative += f"     ✓ Standard fineness\n"
                else:
                    narrative += f"     ⚠ Low fineness - reduced early strength\n"
            
            narrative += f"   • Cement type: {self.trace.cement_batch.cement_type}\n"
            narrative += "\n"
        
        # Stage 4: Concrete and curing
        if self.trace.strength_tests:
            narrative += "4. CONCRETE PROPERTIES & CURING\n"
            narrative += "-" * 40 + "\n"
            
            test = self.trace.strength_tests[0]
            w_c_factor = next((f for f in self.causal_factors if f.factor == InfluenceFactor.CONCRETE_W_C_RATIO), None)
            if w_c_factor:
                narrative += f"   • Water-cement ratio: {w_c_factor.value:.2f}\n"
                if w_c_factor.value <= 0.45:
                    narrative += f"     ✓ Low W/C - HIGH strength expected\n"
                elif w_c_factor.value <= 0.55:
                    narrative += f"     ✓ Moderate W/C - good strength\n"
                else:
                    narrative += f"     ⚠ High W/C - reduced strength\n"
            
            if test.curing_type:
                narrative += f"   • Curing type: {test.curing_type}\n"
            
            narrative += "\n"
        
        # Stage 5: Final prediction
        narrative += "5. RESULTING STRENGTH\n"
        narrative += "-" * 40 + "\n"
        narrative += "   The combination of:\n"
        narrative += "   • Alite content (from raw mix & kiln temperature)\n"
        narrative += "   • Cement fineness (from grinding)\n"
        narrative += "   • Water-cement ratio (from concrete design)\n"
        narrative += "   • Curing conditions\n"
        narrative += "   → Determines final 28-day compressive strength\n"
        
        return narrative
    
    def get_factor_importance_ranking(self) -> List[Tuple[InfluenceFactor, float, str]]:
        """Rank factors by their estimated importance on strength."""
        ranking = []
        
        for factor, weight in self.STRENGTH_FACTOR_WEIGHTS.items():
            causal = next((f for f in self.causal_factors if f.factor == factor), None)
            if causal:
                # Adjust weight based on deviation from spec
                deviation = 0.0
                if not causal.is_within_specification():
                    deviation = abs(causal.value - causal.acceptable_range[0]) / causal.acceptable_range[0]
                
                # Higher weight if out of spec
                adjusted_weight = weight * (1.0 + deviation)
                ranking.append((factor, adjusted_weight, causal.get_impact_description()))
        
        # Sort by importance
        ranking.sort(key=lambda x: x[1], reverse=True)
        return ranking
    
    def predict_strength_impact(self, factor_change: Dict[InfluenceFactor, float]) -> float:
        """Estimate strength change if factors change."""
        # Simple linear model: strength = sum(weight * factor_normalized)
        baseline_strength = 30.0  # MPa baseline
        
        strength_contribution = baseline_strength
        
        for factor, change_amount in factor_change.items():
            weight = self.STRENGTH_FACTOR_WEIGHTS.get(factor, 0.0)
            strength_contribution += weight * change_amount
        
        return strength_contribution
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations to improve strength based on identified issues."""
        recommendations = []
        
        for factor in self.causal_factors:
            if not factor.is_within_specification():
                if factor.factor == InfluenceFactor.RAW_MIX_LSF:
                    if factor.value < factor.acceptable_range[0]:
                        recommendations.append(
                            f"LSF is too low ({factor.value:.2f}): Increase limestone content or decrease silica"
                        )
                    else:
                        recommendations.append(
                            f"LSF is too high ({factor.value:.2f}): Decrease limestone content or increase silica"
                        )
                
                elif factor.factor == InfluenceFactor.KILN_TEMPERATURE:
                    recommendations.append(
                        f"Kiln temperature ({factor.value:.0f}°C) is outside ideal range: "
                        f"Adjust fuel rate or kiln speed"
                    )
                
                elif factor.factor == InfluenceFactor.CLINKER_FREE_CAO:
                    if factor.value > 2.5:
                        recommendations.append(
                            f"Free CaO is too high ({factor.value:.2f}%): "
                            f"Improve raw mix burnability or increase kiln temperature"
                        )
                
                elif factor.factor == InfluenceFactor.CEMENT_FINENESS:
                    if factor.value < factor.acceptable_range[0]:
                        recommendations.append(
                            f"Cement is too coarse ({factor.value:.0f} cm²/g): "
                            f"Increase grinding time"
                        )
                    else:
                        recommendations.append(
                            f"Cement is too fine ({factor.value:.0f} cm²/g): "
                            f"May increase water demand - consider optimization"
                        )
                
                elif factor.factor == InfluenceFactor.CONCRETE_W_C_RATIO:
                    if factor.value > factor.acceptable_range[1]:
                        recommendations.append(
                            f"W/C ratio is too high ({factor.value:.2f}): "
                            f"Reduce water or increase cement content"
                        )
        
        return recommendations


def compare_cement_batches(trace1: LineageTrace, trace2: LineageTrace) -> str:
    """Compare two cement batches and explain differences in strength."""
    
    explainer1 = StrengthExplainer(trace1)
    explainer2 = StrengthExplainer(trace2)
    
    comparison = "=" * 70 + "\n"
    comparison += "CEMENT BATCH COMPARISON\n"
    comparison += "=" * 70 + "\n\n"
    
    # Compare key factors
    comparison += "Batch 1 Key Factors:\n"
    for factor in explainer1.causal_factors[:5]:
        comparison += f"  • {factor.factor.value}: {factor.value} {factor.unit}\n"
    
    comparison += "\nBatch 2 Key Factors:\n"
    for factor in explainer2.causal_factors[:5]:
        comparison += f"  • {factor.factor.value}: {factor.value} {factor.unit}\n"
    
    # Compare rankings
    ranking1 = explainer1.get_factor_importance_ranking()
    ranking2 = explainer2.get_factor_importance_ranking()
    
    comparison += "\n" + "-" * 70 + "\n"
    comparison += "Most Important Factors:\n"
    comparison += f"Batch 1: {ranking1[0][0].value if ranking1 else 'N/A'}\n"
    comparison += f"Batch 2: {ranking2[0][0].value if ranking2 else 'N/A'}\n"
    
    return comparison
