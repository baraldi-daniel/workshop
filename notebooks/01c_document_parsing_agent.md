# 01c — ai_parse_document (Document Parsing)

**Opcional · pós-pipeline**

Parse um PDF em estrutura aproveitável (texto, tabelas, descrições de imagens) usando `ai_parse_document`. 2 caminhos: via Agents UI (sem código) ou via SQL direto.

## Caminho A — Agents UI (Document Parsing)

1. Sidebar → **AI/ML → Agents** → **Create Agent** → **Document Parsing**
2. Configurar:
   - **Name:** `doc_parser_<seu_slug>`
   - **Source files:** `/Volumes/<seu_catalog>/befly_<seu_slug>/raw/sample_doc.pdf`
   - **Output table:** `<seu_catalog>.befly_<seu_slug>.pdf_parsed_raw`
3. **Create + Run** → materializa tabela `pdf_parsed_raw` com colunas `path` e `parsed` (VARIANT).

## Caminho B — SQL direto

```sql
CREATE OR REPLACE TABLE <seu_catalog>.befly_<seu_slug>.pdf_parsed_raw AS
SELECT
  path,
  ai_parse_document(
    content,
    map(
      'version', '2.0',
      'descriptionElementTypes', '*'
    )
  ) AS parsed
FROM read_files(
  '/Volumes/<seu_catalog>/befly_<seu_slug>/raw/sample_doc.pdf',
  format => 'binaryFile'
)
```

Resultado: tabela `pdf_parsed_raw` com `path` + `parsed` (VARIANT estruturado contendo `parsed.document.elements[]` — texto, tabelas, figuras, headers).

## Inspecionar o VARIANT

```sql
SELECT
  path,
  parsed:document:metadata AS metadata,
  size(TRY_CAST(parsed:document:elements AS ARRAY<VARIANT>)) AS total_elementos
FROM <seu_catalog>.befly_<seu_slug>.pdf_parsed_raw
```
