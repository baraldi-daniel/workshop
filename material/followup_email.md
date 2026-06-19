# Follow-up email — Workshop BeFly

Template para enviar **no dia seguinte ao workshop** (sábado 20/06/2026), de manhã.

---

**Assunto:** Workshop Databricks BeFly · materiais, próximos passos, agradecimento

**Para:** participantes do workshop + sponsors BeFly

---

Olá time BeFly,

Obrigado pela energia de ontem à tarde. Em 3 horas a gente passou por 6 dimensões da Databricks Data Intelligence Platform — **construindo cada uma via Genie Code**:

| Módulo | O que rodou |
|---|---|
| Engenharia de dados | Pipeline SDP (Bronze→Silver→Gold com Auto Loader) |
| GenAI no SQL | `ai_query` classificando feedbacks dos passageiros |
| Orquestração | Job multi-task com Asset Bundle |
| Machine Learning | Modelo de previsão de atraso registrado no UC |
| Dashboards | AI/BI dashboard "BeFly — Operações & CX" |
| Genie + Genie One | Q&A em linguagem natural + portal pro business |
| Skills + MCP | 2 skills e 1 servidor MCP customizados |

## Acessos

- **Workspace:** `https://fe-sandbox-baraldi-deployment.cloud.databricks.com`
- **Catalog:** `catalog_baraldi.befly_workshop`
- **Repo do workshop:** [link do repositório]
  - `notebooks/` — todos os notebooks executados
  - `material/skills/` — `befly-route-analyzer` + `befly-feedback-triage`
  - `material/mcp-server/` — servidor MCP com tutorial passo a passo

Recomendo brincar com a Genie Space ainda essa semana — quanto mais perguntas vocês fizerem, mais ela aprende com as `sample queries`.

## Próximos passos sugeridos

**Curto prazo (2-3 semanas):**
1. **Replicar o pipeline com dados reais BeFly** num workspace dev — usem os notebooks como template
2. **Escolher 1 API interna** (operações, fidelidade, ou pricing) e expor via MCP — começa pequeno
3. **Treinar 2-3 engenheiros** em Genie Code + skills — ganho de produtividade composto

**Médio prazo (1-3 meses):**
4. POC de **Knowledge Assistant** (Agent Bricks) sobre manuais técnicos de aeronaves
5. Avaliar **Lakebase** pra OLTP de booking
6. Publicar **Genie One** pra time de operações (50-100 usuários)

## Como manter contato

- Slack: `@daniel.baraldi` (Databricks)
- E-mail: daniel.baraldi@databricks.com
- Office hours: terças 16-17h BRT (link nos próximos dias)

Se rolar alguma dúvida que travou no fim de semana, manda — respondo segunda cedo.

Boa semana, BeFly. ✈️

Daniel
