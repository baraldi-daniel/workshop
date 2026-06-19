# Prompts pro Genie Code — copy & paste

Os 6 prompts principais da demo, prontos pra colar. Todos assumem que você está com o terminal/Claude Code conectado ao workspace `fe-sandbox-baraldi-deployment` e catalog `<seu_catalog>.befly_workshop`.

---

## #1 — Pipeline no Lakeflow Designer (modo UI)

Este bloco **não usa Genie Code** — é Lakeflow Designer ao vivo. Siga o guia em `notebooks/01_engenharia_dados_genai.md` passo a passo. Resumo:

1. Workflows → Pipelines → Create pipeline → **Lakeflow Designer**
2. Nome `befly_pipeline`, target `<seu_catalog>.befly_workshop`, Serverless
3. 6 bronze (drag CSVs do volume, Auto Loader streaming)
4. Transforms pra silver (`silver_flights` com expectations, `silver_bookings`, `silver_customers` dedup, demais passthrough)
5. Gold tradicional: `gold_daily_route_kpis`, `gold_revenue_by_cabin`
6. ⭐ **AI transform com `ai_query`** → `gold_feedback_classified` (structured output: sentimento/categoria/severidade)
7. Publish → Start

**Se precisar de ajuda do Genie Code durante o Designer** (ex: gerar SQL pra uma transform), use:

```
Gere uma expressão SQL pra silver_flights a partir de bronze_flights que: parseia scheduled_departure/arrival como timestamp, deriva dep_hour, dep_dow, is_delayed_15 (delay_minutes >= 15), is_cancelled (status='CANCELLED'). E sugira 3 expectations (1 drop em flight_id IS NOT NULL, 1 warn em origin <> destination, 1 drop em status IN ('COMPLETED','CANCELLED')).
```

---

## #2 — Job multi-task

```
Crie um Databricks Asset Bundle (databricks.yml) com:

bundle.name: befly_workshop

Pipeline befly_sdp (já existe, referenciar por ID).

Job befly_workshop_daily:
- schedule: 06:00 BRT diário
- email_notifications.on_failure: [daniel.baraldi@databricks.com]
- tasks:
  - refresh_pipeline (pipeline_task → befly_sdp)
  - train_ml (notebook_task → 02_machine_learning, depends_on refresh_pipeline)
- max_concurrent_runs: 1
- retries: 2

Salve o YAML em /Users/daniel.baraldi/workshops/befly/databricks.yml. Valide com `databricks bundle validate`. Faça deploy em --target dev.
```

---

## #3 — Modelo ML

```
Treine um modelo de classificação binária para prever atraso de voo (is_delayed_15 = label) em <seu_catalog>.befly_workshop.

Features (apenas estas, nada de leakage):
- categóricas: origin, destination, origin_region, dest_region, aircraft model
- numéricas: seats, year_in_service, distance_km, dep_hour, dep_dow

Filtro: status = 'COMPLETED' only.

Build: pipeline sklearn com ColumnTransformer (OneHotEncoder min_frequency=5 nas categóricas), HistGradientBoostingClassifier(max_iter=200, class_weight='balanced'). train_test_split test_size=0.2, stratify.

MLflow: registry-uri databricks-uc, model name <seu_catalog>.befly_workshop.flight_delay_clf. Log AUC + F1. Inferir signature, input_example.

Promover a última versão pro alias 'champion' usando MlflowClient.set_registered_model_alias.

Salve o notebook em /Workspace/Users/daniel.baraldi@databricks.com/befly_workshop/02_machine_learning.
```

---

## #4 — Dashboard AI/BI

```
Crie um dashboard AI/BI chamado "BeFly — Operações & CX" no workspace, com 4 widgets em <seu_catalog>.befly_workshop:

1. Linha de KPIs (4 cards no topo):
   - voos último mês (silver_flights)
   - pontualidade % último mês (silver_flights, status COMPLETED)
   - receita BRL acumulada último mês (silver_bookings join silver_flights)
   - reclamações severidade >= 4 último mês (gold_feedback_classified)

2. Mapa do Brasil — voos por região de origem último mês (gold_daily_route_kpis join silver_airports).

3. Heatmap rota × dia da semana com % atraso, top 20 rotas em volume.

4. Barra horizontal — top categorias de reclamação negativa (gold_feedback_classified, sentimento='negativo'), color = severidade média.

Use a paleta de cores Databricks (laranja primário). Habilite 2 filtros globais: mês e cabine.

Antes de criar cada widget, valide o SQL com execute_sql.
```

