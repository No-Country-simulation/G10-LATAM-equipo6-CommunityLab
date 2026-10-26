#!/usr/bin/env python3
"""
Script para generar el PDF oficial del Guión de Presentación de CommunityLab (YouTube Demo).
Hackathon ONE G10 - Oracle, Alura y No Country (Equipo 6 LATAM).
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(40, 755, "CommunityLab — Guión de Presentación Oficial (Demo Day YouTube)")
            self.drawRightString(572, 755, "Equipo 6 - LATAM | Oracle ONE & No Country")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 748, 572, 748)
            
        # Footer
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(572, 35, page_str)
        self.drawString(40, 35, "Confidencial & Oficial — Hackathon ONE G10 | Proyecto CommunityLab")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 46, 572, 46)
        self.restoreState()


def build_pdf(filename="PM_Files/Guion_Presentacion_CommunityLab_YouTube.pdf"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()

    # Custom Palette
    C_PRIMARY = colors.HexColor("#0F172A")    # Deep Navy
    C_SECONDARY = colors.HexColor("#1E3A8A")  # Royal Blue
    C_ACCENT = colors.HexColor("#2563EB")     # Electric Blue
    C_AMBER = colors.HexColor("#D97706")      # Amber
    C_DARK = colors.HexColor("#1E293B")       # Dark Slate Text
    C_MUTED = colors.HexColor("#475569")      # Muted Slate
    C_BG_CARD = colors.HexColor("#F8FAFC")    # Very light gray
    C_LINE = colors.HexColor("#E2E8F0")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=C_PRIMARY,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=C_MUTED,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=C_SECONDARY,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=C_PRIMARY,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=C_DARK,
        spaceAfter=4
    )

    narration_style = ParagraphStyle(
        'Narration',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#0F172A")
    )

    visual_style = ParagraphStyle(
        'VisualCue',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=C_SECONDARY
    )

    meta_badge_style = ParagraphStyle(
        'Badge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=C_DARK
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=C_PRIMARY
    )

    story = []

    # --- ENCABEZADO PRINCIPAL ---
    story.append(Paragraph("🚀 CommunityLab — Guión Técnico de Presentación (YouTube Demo)", title_style))
    story.append(Paragraph("<b>Hackathon ONE G10</b> | Oracle Next Education & Alura / No Country &bull; <b>Equipo 6 — LATAM</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=C_ACCENT, spaceBefore=0, spaceAfter=8))

    # --- FICHA TÉCNICA DEL VIDEO ---
    ficha_data = [
        [
            Paragraph("<b>⏱️ Duración Máxima:</b> 5:00 min (Objetivo: 4:45 min)", body_style),
            Paragraph("<b>🌐 Demo en Producción:</b> https://hackathon-g10-latam-06.duckdns.org/", body_style),
            Paragraph("<b>🎯 Audiencia:</b> Evaluadores, Mentores & Tech Community", body_style),
        ],
        [
            Paragraph("<b>☁️ Infraestructura:</b> OCI Always Free (Compute + S3)", body_style),
            Paragraph("<b>🧠 Motores IA:</b> Gemini 2.5 Flash / Groq LLMs + FLUX", body_style),
            Paragraph("<b>🧪 Suite QA:</b> 82/82 Tests Automáticos (100% Pasando)", body_style),
        ]
    ]
    t_ficha = Table(ficha_data, colWidths=[175, 185, 172])
    t_ficha.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_BG_CARD),
        ('BOX', (0,0), (-1,-1), 0.5, C_LINE),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_LINE),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_ficha)
    story.append(Spacer(1, 8))

    # --- CRONOGRAMA DE BLOQUES ---
    story.append(Paragraph("📌 1. Estructura General y Distribución de Tiempo", h1_style))
    
    bloques_header = [
        Paragraph("Tiempo", table_header),
        Paragraph("Bloque Temático", table_header),
        Paragraph("Objetivo Clave en el Pitch", table_header),
        Paragraph("Recurso en Pantalla", table_header)
    ]
    bloques_rows = [
        bloques_header,
        [
            Paragraph("<b>0:00 - 0:35</b><br/>(35 seg)", table_cell_bold),
            Paragraph("<b>1. Gancho & El Problema</b>", table_cell),
            Paragraph("Exponer la pérdida del 95% del valor en chats de comunidad y presentar CommunityLab.", table_cell),
            Paragraph("Animación logo, chats caóticos de Discord/TG y vista de la app en producción.", table_cell)
        ],
        [
            Paragraph("<b>0:35 - 1:30</b><br/>(55 seg)", table_cell_bold),
            Paragraph("<b>2. Ingesta Omnicanal & Deduplicación</b>", table_cell),
            Paragraph("Demostrar escucha activa en vivo (Telegram, Discord, Slack) y filtro OCI en tiempo real.", table_cell),
            Paragraph("Pantalla dividida: Bot en TG/Discord + Pestaña Conexiones + Lote en Streamlit.", table_cell)
        ],
        [
            Paragraph("<b>1:30 - 2:40</b><br/>(70 seg)", table_cell_bold),
            Paragraph("<b>3. Motor Dual, Curaduría & Imágenes</b>", table_cell),
            Paragraph("Explicar conmutación Gemini/n8n, 4 formatos temáticos, generador de imágenes y PAR.", table_cell),
            Paragraph("UI NovaEdu Curaduría: Edición de copy, conmutador de motor, generación de imagen y mockup.", table_cell)
        ],
        [
            Paragraph("<b>2:40 - 3:30</b><br/>(50 seg)", table_cell_bold),
            Paragraph("<b>4. Infraestructura OCI, Seguridad & QA</b>", table_cell),
            Paragraph("Mostrar despliegue Always Free, Caddy HTTPS, clave admin y 82 tests pasando.", table_cell),
            Paragraph("Consola OCI (VM + Bucket), Caddyfile, modal Settings con clave admin y terminal pytest.", table_cell)
        ],
        [
            Paragraph("<b>3:30 - 4:25</b><br/>(55 seg)", table_cell_bold),
            Paragraph("<b>5. El Equipo 6 y Aportes Clave</b>", table_cell),
            Paragraph("Presentar a los 7 integrantes con sus roles y contribuciones técnicas destacadas.", table_cell),
            Paragraph("Diapositiva profesional con fotos, nombres, países, roles y logros de cada miembro.", table_cell)
        ],
        [
            Paragraph("<b>4:25 - 4:45</b><br/>(20 seg)", table_cell_bold),
            Paragraph("<b>6. Cierre & Call to Action</b>", table_cell),
            Paragraph("Conclusión de impacto, agradecer a sponsors (Oracle, Alura, No Country) y GitHub.", table_cell),
            Paragraph("Pantalla final: URL oficial, QR a GitHub y logos institucionales de los sponsors.", table_cell)
        ],
    ]
    t_bloques = Table(bloques_rows, colWidths=[65, 115, 182, 170])
    t_bloques.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_SECONDARY),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 0.5, C_LINE),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_LINE),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_bloques)
    story.append(Spacer(1, 10))

    # --- GUIÓN PASO A PASO DETALLADO ---
    story.append(Paragraph("🎬 2. Guión Escena por Escena (Locución & Dirección de Cámara)", h1_style))

    scenes = [
        (
            "ESCENA 1: Gancho, Problema y Propuesta de Valor (0:00 - 0:35)",
            "Visual: Cámara en pantalla dividida o PIP. Inicia con logo animado de CommunityLab, seguido de clips dinámicos de chats repletos de mensajes no leídos en Discord/Telegram. Transición al panel NovaEdu cargando en navegador con HTTPS.",
            "En las comunidades de aprendizaje tecnológico como Discord, Slack o Telegram, todos los días ocurren cosas extraordinarias: estudiantes consiguen su primer empleo, obtienen certificaciones, resuelven errores complejos y construyen proyectos increíbles.\n\nSin embargo, el 95% de ese valor se pierde en el scroll infinito del chat.\n\nPara resolverlo, el Equipo 6 de la Hackathon ONE G10 creó CommunityLab: el motor inteligente cloud-native que transforma la voz orgánica de la comunidad en activos de alto impacto listos para su distribución."
        ),
        (
            "ESCENA 2: Escucha Omnicanal en Vivo & Deduplicación OCI (0:35 - 1:30)",
            "Visual: Grabación en vivo de un mensaje de prueba enviado en Telegram (@G10_Latam_06_bot) o Discord. Cambio inmediato al panel de Streamlit en la vista '📡 Conexiones & Bots' mostrando el bot respondiendo en verde, y la vista '📥 Procesamiento e Ingesta' procesando un lote con el deduplicador OCI activado.",
            "CommunityLab opera mediante una arquitectura de escucha activa omnicanal. Cuenta con bots conectados en tiempo real a Telegram, Discord y Slack Socket Mode, además de un módulo de ingesta por lotes en JSON y CSV.\n\nToda interacción pasa por un riguroso validador tipado en Pydantic V2 y un Deduplicador inteligente que consulta directamente Oracle Cloud Infrastructure (OCI) Object Storage, garantizando que ninguna publicación se procese dos veces y manteniendo la arquitectura 100% Stateless."
        ),
        (
            "ESCENA 3: Orquestación Dual, Curaduría NovaEdu & Generador de Imágenes (1:30 - 2:40)",
            "Visual: Vista '📝 Curaduría Tri-Panel'. Seleccionar un post pendiente de contratación. Mostrar conmutador de motor (Gemini vs n8n). Editar copy. Clic en 'Generar Imagen con IA' mostrando el prompt generado y la imagen apareciendo al instante en el mockup interactivo de LinkedIn/X.",
            "El corazón del sistema es su Orquestación Dual Homologada: podemos procesar contenido tanto con Google Gemini 2.5 en Python puro a ultra-alta velocidad, como a través de flujos visuales en n8n.\n\nLa IA analiza el sentimiento y clasifica automáticamente en 4 paquetes temáticos: logros para LinkedIn, FAQs técnicas, showcase de proyectos y métricas de salud comunitaria.\n\nEn nuestro Panel de Curaduría NovaEdu, el Community Manager puede revisar, pulir el copy y activar nuestro Generador de Imágenes Dual-Engine con Groq y FLUX. Además, gracias a los tokens PAR (Pre-Authenticated Requests) de OCI, las imágenes alojadas en buckets privados se visualizan de forma instantánea y segura."
        ),
        (
            "ESCENA 4: Infraestructura OCI Always Free, Seguridad Administrativa & QA (2:40 - 3:30)",
            "Visual: Vista rápida de la consola OCI (VM Compute 147.15.9.116 y Bucket S3). Pestaña '⚙️ Settings' mostrando el diálogo protegido por SETTINGS_ADMIN_KEY. Transición a terminal ejecutando 'pytest tests/ -v' con 82 pruebas pasando en verde.",
            "Toda la solución fue construida sobre el ecosistema Always Free de Oracle Cloud Infrastructure. La aplicación y el orquestador n8n corren en una máquina virtual Compute en Linux, protegida con proxy inverso Caddy, certificados automáticos SSL y dominio público bajo DuckDNS.\n\nEn el apartado de seguridad, el panel de configuración está blindado contra fugas de secretos mediante una Clave de Verificación Administrativa.\n\nY gracias a un desarrollo ágil y acelerado, ganamos una semana de ventaja previa a este Demo Day para realizar hardening, alcanzando 82 pruebas automatizadas unitarias e integrales con 100% de éxito."
        ),
        (
            "ESCENA 5: Presentación del Equipo 6 y Aportes Destacados (3:30 - 4:25)",
            "Visual: Diapositiva corporativa 'Equipo 6 - LATAM' con fotos de perfil, banderas, roles e iconos de especialidad. La cámara hace paneo suave mientras el locutor menciona los aportes clave.",
            "Detrás de CommunityLab hay un equipo multidisciplinario de 7 profesionales conectados desde toda Latinoamérica:\n\n• César Cely (Colombia) - Project Manager & Cloud Architect: Liderazgo, arquitectura OCI, gestión de buckets y proxy SSL Caddy.\n• Max Ferrer (Perú) - Backend & Pipeline Developer: Pipeline E2E en Python, adaptación frontend modular y conector LinkedIn.\n• José Medina (Paraguay) - Especialista n8n & LLMs: Admin de la VM OCI, microservicio de imágenes y flujos S3.\n• Edwin Enriquez (Bolivia) - QA Lead & Backend: Estrategia de testing y suite automatizada de 82 pruebas continuas.\n• Carol Arancay (Perú) - Frontend & UX: Diseño del sistema visual NovaEdu y curaduría del dataset oficial.\n• Raúl Gallardo (Argentina) - QA & Cloud Support: Pruebas de persistencia y soporte de nube OCI.\n• Luygy Ruben Vivas Moreno (Colombia) - QA & Pruebas Funcionales: Incorporado en las 2 últimas semanas, liderando pruebas funcionales de extremo a extremo, control de calidad y validación de la experiencia de usuario."
        ),
        (
            "ESCENA 6: Cierre, Agradecimientos & Llamado a la Acción (4:25 - 4:45)",
            "Visual: Mockup en laptop y smartphone con la URL pública activa (https://hackathon-g10-latam-06.duckdns.org/), código QR al repositorio de GitHub y logos de Oracle ONE, Alura Latam y No Country.",
            "CommunityLab demuestra cómo la inteligencia artificial generativa y la nube de Oracle pueden potenciar a las comunidades digitales, convirtiendo cada mensaje en una historia de éxito visible.\n\nLes invitamos a probar la demo en vivo y explorar nuestro código en GitHub. ¡Muchas gracias a Oracle, Alura y No Country por este emocionante reto! Somos el Equipo 6."
        )
    ]

    for title, visual, narration in scenes:
        box_data = [
            [Paragraph(f"<b>{title}</b>", h2_style)],
            [Paragraph(f"<b>🎥 Indicación Visual:</b> {visual}", visual_style)],
            [Paragraph(f"<b>🎙️ Locución (Voz en Off):</b><br/>{narration.replace(chr(10), '<br/>')}", narration_style)]
        ]
        t_scene = Table(box_data, colWidths=[532])
        t_scene.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), C_BG_CARD),
            ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#EFF6FF")),
            ('BACKGROUND', (0,2), (-1,2), colors.white),
            ('BOX', (0,0), (-1,-1), 0.5, C_LINE),
            ('LINEBELOW', (0,0), (-1,0), 0.5, C_LINE),
            ('LINEBELOW', (0,1), (-1,1), 0.5, C_LINE),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_scene)
        story.append(Spacer(1, 6))

    # --- TABLA DE INTEGRANTES Y APORTES ---
    story.append(PageBreak())
    story.append(Paragraph("👥 3. Miembros del Equipo 6 y Aportes al Proyecto", h1_style))
    story.append(Paragraph("Cuadro consolidado de integrantes, roles de liderazgo y contribuciones técnicas implementadas:", body_style))
    story.append(Spacer(1, 4))

    team_header = [
        Paragraph("Integrante", table_header),
        Paragraph("País", table_header),
        Paragraph("Rol Principal", table_header),
        Paragraph("Aporte Técnico Específico al Proyecto", table_header)
    ]
    team_data = [
        team_header,
        [
            Paragraph("<b>César Augusto Cely Pulido</b>", table_cell_bold),
            Paragraph("🇨🇴 Colombia", table_cell),
            Paragraph("<b>Project Manager & Cloud Architect</b>", table_cell),
            Paragraph("Liderazgo del equipo, arquitectura de nube en Oracle Cloud (OCI Always Free), administración de Object Storage y políticas S3, configuración de dominio DuckDNS, certificados SSL y proxy inverso Caddy, y orquestación integral del roadmap.", table_cell)
        ],
        [
            Paragraph("<b>Max Ferrer Cabanillas Salas</b>", table_cell_bold),
            Paragraph("🇵🇪 Perú", table_cell),
            Paragraph("<b>Backend & Pipeline Developer</b>", table_cell),
            Paragraph("Desarrollo del pipeline E2E en Python (`pipeline.py`), ingesta y deduplicación con OCI, modularización y adaptación del frontend NovaEdu en 7 vistas Streamlit, e investigación/validación del conector de publicación en LinkedIn.", table_cell)
        ],
        [
            Paragraph("<b>José Medina</b>", table_cell_bold),
            Paragraph("🇵🇾 Paraguay", table_cell),
            Paragraph("<b>Oracle Ecosystem & n8n / LLMs</b>", table_cell),
            Paragraph("Administración de la máquina virtual Ubuntu en OCI Compute (`147.15.9.116`), diseño y versionado de flujos n8n, implementación del microservicio de generación de imágenes (`POST /webhook/generar-imagen-post2`) con Groq y nodos S3.", table_cell)
        ],
        [
            Paragraph("<b>Edwin Gustavo Enriquez Arias</b>", table_cell_bold),
            Paragraph("🇧🇴 Bolivia", table_cell),
            Paragraph("<b>QA Lead & Testing Automation</b>", table_cell),
            Paragraph("Definición de la estrategia de calidad del proyecto, desarrollo y mantenimiento de la suite automatizada de 82 pruebas con Pytest (100% aprobadas), validación de esquemas Pydantic V2 y blindaje de resiliencia en pipelines.", table_cell)
        ],
        [
            Paragraph("<b>Carol Yesenia Arancay Osorio</b>", table_cell_bold),
            Paragraph("🇵🇪 Perú", table_cell),
            Paragraph("<b>Frontend / UX & Data</b>", table_cell),
            Paragraph("Conceptualización y diseño visual del sistema NovaEdu en Streamlit, propuesta de paleta corporativa y componentes UI, y enriquecimiento y validación del dataset oficial de interacciones de prueba (`data/interacciones_ejemplo.json`).", table_cell)
        ],
        [
            Paragraph("<b>Raúl Gallardo</b>", table_cell_bold),
            Paragraph("🇦🇷 Argentina", table_cell),
            Paragraph("<b>QA & Cloud Support</b>", table_cell),
            Paragraph("Pruebas de estrés y conectividad contra OCI Object Storage, validación de integridad en paquetes de distribución generados y control de respuestas de la IA.", table_cell)
        ],
        [
            Paragraph("<b>Luygy Ruben Vivas Moreno</b>", table_cell_bold),
            Paragraph("🇨🇴 Colombia", table_cell),
            Paragraph("<b>QA & Pruebas Funcionales</b>", table_cell),
            Paragraph("Integrado en las últimas 2 semanas del proyecto, aportando activamente con pruebas funcionales de extremo a extremo, validación exhaustiva de la experiencia de usuario (UX) en la UI y control de calidad sobre la generación de contenidos y bots omnicanal.", table_cell)
        ],
    ]
    t_team = Table(team_data, colWidths=[110, 60, 110, 252])
    t_team.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 0.5, C_LINE),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_LINE),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_team)
    story.append(Spacer(1, 10))

    # --- CHECKLIST Y RECOMENDACIONES DE GRABACIÓN ---
    story.append(Paragraph("🛠️ 4. Checklist & Consejos Técnicos de Grabación para YouTube", h1_style))
    
    tips = [
        "<b>1. Resolución & Formato:</b> Grabar a 1080p (1920x1080) a 60 fps en formato MP4 / MKV con OBS Studio o similar.",
        "<b>2. Entorno Visual Limpio:</b> Ocultar la barra de marcadores del navegador (F11 o Ctrl+Shift+B), cerrar pestañas innecesarias y usar el tema oscuro predeterminado de NovaEdu para resaltar los acentos azul eléctrico.",
        "<b>3. Puntero & Clics:</b> Configurar cursor con halo amarillo o efecto de clic suave para que los evaluadores sigan fácilmente la navegación en el panel de curaduría y el mockup interactivo.",
        "<b>4. Audio Profesional:</b> Grabar con micrófono condensador o auricular con cancelación de ruido. Aplicar filtro compresor y ecualización básica para mantener un volumen homogéneo entre -6dB y -3dB.",
        "<b>5. Ritmo de Locución:</b> Mantener una cadencia de aproximadamente 140 a 150 palabras por minuto. El guión tiene exactamente ~710 palabras de locución, lo que cronometra ~4 minutos con 40 segundos, garantizando cumplir holgadamente la regla de 'menos de 5 minutos'.",
        "<b>6. Miniatura (Thumbnail):</b> Diseñar miniatura atractiva con fondo azul oscuro, el logo de CommunityLab, captura del panel Streamlit y título de alto contraste: 'CommunityLab: El Motor de IA para Comunidades (Demo Oficial ONE G10)'."
    ]

    for tip in tips:
        story.append(Paragraph(f"&bull; {tip}", body_style))

    # Construir documento
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generado exitosamente en: {filename}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "PM_Files/Guion_Presentacion_CommunityLab_YouTube.pdf"
    build_pdf(out)
