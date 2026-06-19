# 06 — Genie Code: app full-stack via prompt

**16:35 – 17:00 · Hands-on**

## 1. Instalar o AI Dev Kit no Genie Code

Sem o AI Dev Kit, o Genie Code não sabe deployar app/pipeline/dashboard. Instalação é **clonando o repo** dentro do próprio Workspace.

**Passos:**

1. Abra qualquer notebook no workspace (ex: o próprio `00_setup`)
2. Click no ícone **Terminal** na barra superior do notebook (ou `View → Terminal`)
3. No terminal, clona o repo:

   ```bash
   git clone https://github.com/databricks-solutions/databricks-ai-dev-kit ~/ai-dev-kit
   ```

4. Abre o Genie Code (sidebar → Genie Code) e na **primeira mensagem** menciona o path:

   ```
   Use as skills do databricks-ai-dev-kit em ~/ai-dev-kit e me liste quantas estão disponíveis.
   ```

Resposta esperada: **24 skills** carregadas — `databricks-app-apx`, `databricks-dbsql`, `databricks-spark-declarative-pipelines`, `databricks-mlflow-evaluation`, `databricks-aibi-dashboards`, `databricks-genie`, etc.

## 2. Conferir auth

```
Qual catalog e workspace estou conectado agora?
```

Deve devolver o workspace do workshop + seu catalog. Se errado: `databricks auth login --host <url>` no terminal.

## 3. Prompt do app

Cole inteiro no Genie Code (substitua `<seu_catalog>` e `<seu_slug>`):

```
Crie um Databricks App full-stack chamado "befly-cx-console-<seu_slug>" (APX: FastAPI + React/Vite/TS) sobre <seu_catalog>.befly_<seu_slug>.

PROPÓSITO: Console pro time de CX triar feedbacks negativos, responder, salvar e exportar.

VISUAL (BeFly real)
- Logo: curl -L -o frontend/public/befly-logo.png "https://images.crunchbase.com/image/upload/c_pad,f_auto,q_auto:eco,dpr_1/f2hl2klkxbvs8if7myym?ik-sanitizeSvg=true"
- Paleta: navy #0A1F44, magenta #E5247A, cinza #4A5160, fundo branco
- Tipografia: Poppins, Inter, system-ui
- Tier chip: Diamond #6366f1, Gold #D97706, Silver #64748B

BACKEND
- GET  /api/feedbacks (gold_tickets_structured ⋈ silver_customers ⋈ cx_actions; priorize pendente, Diamond > Gold)
- POST /api/save → MERGE em cx_actions (cria se não existir: booking_id BIGINT, responder STRING, response_text STRING, status STRING, responded_at TIMESTAMP, DELTA)
- GET  /api/export.csv
- GET  /api/aggregate?dim&metric (dims: categoria, severidade, tier, status; metrics: count, avg_sev)

FRONTEND
- 3 KPI cards · tabela editável · chart builder com Recharts (barras/linha/pizza) · botões Salvar (magenta) e Export CSV

DEPLOY
- get_best_warehouse → injeta no app.yaml
- npm run build → backend/static
- create_or_update_app + deploy_app → devolva a URL
```
