# -*- coding: utf-8 -*-
"""
Mangotek Health Suite — Standardized Module Banner Generator
Generates pixel-perfect, 1200x630 cover banners for all Odoo Health modules
in strict accordance with BRANDKIT.md, PUBLISHING.md, and the Anti-Slop Design System.
"""

import os
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(REPO_ROOT, 'assets', 'icons')

# Design System Palette Tokens (from BRANDKIT.md)
PALETTE = {
    'midnight_navy': (15, 23, 42),       # #0F172A Base Canvas
    'gradient_bottom': (24, 32, 54),     # Bottom Canvas Shading
    'slate_card': (30, 41, 59),          # #1E293B Container Fill
    'slate_border': (51, 65, 85),        # #334155 Border Stroke
    'text_primary': (255, 255, 255),     # Pure White Titles
    'text_muted': (148, 163, 184),       # #94A3B8 Subtitles
    'emerald_mint': (26, 211, 187),      # #1AD3BB Healthcare Accent
    'emerald_bg': (16, 45, 45),          # Top Badge Background
    'odoo_plum': (113, 75, 103),         # Odoo Version Badge Fill
    'odoo_plum_border': (160, 110, 145), # Odoo Version Badge Border
    'pill_neutral_border': (71, 85, 105),# Neutral Badge Border
    'royal_azure': (8, 139, 245),        # Diagnostic Azure
    'vital_coral': (248, 97, 38),        # ER / Pharmacy Coral
    'sunflower_gold': (251, 185, 69),    # Accreditation Gold
}

MODULE_SPECIFICATIONS = [
    {
        "dir": "health_base",
        "icon": "health_base_512.png",
        "title": "Patient & Practitioner Core",
        "subtitle": "Master Patient Registry · Auto-MRN · NIK Validation · ICD-10 & ICD-9 CM",
        "accent": PALETTE['emerald_mint'],
        "highlight": "🏥 Patient Master & ICD-10/9",
    },
    {
        "dir": "health_emr",
        "icon": "health_emr_512.png",
        "title": "Clinical EMR Core",
        "subtitle": "Universal SOAP Notes · Vital Signs · BMI Auto-Calc · Medical Certificates",
        "accent": PALETTE['royal_azure'],
        "highlight": "📋 Universal SOAP & Vital Signs",
    },
    {
        "dir": "health_appointment",
        "icon": "health_appointment_512.png",
        "title": "Outpatient Queuing",
        "subtitle": "Clinic Admission · Physician Rosters · Queue Tickets · TV Display Engine",
        "accent": (46, 188, 250), # Sky Cyan
        "highlight": "🎫 Polyclinic Queue & TV Display",
    },
    {
        "dir": "health_pharmacy",
        "icon": "health_pharmacy_512.png",
        "title": "Pharmacy & Dispensary",
        "subtitle": "e-Prescribing · Compounded Drugs · Clinical Review · FEFO Lot Picking",
        "accent": PALETTE['vital_coral'],
        "highlight": "💊 Compounding & FEFO Lots",
    },
    {
        "dir": "health_billing",
        "icon": "health_billing_512.png",
        "title": "Hospital Billing Ledger",
        "subtitle": "Centralized Charges · Doctor Fee Split · Dynamic QRIS · Odoo Invoicing",
        "accent": PALETTE['sunflower_gold'],
        "highlight": "💳 Tariff Split & Dynamic QRIS",
    },
    {
        "dir": "health_inpatient",
        "icon": "health_inpatient_512.png",
        "title": "Ward & Bed Management",
        "subtitle": "Building Hierarchy · Real-time BOR · Bed Mutations · CPPT Progress Notes",
        "accent": PALETTE['royal_azure'],
        "highlight": "🛏️ Bed Matrix & CPPT Notes",
    },
    {
        "dir": "health_emergency",
        "icon": "health_emergency_512.png",
        "title": "Emergency Room (IGD)",
        "subtitle": "24/7 ER Triage (ATS/ESI) · Fast-Track Admission · Critical Care Flow",
        "accent": PALETTE['vital_coral'],
        "highlight": "🚨 24/7 Emergency Triage",
    },
    {
        "dir": "health_laboratory",
        "icon": "health_laboratory_512.png",
        "title": "Diagnostic Lab (LIS)",
        "subtitle": "Electronic Lab Orders · Age/Gender Normal Ranges · Hematology Analyzer Bridging",
        "accent": PALETTE['emerald_mint'],
        "highlight": "🔬 LIS Analyzer & Lab Orders",
    },
    {
        "dir": "health_radiology",
        "icon": "health_radiology_512.png",
        "title": "Medical Imaging (PACS)",
        "subtitle": "Radiology Orders · X-Ray, CT & USG · Radiologist Expertise · DICOM Web Viewer",
        "accent": PALETTE['royal_azure'],
        "highlight": "🩻 PACS & DICOM Imaging",
    },
    {
        "dir": "health_satusehat",
        "icon": "health_satusehat_512.png",
        "title": "Kemenkes SatuSehat FHIR",
        "subtitle": "HL7 FHIR REST Gateway · Async Outbox Queue · Encounters & Conditions",
        "accent": PALETTE['emerald_mint'],
        "highlight": "🇮🇩 Kemenkes SatuSehat Ready",
    },
    {
        "dir": "health_bpjs",
        "icon": "health_bpjs_512.png",
        "title": "BPJS Healthcare Bridging",
        "subtitle": "PCare FKTP · Peserta Check · Kunjungan REST · HMAC-SHA256 Auth",
        "accent": PALETTE['royal_azure'],
        "highlight": "🛡️ BPJS PCare FKTP",
    },
    {
        "dir": "health_surgery",
        "icon": "health_surgery_512.png",
        "title": "Operating Room & Delivery (VK)",
        "subtitle": "Surgical Theater · WHO Safety Checklist · Aldrete/Bromage PACU · Partus VK",
        "accent": PALETTE['vital_coral'],
        "highlight": "🔪 OR Theater & VK Partus",
    },
    {
        "dir": "health_bpjs_vclaim",
        "icon": "health_bpjs_vclaim_512.png",
        "title": "BPJS Hospital VClaim 2.0",
        "subtitle": "Inpatient/Outpatient SEP Generator · SPRI · Surat Kontrol · Cetak SEP PDF",
        "accent": PALETTE['emerald_mint'],
        "highlight": "🏥 BPJS VClaim 2.0 & SEP",
    },
    {
        "dir": "health_inacbg",
        "icon": "health_inacbg_512.png",
        "title": "INA-CBG E-Klaim Grouper",
        "subtitle": "ICD-10 & ICD-9 CM Case-Mix · Special CMG · Real Cost Disparity Audit · DC Kemenkes",
        "accent": PALETTE['sunflower_gold'],
        "highlight": "📊 E-Klaim Grouper & Audit",
    },
]

