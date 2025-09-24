## Cómo ejecutar
```bash
make install          # crea venv e instala deps
make ingest           # ingesta → bronze
make validate         # validación de calidad
make normalize        # bronze → silver
make kpis             # imprime KPIs en consola
make app              # abre la app Streamlit
