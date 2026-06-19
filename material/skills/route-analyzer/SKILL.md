---
name: befly-route-analyzer
description: Análise consolidada de uma rota BeFly. Use quando o usuário pedir "analise a rota X → Y", "como está a rota X", "performance da rota X", "olhar a rota X no último trimestre". Cruza operação, comercial, CX e manutenção em um único relatório executivo.
allowed-tools: mcp__plugin_databricks-ai-dev-kit_databricks__execute_sql, Read, Write
---

# BeFly Route Analyzer

Análise 360° de uma rota BeFly: operação + comercial + CX + frota.

## Quando usar

Quando o usuário disser qualquer variação de:
- "Analise a rota GRU → SSA"
- "Como está a performance de GIG → REC?"
- "Olha a rota X no último trimestre"
- "Como anda a rota X"

## Catálogo de dados

Todas as tabelas em `<seu_catalog>.befly_workshop`. Use estas (e somente estas):

| Tabela                     | Pra que serve                                  |
|----------------------------|------------------------------------------------|
| `silver_flights`           | Voos individuais, com `is_delayed_15`, `delay_reason`, `status`, `tail_number` |
| `silver_bookings`          | Receita por voo, `cabin`, `price_brl`          |
| `gold_daily_route_kpis`    | KPIs diários agregados                         |
| `gold_feedback_classified` | Feedbacks com sentimento, categoria, severidade|
| `silver_aircraft`          | Frota — `model`, `seats`, `year_in_service`    |
| `silver_maintenance`       | Eventos de manutenção (background, opcional) |

## Procedimento

1. **Parse o input** — extrair `ORIGIN`, `DESTINATION` (IATA 3 letras) e janela temporal (default: últimos 90 dias).
2. **Rodar 5 queries via `execute_sql`** (em paralelo se possível):

```sql
-- Q1: Operação
SELECT count(*) AS voos,
       round(100 * sum(is_delayed_15)/count(*), 1) AS pct_atraso,
       round(avg(delay_minutes), 1) AS atraso_medio_min,
       sum(is_cancelled) AS cancelamentos
FROM <seu_catalog>.befly_workshop.silver_flights
WHERE origin = '{ORIGIN}' AND destination = '{DESTINATION}'
  AND scheduled_departure >= add_months(current_timestamp(), -3);

-- Q2: Top motivos de atraso
SELECT delay_reason, count(*) AS qtd
FROM <seu_catalog>.befly_workshop.silver_flights
WHERE origin = '{ORIGIN}' AND destination = '{DESTINATION}'
  AND scheduled_departure >= add_months(current_timestamp(), -3)
  AND delay_reason != 'none'
GROUP BY 1 ORDER BY qtd DESC LIMIT 5;

-- Q3: Comercial
SELECT b.cabin,
       count(*) AS reservas,
       round(sum(b.price_brl), 2) AS receita_brl,
       round(avg(b.price_brl), 2) AS ticket_medio
FROM <seu_catalog>.befly_workshop.silver_bookings b
JOIN <seu_catalog>.befly_workshop.silver_flights f USING (flight_id)
WHERE f.origin = '{ORIGIN}' AND f.destination = '{DESTINATION}'
  AND f.scheduled_departure >= add_months(current_timestamp(), -3)
GROUP BY 1 ORDER BY receita_brl DESC;

-- Q4: CX
SELECT categoria, count(*) AS qtd, round(avg(severidade), 1) AS sev
FROM <seu_catalog>.befly_workshop.gold_feedback_classified g
JOIN <seu_catalog>.befly_workshop.silver_flights f USING (flight_id)
WHERE f.origin = '{ORIGIN}' AND f.destination = '{DESTINATION}'
  AND g.sentimento = 'negativo'
  AND g.booking_date >= add_months(current_date(), -3)
GROUP BY 1 ORDER BY qtd DESC LIMIT 5;

-- Q5: Frota usada na rota
SELECT a.model,
       count(distinct f.flight_id) AS voos
FROM <seu_catalog>.befly_workshop.silver_flights f
JOIN <seu_catalog>.befly_workshop.silver_aircraft a USING (tail_number)
WHERE f.origin = '{ORIGIN}' AND f.destination = '{DESTINATION}'
GROUP BY a.model;
```

3. **Sintetize** num markdown nesta estrutura exata:

```markdown
# Rota {ORIGIN} → {DESTINATION} — últimos 90 dias

## Operação
- **{voos}** voos · pontualidade **{100-pct_atraso}%** · **{cancelamentos}** cancelados
- Atraso médio: **{atraso_medio_min} min**
- Top motivos: {lista Q2}

## Comercial
- Receita: **R$ {receita_total}** · ticket médio: **R$ {ticket_medio}**
- Mix: {% Economy / Economy+ / Business}

## CX — reclamações
- {top 3 categorias com qtd e severidade média}

## Frota
- Modelos operando: {Q5}

## Recomendações (3 bullets)
- {Ação 1 — sempre acionável, e.g. "Se pct_atraso > 25% e top motivo for atc, escalar com aeroporto"}
- {Ação 2}
- {Ação 3}
```

## Regras

- Sempre formate BRL como `R$ X.XXX,XX`.
- Se a rota retornar 0 voos, diga "rota não operada no período" e pare.
- Não invente recomendações — baseie nos dados retornados.
- Se a janela temporal for diferente de 90 dias, ajuste todas as queries.
