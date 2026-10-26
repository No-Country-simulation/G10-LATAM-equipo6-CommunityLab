# 🚀 CommunityLab — Guión Técnico de Presentación y Pitch (YouTube Demo)

**Hackathon ONE G10 — Oracle Next Education & Alura / No Country**  
**Equipo 6 — LATAM**

---

## 📋 Ficha Técnica del Pitch

- **⏱️ Duración Máxima:** 5:00 minutos *(Objetivo de grabación: ~4 minutos con 45 segundos)*.
- **🌐 Entorno de Producción Oficial:** [https://hackathon-g10-latam-06.duckdns.org/](https://hackathon-g10-latam-06.duckdns.org/)
- **☁️ Infraestructura Cloud:** Oracle Cloud Infrastructure (OCI) Always Free (Compute Linux VM + Object Storage S3).
- **🧠 Motores de IA:** Orquestación Dual con Google Gemini 2.5 Flash / Groq LLMs + Inferencia de Imagen Pollinations.ai (FLUX).
- **🧪 Cobertura de Calidad:** 82/82 pruebas unitarias e integrales automatizadas aprobadas (100%).
- **🎯 Audiencia Objetivo:** Mentores, evaluadores del jurado Oracle/Alura/No Country y comunidad tecnológica.

---

## 📌 1. Estructura General y Distribución de Tiempo

| Tiempo | Bloque Temático | Objetivo Clave en el Pitch | Recurso en Pantalla |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:35** (35s) | **1. Gancho & El Problema** | Exponer la pérdida del 95% del valor en chats de comunidad y presentar CommunityLab. | Animación del logo, capturas de chats caóticos en Discord/Telegram y carga de la aplicación en producción con HTTPS. |
| **0:35 - 1:30** (55s) | **2. Ingesta Omnicanal & Deduplicación** | Demostrar escucha activa en tiempo real y el filtro deduplicador en OCI Storage. | Pantalla dividida: Envío de mensaje en Telegram/Discord + panel *Conexiones & Bots* y lote en Streamlit. |
| **1:30 - 2:40** (70s) | **3. Motor Dual, Curaduría & Imágenes** | Explicar conmutación Gemini/n8n, 4 formatos temáticos, generador de imágenes y soporte PAR. | Vista *Curaduría Tri-Panel*: edición de copy, generación de imagen con IA y previsualización en mockup de redes. |
| **2:40 - 3:30** (50s) | **4. Infraestructura OCI, Seguridad & QA** | Demostrar despliegue Always Free, Caddy HTTPS, clave de administración y 82 pruebas pasando. | Consola OCI (VM + Bucket), Caddyfile, modal Settings con clave admin y terminal ejecutando `pytest`. |
| **3:30 - 4:25** (55s) | **5. El Equipo 6 y sus Aportes** | Presentar a los 7 integrantes con sus roles y contribuciones técnicas destacadas. | Diapositiva corporativa con fotos, nombres, banderas, roles y logros de cada integrante. |
| **4:25 - 4:45** (20s) | **6. Cierre & Call to Action** | Conclusión de impacto, agradecimientos a sponsors y código QR a GitHub. | Pantalla final con URL oficial, QR al repositorio y logos institucionales (Oracle, Alura, No Country). |

---

## 🎬 2. Guión Escena por Escena (Locución & Dirección Visual)

### 🔹 ESCENA 1: Gancho, Problema y Propuesta de Valor (0:00 - 0:35)
* **🎥 Indicación Visual:**  
  Cámara en pantalla dividida o PIP. Inicia con el logo animado de **CommunityLab**, seguido de clips rápidos de chats repletos de mensajes no leídos en Discord y Telegram. Transición fluida a la pantalla de inicio de la aplicación cargando en navegador con conexión segura HTTPS.
* **🎙️ Locución (Voz en Off):**  
  > *"En las comunidades de aprendizaje tecnológico como Discord, Slack o Telegram, todos los días ocurren cosas extraordinarias: estudiantes consiguen su primer empleo, obtienen certificaciones, resuelven errores complejos y construyen proyectos increíbles.  
  > Sin embargo, el **95% de ese valor se pierde en el scroll infinito del chat**.  
  > Para resolverlo, el **Equipo 6 de la Hackathon ONE G10** creó **CommunityLab**: el motor inteligente cloud-native que transforma la voz orgánica de la comunidad en activos de alto impacto listos para su distribución."*

---

### 🔹 ESCENA 2: Escucha Omnicanal en Vivo & Deduplicación OCI (0:35 - 1:30)
* **🎥 Indicación Visual:**  
  Grabación en vivo enviando un mensaje de prueba con un logro técnico en Telegram (`@G10_Latam_06_bot`) o Discord. Cambio inmediato al panel de Streamlit en la vista **`📡 Conexiones & Bots`** mostrando el bot respondiendo en verde, y la vista **`📥 Procesamiento e Ingesta`** procesando un lote con el deduplicador de OCI activado.
* **🎙️ Locución (Voz en Off):**  
  > *"CommunityLab opera mediante una arquitectura de escucha activa omnicanal. Cuenta con bots conectados en tiempo real a **Telegram**, **Discord** y **Slack Socket Mode**, además de un módulo de ingesta por lotes en JSON y CSV.  
  > Toda interacción pasa por un riguroso validador tipado en **Pydantic V2** y un **Deduplicador inteligente** que consulta directamente **Oracle Cloud Infrastructure (OCI) Object Storage**, garantizando que ninguna publicación se procese dos veces y manteniendo la arquitectura 100% Stateless."*

---

### 🔹 ESCENA 3: Orquestación Dual, Curaduría NovaEdu & Generador de Imágenes (1:30 - 2:40)
* **🎥 Indicación Visual:**  
  Vista **`📝 Curaduría Tri-Panel`**. Seleccionar un post pendiente de contratación. Mostrar conmutador de motor (Gemini vs n8n). Editar copy. Clic en el botón **`🎨 Generar Imagen con IA`**, mostrando el prompt visual y la imagen apareciendo al instante en el mockup interactivo de redes sociales.
* **🎙️ Locución (Voz en Off):**  
  > *"El corazón del sistema es su **Orquestación Dual Homologada**: podemos procesar contenido tanto con **Google Gemini 2.5** en Python puro a ultra-alta velocidad, como a través de flujos visuales en **n8n**.  
  > La IA analiza el sentimiento y clasifica automáticamente en 4 paquetes temáticos: logros para LinkedIn, FAQs técnicas, showcase de proyectos y métricas de salud comunitaria.  
  > En nuestro **Panel de Curaduría NovaEdu**, el Community Manager puede revisar, pulir el copy y activar nuestro **Generador de Imágenes Dual-Engine** con Groq y FLUX. Además, gracias a los tokens **PAR (Pre-Authenticated Requests)** de OCI, las imágenes alojadas en buckets privados se visualizan de forma instantánea y segura sin exponer credenciales."*

---

### 🔹 ESCENA 4: Infraestructura OCI Always Free, Seguridad & QA (2:40 - 3:30)
* **🎥 Indicación Visual:**  
  Vista rápida de la consola OCI (VM Compute `147.15.9.116` y Bucket S3). Pestaña **`⚙️ Settings & Seguridad`** mostrando el modal protegido por `SETTINGS_ADMIN_KEY`. Transición a la terminal ejecutando `pytest tests/ -v` con 82 pruebas pasando en verde.
* **🎙️ Locución (Voz en Off):**  
  > *"Toda la solución fue construida sobre el ecosistema **Always Free de Oracle Cloud Infrastructure**. La aplicación y el orquestador n8n corren en una máquina virtual Compute en Linux, protegida con proxy inverso **Caddy**, certificados automáticos SSL y dominio público bajo DuckDNS.  
  > En el apartado de seguridad, el panel de configuración está blindado contra fugas de secretos mediante una Clave de Verificación Administrativa.  
  > Y gracias a un desarrollo ágil y acelerado, ganamos una semana de ventaja previa a este Demo Day para realizar hardening, alcanzando **82 pruebas automatizadas unitarias e integrales con 100% de éxito**."*

---

### 🔹 ESCENA 5: Presentación del Equipo 6 y Aportes Destacados (3:30 - 4:25)
* **🎥 Indicación Visual:**  
  Diapositiva corporativa **`Equipo 6 - LATAM`** con fotos de perfil, banderas, roles e iconos de especialidad. Paneo suave mientras el locutor menciona las contribuciones clave.
* **🎙️ Locución (Voz en Off):**  
  > *"Detrás de CommunityLab hay un equipo multidisciplinario de 7 profesionales conectados desde toda Latinoamérica:  
  > - **César Cely (Colombia) - Project Manager & Cloud Architect:** Liderazgo, arquitectura OCI, gestión de buckets y proxy SSL Caddy.  
  > - **Max Ferrer (Perú) - Backend & Pipeline Developer:** Pipeline E2E en Python, adaptación frontend modular y conector LinkedIn.  
  > - **José Medina (Paraguay) - Especialista n8n & LLMs:** Admin de la VM OCI, microservicio de imágenes y flujos S3.  
  > - **Edwin Enriquez (Bolivia) - QA Lead & Backend:** Estrategia de testing y suite automatizada de 82 pruebas continuas.  
  > - **Carol Arancay (Perú) - Frontend & UX:** Diseño del sistema visual NovaEdu y curaduría del dataset oficial.  
  > - **Raúl Gallardo (Argentina) - QA & Cloud Support:** Pruebas de persistencia y soporte de nube OCI.  
  > - **Luygy Ruben Vivas Moreno (Colombia) - QA & Pruebas Funcionales:** Incorporado en las 2 últimas semanas, liderando pruebas funcionales de extremo a extremo, control de calidad y validación de la experiencia de usuario."*

---

### 🔹 ESCENA 6: Cierre, Agradecimientos & Llamado a la Acción (4:25 - 4:45)
* **🎥 Indicación Visual:**  
  Mockup en laptop y smartphone con la URL pública activa ([https://hackathon-g10-latam-06.duckdns.org/](https://hackathon-g10-latam-06.duckdns.org/)), código QR al repositorio de GitHub y logos de Oracle ONE, Alura Latam y No Country.
* **🎙️ Locución (Voz en Off):**  
  > *"CommunityLab demuestra cómo la inteligencia artificial generativa y la nube de Oracle pueden potenciar a las comunidades digitales, convirtiendo cada mensaje en una historia de éxito visible.  
  > Les invitamos a probar la demo en vivo y explorar nuestro código en GitHub.  
  > ¡Muchas gracias a Oracle, Alura y No Country por este emocionante reto! Somos el Equipo 6."*

---

## 👥 3. Tabla Consolidada de Integrantes y Contribuciones

| Integrante | País | Rol Principal | Aporte Técnico Específico al Proyecto |
| :--- | :--- | :--- | :--- |
| **César Augusto Cely Pulido** | 🇨🇴 Colombia | **Project Manager & Cloud Architect** | Liderazgo del equipo, arquitectura de nube en Oracle Cloud (OCI Always Free), administración de Object Storage y políticas S3, configuración de dominio DuckDNS, certificados SSL y proxy inverso Caddy, y orquestación integral del roadmap. |
| **Max Ferrer Cabanillas Salas** | 🇵🇪 Perú | **Backend & Pipeline Developer** | Desarrollo del pipeline E2E en Python (`pipeline.py`), ingesta y deduplicación con OCI, modularización y adaptación del frontend NovaEdu en 7 vistas Streamlit, e investigación/validación del conector de publicación en LinkedIn. |
| **José Medina** | 🇵🇾 Paraguay | **Oracle Ecosystem & n8n / LLMs** | Administración de la máquina virtual Ubuntu en OCI Compute (`147.15.9.116`), diseño y versionado de flujos n8n, implementación del microservicio de generación de imágenes (`POST /webhook/generar-imagen-post2`) con Groq y nodos S3. |
| **Edwin Gustavo Enriquez Arias** | 🇧🇴 Bolivia | **QA Lead & Testing Automation** | Definición de la estrategia de calidad del proyecto, desarrollo y mantenimiento de la suite automatizada de 82 pruebas con Pytest (100% aprobadas), validación de esquemas Pydantic V2 y blindaje de resiliencia en pipelines. |
| **Carol Yesenia Arancay Osorio** | 🇵🇪 Perú | **Frontend / UX & Data** | Conceptualización y diseño visual del sistema NovaEdu en Streamlit, propuesta de paleta corporativa y componentes UI, y enriquecimiento y validación del dataset oficial de interacciones de prueba (`data/interacciones_ejemplo.json`). |
| **Raúl Gallardo** | 🇦🇷 Argentina | **QA & Cloud Support** | Pruebas de estrés y conectividad contra OCI Object Storage, validación de integridad en paquetes de distribución generados y control de respuestas de la IA. |
| **Luygy Ruben Vivas Moreno** | 🇨🇴 Colombia | **QA & Pruebas Funcionales** | Integrado en las últimas 2 semanas del proyecto, aportando activamente con pruebas funcionales de extremo a extremo, validación exhaustiva de la experiencia de usuario (UX) en la UI y control de calidad sobre la generación de contenidos y bots omnicanal. |

---

## 🛠️ 4. Checklist & Consejos Técnicos de Grabación para YouTube

1. **Resolución & Formato:** Grabar a 1080p (1920x1080) a 60 fps en formato MP4 con OBS Studio.
2. **Entorno Visual Limpio:** Ocultar la barra de marcadores del navegador (`F11` o `Ctrl+Shift+B`), cerrar pestañas ajenas y usar el tema oscuro predeterminado de NovaEdu para resaltar los acentos azul eléctrico (#2563EB) y dorado (#F59E0B).
3. **Puntero & Clics:** Configurar cursor con halo amarillo o efecto de clic suave para que los evaluadores sigan fácilmente la navegación en el panel de curaduría y el mockup interactivo.
4. **Audio Profesional:** Grabar con micrófono condensador o auricular con cancelación de ruido. Aplicar filtro compresor y ecualización básica para mantener un volumen homogéneo entre -6dB y -3dB.
5. **Ritmo de Locución:** Mantener una cadencia de aproximadamente 140 a 150 palabras por minuto. El guión tiene exactamente ~710 palabras de locución, lo que cronometra ~4 minutos con 40 segundos, garantizando cumplir holgadamente la regla de "menos de 5 minutos".
6. **Miniatura (Thumbnail):** Diseñar miniatura atractiva con fondo azul oscuro, el logo de CommunityLab, captura del panel Streamlit y título de alto contraste: *"CommunityLab: El Motor de IA para Comunidades (Demo Oficial ONE G10)"*.
