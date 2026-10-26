"""CSS global de la aplicación."""
import streamlit as st

from .theme import get_theme_palette


def inject_css():
    dark_mode = st.session_state.get("dark_mode", False)
    palette = get_theme_palette(dark_mode)
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stApp {{ font-family:'Plus Jakarta Sans',sans-serif; color:{palette['ink']}; }}
.stApp {{ background:{palette['bg']}; }}
header[data-testid="stHeader"] {{
    display:block !important;
    height:0 !important;
    min-height:0 !important;
    background:transparent !important;
}}
header[data-testid="stHeader"] [data-testid="stToolbar"] {{
    height:0;
    overflow:visible;
}}
header[data-testid="stHeader"] [data-testid="stStatusWidget"],
header[data-testid="stHeader"] [data-testid="stMainMenu"],
header[data-testid="stHeader"] [data-testid="stToolbarActions"] {{
    display:none !important;
}}
header[data-testid="stHeader"] [data-testid="stExpandSidebarButton"],
header[data-testid="stHeader"] button[data-testid="stBaseButton-headerNoPadding"] {{
    position:fixed;
    top:.35rem;
    left:.35rem;
    z-index:1001;
    color:{palette['primary']} !important;
}}
header[data-testid="stHeader"] [data-testid="stExpandSidebarButton"] span,
header[data-testid="stHeader"] button[data-testid="stBaseButton-headerNoPadding"] span {{
    color:{palette['primary']} !important;
}}
.block-container {{ padding:1.1rem 1.6rem 2rem; max-width:100%; }}

