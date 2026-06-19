# Databricks notebook source
# MAGIC %md
# MAGIC # 00 — Setup do seu workshop
# MAGIC
# MAGIC **Horário:** 14:00 – 14:10  ·  **Hands-on:** sim — você executa.
# MAGIC
# MAGIC Este notebook cria **seu schema isolado** e **seu volume com os dados** dentro do catalog escolhido, copiando os arquivos do **git folder** que você clonou.
# MAGIC
# MAGIC ## Pré-requisito (já feito se está vendo isso)
# MAGIC No workspace, você clonou o repo via:
# MAGIC **Workspace → Create → Git folder** → URL: `https://github.com/baraldi-daniel/workshop.git`
# MAGIC
# MAGIC ## O que esse notebook faz
# MAGIC 1. Pede seu `USER_SLUG` no widget
# MAGIC 2. Cria schema `<seu_catalog>.befly_<seu_slug>`
# MAGIC 3. Cria volume `raw`
# MAGIC 4. Copia 7 CSVs + 8 imagens + 1 PDF do git folder → volume
# MAGIC 5. Sanity check

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Configure SEU slug
# MAGIC
# MAGIC Formato: 3 letras + 3 dígitos (ex: `dan001`). **Anote** — você vai reutilizar nos próximos notebooks.

# COMMAND ----------

dbutils.widgets.text("catalog", "catalog_baraldi", "Catalog (pergunte ao facilitador)")
dbutils.widgets.text("user_slug", "dan001", "Seu slug (3 letras + 3 dígitos)")
USER_SLUG = dbutils.widgets.get("user_slug").strip().lower()

assert USER_SLUG.replace("_", "").isalnum() and len(USER_SLUG) <= 12, \
    "Slug deve ser alfanumérico até 12 chars."

CATALOG = dbutils.widgets.get("catalog").strip()
SCHEMA  = f"befly_{USER_SLUG}"
VOLUME_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/raw"

assert CATALOG, "Defina o widget 'catalog' no topo"
print(f"Catalog.schema:  {CATALOG}.{SCHEMA}")
print(f"Volume:          {VOLUME_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Criar schema + volume

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA} "
          f"COMMENT 'Workshop hands-on — {USER_SLUG}'")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {CATALOG}.{SCHEMA}.raw "
          f"COMMENT 'Dados do workshop'")
spark.sql(f"USE {CATALOG}.{SCHEMA}")
print("✓ Schema e volume criados")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Copiar dados do git folder → volume

# COMMAND ----------

import os, shutil

# Descobre a raiz do git folder a partir do path deste notebook
nb_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
# ex: /Users/<email>/workshop/notebooks/00_setup → /Workspace/Users/<email>/workshop
GIT_ROOT = "/Workspace" + nb_path.rsplit("/notebooks/", 1)[0]
DATA_DIR = f"{GIT_ROOT}/data"

print(f"Git folder root: {GIT_ROOT}")
print(f"Data dir:        {DATA_DIR}")
assert os.path.isdir(DATA_DIR), f"Não achei {DATA_DIR}. Você clonou o repo como Git folder?"

# COMMAND ----------

# Copia CSVs e PDF na raiz
copied = 0
for fname in os.listdir(DATA_DIR):
    src = f"{DATA_DIR}/{fname}"
    if os.path.isfile(src):
        dst = f"{VOLUME_PATH}/{fname}"
        shutil.copyfile(src, dst)
        size_kb = os.path.getsize(src) / 1024
        print(f"  ✓ {fname:30s} {size_kb:>8.1f} KB")
        copied += 1
print(f"\nCopiei {copied} arquivos pro volume.")

# COMMAND ----------

# Copia subpasta baggage_claims (8 JPGs)
sub = f"{DATA_DIR}/baggage_claims"
if os.path.isdir(sub):
    dbutils.fs.mkdirs(f"{VOLUME_PATH}/baggage_claims")
    n = 0
    for fname in os.listdir(sub):
        src = f"{sub}/{fname}"
        if os.path.isfile(src):
            shutil.copyfile(src, f"{VOLUME_PATH}/baggage_claims/{fname}")
            n += 1
    print(f"  ✓ baggage_claims/ — {n} imagens copiadas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Sanity check

# COMMAND ----------

files = dbutils.fs.ls(VOLUME_PATH)
csvs = [f for f in files if f.name.endswith(".csv")]
pdfs = [f for f in files if f.name.endswith(".pdf")]
print(f"CSVs:    {len(csvs)} (esperado: 7)")
for f in csvs:
    print(f"  ✓ {f.name:24s} {f.size/1024:>8.1f} KB")
print(f"PDFs:    {len(pdfs)}")
for f in pdfs:
    print(f"  ✓ {f.name:24s} {f.size/1024:>8.1f} KB")

imgs = dbutils.fs.ls(f"{VOLUME_PATH}/baggage_claims")
jpgs = [f for f in imgs if f.name.endswith(".jpg")]
print(f"Imagens: {len(jpgs)} (esperado: 8)")

assert len(csvs) >= 7 and len(pdfs) >= 1 and len(jpgs) >= 8, "Setup incompleto."
print("\n✅ Setup OK — pode seguir pro notebook 01.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Quick look — flights

# COMMAND ----------

display(spark.read.option("header", True).csv(f"{VOLUME_PATH}/flights.csv").limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ✅ Pronto. **Anote seu slug:** `{USER_SLUG}`. Próximo notebook: `01_engenharia_dados_genai`.
