# Respuestas a las preguntas de Codex — pipeline Nettius (cliente base: Nutron)

Consolidado de todo lo definido. Pegale esto a Codex junto con el repo.

## 1. Metricool: SIN API
- El plan NO tiene API → NO usar la API de Metricool.
- Los datos se leen de los **exports CSV de Metricool ya cargados en Google Sheets**
  (ej. de fuente existente: `instagram-posts_2026-08-01_..._contenidos`).
- Las páginas de canal en Looker ya se refrescan solas por el conector de Metricool; los exports
  son solo para el join de propiedad + consolidados.
- PENDIENTE (lo completa el equipo/Claude leyendo el Looker): ids de las Sheets, patrón de
  pestañas por mes y nombres reales de columnas de cada export.

## 2. Propiedad del contenido (la regla más importante)
- Fuente de verdad: **board de Monday** `18404527148` ("Cliente NUTRON").
  [CONFIRMAR: el board con los grupos "Artigo - ..." y los subitems "Publicar" ¿es este mismo
  o es otro board? Si es otro, usar su board_id.]
- Las publicaciones de Nettius = **SUBITEMS (subelementos)** cuyo nombre **empieza con "Publicar"**
  (Publicar post / reel / carrusel / lanzamiento…). Ignorar los subitems "crear…" y "correr ads…".
- Cada "Publicar" tiene: **fecha** (columna Date) y **el/los link(s) del contenido publicado**.
- El contenido **sale en TODAS las redes** (Instagram, LinkedIn, …). No hay columna de red.
- **CRUCE (ownership): por LINK normalizado** — el link de la tarea "Publicar" de Monday debe
  matchear la URL del posteo en el export de Metricool. Como es por link, **NO importa que la otra
  agencia postee el mismo día** (solo entran los links que están en Monday).
- Si un "Publicar" tiene **un solo link** (una red), el resto de las redes del mismo contenido se
  toman como Nettius por ser el mismo item (mismo contenido, misma fecha).
- Refuerzo/alternativa: el **planificador de Metricool** (lo programado por Nettius) es otra fuente
  de verdad de propiedad.
- IMPORTANTE para la API de Monday: son **subitems**, no items de primer nivel → consultá
  `items { subitems { name column_values { ... } } }`. Podés **auto-descubrir los IDs de columnas
  por su título** (link/fecha/archivo) consultando el schema del board; no hace falta copiarlos a mano.

## 3. Decisiones cerradas
- Fallback de propiedad: **link normalizado** (principal) → fecha+tipo solo como fallback explícito
  y logueado. Nunca fecha sola como método principal.
- Shorts: usar el campo "tipo" del export de Metricool si viene; si no, duración ≤ 60s (configurable).
- Orgánicos: seguidores orgánicos **atribuidos a Nettius** (carga manual; pestaña [mes, organicos]).
- pct_crecimiento_nettius = organicos_nettius / nuevos_totales → correcto.
- Ranking de contenido: **interacciones absolutas** (principal), alcance como desempate.
- Narrativa: **OpenAI gpt-4o-mini**, **un párrafo por fila**.
- Tablas vacías en Looker: **conservar encabezados y tipos** (no escribir "(sin datos)").
- Cron: día 1, 09:00 UTC. Falla controlada si falta el dato manual de orgánicos (frenar antes de
  escribir). workflow_dispatch con campos `cliente` y `mes`. Primera config: solo `nutron`.

## 4. Credenciales (van en .env / GitHub Secrets, NUNCA en el chat)
- MONDAY_TOKEN, GOOGLE_SERVICE_ACCOUNT_JSON, OPENAI_API_KEY.
- board_id Monday: 18404527148 (o el que se confirme).
