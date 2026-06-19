# Guia do co-piloto — Workshop BeFly  (hands-on)

**Data:** Sexta-feira, 19 de junho de 2026  ·  **Horário:** 14h00 – 17h00
**Workspace:** `fe-sandbox-baraldi-deployment`
**Volume compartilhado read-only:** `/Volumes/<seu_catalog>/befly_workshop/raw/`
**Schema por participante:** `<seu_catalog>.befly_<seu_slug>` (cada um cria o próprio em `00_setup`)

## Modelo do workshop

Workshop **hands-on**: cada participante executa **todos os 7 módulos** no seu schema isolado. Seu papel como facilitador é **co-piloto**: andar de mesa em mesa, desbloqueio rápido, sincronizar checkpoints, manter o ritmo. Não é demo de palco.

**Recomendação operacional:** spin up de Vector Search endpoint leva 5-15 min. Use **1 endpoint compartilhado** (`befly_workshop_vs`) — cada participante cria SEU índice apontando pra ele.

**Convenções pra todos:**
- `USER_SLUG` = 3 letras + 3 dígitos (ex: `dan001`). Cada participante define no `00_setup` e usa em todos os notebooks/recursos.
- **Nada compartilhado escrita**: tudo que cada um cria leva o slug no nome (pipeline `befly_pipeline_dan001`, modelo `flight_delay_clf` no schema `befly_dan001`, dashboard `BeFly — Operações & CX (dan001)`, MCP App `befly-mcp-dan001`, etc.).
- **Compartilhado leitura**: o volume `/Volumes/.../raw/` com CSVs + JPGs + PDFs gerados.

---

## Antes do workshop (D-1) — só co-piloto

- [ ] Confirmar workspace acessível pros participantes (grupo `befly-workshop-participants`)
- [ ] Volume compartilhado com 7 CSVs + 8 JPGs (já feito via bootstrap)
- [ ] Você rodar o end-to-end uma vez no **seu próprio slug** (ex: `dan999`) pra validar
- [ ] Imprimir/distribuir o **cheat sheet de prompts** (`material/genie_code_prompts.md`)
- [ ] Definir nomenclatura clara pros slugs e anotar quem é quem (Slack post pinned)
- [ ] Ter um Slack channel `#befly-workshop` aberto pra perguntas durante

### Smoke check (3 comandos)

```bash
# Auth no workspace certo
databricks current-user me --profile=fe-sandbox-baraldi-deployment

# Skills do AI Dev Kit carregadas (24 skills, incluindo as do workshop)
ls ~/.claude/plugins/cache/fe-vibe/databricks-ai-dev-kit/*/.test/skills/

# CSVs no volume
databricks fs ls dbfs:/Volumes/<seu_catalog>/befly_workshop/raw/ --profile=fe-sandbox-baraldi-deployment
```

Status atual (validado D-1): ✓ auth ok · ✓ 24 skills carregadas · ✓ 6 CSVs no volume.

## Skills disponíveis no Genie Code

O `databricks-ai-dev-kit` já traz **24 skills carregadas**. As que vão aparecer na demo:

| Módulo | Skills usadas |
|---|---|
| Engenharia de dados + GenAI | **Lakeflow Designer (UI)** com 5 AI capabilities: `ai_query` · `ai_parse_document` · vision (`databricks-claude-sonnet-4`) · Vector Search (delta-sync) · `databricks-asset-bundles`/`databricks-jobs` (Bloco B) |
| Dashboards (AI/BI) | `databricks-aibi-dashboards` com **widgets Vega-Lite** custom (heatmap, sankey, histograma) |
| Machine Learning | `databricks-python-sdk` · `databricks-mlflow-evaluation` · `databricks-model-serving` |
| Dashboards (AI/BI) | `databricks-aibi-dashboards` |
| Genie | `databricks-genie` · `databricks-agent-bricks` |
| Genie Code finale | **`befly-route-analyzer`** + **`befly-feedback-triage`** (criadas neste workshop) + MCP `befly` (criado neste workshop) |

## Material de apoio aberto na tela

- Notebook `00_setup.py` (já rodado)
- README do workshop em uma aba
- Genie Code rodando em outra janela (terminal grande, fonte 18pt+)
- Slide deck no segundo monitor

---

# Roteiro minuto-a-minuto

## 14:00 – 14:10 · Abertura + setup (10 min)

**Objetivo:** todo mundo no mesmo barco em 10 min.

