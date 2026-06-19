#!/usr/bin/env bash
# Recria o workshop BeFly em qualquer workspace Databricks.
#
# Uso:
#   ./bootstrap.sh --profile NOME_DO_PROFILE [--catalog CATALOG] [--schema SCHEMA] [--user EMAIL]
#
# O que faz:
#   1. Gera os CSVs em data/ (se não existirem)
#   2. Cria schema CATALOG.SCHEMA (catalog precisa já existir e ser seu)
#   3. Cria volume CATALOG.SCHEMA.raw
#   4. Faz upload dos 6 CSVs pro volume
#   5. Faz upload dos notebooks + material pra /Users/<email>/befly_workshop
#   6. Imprime os próximos passos manuais (pipeline + ML + app warehouse_id)

set -euo pipefail
cd "$(dirname "$0")"

PROFILE="${PROFILE:-}"
CATALOG="${CATALOG:-catalog_baraldi}"
SCHEMA="${SCHEMA:-befly_workshop}"
USER_EMAIL="${USER_EMAIL:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)  PROFILE="$2";   shift 2 ;;
    --catalog)  CATALOG="$2";   shift 2 ;;
    --schema)   SCHEMA="$2";    shift 2 ;;
    --user)     USER_EMAIL="$2"; shift 2 ;;
    -h|--help)
      grep '^#' "$0" | sed 's|^# \{0,1\}||'
      exit 0 ;;
    *) echo "Arg desconhecido: $1"; exit 1 ;;
  esac
done

if [[ -z "$PROFILE" ]]; then
  echo "❌ --profile obrigatório (use 'databricks auth profiles' pra ver)"
  exit 1
fi

[[ -z "$USER_EMAIL" ]] && USER_EMAIL=$(databricks current-user me --profile="$PROFILE" 2>/dev/null | grep userName | cut -d'"' -f4)
[[ -z "$USER_EMAIL" ]] && { echo "❌ não consegui descobrir seu e-mail; use --user"; exit 1; }

WS_DIR="/Users/${USER_EMAIL}/befly_workshop"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  BeFly Workshop — bootstrap"
echo "═══════════════════════════════════════════════════════════════"
echo "  Profile : $PROFILE"
echo "  Catalog : $CATALOG"
echo "  Schema  : $SCHEMA"
echo "  User    : $USER_EMAIL"
echo "  WS path : $WS_DIR"
echo ""

# 1. Gerar CSVs se não existirem
if [[ ! -f data/flights.csv ]]; then
  echo "→ Gerando CSVs sintéticos…"
  python3 scripts/generate_data.py
fi

# 2. Schema
echo "→ Criando schema $CATALOG.$SCHEMA"
databricks schemas create "$SCHEMA" "$CATALOG" \
  --comment "Workshop BeFly" --profile="$PROFILE" 2>/dev/null \
  | tail -2 | head -1 || echo "  (já existia, ok)"

# 3. Volume
echo "→ Criando volume $CATALOG.$SCHEMA.raw"
databricks volumes create "$CATALOG" "$SCHEMA" raw MANAGED \
  --comment "Raw CSVs do workshop BeFly" --profile="$PROFILE" 2>/dev/null \
  | tail -2 | head -1 || echo "  (já existia, ok)"

