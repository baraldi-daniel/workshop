# Databricks notebook source
# MAGIC %md
# MAGIC # 01d — Vision: análise de fotos de bagagem
# MAGIC
# MAGIC **Opcional · pós-pipeline**
# MAGIC
# MAGIC Modelo multimodal (`databricks-claude-sonnet-4`) lendo imagens reais de bagagem perdida/danificada e extraindo JSON estruturado: tipo de dano, severidade, descrição em PT, flag de reembolso.
# MAGIC
# MAGIC **Run all** depois de configurar os widgets.

# COMMAND ----------

dbutils.widgets.text("catalog", "catalog_baraldi", "Catalog (mesmo do 00_setup)")
dbutils.widgets.text("user_slug", "dan001", "Seu slug (mesmo do 00_setup)")
CATALOG = dbutils.widgets.get("catalog").strip()
USER_SLUG = dbutils.widgets.get("user_slug").strip().lower()
SCHEMA = f"befly_{USER_SLUG}"
spark.sql(f"USE {CATALOG}.{SCHEMA}")
print(f"Working in {CATALOG}.{SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Dados
# MAGIC
# MAGIC 8 fotos reais em `/Volumes/<catalog>/<schema>/raw/baggage_claims/` (CC0 Unsplash). Confere:

# COMMAND ----------

display(spark.sql(f"LIST '/Volumes/{CATALOG}/{SCHEMA}/raw/baggage_claims/'"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Processar as 8 imagens com vision
# MAGIC
# MAGIC `ai_query` com `files => content` (binary direto — sem array/base64/named_struct).

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE gold_baggage_claims AS
# MAGIC SELECT
# MAGIC   path,
# MAGIC   regexp_extract(path, 'claim_([^.]+)\\.jpg$', 1) AS claim_id,
# MAGIC   ai_query(
# MAGIC     'databricks-claude-sonnet-4',
# MAGIC     'Analise a foto de bagagem. Retorne APENAS um JSON válido com as chaves: tipo_dano (string), severidade (int 1-5), objetos_visiveis (array de string), descricao_pt (string), requer_reembolso (bool). Sem markdown, sem texto extra.',
# MAGIC     files => content
# MAGIC   ) AS analise
# MAGIC FROM read_files(
# MAGIC   '/Volumes/${catalog}/befly_${user_slug}/raw/baggage_claims/',
# MAGIC   format => 'binaryFile'
# MAGIC )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Estruturar e ranquear por severidade

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   claim_id,
# MAGIC   get_json_object(analise, '$.tipo_dano')        AS tipo_dano,
# MAGIC   CAST(get_json_object(analise, '$.severidade') AS INT) AS severidade,
# MAGIC   get_json_object(analise, '$.descricao_pt')     AS descricao,
# MAGIC   CAST(get_json_object(analise, '$.requer_reembolso') AS BOOLEAN) AS reembolso,
# MAGIC   get_json_object(analise, '$.objetos_visiveis') AS objetos
# MAGIC FROM gold_baggage_claims
# MAGIC ORDER BY severidade DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Checkpoint
# MAGIC
# MAGIC Tabela `gold_baggage_claims` no schema com 8 linhas. Coluna `analise` (STRING JSON) + `claim_id` (extraído do path).