def load_fonts():
    font_bold = None
    font_regular = None
    if os.path.exists("C:\\Windows\\Fonts\\segoeuib.ttf"):
        font_bold = "C:\\Windows\\Fonts\\segoeuib.ttf"
    elif os.path.exists("C:\\Windows\\Fonts\\arialbd.ttf"):
        font_bold = "C:\\Windows\\Fonts\\arialbd.ttf"
    if os.path.exists("C:\\Windows\\Fonts\\segoeui.ttf"):
        font_regular = "C:\\Windows\\Fonts\\segoeui.ttf"
    elif os.path.exists("C:\\Windows\\Fonts\\arial.ttf"):
        font_regular = "C:\\Windows\\Fonts\\arial.ttf"

    def get_font(size, bold=False):
        p = font_bold if bold else font_regular
        if p and os.path.exists(p):
            return ImageFont.truetype(p, size)
        return ImageFont.load_default()
    return get_font

def generate_banner(mod, get_font):
    W, H = 1200, 630
    img = Image.new('RGB', (W, H), color=PALETTE['midnight_navy'])
    draw = ImageDraw.Draw(img)

    # 1. Subtle Canvas Vertical Gradient
    for y in range(H):
        r = int(PALETTE['midnight_navy'][0] + (PALETTE['gradient_bottom'][0] - PALETTE['midnight_navy'][0]) * (y / H))
        g = int(PALETTE['midnight_navy'][1] + (PALETTE['gradient_bottom'][1] - PALETTE['midnight_navy'][1]) * (y / H))
        b = int(PALETTE['midnight_navy'][2] + (PALETTE['gradient_bottom'][2] - PALETTE['midnight_navy'][2]) * (y / H))
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # 2. Subtle Coordinate Grid
    for x in range(150, W, 150):
        draw.line([(x, 0), (x, H)], fill=(51, 65, 85), width=1)
    for y in [100, 240, 410]:
        draw.line([(0, y), (W, y)], fill=(51, 65, 85), width=1)

    accent = mod["accent"]
    font_top = get_font(12, bold=True)
    font_title = get_font(42, bold=True)
    font_sub = get_font(18, bold=False)
    font_cat = get_font(12, bold=True)
    font_pill = get_font(14, bold=True)

    # 3. Top Tag Pill: 100% Free & Open Source
    tag_text = "100% FREE & OPEN SOURCE · LGPL-3"
    tb = draw.textbbox((0, 0), tag_text, font=font_top)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    pw, ph = tw + 44, 28
    px, py = (W - pw) // 2, 42
    draw.rounded_rectangle([px, py - 4, px + pw, py + ph - 4], radius=14, fill=PALETTE['emerald_bg'], outline=PALETTE['emerald_mint'], width=1)
    draw.ellipse([px + 12, py + 6, px + 20, py + 14], fill=PALETTE['emerald_mint'])
    draw.text((px + 28, py + 2), tag_text, fill=PALETTE['emerald_mint'], font=font_top)

    # 4. Large Module Icon in Rounded Container (140x140 px)
    icon_path = os.path.join(ASSETS_DIR, mod["icon"])
    if os.path.exists(icon_path):
        icon = Image.open(icon_path).convert('RGBA')
        icon = icon.resize((140, 140), Image.Resampling.LANCZOS)
        icon_x = (W - 140) // 2
        icon_y = 100
        draw.rounded_rectangle(
            [icon_x - 14, icon_y - 14, icon_x + 140 + 14, icon_y + 140 + 14],
            radius=26,
            fill=PALETTE['slate_card'],
            outline=PALETTE['slate_border'],
            width=2
        )
        img.paste(icon, (icon_x, icon_y), icon)

    # 5. Centered Module Title (Bold & Crisp)
    tb = draw.textbbox((0, 0), mod["title"], font=font_title)
    tw = tb[2] - tb[0]
    draw.text(((W - tw) // 2, 280), mod["title"], fill=PALETTE['text_primary'], font=font_title)

    # 6. Subtitle / Functional Summary
    tb = draw.textbbox((0, 0), mod["subtitle"], font=font_sub)
    tw = tb[2] - tb[0]
    draw.text(((W - tw) // 2, 348), mod["subtitle"], fill=PALETTE['text_muted'], font=font_sub)

    # 7. Category Overline
    cat_text = "OFFICIAL MANGOTEK HEALTH SUITE ADDON · ZERO-SLOP CLINICAL ARCHITECTURE"
    tb = draw.textbbox((0, 0), cat_text, font=font_cat)
    tw = tb[2] - tb[0]
    draw.text(((W - tw) // 2, 400), cat_text, fill=accent, font=font_cat)

    # 8. Standardized 3-Pill Bottom Row
    pills = [
        ('🟣 Odoo 18.0, 19.0 & 20.0', PALETTE['odoo_plum'], PALETTE['odoo_plum_border']),
        (mod["highlight"], PALETTE['slate_card'], accent),
        ('⚖️ Community & Enterprise', PALETTE['slate_card'], PALETTE['pill_neutral_border']),
    ]

    total_pill_w = 0
    pill_widths = []
    for ptext, _, _ in pills:
        tb = draw.textbbox((0, 0), ptext, font=font_pill)
        w = (tb[2] - tb[0]) + 34
        pill_widths.append(w)
        total_pill_w += w
    total_pill_w += (len(pills) - 1) * 16

    start_x = (W - total_pill_w) // 2
    cur_x = start_x
    pill_y = 515
    for i, (ptext, bg_col, border_col) in enumerate(pills):
        pw = pill_widths[i]
        draw.rounded_rectangle([cur_x, pill_y, cur_x + pw, pill_y + 38], radius=19, fill=bg_col, outline=border_col, width=1)
        tb = draw.textbbox((0, 0), ptext, font=font_pill)
        tw, th = tb[2] - tb[0], tb[3] - tb[1]
        draw.text((cur_x + (pw - tw) // 2, pill_y + (38 - th) // 2 - 2), ptext, fill=(241, 245, 249), font=font_pill)
        cur_x += pw + 16

    # Save to module static/description/banner.png
    out_dir = os.path.join(REPO_ROOT, mod["dir"], 'static', 'description')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'banner.png')
    img.save(out_path, 'PNG', optimize=True)
    print(f"  ✅ Banner generated: {mod['dir']}/static/description/banner.png ({os.path.getsize(out_path):,} bytes)")

def main():
    print("🎨 Generating standardized 1200x630 module banners with prominent 140x140 hero icons...")
    get_font = load_fonts()
    for spec in MODULE_SPECIFICATIONS:
        generate_banner(spec, get_font)
    print("🎉 ALL MODULE BANNERS GENERATED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
