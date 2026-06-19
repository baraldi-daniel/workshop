# 01b — AI Search (Vector Search) sobre chamados

**Opcional · pós-pipeline**

Vector Search não tem operador visual no Designer ainda — config é via **Catalog UI** + **SQL Editor**. Rode quando a tabela `gold_tickets_structured` já estiver materializada (do módulo 01 B.1).

## Cenário

"Mostra chamados parecidos com cliente Diamond que perdeu conexão em Lisboa." Filtros estruturados respondem perguntas exatas; Vector Search responde **similaridade semântica**.

---

## Passo 1 — Habilitar Change Data Feed (SQL Editor)

CDF é pré-requisito do delta-sync do Vector Search.

```sql
ALTER TABLE <seu_catalog>.befly_<seu_slug>.gold_tickets_structured
  SET TBLPROPERTIES (delta.enableChangeDataFeed = true);
```

Espera saída `OK`.

---

## Passo 2 — Criar o AI Search endpoint (compartilhado)

⚠️ **Só o primeiro participante cria** — os demais reutilizam o mesmo endpoint.

1. Sidebar esquerdo → **Compute** → aba **Vector Search**
2. Click **Create**
3. Preenche:
   - **Name:** `befly_workshop_vs`
   - **Type:** Standard
   - **Compute size:** Small (default)
4. **Create** → status fica `PROVISIONING` por 5-15 min até `READY`

> Dica: enquanto o endpoint provisiona, segue pro Passo 3 (criar index não precisa do endpoint pronto, só pra rodar query).

---

## Passo 3 — Criar SEU índice (cada participante)

1. Sidebar → **Catalog** → seu schema `befly_<seu_slug>` → click na tabela `gold_tickets_structured`
2. No header da tabela, click **Create** → **Vector Search index**
3. Modal de criação:

### Basics
- **Catalog:** `<seu_catalog>` (já preenchido)
- **Schema:** `befly_<seu_slug>` (já preenchido)
- **Index name:** `idx_tickets`
- **Primary key:** `ticket_id`

### Embeddings
- **Embedding source:** ✓ **Compute embeddings** (Databricks calcula sozinho)
- **Embedding source column:** `mensagem`

### Compute resources
- **AI Search endpoint:** `befly_workshop_vs` (selecione o que você criou no Passo 2 — pode levar alguns segundos pra aparecer na lista)
- **Index update mode:** ✓ **Triggered**

### Advanced settings (expanda)
- **Embedding model:** `databricks-gte-large-en` ← **essencial selecionar**
- **Columns to index:** deixe em branco (indexa tudo)
- **Budget policy:** Default
- **Use a separate embedding model for queries:** off

4. **Create** → o índice começa a sincronizar (1-5 min pros 1500 chamados)

Status fica visível em **Catalog → Vector Search → seu index**:
- `PROVISIONING` → ainda criando
- `ONLINE_NO_PENDING_UPDATE` → pronto pra query ✅

---

## Passo 4 — Testar busca semântica (SQL Editor)

```sql
SELECT ticket_id, mensagem, search_score
FROM vector_search(
  index => '<seu_catalog>.befly_<seu_slug>.idx_tickets',
  query => 'cliente Diamond perdeu conexão internacional após atraso',
  num_results => 5
)
```

Resultado: 5 chamados mais semanticamente próximos da pergunta, ordenados por `search_score`.

---

## Passo 5 — Busca híbrida (vector + filtro estruturado)

Combina embedding com a `analise` JSON do B.1:

```sql
SELECT
  v.ticket_id, v.search_score,
  v.mensagem,
  get_json_object(v.analise, '$.intent')    AS intent,
  get_json_object(v.analise, '$.urgencia')  AS urgencia
FROM vector_search(
  index => '<seu_catalog>.befly_<seu_slug>.idx_tickets',
  query => 'cobertura de seguro internacional para acidente',
  num_results => 20
) v
WHERE get_json_object(v.analise, '$.urgencia') IN ('alta', 'critica')
ORDER BY v.search_score DESC
```

---

## Pra que serve depois

O índice `idx_tickets` é a base pra agentes BeFly conseguirem perguntas tipo *"casos parecidos com X que viraram churn"* — algo que filtro estruturado sozinho não responde.
