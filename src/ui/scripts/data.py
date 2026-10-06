"""Datos iniciales y de respaldo alineados con el MVP de CommunityLab."""

COPY_DEFAULT = (
    "De la comunidad al mercado ✨\n\n"
    "Hoy celebramos a Mariana Souza, quien pasó de la práctica con IA y OCI a una primera oportunidad como desarrolladora junior. "
    "Sus proyectos reales, el apoyo de la comunidad y la disciplina del aprendizaje hicieron la diferencia.\n\n"
    "Historias como esta muestran el valor de construir en comunidad.\n\n"
    "#CommunityLab #IA #OCI #TalentosTech #OracleONE"
)

POSTS = [
    dict(
        id="post_001",
        title="Estudiante logra empleo junior en IA",
        canal="LinkedIn",
        canal_ingesta="Telegram",
        sentimiento="positivo",
        motor="Python",
        tipo="logro_contratacion",
        fecha="Hoy",
        estado="En revisión",
        hace="Hace 10 min",
        banner="De la comunidad al mercado",
        sub="Caso de éxito con proyectos reales, OCI y aprendizaje colectivo.",
        emoji="🚀",
        copy=COPY_DEFAULT,
    ),
    dict(
        id="post_002",
        title="FAQ sobre nodos condicionales en LangGraph",
        canal="Discord",
        canal_ingesta="Discord",
        sentimiento="neutro",
        motor="Python",
        tipo="duda_tecnica",
        fecha="Ayer",
        estado="Pendiente de edición",
        hace="Hace 2 h",
        banner="Tip rápido: LangGraph",
        sub="Pregunta recurrente detectada en el canal de soporte técnico.",
        emoji="🧠",
        copy="Tip rápido: cómo estructurar nodos condicionales en LangGraph 🚀\n\nCuando la respuesta del LLM requiere reintento, conviene separar la lógica de routing y mantener un punto único de decisión.\n\n#CommunityLab #LangGraph #IA #Python",
    ),
    dict(
        id="post_003",
        title="Highlight semanal de comunidad",
        canal="Newsletter",
        canal_ingesta="Lotes",
        sentimiento="positivo",
        motor="N8N",
        tipo="showcase",
        fecha="Esta semana",
        estado="Aprobado",
        hace="Hace 5 h",
        banner="Community Highlights",
        sub="Resumen semanal con historias, logros y aprendizajes clave.",
        emoji="📬",
        copy="Community Highlights ✨\n\nEsta semana celebramos los avances de nuestros miembros, los proyectos que cerraron su ciclo y las dudas técnicas que se volvieron ejemplos útiles para todo el grupo.\n\n#CommunityLab #Newsletter #Growth",
    ),
    dict(
        id="post_004",
        title="Duda recurrente sobre OCI Object Storage",
        canal="Slack",
        canal_ingesta="Slack",
        sentimiento="negativo",
        motor="N8N",
        tipo="feedback_general",
        fecha="Ayer",
        estado="Derivado a FAQ",
        hace="Hace 1 día",
        banner="FAQ técnica: OCI",
        sub="Pregunta frecuente en canales de soporte y mentoría.",
        emoji="☁️",
        copy="FAQ técnica: cómo organizar buckets en OCI ☁️\n\nPara proyectos pequeños, conviene separar por entorno y tipo de activo para mantener trazabilidad y control de acceso.\n\n#OCI #CommunityLab #Cloud",
    ),
]

BY_ID = {p["id"]: p for p in POSTS}