- (2 min) Quem sou eu / por que estou aqui
- (3 min) Cenário BeFly + dados (mostrar a tabela do README)
- (3 min) "O fio condutor de hoje: tudo será construído via **Genie Code** com **skills** e **MCP** — multiplicador de produtividade"
- (2 min) Mostrar `00_setup.py` rodado → CSVs no volume → 6 tabelas no catalog

**Frases-âncora:**
> *"Esse workshop tem 6 dimensões em 3h. Não vou clicar em UI quase nenhuma. Vou pedir."*

---

## 14:10 – 15:05 · Engenharia de dados + GenAI (55 min)

### A) Lakeflow Designer + `ai_query` — 30 min  ⭐ destaque do bloco

**Modo:** Hands-on. Cada participante executa. **GUI ao vivo** — Lakeflow Designer no browser, lado a lado com Genie Code (que ajuda só nas SQLs/expectations).

Steps (detalhe em `01_engenharia_dados_genai.md`):
1. **Create pipeline → Lakeflow Designer**
2. Drag-drop 6 sources do volume → 6 `bronze_*` (Auto Loader streaming)
3. Adicionar transforms para `silver_flights`, `silver_bookings`, `silver_customers` (com expectations marcadas)
4. Group-by sobre silver → `gold_daily_route_kpis` e `gold_revenue_by_cabin`
5. ⭐ **5 AI capabilities** todas no mesmo bloco — cada uma resolve um tipo de dado caótico:
   - **5.1 `gold_tickets_structured`** ← THE highlight. `ai_query` em `silver_support_tickets.mensagem` (PT-BR livre, WhatsApp/e-mail/chat) → 9 campos estruturados (intent, urgencia, sentimento, tipo_viagem, destino, datas_mencionadas, orcamento_brl, tamanho_grupo, resumo_pt).
   - **5.2 `gold_feedback_classified`** ← quick win, sentimento de feedback pós-viagem. Alimenta o app no módulo final.
   - **5.3 `gold_invoices_parsed`** ← `ai_parse_document` em PDFs de faturas de hotel → hospede, datas, total, etc.
   - **5.4 `gold_baggage_claims_parsed`** ← **vision model** (`databricks-claude-sonnet-4`) lendo imagens base64 de bagagens danificadas → tipo_dano, severidade, objetos_visiveis, requer_reembolso.
   - **5.5 `idx_tickets`** ← **AI Search / Mosaic Vector Search** com delta-sync, indexa as mensagens → busca semântica + híbrida (vector × filtro estruturado).
6. Publish + Start → ~3 min até gold materializar

**Frases-âncora — texto livre (5.1):**
> *"Olhem essas 4 mensagens — não tem padrão nenhum. Datas de 10 formas, destinos como cidade/região/sinônimo, orçamento embutido. **Regex morre, NLP tradicional leva semanas**. `ai_query` + JSON schema: UMA SQL, output garantido."*

**Frases-âncora — PDFs (5.3) e imagens (5.4):**
> *"`ai_parse_document` engole PDF, scan, imagem, DOCX — devolve texto + tabelas. Pra BeFly Conecta é eliminar uma BPO inteira de digitação de fatura."*

> *"Vision: mesma `ai_query`, agora com `files=>array(base64(content))`. O modelo Claude Sonnet 4 olha a foto, classifica avaria. **Pixel também vira coluna**."*

**Frases-âncora — busca semântica (5.5):**
> *"Estruturado responde 'quantos casos da semana foram emergência'. Vector Search responde 'mostra casos parecidos com o que aconteceu com a Diamond em Lisboa'. Dois eixos, mesma fonte."*

> *"Delta-sync: nova linha em silver vira embedding em 1-5 min, automático. Embedding é gerenciado pelo Databricks."*

**Frases-âncora gerais do Designer:**
> *"Pipeline de produção visual, com lineage UC, expectations declarativas, **e LLMs como bloco do canvas**. Dá pra um analista de negócio? Sim. Vira código real por baixo dos panos."*

**Se rolar pergunta "e se eu quiser código?":** **Export → Python** do Designer gera SDP source notebook editável.

### B) Jobs — 25 min

**Modo:** Hands-on. Cada participante executa. Genie Code via skill `databricks-asset-bundles`.

