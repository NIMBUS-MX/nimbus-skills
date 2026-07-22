# Report spec — "Transformación con IA — CIDCA"

Language: **Spanish**. Audience: founder / finance (non-technical). Tone: MVP/startup,
concrete, honest. Build from `ai_metrics.json` (embedded verbatim).

## Section order
1. **Encabezado** — título, subtítulo con la ventana de fechas y el costo del plan
   ($200/mes compartido desde 13-abr-2026), fecha de generación.
2. **Resumen ejecutivo (KPI row)** — 4–5 tiles grandes: Commits, Líneas de código
   añadidas, Features enviados a preprod, PRs mergeados, Contribuidores. Cada tile
   muestra el valor "Después" y el delta % vs "Antes".
3. **La foto: Antes vs Después** — tabla + barras agrupadas de las métricas clave
   (commits, líneas +, features, fixes) en las dos ventanas iguales.
4. **Ritmo semanal** — line/area chart de commits por semana (timeline), con una
   línea vertical marcando el 13-abr (inicio del plan Max).
5. **Dónde se produjo** — barras por repo activo (commits + líneas), y el desglose
   del monorepo por subproyecto (Backend / Frontend / iOS).
6. **Legacy → Monorepo** — una nota + mini-visual de cómo los repos legacy
   (ecg_auto, ecg-ui) se apagaron al consolidarse en `cidca-platform`.
7. **Calidad** — adopción de Conventional Commits (%), razón feat:fix, y la
   distribución de tipos de commit (feat/fix/refactor/test/docs/chore).
8. **El caso de reembolso** — párrafo corto: costo ($200/mes × meses) vs. output
   (features, PRs, líneas); enmarcar como "lo pagamos de nuestra bolsa".
9. **Metodología y datos crudos** — bullets de metodología (ver SKILL) + la tabla
   por repo completa. Nota: "Datos reales de git/gh, sin datos inventados."

## KPI formulas (all from ai_metrics.json)
- delta% = round(100*(after-before)/before) ; if before==0 → "nuevo".
- "Líneas de código" = totals.after.insertions (churn con generados excluidos).
- "Features a preprod" = max(totals.after.features, totals.after.merged_prs) —
  usa el mayor y explica ambos ("94 commits feat / 127 PRs mergeados").
- Razón feat:fix = after.features / after.fixes.

## Charts (inline SVG via vanilla JS reading the embedded JSON — NO external libs)
- **Grouped bars** Antes vs Después (4 series).
- **Area/line** commits por semana (x = weeks[], y = sum over active repos of
  weekly[week]); dashed vertical at `since`.
- **Horizontal bars** por repo (commits y líneas).
- **Stacked/segmented bar or small pie** de la distribución de tipos.
Colors: brand-neutral, accessible in light+dark (see dataviz skill palette). Never
color-only encoding for the legend — always label.

## Copy notes
- Convert relative dates to absolute (es-MX).
- Redondea números grandes con separador de miles.
- Un disclaimer honesto: la ventana "antes" también incluye trabajo del equipo sin
  IA intensiva; el salto NO es solo por la herramienta, pero el plan Max habilitó
  el ritmo. No sobre-vender.
