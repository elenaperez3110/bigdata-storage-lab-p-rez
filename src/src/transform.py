from __future__ import annotations

import re
from typing import Dict

import pandas as pd


def _normalize_amount_series(s: pd.Series) -> pd.Series:
    """
    Normalizes monetary strings to float:
    - Removes currency symbols and spaces.
    - Handles European decimal commas.
    - Preserves sign.
    """
    if pd.api.types.is_numeric_dtype(s):
        return s.astype(float)

    # Convert to string, strip spaces
    s_str = s.astype("string").fillna("").str.strip()

    # Remove currency symbols and any letter; keep digits, separators, sign
    s_str = s_str.str.replace(r"[^\d,.\-+]", "", regex=True)

    def _to_float(val: str) -> float | None:
        if val == "":
            return None
        # Decide decimal separator:
        # If both separators present, assume the rightmost is the decimal separator.
        last_comma = val.rfind(",")
        last_dot = val.rfind(".")
        if last_comma == -1 and last_dot == -1:
            # Only digits/sign -> integer
            try:
                return float(val)
            except Exception:
                return None
        if last_comma > last_dot:
            # Comma is decimal sep: remove thousand dots, replace comma with dot
            cleaned = val.replace(".", "").replace(",", ".")
        elif last_dot > last_comma:
            # Dot is decimal sep: remove thousand commas
            cleaned = val.replace(",", "")
        else:
            cleaned = val  # fallback

        try:
            return float(cleaned)
        except Exception:
            return None

    return s_str.map(_to_float).astype("float")


def normalize_columns(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Renames columns using `mapping` (origin -> {'date','partner','amount'}),
    parses dates to datetime64 (ISO-like), normalizes amount to float,
    and trims/collapses spaces in partner.
    """
    out = df.copy()

    # 1) Rename incoming columns to canonical
    out = out.rename(columns=mapping)

    # 2) Parse date
    if "date" in out.columns:
        out["date"] = pd.to_datetime(out["date"], errors="coerce", infer_datetime_format=True)

    # 3) Normalize amount
    if "amount" in out.columns:
        out["amount"] = _normalize_amount_series(out["amount"])

    # 4) Clean partner: strip and collapse internal whitespace
    if "partner" in out.columns:
        out["partner"] = (
            out["partner"]
            .astype("string")
            .fillna("")
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

    return out


def to_silver(bronze: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates Bronze to Silver:
    - Groups by partner and month.
    - `month` is month start timestamp (from Period[M] -> Timestamp).
    - Sums `amount`.
    """
    required_cols = {"date", "partner", "amount"}
    missing = required_cols - set(bronze.columns)
    if missing:
        raise ValueError(f"Bronze frame missing required columns: {missing}")

    silver = bronze.copy()
    # Ensure types
    silver["date"] = pd.to_datetime(silver["date"], errors="coerce")
    silver["amount"] = pd.to_numeric(silver["amount"], errors="coerce")

    # Month as Timestamp (month start)
    silver["month"] = silver["date"].dt.to_period("M").dt.to_timestamp("MS")

    agg = (
        silver.dropna(subset=["partner", "month"])
        .groupby(["partner", "month"], as_index=False, dropna=False)["amount"]
        .sum()
        .sort_values(["partner", "month"])
        .reset_index(drop=True)
    )

    return agg
