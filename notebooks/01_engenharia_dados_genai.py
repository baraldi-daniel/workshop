# Databricks notebook source
# MAGIC %md
# MAGIC # 01 — Engenharia de dados (Lakeflow Designer)
# MAGIC
# MAGIC **14:10 – 15:05 · Hands-on · execução no Lakeflow Designer**
# MAGIC
# MAGIC Você vai criar **2 pipelines** separadas no Designer:
# MAGIC
# MAGIC - **Pipeline 1 — Bronze:** 5 Sources lendo CSVs + 5 Outputs → 5 tabelas `bronze_*`
# MAGIC - **Pipeline 2 — Gold:** 5 SQLs + 5 Outputs (silvers) **e** 1 SQL com `ai_query` Opus + 1 Output (gold tickets) — tudo num mesmo job
# MAGIC
# MAGIC Outras AI capabilities em arquivos próprios:
# MAGIC - `01b_ai_search.md` — Vector Search sobre `gold_tickets_structured`
# MAGIC - `01c_document_parsing_agent.md` — `ai_parse_document` em PDF
# MAGIC - `01d_vision_baggage.py` — vision multimodal em fotos

# COMMAND ----------

# MAGIC %md
# MAGIC ## Operadores do Designer
# MAGIC
# MAGIC | Operador | Pra que serve |
# MAGIC |---|---|
# MAGIC | **Source** | Lê CSV do volume (temp view) |
# MAGIC | **SQL** | Custom SQL — também pode ser standalone com `read_files`/`FROM <catalog>.<table>` |
# MAGIC | **Output** | **Materializa em tabela Delta** — terminal, nada conecta depois |
# MAGIC
# MAGIC ## 📌 Regras
# MAGIC
# MAGIC 1. **Output é terminal.** Pra encadear camadas, faça 2 pipelines separadas. Pipeline 2 lê via SQL standalone `FROM <catalog>.<schema>.bronze_*`.
# MAGIC 2. **Sem Output não vira tabela.** Source e SQL sozinhos são temp views do pipeline.
# MAGIC 3. **Vários Outputs num mesmo pipeline.** Cada SQL+Output materializa uma tabela. Pipeline 2 tem 6 pares (5 silver + 1 gold).

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pipeline 1 — Bronze
# MAGIC
# MAGIC **+ New → Visual data prep**
# MAGIC - Name: `befly_bronze_<seu_slug>`
# MAGIC - Destination: `<seu_catalog>` / `befly_<seu_slug>`
# MAGIC - Compute: Serverless → **Create**
# MAGIC
# MAGIC ### Adicionar 5 Sources + 5 Outputs
# MAGIC
# MAGIC Pra cada CSV: drag **Source** + drag **Output** depois.
# MAGIC
# MAGIC | # | Source (renomeie) | Path no volume | Output (table) |
# MAGIC |---|---|---|---|
# MAGIC | 1 | `src_support_tickets` | `support_tickets.csv` | `bronze_support_tickets` |
# MAGIC | 2 | `src_flights`         | `flights.csv`         | `bronze_flights` |
# MAGIC | 3 | `src_bookings`        | `bookings.csv`        | `bronze_bookings` |
# MAGIC | 4 | `src_customers`       | `customers.csv`       | `bronze_customers` |
# MAGIC | 5 | `src_airports`        | `airports.csv`        | `bronze_airports` |
# MAGIC
# MAGIC Format: CSV (header). Em cada Output: Catalog = `<seu_catalog>`, Schema = `befly_<seu_slug>`, Table name = `bronze_*`.
# MAGIC
# MAGIC **Publish + Start** → 5 tabelas `bronze_*` materializadas em ~1 min.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pipeline 2 — Gold
# MAGIC
# MAGIC **+ New → Visual data prep**
# MAGIC - Name: `befly_gold_<seu_slug>`
# MAGIC - Mesmo destination
# MAGIC - Serverless → **Create**
# MAGIC
# MAGIC ### Parte A — 5 Silvers (SQL + Output cada)
# MAGIC
# MAGIC Pra cada bronze materializado: drag **SQL** (standalone) + drag **Output**.
# MAGIC
# MAGIC | # | SQL node (renomeie) | Query | Output (table) |
# MAGIC |---|---|---|---|
# MAGIC | 1 | `tr_support_tickets` | `SELECT * FROM <seu_catalog>.befly_<seu_slug>.bronze_support_tickets` | `silver_support_tickets` |
# MAGIC | 2 | `tr_flights`         | `SELECT * FROM <seu_catalog>.befly_<seu_slug>.bronze_flights`         | `silver_flights` |
# MAGIC | 3 | `tr_bookings`        | `SELECT * FROM <seu_catalog>.befly_<seu_slug>.bronze_bookings`        | `silver_bookings` |
# MAGIC | 4 | `tr_customers`       | `SELECT * FROM <seu_catalog>.befly_<seu_slug>.bronze_customers`       | `silver_customers` |
# MAGIC | 5 | `tr_airports`        | `SELECT * FROM <seu_catalog>.befly_<seu_slug>.bronze_airports`        | `silver_airports` |
# MAGIC
# MAGIC ### Parte B — Gold com `ai_query` (Opus 4.8) ⭐
# MAGIC
# MAGIC Mais 1 par no mesmo pipeline: drag **SQL** + drag **Output**.
# MAGIC
# MAGIC - **SQL node:** `tr_ai_tickets`
# MAGIC - **Query** (cole inteira):
# MAGIC
# MAGIC ```sql
# MAGIC SELECT
# MAGIC   ticket_id, marca, canal, customer_id, received_at, mensagem,
# MAGIC   ai_query(
# MAGIC     'databricks-claude-opus-4-8',
# MAGIC     CONCAT('Retorne APENAS um JSON válido (sem markdown, sem texto extra) com as chaves: intent, urgencia, sentimento, destino, orcamento_brl, resumo_pt. Mensagem: "', mensagem, '"')
# MAGIC   ) AS analise
# MAGIC FROM <seu_catalog>.befly_<seu_slug>.bronze_support_tickets
# MAGIC ```
# MAGIC
# MAGIC - **Output:** `gold_tickets_structured`
# MAGIC
# MAGIC > Validado no Designer — `ai_query()` inline dentro do SQL operator funciona. O operador **AI Function** tem limitações no form (não aceita `CONCAT(...)` no Request, sem campo de alias da saída), então preferimos SQL.
# MAGIC
# MAGIC **Publish + Start** → 6 tabelas materializadas (`silver_*` × 5 + `gold_tickets_structured`).

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Checkpoint
# MAGIC
# MAGIC No Catalog → `<seu_catalog>.befly_<seu_slug>` deve ter **11 tabelas**:
# MAGIC
# MAGIC **5 bronze:** bronze_support_tickets, bronze_flights, bronze_bookings, bronze_customers, bronze_airports
# MAGIC
# MAGIC **5 silver:** silver_support_tickets, silver_flights, silver_bookings, silver_customers, silver_airports
# MAGIC
# MAGIC **1 gold:** gold_tickets_structured (1.500 linhas com coluna `analise` JSON via Opus 4.8)
# MAGIC
# MAGIC ### Validar gold rapidinho (SQL Editor)
# MAGIC
# MAGIC ```sql
# MAGIC SELECT
# MAGIC   ticket_id,
# MAGIC   marca,
# MAGIC   get_json_object(analise, '$.intent')     AS intent,
# MAGIC   get_json_object(analise, '$.urgencia')   AS urgencia,
# MAGIC   get_json_object(analise, '$.sentimento') AS sentimento,
# MAGIC   get_json_object(analise, '$.resumo_pt')  AS resumo
# MAGIC FROM <seu_catalog>.befly_<seu_slug>.gold_tickets_structured
# MAGIC LIMIT 20
# MAGIC ```
# MAGIC
# MAGIC ## Próximos
# MAGIC
# MAGIC - **`01b_ai_search.md`** → Vector Search sobre `gold_tickets_structured`
# MAGIC - **`01c_document_parsing_agent.md`** → `ai_parse_document`
# MAGIC - **`01d_vision_baggage.py`** → vision em fotos
# MAGIC - **`02_machine_learning.py`** → ML
