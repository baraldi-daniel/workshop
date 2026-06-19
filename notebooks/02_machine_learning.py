# Databricks notebook source
# MAGIC %pip install mlflow scikit-learn pandas
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC # 02 — Machine Learning
# MAGIC
# MAGIC **Horário:** 15:15 – 15:35  ·  **Duração:** 20 min  ·  **Hands-on:** sim — você treina + registra
# MAGIC
# MAGIC Cada participante registra **seu próprio modelo** em `catalog_baraldi.befly_<seu_slug>.flight_delay_clf`.
# MAGIC
# MAGIC Cenário: prever se um voo vai atrasar ≥15 min. Pipeline: feature table → treinar → registrar no UC → (opcional) serving.

# COMMAND ----------

dbutils.widgets.text("catalog", "catalog_baraldi", "Catalog (mesmo do 00_setup)")
dbutils.widgets.text("user_slug", "dan001", "Seu slug (mesmo do 00_setup)")
CATALOG = dbutils.widgets.get("catalog").strip()
USER_SLUG = dbutils.widgets.get("user_slug").strip().lower()
SCHEMA  = f"befly_{USER_SLUG}"
spark.sql(f"USE {CATALOG}.{SCHEMA}")
print(f"Trabalhando em {CATALOG}.{SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Feature table

# COMMAND ----------

from pyspark.sql import functions as F

VOL = f"/Volumes/{CATALOG}/{SCHEMA}/raw"

# Lê CSVs direto do volume (independente do pipeline 01)
flights = (spark.read.option("header", True).csv(f"{VOL}/flights.csv")
    .filter("status = 'COMPLETED'")
    .withColumn("dep_hour", F.hour(F.to_timestamp("scheduled_departure")))
    .withColumn("dep_dow",  F.dayofweek(F.to_timestamp("scheduled_departure")))
    .withColumn("is_delayed_15", F.when(F.col("delay_minutes").cast("int") >= 15, 1).otherwise(0))
    .withColumn("distance_km", F.col("distance_km").cast("int"))
)
ac = (spark.read.option("header", True).csv(f"{VOL}/aircraft.csv")
        .select("tail_number", "model", F.col("seats").cast("int").alias("seats"),
                F.col("year_in_service").cast("int").alias("year_in_service")))
ap = spark.read.option("header", True).csv(f"{VOL}/airports.csv")

features = (
    flights.join(ac, "tail_number", "left")
    .join(ap.select(F.col("airport_code").alias("origin"), F.col("region").alias("origin_region")), "origin", "left")
    .join(ap.select(F.col("airport_code").alias("destination"), F.col("region").alias("dest_region")), "destination", "left")
    .select(
        "flight_id",
        "origin", "destination", "origin_region", "dest_region",
        "model", "seats", "year_in_service",
        "distance_km", "dep_hour", "dep_dow",
        F.col("is_delayed_15").alias("label"),
    )
)
features.write.mode("overwrite").saveAsTable("feat_flight_delay")
display(spark.table("feat_flight_delay").limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Treinar + registrar no UC

# COMMAND ----------

import mlflow
import mlflow.sklearn
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, f1_score

mlflow.set_registry_uri("databricks-uc")
MODEL_NAME = f"{CATALOG}.{SCHEMA}.flight_delay_clf"   # ← já é per-user via USER_SLUG

pdf = spark.table("feat_flight_delay").toPandas().dropna()
X = pdf.drop(columns=["flight_id", "label"])
y = pdf["label"].astype(int)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

cat = ["origin", "destination", "origin_region", "dest_region", "model"]
num = ["seats", "year_in_service", "distance_km", "dep_hour", "dep_dow"]
pre = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=5, sparse_output=False), cat),
    ("num", "passthrough", num),
])

with mlflow.start_run(run_name="hist_gbm") as run:
    pipe = Pipeline([("pre", pre), ("clf", HistGradientBoostingClassifier(max_iter=200, class_weight="balanced"))])
    pipe.fit(X_tr, y_tr)
    proba = pipe.predict_proba(X_te)[:, 1]
    auc = roc_auc_score(y_te, proba)
    f1 = f1_score(y_te, (proba >= 0.5).astype(int))
    mlflow.log_metric("auc", auc)
    mlflow.log_metric("f1", f1)
    signature = mlflow.models.infer_signature(X_tr.head(5), pipe.predict(X_tr.head(5)))
    mlflow.sklearn.log_model(
        pipe, "model",
        registered_model_name=MODEL_NAME,
        signature=signature,
        input_example=X_tr.head(2),
    )
    print(f"AUC={auc:.3f}  F1={f1:.3f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Promover para alias `champion`

# COMMAND ----------

from mlflow import MlflowClient
client = MlflowClient()
versions = client.search_model_versions(f"name='{MODEL_NAME}'")
latest = sorted(versions, key=lambda v: int(v.version))[-1]
client.set_registered_model_alias(MODEL_NAME, "champion", latest.version)
print(f"v{latest.version} promovida a champion")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. (Opcional) Serving
# MAGIC
# MAGIC ### Criar endpoint
# MAGIC
# MAGIC Sidebar → **Serving** → **Create serving endpoint**:
# MAGIC - **Endpoint name:** `flight-delay-<seu_slug>` (ex: `flight-delay-dan000`)
# MAGIC - **Entity:** `catalog_baraldi.befly_<seu_slug>.flight_delay_clf` · alias `champion`
# MAGIC - **Workload size:** Small · **Scale-to-zero:** ✓
# MAGIC
# MAGIC Aguarda ~3-5 min até endpoint ficar **Ready**.
# MAGIC
# MAGIC ### Testar pela UI do endpoint
# MAGIC
# MAGIC Roda a próxima célula pra gerar o JSON de input → copia o output → cola em **Endpoint → Query endpoint** (formato JSON).

# COMMAND ----------

import json

sample = X_te.head(3).to_dict(orient="records")
payload = {"dataframe_records": sample}
print(json.dumps(payload, indent=2, default=str))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Ou via SDK (rode após o endpoint estar Ready)

# COMMAND ----------

from databricks.sdk import WorkspaceClient

ENDPOINT_NAME = f"flight-delay-{USER_SLUG}"
w = WorkspaceClient()
try:
    response = w.serving_endpoints.query(name=ENDPOINT_NAME, dataframe_records=sample)
    print("Predictions:", response.predictions)
except Exception as e:
    print(f"(endpoint não pronto ou inexistente: {e})")

# COMMAND ----------

# MAGIC %md
# MAGIC Próximo módulo: **Dashboards (AI/BI)**.