# 4. Upload CSVs + PDF + JPGs
echo "→ Upload de CSVs"
for f in data/*.csv; do
  name=$(basename "$f")
  databricks fs cp "$f" "dbfs:/Volumes/$CATALOG/$SCHEMA/raw/$name" \
    --profile="$PROFILE" --overwrite 2>&1 | tail -1
done

echo "→ Upload do PDF de exemplo"
for f in data/*.pdf; do
  [[ -f "$f" ]] || continue
  databricks fs cp "$f" "dbfs:/Volumes/$CATALOG/$SCHEMA/raw/$(basename $f)" \
    --profile="$PROFILE" --overwrite 2>&1 | tail -1
done

echo "→ Upload das imagens de bagagem"
databricks fs mkdirs "dbfs:/Volumes/$CATALOG/$SCHEMA/raw/baggage_claims" --profile="$PROFILE" 2>&1 || true
for f in data/baggage_claims/*.jpg; do
  [[ -f "$f" ]] || continue
  databricks fs cp "$f" "dbfs:/Volumes/$CATALOG/$SCHEMA/raw/baggage_claims/$(basename $f)" \
    --profile="$PROFILE" --overwrite 2>&1 | tail -1
done

# 5. Workspace files
echo "→ Criando pasta $WS_DIR"
databricks workspace mkdirs "$WS_DIR" --profile="$PROFILE" 2>&1 || true
databricks workspace mkdirs "$WS_DIR/mcp-server" --profile="$PROFILE" 2>&1 || true
databricks workspace mkdirs "$WS_DIR/skills/route-analyzer" --profile="$PROFILE" 2>&1 || true
databricks workspace mkdirs "$WS_DIR/skills/feedback-triage" --profile="$PROFILE" 2>&1 || true

echo "→ Upload notebooks/"
for f in notebooks/00_setup.py notebooks/02_machine_learning.py; do
  name=$(basename "$f" .py)
  databricks workspace import "$WS_DIR/$name" --file "$f" \
    --language PYTHON --format SOURCE --overwrite --profile="$PROFILE" 2>&1 | tail -1
done
for f in notebooks/*.md; do
  databricks workspace import "$WS_DIR/$(basename $f)" --file "$f" \
    --format AUTO --overwrite --profile="$PROFILE" 2>&1 | tail -1
done

echo "→ Upload material/"
for f in material/*.md; do
  databricks workspace import "$WS_DIR/$(basename $f)" --file "$f" \
    --format AUTO --overwrite --profile="$PROFILE" 2>&1 | tail -1
done
for f in material/mcp-server/*; do
  databricks workspace import "$WS_DIR/mcp-server/$(basename $f)" --file "$f" \
    --format AUTO --overwrite --profile="$PROFILE" 2>&1 | tail -1
done
for f in material/skills/route-analyzer/*.md; do
  databricks workspace import "$WS_DIR/skills/route-analyzer/$(basename $f)" --file "$f" \
    --format AUTO --overwrite --profile="$PROFILE" 2>&1 | tail -1
done
for f in material/skills/feedback-triage/*.md; do
  databricks workspace import "$WS_DIR/skills/feedback-triage/$(basename $f)" --file "$f" \
    --format AUTO --overwrite --profile="$PROFILE" 2>&1 | tail -1
done

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ Bootstrap concluído"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# CATALOG diferente do default? Avisa de patches a fazer
if [[ "$CATALOG" != "catalog_baraldi" || "$SCHEMA" != "befly_workshop" ]]; then
  cat <<EOF
  ⚠️  Você usou catalog/schema customizado. Os notebooks/material têm
      "catalog_baraldi.befly_workshop" hardcoded. Para substituir em massa:

      cd "$(pwd)"
      LC_ALL=C find notebooks material -type f -exec \\
        sed -i '' "s/catalog_baraldi\\.befly_workshop/$CATALOG.$SCHEMA/g" {} +

      Depois re-rode este bootstrap (vai re-upload).

EOF
fi

cat <<EOF
  PRÓXIMOS PASSOS (manual)

  1. PIPELINE
     Workflows → Pipelines → Create pipeline → Lakeflow Designer
     Siga: $WS_DIR/01_engenharia_dados_genai

  2. MACHINE LEARNING
     Abrir $WS_DIR/02_machine_learning e Run All

  3. APP (FastAPI + React, criado ao vivo via Genie Code)
     Não há código pré-construído — o app nasce no momento da demo.
     Use o prompt #6 em material/genie_code_prompts.md.

  4. SKILLS GENIE CODE
     Copie material/skills/befly-* para ~/.claude/skills/ (laptop do facilitador)

  5. MCP SERVER
     Siga material/mcp-server/README.md (passos 1-5)

EOF
