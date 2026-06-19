# 04 — Genie Space (perguntas em linguagem natural)

**15:55 – 16:15 · Hands-on**

## 1. Criar a Space

Sidebar → **Genie** → **New**:
- **Name:** `BeFly (<seu_slug>)`
- **SQL warehouse:** serverless padrão

## 2. Add data

Click **Add data** → seleciona **1 tabela**: `<seu_catalog>.befly_<seu_slug>.gold_tickets_structured`

## 3. Instructions

```
Esta Genie Space responde perguntas sobre chamados de CX da BeFly.

A coluna `analise` é STRING JSON — use get_json_object(analise, '$.intent'),
'$.urgencia', '$.sentimento', '$.destino', '$.orcamento_brl', '$.resumo_pt'.

NUNCA exponha email/PII do customer.
```

## 4. Sample query

```sql
SELECT get_json_object(analise, '$.intent') AS intent, count(*) AS qtd
FROM gold_tickets_structured
GROUP BY 1 ORDER BY qtd DESC LIMIT 10
```

## 5. Save e teste

Perguntas pra fazer no chat:

1. *"Quais os principais intents dos chamados?"*
2. *"Distribuição de sentimento por marca"*
3. *"Chamados com urgência alta"* (follow-up)

Próximo: **Genie One**.
