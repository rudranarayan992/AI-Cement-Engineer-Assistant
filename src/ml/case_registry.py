"""Case registry for persistent engineering memory and historical case tracking.

This module provides:
1. Case ID generation (UUID-based with semantic prefixes)
2. Case persistence (SQLite database)
3. Case metadata (inputs, predictions, actual results, errors)
4. Exact case matching (find identical or near-identical inputs)
5. Similar case search (k-NN based on feature similarity)
6. Case-to-outcome tracking (prediction vs actual, residual analysis)
7. Case narrative generation (story of each engineering decision)

SCIENTIFIC PRINCIPLES:
- All case data must be labeled with provenance (MEASURED/CALCULATED/PREDICTED/REFERENCE)
- Case history is NEVER fabricated; only recorded from real predictions or explicit user entry
- Exact match requires identical input normalizations and unit conversions
- Similar case search uses Euclidean distance in normalized feature space
- Cases are immutable once recorded; corrections create new cases
- Case DB supports retraining analysis and actual-vs-predicted tracking

DATABASE SCHEMA:
- cases: master case table with ID, timestamp, input hash, prediction, unit, status
- case_features: normalized input features for similarity search
- case_actuals: recorded actual results (from lab tests or user feedback)
- case_errors: prediction error analysis (residual, MAPE, direction)
- case_tags: user-assigned tags for case grouping and annotation
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

import numpy as np
import pandas as pd


@dataclass
class CaseMetadata:
    """Immutable metadata for a single engineering case."""

    case_id: str
    timestamp: str
    target: str
    unit: str
    input_hash: str
    provenance: str  # MEASURED/CALCULATED/PREDICTED/REFERENCE/SYNTHETIC
    input_dict: Dict[str, Any]
    prediction: Optional[float]
    confidence: float
    uncertainty: float
    ood_status: str
    physics_status: str
    warnings: List[str]
    explanation: Optional[str] = None
    drivers: Optional[Dict[str, Any]] = None


@dataclass
class CaseActual:
    """Recorded actual result for a case (from lab test or user feedback)."""

    case_id: str
    actual_value: float
    measurement_date: str
    measurement_source: str  # lab_test, user_entry, instrument, reference_publication
    measurement_method: str
    measurement_uncertainty: Optional[float] = None
    notes: str = ""


@dataclass
class CaseError:
    """Computed error metrics for a case with actual result."""

    case_id: str
    predicted: float
    actual: float
    error_absolute: float
    error_percent: float
    error_direction: str  # under_predicted, over_predicted, unbiased
    residual_z_score: Optional[float] = None


class CaseRegistry:
    """Persistent case database for engineering memory and historical matching."""

    def __init__(self, db_path: str | Path = "cases.db"):
        """Initialize case registry with SQLite database."""
        self.db_path = Path(db_path)
        self._ensure_db_exists()

    def _ensure_db_exists(self) -> None:
        """Create database schema if not exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Master cases table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cases (
                case_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                target TEXT NOT NULL,
                unit TEXT NOT NULL,
                input_hash TEXT NOT NULL UNIQUE,
                provenance TEXT NOT NULL,
                input_json TEXT NOT NULL,
                prediction REAL,
                confidence REAL,
                uncertainty REAL,
                ood_status TEXT,
                physics_status TEXT,
                warnings_json TEXT,
                explanation TEXT,
                drivers_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Case features for similarity search (normalized)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS case_features (
                feature_id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                feature_name TEXT NOT NULL,
                feature_value REAL,
                FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
            )
            """
        )

        # Actual results (from lab tests)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS case_actuals (
                actual_id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                actual_value REAL NOT NULL,
                measurement_date TEXT NOT NULL,
                measurement_source TEXT NOT NULL,
                measurement_method TEXT NOT NULL,
                measurement_uncertainty REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
            )
            """
        )

        # Error analysis
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS case_errors (
                error_id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                predicted REAL NOT NULL,
                actual REAL NOT NULL,
                error_absolute REAL NOT NULL,
                error_percent REAL NOT NULL,
                error_direction TEXT NOT NULL,
                residual_z_score REAL,
                computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
            )
            """
        )

        # User tags for case annotation
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS case_tags (
                tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                tag TEXT NOT NULL,
                FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
            )
            """
        )

        # Create indices for fast lookup
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_target ON cases(target)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON cases(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_input_hash ON cases(input_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_provenance ON cases(provenance)")

        conn.commit()
        conn.close()

    def _compute_input_hash(self, input_dict: Dict[str, Any]) -> str:
        """Compute deterministic hash of normalized input for exact matching."""
        # Sort keys and serialize to JSON for consistent hashing
        sorted_input = json.dumps(input_dict, sort_keys=True, default=str)
        return hashlib.sha256(sorted_input.encode()).hexdigest()[:16]

    def record_case(
        self,
        target: str,
        unit: str,
        input_dict: Dict[str, Any],
        prediction: Optional[float],
        confidence: float,
        uncertainty: float,
        ood_status: str,
        physics_status: str,
        warnings: List[str],
        provenance: str,
        explanation: Optional[str] = None,
        drivers: Optional[Dict[str, Any]] = None,
        features_normalized: Optional[Dict[str, float]] = None,
    ) -> str:
        """Record a single engineering case and return case_id.

        Args:
            target: prediction target name (e.g., "compressive_strength")
            unit: target unit (e.g., "MPa")
            input_dict: normalized input parameters
            prediction: predicted value or None if blocked
            confidence: confidence score [0, 1]
            uncertainty: uncertainty estimate
            ood_status: OOD detection result (IN_DISTRIBUTION, OOD, BLOCKED, etc.)
            physics_status: physics validation result (OK, WARNING, VIOLATION, BLOCKED)
            warnings: list of warning messages
            provenance: data provenance (MEASURED, CALCULATED, PREDICTED, REFERENCE, SYNTHETIC)
            explanation: natural language explanation
            drivers: feature importance / driver analysis
            features_normalized: normalized features for similarity search

        Returns:
            case_id as string
        """
        case_id = f"{target[:3].upper()}-{uuid4().hex[:12].upper()}"
        timestamp = datetime.utcnow().isoformat() + "Z"
        input_hash = self._compute_input_hash(input_dict)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO cases (
                    case_id, timestamp, target, unit, input_hash, provenance,
                    input_json, prediction, confidence, uncertainty, ood_status,
                    physics_status, warnings_json, explanation, drivers_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    case_id,
                    timestamp,
                    target,
                    unit,
                    input_hash,
                    provenance,
                    json.dumps(input_dict, default=str),
                    prediction,
                    confidence,
                    uncertainty,
                    ood_status,
                    physics_status,
                    json.dumps(warnings),
                    explanation,
                    json.dumps(drivers, default=str) if drivers else None,
                ),
            )

            # Record normalized features if provided
            if features_normalized:
                for fname, fvalue in features_normalized.items():
                    cursor.execute(
                        "INSERT INTO case_features (case_id, feature_name, feature_value) VALUES (?, ?, ?)",
                        (case_id, fname, fvalue),
                    )

            conn.commit()
            return case_id

        except sqlite3.IntegrityError as e:
            conn.close()
            raise ValueError(f"Case with input_hash {input_hash} already exists") from e
        finally:
            conn.close()

    def find_exact_match(self, input_dict: Dict[str, Any], target: str) -> Optional[Dict[str, Any]]:
        """Find an exact matching case by input hash.

        Returns case metadata or None if not found.
        """
        input_hash = self._compute_input_hash(input_dict)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM cases WHERE input_hash = ? AND target = ? LIMIT 1",
            (input_hash, target),
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_case_dict(row)

    def find_similar_cases(
        self,
        input_features: Dict[str, float],
        target: str,
        k: int = 5,
        distance_threshold: float = 2.0,
    ) -> List[Dict[str, Any]]:
        """Find k most similar cases using Euclidean distance in feature space.

        Args:
            input_features: normalized input features (dict of feature_name -> value)
            target: prediction target
            k: number of neighbors to return
            distance_threshold: only return cases with distance <= threshold

        Returns:
            List of case metadata dicts, sorted by distance (ascending)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get all cases for this target with their features
        cursor.execute(
            """
            SELECT DISTINCT c.case_id, c.timestamp, c.prediction, c.target, c.unit
            FROM cases c
            WHERE c.target = ?
            ORDER BY c.timestamp DESC
            """,
            (target,),
        )
        case_rows = cursor.fetchall()

        # Compute distances
        distances: List[Tuple[str, float]] = []

        for case_row in case_rows:
            case_id = case_row[0]

            # Get features for this case
            cursor.execute(
                "SELECT feature_name, feature_value FROM case_features WHERE case_id = ?",
                (case_id,),
            )
            case_features_raw = cursor.fetchall()
            case_features = {fname: fval for fname, fval in case_features_raw}

            # Compute Euclidean distance
            distance = self._compute_feature_distance(input_features, case_features)
            distances.append((case_id, distance))

        conn.close()

        # Sort by distance and filter by threshold
        distances.sort(key=lambda x: x[1])
        similar_ids = [cid for cid, dist in distances if dist <= distance_threshold][:k]

        # Fetch full case metadata
        similar_cases = []
        for case_id in similar_ids:
            case_dict = self.get_case(case_id)
            if case_dict:
                similar_cases.append(case_dict)

        return similar_cases

    def _compute_feature_distance(
        self, features1: Dict[str, float], features2: Dict[str, float]
    ) -> float:
        """Compute Euclidean distance between two feature dictionaries."""
        all_keys = set(features1.keys()) | set(features2.keys())
        if not all_keys:
            return 0.0

        squared_diffs = []
        for key in all_keys:
            v1 = features1.get(key, 0.0)
            v2 = features2.get(key, 0.0)
            squared_diffs.append((v1 - v2) ** 2)

        return float(np.sqrt(np.sum(squared_diffs)))

    def record_actual(
        self,
        case_id: str,
        actual_value: float,
        measurement_source: str,
        measurement_method: str,
        measurement_date: Optional[str] = None,
        measurement_uncertainty: Optional[float] = None,
        notes: str = "",
    ) -> None:
        """Record actual measurement result for a case.

        Args:
            case_id: case identifier
            actual_value: measured value
            measurement_source: lab_test, user_entry, instrument, reference_publication, etc.
            measurement_method: description of measurement method (e.g., "XRD Rietveld", "28-day cylinder test")
            measurement_date: ISO format date or None for now
            measurement_uncertainty: uncertainty of measurement
            notes: additional notes
        """
        if measurement_date is None:
            measurement_date = datetime.utcnow().isoformat() + "Z"

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO case_actuals (
                case_id, actual_value, measurement_date, measurement_source,
                measurement_method, measurement_uncertainty, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                case_id,
                actual_value,
                measurement_date,
                measurement_source,
                measurement_method,
                measurement_uncertainty,
                notes,
            ),
        )

        conn.commit()
        conn.close()

        # Automatically compute error
        self._compute_case_error(case_id)

    def _compute_case_error(self, case_id: str) -> None:
        """Compute and store error metrics when actual result is recorded."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get prediction
        cursor.execute("SELECT prediction FROM cases WHERE case_id = ?", (case_id,))
        pred_row = cursor.fetchone()
        if not pred_row or pred_row[0] is None:
            conn.close()
            return

        prediction = pred_row[0]

        # Get actual
        cursor.execute(
            "SELECT actual_value FROM case_actuals WHERE case_id = ? ORDER BY created_at DESC LIMIT 1",
            (case_id,),
        )
        actual_row = cursor.fetchone()
        if not actual_row:
            conn.close()
            return

        actual = actual_row[0]

        # Compute metrics
        error_abs = abs(actual - prediction)
        error_pct = (error_abs / abs(actual)) * 100 if actual != 0 else float("inf")
        error_dir = "over_predicted" if prediction > actual else ("under_predicted" if prediction < actual else "unbiased")

        cursor.execute(
            """
            INSERT INTO case_errors (
                case_id, predicted, actual, error_absolute, error_percent, error_direction
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (case_id, prediction, actual, error_abs, error_pct, error_dir),
        )

        conn.commit()
        conn.close()

    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve full case metadata by case_id."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        case_dict = self._row_to_case_dict(row)

        # Add features
        cursor.execute("SELECT feature_name, feature_value FROM case_features WHERE case_id = ?", (case_id,))
        features = {fname: fval for fname, fval in cursor.fetchall()}
        case_dict["features"] = features

        # Add actual if exists
        cursor.execute(
            "SELECT actual_value, measurement_source, measurement_date FROM case_actuals WHERE case_id = ? ORDER BY created_at DESC LIMIT 1",
            (case_id,),
        )
        actual_row = cursor.fetchone()
        if actual_row:
            case_dict["actual"] = {
                "value": actual_row[0],
                "source": actual_row[1],
                "date": actual_row[2],
            }

        # Add error if exists
        cursor.execute(
            "SELECT error_absolute, error_percent, error_direction FROM case_errors WHERE case_id = ? ORDER BY computed_at DESC LIMIT 1",
            (case_id,),
        )
        error_row = cursor.fetchone()
        if error_row:
            case_dict["error"] = {
                "absolute": error_row[0],
                "percent": error_row[1],
                "direction": error_row[2],
            }

        conn.close()
        return case_dict

    def _row_to_case_dict(self, row: Tuple) -> Dict[str, Any]:
        """Convert database row to case dictionary."""
        return {
            "case_id": row[0],
            "timestamp": row[1],
            "target": row[2],
            "unit": row[3],
            "input_hash": row[4],
            "provenance": row[5],
            "input": json.loads(row[6]),
            "prediction": row[7],
            "confidence": row[8],
            "uncertainty": row[9],
            "ood_status": row[10],
            "physics_status": row[11],
            "warnings": json.loads(row[12]) if row[12] else [],
            "explanation": row[13],
            "drivers": json.loads(row[14]) if row[14] else None,
        }

    def get_cases_for_target(self, target: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all cases for a target, ordered by most recent."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT case_id FROM cases WHERE target = ? ORDER BY timestamp DESC LIMIT ?",
            (target, limit),
        )
        case_ids = [row[0] for row in cursor.fetchall()]
        conn.close()

        return [self.get_case(cid) for cid in case_ids if self.get_case(cid)]

    def get_cases_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get all cases with a specific tag."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT case_id FROM case_tags WHERE tag = ?", (tag,))
        case_ids = [row[0] for row in cursor.fetchall()]
        conn.close()

        return [self.get_case(cid) for cid in case_ids if self.get_case(cid)]

    def add_tag(self, case_id: str, tag: str) -> None:
        """Add a tag to a case for annotation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO case_tags (case_id, tag) VALUES (?, ?)", (case_id, tag))

        conn.commit()
        conn.close()

    def get_error_statistics(self, target: str, provenance: Optional[str] = None) -> Dict[str, float]:
        """Compute error statistics for cases with actual results.

        Args:
            target: prediction target
            provenance: filter by provenance (MEASURED, PREDICTED, etc.) or None for all

        Returns:
            Dict with mean/median/stdev error metrics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT ce.error_absolute, ce.error_percent, ce.error_direction
            FROM case_errors ce
            JOIN cases c ON ce.case_id = c.case_id
            WHERE c.target = ?
        """
        params = [target]

        if provenance:
            query += " AND c.provenance = ?"
            params.append(provenance)

        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return {
                "count": 0,
                "mean_error_abs": None,
                "median_error_abs": None,
                "stdev_error_abs": None,
                "mean_error_pct": None,
            }

        errors_abs = [row[0] for row in rows]
        errors_pct = [row[1] for row in rows]

        return {
            "count": len(rows),
            "mean_error_abs": float(np.mean(errors_abs)),
            "median_error_abs": float(np.median(errors_abs)),
            "stdev_error_abs": float(np.std(errors_abs)) if len(errors_abs) > 1 else 0.0,
            "mean_error_pct": float(np.mean(errors_pct)),
            "over_predicted_count": sum(1 for row in rows if row[2] == "over_predicted"),
            "under_predicted_count": sum(1 for row in rows if row[2] == "under_predicted"),
        }

    def export_cases_dataframe(self, target: Optional[str] = None) -> pd.DataFrame:
        """Export cases as pandas DataFrame for analysis."""
        conn = sqlite3.connect(self.db_path)
        query = "SELECT case_id, timestamp, target, prediction, ood_status, physics_status, provenance FROM cases"
        params = []

        if target:
            query += " WHERE target = ?"
            params.append(target)

        df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        return df

    def delete_case(self, case_id: str) -> None:
        """Delete a case and all associated data (use cautiously)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM cases WHERE case_id = ?", (case_id,))

        conn.commit()
        conn.close()

    def summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics of the case database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM cases")
        total_cases = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM case_actuals")
        cases_with_actuals = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM case_errors")
        cases_with_errors = cursor.fetchone()[0]

        cursor.execute("SELECT DISTINCT target FROM cases")
        targets = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT provenance, COUNT(*) FROM cases GROUP BY provenance")
        provenance_dist = {row[0]: row[1] for row in cursor.fetchall()}

        conn.close()

        return {
            "total_cases": total_cases,
            "cases_with_actuals": cases_with_actuals,
            "cases_with_errors": cases_with_errors,
            "targets": targets,
            "provenance_distribution": provenance_dist,
        }
