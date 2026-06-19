"""Gera imagens placeholder de avarias de bagagem pro workshop BeFly.

Cada imagem é um cartão sintético — não foto real — mas é o suficiente
pro modelo de visão extrair os campos estruturados durante a demo.
"""
from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

random.seed(13)

OUT = Path(__file__).resolve().parent.parent / "data" / "baggage_claims"
OUT.mkdir(parents=True, exist_ok=True)

FONT_REG  = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

CASES = [
    {"slug": "claim_001_mala_rasgada",  "tipo": "RASGO LATERAL", "voo": "BF1234", "rota": "GRU → REC",
     "cor": (200, 60, 60),  "obs": "Tecido externo rompido, cantos visíveis"},
    {"slug": "claim_002_mala_molhada",  "tipo": "BAGAGEM MOLHADA", "voo": "BF7700", "rota": "GIG → SSA",
     "cor": (60, 90, 180),  "obs": "Manchas escuras, sinais de líquido"},
    {"slug": "claim_003_mala_quebrada", "tipo": "RODA QUEBRADA",  "voo": "BF5500", "rota": "POA → CGH",
     "cor": (140, 60, 140), "obs": "Roda dianteira solta, alça com fissura"},
    {"slug": "claim_004_sem_avaria",    "tipo": "SEM AVARIA APARENTE", "voo": "BF2200", "rota": "CWB → BSB",
     "cor": (60, 140, 80),  "obs": "Bagagem íntegra, apenas etiqueta amassada"},
    {"slug": "claim_005_conteudo_perdido", "tipo": "VIOLAÇÃO COM PERDA", "voo": "BF4499", "rota": "GRU → FOR",
     "cor": (160, 30, 30),  "obs": "Cadeado violado, perfume e relógio ausentes"},
    {"slug": "claim_006_amassado",      "tipo": "AMASSADO", "voo": "BF8800", "rota": "MAO → BEL",
     "cor": (200, 130, 40), "obs": "Tampa amassada, sem ruptura"},
    {"slug": "claim_007_etiqueta_perdida", "tipo": "BAGAGEM SEM ETIQUETA", "voo": "BF3300", "rota": "BSB → GRU",
     "cor": (80, 80, 80),   "obs": "Encontrada sem identificação, aguardando cliente"},
    {"slug": "claim_008_pintura_descascada", "tipo": "ESTRUTURA EXTERNA AVARIADA", "voo": "BF6600", "rota": "SDU → MCZ",
     "cor": (90, 60, 140),  "obs": "Cantoneira descascada, sem comprometer estrutura"},
]

for c in CASES:
    img = Image.new("RGB", (1200, 800), c["cor"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([(40, 40), (1160, 760)], outline=(255, 255, 255), width=4)

    f_big = ImageFont.truetype(FONT_BOLD, 64)
    f_md  = ImageFont.truetype(FONT_BOLD, 36)
    f_sm  = ImageFont.truetype(FONT_REG, 28)

    draw.text((80, 80),  "BEFLY — RELATÓRIO IRREGULAR (RIR)", font=f_md, fill=(255, 255, 255))
    draw.text((80, 200), c["tipo"], font=f_big, fill=(255, 255, 255))
    draw.text((80, 340), f"Voo:  {c['voo']}", font=f_sm, fill=(255, 255, 255))
    draw.text((80, 390), f"Rota: {c['rota']}", font=f_sm, fill=(255, 255, 255))
    draw.text((80, 460), "Observação do agente:", font=f_sm, fill=(230, 230, 230))
    # quebra linha simples
    obs = c["obs"]
    if len(obs) > 60:
        i = obs.rfind(" ", 0, 60)
        draw.text((80, 500), obs[:i], font=f_sm, fill=(255, 255, 255))
        draw.text((80, 540), obs[i+1:], font=f_sm, fill=(255, 255, 255))
    else:
        draw.text((80, 500), obs, font=f_sm, fill=(255, 255, 255))
    draw.text((80, 700), "Imagem ilustrativa · BeFly Travel · Workshop Databricks", font=f_sm, fill=(220, 220, 220))

    p = OUT / f"{c['slug']}.jpg"
    img.save(p, "JPEG", quality=88)
    print("✓", p)