**Prompt ao Genie Code:**
> *Crie um Databricks Asset Bundle pro workshop BeFly com job `befly_workshop_daily` que: (1) atualiza o pipeline `befly_pipeline`, (2) roda o notebook `02_machine_learning`, (3) notifica daniel.baraldi@databricks.com em falha. Schedule diário 06:00 BRT. Salve em /Users/daniel.baraldi/workshops/befly/databricks.yml. Valide e deploy em --target dev.*

Mostre:
- O `databricks.yml` gerado (15 linhas)
- `databricks bundle validate` passando
- Job criado na UI
- Disparar uma run manual

**Talking points:**
- "DAB = jobs versionados, CI/CD friendly"
- "Notificação pode ser email, Slack webhook, PagerDuty webhook"
- "O Designer + DAB juntos: visual pra construir + código pra versionar/promover"

---

## 15:05 – 15:15 · Pausa (10 min)

Sugestão: ficar disponível pra perguntas 1:1.

---

## 15:15 – 15:35 · Machine Learning (20 min)

**Prompt 4:**
> *Crie um modelo de classificação que prevê se um voo vai atrasar ≥ 15 min, usando `silver_flights` + features de aeronave e aeroporto. Treine HistGradientBoostingClassifier, registre em `<seu_catalog>.befly_workshop.flight_delay_clf`, promova a versão melhor com alias `champion`.*

Mostre:
- O notebook gerado pelo agente
- A run no MLflow com AUC, F1
- O modelo no UC Model Registry com alias

**Talking points:**
- "AutoML existe e seria 1 linha — mas mostrei explícito pra você ver o que está acontecendo"
- "Alias `champion`/`challenger` substitui stages (deprecados)"
- "Pra texto livre — feedback dos passageiros — `ai_query` é melhor que treinar do zero"

---

## 15:35 – 15:55 · Dashboards AI/BI (20 min)

**Prompt 5** (ver `03_dashboards.md` na íntegra):
> *Crie um dashboard AI/BI `BeFly — Operações & CX` com 4 widgets em `<seu_catalog>.befly_workshop`: KPIs, mapa do Brasil, heatmap rota × dow, top reclamações.*

Mostre:
- Como ele valida cada SQL antes de criar o widget
- O dashboard pronto, abrir no browser
- Adicionar um filtro global ao vivo: "Adicione um filtro por mês"

**Talking points:**
- "Dashboard como código — pode virar DAB resource e versionar"
- "Mesmo dataset que a Genie Space vai usar — single source of truth"

---

## 15:55 – 16:15 · Genie (20 min)

**Prompt 6:**
> *Crie uma Genie Space "BeFly — Operações & CX" sobre as gold tables, com instructions em PT-BR e 4 sample queries. (Detalhe na pergunta exatamente como em `04_genie_space.md`.)*

Mostre — perguntas ao vivo na space:
1. "Quais foram as 10 rotas com mais voos nos últimos 30 dias?"
2. "E destas, quais tiveram pior pontualidade?" ← follow-up
3. "Quais as principais reclamações dos passageiros?" ← puxa a gold do `ai_query`
4. "Compare pontualidade Sudeste vs Nordeste"

**Talking points:**
- "Genie é caso de uso # 1 pra Q&A — não confundir com Genie Code"
- "Instructions + sample queries = a 'memória curada' que o LLM usa"

---

## 16:15 – 16:35 · Genie One (20 min)

Modo hands-on (cada um executa) (sem mexer em produção):
1. Mostrar a tela de admin → como habilitaria pra grupo `befly-business-users`
2. Mostrar a landing curada (screenshot ou ambiente de teste)
3. Trocar pra um usuário de negócio → fazer 2 perguntas
4. ⭐ **No chat do Genie One, digite ao vivo:**
   > *"Manda o dashboard 'BeFly — Operações & CX' pro meu e-mail (daniel.baraldi@databricks.com) e pra cx-ops@befly.com.br todo dia útil às 07:30, em PDF. Assunto: '[BeFly] Operações & CX — {date}'. E dispara uma execução agora."*

   Genie One pede confirmação → aprovação → schedule criado + Run now → e-mail chega em 30s. Abrir no telão (segundo monitor).
5. Variação no chat: *"Quais subscriptions estão ativas? Cancela a primeira."* — Genie One lista, pede confirmação, deleta
6. Mostrar `system.access.audit` (`service_name='lakeview'`/`genie'`) + Workflows → Jobs com prefixos `lakeview_subscription_…` e `genie_subscription_…`

