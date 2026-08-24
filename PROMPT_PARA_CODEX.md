# Prompt para pegar en ChatGPT Codex

Copiá TODO lo de abajo (entre las líneas) y pegalo en Codex, junto con los archivos de este repo (`README.md`, `config.example.yaml`, `schemas/metrics.schema.json` y la carpeta `src/`). Codex tiene que **completar los `# TODO(codex)` y dejar el pipeline corriendo end-to-end.**

---

Sos un ingeniero de datos. Te paso un repo prototipo (`nettius_reportes/`) que automatiza los reportes mensuales de redes de la agencia Nettius en Looker Studio. Leé `README.md` primero: tiene la arquitectura, las reglas de negocio y el contrato de datos. **Respetá esas reglas al pie de la letra**, en especial:

- Las tablas de **contenido** muestran **solo lo de Nettius**; la propiedad se decide por **join contra Monday** (lookup, nunca por criterio de un modelo).
- Los **KPIs de cuenta** van completos (no se filtran).
- **YouTube** también se filtra a solo-Nettius (mismos videos que están en Monday).
- Los **seguidores orgánicos de IG** son **carga manual** (una celda de la Sheet), no vienen por API.
- La IA solo se usa para el **texto del análisis** (capa 5), con un modelo barato. Todo lo demás es determinístico.

Tu tarea, en orden:

**IMPORTANTE — Metricool SIN API:** el plan de Metricool NO tiene API. Los datos de redes ya
entran a Looker por el conector de Metricool (páginas de canal se refrescan solas). Para lo que
el pipeline procesa, se leen los **exports CSV de Metricool cargados en Google Sheets** (hoy ya
se hace a mano, ej: `instagram-posts_2026-08-01_..._contenidos`). NO uses la API de Metricool.

1. **Completá los extractores** (`src/extract/*.py`):
   - `metricool.py`: completá el lector de exports (Google Sheets) y el mapeo de columnas
     (`MAP_POSTS` y los `# NEEDS_INPUT`) para `fetch_posts` (IG/LinkedIn), `fetch_account_kpis`,
     `fetch_youtube` y `fetch_meta_ads`. Todo desde las Sheets de export, no desde API.
   - `youtube.py` / `meta_ads.py`: ya delegan en `metricool.py`; dejalos así.
   - `monday.py`: GraphQL al board de Nettius → lista de publicaciones del mes con link/ID, fecha
     y red. **Solo se usa para decidir propiedad**, no para métricas.
   - Recordá: los **seguidores orgánicos** son carga manual (celda de la Sheet), no salen por API.
2. **Verificá el join de propiedad** (`src/transform/ownership.py`): tiene que cruzar posts de Metricool y videos de YouTube contra la lista de Monday por link/ID (fallback: fecha+red) y devolver solo lo de Nettius. Escribí tests con casos borde (post sin link, fecha desfasada, item de la otra agencia).
3. **Verificá el cálculo** (`src/transform/metrics.py`): que la salida cumpla `schemas/metrics.schema.json`. Nuevos seguidores = orgánicos (celda manual) + de campaña (API).
4. **Escribí a la Google Sheet de trabajo** (`src/sheets/writer.py`) con la service account: una pestaña por tabla que consume Looker + una pestaña de consolidados. Idempotente (reescribe, no duplica).
5. **Narrativa** (`src/narrative/generate.py`): llamá al modelo barato configurado (Claude Haiku o GPT-4o-mini) con el `metrics.json` + la plantilla fija de 6 puntos. Devolvé los párrafos y escribilos en la pestaña de análisis de la Sheet.
6. **Orquestador** (`src/run_month.py`): que corra las 5 capas para `--cliente` y `--mes`, con logging claro, reintentos en las llamadas de red, y que si falta el dato manual de Meta lo pida y frene con un mensaje claro.
7. **Scheduler**: generá `.github/workflows/reporte-mensual.yml` (cron mensual + `workflow_dispatch`) y documentá qué secrets de GitHub hay que cargar.
8. **Tests + README de uso**: `pytest` para el join y el cálculo con datos de ejemplo (fixtures), e instrucciones para correr un mes localmente.

Entregá el código completo, corriendo, con manejo de errores y sin claves hardcodeadas. Donde una decisión dependa de info que no tengo (plan de Metricool, estructura del board de Monday, etc.), dejá el punto marcado con `# NEEDS_INPUT:` y una pregunta concreta, y usá un stub razonable para que el resto compile y corra con datos de ejemplo.

---
