# Crear la página de YouTube en el reporte (paso puntual de Looker)

La página de YouTube **todavía no existe** en el reporte de Nutron. Esto es un paso de Looker
(no del pipeline). Se puede hacer ahora para agosto, y una vez que el pipeline corre, la misma
página se alimenta sola desde la pestaña `YouTube_Nettius` de la Google Sheet.

## Fuente de datos
- **Hoy (agosto, a mano):** la Sheet de YouTube del reporte (`Métricas TY Nutron`, versión agosto).
  Requisito: que traiga solo los videos de Nettius (los que están en Monday). Si trae todo el
  canal, hay que filtrarla (ver más abajo).
- **Con el pipeline (a futuro):** la pestaña `YouTube_Nettius`, que ya sale filtrada a Nettius.

## Diseño de la página
- Encabezado con logo de YouTube (en línea con las otras redes).
- Scorecards: **Visualizações totais · Nº de vídeos · Nº de Shorts**.
- Tabla: **Título · Data · Tipo (vídeo/short) · Visualizações · Link**.
- Rango de fechas = mes del reporte (agosto).

## Instrucción para pegar en el Claude del panel de Chrome

> En el reporte "Nutron Brasil Agosto" (Looker, modo Editar), creá una página nueva llamada
> **"YouTube"** (dentro del grupo NUTRON BRASIL, junto a las otras redes) y armá:
> 1. Una tabla usando la fuente de datos de YouTube del reporte (la Sheet `Métricas TY Nutron`).
>    Columnas: **Título, Data, Tipo, Visualizações, Link**. Ordená por Visualizações desc.
> 2. Tres scorecards arriba: total de **Visualizações**, cantidad de **vídeos**, cantidad de **Shorts**.
> 3. Poné el rango de fechas de la página en **agosto 2026**.
> 4. Si la Sheet trae videos que NO son de Nettius (de la otra agencia), avisame — hay que
>    filtrarla contra la lista de Monday y todavía no está resuelto ese cruce.
> Decime cuántos videos/shorts quedaron y si la fuente ya venía solo con contenido de Nettius.

## Pendiente para confirmar con el equipo
- ¿La Sheet `Métricas TY Nutron` ya viene solo con videos de Nettius, o con todo el canal?
  - Si **solo Nettius** → la página queda lista tal cual.
  - Si **todo el canal** → hay que filtrar por la lista de Monday (mismo join que el pipeline).
- Falta cargar la versión de **agosto** de esa Sheet (hoy dice "Julio").