**Talking points:**
- "Genie One é a face pro time de negócio — sem ver Workflows, Catalog, Compute"
- "**Tarefas agendadas + e-mail** = relatório matinal sem ninguém abrir nada. Cada subscription vira um Job serverless invisível"
- "Se o usuário perde permissão na fonte, o e-mail para automaticamente — UC respeita até no envio agendado"
- "100% da governança Unity Catalog continua valendo"

---

## 16:35 – 17:00 · Genie Code — skills + MCP + app criado ao vivo (25 min)

**Foco do bloco:** mostrar que o Genie Code é **extensível** pela BeFly E **produtivo** ao ponto de criar um app full-stack do zero numa demo.

### Skills (10 min)

Abra `material/skills/befly-route-analyzer/SKILL.md` ao vivo:
- Frontmatter (`name`, `description`, `allowed-tools`)
- Procedimento + queries SQL
- Output esperado

Invoque ao vivo:
> *Use a skill befly-route-analyzer pra rota GRU → SSA no último trimestre.*

Mostre o output. Aponte: "isso aqui foi escrito uma vez — agora qualquer pessoa do time pode rodar essa análise com 1 linha".

Mostre a outra skill (`befly-feedback-triage`) com prompt similar.

### MCP server **deployado como Databricks App** (8 min)

Abra `material/mcp-server/README.md` na tela. Vá tela a tela:
1. **O que é MCP?** (slide rápido)
2. **server.py** — 3 tools mockadas (`get_flight_status`, `get_customer_loyalty`, `notify_passenger`)
3. **Registro em `~/.claude/mcp_servers.json`**
4. **Demo ao vivo:**
   > *Qual o status do voo BF1234 agora e se estiver atrasado, notifique o passageiro do booking 42 por SMS.*
   - O agente chama `mcp__befly__get_flight_status` → recebe `DELAYED`
   - Chama `mcp__befly__notify_passenger` → confirma com você antes
5. **Combinação skill + MCP** — explicar a sinergia

### App full-stack ao vivo (7 min)  ⭐ highlight do encerramento

Cole o **prompt #6** (`material/genie_code_prompts.md`) no Genie Code:

> *Crie um Databricks App full-stack chamado "befly-cx-console" usando o padrão APX (FastAPI + React/Vite/TS) sobre <seu_catalog>.befly_workshop. Coloque o logo da BeFly no header (gere SVG inline: "Be" laranja #FF511E, "Fly" navy #111633, ícone de avião). Tabela editável + chart builder (Recharts: barras/linha/pizza, dim escolhível: categoria/tier/mes/regiao..., metric: count/avg_sev/pendentes). MERGE em cx_actions. Export CSV. Deploy via get_best_warehouse + create_or_update_app.*

Enquanto ele constrói (vai levar 2-3 min), narre o que está acontecendo:
- Skill `databricks-app-apx` foi invocada
- Está gerando estrutura `backend/` + `frontend/`
- Frontend buildando com Vite
- Deploy via `create_or_update_app`

**Quando a URL voltar:**
- Abrir no browser, mostrar logo + KPIs
- Filtrar últimos 7 dias, sev ≥ 4
- Trocar gráfico pra `tier × count × pizza` → mostra que reclamantes são proporcionalmente mais Diamond/Gold (impacto de receita!)
- Editar uma linha, Save, refresh, mostrar a tabela `cx_actions` no Catalog Explorer

**Encerramento (3 min):**
- Recap das 6 dimensões em 1 slide
- 2 next steps recomendados pra BeFly: (1) replicar pipeline com dados reais, (2) escolher 1 API interna e expor via MCP

---

## Perguntas frequentes (esperadas)

| Pergunta | Resposta curta |
|---|---|
| "Quanto custa `ai_query`?" | Pay-per-token nos endpoints DBRX. Visível em `system.serving.endpoint_usage`. |
| "Posso usar GPT-4 em vez do Llama?" | Sim, via External Models — mas pra cargas grandes recomendamos endpoints Databricks (latência + governança). |
| "Como gerencio versões das skills?" | Como código — repo git separado, ou junto com o DAB. |
| "MCP roda no Databricks?" | Servidor MCP roda onde você quiser (local, container, Lambda). Pode rodar como Databricks App. |
| "Genie Code substitui Notebook?" | Não — ele edita/cria notebooks. Os participantes do workshop continuarão usando notebooks normalmente. |
| "Modelos ficam treinados ao vivo?" | No workshop sim. Em produção, o Job da agenda treina diário. |