---

## #5 — Genie Space

```
Crie uma Genie Space chamada "BeFly — Operações & CX" sobre as tabelas em <seu_catalog>.befly_workshop. Inclua:

Tabelas:
- gold_daily_route_kpis
- gold_revenue_by_cabin
- gold_feedback_classified
- silver_flights
- silver_bookings
- silver_airports (dimensão)
- silver_customers (dimensão)

Instructions em PT-BR (cole exatamente):
"""
Esta Genie Space responde perguntas operacionais e de CX da BeFly.

REGRAS DE NEGÓCIO
- Voos com delay_minutes >= 15 são atrasados.
- Cancelamentos têm status='CANCELLED' — excluí-los de métricas de pontualidade.
- Receita = sum(price_brl) em silver_bookings.
- 'Top rotas' significa por número de voos, salvo indicação.
- Formate BRL como 'R$ X.XXX,XX'.

DIMENSÕES
- Rota: origin + ' → ' + destination
- Cabine: Economy, Economy+, Business
- Região: Sudeste, Sul, Nordeste, Norte, Centro-Oeste

NUNCA exponha email do customer.
"""

Sample queries (anexar 4):
1. "Top 10 rotas mais movimentadas no último mês" → SELECT origin, destination, sum(flights) AS voos FROM gold_daily_route_kpis WHERE flight_date >= add_months(current_date(), -1) GROUP BY 1,2 ORDER BY voos DESC LIMIT 10
2. "Quais rotas têm pior pontualidade?" → SELECT origin, destination, sum(delayed_15plus)/sum(flights) AS pct_atraso FROM gold_daily_route_kpis GROUP BY 1,2 HAVING sum(flights) > 50 ORDER BY pct_atraso DESC LIMIT 10
3. "Receita por cabine mês a mês" → SELECT month, cabin, revenue_brl FROM gold_revenue_by_cabin ORDER BY month, cabin
4. "Principais reclamações" → SELECT categoria, count(*) AS qtd FROM gold_feedback_classified WHERE sentimento='negativo' GROUP BY 1 ORDER BY qtd DESC

Use o SQL warehouse serverless padrão. Salve a space.
```

---

## #6 — App editável (FastAPI + React) com gráficos e logo BeFly

