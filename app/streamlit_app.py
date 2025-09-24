# streamlit_app.py
# ------------------------------------------------------------
# App Streamlit para ingestar múltiples CSV heterogéneos,
# normalizarlos a un esquema canónico (date, partner, amount),
# etiquetar linaje, validar y derivar una capa Silver agregada
# por partner x mes. Permite descargar bronze.csv y silver.csv.
# ------------------------------------------------------------

from __future__ import annotations

from io import StringIO, BytesIO
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st

# Funciones del pipeline (de este repo)
from src.transform import normalize_columns, to_silver
from src.validate import basic_checks
from src.ingest import tag_lineage, concat_bronze


# --------------------------
# Utilidades
# --------------------------
def read_csv_safely(file) -> pd.DataFrame:
    """
    Intenta leer un CSV con UTF-8 y hace fallback a latin-1 si falla.
    Devuelve DataFrame; si no se puede leer, relanza la excepción.
    """
    # Streamlit sube archivos como buffer tipo BytesIO
    # Probamos primero utf-8
    try:
        return pd.read_csv(file, encoding="utf-8")
    except UnicodeDecodeError:
        file.seek(0)  # Reset buffer al inicio para reintentar
        return pd.read_csv(file, encoding="latin-1")
    except Exception:
        # Reset por si el usuario quiere volver a reintentar desde la UI
        file.seek(0)
        raise


def build_mapping(date_col: str, partner_col: str, amount_col: str) -> Dict[str, str]:
    """
    Construye el mapeo origen -> canónico para normalize_columns.
    Solo incluye entradas no vacías.
    """
    mapping: Dict[str, str] = {}
    if date_col.strip():
        mapping[date_col.strip()] = "date"
    if partner_col.strip():
        mapping[partner_col.strip()] = "partner"
    if amount_col.strip():
        mapping[amount_col.strip()] = "amount"
    return mapping


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """
    Serializa un DataFrame a CSV (UTF-8 con BOM opcional no requerido).
    """
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue().encode("utf-8")


# --------------------------
# UI: Sidebar
# --------------------------
st.set_page_config(page_title="Big Data Storage Lab - Bronze/Silver", layout="wide")

st.sidebar.header("Configuración de columnas origen")
st.sidebar.caption("Indica cómo se llaman en tus CSV las columnas que mapean a `date`, `partner`, `amount`.")

col_date = st.sidebar.text_input("Columna de fecha (origen → date)", value="date")
col_partner = st.sidebar.text_input("Columna de socio/cliente (origen → partner)", value="partner")
col_amount = st.sidebar.text_input("Columna de importe (origen → amount)", value="amount")

mapping = build_mapping(col_date, col_partner, col_amount)

st.sidebar.markdown("---")
uploaded_files = st.sidebar.file_uploader(
    "Sube uno o más CSV",
    type=["csv"],
    accept_multiple_files=True,
    help="Puedes arrastrar varios archivos a la vez."
)

st.title("De CSVs heterogéneos a un almacén analítico confiable")
st.write(
    "Esta app normaliza CSVs al esquema canónico **(date, partner, amount)**, "
    "agrega metadatos de linaje y deriva una capa **Silver** por partner × mes."
)

# --------------------------
# Lógica principal
# --------------------------
if not uploaded_files:
    st.info("⬆️ Sube uno o más CSV desde la barra lateral para comenzar.")
    st.stop()

# Leer, normalizar y etiquetar linaje por archivo
frames_bronze: List[pd.DataFrame] = []
read_errors: List[Tuple[str, str]] = []

with st.spinner("Leyendo y normalizando archivos..."):
    for uf in uploaded_files:
        try:
            df_raw = read_csv_safely(uf)
            df_norm = normalize_columns(df_raw, mapping=mapping)
            df_tagged = tag_lineage(df_norm, source_name=uf.name)
            frames_bronze.append(df_tagged)
        except Exception as ex:
            read_errors.append((uf.name, str(ex)))

