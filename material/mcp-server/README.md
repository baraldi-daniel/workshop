# BeFly MCP server — Databricks App

Tutorial passo a passo para subir um **servidor MCP como Databricks App**, com 4 tools que o Genie Code (ou qualquer cliente MCP) consegue chamar por HTTP autenticado.

## Por que Databricks Apps (e não stdio local)?

| stdio local (laptop) | Databricks App ← escolhemos esta |
|---|---|
| Roda só no laptop do facilitador | Centralizado no workspace |
| Cada usuário precisa instalar/configurar | URL única compartilhada |
| Sem OAuth — usa as credenciais da máquina | OAuth on-behalf-of o user que abriu |
| Não tem auditoria | `system.access.audit` por chamada |
| Escala = laptop | Scale-to-zero + autoscale gerenciado |
| Tools usam mocks | Tools usam o **warehouse SQL real** e consultam silver/gold |

## Tools expostas (4)

| Tool                       | O que faz                                                                                  |
|----------------------------|--------------------------------------------------------------------------------------------|
| `get_flight_status`        | Lê `silver_flights` por `flight_id` — retorna status, atraso, motivo, tail               |
| `get_customer_loyalty`     | Lê `silver_customers` + agrega bookings — retorna tier, total de viagens, gasto BRL       |
| `search_similar_tickets`   | Roda Vector Search em `idx_tickets` (do módulo 5.5) — busca semântica + filtro de urgência |
| `notify_passenger`         | MERGE em `cx_notifications` (cria se não existir) — idempotente por hash da mensagem      |

## Estrutura

```
mcp-server/
├── server.py            # FastMCP + streamable_http_app() ASGI
├── app.yaml             # Config Databricks Apps
└── requirements.txt
```

---

## Passo a passo (10 min)

### 1. Pegar um warehouse SQL

```bash
databricks warehouses list --profile=fe-sandbox-baraldi-deployment -o json \
  | jq -r '.[] | select(.state=="RUNNING") | "\(.id)  \(.name)"' | head
```

### 2. Substituir o ID em `app.yaml`

```bash
WAREHOUSE_ID=<id_escolhido>
sed -i '' "s/<SUBSTITUIR_PELO_WAREHOUSE_ID>/$WAREHOUSE_ID/" app.yaml
```

### 3. Criar o app no workspace

```bash
databricks apps create befly-mcp \
  --description "MCP server BeFly — chamado pelo Genie Code" \
  --profile=fe-sandbox-baraldi-deployment
```

### 4. Deploy

```bash
databricks apps deploy befly-mcp \
  --source-code-path "$(pwd)" \
  --profile=fe-sandbox-baraldi-deployment
```

Em ~30s o app sobe. Saída:
```
status: RUNNING
url:    https://befly-mcp-<workspace-id>.cloud.databricksapps.com
```

### 5. Sanity test do endpoint MCP

```bash
APP_URL="https://befly-mcp-<workspace-id>.cloud.databricksapps.com/mcp"
# Lista as tools expostas
curl -s "$APP_URL/tools" -H "Authorization: Bearer $(databricks auth token --profile=fe-sandbox-baraldi-deployment | jq -r .access_token)" | jq .
```

Deve retornar JSON com as 4 tools (`get_flight_status`, `get_customer_loyalty`, `search_similar_tickets`, `notify_passenger`).

### 6. Registrar no Genie Code

Edite `~/.claude/mcp_servers.json`:

```json
{
  "mcpServers": {
    "befly": {
      "url": "https://befly-mcp-<workspace-id>.cloud.databricksapps.com/mcp",
      "transport": "streamable-http",
      "auth": {
        "type": "databricks-oauth",
        "profile": "fe-sandbox-baraldi-deployment"
      }
    }
  }
}
```

Reinicie o Genie Code. As 4 tools aparecem sob prefixo `mcp__befly__*`.

### 7. Testar de verdade

No Genie Code:

> *Qual o status do voo 42? Se estiver atrasado e o customer 17 for Diamond, busque chamados parecidos no histórico via search_similar_tickets e me dê uma sugestão de comunicação. Antes de mandar a notificação, me pergunta.*

O agente vai:
1. `mcp__befly__get_flight_status(42)` → atraso 90min, motivo "atc"
2. `mcp__befly__get_customer_loyalty(17)` → Diamond, 41 voos no ano
3. `mcp__befly__search_similar_tickets("Diamond atraso ATC longo")` → 5 casos similares
4. Sugere mensagem
5. **Pede confirmação** (não envia sozinho)
6. Após "ok", chama `mcp__befly__notify_passenger(booking_id, "whatsapp", "...")` → registra em `cx_notifications`

## Padrões de segurança (importantes pra produção)

- **OAuth on-behalf-of**: o app só vê o que o usuário que invocou veria. Quem não tem `SELECT` em `silver_flights` não consegue chamar `get_flight_status`.
- **Allow-list de tools**: nunca exponha uma tool genérica tipo "execute SQL". Defina explicitamente cada operação.
- **Idempotência**: `notify_passenger` usa `MERGE` por hash de `(booking_id, channel, message)` → chamar 2× não duplica.
- **Audit**: `system.access.audit` mostra `service_name = 'sql warehouse'` + identificador do app pra cada chamada.
- **Quota**: configure no `app.yaml` requests/min se o agente ficar muito ávido.
- **Ação destrutiva sempre com confirmação humana** — não deixe o agente cancelar voo, reembolsar, etc., sem etapa de aprovação.

## Demonstração (~5 min)

1. Mostrar o `app.yaml` + `server.py` no editor (50 linhas relevantes)
2. Mostrar o app já rodando no workspace (Compute → Apps → `befly-mcp`)
3. No Genie Code: o prompt do passo 7 acima
4. Mostrar o agente chamando as tools uma a uma (logs no terminal)
5. Voltar no Catalog Explorer → `cx_notifications` aparece com a linha nova
6. Fechar com a frase: *"Mesmo padrão pra qualquer API interna que BeFly tenha — Salesforce, manutenção, pricing. Coloca em uma tool, deploya como app, agente usa."*
