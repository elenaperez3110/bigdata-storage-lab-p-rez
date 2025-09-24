import pandas as pd
import pandera as pa
from pandera.typing import DataFrame, Series
from src.common.io import path
import glob

class Schema(pa.DataFrameModel):
    # Ajusta a tu dataset de muestra
    id: Series[int] = pa.Field(nullable=False)
    fecha: Series[str]
    valor: Series[float] = pa.Field(ge=0)

def validate_bronze():
    for fp in glob.glob(path("bronze", "*.parquet")):
        df = pd.read_parquet(fp)
        Schema.validate(df, lazy=True)

if __name__ == "__main__":
    validate_bronze()
    print("Validación OK")