# Mostrar errores de lectura (si los hubo)
if read_errors:
    with st.expander("⚠️ Errores al leer/normalizar algunos archivos", expanded=True):
        for fname, msg in read_errors:
            st.error(f"**{fname}**: {msg}")

# Unificar Bronze
bronze = concat_bronze(frames_bronze)

st.subheader("Bronze unificado")
st.dataframe(bronze, use_container_width=True, hide_index=True)

# Validaciones
st.subheader("Validaciones (basic_checks)")
errors = basic_checks(bronze)

if errors:
    st.error("Se encontraron problemas en los datos canónicos:")
    for e in errors:
        st.write(f"- {e}")
    st.info("Corrige las columnas de mapeo o revisa los CSV y vuelve a intentar.")
else:
    st.success("Validaciones OK ✅ Los datos cumplen las verificaciones mínimas.")

# Descarga Bronze siempre disponible (aunque con errores, puede ayudar a depurar)
bronze_csv = df_to_csv_bytes(bronze)
st.download_button(
    "⬇️ Descargar bronze.csv",
    data=bronze_csv,
    file_name="bronze.csv",
    mime="text/csv",
    use_container_width=True,
)

# Si OK, derivar Silver
if not errors:
    with st.spinner("Derivando capa Silver (partner × mes)..."):
        silver = to_silver(bronze)

    st.subheader("Silver (partner × mes)")
    st.dataframe(silver, use_container_width=True, hide_index=True)

    # KPIs simples
    st.subheader("KPIs")
    c1, c2, c3, c4 = st.columns(4)
    total_rows = len(bronze)
    unique_partners = bronze["partner"].nunique(dropna=True) if "partner" in bronze.columns else 0
    total_amount = silver["amount"].sum() if "amount" in silver.columns else 0.0
    date_min = pd.to_datetime(bronze["date"], errors="coerce").min()
    date_max = pd.to_datetime(bronze["date"], errors="coerce").max()

    c1.metric("Filas (Bronze)", f"{total_rows:,}")
    c2.metric("Partners únicos", f"{unique_partners:,}")
    c3.metric("Total amount (EUR)", f"{total_amount:,.2f}")
    c4.metric(
        "Rango de fechas",
        f"{date_min.date() if pd.notna(date_min) else '—'} → {date_max.date() if pd.notna(date_max) else '—'}",
    )

    # Bar chart: mes vs amount
    st.subheader("Evolución por mes (Silver)")
    # Aseguramos un índice temporal mensual para la gráfica
    monthly = silver.groupby("month", as_index=False)["amount"].sum().sort_values("month")
    monthly_chart = monthly.set_index("month")  # index = Timestamp (inicio de mes)
    st.bar_chart(monthly_chart, use_container_width=True)

    # Descarga Silver
    silver_csv = df_to_csv_bytes(silver)
    st.download_button(
        "⬇️ Descargar silver.csv",
        data=silver_csv,
        file_name="silver.csv",
        mime="text/csv",
        use_container_width=True,
    )

# Notas de ayuda
with st.expander("Ayuda / Notas"):
    st.markdown(
        """
- **Mapeo de columnas**: usa la barra lateral para indicar cómo se llaman en tus CSV las columnas que deben mapearse a `date`, `partner`, `amount`.
- **Fechas**: se intentan parsear automáticamente a `datetime`. Formatos comunes (`YYYY-MM-DD`, `DD/MM/YYYY`, etc.) son soportados.
- **Amount**: se limpian símbolos monetarios y separadores europeos (coma decimal). Se normaliza a `float` en EUR.
- **Linaje**: se añaden `source_file` y `ingested_at (UTC)`.
- **Validaciones**: `basic_checks` exige columnas canónicas, `amount` numérico y ≥ 0, y `date` en datetime.
- **Gráfica**: se construye desde Silver, agregando por mes (marca de tiempo de inicio de mes).
        """
    )
