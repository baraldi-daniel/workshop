"""Gera os CSVs do workshop Befly.

Roda em qualquer Python 3 sem dependências externas (só stdlib).
Saída em ../data/
"""
from __future__ import annotations

import csv
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

OUT = Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Aeroportos brasileiros (IATA, cidade, UF, região)
AIRPORTS = [
    ("GRU", "São Paulo - Guarulhos", "SP", "Sudeste"),
    ("CGH", "São Paulo - Congonhas", "SP", "Sudeste"),
    ("VCP", "Campinas - Viracopos", "SP", "Sudeste"),
    ("GIG", "Rio de Janeiro - Galeão", "RJ", "Sudeste"),
    ("SDU", "Rio de Janeiro - Santos Dumont", "RJ", "Sudeste"),
    ("CNF", "Belo Horizonte - Confins", "MG", "Sudeste"),
    ("BSB", "Brasília", "DF", "Centro-Oeste"),
    ("GYN", "Goiânia", "GO", "Centro-Oeste"),
    ("CGB", "Cuiabá", "MT", "Centro-Oeste"),
    ("CGR", "Campo Grande", "MS", "Centro-Oeste"),
    ("CWB", "Curitiba", "PR", "Sul"),
    ("POA", "Porto Alegre", "RS", "Sul"),
    ("FLN", "Florianópolis", "SC", "Sul"),
    ("NVT", "Navegantes", "SC", "Sul"),
    ("IGU", "Foz do Iguaçu", "PR", "Sul"),
    ("SSA", "Salvador", "BA", "Nordeste"),
    ("REC", "Recife", "PE", "Nordeste"),
    ("FOR", "Fortaleza", "CE", "Nordeste"),
    ("NAT", "Natal", "RN", "Nordeste"),
    ("JPA", "João Pessoa", "PB", "Nordeste"),
    ("MCZ", "Maceió", "AL", "Nordeste"),
    ("AJU", "Aracaju", "SE", "Nordeste"),
    ("THE", "Teresina", "PI", "Nordeste"),
    ("SLZ", "São Luís", "MA", "Nordeste"),
    ("MAO", "Manaus", "AM", "Norte"),
    ("BEL", "Belém", "PA", "Norte"),
    ("MCP", "Macapá", "AP", "Norte"),
    ("BVB", "Boa Vista", "RR", "Norte"),
    ("RBR", "Rio Branco", "AC", "Norte"),
    ("PMW", "Palmas", "TO", "Norte"),
]

