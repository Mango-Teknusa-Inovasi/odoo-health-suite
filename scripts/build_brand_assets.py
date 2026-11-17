# -*- coding: utf-8 -*-
"""
Mangotek Health Suite — Master Brand Asset Builder (V2 - Native Odoo Style)
Generates bold, full-bleed (90-95% canvas fill), multi-colored, seamless geometric
vector SVGs, raster PNGs (50, 100, 512, 1024), launcher icons, and master banners.
Accurately mirrors native Odoo 18 app icon design language.
"""

import os
import io
import resvg_py
from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")

os.makedirs(ICONS_DIR, exist_ok=True)

# Full-bleed, vibrant, multi-colored native Odoo style (viewBox 0 0 50 50, coordinates 2..48)
SVG_DEFINITIONS = {
    "mangotek_health_suite": """<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="suiteMint" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2DD4BF"/>
      <stop offset="100%" stop-color="#0D9488"/>
    </linearGradient>
    <linearGradient id="suitePlum" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#A855F7"/>
      <stop offset="100%" stop-color="#7E22CE"/>
    </linearGradient>
  </defs>
  <!-- Top Left Facet: Vibrant Odoo Plum / Violet #875A7B / #A855F7 -->
  <path d="M7 3h20l-9 22H3a4 4 0 0 1-4-4V7a4 4 0 0 1 4-4h4Z" transform="translate(3, 1)" fill="url(#suitePlum)"/>
  <!-- Top Right Facet: Radiant Sunflower Gold #FBB945 -->
  <path d="M24 4h20a5 5 0 0 1 5 5v12a5 5 0 0 1-5 5H33l-9-22Z" fill="#FBB945"/>
  <!-- Center Diagonal Prism: Luminous Emerald Mint Gradient -->
  <path d="M15 25l10-21 18 21-10 21H15Z" fill="url(#suiteMint)"/>
  <!-- Center Shading Facet: Deep Petrol Slate #005E7A -->
  <path d="M25 25l9 21H16l9-21Z" fill="#005E7A"/>
  <!-- Bottom Right Facet: Royal Azure #088BF5 -->
  <path d="M34 25h10a5 5 0 0 1 5 5v11a5 5 0 0 1-5 5H25l9-21Z" fill="#088BF5"/>
  <!-- Bottom Left Facet: Dynamic Coral #F86126 -->
  <path d="M4 25h12l-9 21H6a5 5 0 0 1-5-5V30a5 5 0 0 1 5-5Z" transform="translate(2, 0)" fill="#F86126"/>
  <!-- Big Central Medical Cross Emblem (Crisp White + Emerald Core) -->
  <g transform="translate(0, 0)">
    <rect x="21" y="14" width="8" height="22" rx="2.5" fill="#FFFFFF"/>
    <rect x="14" y="21" width="22" height="8" rx="2.5" fill="#FFFFFF"/>
    <rect x="22.5" y="15.5" width="5" height="19" rx="1.5" fill="#0D9488"/>
    <rect x="15.5" y="22.5" width="19" height="5" rx="1.5" fill="#0D9488"/>
    <circle cx="25" cy="25" r="2.5" fill="#FFFFFF"/>
  </g>
</svg>""",

    "health_base": """<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="basePlum" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#985184"/>
      <stop offset="100%" stop-color="#6B21A8"/>
    </linearGradient>
    <linearGradient id="baseEmerald" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2DD4BF"/>
      <stop offset="100%" stop-color="#0F766E"/>
    </linearGradient>
  </defs>
  <!-- Main Bold Healthcare Base Folio (Full Bleed) -->
  <rect x="3" y="3" width="44" height="44" rx="8" fill="url(#basePlum)"/>
  <!-- Top Right Geometric Facet in Emerald Mint -->
  <path d="M21 3h18a8 8 0 0 1 8 8v18l-26-26Z" fill="url(#baseEmerald)"/>
  <!-- Golden Patient Badge Banner Tab -->
  <path d="M3 13h12a4 4 0 0 1 4 4v16a4 4 0 0 1-4 4H3V13Z" fill="#FBB945"/>
  <!-- Big Dimensional Medical Cross (White Base + Vibrant Layered Core) -->
  <rect x="21" y="11" width="10" height="28" rx="3" fill="#FFFFFF"/>
  <rect x="12" y="20" width="28" height="10" rx="3" fill="#FFFFFF"/>
  <rect x="23" y="13" width="6" height="24" rx="2" fill="#0D9488"/>
  <rect x="14" y="22" width="24" height="6" rx="2" fill="#0D9488"/>
  <circle cx="26" cy="25" r="3" fill="#FFFFFF"/>
  <circle cx="26" cy="25" r="1.5" fill="#FBB945"/>
  <!-- Bottom Foundation Accent Bar in Deep Slate -->
  <path d="M3 39h44a8 8 0 0 1-8 8H11a8 8 0 0 1-8-8Z" fill="#005E7A" fill-opacity="0.6"/>
</svg>""",

    "health_emr": """<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="emrBlue" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8"/>
      <stop offset="100%" stop-color="#0284C7"/>
    </linearGradient>
    <linearGradient id="emrEcg" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#F43F5E"/>
      <stop offset="50%" stop-color="#F59E0B"/>
      <stop offset="100%" stop-color="#10B981"/>
    </linearGradient>
  </defs>
  <!-- Clipboard Outer Frame in Vibrant Azure Blue -->
  <rect x="4" y="4" width="42" height="42" rx="7" fill="url(#emrBlue)"/>
  <!-- Top Metallic Binder Clip in Amethyst Violet #875A7B -->
  <rect x="15" y="2" width="20" height="7" rx="3" fill="#875A7B"/>
  <rect x="19" y="3.5" width="12" height="4" rx="1.5" fill="#F1F5F9"/>
  <!-- Inner Clean White Clinical Chart -->
  <rect x="7" y="11" width="36" height="32" rx="4" fill="#FFFFFF"/>
  <!-- Header Patient Details Bar in Mint & Gold -->
  <rect x="10" y="14" width="16" height="3" rx="1.5" fill="#0D9488"/>
  <rect x="28" y="14" width="12" height="3" rx="1.5" fill="#FBB945"/>
  <!-- Bold Multi-Color ECG Cardiac Waveform (Hero Element) -->
  <path d="M8 28h8l3-10 5 18 4-11 3 5h9" fill="none" stroke="url(#emrEcg)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- SOAP Clinical Prescription Lines -->
  <line x1="10" y1="36" x2="26" y2="36" stroke="#0284C7" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="29" y1="36" x2="38" y2="36" stroke="#94A3B8" stroke-width="2.5" stroke-linecap="round"/>
  <!-- Heartbeat Mini Pulse Dot in Ruby Red -->
  <circle cx="40" cy="28" r="2.5" fill="#F43F5E"/>
</svg>""",

    "health_appointment": """<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="apptSky" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8"/>
      <stop offset="100%" stop-color="#0284C7"/>
    </linearGradient>
    <linearGradient id="appGold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FDE047"/>
      <stop offset="100%" stop-color="#F59E0B"/>
    </linearGradient>
  </defs>
  <!-- Background Clinic Reception Portal (Bold Full-Bleed) -->
  <rect x="3" y="4" width="44" height="42" rx="8" fill="url(#apptSky)"/>
  <!-- Diagonal Portal Wing in Emerald Mint -->
  <path d="M3 4h20l24 24v10a8 8 0 0 1-8 8H19L3 20V4Z" fill="#10B981" fill-opacity="0.35"/>
  <!-- Large Prominent Queue Ticket in Golden Amber -->
  <rect x="9" y="12" width="32" height="27" rx="5" fill="url(#appGold)"/>
  <!-- Ticket Notch Cutouts -->
  <circle cx="9" cy="25" r="3.5" fill="#0284C7"/>
  <circle cx="41" cy="25" r="3.5" fill="#0284C7"/>
  <!-- Bold Queue Ticket ID "A1" in Pure Midnight Navy -->
  <path d="M16 31l5-12 5 12m-8-4h6" fill="none" stroke="#0F172A" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M30 21v10m-3-7l3-3" fill="none" stroke="#0F172A" stroke-width="3" stroke-linecap="round"/>
  <!-- Live Calling Beacon / TV Indicator in Emerald Green -->
  <circle cx="25" cy="8" r="3" fill="#34D399"/>
  <circle cx="25" cy="8" r="1.5" fill="#FFFFFF"/>
</svg>""",

    "health_pharmacy": """<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="pharmCoral" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FB7185"/>
      <stop offset="100%" stop-color="#E11D48"/>
    </linearGradient>
    <linearGradient id="pharmTeal" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2DD4BF"/>
      <stop offset="100%" stop-color="#0F766E"/>
    </linearGradient>
    <linearGradient id="pharmGold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FCD34D"/>
      <stop offset="100%" stop-color="#F59E0B"/>
    </linearGradient>
  </defs>
  <!-- Background Dispensary Canvas in Deep Petrol Slate -->
  <rect x="3" y="3" width="44" height="44" rx="8" fill="#0F172A"/>
  <!-- Golden Apothecary Mortar Bowl (Large, Bold & Seamless) -->
  <path d="M9 24h32c0 10-6 17-16 17S9 34 9 24Z" fill="url(#pharmGold)"/>
  <!-- Mortar Lip Rim in Pure White -->
  <rect x="7" y="21.5" width="36" height="5" rx="2.5" fill="#FFFFFF"/>
  <!-- Plum Pestle Angled Diagonal -->
  <path d="M29 9l8-5 5 7-8 10-5-12Z" fill="#875A7B"/>
  <!-- Giant Diagonal Dual-Color Capsule in Coral & Emerald Mint -->
  <g transform="translate(19, 13) rotate(42)">
    <!-- Top Half: Vibrant Coral Red -->
    <rect x="-8" y="-15" width="16" height="15" rx="8" fill="url(#pharmCoral)"/>
    <!-- Bottom Half: Radiant Emerald Mint -->
    <rect x="-8" y="0" width="16" height="15" rx="8" fill="url(#pharmTeal)"/>
    <!-- Center Dividing Band in Pure White -->
    <line x1="-8" y1="0" x2="8" y2="0" stroke="#FFFFFF" stroke-width="2.5"/>
    <!-- Capsule Gloss Reflection -->
    <line x1="-3" y1="-10" x2="-3" y2="-3" stroke="#FFFFFF" stroke-width="1.5" stroke-linecap="round"/>
  </g>
</svg>""",

    "health_billing": """<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="billPlum" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#A855F7"/>
      <stop offset="100%" stop-color="#6B21A8"/>
    </linearGradient>
    <linearGradient id="billGold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FDE047"/>
      <stop offset="100%" stop-color="#D97706"/>
    </linearGradient>
  </defs>
  <!-- Main Invoicing Ledger in Odoo Plum (Full Bleed) -->
  <rect x="3" y="3" width="44" height="44" rx="8" fill="url(#billPlum)"/>
  <!-- Diagonal Accounting Split Facet in Royal Azure -->
  <path d="M3 3h20l24 24v12a8 8 0 0 1-8 8H21L3 21V3Z" fill="#0284C7" fill-opacity="0.45"/>
  <!-- Inner White Receipt Folio -->
  <rect x="7" y="10" width="36" height="32" rx="4" fill="#FFFFFF"/>
  <!-- Dynamic QRIS Scan Target in Vivid Coral #F86126 -->
  <rect x="11" y="14" width="12" height="12" rx="3" fill="#F86126"/>
  <rect x="13.5" y="16.5" width="7" height="7" rx="1.5" fill="#FFFFFF"/>
  <rect x="15" y="18" width="4" height="4" fill="#F86126"/>
  <!-- Itemized Clinical Tariffs & Doctor Fees in Emerald & Slate -->
  <line x1="26" y1="16" x2="39" y2="16" stroke="#0D9488" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="26" y1="22" x2="36" y2="22" stroke="#64748B" stroke-width="2.5" stroke-linecap="round"/>
  <!-- Paid Settlement Bar in Golden Amber -->
  <rect x="11" y="30" width="28" height="7" rx="2.5" fill="url(#billGold)"/>
  <line x1="15" y1="33.5" x2="35" y2="33.5" stroke="#0F172A" stroke-width="2" stroke-linecap="round"/>
</svg>""",

    "health_inpatient": """<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="inpAzure" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8"/>
      <stop offset="100%" stop-color="#0369A1"/>
    </linearGradient>
    <linearGradient id="inpMint" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#34D399"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>
  </defs>
  <!-- Hospital Ward Pavilion Architecture (Full Bleed) -->
  <rect x="3" y="5" width="44" height="41" rx="8" fill="url(#inpAzure)"/>
  <!-- Architectural Diagonal Skylight Facet in Sky Cyan -->
  <path d="M3 5h20l24 24v9a8 8 0 0 1-8 8H21L3 21V5Z" fill="#0284C7" fill-opacity="0.4"/>
  <!-- Large High-Contrast Inpatient Hospital Bed in Pure White -->
  <path d="M8 26v12m0-5h34m0-7v12" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="round"/>
  <!-- Ergonomic Medical Mattress in Vibrant Emerald Mint -->
  <rect x="12" y="27" width="26" height="5" rx="2" fill="url(#inpMint)"/>
  <!-- Comfortable Patient Pillow in Golden Amber -->
  <rect x="12" y="23" width="9" height="5" rx="2" fill="#FBB945"/>
  <!-- Real-Time Bed Occupancy Beacon (BOR Status) -->
  <circle cx="36" cy="15" r="4.5" fill="#FBB945"/>
  <circle cx="36" cy="15" r="2" fill="#FFFFFF"/>
</svg>""",

    "health_emergency": """<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="erCoral" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FF4B4B"/>
      <stop offset="100%" stop-color="#BE123C"/>
    </linearGradient>
    <linearGradient id="erGold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FDE047"/>
      <stop offset="100%" stop-color="#EA580C"/>
    </linearGradient>
  </defs>
  <!-- Bold Emergency Shield Frame in Dark Midnight Slate -->
  <rect x="3" y="3" width="44" height="44" rx="8" fill="#0B0F19"/>
  <!-- Vibrant Emergency Red Background Halo -->
  <path d="M25 4l18 6v15c0 13-9 21-18 24C16 46 7 38 7 25V10l18-6Z" fill="#1E293B"/>
  <!-- Large Six-Pointed Star of Life in Vivid Crimson Coral -->
  <g transform="translate(25, 24)" fill="url(#erCoral)">
    <rect x="-5" y="-17" width="10" height="34" rx="3.5"/>
    <rect x="-5" y="-17" width="10" height="34" rx="3.5" transform="rotate(60)"/>
    <rect x="-5" y="-17" width="10" height="34" rx="3.5" transform="rotate(120)"/>
    <!-- Crisp White Interlocking Border for 3D Contrast -->
    <circle cx="0" cy="0" r="6" fill="#FFFFFF"/>
  </g>
  <!-- Giant Resuscitation Lightning Bolt in Sunflower Gold -->
  <polygon points="25,10 19,25 25,25 22,38 31,21 25,21" fill="url(#erGold)"/>
</svg>""",

    "health_laboratory": """<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="labTeal" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2DD4BF"/>
      <stop offset="100%" stop-color="#0F766E"/>
    </linearGradient>
    <linearGradient id="labCyan" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8"/>
      <stop offset="100%" stop-color="#0284C7"/>
    </linearGradient>
  </defs>
  <!-- Deep Slate Laboratory Background -->
  <rect x="3" y="3" width="44" height="44" rx="8" fill="#0F172A"/>
  <!-- Diagonal Analysis Prism in Royal Blue -->
  <path d="M3 3h22l22 22v14a8 8 0 0 1-8 8H21L3 21V3Z" fill="#0284C7" fill-opacity="0.3"/>
  <!-- Left Specimen Tube in Crisp White & Luminous Sky Cyan -->
  <rect x="11" y="10" width="10" height="28" rx="5" fill="#FFFFFF"/>
  <rect x="11" y="22" width="10" height="16" rx="5" fill="url(#labCyan)"/>
  <rect x="9" y="8" width="14" height="4" rx="2" fill="#FFFFFF"/>
  <!-- Right Specimen Tube in Crisp White & Emerald Mint -->
  <rect x="29" y="13" width="10" height="25" rx="5" fill="#FFFFFF"/>
  <rect x="29" y="24" width="10" height="14" rx="5" fill="url(#labTeal)"/>
  <rect x="27" y="11" width="14" height="4" rx="2" fill="#FFFFFF"/>
  <!-- Meniscus Diagnostic Glow Bubbles in Amber Gold -->
  <circle cx="16" cy="27" r="2" fill="#FBB945"/>
  <circle cx="34" cy="29" r="2" fill="#FBB945"/>
  <circle cx="25" cy="18" r="2" fill="#FFFFFF"/>
</svg>""",

    "health_radiology": """<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="radAzure" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8"/>
      <stop offset="100%" stop-color="#0284C7"/>
    </linearGradient>
  </defs>
  <!-- Radiology Illuminator Lightbox (Full Bleed) -->
  <rect x="3" y="3" width="44" height="44" rx="8" fill="#0B1120" stroke="#334155" stroke-width="2"/>
  <!-- Inner Luminescent Blue Diagnostic Radiance -->
  <rect x="6" y="6" width="38" height="38" rx="5" fill="url(#radAzure)" fill-opacity="0.4"/>
  <!-- Skeletal Thoracic Ribcage in Bold Crisp White -->
  <path d="M25 10v29" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="round"/>
  <path d="M14 17c6 4 16 4 22 0" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" fill="none"/>
  <path d="M12 24c7 4 19 4 26 0" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" fill="none"/>
  <path d="M14 31c6 4 16 4 22 0" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" fill="none"/>
  <!-- Radiation Ionizing Aperture Emblem in Sunflower Gold -->
  <circle cx="38" cy="12" r="4" fill="#FBB945"/>
  <circle cx="38" cy="12" r="2" fill="#0B1120"/>
</svg>""",

    "health_satusehat": """<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="ssMint" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2DD4BF"/>
      <stop offset="100%" stop-color="#0D9488"/>
    </linearGradient>
    <linearGradient id="ssAzure" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8"/>
      <stop offset="100%" stop-color="#0284C7"/>
    </linearGradient>
  </defs>
  <!-- National Cloud Shield in Emerald Mint (Full Bleed) -->
  <path d="M25 3l20 7v17c0 13-9 22-20 25C14 49 5 40 5 27V10l20-7Z" fill="url(#ssMint)"/>
  <!-- Right Facet Wing in Royal Azure Blue -->
  <path d="M25 3l20 7v17c0 13-9 22-20 25V3Z" fill="url(#ssAzure)"/>
  <!-- Inner Deep Shield Core in Midnight Petrol #005E7A -->
  <path d="M25 8l15 5.5v13c0 10-6.5 17-15 20-8.5-3-15-10-15-20V13.5L25 8Z" fill="#005E7A"/>
  <!-- Interconnected HL7 FHIR Interoperability Nodes in Crisp White & Gold -->
  <circle cx="25" cy="17" r="3.5" fill="#FBB945"/>
  <circle cx="16" cy="27" r="3" fill="#FFFFFF"/>
  <circle cx="34" cy="27" r="3" fill="#FFFFFF"/>
  <circle cx="20" cy="38" r="3" fill="#FFFFFF"/>
  <circle cx="30" cy="38" r="3" fill="#FFFFFF"/>
  <line x1="25" y1="17" x2="16" y2="27" stroke="#FFFFFF" stroke-width="2.5"/>
  <line x1="25" y1="17" x2="34" y2="27" stroke="#FFFFFF" stroke-width="2.5"/>
  <line x1="16" y1="27" x2="20" y2="38" stroke="#FFFFFF" stroke-width="2.5"/>
  <line x1="34" y1="27" x2="30" y2="38" stroke="#FFFFFF" stroke-width="2.5"/>
  <line x1="20" y1="38" x2="30" y2="38" stroke="#FFFFFF" stroke-width="2.5"/>
</svg>""",

    "health_bpjs": """<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bpjsBlue" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8"/>
      <stop offset="100%" stop-color="#0284C7"/>
    </linearGradient>
    <linearGradient id="bpjsMint" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2DD4BF"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>
  </defs>
  <!-- Bi-Color Health Security Shield (Full Bleed) -->
  <path d="M25 3l20 7v17c0 13-9 22-20 25C14 49 5 40 5 27V10l20-7Z" fill="url(#bpjsBlue)"/>
  <!-- Right Wing in Luminous Emerald Mint -->
  <path d="M25 3l20 7v17c0 13-9 22-20 25V3Z" fill="url(#bpjsMint)"/>
  <!-- Inner Shield Core in Deep Navy Slate -->
  <path d="M25 8l15 5.5v13c0 10-6.5 17-15 20-8.5-3-15-10-15-20V13.5L25 8Z" fill="#0F172A"/>
  <!-- Golden Bridge Gateway Arch #FBB945 -->
  <path d="M14 36c0-7 5-13 11-13s11 6 11 13" fill="none" stroke="#FBB945" stroke-width="3" stroke-linecap="round"/>
  <!-- Giant Verification Checkmark in Crisp White -->
  <path d="M18 24l5 5 11-12" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",

    "health_surgery": """<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="surgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0284C7"/>
      <stop offset="100%" stop-color="#0F766E"/>
    </linearGradient>
    <linearGradient id="coralAccent" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F87171"/>
      <stop offset="100%" stop-color="#DC2626"/>
    </linearGradient>
  </defs>
  <!-- Main Surgical Theater Folio -->
  <rect x="3" y="3" width="44" height="44" rx="8" fill="url(#surgGrad)"/>
  <!-- Top Right Geometric Facet in Coral -->
  <path d="M21 3h18a8 8 0 0 1 8 8v18l-26-26Z" fill="url(#coralAccent)"/>
  <!-- Operating Light Beam Dome -->
  <ellipse cx="25" cy="14" rx="14" ry="4" fill="#FFFFFF" fill-opacity="0.9"/>
  <polygon points="11,14 4,42 46,42 39,14" fill="#FFFFFF" fill-opacity="0.12"/>
  <!-- Scalpel Blade & Forceps Cross -->
  <g transform="translate(25, 27)">
    <line x1="-12" y1="12" x2="12" y2="-12" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="round"/>
    <polygon points="9,-9 14,-14 12,-7" fill="#FFFFFF"/>
    <line x1="-12" y1="-12" x2="12" y2="12" stroke="#FBB945" stroke-width="3" stroke-linecap="round"/>
    <circle cx="0" cy="0" r="3.5" fill="#0F172A"/>
    <circle cx="0" cy="0" r="1.5" fill="#38BDF8"/>
  </g>
</svg>""",

    "health_bpjs_vclaim": """<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="vclaimNavy" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1E3A8A"/>
      <stop offset="100%" stop-color="#0369A1"/>
    </linearGradient>
    <linearGradient id="vclaimGreen" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10B981"/>
      <stop offset="100%" stop-color="#047857"/>
    </linearGradient>
  </defs>
  <!-- Base Shield Canvas -->
  <path d="M25 3l20 7v17c0 13-9 22-20 25C14 49 5 40 5 27V10l20-7Z" fill="url(#vclaimNavy)"/>
  <!-- Right Wing Emerald -->
  <path d="M25 3l20 7v17c0 13-9 22-20 25V3Z" fill="url(#vclaimGreen)"/>
  <!-- White Inset SEP Document -->
  <rect x="14" y="14" width="22" height="26" rx="3" fill="#FFFFFF"/>
  <rect x="18" y="18" width="14" height="2.5" rx="1" fill="#0284C7"/>
  <rect x="18" y="23" width="10" height="2" rx="1" fill="#64748B"/>
  <rect x="18" y="27" width="14" height="2" rx="1" fill="#64748B"/>
  <!-- Golden VClaim Stamp / Seal -->
  <circle cx="28" cy="33" r="5" fill="#FBB945"/>
  <polyline points="26,33 27.5,34.5 30,31.5" fill="none" stroke="#FFFFFF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",

    "health_inacbg": """<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="inacbgBase" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#7C3AED"/>
      <stop offset="100%" stop-color="#4338CA"/>
    </linearGradient>
    <linearGradient id="goldCoins" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FDE047"/>
      <stop offset="100%" stop-color="#D97706"/>
    </linearGradient>
  </defs>
  <!-- Main Base Folio -->
  <rect x="3" y="3" width="44" height="44" rx="8" fill="url(#inacbgBase)"/>
  <!-- Case-Mix 3-Tier Grouping Blocks -->
  <!-- Level 1 (Light) -->
  <rect x="9" y="30" width="8" height="12" rx="2" fill="#2DD4BF"/>
  <!-- Level 2 (Medium) -->
  <rect x="19" y="22" width="8" height="20" rx="2" fill="#38BDF8"/>
  <!-- Level 3 (Severe) -->
  <rect x="29" y="14" width="8" height="28" rx="2" fill="#F87171"/>
  <!-- Golden E-Klaim Grouper Emblem Overlay -->
  <circle cx="36" cy="14" r="8" fill="url(#goldCoins)"/>
  <text x="36" y="18" font-size="10" font-weight="900" fill="#78350F" text-anchor="middle">₹</text>
  <!-- Analytic Connecting Trendline -->
  <polyline points="13,28 23,20 33,12" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="13" cy="28" r="2" fill="#FFFFFF"/>
  <circle cx="23" cy="20" r="2" fill="#FFFFFF"/>
</svg>""",
}

