# Setup pré-workshop — participantes BeFly

**O que você precisa ter pronto até quinta-feira (D-1).**

> Workshop **hands-on**: você vai executar tudo. Não vai assistir demo, vai construir. Reserve 3h livres na sexta sem reuniões.

Tempo estimado: 15 min.

---

## 1. Acesso ao workspace Databricks

URL: `https://fe-sandbox-baraldi-deployment.cloud.databricks.com`

- Faça login com seu e-mail @befly.com
- Se der `403` ou e-mail não encontrado, fale com **Daniel** (daniel.baraldi@databricks.com)

**Teste rápido:**
- Sidebar → Catalog → procure `<seu_catalog>` → `befly_workshop` → você deve ver:
  - 1 volume: `raw`
  - 6 CSVs dentro do volume
- Sidebar → SQL → New query → rode:
  ```sql
  SELECT * FROM <seu_catalog>.befly_workshop.raw LIMIT 1;
  ```

Se a query rodar, você está pronto pra parte Databricks. ✓

---

## 2. Genie Code (opcional — quem quiser acompanhar a parte agentic)

Os módulos finais (Genie Code + skills + MCP) podem ser **observados** sem instalar nada. Mas se quiser reproduzir depois:

### Instalação

```bash
# macOS
brew install genie-code

# Linux/Windows: consultar instalador oficial Databricks
```

### Autenticação

```bash
databricks auth login --host https://fe-sandbox-baraldi-deployment.cloud.databricks.com --profile befly
```

Confirma:
```bash
databricks current-user me --profile befly
```

### Plugin Databricks AI Dev Kit

Se ainda não estiver carregado:
```bash
claude plugin add databricks-ai-dev-kit
```

Valide com:
```bash
ls ~/.claude/plugins/cache/fe-vibe/databricks-ai-dev-kit/*/.test/skills/
```

Você deve ver ~24 skills `databricks-*` listadas. Durante o workshop o agente vai escolher sozinho qual usar.

---

## 3. Conhecimento prévio (opcional)

Recomendado, mas não obrigatório:

| Recurso | Tempo | Por quê |
|---|---|---|
| [Tour de 10 min da Databricks](https://docs.databricks.com/getting-started/index.html) | 10 min | Linguagem comum |
| [Spark Declarative Pipelines docs](https://docs.databricks.com/aws/en/dlt/) | 15 min | A pedra fundamental |
| [Genie overview](https://docs.databricks.com/aws/en/genie/) | 5 min | Pra entender Genie vs Genie One vs Genie Code |

---

## 4. O que trazer

- Laptop carregado
- Acesso ao Slack do workshop (`#befly-workshop-databricks`)
- Curiosidade — vamos fazer muita coisa em 3 horas

---

## 5. Seu slug pessoal

Antes do workshop, escolha **seu USER_SLUG** — usaremos pra isolar seu trabalho dentro do workspace compartilhado.

- Formato: 3 letras + 3 dígitos (ex: `mar042`, `ren007`, `cam123`)
- Onde usar: você vai colar nos widgets dos notebooks
- Onde você vai criar coisas:
  - Schema: `<seu_catalog>.befly_<slug>`
  - Pipeline: `befly_pipeline_<slug>`
  - Modelo: `flight_delay_clf` (dentro do seu schema)
  - Dashboard: `BeFly — Operações & CX (<slug>)`
  - Genie Space: `BeFly (<slug>)`
  - MCP App: `befly-mcp-<slug>`
  - CX Console App: `befly-cx-<slug>`

> **Anote o slug no celular ou Post-it.** Você vai colá-lo umas 10 vezes.

## 6. Cenário do workshop

BeFly é uma companhia aérea brasileira (fictícia neste exercício). Vamos construir o **stack completo de dados** dela usando o Databricks AI Dev Kit:

```
CSVs raw → Bronze/Silver (SDP) → Gold com ai_query → ML → Dashboards → Genie → Genie One
                                                          ↑
                                                   Tudo via Genie Code
                                                   (skills + MCP)
```

---

## Dúvidas

- **Tech:** Daniel Baraldi (daniel.baraldi@databricks.com / Slack `@daniel.baraldi`)
- **Logística:** PoC BeFly no Slack
