# Gobierno y Gobernanza de Datos

## Origen y Linaje
- Todo dataset debe documentar:
  - Fuente original (archivo, sistema, proveedor).
  - Fecha y método de ingesta.
  - Transformaciones aplicadas (ingesta → Bronze → Silver).
- Se debe mantener un registro auditable de cada paso para garantizar la trazabilidad.

## Validaciones Mínimas
- **Formato de fecha**: cumplir con ISO 8601 (`YYYY-MM-DD`).
- **Partner**: no nulo, string limpio sin caracteres ilegales.
- **Amount**: numérico, mayor o igual a 0, en euros.
- **Duplicados**: eliminación o señalización explícita.
- **Valores faltantes**: documentar y tratar según políticas (ej. imputación o exclusión).

## Política de Mínimos Privilegios
- Acceso a **datos crudos (Bronze)** restringido a ingenieros de datos.  
- **Silver/Gold** accesibles solo a perfiles autorizados de analítica.  
- Cuentas de servicio separadas para ingesta, validación y visualización.  
- No compartir credenciales en repositorios o código.

## Trazabilidad
- Uso de logs en cada fase del pipeline.  
- Metadatos obligatorios:
  - Quién generó el dataset.
  - Cuándo se generó.
  - Transformaciones aplicadas.  
- Identificación única de cada versión de dataset.

## Roles
- **Data Engineer**: ingesta, validación, normalización, mantenimiento del pipeline.  
- **Data Steward**: supervisión de la calidad de datos, actualización del diccionario y gobierno.  
- **Data Analyst**: consumo de capas Silver/Gold, creación de KPIs.  
- **Administrador**: gestión de accesos y cumplimiento de la política de mínimos privilegios.  

