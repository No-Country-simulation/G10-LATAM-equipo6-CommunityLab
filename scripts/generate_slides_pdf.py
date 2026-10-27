#!/usr/bin/env python3
"""
Script para generar el PDF oficial de la Presentación Ejecutiva de CommunityLab (4 Slides).
Formato apaisado (Landscape), diseño corporate moderno y preparado para presentación o proyección.
Hackathon ONE G10 - Oracle, Alura y No Country (Equipo 6 LATAM).
"""

import os
import sys
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas

# Paleta Corporativa NovaEdu & Oracle Cloud
NAVY = colors.HexColor("#0F172A")
NAVY_LIGHT = colors.HexColor("#1E293B")
SLATE_BORDER = colors.HexColor("#CBD5E1")
SLATE_BG = colors.HexColor("#F8FAFC")
ORACLE_RED = colors.HexColor("#C74634")
AMBER = colors.HexColor("#D97706")
AMBER_BG = colors.HexColor("#FEF3C7")
INDIGO = colors.HexColor("#4F46E5")
INDIGO_BG = colors.HexColor("#EEF2FF")
EMERALD = colors.HexColor("#059669")
EMERALD_BG = colors.HexColor("#ECFDF5")
ROSE = colors.HexColor("#DC2626")
ROSE_BG = colors.HexColor("#FEF2F2")
TEXT_DARK = colors.HexColor("#1E293B")
TEXT_MUTED = colors.HexColor("#64748B")
WHITE = colors.HexColor("#FFFFFF")


