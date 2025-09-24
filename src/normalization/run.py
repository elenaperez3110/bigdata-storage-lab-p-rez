import pandas as pd
import glob, os
from src.common.io import path

def normalize_to_silver():
    os.makedirs(path("silver"), exist_ok=True)
    frames = []
    for fp in glob.glob(path("bronze", "*.parquet")):
        df = pd.read_parquet(fp)
        # Normalización mínima: nombres canónicos
        df = df.rename(columns=str.lower)
        # Estandariza fecha si viene como string
        if "fecha" in df.columns:
            df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce").dt.date
        frames.append(df)
    if frames:
        out = pd.concat(frames, ignore_index=True)
        out.to_parquet(path("silver", "dataset.parquet"), index=False)

if __name__ == "__main__":
    normalize_to_silver()
    print("Silver OK")