def render_svg_to_png(svg_str, width, height):
    png_bytes = resvg_py.svg_to_bytes(svg_str)
    img = Image.open(io.BytesIO(png_bytes))
    if img.size != (width, height):
        img = img.resize((width, height), Image.LANCZOS)
    return img

def main():
    print("=" * 70)
    print(" 🎨 MANGOTEK HEALTH SUITE — REBUILDING NATIVE ODOO APP ICONS (V2)")
    print("=" * 70)

    # 1. Suite Master Icon
    print("\n📦 Updating Master Suite Assets...")
    suite_svg_path = os.path.join(ICONS_DIR, "mangotek_health_suite.svg")
    with open(suite_svg_path, "w", encoding="utf-8") as f:
        f.write(SVG_DEFINITIONS["mangotek_health_suite"])

    for size in [50, 100, 512, 1024]:
        png_path = os.path.join(ICONS_DIR, f"mangotek_health_suite_{size}.png")
        img = render_svg_to_png(SVG_DEFINITIONS["mangotek_health_suite"], size, size)
        img.save(png_path, "PNG", optimize=True)
        print(f"  ✅ Rendered PNG ({size}x{size}): assets/icons/mangotek_health_suite_{size}.png")

    # 2. Per-Module Icons
    print("\n📦 Updating Per-Module Icons (Vibrant Full-Bleed 95% Canvas Fill)...")
    for mod_name, svg_content in SVG_DEFINITIONS.items():
        if mod_name == "mangotek_health_suite":
            continue

        svg_file = os.path.join(ICONS_DIR, f"{mod_name}.svg")
        with open(svg_file, "w", encoding="utf-8") as f:
            f.write(svg_content)

        p100 = os.path.join(ICONS_DIR, f"{mod_name}_100.png")
        p512 = os.path.join(ICONS_DIR, f"{mod_name}_512.png")
        img100 = render_svg_to_png(svg_content, 100, 100)
        img512 = render_svg_to_png(svg_content, 512, 512)
        img100.save(p100, "PNG", optimize=True)
        img512.save(p512, "PNG", optimize=True)

        # Deploy 100x100 directly to module static/description/icon.png
        mod_icon_path = os.path.join(REPO_ROOT, mod_name, "static", "description", "icon.png")
        img100.save(mod_icon_path, "PNG", optimize=True)
        print(f"  ✅ Rebuilt & Deployed [{mod_name}] -> {mod_name}/static/description/icon.png")

    print("\n🎉 ALL ICONS SUCCESSFULLY REBUILT IN NATIVE ODOO VIBRANT STYLE!")

if __name__ == "__main__":
    main()