with open(OUT / "airports.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["airport_code", "city", "state", "region"])
    w.writerows(AIRPORTS)

# ---------------------------------------------------------------------------
# Frota (20 aeronaves)
AIRCRAFT_TYPES = [
    ("A320neo", 180, 5000),
    ("A321neo", 220, 5500),
    ("B737-800", 174, 5200),
    ("B737 MAX 8", 178, 6500),
    ("E195-E2", 132, 4800),
]

aircraft_rows = []
for i in range(1, 21):
    model, seats, range_km = random.choice(AIRCRAFT_TYPES)
    year = random.randint(2015, 2024)
    tail = f"PR-BFY{i:02d}"
    aircraft_rows.append((tail, model, seats, range_km, year))

with open(OUT / "aircraft.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["tail_number", "model", "seats", "range_km", "year_in_service"])
    w.writerows(aircraft_rows)

# ---------------------------------------------------------------------------
# Customers (500)
FIRST_NAMES = [
    "Ana", "Bruno", "Carla", "Daniel", "Eduarda", "Felipe", "Gabriela", "Henrique",
    "Isabela", "João", "Karina", "Lucas", "Mariana", "Natália", "Otávio", "Patrícia",
    "Rafael", "Sofia", "Tiago", "Vanessa", "William", "Yasmin", "Pedro", "Beatriz",
    "Caio", "Larissa", "Mateus", "Júlia", "Renato", "Camila",
]
LAST_NAMES = [
    "Silva", "Souza", "Oliveira", "Santos", "Pereira", "Costa", "Rodrigues", "Almeida",
    "Nascimento", "Carvalho", "Gomes", "Martins", "Araújo", "Ribeiro", "Alves",
    "Monteiro", "Mendes", "Barbosa", "Rocha", "Dias",
]
TIER = ["Diamond", "Gold", "Silver", "Bronze", "None"]
TIER_WEIGHTS = [1, 5, 15, 30, 49]
states = [a[2] for a in AIRPORTS]

customers = []
for cid in range(1, 501):
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    email = f"{first}.{last}{cid}@example.com".lower().replace("ã", "a").replace("á", "a").replace("ç", "c").replace("í", "i").replace("é", "e").replace("ó", "o").replace("ú", "u").replace("â", "a").replace("ê", "e").replace("ô", "o")
    state = random.choice(states)
    signup = datetime(2022, 1, 1) + timedelta(days=random.randint(0, 1400))
    tier = random.choices(TIER, weights=TIER_WEIGHTS)[0]
    age = random.randint(18, 75)
    customers.append((cid, first + " " + last, email, state, signup.date().isoformat(), tier, age))

with open(OUT / "customers.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["customer_id", "name", "email", "home_state", "signup_date", "loyalty_tier", "age"])
    w.writerows(customers)

# ---------------------------------------------------------------------------
# Flights (5000) — 12 meses
codes = [a[0] for a in AIRPORTS]
tails = [a[0] for a in aircraft_rows]

# distância aproximada por região (km) — bem grosseira
REGION_DIST = {
    ("Sudeste", "Sudeste"): 400, ("Sudeste", "Sul"): 800, ("Sudeste", "Centro-Oeste"): 900,
    ("Sudeste", "Nordeste"): 1800, ("Sudeste", "Norte"): 2800,
    ("Sul", "Sul"): 500, ("Sul", "Centro-Oeste"): 1300, ("Sul", "Nordeste"): 2800, ("Sul", "Norte"): 3500,
    ("Centro-Oeste", "Centro-Oeste"): 700, ("Centro-Oeste", "Nordeste"): 1700, ("Centro-Oeste", "Norte"): 2000,
    ("Nordeste", "Nordeste"): 600, ("Nordeste", "Norte"): 2000,
    ("Norte", "Norte"): 1200,
}
def dist(r1, r2):
    return REGION_DIST.get((r1, r2)) or REGION_DIST.get((r2, r1)) or 1500

region_by_code = {a[0]: a[3] for a in AIRPORTS}

DELAY_REASONS = ["weather", "mechanical", "atc", "crew", "operational", "none"]
DELAY_WEIGHTS = [10, 5, 8, 4, 6, 67]

flights = []
flight_id = 1
start = datetime(2025, 6, 1, 0, 0)
for _ in range(5000):
    origin = random.choice(codes)
    destination = random.choice([c for c in codes if c != origin])
    d = dist(region_by_code[origin], region_by_code[destination])
    sched_dep = start + timedelta(minutes=random.randint(0, 365 * 24 * 60))
    duration = int(d / 800 * 60) + random.randint(-10, 20)
    sched_arr = sched_dep + timedelta(minutes=duration)
    reason = random.choices(DELAY_REASONS, weights=DELAY_WEIGHTS)[0]
    delay_min = 0 if reason == "none" else random.randint(15, 240)
    actual_dep = sched_dep + timedelta(minutes=delay_min if random.random() < 0.7 else 0)
    actual_arr = actual_dep + timedelta(minutes=duration + random.randint(-5, 10))
    status = "CANCELLED" if (delay_min > 180 and random.random() < 0.15) else "COMPLETED"
    tail = random.choice(tails)
    flights.append((
        flight_id, f"BF{1000 + flight_id % 9000}", origin, destination, tail,
        sched_dep.isoformat(timespec="minutes"), sched_arr.isoformat(timespec="minutes"),
        actual_dep.isoformat(timespec="minutes") if status != "CANCELLED" else "",
        actual_arr.isoformat(timespec="minutes") if status != "CANCELLED" else "",
        d, status, delay_min, reason,
    ))
    flight_id += 1

with open(OUT / "flights.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow([
        "flight_id", "flight_number", "origin", "destination", "tail_number",
        "scheduled_departure", "scheduled_arrival", "actual_departure", "actual_arrival",
        "distance_km", "status", "delay_minutes", "delay_reason",
    ])
    w.writerows(flights)

# ---------------------------------------------------------------------------
# Bookings (12000) — com feedback livre para ai_query
FEEDBACK_POS = [
    "Voo tranquilo, tripulação muito atenciosa.",
    "Pontual e confortável, recomendo!",
    "Excelente experiência, embarque rápido.",
    "Comissários muito gentis, voo perfeito.",
    "Cheguei antes do horário, parabéns Befly.",
    "Aeronave nova e limpa, gostei bastante.",
    "Atendimento de primeira no balcão.",
    "Conexão sem stress e bagagem chegou junto.",
]
FEEDBACK_NEG = [
    "Voo atrasou 3 horas e nenhuma comunicação foi feita.",
    "Perderam minha mala, péssimo atendimento.",
    "Aeronave suja e ar condicionado quebrado.",
    "Tripulação despreparada para lidar com atraso.",
    "Cancelaram o voo sem reacomodação adequada.",
    "Cobraram bagagem extra que estava dentro do limite.",
    "Embarque caótico e sem organização.",
    "Atendimento por telefone é horrível, ninguém resolve.",
]
FEEDBACK_NEU = [
    "Voo dentro do esperado, sem problemas.",
    "Tudo ok, nada demais a comentar.",
    "Padrão de companhia aérea, normal.",
    "Cumpriu o prometido, foi razoável.",
    "",
    "",
]

CHANNELS = ["app", "site", "agente", "agencia"]
CHANNEL_WEIGHTS = [50, 30, 5, 15]
CABIN = ["Economy", "Economy+", "Business"]
CABIN_WEIGHTS = [75, 18, 7]

bookings = []
for bid in range(1, 12001):
    flight = random.choice(flights)
    flight_id = flight[0]
    cust_id = random.randint(1, 500)
    booked_at = datetime.fromisoformat(flight[5]) - timedelta(days=random.randint(1, 60))
    cabin = random.choices(CABIN, weights=CABIN_WEIGHTS)[0]
    base_price = {"Economy": 350, "Economy+": 550, "Business": 1400}[cabin]
    price = round(base_price * (1 + random.uniform(-0.3, 0.6)) * (flight[9] / 600), 2)
    channel = random.choices(CHANNELS, weights=CHANNEL_WEIGHTS)[0]
    # feedback: mais provável de existir se o voo atrasou ou cancelou
    delay = flight[11]
    status = flight[10]
    if status == "CANCELLED" or delay >= 60:
        feedback = random.choices([random.choice(FEEDBACK_NEG), random.choice(FEEDBACK_NEU), ""], weights=[60, 20, 20])[0]
    elif delay >= 15:
        feedback = random.choices([random.choice(FEEDBACK_NEG), random.choice(FEEDBACK_NEU), random.choice(FEEDBACK_POS), ""], weights=[25, 25, 20, 30])[0]
    else:
        feedback = random.choices([random.choice(FEEDBACK_POS), random.choice(FEEDBACK_NEU), ""], weights=[20, 15, 65])[0]
    bookings.append((bid, flight_id, cust_id, booked_at.date().isoformat(), cabin, price, channel, feedback))

with open(OUT / "bookings.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["booking_id", "flight_id", "customer_id", "booking_date", "cabin", "price_brl", "channel", "feedback_text"])
    w.writerows(bookings)

# ---------------------------------------------------------------------------
# Maintenance (300)
MAINT_TYPES = ["preventiva", "corretiva", "inspeção A-check", "inspeção C-check", "AOG"]
MAINT_WEIGHTS = [40, 25, 20, 10, 5]
MAINT_NOTES = [
    "Troca de pneus do trem de pouso principal.",
    "Substituição de válvula hidráulica.",
    "Inspeção do motor 2 e troca de filtros.",
    "Reparo em sistema de pressurização.",
    "Atualização de software do FMS.",
    "Reposição de luzes externas.",
    "Calibração de instrumentos do cockpit.",
    "Reparo emergencial em sistema de ar condicionado.",
    "Troca de bateria APU.",
    "Inspeção estrutural após pouso duro.",
]
maint = []
for mid in range(1, 301):
    tail = random.choice(tails)
    date = datetime(2025, 6, 1) + timedelta(days=random.randint(0, 365))
    mtype = random.choices(MAINT_TYPES, weights=MAINT_WEIGHTS)[0]
    hours = round(random.uniform(2, 80), 1)
    cost = round(hours * random.uniform(800, 5000), 2)
    note = random.choice(MAINT_NOTES)
    maint.append((mid, tail, date.date().isoformat(), mtype, hours, cost, note))

with open(OUT / "maintenance.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["maintenance_id", "tail_number", "event_date", "type", "hours", "cost_brl", "notes"])
    w.writerows(maint)

# ---------------------------------------------------------------------------
print("Generated:")
for f in sorted(OUT.glob("*.csv")):
    rows = sum(1 for _ in open(f)) - 1
    print(f"  {f.name}: {rows} rows")