/* Sidebar */
section[data-testid="stSidebar"] {{
    width:254px !important;
    min-width:254px !important;
}}
section[data-testid="stSidebar"][aria-expanded="false"] {{
    width:0 !important;
    min-width:0 !important;
}}
[data-testid="stSidebar"], section[data-testid="stSidebar"],
[data-testid="stSidebar"] > div, section[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] section, [data-testid="stSidebar"] .block-container {{
    background:{palette['navy']} !important;
}}
[data-testid="stSidebarContent"], [data-testid="stSidebarUserContent"],
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
    background:{palette['navy']} !important;
}}
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] button {{
    visibility:visible !important;
}}
[data-testid="stSidebar"] .block-container {{
    width:100% !important;
    box-sizing:border-box;
    padding:1.25rem .85rem 1.1rem !important;
    margin-top:0 !important;
}}
[data-testid="stSidebar"] *, section[data-testid="stSidebar"] * {{ color:{palette['sidebar_item']}; }}
[data-testid="stSidebar"] a, [data-testid="stSidebar"] a:visited,
section[data-testid="stSidebar"] a, section[data-testid="stSidebar"] a:visited {{ color:{palette['sidebar_item']} !important; }}
[data-testid="stSidebar"] a:hover, section[data-testid="stSidebar"] a:hover {{ color:#fff !important; }}
[data-testid="stSidebar"] .nav a.on, section[data-testid="stSidebar"] .nav a.on {{ color:#fff !important; }}
[data-testid="stSidebar"] button {{ color:#fff !important; }}
[data-testid="stSidebar"] button svg {{ color:#fff !important; stroke:#fff !important; }}
.nav-title {{ font-size:.72rem; letter-spacing:.12em; text-transform:uppercase; color:{palette['sidebar_heading']} !important; margin:9px 0 5px 8px; font-weight:700; }}
[data-testid="stSidebar"] [class*="st-key-nav_group_"] {{
    box-sizing:border-box;
    width:100%;
    padding:6px;
    margin:0 0 6px;
    border:1px solid rgba(255,255,255,0.05);
    border-radius:14px;
    background:rgba(255,255,255,0.02);
    gap:0 !important;
}}
[data-testid="stSidebar"] .stButton {{
    width:100% !important;
    margin:0 !important;
    padding:0 !important;
    display:block !important;
}}
[data-testid="stSidebar"] .stButton > button {{
    width:100% !important;
    height:36px !important;
    min-height:36px !important;
    margin:2px 0 !important;
    padding:7px 14px !important;
    border-radius:10px !important;
    border:0 !important;
    background:transparent !important;
    color:{palette['sidebar_item']} !important;
    font-weight:500 !important;
    font-size:.88rem !important;
    text-align:left !important;
    display:flex !important;
    align-items:center !important;
    justify-content:flex-start !important;
    gap:10px !important;
    box-shadow:none !important;
    line-height:1.15 !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background:rgba(255,255,255,.06) !important;
    color:#fff !important;
}}
[data-testid="stSidebar"] .stButton > button p,
[data-testid="stSidebar"] .stButton > button div {{
    margin:0 !important;
}}
[data-testid="stSidebar"] .stButton > button > div {{
    width:100% !important;
    justify-content:flex-start !important;
}}
[data-testid="stSidebar"] .stButton > button[kind="primary"],
[data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"] {{
    background:{palette['primary']} !important;
    color:#fff !important;
    font-weight:700 !important;
}}
.brand {{ font-size:1.35rem; font-weight:800; color:#fff !important; display:flex; gap:10px; align-items:center; }}
.brand small {{ display:block; font-size:.78rem; font-weight:400; color:{palette['sidebar_heading']} !important; line-height:1.2; }}
.nav a {{ display:flex; gap:12px; align-items:center; padding:11px 14px; border-radius:10px;
          text-decoration:none; margin:4px 0; font-weight:500; font-size:.88rem; white-space:nowrap; }}
.nav-icon {{ width:22px; display:inline-flex; justify-content:center; font-size:1.15rem; line-height:1; }}
.nav a.on {{ background:{palette['primary']}; color:#fff; font-weight:700; }}
.ai-card {{ border:1px solid #3A3E8A; border-radius:8px; padding:14px; margin-top:190px; font-size:.82rem; }}
.ai-card b {{ color:#fff; font-size:.9rem; }}

/* Paneles */
[data-testid="stVerticalBlockBorderWrapper"] {{ background:{palette['panel']}; border-radius:14px; border-color:{palette['line']}; }}
.title {{ font-size:2rem; font-weight:800; margin:0; }}
.subtitle {{ color:{palette['muted']}; margin-bottom:12px; }}
.panel-title {{ font-weight:800; font-size:1.05rem; margin-bottom:8px; }}
.user {{ display:flex; gap:10px; align-items:center; justify-content:flex-end; }}
.user .av {{ width:38px; height:38px; border-radius:50%; background:{palette['primary_soft']};
             display:flex; align-items:center; justify-content:center; }}

/* Stepper */
.stepper {{ display:flex; align-items:center; gap:10px; background:{palette['panel']}; border-radius:14px; padding:14px 18px; margin-bottom:12px; }}
.step {{ display:flex; align-items:center; gap:8px; font-weight:600; color:{palette['muted']}; }}
.step i {{ width:32px; height:32px; border-radius:50%; border:1px solid {palette['line']}; display:flex; align-items:center;
           justify-content:center; font-style:normal; font-size:.85rem; }}
.step.done i {{ background:#2FB36B; color:#fff; border:0; }}
.step.on {{ color:{palette['primary']}; }}
.step.on i {{ background:{palette['primary']}; color:#fff; border:0; }}
.line {{ flex:1; height:1px; background:{palette['line']}; }}

/* Tarjeta de post */
.pcard {{ display:flex; gap:12px; padding:10px; border:1px solid {palette['line']}; border-radius:12px; margin-top:8px; }}
.pcard.sel {{ border:1.5px solid {palette['primary']}; background:{palette['soft']}; }}
.pcard .meta {{ flex:1; min-width:0; }}
.pcard .t {{ font-weight:700; font-size:.9rem; }}
.pcard .c {{ color:{palette['muted']}; font-size:.78rem; }}
.badge {{ display:inline-block; padding:2px 10px; border-radius:99px; font-size:.72rem; font-weight:600; margin-top:6px; }}
.pcard .ago {{ float:right; color:{palette['muted']}; font-size:.72rem; margin-top:10px; }}

/* Vista previa */
.ig {{ border:1px solid {palette['line']}; border-radius:12px; padding:12px; }}
.ig .h {{ display:flex; gap:10px; align-items:center; margin-bottom:8px; }}
.ig .h .a {{ width:34px; height:34px; border-radius:50%; background:{palette['navy']}; color:#fff;
             display:flex; align-items:center; justify-content:center; }}
.ig .cap {{ font-size:.82rem; line-height:1.45; margin-top:6px; }}
.ready {{ background:#EAF8F0; border:1px solid #BFE8CE; border-radius:12px; padding:12px 14px;
          font-size:.8rem; color:#1E7B48; margin-top:12px; }}
.ready b {{ display:block; margin-bottom:2px; }}
/* =========================================================================
   SISTEMA DE BOTONES PREMIUM, ACCESIBLES Y ULTRA-VISIBLES
   ========================================================================= */

/* Regla base universal para TODOS los botones */
.stButton, .stButton > button, button[data-testid*="BaseButton"], button[data-testid*="baseButton"] {{
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    line-height: 1.25 !important;
    letter-spacing: 0.01em !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}}

/* Forzar que cualquier elemento interno (p, span, div, svg) herede el color y peso */
.stButton button *,
.stButton button p,
.stButton button span,
.stButton button div,
button[data-testid*="BaseButton"] *,
button[data-testid*="baseButton"] * {{
    color: inherit !important;
    font-weight: inherit !important;
}}

/* Botones Secundarios / Por Defecto (Alto contraste, fondo blanco, texto e icono legibles) */
.stButton > button,
.stButton > button[kind="secondary"],
.stButton > button[data-testid*="secondary"],
button[data-testid*="BaseButton-secondary"],
button[data-testid*="baseButton-secondary"] {{
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
    color: #3730A3 !important;
    border: 1.5px solid #C7D2FE !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
}}

.stButton > button:hover,
.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid*="secondary"]:hover,
button[data-testid*="BaseButton-secondary"]:hover,
button[data-testid*="baseButton-secondary"]:hover {{
    background-color: #EEF2FF !important;
    background: #EEF2FF !important;
    color: #312E81 !important;
    border-color: #6366F1 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.16) !important;
}}

.stButton > button:active,
.stButton > button[kind="secondary"]:active,
.stButton > button[data-testid*="secondary"]:active,
button[data-testid*="BaseButton-secondary"]:active,
button[data-testid*="baseButton-secondary"]:active {{
    background-color: #E0E7FF !important;
    background: #E0E7FF !important;
    border-color: #4F46E5 !important;
    transform: translateY(0) !important;
}}

/* Botones Primarios (Vibrantes, azul/violeta con texto blanco puro) */
.stButton > button[kind="primary"],
.stButton > button[data-testid*="primary"],
button[data-testid*="BaseButton-primary"],
button[data-testid*="baseButton-primary"] {{
    background: linear-gradient(135deg, #5B4BDB 0%, #4737C8 100%) !important;
    background-color: #5B4BDB !important;
    color: #FFFFFF !important;
    border: 1.5px solid #372A99 !important;
    box-shadow: 0 4px 14px rgba(91, 75, 219, 0.32) !important;
}}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid*="primary"]:hover,
button[data-testid*="BaseButton-primary"]:hover,
button[data-testid*="baseButton-primary"]:hover {{
    background: linear-gradient(135deg, #4F3ECC 0%, #3B2BB8 100%) !important;
    background-color: #4F3ECC !important;
    color: #FFFFFF !important;
    border-color: #2F2188 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(91, 75, 219, 0.45) !important;
}}

.stButton > button[kind="primary"]:active,
.stButton > button[data-testid*="primary"]:active,
button[data-testid*="BaseButton-primary"]:active,
button[data-testid*="baseButton-primary"]:active {{
    background: #372A99 !important;
    transform: translateY(0) !important;
}}

/* Acciones de Curaduría 1: Botón APROBAR (Verde) */
[class*="st-key-btn_ap_"] button {{
    border-radius: 10px !important;
    font-weight: 800 !important;
}}
[class*="st-key-btn_ap_"] button[data-testid*="secondary"],
[class*="st-key-btn_ap_"] button[kind="secondary"] {{
    background-color: #ECFDF5 !important;
    background: #ECFDF5 !important;
    color: #065F46 !important;
    border: 1.5px solid #10B981 !important;
    box-shadow: 0 1px 3px rgba(16, 185, 129, 0.12) !important;
}}
[class*="st-key-btn_ap_"] button[data-testid*="secondary"]:hover,
[class*="st-key-btn_ap_"] button[kind="secondary"]:hover {{
    background-color: #D1FAE5 !important;
    background: #D1FAE5 !important;
    color: #047857 !important;
    border-color: #059669 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25) !important;
}}
[class*="st-key-btn_ap_"] button[data-testid*="primary"],
[class*="st-key-btn_ap_"] button[kind="primary"] {{
    background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
    background-color: #059669 !important;
    color: #FFFFFF !important;
    border: 2px solid #047857 !important;
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.45) !important;
}}
[class*="st-key-btn_ap_"] button[data-testid*="primary"]:hover,
[class*="st-key-btn_ap_"] button[kind="primary"]:hover {{
    background: #047857 !important;
    color: #FFFFFF !important;
    transform: translateY(-1px) !important;
}}

/* Acciones de Curaduría 2: Botón DESCARTAR (Rojo) */
[class*="st-key-btn_desc_"] button {{
    border-radius: 10px !important;
    font-weight: 800 !important;
}}
[class*="st-key-btn_desc_"] button[data-testid*="secondary"],
[class*="st-key-btn_desc_"] button[kind="secondary"] {{
    background-color: #FEF2F2 !important;
    background: #FEF2F2 !important;
    color: #991B1B !important;
    border: 1.5px solid #EF4444 !important;
    box-shadow: 0 1px 3px rgba(239, 68, 68, 0.12) !important;
}}
[class*="st-key-btn_desc_"] button[data-testid*="secondary"]:hover,
[class*="st-key-btn_desc_"] button[kind="secondary"]:hover {{
    background-color: #FEE2E2 !important;
    background: #FEE2E2 !important;
    color: #7F1D1D !important;
    border-color: #DC2626 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.25) !important;
}}
[class*="st-key-btn_desc_"] button[data-testid*="primary"],
[class*="st-key-btn_desc_"] button[kind="primary"] {{
    background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%) !important;
    background-color: #DC2626 !important;
    color: #FFFFFF !important;
    border: 2px solid #B91C1C !important;
    box-shadow: 0 4px 16px rgba(239, 68, 68, 0.45) !important;
}}
[class*="st-key-btn_desc_"] button[data-testid*="primary"]:hover,
[class*="st-key-btn_desc_"] button[kind="primary"]:hover {{
    background: #B91C1C !important;
    color: #FFFFFF !important;
    transform: translateY(-1px) !important;
}}

/* Acciones de Curaduría 3: Botón LEÍDO (Índigo) */
[class*="st-key-btn_read_"] button {{
    border-radius: 10px !important;
    font-weight: 800 !important;
}}
[class*="st-key-btn_read_"] button[data-testid*="secondary"],
[class*="st-key-btn_read_"] button[kind="secondary"] {{
    background-color: #EEF2FF !important;
    background: #EEF2FF !important;
    color: #3730A3 !important;
    border: 1.5px solid #6366F1 !important;
    box-shadow: 0 1px 3px rgba(99, 102, 241, 0.12) !important;
}}
[class*="st-key-btn_read_"] button[data-testid*="secondary"]:hover,
[class*="st-key-btn_read_"] button[kind="secondary"]:hover {{
    background-color: #E0E7FF !important;
    background: #E0E7FF !important;
    color: #312E81 !important;
    border-color: #4F46E5 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25) !important;
}}
[class*="st-key-btn_read_"] button[data-testid*="primary"],
[class*="st-key-btn_read_"] button[kind="primary"] {{
    background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
    background-color: #4F46E5 !important;
    color: #FFFFFF !important;
    border: 2px solid #3730A3 !important;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.45) !important;
}}
[class*="st-key-btn_read_"] button[data-testid*="primary"]:hover,
[class*="st-key-btn_read_"] button[kind="primary"]:hover {{
    background: #3730A3 !important;
    color: #FFFFFF !important;
    transform: translateY(-1px) !important;
}}

/* Acciones de Selección de Post (pick_) */
[class*="st-key-pick_"] button {{
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    padding: 6px 12px !important;
    margin-top: 4px !important;
}}
[class*="st-key-pick_"] button[data-testid*="primary"],
[class*="st-key-pick_"] button[kind="primary"] {{
    background: #5B4BDB !important;
    color: #FFFFFF !important;
    border: 1.5px solid #4338CA !important;
    font-weight: 800 !important;
}}
[class*="st-key-pick_"] button[data-testid*="secondary"],
[class*="st-key-pick_"] button[kind="secondary"] {{
    background: #FFFFFF !important;
    color: #334155 !important;
    border: 1.5px solid #CBD5E1 !important;
    font-weight: 700 !important;
}}
[class*="st-key-pick_"] button[data-testid*="secondary"]:hover,
[class*="st-key-pick_"] button[kind="secondary"]:hover {{
    background: #F1F5F9 !important;
    border-color: #5B4BDB !important;
    color: #5B4BDB !important;
}}

/* Botones de Generador de Imagen */
[class*="st-key-btn_img_"] button {{
    background: linear-gradient(135deg, #7C3AED 0%, #5B4BDB 100%) !important;
    color: #FFFFFF !important;
    border: 1.5px solid #5B21B6 !important;
    font-weight: 700 !important;
    box-shadow: 0 3px 10px rgba(124, 58, 237, 0.3) !important;
}}
[class*="st-key-btn_img_"] button:hover {{
    background: linear-gradient(135deg, #6D28D9 0%, #4C1D95 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 14px rgba(124, 58, 237, 0.45) !important;
}}

[class*="st-key-btn_adj_"] button {{
    background: #FFFFFF !important;
    color: #3730A3 !important;
    border: 1.5px solid #A5B4FC !important;
    font-weight: 700 !important;
}}
[class*="st-key-btn_adj_"] button:hover {{
    background: #EEF2FF !important;
    border-color: #6366F1 !important;
    color: #312E81 !important;
}}

/* File Uploader button */
[data-testid="stFileUploader"] button {{
    background: #FFFFFF !important;
    color: #3730A3 !important;
    border: 1.5px solid #C7D2FE !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
}}
[data-testid="stFileUploader"] button:hover {{
    background: #EEF2FF !important;
    border-color: #5B4BDB !important;
    color: #4338CA !important;
}}

/* Segmented Control / Radio Buttons Pills */
div[data-testid="stRadio"] div[role="radiogroup"] {{
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 8px !important;
    align-items: center !important;
    background: transparent !important;
    padding: 2px 0 !important;
}}
div[data-testid="stRadio"] div[role="radiogroup"] > label {{
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: #FFFFFF !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 9999px !important;
    padding: 5px 14px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    margin: 0 !important;
    color: #334155 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
}}
div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {{
    border-color: #5B4BDB !important;
    background: #EEF2FF !important;
    color: #4338CA !important;
    transform: translateY(-1px) !important;
}}
div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {{
    display: none !important;
}}
div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {{
    background: #5B4BDB !important;
    border-color: #4338CA !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 8px rgba(91, 75, 219, 0.35) !important;
}}
div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) * {{
    color: #FFFFFF !important;
    font-weight: 800 !important;
}}
div[data-testid="stRadio"] div[role="radiogroup"] > label p {{
    margin: 0 !important;
    font-size: 0.82rem !important;
    line-height: 1.2 !important;
}}
input, textarea, [data-baseweb="select"] > div {{ background:{palette['panel']} !important; color:{palette['ink']} !important; border-color:{palette['line']} !important; border-radius:10px !important; }}
[data-testid="stMain"] [data-testid="stMarkdownContainer"] {{ color:{palette['ink']}; }}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{ color:#E6E8FF; }}

/* Modern KPI Cards & Hero Components */
.kpi-card {{
    background: {palette['panel']};
    border: 1px solid {palette['line']};
    border-radius: 16px;
    padding: 1.1rem 1.2rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
    transition: all 0.25s ease;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}}
.kpi-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(67, 75, 178, 0.08);
    border-color: {palette['primary']};
}}
.kpi-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.6rem;
}}
.kpi-icon-box {{
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: {palette['primary_soft']};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
}}
.kpi-label {{
    font-size: 0.78rem;
    font-weight: 700;
    color: {palette['muted']};
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
.kpi-value {{
    font-size: 2rem;
    font-weight: 800;
    color: {palette['ink']};
    line-height: 1.1;
    margin: 0.2rem 0;
}}
.kpi-delta {{
    font-size: 0.8rem;
    font-weight: 600;
    color: #10B981;
    display: flex;
    align-items: center;
    gap: 4px;
}}

/* Status Pills */
.status-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    line-height: 1.2;
}}
.status-pill.online {{
    background: rgba(16, 185, 129, 0.12);
    color: #059669;
    border: 1px solid rgba(16, 185, 129, 0.3);
}}
.status-pill.standby {{
    background: rgba(245, 158, 11, 0.12);
    color: #D97706;
    border: 1px solid rgba(245, 158, 11, 0.3);
}}
.status-pill.offline {{
    background: rgba(239, 68, 68, 0.12);
    color: #DC2626;
    border: 1px solid rgba(239, 68, 68, 0.3);
}}
.status-pill.oci {{
    background: rgba(249, 115, 22, 0.12);
    color: #C2410C;
    border: 1px solid rgba(249, 115, 22, 0.35);
}}
.status-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
}}
.status-dot.online {{ background: #10B981; box-shadow: 0 0 6px #10B981; }}
.status-dot.standby {{ background: #F59E0B; }}
.status-dot.offline {{ background: #EF4444; }}

/* Hero Announcement Banner */
.hero-banner {{
    background: linear-gradient(135deg, #1C2340 0%, #2A335E 100%);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.25rem 1.6rem;
    color: #FFFFFF;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}}
.hero-banner .title {{
    color: #FFFFFF !important;
    font-size: 1.4rem;
    font-weight: 800;
    margin: 0 0 4px 0;
}}
.hero-banner .desc {{
    color: #C5CEE0 !important;
    font-size: 0.88rem;
    margin: 0;
}}
.hero-tags {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}}
.hero-tag {{
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 0.78rem;
    font-weight: 600;
    color: #FFFFFF;
}}

/* Channel Cards */
.channel-card {{
    background: {palette['panel']};
    border: 1px solid {palette['line']};
    border-radius: 14px;
    padding: 1.1rem;
    position: relative;
    overflow: hidden;
    transition: all 0.2s ease;
}}
.channel-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
}}
.channel-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 5px;
    height: 100%;
}}
.channel-card.discord::before {{ background: #5865F2; }}
.channel-card.slack::before {{ background: #E01E5A; }}
.channel-card.telegram::before {{ background: #24A1DE; }}
.channel-card.oci::before {{ background: #C74634; }}

/* Live Pulse & Latency Metrics */
@keyframes pulse-green {{
    0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
    70% {{ transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }}
    100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
}}
.live-pulse {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10B981;
    animation: pulse-green 2s infinite;
    display: inline-block;
}}
.latency-bar {{
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    padding: 6px 12px;
    border-radius: 10px;
    background: {palette['panel']};
    border: 1px solid {palette['line']};
    font-size: 0.76rem;
    color: {palette['muted']};
}}
.latency-pill {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-weight: 600;
    color: {palette['ink']};
}}

/* Interactive Execution Center (motores.png proposal) */
.exec-center-wrap {{
    background: {palette['panel']};
    border: 1px solid {palette['line']};
    border-radius: 18px;
    padding: 1.4rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
    margin-top: 0.8rem;
    margin-bottom: 1.2rem;
}}
.exec-center-title {{
    font-size: 1.25rem;
    font-weight: 700;
    color: {palette['ink']};
    margin-bottom: 1.1rem;
}}
.engine-box {{
    background: {palette['bg']};
    border: 1px solid {palette['line']};
    border-radius: 14px;
    padding: 1.2rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
    box-sizing: border-box;
}}
.engine-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.8rem;
}}
.engine-title {{
    font-size: 1.05rem;
    font-weight: 700;
    color: {palette['ink']};
    line-height: 1.3;
}}
.engine-subtitle {{
    font-size: 0.85rem;
    font-weight: 500;
    color: {palette['muted']};
}}
.n8n-badge {{
    background: rgba(234, 88, 12, 0.12);
    border: 1px solid rgba(234, 88, 12, 0.3);
    color: #EA580C;
    font-weight: 700;
    font-size: 0.82rem;
    padding: 3px 8px;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}}
.gemini-sparkle {{
    font-size: 1.6rem;
    display: inline-block;
    line-height: 1;
}}
.badge-tag {{
    background: {palette['line']};
    color: {palette['muted']};
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.74rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    margin-top: 6px;
}}
.badge-status-green {{
    background: rgba(16, 185, 129, 0.15);
    color: #10B981;
    border: 1px solid rgba(16, 185, 129, 0.25);
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.76rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}}

/* Contenedores oscuros EXCLUSIVAMENTE para los dos Motores de Procesamiento */
.st-key-motor_n8n_card,
.st-key-motor_python_card,
[class*="st-key-motor_n8n_card"],
[class*="st-key-motor_python_card"] {{
    background-color: #0F172A !important;
    background: #0F172A !important;
    border: 1px solid #1E293B !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
    padding: 1.2rem !important;
    color: #F8FAFC !important;
}}

.st-key-motor_n8n_card p,
.st-key-motor_python_card p,
[class*="st-key-motor_n8n_card"] p,
[class*="st-key-motor_python_card"] p {{
    color: #CBD5E1 !important;
}}

.st-key-motor_n8n_card label,
.st-key-motor_python_card label,
[class*="st-key-motor_n8n_card"] label,
[class*="st-key-motor_python_card"] label,
.st-key-motor_n8n_card [data-testid="stWidgetLabel"] p,
.st-key-motor_python_card [data-testid="stWidgetLabel"] p {{
    color: #F1F5F9 !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
}}

.st-key-motor_n8n_card input,
.st-key-motor_python_card input,
[class*="st-key-motor_n8n_card"] input,
[class*="st-key-motor_python_card"] input,
.st-key-motor_n8n_card [data-baseweb="input"],
.st-key-motor_python_card [data-baseweb="input"],
.st-key-motor_n8n_card [data-baseweb="base-input"],
.st-key-motor_python_card [data-baseweb="base-input"] {{
    background-color: #1E293B !important;
    background: #1E293B !important;
    border: 1px solid #334155 !important;
    color: #F8FAFC !important;
    border-radius: 8px !important;
    font-size: 0.88rem !important;
}}

.st-key-motor_n8n_card input:focus,
.st-key-motor_python_card input:focus,
[class*="st-key-motor_n8n_card"] input:focus,
[class*="st-key-motor_python_card"] input:focus {{
    border-color: #38BDF8 !important;
    box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25) !important;
}}

.st-key-motor_n8n_card input:disabled,
.st-key-motor_python_card input:disabled,
[class*="st-key-motor_n8n_card"] input:disabled,
[class*="st-key-motor_python_card"] input:disabled {{
    background-color: #1E293B !important;
    background: #1E293B !important;
    color: #94A3B8 !important;
    -webkit-text-fill-color: #94A3B8 !important;
    border-color: #334155 !important;
}}

.st-key-motor_n8n_card .badge-tag,
.st-key-motor_python_card .badge-tag,
[class*="st-key-motor_n8n_card"] .badge-tag,
[class*="st-key-motor_python_card"] .badge-tag {{
    background: rgba(30, 41, 59, 0.9) !important;
    color: #94A3B8 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
}}

.engine-features-list {{
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 10px 14px;
    margin: 8px 0 12px 0;
    display: flex;
    flex-direction: column;
    gap: 7px;
}}

.engine-feature-item {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.82rem;
    line-height: 1.35;
}}

.engine-feat-icon {{
    font-size: 0.95rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
}}

.engine-feat-label {{
    font-weight: 700;
    color: #F8FAFC;
}}

.engine-feat-val {{
    color: #CBD5E1;
}}

.engine-port-pill {{
    background: rgba(45, 212, 191, 0.15);
    color: #2DD4BF;
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 0.78rem;
    font-weight: 600;
    border: 1px solid rgba(45, 212, 191, 0.25);
}}

/* Stepper and Metrics Bottom Row (Alturas exactamente idénticas: 90px) */
.stepper-container {{
    background: {palette['bg']};
    border: 1px solid {palette['line']};
    border-radius: 14px;
    padding: 0 1.8rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 90px !important;
    min-height: 90px !important;
    max-height: 90px !important;
    box-sizing: border-box !important;
}}
.step-node {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    position: relative;
    z-index: 2;
}}
.step-circle {{
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.88rem;
    background: {palette['panel']};
    border: 2px solid {palette['line']};
    color: {palette['muted']};
}}
.step-circle.active {{
    background: #6366F1;
    border-color: #6366F1;
    color: #FFFFFF;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}}
.step-label {{
    font-size: 0.75rem;
    font-weight: 600;
    color: {palette['muted']};
    text-align: center;
    line-height: 1.1;
}}
.step-label.active {{
    color: {palette['ink']};
}}
.step-connector {{
    flex: 1;
    height: 3px;
    background: {palette['line']};
    margin: 0 8px 18px 8px;
}}
.step-connector.active {{
    background: #6366F1;
}}
.metric-box-card {{
    background: {palette['bg']};
    border: 1px solid {palette['line']};
    border-radius: 14px;
    padding: 0 1.4rem;
    height: 90px !important;
    min-height: 90px !important;
    max-height: 90px !important;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-sizing: border-box !important;
}}
.metric-box-title {{
    font-size: 0.72rem;
    font-weight: 700;
    color: {palette['muted']};
    text-transform: uppercase;
    letter-spacing: 0.06em;
    line-height: 1;
    margin: 0 0 4px 0;
}}
.metric-box-value {{
    background: {palette['panel']};
    border: 1px solid {palette['line']};
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 1.25rem;
    font-weight: 800;
    color: {palette['ink']};
    display: inline-block;
    width: fit-content;
    line-height: 1.2;
    margin: 0;
}}
.metric-box-desc {{
    font-size: 0.72rem;
    color: {palette['muted']};
    line-height: 1;
    margin: 4px 0 0 0;
}}
</style>
""",
        unsafe_allow_html=True,
    )
