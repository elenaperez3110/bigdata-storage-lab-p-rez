import streamlit as st
import pandas as pd
from src.common.io import path

st.title("Calidad de Datos y KPIs (Silver)")
fp = path("silver", "dataset.parquet")

try:
    df = pd.read_parquet(fp)
    st.metric("Registros", len(df))
    st.metric("Completitud (%)", round(100 * (1 - df.isna().mean().mean()), 2))
    st.metric("Duplicados", int(df.duplicated().sum()))
    st.subheader("Vista Silver")
    st.dataframe(df.head(500))
except Exception as e:
    st.warning(f"No se pudo cargar {fp}. Corre primero: make ingest validate normalize")
