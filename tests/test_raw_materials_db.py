import os
import tempfile
import pandas as pd
from src.chemistry import raw_materials_db as rdb


def test_create_and_add_and_export():
    td = tempfile.mkdtemp()
    csv_path = os.path.join(td, "raw_materials.csv")
    # Create template
    rdb.create_raw_materials_template(csv_path)
    assert os.path.exists(csv_path)

    # Add an illustrative row (allowed but must be marked illustrative)
    row = {
        "Source_ID": "ILL-EX-001",
        "Source_Name": "Illustrative Limestone",
        "Source_Type": "supplier",
        "DOI_URL": "",
        "table_figure_page": "",
        "unit": "wt%",
        "measurement_method": "illustrative",
        "data_status": "illustrative",
        "CaO": "52.3",
        "SiO2": "1.2",
        "Al2O3": "0.3",
    }
    rdb.add_material(row, csv_path)
    df = pd.read_csv(csv_path, dtype=str)
    assert df.shape[0] == 1
    assert df.iloc[0]["Source_ID"] == "ILL-EX-001"

    # Export to excel
    excel_path = os.path.join(td, "AI_Cement_Database.xlsx")
    rdb.export_to_excel({"02_Raw_Materials": csv_path}, excel_path)
    assert os.path.exists(excel_path)
