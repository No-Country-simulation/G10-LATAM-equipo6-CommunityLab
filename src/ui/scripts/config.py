"""Tokens de diseño y constantes visuales."""

NAVY = "#141850"
PRIMARY = "#5B4BDB"
PRIMARY_SOFT = "#EEEBFF"
INK = "#1B1D4B"
MUTED = "#6B7090"
BG = "#F4F6FC"
LINE = "#E3E6F2"

# estado -> (fondo, texto)
BADGE = {
    "En edición": ("#E3F6EA", "#1E7B48"),
    "Pendiente de edición": ("#FFF0E0", "#B85C00"),
    "En revisión": ("#FFF0E0", "#B85C00"),
    "Aprobado": ("#E3F6EA", "#1E7B48"),
    "Derivado a FAQ": ("#EAF2FF", "#2E5BBA"),
    "Publicado": ("#EEF0F7", "#6B7090"),
    "Descartado": ("#FEE2E2", "#DC2626"),
    "Leído": ("#E0E7FF", "#4338CA"),
}

CANAL_ICON = {
    "Telegram": "Telegram",
    "Discord": "Discord",
    "Slack": "Slack",
    "LinkedIn": "LinkedIn",
    "X": "X",
    "Dataset Batch": "Lote de Datos",
    "Lotes": "Lotes",
    "Newsletter": "Boletín",
    "WhatsApp": "WhatsApp",
}

CANAL_LUCIDE_NAME = {
    "Telegram": "telegram",
    "Discord": "discord",
    "Slack": "slack",
    "LinkedIn": "linkedin",
    "X": "twitter",
    "Dataset Batch": "package",
    "Lotes": "package",
    "Newsletter": "file-text",
    "WhatsApp": "message-square",
}
TODOS_LOS_CANALES = ["LinkedIn", "X", "Telegram", "Discord", "Slack", "Newsletter"]

BACKEND_FLOW = {
    "N8N": "Automatización visual (Webhook OCI)",
    "Python": "Pipeline programático Gemini 2.5",
}

# Agrupación de estados para los filtros de la lista
GRUPOS_FILTRO = {
    "Pendientes": {"En edición", "Pendiente de edición", "En revisión"},
    "Aprobados": {"Aprobado", "Derivado a FAQ"},
    "Publicados": {"Publicado", "Leído"},
    "Descartados": {"Descartado"},
}
FILTROS = ["Todos", "Pendientes", "Aprobados", "Publicados"]

MAX_CHARS = 3000