class SlideCanvas(canvas.Canvas):
    """Canvas con encabezado y pie de página para diapositivas apaisadas."""
    def __init__(self, *args, **kwargs):
        super(SlideCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_slide_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_slide_decorations(self, total_slides):
        self.saveState()
        w, h = landscape(letter)  # 792 x 612 pt
        
        # Barra superior decorativa
        self.setFillColor(INDIGO)
        self.rect(0, h - 8, w, 8, fill=True, stroke=False)
        self.setFillColor(ORACLE_RED)
        self.rect(0, h - 8, 120, 8, fill=True, stroke=False)

        # Header texto sutil
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(TEXT_MUTED)
        self.drawString(36, h - 24, "COMMUNITYLAB · HACKATHON ORACLE ONE G10")
        self.drawRightString(w - 36, h - 24, "EQUIPO 6 — LATAM")
        
        self.setStrokeColor(SLATE_BORDER)
        self.setLineWidth(0.5)
        self.line(36, h - 28, w - 36, h - 28)

        # Footer
        self.line(36, 32, w - 36, 32)
        self.setFont("Helvetica", 8)
        self.setFillColor(TEXT_MUTED)
        self.drawString(36, 20, "Confidencial & Oficial · Oracle Next Education, Alura & No Country")
        slide_str = f"Slide {self._pageNumber} de {total_slides}"
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(INDIGO)
        self.drawRightString(w - 36, 20, slide_str)
        self.restoreState()


def create_slide_deck(filename="PM_Files/Presentacion_CommunityLab_4_Slides.pdf"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    w, h = landscape(letter)
    
    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=40,
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos tipográficos
    title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=NAVY,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        'SlideSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=TEXT_MUTED,
        spaceAfter=12,
    )
    card_title = ParagraphStyle(
        'CardTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=NAVY,
        spaceAfter=6,
    )
    card_body = ParagraphStyle(
        'CardBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=TEXT_DARK,
    )
    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=TEXT_DARK,
        leftIndent=10,
        firstLineIndent=-10,
        spaceAfter=3,
    )
    badge_style = ParagraphStyle(
        'BadgeText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=WHITE,
        alignment=1,
    )
    notes_style = ParagraphStyle(
        'SpeakerNotes',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10,
        textColor=TEXT_MUTED,
    )

    story = []

    # =========================================================================
    # SLIDE 1: PORTADA, PROBLEMA & VISIÓN DE PRODUCTO
    # =========================================================================
    story.append(Paragraph("1. CommunityLab: Transformación y Curaduría de Comunidades", title_style))
    story.append(Paragraph("Hackathon ONE G10 — Oracle Next Education, Alura & No Country | Equipo 6 LATAM", subtitle_style))
    
    # 2 Columnas: Problema vs Solución
    col1_content = [
        Paragraph("<font color='#DC2626'><b>[PROBLEMA]</b></font> <b>Sobrecarga en Comunidades Masivas</b>", card_title),
        Spacer(1, 4),
        Paragraph("• <b>Sobrecarga y Dispersión:</b> Miles de mensajes diarios en Discord, Telegram y Slack sin categorización ni auditoría.", bullet_style),
        Paragraph("• <b>90% del Valor se Pierde:</b> Dudas técnicas resueltas, certificaciones obtenidas y logros de contratación quedan sepultados en el chat.", bullet_style),
        Paragraph("• <b>Cuello de Botella Manual:</b> Los Community Managers tardan horas redactando posts y FAQs de forma artesanal e insostenible.", bullet_style),
        Spacer(1, 8),
        Paragraph("<b>Impacto Negativo:</b> Pérdida de visibilidad del impacto educativo y desaprovechamiento de casos de éxito.", card_body),
    ]
    
    col2_content = [
        Paragraph("<font color='#059669'><b>[SOLUCIÓN]</b></font> <b>Plataforma Integral CommunityLab</b>", card_title),
        Spacer(1, 4),
        Paragraph("• <b>Escucha Activa Omnicanal:</b> Bots en tiempo real (Telegram, Discord, Slack) y procesamiento masivo de lotes.", bullet_style),
        Paragraph("• <b>Enriquecimiento Multimodal con IA:</b> Extracción de copys para LinkedIn/X, generación de FAQs técnicas e imágenes FLUX.", bullet_style),
        Paragraph("• <b>Control Humano en 1 Clic:</b> Tri-Panel de curaduría con aprobación y persistencia formal en OCI.", bullet_style),
        Spacer(1, 8),
        Paragraph("<b>Propuesta de Valor:</b> De horas de trabajo manual a distribución en segundos, a <b>Costo $0</b> en OCI Always Free.", card_body),
    ]
    
    t1 = Table(
        [[col1_content, col2_content]],
        colWidths=[355, 355],
    )
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), ROSE_BG),
        ('BACKGROUND', (1, 0), (1, 0), EMERALD_BG),
        ('BOX', (0, 0), (0, 0), 1, colors.HexColor("#FCA5A5")),
        ('BOX', (1, 0), (1, 0), 1, colors.HexColor("#86EFAC")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(t1)
    story.append(Spacer(1, 10))
    
    # Banner inferior métricas de impacto proyectado
    kpi_banner = [
        [
            Paragraph("<b>4 Canales Integrados</b><br/><font color='#64748B' size='7'>Telegram, Discord, Slack, Lotes</font>", card_title),
            Paragraph("<b>Dual-Engine IA</b><br/><font color='#64748B' size='7'>Gemini 2.5 Flash + Groq Llama 3</font>", card_title),
            Paragraph("<b>Costo de Infraestructura</b><br/><font color='#059669' size='8'><b>$0.00 (OCI Always Free)</b></font>", card_title),
            Paragraph("<b>Aprobación Eficiente</b><br/><font color='#4F46E5' size='8'><b>Tri-Panel en 1 Clic</b></font>", card_title),
        ]
    ]
    t_kpi = Table(kpi_banner, colWidths=[177, 177, 178, 178])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SLATE_BG),
        ('BOX', (0, 0), (-1, -1), 1, SLATE_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_kpi)
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>[NOTAS DEL PRESENTADOR - 1:15 min]:</b> <i>Enfatizar la sobrecarga de mensajes que viven los coordinadores de ONE y Alura. Presentar a CommunityLab como el puente inteligente que convierte conversaciones desordenadas en vitrinas oficiales de empleo y conocimiento con costo cero de infraestructura.</i>", notes_style))

    story.append(PageBreak())

    # =========================================================================
    # SLIDE 2: ARQUITECTURA TÉCNICA & ECOSISTEMA ORACLE CLOUD
    # =========================================================================
    story.append(Paragraph("2. Arquitectura Cloud-Native & Orquestación Dual Homologada", title_style))
    story.append(Paragraph("Infraestructura Empresarial y Resiliente en Oracle Cloud Infrastructure (Always Free)", subtitle_style))
    
    # 3 Cajas Técnicas: Ingesta -> Dual Engine -> Persistencia OCI
    box_ingesta = [
        Paragraph("<b>1. Ingesta Omnicanal</b>", card_title),
        Paragraph("• <b>Telegram:</b> @G10_Latam_06_bot (Long Polling + Webhook).", bullet_style),
        Paragraph("• <b>Discord:</b> WebSocket Gateway asincrono en canal de dudas.", bullet_style),
        Paragraph("• <b>Slack:</b> Socket Mode bidireccional seguro sin abrir puertos.", bullet_style),
        Paragraph("• <b>Lotes Masivos:</b> Ingesta batch JSON/CSV con deduplicador OCI.", bullet_style),
    ]
    
    box_engine = [
        Paragraph("<b>2. Dual-Engine Orquestado</b>", card_title),
        Paragraph("• <b>Motor Python Nativo:</b> Inferencia directa con Gemini 2.5 Flash + Pydantic v2 (~2 a 4s por lote).", bullet_style),
        Paragraph("• <b>Orquestador n8n:</b> Workflows visuales en Docker + Groq LLM + Nodos S3.", bullet_style),
        Paragraph("• <b>4 Archivos Tematicos:</b> Logros, Showcase, FAQs tecnicas y Feedback.", bullet_style),
    ]
    
    box_oci = [
        Paragraph("<b>3. Nube OCI & Seguridad</b>", card_title),
        Paragraph("• <b>OCI Compute VM:</b> Instancia Ubuntu con Caddy Reverse Proxy y SSL Let's Encrypt.", bullet_style),
        Paragraph("• <b>OCI Object Storage:</b> Persistencia cronologica (activos/YYYY-MM-DD/*.json).", bullet_style),
        Paragraph("• <b>Tokens PAR:</b> Acceso privado temporal para visualizacion segura de imagenes.", bullet_style),
        Paragraph("• <b>Dominio Oficial:</b> hackathon-g10-latam-06.duckdns.org", bullet_style),
    ]
    
    t_arch = Table([[box_ingesta, box_engine, box_oci]], colWidths=[232, 246, 232])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#F1F5F9")),
        ('BACKGROUND', (1, 0), (1, 0), INDIGO_BG),
        ('BACKGROUND', (2, 0), (2, 0), colors.HexColor("#FFF7ED")),
        ('BOX', (0, 0), (0, 0), 1, SLATE_BORDER),
        ('BOX', (1, 0), (1, 0), 1, colors.HexColor("#A5B4FC")),
        ('BOX', (2, 0), (2, 0), 1, colors.HexColor("#FDBA74")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 10))

    # Diagrama de flujo textual de datos en 1 columna limpia
    flow_content = [
        [Paragraph("<b>Flujo Homologado de Datos E2E:</b>", card_title)],
        [Paragraph("Mensaje de Comunidad (Telegram / Discord / Slack) &rarr; Despachador Omnicanal &rarr; Conmutador Dual (Python Gemini / n8n Groq) &rarr; Validacion Estricta Pydantic v2 &rarr; OCI Object Storage &rarr; Panel Curaduria NovaEdu (Tokens PAR) &rarr; Publicacion Oficial.", card_body)]
    ]
    t_flow = Table(flow_content, colWidths=[710])
    t_flow.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SLATE_BG),
        ('BOX', (0, 0), (-1, -1), 1, SLATE_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(t_flow)
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>[NOTAS DEL PRESENTADOR - 1:15 min]:</b> <i>Explicar el concepto Dual-Engine: la versatilidad de alternar entre codigo Python de alta velocidad y workflows visuales de n8n sin tocar la persistencia en OCI. Destacar la utilizacion de tokens PAR para no comprometer la seguridad de los buckets.</i>", notes_style))

    story.append(PageBreak())

    # =========================================================================
    # SLIDE 3: FUNCIONALIDADES & CURADURÍA HUMANA TRI-PANEL
    # =========================================================================
    story.append(Paragraph("3. Demostracion Funcional: Curaduria Tri-Panel e IA Generativa", title_style))
    story.append(Paragraph("Experiencia de Usuario NovaEdu: Accesibilidad, Decision en 1 Clic y Control Humano", subtitle_style))
    
    col_p1 = [
        Paragraph("<b>[1] Panel Izquierdo: Lista & Filtros</b>", card_title),
        Paragraph("• <b>Pastillas Segmentadas:</b> Filtro rapido por Todos, Pendientes, Aprobados y Publicados.", bullet_style),
        Paragraph("• <b>Filtros Combinados:</b> Sentimiento LLM, motor y canal.", bullet_style),
        Paragraph("• <b>Selector OCI Inteligente:</b> Descubrimiento dinamico de archivos del dia (activos/YYYY-MM-DD/*.json).", bullet_style),
        Paragraph("• <b>Estado Activo:</b> Indicador visual nitido [EDITANDO] Editando activo (Activo).", bullet_style),
    ]
    
    col_p2 = [
        Paragraph("<b>[2] Panel Central: Editor & IA</b>", card_title),
        Paragraph("• <b>Editor Multicanal:</b> Redaccion guiada con limite de caracteres para LinkedIn y X.", bullet_style),
        Paragraph("• <b>Generador de Imagenes Dual:</b> Inferencia visual con Gemini 2.5 o FLUX Pollinations en n8n.", bullet_style),
        Paragraph("• <b>Botonera Semantica Dinamica:</b>", bullet_style),
        Paragraph("  - [APROBAR] Aprobado (Activo) - Verde Esmeralda", bullet_style),
        Paragraph("  - [DESCARTAR] Descartado (Activo) - Rojo Carmesin", bullet_style),
        Paragraph("  - [LEIDO] Leido (Activo) - Indigo Profundo", bullet_style),
    ]
    
    col_p3 = [
        Paragraph("<b>[3] Panel Derecho: Mockup & Feed</b>", card_title),
        Paragraph("• <b>Mockup de Redes Sociales:</b> Vista fidedigna previa para LinkedIn, X, Discord y Slack.", bullet_style),
        Paragraph("• <b>Renderizado Seguro PAR:</b> Carga de imagenes sin exponer URLs publicas de OCI.", bullet_style),
        Paragraph("• <b>Simulador de Dispositivo:</b> Alternancia instantanea entre Desktop y Mobile.", bullet_style),
        Paragraph("• <b>Persistencia en 1 Clic:</b> Guardado directo en curaduria_aprobados.json.", bullet_style),
    ]
    
    t_tri = Table([[col_p1, col_p2, col_p3]], colWidths=[232, 246, 232])
    t_tri.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), SLATE_BG),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#FAF5FF")),
        ('BACKGROUND', (2, 0), (2, 0), SLATE_BG),
        ('BOX', (0, 0), (0, 0), 1, SLATE_BORDER),
        ('BOX', (1, 0), (1, 0), 1, colors.HexColor("#D8B4FE")),
        ('BOX', (2, 0), (2, 0), 1, SLATE_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_tri)
    story.append(Spacer(1, 10))

    # Barra de otras vistas de la app en 1 columna limpia
    vistas_content = [
        [Paragraph("<b>Suite de 7 Vistas Operativas Integradas en Streamlit:</b>", card_title)],
        [Paragraph("<b>1. Dashboard de Comunidad:</b> Metricas y graficos LLM &nbsp;|&nbsp; <b>2. Curaduria Tri-Panel:</b> Aprobacion en 1 clic &nbsp;|&nbsp; <b>3. Ingesta &amp; Lotes:</b> Ingesta batch y deduplicacion &nbsp;|&nbsp; <b>4. Almacenamiento OCI:</b> Explorador de buckets y PAR &nbsp;|&nbsp; <b>5. Conexiones &amp; Bots:</b> Control en vivo &nbsp;|&nbsp; <b>6. Settings &amp; Clave Admin:</b> Blindaje con SETTINGS_ADMIN_KEY &nbsp;|&nbsp; <b>7. Observabilidad:</b> Auditoria y logs rotativos.", card_body)]
    ]
    t_vistas = Table(vistas_content, colWidths=[710])
    t_vistas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), INDIGO_BG),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#C7D2FE")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(t_vistas)
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>[NOTAS DEL PRESENTADOR - 1:30 min]:</b> <i>Demostrar visualmente como el Tri-Panel permite al Community Manager validar la respuesta tecnica o el post de empleo en 1 solo clic. Resaltar la ergonomia de los nuevos botones de alto contraste y la fidelidad del mockup de redes sociales.</i>", notes_style))

    story.append(PageBreak())

    # =========================================================================
    # SLIDE 4: EQUIPO MULTIDISCIPLINARIO, RIGOR QA & IMPACTO
    # =========================================================================
    story.append(Paragraph("4. Equipo Multidisciplinario, Rigor QA & Resultados", title_style))
    story.append(Paragraph("Compromiso Agil, 82 Tests Automatizados y Despliegue en Produccion", subtitle_style))
    
    # Tabla de Integrantes (7 miembros)
    team_data = [
        [
            Paragraph("<b>Integrante</b>", card_title),
            Paragraph("<b>Ubicacion</b>", card_title),
            Paragraph("<b>Rol & Responsabilidad Principal</b>", card_title),
        ],
        [
            Paragraph("<b>Cesar Augusto Cely Pulido</b>", card_body),
            Paragraph("Bogota, Colombia", card_body),
            Paragraph("<b>Project Manager & Cloud Architect:</b> Liderazgo agil, arquitectura OCI y diseno integral del sistema.", card_body),
        ],
        [
            Paragraph("<b>Max Ferrer Cabanillas Salas</b>", card_body),
            Paragraph("Lima, Peru", card_body),
            Paragraph("<b>Backend & Pipeline Developer:</b> Pipeline E2E, conector omnicanal y research de APIs LinkedIn/X.", card_body),
        ],
        [
            Paragraph("<b>Jose Medina</b>", card_body),
            Paragraph("Paraguay", card_body),
            Paragraph("<b>Oracle Ecosystem & N8N Specialist:</b> Microservicio de generacion de imagenes FLUX y flujos n8n.", card_body),
        ],
        [
            Paragraph("<b>Edwin Gustavo Enriquez Arias</b>", card_body),
            Paragraph("La Paz, Bolivia", card_body),
            Paragraph("<b>QA Lead & Testing Automation:</b> Suite automatizada de pruebas, casos limite y robustez backend.", card_body),
        ],
        [
            Paragraph("<b>Carol Yesenia Arancay Osorio</b>", card_body),
            Paragraph("Lima, Peru", card_body),
            Paragraph("<b>Frontend / UX & Data:</b> Diseno modular NovaEdu en Streamlit, metricas de comunidad y diseno visual.", card_body),
        ],
        [
            Paragraph("<b>Raul Gallardo</b>", card_body),
            Paragraph("Buenos Aires, Argentina", card_body),
            Paragraph("<b>QA & Cloud Support:</b> Validacion de infraestructura OCI, soporte de despliegue y pruebas de carga.", card_body),
        ],
        [
            Paragraph("<b>Luygy Ruben Vivas Moreno</b>", card_body),
            Paragraph("Colombia", card_body),
            Paragraph("<b>QA & Pruebas Funcionales:</b> Aseguramiento de calidad funcional en bots y verificacion de experiencia de usuario.", card_body),
        ],
    ]
    
    t_team = Table(team_data, colWidths=[185, 125, 400])
    t_team.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('GRID', (0, 0), (-1, -1), 0.5, SLATE_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, SLATE_BG]),
    ]))
    story.append(t_team)
    story.append(Spacer(1, 10))

    # Indicadores finales de calidad
    final_metrics = [
        [
            Paragraph("<b>82 / 82 Tests Pasando (100%)</b><br/><font color='#059669' size='7.5'>Ingesta, Pydantic, OCI, Bots y Streamlit</font>", card_title),
            Paragraph("<b>Semana 5 Ganada de Ventaja</b><br/><font color='#4F46E5' size='7.5'>Dedicada a Hardening, Accesibilidad y QA</font>", card_title),
            Paragraph("<b>Produccion en Vivo Activa</b><br/><font color='#C74634' size='7.5'>Dominio HTTPS Caddy + OCI Compute</font>", card_title),
        ]
    ]
    t_fmet = Table(final_metrics, colWidths=[236, 238, 236])
    t_fmet.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), EMERALD_BG),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#86EFAC")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_fmet)
    
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>[NOTAS DEL PRESENTADOR - 1:00 min]:</b> <i>Cerrar con fuerza destacando la diversidad internacional del equipo (Colombia, Peru, Paraguay, Bolivia, Argentina). Recalcar que CommunityLab es una solucion terminada, con 82 pruebas aprobadas al 100%, desplegada en vivo y lista para integrarse de inmediato en el ecosistema de Oracle y Alura.</i>", notes_style))

    doc.build(story, canvasmaker=SlideCanvas)
    print(f"✅ Presentación PDF generada exitosamente en: {filename}")


if __name__ == "__main__":
    output_path = sys.argv[1] if len(sys.argv) > 1 else "PM_Files/Presentacion_CommunityLab_4_Slides.pdf"
    create_slide_deck(output_path)
