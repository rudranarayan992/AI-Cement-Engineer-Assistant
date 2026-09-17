"""Raw materials database utilities for AI Cement Engineer Phase 1.

Functions:
- create_raw_materials_template(csv_path)
- load_raw_materials(csv_path)
- validate_material_row(row_dict)
- add_material(entry_dict, csv_path)
- export_to_excel(csv_paths_dict, excel_path)

Notes:
- This module creates templates and performs validation only.
- It does NOT invent measured data. Any example rows must be labelled `illustrative`.
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List
import pandas as pd

REQUIRED_COLUMNS = [
    "Source_ID",
    "Source_Name",
    "Source_Type",
    "DOI_URL",
    "table_figure_page",
    "unit",
    "measurement_method",
    "data_status",
    "CaO",
    "SiO2",
    "Al2O3",
    "Fe2O3",
    "MgO",
    "SO3",
    "Na2O",
    "K2O",
    "TiO2",
    "P2O5",
    "LOI",
    "moisture",
    "density",
    "fineness",
    "particle_size",
    "specific_surface",
    "mineralogy",
    "notes",
    "added_date",
]

ALLOWED_DATA_STATUS = {"measured", "calculated", "simulated", "illustrative", "missing"}


def create_raw_materials_template(csv_path: str) -> None:
    """Create a template CSV for raw materials with header and notes."""
    df = pd.DataFrame(columns=REQUIRED_COLUMNS)
    df.to_csv(csv_path, index=False)


def load_raw_materials(csv_path: str) -> pd.DataFrame:
    """Load raw materials CSV into a DataFrame.

    Raises FileNotFoundError if missing.
    """
    df = pd.read_csv(csv_path, dtype=str)
    return df


def validate_material_row(row: Dict) -> List[str]:
    """Validate a single raw-material row dict.

    Returns list of validation error messages (empty if valid).
    """
    errors = []
    for col in ["Source_ID", "data_status"]:
        if col not in row or pd.isna(row.get(col)) or str(row.get(col)).strip() == "":
            errors.append(f"Missing required field: {col}")

    ds = str(row.get("data_status", "")).strip().lower()
    if ds not in ALLOWED_DATA_STATUS:
        errors.append(f"Invalid data_status '{row.get('data_status')}'. Allowed: {sorted(ALLOWED_DATA_STATUS)}")

    # unit should be provided for measured or calculated values
    if ds in {"measured", "calculated"}:
        if not row.get("unit"):
            errors.append("unit is required for measured or calculated data_status")

    # Basic numeric columns validation: ensure if present they are parseable to float
    numeric_cols = ["CaO", "SiO2", "Al2O3", "Fe2O3", "MgO", "SO3", "Na2O", "K2O", "TiO2", "P2O5", "LOI", "moisture", "density", "fineness", "particle_size", "specific_surface"]
    for c in numeric_cols:
        val = row.get(c)
        if val is None or (isinstance(val, float) and pd.isna(val)):
            continue
        if str(val).strip() == "":
            continue
        try:
            float(str(val))
        except Exception:
            errors.append(f"Column {c} must be numeric or empty. Got: {val}")

    return errors


def add_material(entry: Dict, csv_path: str) -> None:
    """Validate and append a material entry (dict) to `csv_path`.

    entry should contain at least `Source_ID` and `data_status`.
    """
    errs = validate_material_row(entry)
    if errs:
        raise ValueError("Validation errors: " + "; ".join(errs))

    # Ensure all required columns present
    row = {c: entry.get(c, "") for c in REQUIRED_COLUMNS}
    if not row.get("added_date"):
        row["added_date"] = datetime.utcnow().isoformat()

    df = None
    try:
        df = pd.read_csv(csv_path, dtype=str)
    except FileNotFoundError:
        df = pd.DataFrame(columns=REQUIRED_COLUMNS)

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True, sort=False)
    df.to_csv(csv_path, index=False)


def export_to_excel(csv_paths: Dict[str, str], excel_path: str) -> None:
    """Export multiple CSVs to an Excel workbook with sheet mapping.

    csv_paths: mapping sheet_name -> csv_path
    """
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        for sheet, path in csv_paths.items():
            try:
                df = pd.read_csv(path, dtype=str)
            except FileNotFoundError:
                df = pd.DataFrame()
            df.to_excel(writer, sheet_name=sheet[:31], index=False)


if __name__ == "__main__":
    # Minimal demo: create template if run directly
    import os
    base = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
    base = os.path.abspath(base)
    template_path = os.path.join(base, "02_Raw_Materials_template.csv")
    create_raw_materials_template(template_path)
    print("Created template:", template_path)
