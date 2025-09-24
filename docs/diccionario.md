# Diccionario de Datos (Canónico)

## Esquema Canónico
Los datasets deberán normalizarse al siguiente **esquema canónico**:

| Campo   | Tipo         | Descripción                                           | Ejemplo              |
|---------|-------------|-------------------------------------------------------|----------------------|
| date    | `YYYY-MM-DD` | Fecha del registro en formato estándar ISO 8601       | `2025-09-24`         |
| partner | `string`     | Nombre del socio/cliente/proveedor                    | `"Acme Corp"`        |
| amount  | `float (EUR)`| Monto de la transacción en euros, con decimales (.)   | `1234.56`            |

---

## Mapeos Origen → Canónico

| Origen (CSV)      | Campo Origen       | Campo Canónico | Transformación / Nota                          |
|-------------------|-------------------|----------------|-----------------------------------------------|
| ventas_2023.csv   | `fecha`           | `date`         | Convertir a `YYYY-MM-DD`                      |
| ventas_2023.csv   | `cliente`         | `partner`      | Normalizar a minúsculas, sin tildes            |
| ventas_2023.csv   | `importe_euros`   | `amount`       | Asegurar `float` con `.` como separador        |
| pagos.xls         | `payment_date`    | `date`         | Convertir `dd/mm/yyyy` → `YYYY-MM-DD`         |
| pagos.xls         | `supplier_name`   | `partner`      | Homologar naming y trimming espacios           |
| pagos.xls         | `value`           | `amount`       | Convertir de `string` a `float` en EUR        |

> ⚠️ Nota: se recomienda documentar **cualquier nuevo mapeo** en esta tabla, ampliando los casos según crezcan los orígenes de datos.

