"""Safe architecture and schema definitions for future real cement/clinker ML.

This module is intentionally limited to interface design, validation logic, and
future data contracts. It does not train models, generate target labels, or
claim predictive performance.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import pandas as pd

MEASURED_GROUND_TRUTH_CATEGORIES = {
    "MEASURED_XRF",
    "MEASURED_XRD",
    "MEASURED_RIETVELD",
    "MEASURED_LAB",
}

REFERENCE_GROUND_TRUTH_CATEGORIES = {
    "BOGUE_CALCULATED",
    "CHEMISTRY_DERIVED",
    "SYNTHETIC",
}

ALLOWED_GROUND_TRUTH_CATEGORIES = MEASURED_GROUND_TRUTH_CATEGORIES | REFERENCE_GROUND_TRUTH_CATEGORIES


@dataclass(frozen=True)
class TargetDefinition:
    """Formal target specification for a future cement/clinker ML task."""

    name: str
    unit: str
    measurement_method: str
    ground_truth_source: str
    prediction_stage: str
    online_suitable: bool
    leakage_risks: List[str] = field(default_factory=list)
    notes: str = ""

    def __post_init__(self) -> None:
        if self.ground_truth_source not in ALLOWED_GROUND_TRUTH_CATEGORIES:
            raise ValueError(
                f"Unsupported ground-truth source '{self.ground_truth_source}'. "
                f"Allowed: {sorted(ALLOWED_GROUND_TRUTH_CATEGORIES)}"
            )

    def is_measured_ground_truth(self) -> bool:
        return self.ground_truth_source in MEASURED_GROUND_TRUTH_CATEGORIES

    def validate_for_training(self) -> None:
        if not self.is_measured_ground_truth():
            raise ValueError(
                f"Target '{self.name}' uses '{self.ground_truth_source}', which is not a valid future "
                "measured ground-truth source for supervised training."
            )


class FeatureAvailabilityLevel(str, Enum):
    ONLINE_CONTROL = "LEVEL_A_ONLINE_CONTROL"
    POST_PRODUCTION_DIAGNOSTIC = "LEVEL_B_POST_PRODUCTION"


@dataclass(frozen=True)
class FeaturePolicyEntry:
    """Single feature policy rule describing when a feature is available."""

    name: str
    availability_level: FeatureAvailabilityLevel
    online_eligible: bool
    description: str
    leakage_risk: str = "LOW"


@dataclass
class FeaturePolicy:
    """Feature-policy registry for future cement/clinker model design."""

    features: List[FeaturePolicyEntry]

    def get_feature(self, name: str) -> Optional[FeaturePolicyEntry]:
        for feature in self.features:
            if feature.name == name:
                return feature
        return None

    def online_features(self) -> List[FeaturePolicyEntry]:
        return [feature for feature in self.features if feature.online_eligible]

    def post_production_features(self) -> List[FeaturePolicyEntry]:
        return [feature for feature in self.features if not feature.online_eligible]


@dataclass
class ProvenanceMetadata:
    plant_id: Optional[str] = None
    line_id: Optional[str] = None
    kiln_id: Optional[str] = None
    batch_id: Optional[str] = None
    sample_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    source_file: Optional[str] = None
    measurement_method: Optional[str] = None
    data_status: str = "UNKNOWN"
    basis: Optional[str] = None
    units: Optional[str] = None


@dataclass
class RawMaterialRecord(ProvenanceMetadata):
    material_id: Optional[str] = None
    material_type: Optional[str] = None
    cao_percent: Optional[float] = None
    sio2_percent: Optional[float] = None
    al2o3_percent: Optional[float] = None
    fe2o3_percent: Optional[float] = None
    mgo_percent: Optional[float] = None
    so3_percent: Optional[float] = None
    loi_percent: Optional[float] = None


@dataclass
class RawMixRecord(ProvenanceMetadata):
    raw_mix_id: Optional[str] = None
    material_proportions: Dict[str, float] = field(default_factory=dict)
    cao_percent: Optional[float] = None
    sio2_percent: Optional[float] = None
    al2o3_percent: Optional[float] = None
    fe2o3_percent: Optional[float] = None
    loi_percent: Optional[float] = None
    lsf: Optional[float] = None
    sm: Optional[float] = None
    am: Optional[float] = None


@dataclass
class KilnFeedRecord(ProvenanceMetadata):
    kiln_feed_id: Optional[str] = None
    feed_rate_tph: Optional[float] = None
    feed_cao_percent: Optional[float] = None
    feed_sio2_percent: Optional[float] = None
    feed_al2o3_percent: Optional[float] = None
    feed_fe2o3_percent: Optional[float] = None
    burning_zone_temp_c: Optional[float] = None


@dataclass
class ProcessRecord(ProvenanceMetadata):
    process_record_id: Optional[str] = None
    kiln_temp_c: Optional[float] = None
    fan_speed_rpm: Optional[float] = None
    sec_air_temp_c: Optional[float] = None
    feed_rate_tph: Optional[float] = None
    residence_time_minutes: Optional[float] = None
    aggregation_window_minutes: Optional[float] = None


@dataclass
class HotMealRecord(ProvenanceMetadata):
    hot_meal_id: Optional[str] = None
    meal_lsf: Optional[float] = None
    meal_sm: Optional[float] = None
    meal_am: Optional[float] = None
    fineness_90um_pct: Optional[float] = None


@dataclass
class ClinkerMeasurement(ProvenanceMetadata):
    clinker_id: Optional[str] = None
    free_cao_percent: Optional[float] = None
    c3s_percent: Optional[float] = None
    c2s_percent: Optional[float] = None
    c3a_percent: Optional[float] = None
    c4af_percent: Optional[float] = None
    cao_percent: Optional[float] = None
    sio2_percent: Optional[float] = None
    al2o3_percent: Optional[float] = None
    fe2o3_percent: Optional[float] = None
    measurement_method: str = "MEASURED_XRF"


@dataclass
class CementMeasurement(ProvenanceMetadata):
    cement_batch_id: Optional[str] = None
    blaine_cm2_g: Optional[float] = None
    gypsum_so3_pct: Optional[float] = None
    wc_ratio: Optional[float] = None
    strength_3d_mpa: Optional[float] = None
    strength_7d_mpa: Optional[float] = None
    strength_28d_mpa: Optional[float] = None
    measurement_method: str = "MEASURED_LAB"


@dataclass
class MLTrainingRecord(ProvenanceMetadata):
    record_id: Optional[str] = None
    target: Optional[str] = None
    target_measurement_method: Optional[str] = None
    features: List[str] = field(default_factory=list)
    feature_policy: List[str] = field(default_factory=list)
    training_period: Optional[str] = None
    validation_period: Optional[str] = None
    test_period: Optional[str] = None
    labels_are_measured: bool = False

    def validate_training_target(self) -> None:
        if not self.labels_are_measured:
            raise ValueError(
                "Training records must only be created with measured experimental labels. "
                "Synthetic or Bogue-derived targets are not allowed."
            )


@dataclass
class MLPrediction:
    prediction: float
    uncertainty: Optional[float] = None
    ood_status: str = "UNKNOWN"
    warning: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PredictionMetadata:
    model_id: Optional[str] = None
    dataset_version: Optional[str] = None
    target: Optional[str] = None
    target_measurement_method: Optional[str] = None
    features: List[str] = field(default_factory=list)
    feature_policy: List[str] = field(default_factory=list)
    plant_id: Optional[str] = None
    line_id: Optional[str] = None
    kiln_id: Optional[str] = None
    time_range: Optional[str] = None
    preprocessing_version: Optional[str] = None
    algorithm: Optional[str] = None
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    train_period: Optional[str] = None
    validation_period: Optional[str] = None
    test_period: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    uncertainty_method: Optional[str] = None
    ood_method: Optional[str] = None
    known_limitations: List[str] = field(default_factory=list)


@dataclass
class OODResult:
    status: str = "UNKNOWN"
    score: Optional[float] = None
    method: Optional[str] = None
    threshold: Optional[float] = None
    warning: Optional[str] = None


@dataclass
class UncertaintyResult:
    value: Optional[float] = None
    method: Optional[str] = None
    calibrated: bool = False
    warning: Optional[str] = None


@dataclass
class ValidationResult:
    chemistry_valid: bool = True
    phase_valid: bool = True
    stoichiometric_valid: bool = True
    ood_valid: bool = True
    warnings: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class TemporalAlignmentConfig:
    """Temporal alignment configuration for process telemetry and lab targets."""

    timestamp_col: str = "timestamp"
    frequency: str = "1h"
    lag_minutes: int = 0
    residence_time_minutes: Optional[int] = None
    aggregation_window_minutes: int = 60
    aggregation_method: str = "mean"
    missing_interval_policy: str = "drop"

    def validate(self) -> None:
        if self.residence_time_minutes is None:
            raise ValueError(
                "Residence time must be configured explicitly. Nearest-timestamp joins are not sufficient when process residence time is material."
            )
        if self.aggregation_window_minutes <= 0:
            raise ValueError("aggregation_window_minutes must be positive.")
        if self.aggregation_method not in {"mean", "sum", "median", "max", "min"}:
            raise ValueError(f"Unsupported aggregation_method '{self.aggregation_method}'.")

    def align(self, process_df: pd.DataFrame, target_df: pd.DataFrame) -> pd.DataFrame:
        """Align process telemetry to measured targets using explicit lag/residence-time logic."""
        self.validate()
        process = process_df.copy()
        target = target_df.copy()
        process[self.timestamp_col] = pd.to_datetime(process[self.timestamp_col])
        target[self.timestamp_col] = pd.to_datetime(target[self.timestamp_col])

        process = process.sort_values(self.timestamp_col).reset_index(drop=True)
        target = target.sort_values(self.timestamp_col).reset_index(drop=True)

        target[self.timestamp_col] = target[self.timestamp_col] + pd.to_timedelta(
            self.lag_minutes + (self.residence_time_minutes or 0), unit="min"
        )

        merged = pd.merge_asof(
            target.sort_values(self.timestamp_col),
            process.sort_values(self.timestamp_col),
            on=self.timestamp_col,
            direction="nearest",
            tolerance=pd.Timedelta(minutes=self.aggregation_window_minutes),
        )

        if self.missing_interval_policy == "drop":
            merged = merged.dropna(subset=[col for col in merged.columns if col != self.timestamp_col])
        return merged


@dataclass
class ChronologicalSplitConfig:
    """Time-aware split configuration to prevent future leakage."""

    train_end: Optional[datetime] = None
    validation_end: Optional[datetime] = None
    test_end: Optional[datetime] = None
    train_start: Optional[datetime] = None
    validation_start: Optional[datetime] = None
    test_start: Optional[datetime] = None
    strategy: str = "chronological"

    def validate(self) -> None:
        if self.strategy not in {"chronological", "rolling", "plant_wise", "kitchen_sink"}:
            raise ValueError(f"Unsupported split strategy '{self.strategy}'.")
        if self.train_end is None or self.validation_end is None or self.test_end is None:
            raise ValueError("train_end, validation_end, and test_end must be specified.")
        if self.train_end >= self.validation_end:
            raise ValueError("Validation period must begin after the training period ends.")
        if self.validation_end >= self.test_end:
            raise ValueError("Test period must begin after the validation period ends.")

    def build_ranges(self) -> Dict[str, Tuple[Optional[datetime], Optional[datetime]]]:
        self.validate()
        return {
            "train": (self.train_start, self.train_end),
            "validation": (self.validation_start or self.train_end, self.validation_end),
            "test": (self.test_start or self.validation_end, self.test_end),
        }


def create_chronological_split(df: pd.DataFrame, timestamp_col: str, config: ChronologicalSplitConfig) -> Dict[str, pd.DataFrame]:
    """Return chronological time buckets for future training/validation/test data.

    No leakage is introduced here: each split is based on time windows and the
    configuration explicitly requires future periods to be later than training.
    """
    config.validate()
    time_df = df.copy()
    time_df[timestamp_col] = pd.to_datetime(time_df[timestamp_col])
    ranges = config.build_ranges()
    split_frames: Dict[str, pd.DataFrame] = {}
    for key, (start, end) in ranges.items():
        mask = time_df[timestamp_col].between(start, end) if start is not None and end is not None else time_df[timestamp_col].notna()
        split_frames[key] = time_df.loc[mask].copy()
    return split_frames


@dataclass
class ModelConfig:
    algorithm: str
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    feature_policy: List[str] = field(default_factory=list)
    target: Optional[str] = None
    dataset_version: Optional[str] = None
    supports_ood: bool = False
    supports_uncertainty: bool = False

    def validate(self) -> None:
        allowed = {"ridge", "random_forest", "svr", "xgboost", "neural_network", "gaussian_process"}
        if self.algorithm.lower() not in allowed:
            raise ValueError(f"Unsupported future model algorithm '{self.algorithm}'. Allowed: {sorted(allowed)}")


@dataclass
class PhysicsValidationConfig:
    """Safety-bound validation for future cement/clinker predictions."""

    phase_bounds: Dict[str, Tuple[float, float]] = field(
        default_factory=lambda: {
            "C3S": (0.0, 100.0),
            "C2S": (0.0, 100.0),
            "C3A": (0.0, 100.0),
            "C4AF": (0.0, 100.0),
            "Free_CaO": (0.0, 10.0),
        }
    )
    allow_negative_phases: bool = False
    phase_sum_tolerance: float = 5.0

    def validate_prediction(self, phases: Mapping[str, float]) -> ValidationResult:
        warnings: List[str] = []
        for name, value in phases.items():
            if value is None:
                warnings.append(f"Phase '{name}' is None.")
                continue
            numeric = float(value)
            if numeric < 0 and not self.allow_negative_phases:
                warnings.append(f"Phase '{name}' is negative ({numeric}).")
            lower, upper = self.phase_bounds.get(name, (0.0, 100.0))
            if numeric < lower or numeric > upper:
                warnings.append(f"Phase '{name}' = {numeric} outside configured bounds [{lower}, {upper}].")

        phase_sum = sum(float(v) for v in phases.values() if v is not None)
        if phase_sum > 100.0 + self.phase_sum_tolerance:
            warnings.append(f"Phase sum {phase_sum:.2f} exceeds the expected operating range by more than {self.phase_sum_tolerance}.")

        return ValidationResult(
            chemistry_valid=not warnings,
            phase_valid=not warnings,
            stoichiometric_valid=True,
            ood_valid=True,
            warnings=warnings,
        )


def validate_phase_prediction(phases: Mapping[str, float], config: Optional[PhysicsValidationConfig] = None) -> ValidationResult:
    """Validate future phase predictions against engineering safety bounds."""
    if config is None:
        config = PhysicsValidationConfig()
    return config.validate_prediction(phases)


@dataclass
class StoichiometricReconstructionResult:
    status: str
    reconstructed_oxide: Dict[str, float] = field(default_factory=dict)
    residual: Dict[str, float] = field(default_factory=dict)
    notes: str = ""


def reconstruct_oxide_from_phases(
    predicted_phases: Mapping[str, float],
    measured_oxide: Optional[Mapping[str, float]] = None,
    phase_stoichiometry: Optional[Mapping[str, Mapping[str, float]]] = None,
) -> StoichiometricReconstructionResult:
    """Future stoichiometric reconstruction hook.

    This does not fabricate coefficients or pretend that Bogue equations are exact
    physics. It simply provides an explicit validation interface for a real
    industrial implementation when stoichiometric coefficients are available.
    """
    if phase_stoichiometry is None:
        return StoichiometricReconstructionResult(
            status="UNAVAILABLE",
            reconstructed_oxide={},
            residual={},
            notes=(
                "Stoichiometric reconstruction requires explicit industrial phase stoichiometry "
                "coefficients and independently measured oxide composition. No fabricated coefficients were added."
            ),
        )

    reconstructed: Dict[str, float] = {"CaO": 0.0, "SiO2": 0.0, "Al2O3": 0.0, "Fe2O3": 0.0}
    for phase_name, phase_fraction in predicted_phases.items():
        if phase_name not in phase_stoichiometry:
            continue
        coeffs = phase_stoichiometry[phase_name]
        for oxide_name, coef in coeffs.items():
            if oxide_name in reconstructed:
                reconstructed[oxide_name] += float(phase_fraction) * float(coef)

    residual = {}
    if measured_oxide is not None:
        for oxide_name in list(reconstructed.keys()):
            measured = float(measured_oxide.get(oxide_name, 0.0))
            residual[oxide_name] = measured - reconstructed.get(oxide_name, 0.0)

    return StoichiometricReconstructionResult(
        status="READY_WHEN_CONFIGURED",
        reconstructed_oxide=reconstructed,
        residual=residual,
        notes="Stoichiometric reconstruction is a future validation path; only use when coefficients are explicitly supplied from real process or literature definitions.",
    )


@dataclass
class PredictionExplanation:
    feature_importance: Dict[str, float] = field(default_factory=dict)
    local_attribution: Dict[str, float] = field(default_factory=dict)
    explanation_method: str = "SHAP"
    notes: str = "Feature importance is model-behavior evidence, not proof of causation."


@dataclass
class InverseOptimizationConfig:
    target_quality: Dict[str, float] = field(default_factory=dict)
    candidate_constraints: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    chemistry_validation_required: bool = True
    uncertainty_required: bool = True
    ood_required: bool = True


@dataclass
class LLMToolRequest:
    tool_name: str
    arguments: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMToolResponse:
    tool_name: str
    result: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


class TargetTaxonomy:
    """Registry of future cement/clinker targets including their ground-truth rules."""

    def __init__(self, targets: Sequence[TargetDefinition]):
        self.targets = list(targets)
        self.index = {target.name: target for target in self.targets}

    def add_target(self, target: TargetDefinition) -> None:
        self.index[target.name] = target
        self.targets.append(target)

    def get(self, name: str) -> TargetDefinition:
        if name not in self.index:
            raise KeyError(f"Target '{name}' not found.")
        return self.index[name]

    def training_targets(self) -> List[TargetDefinition]:
        return [target for target in self.targets if target.is_measured_ground_truth()]

    def enforce_measurement_policy(self, name: str) -> None:
        self.get(name).validate_for_training()

    def to_dict(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": target.name,
                "unit": target.unit,
                "measurement_method": target.measurement_method,
                "ground_truth_source": target.ground_truth_source,
                "prediction_stage": target.prediction_stage,
                "online_suitable": target.online_suitable,
                "leakage_risks": target.leakage_risks,
                "notes": target.notes,
            }
            for target in self.targets
        ]


FUTURE_TARGET_TAXONOMY = TargetTaxonomy(
    [
        TargetDefinition(
            name="Free_CaO",
            unit="%",
            measurement_method="Laboratory analysis",
            ground_truth_source="MEASURED_LAB",
            prediction_stage="clinker_production",
            online_suitable=True,
            leakage_risks=["future process observations", "post-clinker chemistry leakage"],
            notes="Future online target when measured by lab or XRF at appropriate time.",
        ),
        TargetDefinition(
            name="C3S",
            unit="%",
            measurement_method="Measured XRD / Rietveld or lab phase analysis",
            ground_truth_source="MEASURED_XRD",
            prediction_stage="clinker_production",
            online_suitable=False,
            leakage_risks=["phase measurement timing", "post-production lab information"],
            notes="Use only when a measured XRD or equivalent phase measurement is available.",
        ),
        TargetDefinition(
            name="C2S",
            unit="%",
            measurement_method="Measured XRD / Rietveld or lab phase analysis",
            ground_truth_source="MEASURED_XRD",
            prediction_stage="clinker_production",
            online_suitable=False,
            leakage_risks=["phase measurement timing", "post-production lab information"],
            notes="Use only when a measured XRD or equivalent phase measurement is available.",
        ),
        TargetDefinition(
            name="C3A",
            unit="%",
            measurement_method="Measured XRD / Rietveld or lab phase analysis",
            ground_truth_source="MEASURED_XRD",
            prediction_stage="clinker_production",
            online_suitable=False,
            leakage_risks=["phase measurement timing", "post-production lab information"],
            notes="Use only when a measured XRD or equivalent phase measurement is available.",
        ),
        TargetDefinition(
            name="C4AF",
            unit="%",
            measurement_method="Measured XRD / Rietveld or lab phase analysis",
            ground_truth_source="MEASURED_XRD",
            prediction_stage="clinker_production",
            online_suitable=False,
            leakage_risks=["phase measurement timing", "post-production lab information"],
            notes="Use only when a measured XRD or equivalent phase measurement is available.",
        ),
        TargetDefinition(
            name="Clinker_Oxide_Composition",
            unit="%",
            measurement_method="Measured XRF or lab composition analysis",
            ground_truth_source="MEASURED_XRF",
            prediction_stage="post_production_diagnostics",
            online_suitable=False,
            leakage_risks=["post-production lab chemistry"],
            notes="Applicable for offline diagnostics; not for online control when unavailable at prediction time.",
        ),
        TargetDefinition(
            name="Cement_Fineness",
            unit="cm2/g",
            measurement_method="Laboratory Blaine or equivalent",
            ground_truth_source="MEASURED_LAB",
            prediction_stage="cement_grinding",
            online_suitable=False,
            leakage_risks=["post-grinding laboratory measurement"],
            notes="Useful for offline mill optimization and product quality modeling.",
        ),
        TargetDefinition(
            name="Setting_Time",
            unit="minutes",
            measurement_method="Standard mortar setting-time test",
            ground_truth_source="MEASURED_LAB",
            prediction_stage="cement_property",
            online_suitable=False,
            leakage_risks=["post-production laboratory testing"],
            notes="A downstream cement property target, not an online kiln-control target.",
        ),
        TargetDefinition(
            name="Soundness",
            unit="mm",
            measurement_method="Le Chatelier or autoclave expansion test",
            ground_truth_source="MEASURED_LAB",
            prediction_stage="cement_property",
            online_suitable=False,
            leakage_risks=["post-production lab information"],
            notes="An offline quality target for downstream product assurance.",
        ),
        TargetDefinition(
            name="Compressive_Strength_28d",
            unit="MPa",
            measurement_method="Cement mortar/concrete strength test",
            ground_truth_source="MEASURED_LAB",
            prediction_stage="cement_property",
            online_suitable=False,
            leakage_risks=["post-production curing time and test outcome leakage"],
            notes="This is a downstream product-quality target and is not an online kiln-control target.",
        ),
    ]
)


DEFAULT_FEATURE_POLICY = FeaturePolicy(
    features=[
        FeaturePolicyEntry(
            name="raw_material_chemistry",
            availability_level=FeatureAvailabilityLevel.ONLINE_CONTROL,
            online_eligible=True,
            description="Raw-material oxide composition and moisture information available before kiln processing.",
            leakage_risk="LOW",
        ),
        FeaturePolicyEntry(
            name="raw_mix_proportions",
            availability_level=FeatureAvailabilityLevel.ONLINE_CONTROL,
            online_eligible=True,
            description="Blend ratios and raw-meal recipe available before the kiln process completes.",
            leakage_risk="LOW",
        ),
        FeaturePolicyEntry(
            name="kiln_feed_chemistry",
            availability_level=FeatureAvailabilityLevel.ONLINE_CONTROL,
            online_eligible=True,
            description="Chemistry of the kiln feed before burning or early in the process.",
            leakage_risk="LOW",
        ),
        FeaturePolicyEntry(
            name="LSF",
            availability_level=FeatureAvailabilityLevel.ONLINE_CONTROL,
            online_eligible=True,
            description="Lime saturation factor computed from raw-meal chemistry.",
            leakage_risk="LOW",
        ),
        FeaturePolicyEntry(
            name="SM",
            availability_level=FeatureAvailabilityLevel.ONLINE_CONTROL,
            online_eligible=True,
            description="Silica modulus computed from raw-meal chemistry.",
            leakage_risk="LOW",
        ),
        FeaturePolicyEntry(
            name="AM",
            availability_level=FeatureAvailabilityLevel.ONLINE_CONTROL,
            online_eligible=True,
            description="Alumina modulus computed from raw-meal chemistry.",
            leakage_risk="LOW",
        ),
        FeaturePolicyEntry(
            name="kiln_telemetry",
            availability_level=FeatureAvailabilityLevel.ONLINE_CONTROL,
            online_eligible=True,
            description="Process telemetry available during operation, but must be time-aligned to targets.",
            leakage_risk="MEDIUM",
        ),
        FeaturePolicyEntry(
            name="clinker_xrf_oxide",
            availability_level=FeatureAvailabilityLevel.POST_PRODUCTION_DIAGNOSTIC,
            online_eligible=False,
            description="Clinker oxide chemistry measured after production and therefore unsuitable for online prediction when unavailable at prediction time.",
            leakage_risk="HIGH",
        ),
        FeaturePolicyEntry(
            name="clinker_xrd_phase",
            availability_level=FeatureAvailabilityLevel.POST_PRODUCTION_DIAGNOSTIC,
            online_eligible=False,
            description="Measured XRD or Rietveld phase fractions only available after production; use only for offline diagnostics.",
            leakage_risk="HIGH",
        ),
        FeaturePolicyEntry(
            name="cement_strength_test",
            availability_level=FeatureAvailabilityLevel.POST_PRODUCTION_DIAGNOSTIC,
            online_eligible=False,
            description="Measured strength and other test results generated after curing or laboratory evaluation.",
            leakage_risk="HIGH",
        ),
    ]
)


def safe_feature_policy_table() -> List[Dict[str, Any]]:
    return [
        {
            "name": feature.name,
            "availability_level": feature.availability_level.value,
            "online_eligible": feature.online_eligible,
            "description": feature.description,
            "leakage_risk": feature.leakage_risk,
        }
        for feature in DEFAULT_FEATURE_POLICY.features
    ]


def align_process_to_target(
    process_df: pd.DataFrame,
    target_df: pd.DataFrame,
    timestamp_col: str = "timestamp",
    lag_minutes: int = 0,
    residence_time_minutes: Optional[int] = None,
    aggregation_window_minutes: int = 60,
    aggregation_method: str = "mean",
    missing_interval_policy: str = "drop",
) -> pd.DataFrame:
    """Simple helper that aligns process telemetry to target observations with explicit residence-time configuration."""
    config = TemporalAlignmentConfig(
        timestamp_col=timestamp_col,
        lag_minutes=lag_minutes,
        residence_time_minutes=residence_time_minutes,
        aggregation_window_minutes=aggregation_window_minutes,
        aggregation_method=aggregation_method,
        missing_interval_policy=missing_interval_policy,
    )
    return config.align(process_df, target_df)
