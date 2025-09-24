import pandas as pd
from src.common.io import path

if __name__ == "__main__":
    df = pd.read_parquet(path("silver", "dataset.parquet"))
    kpis = {
        "registros": len(df),
        "completitud_%": 100 * (1 - df.isna().mean().mean()),
        "duplicados": int(df.duplicated().sum()),
    }
    print(kpis)
