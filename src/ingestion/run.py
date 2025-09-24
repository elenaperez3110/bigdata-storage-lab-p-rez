from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, List

import pandas as pd


def tag_lineage(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    """
    Adds lineage metadata:
    - source_file: provided name/path for the origin.
    - ingested_at: UTC ISO-8601 timestamp.
    """
    out = df.copy()
    out["source_file"] = source_name
    out["ingested_at"] = datetime.now(timezone.utc).isoformat()
    return out


def concat_bronze(frames: Iterable[pd.DataFrame]) -> pd.DataFrame:
    """
    Concatenates frames into the Bronze schema:
    Columns: date, partner, amount, source_file, ingested_at
    - Ensures missing columns exist.
    - Preserves order.
    """
    cols = ["date", "partner", "amount", "source_file", "ingested_at"]
    prepared: List[pd.DataFrame] = []
    for df in frames:
        tmp = df.copy()
        # Ensure required columns exist (create if missing)
        for c in cols:
            if c not in tmp.columns:
                tmp[c] = pd.NA
        prepared.append(tmp[cols])

    if not prepared:
        return pd.DataFrame(columns=cols)

    bronze = pd.concat(prepared, ignore_index=True)
    return bronze
