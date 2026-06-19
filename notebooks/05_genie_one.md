# 05 — Genie One

**16:15 – 16:35 · Hands-on**

Genie One = portal pro time de negócio. Você agenda dashboards e respostas Genie pra chegarem no e-mail — **via chat, em PT-BR natural**.

## Agendar e-mail do dashboard via chat

No chat do Genie One, digite:

> *"Manda o dashboard 'BeFly — Operações & CX' pro meu e-mail todo dia útil às 07:30 em PDF. E dispara uma execução agora pra eu ver chegando."*

Genie One pede confirmação → você aprova → schedule criado + Run now → e-mail chega em ~30s.

## Variações pra testar

> *"Quais subscriptions estão ativas e quem recebe?"*

> *"Cancela a subscription do dashboard CX matinal."*

> *"Manda só uma vez agora, sem agendar."*

> *"Agenda também a Genie Space de chamados críticos pra 8h, segunda a sexta."*

## Por baixo

Cada pedido vira um Databricks Job serverless (`lakeview_subscription_…` ou `genie_subscription_…`). Auditado em `system.access.audit`, respeita UC (sem permissão → e-mail em branco).

Próximo: **Genie Code**.
