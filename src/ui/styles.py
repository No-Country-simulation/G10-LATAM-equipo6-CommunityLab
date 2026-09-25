"""Sistema de diseño, tokens visuales y estilos CSS premium para CommunityLab.

Inspirado en la plantilla NovaEdu (SaaS de Marketing Educativo):
- Sidebar: Azul noche profundo (#0D1127 / #131938)
- Fondo: Gris perla suave (#F8F9FD)
- Acento / Brand: Púrpura / Índigo (#635BFF / #4F46E5)
- Tarjetas: Blanco puro (#FFFFFF) con bordes suaves (#E2E8F0) y sombras sutiles
- Layout: 3 Columnas (Lista de Posts -> Editor de IA -> Mockup de Red Social)
"""

def get_novaedu_css() -> str:
    """Retorna el bloque CSS inyectable en Streamlit para transformar la interfaz."""
    return """
    <style>
    /* -------------------------------------------------------------------------
       1. VARIABLES Y TIPOGRAFÍA BASE
       ------------------------------------------------------------------------- */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --brand-purple: #635BFF;
        --brand-purple-hover: #4E44E6;
        --brand-purple-light: #EEF0FF;
        --bg-main: #F8F9FD;
        --bg-card: #FFFFFF;
        --border-color: #E6ECF5;
        --text-primary: #1A1F36;
        --text-secondary: #4F566B;
        --text-muted: #8792A2;
        --sidebar-bg: #0D1127;
        --sidebar-hover: #1A203F;
        --badge-green-bg: #E6FBF2;
        --badge-green-text: #059669;
        --badge-amber-bg: #FEF3C7;
        --badge-amber-text: #D97706;
        --badge-blue-bg: #EEF2FF;
        --badge-blue-text: #4F46E5;
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: var(--text-primary);
    }

    /* -------------------------------------------------------------------------
       2. CONTENEDOR PRINCIPAL Y SIDEBAR
       ------------------------------------------------------------------------- */
    /* Fondo general */
    .stApp {
        background-color: var(--bg-main) !important;
    }

    /* Sidebar oscuro estilo NovaEdu */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    [data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
    }

    /* Sidebar logo header */
    .sidebar-brand-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 16px 8px 24px 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 20px;
    }

    .sidebar-brand-icon {
        font-size: 28px;
        background: linear-gradient(135deg, #635BFF 0%, #A29BFE 100%);
        padding: 8px;
        border-radius: 12px;
        color: white !important;
    }

    .sidebar-brand-title {
        font-size: 20px;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #FFFFFF !important;
        margin: 0;
        line-height: 1.2;
    }

    .sidebar-brand-subtitle {
        font-size: 11px;
        color: #94A3B8 !important;
        margin: 0;
    }

    /* Navegación activa en Sidebar */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 8px;
    }

    [data-testid="stSidebar"] .stRadio label {
        padding: 10px 14px !important;
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
        background: transparent !important;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        background: var(--sidebar-hover) !important;
    }

    /* -------------------------------------------------------------------------
       3. TOPBAR HEADER
       ------------------------------------------------------------------------- */
    .topbar-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #FFFFFF;
        padding: 14px 24px;
        border-radius: 16px;
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
        margin-bottom: 24px;
    }

    .topbar-left {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .topbar-badge-oci {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #E6FBF2;
        color: #059669;
        font-size: 12px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        border: 1px solid #A7F3D0;
    }

    .topbar-pulse {
        width: 8px;
        height: 8px;
        background: #10B981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
    }

    /* -------------------------------------------------------------------------
       4. STEPPER SUPERIOR (PROGRESO DEL WORKFLOW)
       ------------------------------------------------------------------------- */
    .stepper-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #FFFFFF;
        padding: 16px 28px;
        border-radius: 14px;
        border: 1px solid var(--border-color);
        margin-bottom: 24px;
        position: relative;
    }

    .stepper-step {
        display: flex;
        align-items: center;
        gap: 10px;
        z-index: 1;
    }

    .step-number {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 13px;
    }

    .step-number.completed {
        background: #10B981;
        color: white;
    }

    .step-number.active {
        background: var(--brand-purple);
        color: white;
        box-shadow: 0 0 0 4px var(--brand-purple-light);
    }

    .step-number.inactive {
        background: #E2E8F0;
        color: #64748B;
    }

    .step-label {
        font-size: 13px;
        font-weight: 600;
        color: var(--text-secondary);
    }

    .step-label.active {
        color: var(--brand-purple);
        font-weight: 700;
    }

    /* -------------------------------------------------------------------------
       5. TARJETAS DE CONTENIDO Y COLUMNAS
       ------------------------------------------------------------------------- */
    .panel-card {
        background: #FFFFFF;
        border-radius: 16px;
        border: 1px solid var(--border-color);
        padding: 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
        height: 100%;
        margin-bottom: 16px;
    }

    .panel-card-title {
        font-size: 15px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* Tarjetas de lista de posts (Columna 1) */
    .post-item-card {
        background: #FFFFFF;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
        cursor: pointer;
    }

    .post-item-card:hover {
        border-color: var(--brand-purple);
        box-shadow: 0 4px 12px rgba(99, 91, 255, 0.08);
        transform: translateY(-1px);
    }

    .post-item-card.selected {
        border-color: var(--brand-purple);
        background: #FAFAFF;
        border-width: 2px;
    }

    .post-item-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }

    .badge-channel {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 6px;
    }

    .badge-channel.linkedin { background: #E8F4F9; color: #0A66C2; }
    .badge-channel.discord { background: #EEF0FD; color: #5865F2; }
    .badge-channel.telegram { background: #E7F5FD; color: #229ED9; }
    .badge-channel.slack { background: #F5EBF7; color: #4A154B; }
    .badge-channel.batch { background: #EDF2F7; color: #4A5568; }

    .badge-status-pill {
        font-size: 10px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 20px;
        text-transform: uppercase;
    }

    .badge-status-pill.aprobado { background: var(--badge-green-bg); color: var(--badge-green-text); }
    .badge-status-pill.pendiente { background: var(--badge-amber-bg); color: var(--badge-amber-text); }
    .badge-status-pill.descartado { background: #FEE2E2; color: #DC2626; }
    .badge-status-pill.leido { background: var(--badge-blue-bg); color: var(--badge-blue-text); }

    .post-item-body {
        font-size: 12px;
        color: var(--text-secondary);
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        line-height: 1.4;
    }

    /* -------------------------------------------------------------------------
       6. MOCKUP PREVIEW REALISTA DE LINKEDIN (COLUMNA 3)
       ------------------------------------------------------------------------- */
    .linkedin-mockup-card {
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    .linkedin-author-box {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
    }

    .linkedin-avatar {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: linear-gradient(135deg, #0A66C2 0%, #004182 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 18px;
    }

    .linkedin-meta h5 {
        margin: 0;
        font-size: 14px;
        font-weight: 600;
        color: rgba(0,0,0,0.9);
        line-height: 1.2;
    }

    .linkedin-meta p {
        margin: 0;
        font-size: 11px;
        color: rgba(0,0,0,0.6);
    }

    .linkedin-content-text {
        font-size: 13px;
        color: rgba(0,0,0,0.9);
        line-height: 1.5;
        white-space: pre-wrap;
        margin-bottom: 12px;
    }

    .linkedin-tags {
        color: #0A66C2;
        font-weight: 600;
        font-size: 12px;
        margin-bottom: 14px;
    }

    .linkedin-reactions-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 10px;
        border-top: 1px solid #EBEBEB;
        font-size: 12px;
        color: rgba(0,0,0,0.6);
    }

    .linkedin-actions-row {
        display: flex;
        justify-content: space-around;
        padding-top: 10px;
        border-top: 1px solid #EBEBEB;
        margin-top: 8px;
    }

    .linkedin-action-btn {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        font-weight: 600;
        color: rgba(0,0,0,0.6);
    }

    /* -------------------------------------------------------------------------
       7. BOTONES PERSONALIZADOS ESTILO NOVAEDU
       ------------------------------------------------------------------------- */
    .stButton button[kind="primary"], .btn-novaedu-primary {
        background: linear-gradient(135deg, var(--brand-purple) 0%, #7C3AED 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 12px rgba(99, 91, 255, 0.25) !important;
        transition: all 0.2s ease !important;
    }

    .stButton button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(99, 91, 255, 0.35) !important;
    }

    .tag-chip-nova {
        display: inline-block;
        background: var(--brand-purple-light);
        color: var(--brand-purple);
        font-size: 11px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    /* -------------------------------------------------------------------------
       8. VISTA ORQUESTADOR DUAL (FASE 3)
       ------------------------------------------------------------------------- */
    .engine-card {
        background: #FFFFFF;
        border-radius: 16px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        padding: 24px;
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }

    .engine-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    }

    .engine-card.n8n {
        border-top: 4px solid #F59E0B;
    }

    .engine-card.python {
        border-top: 4px solid #635BFF;
    }

    .engine-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 14px;
    }

    .engine-title {
        font-size: 18px;
        font-weight: 800;
        color: var(--text-dark);
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .engine-badge {
        font-size: 11px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .engine-badge.n8n {
        background: #FEF3C7;
        color: #B45309;
    }

    .engine-badge.python {
        background: #EEF2FF;
        color: #4F46E5;
    }

    .engine-description {
        font-size: 13px;
        color: var(--text-muted);
        line-height: 1.5;
        margin-bottom: 16px;
    }

    .engine-features-list {
        list-style: none;
        padding: 0;
        margin: 0 0 16px 0;
    }

    .engine-features-list li {
        font-size: 12.5px;
        color: #334155;
        padding: 6px 0;
        border-bottom: 1px dashed #F1F5F9;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .engine-features-list li:last-child {
        border-bottom: none;
    }

    .telemetry-card {
        background: #F8FAFC;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        padding: 16px;
        margin-top: 14px;
        display: flex;
        justify-content: space-around;
        text-align: center;
    }

    .telemetry-item {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .telemetry-label {
        font-size: 11px;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
    }

    .telemetry-value {
        font-size: 16px;
        font-weight: 800;
        color: #0F172A;
    }

    /* -------------------------------------------------------------------------
       9. VISTA HISTÓRICO OCI OBJECT STORAGE (FASE 4)
       ------------------------------------------------------------------------- */
    .storage-stat-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }

    .storage-stat-card {
        background: #FFFFFF;
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
    }

    .storage-stat-title {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        color: var(--text-muted);
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }

    .storage-stat-val {
        font-size: 22px;
        font-weight: 800;
        color: var(--text-dark);
    }

    .storage-asset-card {
        background: #FFFFFF;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02);
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.2s ease;
    }

    .storage-asset-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }

    .storage-asset-info {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .storage-asset-name {
        font-family: monospace;
        font-size: 13.5px;
        font-weight: 700;
        color: #0F172A;
    }

    .storage-asset-meta {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 12px;
        color: #64748B;
    }

    .storage-badge-type {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 6px;
    }

    .storage-badge-type.logros {
        background: #DCFCE7;
        color: #15803D;
    }

    .storage-badge-type.dudas {
        background: #DBEAFE;
        color: #1D4ED8;
    }

    .storage-badge-type.showcase {
        background: #F3E8FF;
        color: #7E22CE;
    }

    .storage-badge-type.feedback {
        background: #FEF3C7;
        color: #B45309;
    }

    .storage-badge-type.general {
        background: #F1F5F9;
        color: #475569;
    }

    .storage-par-box {
        background: #F8FAFC;
        border: 1px dashed #635BFF;
        border-radius: 10px;
        padding: 12px 16px;
        margin-top: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    </style>
    """
