"""BeFly MCP server — Databricks App (streamable HTTP).

Expõe tools BeFly que o Genie Code (ou qualquer cliente MCP) chama via HTTP.
Hospedado como Databricks App → OAuth nativo, scale-to-zero, centralizado.

Tools:
- get_flight_status(flight_id)           → consulta silver_flights
- get_customer_loyalty(customer_id)      → consulta silver_customers
- search_similar_tickets(query)          → Vector Search em idx_tickets
- notify_passenger(booking_id, channel, message) → registra notificação em cx_notifications
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Literal

from databricks import sql
from databricks.sdk.core import Config
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("befly")

CATALOG = "<seu_catalog>"
SCHEMA = "befly_workshop"


# ---------------------------------------------------------------------------
def _conn():
    cfg = Config()
    return sql.connect(
        server_hostname=cfg.host.replace("https://", ""),
        http_path=f"/sql/1.0/warehouses/{os.environ['DATABRICKS_WAREHOUSE_ID']}",
        credentials_provider=lambda: cfg.authenticate,
    )


def _query(query: str, params: tuple = ()) -> list[dict]:
    with _conn().cursor() as c:
        c.execute(query, params)
        rows = c.fetchall()
        cols = [d[0] for d in c.description]
    return [dict(zip(cols, r)) for r in rows]


def _exec(query: str, params: tuple = ()) -> None:
    with _conn().cursor() as c:
        c.execute(query, params)


# ---------------------------------------------------------------------------
@mcp.tool()
def get_flight_status(flight_id: int) -> dict:
    """Retorna o status atual de um voo BeFly e do atraso/cancelamento.

    Args:
        flight_id: ID numérico do voo na tabela silver_flights.

    Returns:
        Dict com status, origin, destination, atraso, motivo etc.
        Retorna {"found": false} se o voo não existir.
    """
    rows = _query(
        f"""
        SELECT flight_id, flight_number, origin, destination, status,
               scheduled_departure, actual_departure,
               delay_minutes, delay_reason, tail_number
        FROM {CATALOG}.{SCHEMA}.silver_flights
        WHERE flight_id = ?
        """,
        (flight_id,),
    )
    if not rows:
        return {"found": False, "flight_id": flight_id}
    r = rows[0]
    return {"found": True, **r}


@mcp.tool()
def get_customer_loyalty(customer_id: int) -> dict:
    """Retorna o tier de fidelidade e o histórico do cliente BeFly.

    Args:
        customer_id: ID do cliente em silver_customers.
    """
    rows = _query(
        f"""
        WITH base AS (
          SELECT c.customer_id, c.name, c.email, c.loyalty_tier, c.home_state, c.signup_date,
                 count(b.booking_id) AS bookings_total,
                 sum(b.price_brl)    AS total_brl
          FROM {CATALOG}.{SCHEMA}.silver_customers c
          LEFT JOIN {CATALOG}.{SCHEMA}.silver_bookings b USING (customer_id)
          WHERE c.customer_id = ?
          GROUP BY 1,2,3,4,5,6
        )
        SELECT * FROM base
        """,
        (customer_id,),
    )
    if not rows:
        return {"found": False, "customer_id": customer_id}
    return {"found": True, **rows[0]}


@mcp.tool()
def search_similar_tickets(
    query: str,
    num_results: int = 5,
    urgencia_min: Literal["baixa", "media", "alta", "critica"] = "baixa",
) -> list[dict]:
    """Busca semântica em chamados BeFly via Vector Search.

    Args:
        query: pergunta livre em PT-BR, ex: "cliente Diamond perdeu conexão internacional".
        num_results: quantos chamados similares retornar (default 5).
        urgencia_min: filtro mínimo de urgência ("baixa", "media", "alta", "critica").

    Returns:
        Lista de chamados ordenados por relevância semântica.
    """
    rank = {"baixa": 1, "media": 2, "alta": 3, "critica": 4}[urgencia_min]
    return _query(
        f"""
        SELECT v.ticket_id, v.search_score, t.marca, t.canal, t.received_at,
               t.mensagem, g.intent, g.urgencia, g.resumo_pt
        FROM vector_search(
          index => '{CATALOG}.{SCHEMA}.idx_tickets',
          query => ?,
          num_results => ?
        ) v
        JOIN {CATALOG}.{SCHEMA}.silver_support_tickets t USING (ticket_id)
        LEFT JOIN {CATALOG}.{SCHEMA}.gold_tickets_structured g ON g.ticket_id = t.ticket_id
        WHERE CASE g.urgencia WHEN 'critica' THEN 4 WHEN 'alta' THEN 3 WHEN 'media' THEN 2 ELSE 1 END >= ?
        ORDER BY v.search_score DESC
        """,
        (query, num_results, rank),
    )


@mcp.tool()
def notify_passenger(
    booking_id: int,
    channel: Literal["whatsapp", "email", "sms", "push"],
    message: str,
) -> dict:
    """Registra uma notificação a um passageiro BeFly (idempotente).

    Args:
        booking_id: ID da reserva (silver_bookings.booking_id).
        channel: canal — "whatsapp", "email", "sms" ou "push".
        message: texto. SMS limitado a 320 chars.

    Returns:
        Dict com ID da notificação registrada.
    """
    if channel == "sms" and len(message) > 320:
        return {"ok": False, "error": "Mensagem SMS > 320 chars"}

    # Garante que a tabela existe
    _exec(
        f"""
        CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.cx_notifications (
          notification_id  STRING,
          booking_id       BIGINT,
          channel          STRING,
          message_preview  STRING,
          sent_at          TIMESTAMP
        ) USING DELTA
        """
    )
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    notif_id = f"NTF-{abs(hash((booking_id, channel, message))) % 1_000_000:06d}"
    preview = (message[:120] + "…") if len(message) > 120 else message
    _exec(
        f"""
        MERGE INTO {CATALOG}.{SCHEMA}.cx_notifications t
        USING (SELECT ? AS notification_id) s
        ON t.notification_id = s.notification_id
        WHEN NOT MATCHED THEN INSERT
          (notification_id, booking_id, channel, message_preview, sent_at)
          VALUES (?, ?, ?, ?, TIMESTAMP '{now}')
        """,
        (notif_id, notif_id, booking_id, channel, preview),
    )
    return {"ok": True, "notification_id": notif_id, "channel": channel, "sent_at": now}


# ---------------------------------------------------------------------------
# ASGI app pro Databricks Apps (streamable HTTP transport)
app = mcp.streamable_http_app()
