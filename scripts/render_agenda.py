"""Renderiza a agenda do workshop Befly como PNG."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "agenda.png"

ROWS = [
    ("14:00 – 14:10", "Abertura + setup do workspace"),
    ("14:10 – 15:05", "Engenharia de dados + GenAI"),
    ("15:05 – 15:15", "Pausa"),
    ("15:15 – 15:35", "Machine Learning"),
    ("15:35 – 15:55", "Dashboards (AI/BI)"),
    ("15:55 – 16:15", "Genie — perguntas em linguagem natural"),
    ("16:15 – 16:35", "Genie One"),
    ("16:35 – 17:00", "Genie Code — skills do Genie Code"),
]
HEADER = ("Horário", "Tema")

SCALE = 2
PADDING = 28 * SCALE
ROW_H = 60 * SCALE
HEADER_H = 72 * SCALE
TITLE_H = 110 * SCALE
COL_W = [220 * SCALE, 700 * SCALE]
W = sum(COL_W) + 2 * PADDING
H = TITLE_H + HEADER_H + len(ROWS) * ROW_H + 2 * PADDING

BG          = (255, 255, 255)
TITLE       = (17, 22, 51)
SUBTITLE    = (90, 100, 120)
HEADER_BG   = (17, 22, 51)
HEADER_FG   = (255, 255, 255)
ROW_ALT     = (245, 248, 252)
TEXT        = (32, 38, 60)
ACCENT      = (255, 81, 30)
LINE        = (220, 225, 235)
BREAK_BG    = (255, 247, 230)
HIGHLIGHT_BG = (235, 244, 255)

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

FONT_REG  = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

f_title    = ImageFont.truetype(FONT_BOLD, 34 * SCALE)
f_subtitle = ImageFont.truetype(FONT_REG, 18 * SCALE)
f_header   = ImageFont.truetype(FONT_BOLD, 18 * SCALE)
f_row      = ImageFont.truetype(FONT_REG, 17 * SCALE)
f_row_b    = ImageFont.truetype(FONT_BOLD, 17 * SCALE)
f_footer   = ImageFont.truetype(FONT_REG, 13 * SCALE)

y = PADDING
draw.text((PADDING, y), "Workshop Hands-On Databricks", font=f_title, fill=TITLE)
y += 46 * SCALE
draw.text((PADDING, y), "Sexta-feira, 19 de junho de 2026  ·  14h00 – 17h00", font=f_subtitle, fill=SUBTITLE)
y += 34 * SCALE
draw.rectangle([(PADDING, y), (PADDING + 70 * SCALE, y + 4 * SCALE)], fill=ACCENT)
y += 24 * SCALE

x = PADDING
draw.rectangle([(PADDING, y), (PADDING + sum(COL_W), y + HEADER_H)], fill=HEADER_BG)
for i, h in enumerate(HEADER):
    draw.text((x + 18 * SCALE, y + 24 * SCALE), h, font=f_header, fill=HEADER_FG)
    x += COL_W[i]
y += HEADER_H

for idx, (horario, tema) in enumerate(ROWS):
    if "Pausa" in tema:
        bg = BREAK_BG
    elif "ai_query" in tema:
        bg = HIGHLIGHT_BG
    elif idx % 2 == 1:
        bg = ROW_ALT
    else:
        bg = BG
    draw.rectangle([(PADDING, y), (PADDING + sum(COL_W), y + ROW_H)], fill=bg)
    draw.rectangle([(PADDING, y + 14 * SCALE), (PADDING + 4 * SCALE, y + ROW_H - 14 * SCALE)],
                   fill=ACCENT if "Pausa" not in tema else (210, 160, 60))
    x = PADDING
    draw.text((x + 18 * SCALE, y + 19 * SCALE), horario, font=f_row_b, fill=TEXT)
    x += COL_W[0]
    draw.text((x + 18 * SCALE, y + 19 * SCALE), tema, font=f_row, fill=TEXT)
    y += ROW_H
    draw.line([(PADDING, y), (PADDING + sum(COL_W), y)], fill=LINE, width=1)

img.save(OUT, "PNG")
print(f"Saved: {OUT} ({W}x{H})")
