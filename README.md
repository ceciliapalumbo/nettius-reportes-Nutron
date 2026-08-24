# Pipeline mensual de reportes Nettius

Automatiza las tablas custom de Looker Studio y genera el análisis mensual. La IA se usa
exclusivamente para redactar seis párrafos a partir de un JSON ya calculado. Extracción,
ownership, KPIs y escritura son determinísticos.

## Reglas implementadas

- Metricool **no se consulta por API**: el pipeline lee sus exports CSV cargados en Google Sheets.
- Los KPIs de cuenta se conservan completos.
- Las tablas de Instagram, LinkedIn y YouTube incluyen solo contenido identificado en Monday.
- Monday se usa solo para ownership: subitems cuyo nombre comienza con `Publicar`.
- El cruce usa ID/link normalizado; `fecha + red` solo se habilita para una fila de Monday sin link
  o al configurar explícitamente `clave_cruce: fecha_red`. El fallback queda registrado en logs.
- Seguidores orgánicos atribuibles a Nettius se leen de `Manual_Meta`, columnas `mes, organicos`.
- Nuevos seguidores = orgánicos manuales + seguidores de campaña del export de Meta Ads.
- Si falta el dato manual, la ejecución termina con código 2 antes de escribir resultados.

## Flujo

1. `extract/metricool.py` lee y normaliza los cinco exports desde Sheets.
2. `extract/monday.py` pagina el board, descubre columnas y obtiene subitems `Publicar`.
3. `transform/ownership.py` filtra las tablas de contenido.
4. `transform/metrics.py` calcula el JSON y `run_month.py` lo valida contra el schema.
5. `sheets/writer.py` limpia y reescribe cada pestaña conservando encabezados vacíos.
6. `narrative/generate.py` solicita exactamente seis párrafos a `gpt-4o-mini`.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.yaml config.nutron.yaml
```

Completar en `config.nutron.yaml`:

- `google_sheet.spreadsheet_id` de la Sheet que consume Looker.
- `spreadsheet_id`, `worksheet` y, si difieren, los encabezados de cada export.
- El `board_id` de Monday. El valor inicial es `18404527148`, pendiente de confirmar.

Los patrones de pestaña admiten `{mes}`, `{desde}` y `{hasta}`. Por ejemplo, para agosto:
`instagram-posts_{desde}_{hasta}_contenidos` se convierte en
`instagram-posts_2026-08-01_2026-08-31_contenidos`.

### Credenciales locales

Crear `.env` sin commitearlo:

```dotenv
MONDAY_TOKEN=...
GOOGLE_SERVICE_ACCOUNT_JSON=/ruta/service-account.json
OPENAI_API_KEY=...
```

`GOOGLE_SERVICE_ACCOUNT_JSON` acepta tanto una ruta local como el JSON completo. Compartir todas
las Sheets de entrada y salida con el `client_email` de la service account.

## Configuración de columnas

Los alias más frecuentes en español, portugués e inglés ya están incluidos. Si un encabezado
real difiere, declararlo sin cambiar Python:

```yaml
metricool:
  exports:
    instagram_posts:
      spreadsheet_id: "ID"
      worksheet: "{mes}"
      columns:
        link: "Enlace permanente"
        fecha: "Data"
        titulo: "Conteúdo"
        alcance: "Alcance total"
        impresiones: "Impressões"
        interacciones: "Interações"
```

Para KPIs con varias filas diarias, `seguidores` usa el último valor y las métricas del periodo
usan suma. Se puede sobrescribir con `aggregation` (`sum`, `last`, `max`, etc.).

## Carga manual obligatoria

La pestaña configurada como `dato_manual` debe contener:

| mes | organicos |
|---|---:|
| 2026-08 | 42 |

No debe incluir los seguidores de campaña: esos se suman desde el export de Meta Ads.

## Ejecución

Producción:

```bash
python -m src.run_month --cliente nutron --mes 2026-08
```

Demo end-to-end sin credenciales; escribe CSV y `metrics.json` en `output/demo/`:

```bash
python -m src.run_month --cliente nutron --mes 2026-08 --demo
```

Pruebas:

```bash
pytest -q
```

## Pestañas escritas

- `IG_Contenido_Nettius`
- `LinkedIn_Contenido_Nettius`
- `YouTube_Nettius`
- `MetaAds_Campanhas`
- `Consolidados`
- `Analise_Texto` (filas 1 a 6)

La escritura es idempotente: cada corrida reemplaza el contenido de las pestañas, pero conserva
sus encabezados incluso cuando no haya datos.

## GitHub Actions

`.github/workflows/reporte-mensual.yml` corre el día 1 a las 09:00 UTC usando el mes anterior.
También permite ejecución manual con `cliente` y `mes`.

Configurar en **Settings → Secrets and variables → Actions**:

- `MONDAY_TOKEN`
- `GOOGLE_SERVICE_ACCOUNT_JSON` (contenido completo del JSON)
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY` solamente si se cambia el proveedor a Anthropic

Los IDs y nombres de pestañas no son secretos y viven en `config.nutron.yaml`.

## NEEDS_INPUT pendientes para producción

1. Confirmar que `18404527148` es el board que contiene los subitems `Publicar`.
2. Completar IDs y pestañas reales de los cinco exports y de la Sheet de salida.
3. Pegar los encabezados reales para confirmar los mapeos de `columns`.
4. Confirmar si `account_kpis` trae una fila mensual o series diarias y ajustar `aggregation`.
5. Confirmar la columna exacta del export Meta Ads que representa seguidores de campaña.

No se requieren tokens de Metricool, Meta Ads ni YouTube.
