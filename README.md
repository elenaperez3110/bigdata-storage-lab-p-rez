## Cómo ejecutar
```bash
make install          # crea venv e instala deps
make ingest           # ingesta → bronze
make validate         # validación de calidad
make normalize        # bronze → silver
make kpis             # imprime KPIs en consola
make app              # abre la app Streamlit


---

## 4) Añade un dataset de ejemplo (sintético)
Crea un CSV pequeño en `data/sample/ventas.csv`:
```csv
id,fecha,valor
1,2025-01-01,100.5
2,2025/01/02,200
3,01-03-2025,150.25
4,2025-01-04,
4,2025-01-04,300
