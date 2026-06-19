# Outline dos slides — Workshop BeFly

Estrutura sugerida pra montar a apresentação. Cada bloco = 1 slide salvo formato `[TÍTULO] (sub)`.

---

## Abertura (3 slides)

1. **Capa** — "Workshop Databricks · BeFly · 19/06/2026" + logo BeFly + foto/título do facilitador
2. **Agenda** — usar `agenda.png` (já gerado em `~/Downloads/befly-agenda.png`)
3. **Cenário** — BeFly em 1 slide:
   - "BeFly: companhia aérea brasileira fictícia"
   - 6 tabelas (airports, aircraft, customers, flights, bookings, maintenance)
   - "Vamos modernizar o stack de dados em 3h, sem clicar quase nada — via Genie Code"

---

## Engenharia de dados + GenAI (5 slides)

4. **Lakeflow Designer** — visual pipeline builder, gera SDP por baixo dos panos, mesma governance UC
5. **Demo Designer** — screenshot do canvas BeFly: bronze → silver → gold + nó `ai_query` no meio
6. **AI transformation com `ai_query`** — bloco no canvas, structured output (JSON schema), incremental refresh
7. **Preview no canvas** — mostrar a tabela `gold_feedback_classified` aparecendo ao vivo (sentimento/categoria/severidade)
8. **Jobs com DAB** — YAML em 15 linhas, orquestra pipeline + ML

---

## Pausa (1 slide)

9. **Pausa 10 min** — slide de timer (15:05 – 15:15)

---

## Machine Learning (3 slides)

10. **MLOps na Databricks** — diagrama: feature → train → log → register → alias → serve
11. **Demo ML** — screenshot do MLflow + AUC/F1
12. **`ai_query` vs modelo treinado** — quando usar cada um (tabular → treinar; texto sem label → ai_query)

---

## Dashboards AI/BI (3 slides)

13. **AI/BI Dashboards** — o que mudou (vs Lakeview legacy), dashboards como código
14. **Demo dashboard** — screenshot do dashboard BeFly
15. **Como o Genie Code monta** — fluxo skill databricks-aibi-dashboards (validar SQL → render → publicar)

---

## Genie (3 slides)

16. **O que é Genie Space** — "Q&A em linguagem natural com governance UC"
17. **Anatomia de uma Genie Space** — Tables + Instructions + Sample queries + Trusted functions
18. **Demo Genie** — 4 perguntas ao vivo (preparar fallback em vídeo curto se quiser)

---

## Genie One (2 slides)

19. **Genie One** — "landing curada pro business user, zero Engineering UI"
20. **Demo Genie One** — screenshot da landing BeFly + flow de pergunta

---

## Genie Code + skills + MCP (5 slides)

21. **Genie Code: do que se trata** — agente de desenvolvimento Databricks com acesso a skills + MCP. Diferença vs Genie Space.
22. **O que é uma skill** — frontmatter + procedimento + progressive disclosure. Slide com a estrutura de `befly-route-analyzer/SKILL.md`.
23. **Demo skill** — invocação `befly-route-analyzer` + output em markdown
24. **O que é MCP** — protocolo, server + client, "USB-C pra LLMs"
25. **Demo MCP** — fluxo `get_flight_status` → `notify_passenger` com aprovação humana

---

## Encerramento (3 slides)

26. **Recap** — as 6 dimensões em uma imagem, com "tudo via Genie Code" no centro
27. **Próximos passos pra BeFly** — 3 bullets concretos (replicar pipeline em dados reais; escolher 1 API interna pra expor via MCP; treinar 2-3 engenheiros no Genie Code + skills)
28. **Obrigado + contato** — email + Slack + link pro repo

---

## Dicas de design

- **Mínimo de texto** — 5 linhas por slide max
- **Mostre printscreens do produto** — não bullet points
- **Fonte ≥ 24pt** — sala vai ter pessoas no fundo
- **Paleta:** primário Databricks orange `#FF511E`, secundário navy `#111633`
- **Sem code dump** — se precisar mostrar código, faça em janela ao lado (terminal/IDE), não num slide
