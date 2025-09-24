import pandas as pd
from src.common.io import path

def load_raw_to_bronze():
    # Ejemplo: ingiere todos los CSV de data/sample a bronze con tipado básico
    sample_dir = path("sample")
    bronze_dir = path("bronze")
    bronze_dir and os.makedirs(bronze_dir, exist_ok=True)

    for f in os.listdir(sample_dir):
        if f.endswith(".csv"):
            df = pd.read_csv(os.path.join(sample_dir, f))
            # Tipado mínimo: fechas/num si aplica
            df.to_parquet(os.path.join(bronze_dir, f.replace(".csv", ".parquet")), index=False)

if __name__ == "__main__":
    import os
    os.makedirs(path("bronze"), exist_ok=True)
    load_raw_to_bronze()
    print("Ingesta → Bronze OK")
