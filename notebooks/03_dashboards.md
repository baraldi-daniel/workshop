# 03 — Dashboards (AI/BI)

**15:35 – 15:55 · Hands-on**

## Prompt pro Genie Code (charts nativos)

> *Crie um dashboard AI/BI chamado `BeFly — Operações & CX (<seu_slug>)` em `<seu_catalog>.befly_<seu_slug>` com:*
>
> *- KPIs no topo: voos último mês, pontualidade %, receita BRL, # reclamações severidade ≥ 4*
> *- Bar horizontal: voos por região (silver_flights + silver_airports)*
> *- Bar stacked: distribuição de intent por marca (gold_tickets_structured — `analise` é STRING JSON, use `get_json_object(analise, '$.intent')`)*
>
> *Use paleta BeFly: navy #0A1F44, magenta #E5247A. Valide cada SQL antes de criar.*

## Adicionar 1 chart Vega-Lite manualmente (depois)

**Heatmap Rota × Dia da semana (% atraso)** — chart custom que não tem no widget nativo.

1. Aba **Data** → **+ Create dataset from SQL** → cole a query abaixo, nome `heatmap_rota_dow`, Save
2. Volta no Canvas → **Add visualization** → dataset `heatmap_rota_dow` → **Visualization type: Vega-Lite** → cole o spec

**Dataset:**
```sql
WITH top_routes AS (
  SELECT origin, destination, count(*) AS total
  FROM <seu_catalog>.befly_<seu_slug>.silver_flights
  WHERE status = 'COMPLETED'
  GROUP BY 1, 2 ORDER BY total DESC LIMIT 20
)
SELECT
  concat(f.origin, ' → ', f.destination) AS rota,
  dayofweek(to_timestamp(f.scheduled_departure)) AS dep_dow,
  round(100.0 * sum(CASE WHEN CAST(f.delay_minutes AS INT) >= 15 THEN 1 ELSE 0 END) / count(*), 1) AS pct_atraso
FROM <seu_catalog>.befly_<seu_slug>.silver_flights f
JOIN top_routes t USING (origin, destination)
WHERE f.status = 'COMPLETED'
GROUP BY 1, 2
```

**Spec:**
```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "mark": {"type": "rect", "stroke": "#FFFFFF", "strokeWidth": 1},
  "encoding": {
    "x": {
      "field": "dep_dow", "type": "ordinal",
      "title": "Dia da semana",
      "axis": {"labelExpr": "['', 'Dom','Seg','Ter','Qua','Qui','Sex','Sáb'][datum.value]"}
    },
    "y": {"field": "rota", "type": "nominal", "sort": "-x", "title": null},
    "color": {
      "field": "pct_atraso", "type": "quantitative",
      "scale": {"range": ["#FFFFFF", "#0A1F44", "#E5247A"]},
      "title": "% atraso"
    },
    "tooltip": [
      {"field": "rota", "title": "Rota"},
      {"field": "dep_dow", "title": "Dia"},
      {"field": "pct_atraso", "title": "% atraso", "format": ".1f"}
    ]
  },
  "config": {"font": "Poppins, Inter, system-ui", "background": "transparent", "view": {"stroke": "transparent"}}
}
```

Próximo: **Genie Space**.
