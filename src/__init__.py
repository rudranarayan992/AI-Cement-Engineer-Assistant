"""AI Cement Project package."""

from . import pipeline
from . import future_ml
from . import data_qualification
from . import ml_readiness_gate

from . import chemistry
from . import preprocessing
from . import models
from . import prediction
from . import explainability
from . import optimization
from . import rules
from . import llm
from . import uncertainty

# Data lineage and traceability
from .data_lineage import (
    RawMaterial,
    RawMix,
    KilnRun,
    Clinker,
    CementBatch,
    StrengthTest,
    StandardCompliance,
    LineageTrace,
)
from .data_integration import LineageDatabase
from .data_chain_loader import DataChainBuilder
from .explainability.strength_explainer import StrengthExplainer
from .data_qualification import (
    DataBasis,
    VariableClassification,
    DatasetQualificationResult,
    MLReadinessGate,
    qualify_dataset,
    classify_dataframe,
    qualify_dataset_from_file,
    qualify_repository_data,
    assess_ml_readiness,
)

__all__ = [
    "pipeline",
    "future_ml",
    "data_qualification",
    "ml_readiness_gate",
    "chemistry",
    "preprocessing",
    "models",
    "prediction",
    "explainability",
    "optimization",
    "rules",
    "llm",
    "uncertainty",
    "DataBasis",
    "VariableClassification",
    "DatasetQualificationResult",
    "MLReadinessGate",
    "qualify_dataset",
    "classify_dataframe",
    "qualify_dataset_from_file",
    "qualify_repository_data",
    "assess_ml_readiness",
    # Data lineage classes
    "RawMaterial",
    "RawMix",
    "KilnRun",
    "Clinker",
    "CementBatch",
    "StrengthTest",
    "StandardCompliance",
    "LineageTrace",
    "LineageDatabase",
    "DataChainBuilder",
    "StrengthExplainer",
]