```
Crie um Databricks App full-stack chamado "befly-cx-console" usando o padrão APX (FastAPI no backend + React/Vite/TypeScript no frontend) sobre <seu_catalog>.befly_workshop.

PROPÓSITO
Console pro time de CX da BeFly triar feedbacks negativos, responder, salvar de volta na tabela e exportar.

IDENTIDADE VISUAL (use a marca BeFly de verdade — befly.com.br)
- Logo: baixe direto da CDN da Crunchbase:
  curl -L -o frontend/public/befly-logo.png "https://images.crunchbase.com/image/upload/c_pad,f_auto,q_auto:eco,dpr_1/f2hl2klkxbvs8if7myym?ik-sanitizeSvg=true"
  Referencie no header com <img src="/befly-logo.png" alt="BeFly" style="height:40px" />.
- Paleta (BeFly real):
  • Navy primário #0A1F44 (cor dominante do site/logo)
  • Branco #FFFFFF (fundo)
  • Azul claro #E6EEF8 pros painéis e linhas
  • Accent magenta/rosa #E5247A (para CTAs, badges e severidade alta)
  • Cinza texto #4A5160 e cinza muted #8A93A6
  • Vermelho #EF4444 apenas pra alertas críticos
- Tipografia: stack do site BeFly — 'Poppins', 'Inter', system-ui, -apple-system, sans-serif; pesos 400/600/700; títulos com letter-spacing -0.01em.
- Layout:
  • Sidebar de filtros à esquerda (260px), fundo #F7F9FC, divisor em #E6EEF8
  • Header com logo + título "BeFly · CX Console" em navy, e logo abaixo do título o tagline em cinza muted: "O ecossistema de turismo mais transformador na experiência de cada um."
  • KPI cards com border-left 4px em navy; o card "Pendentes" com border-left magenta se houver pendências
  • Botão primário (Salvar) em magenta #E5247A, hover #C41B69; botão secundário (Export) outline navy
  • Tier do cliente com chip colorido: Diamond #6366f1, Gold #D97706, Silver #64748B, Bronze #92400E, None #94A3B8
  • Footer pequeno com "BeFly · Criamos caminhos além do imaginável" centralizado em cinza muted

BACKEND (FastAPI)
- Endpoints:
  - GET  /api/feedbacks?dias&severidade_min&categorias[] — lista feedbacks (gold_feedback_classified left join silver_customers left join cx_actions). Prioridade: pendente > in_progress > resolvido; tier Diamond > Gold > Silver > resto; depois severidade desc.
  - POST /api/save — body {responder, edits[{booking_id, response_text, status}]}. MERGE em cx_actions (criar a tabela se não existir: booking_id BIGINT, responder STRING, response_text STRING, status STRING, responded_at TIMESTAMP, USING DELTA).
  - GET  /api/export.csv — mesma janela filtrada, headers content-disposition pra download.
  - GET  /api/aggregate?dim&metric — group by dim, retorna [{dim, value}] top 30. dims permitidas: categoria, severidade, tier, cabin, status, mes, dia_semana, regiao_orig, regiao_dest. metrics: count, avg_sev, pendentes.
  - GET  /api/chart-options — retorna {dims, metrics}.
- Use databricks-sql-connector + databricks-sdk pra autenticar com o warehouse via DATABRICKS_WAREHOUSE_ID.

FRONTEND (React + Vite + TS)
- 3 KPI cards no topo: total de feedbacks, pendentes, severidade média
- Tabela editável com colunas: booking, cliente, tier (colorido por tier), categoria, sev, feedback (truncado, clique expande), resposta (textarea inline), status (select)
- Chart builder: dropdowns pra dimensão / métrica / tipo (barras/linha/pizza) usando Recharts. Atualiza ao mudar qualquer filtro ou seleção.
- Botões "💾 Salvar" (chama POST /api/save com as linhas alteradas) e "⬇️ Exportar CSV"
- Toast de confirmação após salvar

DEPLOY
- app.yaml com command uvicorn, env DATABRICKS_WAREHOUSE_ID, resource sql_warehouse.
- Use get_best_warehouse pra escolher um warehouse serverless e injetar o ID no app.yaml.
- Build do frontend (npm run build) deve sair em backend/static.
- Crie a tabela cx_actions antes do deploy.
- create_or_update_app com source-code-path apontando pra material/app.
- Devolva a URL pública.

Salve o código todo em /Users/daniel.baraldi/workshops/befly/material/app/ seguindo a estrutura: backend/main.py, backend/requirements.txt, frontend/{package.json,vite.config.ts,tsconfig.json,index.html,src/{main.tsx,App.tsx,api.ts,components/*.tsx}}, app.yaml, README.md.
```

---

## Prompts auxiliares (se travar)

### Quando ele inventar nome de tabela errado:
```
Antes de continuar, liste todas as tabelas em <seu_catalog>.befly_workshop e me confirme os schemas. Não invente colunas.
```

### Quando o agente fica enrolado:
```
Pare. Resuma em 3 bullets o que você fez até agora e o próximo passo concreto. Não rode mais comandos até eu confirmar.
```

### Pra invocar as skills:
```
Use a skill befly-route-analyzer pra rota GRU → SSA no último trimestre.

Use a skill befly-feedback-triage com severidade >= 4 nos últimos 7 dias.
```

### Pra testar o MCP server:
```
Qual o status do voo BF1234 agora? Use o MCP befly.

Se estiver atrasado >30min, busque o tier do customer com email maria@example.com e me sugira uma resposta personalizada — mas ANTES de enviar a notificação me peça confirmação.
```
