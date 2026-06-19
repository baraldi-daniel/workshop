---
name: befly-feedback-triage
description: Triagem priorizada de feedbacks negativos recentes da BeFly. Use quando o usuário pedir "triagem de reclamações", "feedbacks críticos da semana", "olhar reclamações severas", "priorize as queixas dos passageiros". Cruza severidade + tier do cliente + contexto do voo e propõe resposta personalizada.
allowed-tools: mcp__plugin_databricks-ai-dev-kit_databricks__execute_sql, Read, Write
---

# BeFly Feedback Triage

Lê os feedbacks negativos críticos, prioriza, e gera uma lista pronta pro time de CX agir.

## Quando usar

- "Triagem de reclamações da última semana"
- "Quais feedbacks críticos preciso responder hoje?"
- "Priorize as queixas dos passageiros Diamond"
- "Olha as reclamações severas"

## Parâmetros (default em parênteses)

- `dias` — janela em dias (7)
- `severidade_min` — severidade mínima (4)
- `top_n` — quantos casos retornar (10)

## Passo 1 — Buscar candidatos

```sql
SELECT
  g.booking_id, g.flight_id, g.customer_id, g.booking_date,
  g.categoria, g.severidade, g.feedback_text, g.cabin,
  c.name AS cliente, c.loyalty_tier, c.email,
  f.origin, f.destination, f.scheduled_departure, f.delay_minutes, f.status, f.delay_reason
FROM <seu_catalog>.befly_workshop.gold_feedback_classified g
LEFT JOIN <seu_catalog>.befly_workshop.silver_customers c ON c.customer_id = g.customer_id
LEFT JOIN <seu_catalog>.befly_workshop.silver_flights f USING (flight_id)
WHERE g.sentimento = 'negativo'
  AND g.severidade >= {severidade_min}
  AND g.booking_date >= date_sub(current_date(), {dias})
ORDER BY
  CASE c.loyalty_tier WHEN 'Diamond' THEN 1 WHEN 'Gold' THEN 2 WHEN 'Silver' THEN 3 ELSE 4 END,
  g.severidade DESC,
  g.booking_date DESC
LIMIT {top_n};
```

## Passo 2 — Para cada feedback, decidir resposta

Use estes templates por categoria. Personalize com nome, número do voo e tier.

| Categoria         | Tom         | Template base                                                                                          |
|-------------------|-------------|--------------------------------------------------------------------------------------------------------|
| atraso            | Empático    | "Olá {Nome}, sentimos muito pelo atraso do voo {Voo}. Sabemos que seu tempo é precioso..."             |
| bagagem           | Resolutivo  | "Olá {Nome}, recebemos seu relato sobre a bagagem do voo {Voo}. Já abrimos o protocolo {PROTO}..."     |
| atendimento       | Pessoal     | "Olá {Nome}, lamentamos a experiência. Estamos investigando internamente e gostaríamos de conversar..."|
| aeronave          | Técnico     | "Olá {Nome}, agradecemos o relato sobre o voo {Voo}. Encaminhamos para a equipe técnica..."           |
| preco             | Comercial   | "Olá {Nome}, entendemos sua frustração. Gostaríamos de oferecer um cupom para sua próxima viagem..."   |

**Diamond/Gold** sempre recebem oferta de compensação (milhas ou voucher) — Silver/Bronze recebem desculpa formal.

## Passo 3 — Output

Markdown nesta estrutura:

```markdown
# Triagem de feedbacks — {hoje}
**{N} casos**, severidade ≥ {severidade_min}, últimos {dias} dias

---

## #1 — {Nome} ({Tier})  ·  Severidade {sev}/5
**Voo:** {origin} → {dest}  ·  {data}  ·  atraso {delay_min}min
**Categoria:** {categoria}
**Feedback:** "{feedback_text}"

**Resposta sugerida:**
> {texto personalizado}

**Ação interna:** {abrir protocolo / escalar / nada}

---

## #2 ...
```

## Regras

- Nunca invente protocolo numérico — use "{PROTO}" pro time preencher.
- Se `delay_minutes` for null → não mencione atraso na resposta.
- Diamond/Gold devem aparecer primeiro, mesmo com severidade ligeiramente menor que Silver.
- Se nenhum feedback bate o filtro, retorne "Sem casos críticos na janela — bom trabalho!" e pare.
- Não envie a resposta — só sugira o texto para o time de CX revisar.
