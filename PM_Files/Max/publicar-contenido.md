# 📢 Estrategia y Viabilidad de Publicación Automática: LinkedIn, X (Twitter) y Newsletters

> **Proyecto:** CommunityLab — Hackathon Oracle ONE & Alura  
> **Autor / Desarrollador:** Max Ferrer Cabanillas Salas (`mcabanillassalas`) — Backend & Pipeline Developer  
> **Célula:** Células 1 & 3 (IA, Pipeline E2E & Curaduría Streamlit / Canales Dinámicos)  
> **Fecha:** 23 de Septiembre de 2026  
> **Estado:** Documento de Análisis Arquitectónico y Diseño Técnico  

---

## 1. Contexto y Objetivo de Negocio

El enunciado oficial del proyecto CommunityLab establece:

> *"Generador Automático de Contenido para Redes Sociales: Creación de publicaciones estructuradas para LinkedIn, X (Twitter) y Newsletters a partir de debates y logros de la comunidad."*

Actualmente, el pipeline de CommunityLab ya procesa la actividad de las comunidades (ingesta batch y canales interactivos en Telegram, Discord y Slack), extrayendo mediante IA:
- Detección de sentimiento y clasificación temática.
- Respuestas directas al usuario con soporte técnico y FAQ.
- **Activos de marketing generados:** Copys estructurados para publicaciones (`post_linkedin`, tips técnicos y síntesis de debates).

En la interfaz de usuario en **Streamlit** (`src/ui/app.py`), el Community Manager cuenta con el módulo **"Curaduría Humana" (Human-in-the-Loop)**, donde puede inspeccionar el activo, editar el texto generado y pulsar el botón **"✅ Aprobar Copy"**.

### La Interrogante Planteada
Una vez aprobado el copy en el panel de curaduría:
> **¿Qué tan viable es incorporar botones de publicación directa ("Publicar en LinkedIn", "Publicar en X", "Publicar en Newsletter") bajo los dos enfoques del proyecto: 1. n8n Nativo vs 2. Python Puro?**

---

## 2. Análisis de Viabilidad por Red / Canal

### 2.1 LinkedIn (Alta Relevancia para el Proyecto)

LinkedIn es la red prioritaria de Oracle ONE y Alura para amplificar contrataciones de alumnos, proyectos destacados y casos de éxito.

* **API Oficial:** LinkedIn REST API v2 (`/rest/posts` o `/v2/ugcPosts`).
* **Permisos Requeridos:**
  - `w_member_social`: Para publicar en el perfil personal del usuario autenticado.
  - `w_organization_social`: Para publicar en la página oficial de la empresa/organización (ej. Página de Oracle ONE o Alura). Requiere ser Administrador verificado de dicha página de LinkedIn.
