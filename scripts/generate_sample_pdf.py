"""Gera um PDF realista BeFly — contrato com cadeia hoteleira internacional.

Sem dependência externa — usa PIL (já instalado) pra renderizar páginas
como imagem e empilhar num único PDF multi-página.

Output: data/sample_doc.pdf (substitui o monografia antigo)
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "data" / "sample_doc.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

FONT_REG  = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_ITAL = "/System/Library/Fonts/Supplemental/Arial Italic.ttf"

W, H = 1240, 1754  # ~A4 a 150 DPI
MARGIN = 100
NAVY   = (10, 31, 68)
MAGENTA = (229, 36, 122)
GRAY   = (110, 120, 140)
TEXT   = (40, 45, 65)
LINE   = (220, 226, 240)
PANEL  = (247, 249, 252)


def new_page():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    # header strip
    d.rectangle([(0, 0), (W, 60)], fill=NAVY)
    f_brand = ImageFont.truetype(FONT_BOLD, 22)
    d.text((MARGIN, 17), "GLOBEHOTEL INTERNATIONAL", font=f_brand, fill=(255, 255, 255))
    d.text((W - 280, 17), "× BeFly Conecta · 2026 MSA", font=ImageFont.truetype(FONT_REG, 16), fill=(220, 226, 240))
    # footer
    d.line([(MARGIN, H - 70), (W - MARGIN, H - 70)], fill=LINE, width=1)
    d.text((MARGIN, H - 55), "Confidential — Master Services Agreement", font=ImageFont.truetype(FONT_ITAL, 12), fill=GRAY)
    return img, d


def title(d, y, txt, size=44, color=NAVY, font_path=FONT_BOLD):
    d.text((MARGIN, y), txt, font=ImageFont.truetype(font_path, size), fill=color)


def para(d, y, lines, size=17, color=TEXT, leading=28):
    f = ImageFont.truetype(FONT_REG, size)
    for ln in lines:
        d.text((MARGIN, y), ln, font=f, fill=color)
        y += leading
    return y


def hrule(d, y, color=LINE):
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=color, width=2)


def table(d, y, header, rows, col_w=None):
    n = len(header)
    if col_w is None:
        col_w = [(W - 2 * MARGIN) // n] * n
    f_h = ImageFont.truetype(FONT_BOLD, 16)
    f_r = ImageFont.truetype(FONT_REG, 15)
    row_h = 40
    # header
    d.rectangle([(MARGIN, y), (W - MARGIN, y + row_h)], fill=NAVY)
    x = MARGIN
    for i, h in enumerate(header):
        d.text((x + 12, y + 11), h, font=f_h, fill=(255, 255, 255))
        x += col_w[i]
    y += row_h
    # rows
    for idx, row in enumerate(rows):
        bg = PANEL if idx % 2 else (255, 255, 255)
        d.rectangle([(MARGIN, y), (W - MARGIN, y + row_h)], fill=bg)
        x = MARGIN
        for i, cell in enumerate(row):
            d.text((x + 12, y + 11), str(cell), font=f_r, fill=TEXT)
            x += col_w[i]
        y += row_h
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=LINE, width=1)
    return y


# ---------------------------------------------------------------------------
pages = []

# -- Page 1 — Cover --
img, d = new_page()
d.rectangle([(MARGIN, 320), (W - MARGIN, 330)], fill=MAGENTA)
title(d, 360, "Master Services", 64)
title(d, 440, "Agreement", 64)
title(d, 580, "Corporate Travel Distribution Partnership", 22, color=GRAY)
hrule(d, 700)
para(d, 740, [
    "PARTIES",
    "  Globehotel International Ltd. (the “Supplier”)",
    "  BeFly Conecta SA (the “Distributor”)",
    "",
    "EFFECTIVE DATE",
    "  January 1st, 2027",
    "",
    "TERM",
    "  Three (3) years, automatically renewed unless terminated",
    "",
    "GOVERNING LAW",
    "  Federative Republic of Brazil",
], size=18, leading=30)
pages.append(img)

# -- Page 2 — Executive Summary --
img, d = new_page()
title(d, 100, "Executive Summary")
hrule(d, 160)
para(d, 200, [
    "This Master Services Agreement (the “Agreement”) sets forth the terms and",
    "conditions under which Globehotel International Ltd. (“Supplier”) provides",
    "lodging services worldwide to the corporate clients of BeFly Conecta SA",
    "(“Distributor”), Brazil's largest travel ecosystem comprising Flytour,",
    "Belvitur, Queensberry, BeFly Travel and 28 additional brands.",
    "",
    "Distributor will market, sell and operationally support Supplier's portfolio",
    "of 2,400 properties across 87 countries, including the Globehotel,",
    "GlobeSelect, GlobeEssentials and GlobeResidences brands.",
    "",
    "The Agreement covers: commercial terms, rate card construction, commission",
    "structure, service levels, reporting and KPIs, content distribution and",
    "the contingency and force-majeure protocols.",
], leading=29)
pages.append(img)

# -- Page 3 — Article 1: Scope --
img, d = new_page()
title(d, 100, "Article 1 — Scope of Services", size=36)
hrule(d, 160)
para(d, 200, [
    "1.1 Supplier grants Distributor a non-exclusive right to distribute,",
    "    market and book the inventory of all Supplier properties listed in",
    "    Appendix A through Distributor's GDS, NDC, web and corporate-direct",
    "    booking channels.",
    "",
    "1.2 Distributor undertakes to provide its corporate customers with last-",
    "    room-availability access at negotiated rates as defined in Appendix B.",
    "",
    "1.3 Both parties commit to maintaining 99.5% systems-uptime in all booking",
    "    interfaces and to a four-hour maximum response window for incident",
    "    handling, twenty-four hours per day, seven days per week.",
    "",
    "1.4 Distributor shall be authorized to subdistribute through its franchise",
    "    network (BeFly Travel, Vai Voando, Instaviagem, Desviantes) provided",
    "    that commercial conditions remain in line with this Agreement.",
])
pages.append(img)

# -- Page 4 — Article 2: Commercial --
img, d = new_page()
title(d, 100, "Article 2 — Commercial Terms", size=36)
hrule(d, 160)
para(d, 200, [
    "2.1 Negotiated rates are exclusive of taxes and resort fees, which shall",
    "    be disclosed at point of sale.",
    "",
    "2.2 The base commission for transient bookings is set at the percentages",
    "    described in the table below, applied to net room revenue.",
    "",
])
y = table(d, 380,
    ["Brand", "Transient", "Corporate", "Group"],
    [
        ["Globehotel",       "10.0%", "8.0%",  "12.0%"],
        ["GlobeSelect",      "11.0%", "9.0%",  "13.0%"],
        ["GlobeEssentials",  "9.5%",  "7.5%",  "11.0%"],
        ["GlobeResidences",  "12.0%", "10.0%", "14.0%"],
    ],
    col_w=[400, 220, 220, 200],
)
para(d, y + 30, [
    "2.3 Additional override of one and a half percent (1.5%) applies when",
    "    aggregated annual production exceeds USD 50,000,000 in net revenue.",
    "",
    "2.4 Payments to Distributor shall be settled by the 15th of the month",
    "    following the month of stay, in United States Dollars, via wire",
    "    transfer to the account designated in Appendix C.",
])
pages.append(img)

# -- Page 5 — Article 3: Rate Card --
img, d = new_page()
title(d, 100, "Article 3 — Rate Card Construction", size=36)
hrule(d, 160)
para(d, 200, [
    "3.1 Rates are constructed by market and segment as follows.",
])
y = table(d, 280,
    ["Market", "BAR", "Corporate", "Government", "Family"],
    [
        ["São Paulo · Tier 1",   "USD 280", "USD 245", "USD 210", "USD 320"],
        ["Rio de Janeiro · Tier 1","USD 295", "USD 255", "USD 220", "USD 340"],
        ["New York · Manhattan", "USD 410", "USD 360", "USD 330", "USD 470"],
        ["Lisbon · Centro",      "EUR 245", "EUR 215", "EUR 195", "EUR 285"],
        ["Buenos Aires · CBA",   "USD 175", "USD 150", "USD 135", "USD 200"],
        ["Miami · South Beach",  "USD 360", "USD 320", "USD 290", "USD 410"],
    ],
    col_w=[420, 165, 165, 165, 125],
)
para(d, y + 30, [
    "3.2 Rates are reviewed annually on November 15th. Any modification",
    "    exceeding eight percent (8%) over the prior period requires written",
    "    consent of Distributor's commercial board.",
    "",
    "3.3 Currency exposure is the responsibility of Distributor for non-USD",
    "    rated properties, as governed by Section 9.",
])
pages.append(img)

# -- Page 6 — Service Levels --
img, d = new_page()
title(d, 100, "Article 4 — Service Levels (SLA)", size=36)
hrule(d, 160)
para(d, 200, [
    "4.1 Supplier guarantees the following service levels.",
])
y = table(d, 280,
    ["KPI", "Target", "Penalty cap"],
    [
        ["Booking confirmation latency",          "≤ 8 sec p95",       "0.5% credit"],
        ["Inventory availability accuracy",       "≥ 99.8% monthly",   "1.0% credit"],
        ["Last-room-availability honored",        "≥ 98%",             "0.5% credit"],
        ["GDS uptime (Sabre/Amadeus/Travelport)", "≥ 99.95% annual",   "1.5% credit"],
        ["NDC content parity vs direct",          "≥ 95% of attributes","1.0% credit"],
        ["Average billing dispute resolution",    "≤ 10 business days","0.5% credit"],
    ],
    col_w=[540, 320, 180],
)
para(d, y + 30, [
    "4.2 Credits are aggregated and applied to the immediately subsequent",
    "    invoice cycle in accordance with Appendix D.",
    "",
    "4.3 Failure to meet two consecutive cumulative thresholds invokes",
    "    Section 8 (Remediation Plan).",
])
pages.append(img)

# -- Page 7 — Reporting & figure --
img, d = new_page()
title(d, 100, "Article 5 — Reporting & KPIs", size=36)
hrule(d, 160)
para(d, 200, [
    "5.1 Supplier shall make available a monthly performance dashboard within",
    "    seven business days of month-end, including: room nights, average",
    "    daily rate, total net revenue, distribution mix and complaint rate.",
    "",
    "5.2 Distributor shall provide quarterly market-share analysis comparing",
    "    Supplier performance against the top three competing supplier groups",
    "    in each Tier-1 market.",
])
# Figure placeholder
fy = 460
d.rectangle([(MARGIN, fy), (W - MARGIN, fy + 380)], outline=NAVY, width=2)
d.rectangle([(MARGIN, fy), (W - MARGIN, fy + 38)], fill=NAVY)
d.text((MARGIN + 14, fy + 9), "Figure 5.1 — Quarterly room-night trend by market", font=ImageFont.truetype(FONT_BOLD, 16), fill=(255, 255, 255))
# simulate bars
import random
random.seed(3)
bx = MARGIN + 50
for i, (label, val) in enumerate([("Q1 GRU",0.7),("Q2 GRU",0.85),("Q3 GRU",0.92),("Q4 GRU",1.0),("Q1 GIG",0.55),("Q2 GIG",0.7),("Q3 GIG",0.78),("Q4 GIG",0.88),("Q1 NYC",0.62),("Q2 NYC",0.72),("Q3 NYC",0.83),("Q4 NYC",0.94)]):
    h = int(val * 250)
    d.rectangle([(bx, fy + 360 - h), (bx + 60, fy + 360)], fill=MAGENTA if "NYC" in label else NAVY)
    d.text((bx, fy + 365), label, font=ImageFont.truetype(FONT_REG, 11), fill=GRAY)
    bx += 78
para(d, fy + 420, [
    "5.3 Both parties commit to a joint quarterly business review at the",
    "    Distributor's headquarters in São Paulo.",
])
pages.append(img)

# -- Page 8 — Signatures --
img, d = new_page()
title(d, 100, "Article 14 — Execution", size=36)
hrule(d, 160)
para(d, 200, [
    "IN WITNESS WHEREOF, the parties have caused this Agreement to be executed",
    "by their duly authorized representatives as of the Effective Date.",
])
y0 = 500
for who, name, role in [
    ("GLOBEHOTEL INTERNATIONAL LTD.", "James W. Hollis",     "Chief Commercial Officer"),
    ("BEFLY CONECTA SA",              "Marina Cavalcanti",   "Chief Operations Officer · BeFly Conecta"),
]:
    d.text((MARGIN, y0), who, font=ImageFont.truetype(FONT_BOLD, 16), fill=NAVY)
    d.line([(MARGIN, y0 + 100), (MARGIN + 480, y0 + 100)], fill=TEXT, width=2)
    d.text((MARGIN, y0 + 110), f"{name}, {role}", font=ImageFont.truetype(FONT_REG, 14), fill=TEXT)
    d.text((MARGIN, y0 + 135), "Date: ____ / ____ / ________", font=ImageFont.truetype(FONT_REG, 14), fill=GRAY)
    y0 += 280
pages.append(img)

# ---------------------------------------------------------------------------
pages[0].save(OUT, "PDF", save_all=True, append_images=pages[1:], resolution=150.0)
print(f"✓ {OUT} — {len(pages)} páginas")
