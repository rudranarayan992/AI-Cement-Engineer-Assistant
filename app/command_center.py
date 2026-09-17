"""Lightweight Streamlit command center placeholder.

Provides navigation links and quick actions to key ML functions implemented.
"""
from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="AI Engineering Command Center", layout="wide")

st.title("AI Engineering Command Center")
st.write("This is a lightweight command center. Use the left nav to access tools.")

st.header("Quick Actions")
if st.button("Train all eligible models"):
    st.write("Run `train_all_models.py` in a terminal to execute training pipeline.")

st.markdown("- Case DB: `src/ml/case_registry.py`")
st.markdown("- Unified Input Parser: `src/ml/unified_input.py`")
st.markdown("- Deterministic calculations: `src/ml/deterministic_calculations.py`")

st.header("Status")
st.info("Clinker ML targets: BLOCKED until measured clinker dataset is provided.")