* **Mecanismo de Autenticación:**
  - OAuth 2.0 con *3-legged Authorization Code Flow*.
  - El usuario debe iniciar sesión en un navegador, autorizar la app creada en el [LinkedIn Developer Portal](https://developer.linkedin.com/) y recibir un `access_token`.
  - Duración del token: **60 días**.
* **Viabilidad Técnica:**
  - **Muy Alta.** El texto generado por la IA en CommunityLab ya viene con estructura de copy profesional (gancho, desarrollo, hashtags `#OracleONE #AluraLatam` y emojis).
  - Ambos mundos (n8n y Python) pueden publicar posts de texto simple o texto con imagen/enlace con una sola llamada HTTP POST.

---

### 2.2 X / Twitter (Media-Alta Relevancia, pero con Barreras de API)

Ideal para la amplificación rápida de debates técnicos, FAQs cortas e hilos de aprendizaje.

* **API Oficial:** X API v2 (`POST https://api.twitter.com/2/tweets`).
* **Barreras y Restricciones Actuales de la Plataforma (Factores Críticos):**
  - **Límites de Caracteres:** Máximo **280 caracteres** por tweet (a menos que la cuenta posea X Premium). Un copy de LinkedIn suele tener entre 500 y 1,200 caracteres, por lo que para X se requiere:
    1. Recorte inteligente con resumen del copy.
    2. O generación de un hilo (Thread) de 2 a 3 tweets enlazados.
  - **Política de API de X (Nivel Gratuito / Free Tier):**
    - La API gratuita de X permite un volumen write-only de hasta 1,500 tweets mensuales por app.
    - Sin embargo, obtener la aprobación de la cuenta de desarrollador en [developer.x.com](https://developer.x.com/) requiere verificación de número telefónico y justificación de caso de uso que puede demorar de 24 a 72 horas.
* **Mecanismo de Autenticación:**
  - OAuth 1.0a (API Key, API Secret, Access Token, Access Token Secret) o OAuth 2.0 User Context (PKCE con scope `tweet.write`).
* **Viabilidad Técnica:**
  - **Alta en código, Media en configuración:** Enviar un tweet por API toma 10 líneas de código, pero depende de la disponibilidad inmediata de credenciales activas de Twitter Developer.

---

### 2.3 Newsletters (Definición del Objetivo)

A diferencia de LinkedIn o X, *"Newsletter"* no es una red social única, sino una categoría de distribución de correo/boletines. Para integrarla, es obligatorio definir la plataforma objetivo:

| Plataforma | API Oficial | Evaluación para CommunityLab |
| :--- | :--- | :--- |
| **Substack** | ❌ **No tiene API pública oficial de publicación.** | No recomendado para integración formal por requerir web scraping frágil y no oficial. |
| **Resend / SendGrid** | ✅ **API REST moderna y abierta.** | **Altamente Recomendado.** Permite enviar el newsletter estructurado en HTML/Markdown a una lista de suscriptores con un simple token de API. |
| **Brevo (Sendinblue) / Mailchimp** | ✅ **API REST completa + Nodos n8n nativos.** | **Muy Recomendado para n8n.** Permiten crear campañas en estado "Draft" (Borrador) listas para ser revisadas y enviadas. |
| **Beehiiv / Ghost** | ✅ **API REST de publicación directa.** | Excelente para newsletters tipo blog moderno con soporte de `POST /posts` con estado `draft` o `published`. |
| **Boletín Markdown Digest en OCI (Alternativa Interna)** | ✅ **Arquitectura nativa del proyecto.** | Los activos aprobados se consolidan en un archivo semanal `newsletter_semana_XX.md` o HTML y se almacenan automáticamente en el bucket de **Oracle Cloud (OCI Object Storage)** para consumo del equipo editorial. |

---

## 3. Comparativa: Opción 1 (n8n Nativo) vs. Opción 2 (Python Puro)

A continuación se contrastan ambos enfoques para implementar los botones:  
`[🚀 Publicar LinkedIn]` — `[🐦 Publicar X]` — `[📰 Publicar Newsletter]`

```
                             [ Panel Curaduría Streamlit ]
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   ▼                                             ▼
        [ OPCIÓN 1: n8n Nativo ]                      [ OPCIÓN 2: Python Puro ]
                   │                                             │
      POST /webhook/publicar-redes                    Llamada a módulos internos
                   │                                     src/publishers/*.py
                   ▼                                             ▼
     Flujo n8n con Nodos Oficiales:               Librerías SDKs / REST en Python:
      - LinkedIn Node                              - requests (LinkedIn REST)
      - Twitter Node                               - tweepy / requests (X API v2)
      - Mailchimp / SendGrid Node                  - resend / sendgrid / oci_client
                   │                                             │
                   ▼                                             ▼
            [ REDES / BOLETINES ]                         [ REDES / BOLETINES ]
```

### Tabla Comparativa de Criterios

| Criterio de Evaluación | Opción 1: n8n Nativo | Opción 2: Python Puro |
| :--- | :--- | :--- |
| **Desacoplamiento** | 🟢 **Excelente:** Streamlit solo envía un webhook JSON (`{red, copy, id}`). Toda la lógica de redes vive aislada en n8n. | 🟡 **Medio:** Las dependencias (`tweepy`, SDKs de correo) se instalan en el entorno virtual de Python (`env3.11`). |
| **Gestión de Credenciales OAuth** | 🟢 **Superior:** n8n cuenta con gestión visual de credenciales OAuth2, refresco automático de tokens y reintentos automáticos. | 🔴 **Complejo:** En Python puro hay que gestionar manualmente la expiración del `access_token` de LinkedIn y el intercambio de códigos OAuth. |
| **Velocidad de Implementación** | 🟢 **Muy Rápida:** Conectar nodos drag & drop de LinkedIn, Twitter y SendGrid en n8n toma minutos. | 🟡 **Media:** Requiere escribir y probar clases clientes (`LinkedInPublisher`, `TwitterPublisher`, `NewsletterPublisher`). |
| **Testeo Automatizado (CI/CD)** | 🟡 **Externo:** Se prueba vía peticiones HTTP mock a n8n o verificando el webhook. | 🟢 **Excelente:** 100% integrable a la suite de tests existente con `pytest` y mocks de `unittest.mock`. |
| **Dependencias de Infraestructura** | 🔴 **Requiere n8n activo:** Depende de que el contenedor Docker esté arriba y tenga conectividad pública si la red requiere callback URL. | 🟢 **Independiente:** Funciona de forma autónoma con solo ejecutar Streamlit o scripts de consola. |
| **Flexibilidad de Formateo** | 🟢 **Alta:** Nodos `Code` en n8n para adaptar el copy por red (ej. recortar a 280 caracteres para Twitter). | 🟢 **Alta:** Métodos Python de transformación de texto (`formatear_para_tweet()`, `formatear_para_newsletter()`). |

---

## 4. Diseño de la Solución en Ambas Opciones

### 4.1 Enfoque con Opción 1: n8n Nativo (Recomendado para Redes Sociales)

#### ¿Cómo interactúa Streamlit?
Al hacer clic en el botón de Streamlit, Python solo hace una petición POST al webhook de n8n:

```python
# En src/ui/app.py
if st.button("🚀 Publicar en LinkedIn", key=f"btn_lk_{id}"):
    payload = {
        "accion": "publicar",
        "red": "linkedin",
        "interaccion_id": interaccion["id"],
        "autor_original": interaccion["autor"],
        "copy_aprobado": copy_editado,
        "metadata": {"canal": interaccion["canal_origen"]}
    }
    # Enviar al webhook de n8n (sea local o ngrok)
    resp = requests.post(f"{get_n8n_webhook_base()}webhook/communitylab-publicar", json=payload)
    if resp.status_code == 200:
        st.success("✅ ¡Publicación enviada exitosamente a LinkedIn vía n8n!")
```

#### Flujo en n8n (`CommunityLab_Publicador_Omnicanal`):
1. **Webhook Inbound Node:** Recibe `POST /webhook/communitylab-publicar`.
2. **Switch Node (Enrutador por Red):**
   - Rama 1: `red == 'linkedin'` ➡️ **LinkedIn Node** (Usa credencial OAuth2 y publica post en feed).
   - Rama 2: `red == 'twitter'` ➡️ **Code Node** (Ajusta a 280 caracteres) ➡️ **Twitter Node** (Crea Tweet en X).
   - Rama 3: `red == 'newsletter'` ➡️ **SendGrid / Resend Node** (Envía borrador o campaña a la lista de correo) o guarda el Markdown en OCI.
3. **Respond to Webhook Node:** Retorna `{status: "ok", url_publicacion: "https://...", id: "..."}`.

---

### 4.2 Enfoque con Opción 2: Python Puro (Recomendado para Independencia Total)

#### Arquitectura de Clientes en `src/publishers/`:
Se crea un paquete modular limpio en el backend:

```text
src/
└── publishers/
    ├── __init__.py
    ├── base_publisher.py       # Clase abstracta con interface publicar()
    ├── linkedin_publisher.py   # Cliente HTTP REST para LinkedIn API v2
    ├── twitter_publisher.py    # Cliente usando tweepy o requests con OAuth 1.0a
    └── newsletter_publisher.py # Cliente para Resend / SendGrid o generador OCI
```

#### Implementación del Publicador Base con Modo Simulación (Mock):
Para garantizar que la demo de la hackatón funcione **incluso si un jurado no tiene tokens reales de LinkedIn o Twitter**, se implementa un patrón con fallback automático a simulación:

```python
# src/publishers/linkedin_publisher.py
import os
import requests
from src.utils.logger import setup_logger

logger = setup_logger("CommunityLab.Publishers.LinkedIn")

class LinkedInPublisher:
    def __init__(self, access_token: str = None):
        self.access_token = access_token or os.getenv("LINKEDIN_ACCESS_TOKEN", "").strip()

    def publicar_post(self, texto: str) -> dict:
        if not self.access_token or self.access_token.startswith("tu_token"):
            logger.info("Modo Simulación activo: Publicación en LinkedIn simulada con éxito.")
            return {
                "success": True,
                "modo": "SIMULACION",
                "post_url": "https://www.linkedin.com/feed/update/urn:li:share:simulacion-communitylab-001",
                "mensaje": "Post simulado correctamente (Token no configurado)"
            }
        
        # Publicación Real REST API v2
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        # Payload oficial de LinkedIn UGC
        # ...
```

---

## 5. Estrategia Pragmática y Recomendada para el Hackatón

Para la presentación del proyecto ante los evaluadores de Oracle y Alura, la mejor estrategia técnica es una **Solución Híbrida Inteligente**:

### 1. En la Interfaz de Curaduría (Streamlit):
Organizar los botones de acción post-aprobación en una fila de 3 columnas compactas:
- Columna 1: `[ 🚀 Publicar en LinkedIn ]`
- Columna 2: `[ 🐦 Publicar en X (Twitter) ]`
- Columna 3: `[ 📰 Añadir a Newsletter ]`

### 2. Definición del Newsletter Objetivo para la Hackatón:
Se recomienda adoptar un **modelo de doble impacto**:
- **Canal Externo (Marketing):** Envío de un correo de prueba estructurado vía **Resend** o **SendGrid** (que otorgan cuentas gratuitas instantáneas con API Key en 2 minutos sin trabas burocráticas).
- **Canal Interno (Curaduría & OCI):** Consolidación semanal acumulativa en un archivo `activos/boletines/newsletter_semanal_oracle_alura.md` subido automáticamente al Bucket de **Oracle Cloud (OCI Object Storage)**, listo para ser consumido por el equipo de Marketing.

### 3. Modo Real con Respaldo de Simulación Transparente:
- Si existen tokens en `.env` (`LINKEDIN_ACCESS_TOKEN`, `TWITTER_API_KEY`, `RESEND_API_KEY`): Se realiza la publicación en vivo a la red correspondiente.
- Si no existen tokens (o están en placeholder): El sistema simula la publicación, muestra la tarjeta de éxito con el enlace simulado y actualiza el estado del activo a `"publicado": true` en el historial acumulativo.
- **Resultado:** El flujo de curaduría y publicación se demuestra de extremo a extremo sin riesgo de fallar durante la presentación en vivo.

---

## 6. Próximos Pasos Sugeridos

1. **Prioridad Inmediata Actual:** Finalizar la validación pendiente de **Slack con n8n** (`CommunityLab_Slack_Dinamico`) para completar el 100% de canales interactivos en ambas vías (Python y n8n).
2. **Fase Posterior (Publicadores):**
   - Crear el módulo base `src/publishers/` en Python para dotar a Streamlit de los botones de publicación directa.
   - Crear el flujo `CommunityLab_Publicador_Omnicanal.json` en n8n para quien prefiera delegar la publicación al orquestador visual.
