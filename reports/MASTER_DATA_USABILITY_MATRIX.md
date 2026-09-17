# MASTER DATA USABILITY MATRIX
| Dataset | Rows | Raw-material chemistry | Raw-mix data | Raw-meal chemistry | Kiln telemetry | Clinker chemistry | Free CaO | C3S | C2S | C3A | C4AF | Timestamps | Sample IDs | Plant IDs | Measurement methods | Traceability | Scientific usability |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DiB - Cement Plant data.xlsx | 1126 | Possibly inventory items | No | No | Possibly process/energy info | No measured clinker chemistry | No | No | No | No | No | No production timestamps | No plant sample IDs | Possibly process plants/locations | Inventory methodology documented, not clinker measurement | No clinker traceability | Plant LCA / impact inventory only |
| Concrete_Data.xls | 1030 | No | No | No | No | No | No | No | No | No | No | No | No | No | Concrete testing methods, not clinker | No | Concrete dataset only |
| blended_cement_concrete_database.csv | 8979 | No | No | No | No | No | No | No | No | No | No | No | No | No | Concrete curing and strength measurement protocols | No | Concrete strength database only |
| AI_Cement_Project/reports/baseline_model_results.csv | 4 | No | No | No | No | No | No | No | No | No | No | No | No | No | Model metrics only | No | Not an input dataset |
| AI_Cement_Project/data/cement_master_dataset.csv | 1200 | No | Yes | Yes | Yes | Yes | Yes (generated) | Yes (generated/Bogue-style) | Yes (generated/Bogue-style) | Yes (generated/Bogue-style) | Yes (generated/Bogue-style) | No | Yes (Batch_ID) | No | Not documented | Synthetic / no real process chain | Rejected for clinker ML |
| AI_Cement_Project/data/raw_mix/raw_meal_samples.csv | 1200 | No | Yes | Yes | No | No | No | No | No | No | No | No | Yes (Batch_ID) | No | Not documented | Synthetic only | Demonstration only |
| AI_Cement_Project/data/raw_materials/raw_materials_database.csv | 6 | Yes | No | No | No | No | No | No | No | No | No | No | Yes (Sample_ID) | No | Material assay not documented | No | Reference only |
| AI_Cement_Project/data/processed/concrete_X_train.csv | 804 | No | No | No | No | No | No | No | No | No | No | No | No | No | Not documented | No | Not valid for clinker work |
| AI_Cement_Project/data/processed/concrete_y_train.csv | 804 | No | No | No | No | No | No | No | No | No | No | No | No | No | Not documented | No | Not valid for clinker work |
