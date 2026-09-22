# Workflows de n8n (JSON Exports)

Este directorio almacena los flujos de n8n exportados para control de versiones en Git:

## 📦 Flujos Disponibles:

### 1. `communitylab_ingesta_llm.json` (Flujo Original del Equipo - César Cely)
* **Descripción:** Pipeline original de ingesta y análisis con disparador manual (`manualTrigger`) y dataset integrado de 15 interacciones.
* **Componentes:**
  * Ingesta fija de 15 registros de `data/interacciones_ejemplo.json`.
  * `Loop Over Items` secuencial (Batch Size: 1).
  * `Basic LLM Chain` + `Groq Chat Model` (`openai/gpt-oss-20b`) / Gemini.
  * `Structured Output Parser` con validación estricta de JSON Schema.
  * `Edit Fields (Set)`: Fusión de metadatos de autor con los activos generados.
  * `Wait` (12s) para control estricto de cuota (TPM/RPM).

### 2. `ingestion_groq_subflow.json` (Persistencia E2E en OCI Object Storage)
* **Descripción:** Pipeline end-to-end con clasificación LLM (Groq Compound), enrutamiento condicional y persistencia en OCI Object Storage.
* **Componentes de Persistencia OCI:**
  * `Consolidar Paquete OCI`: Genera 4 paquetes estructurados e independientes (uno por categoría):
    1. `activos/{fecha}/marketing_linkedin_logros.json` (Historias de éxito para LinkedIn y Newsletter).
    2. `activos/{fecha}/faqs_soporte_tecnico.json` (FAQs y tips técnicos de soporte).
    3. `activos/{fecha}/marketing_showcase.json` (Proyectos y bots de la comunidad).
    4. `activos/{fecha}/metricas_feedback_comunidad.json` (Métricas de sentimiento y salud de comunidad).
  * `Convert to File`: Convierte cada uno de los 4 paquetes en binario en memoria (`mode: each`).
  * `Upload a file (S3)`: Sube los 4 objetos directamente al bucket `communitylab-activos-marketing` de OCI.

### 3. `communitylab_ingesta_local_webhook.json` (Adaptación para Desarrollo Local y Streamlit)
* **Descripción:** Adaptación para recibir interacciones dinámicamente vía HTTP Webhook desde Streamlit o scripts locales y responder síncronamente.
* **Diferencias con el flujo original:**
  * **Disparador:** Nodo `Webhook` (`POST /webhook/communitylab-ingesta`) en lugar de `manualTrigger`.
  * **Entrada dinámica:** Recibe las interacciones seleccionadas en Streamlit (`$json.body.interacciones`).
  * **Respuesta síncrona:** Nodo `Respond to Webhook` al completar el loop para devolver el paquete de activos estructurado a la UI.

### 4. `jmedinag_WF_002.json`
* **Descripción:** Flujo de trabajo de referencia desarrollado por José Medina.

---

## 🛠️ Cómo importar y activar en n8n Local (`http://localhost:5678`)

Para que cualquier miembro del equipo pruebe el flujo completo en su máquina:

1. **Levantar el servicio:**
   ```bash
   docker compose up -d
   ```
2. **Abrir n8n en el navegador:**
   [http://localhost:5678](http://localhost:5678)
3. **Importar el flujo:**
   * Ve al menú superior derecho (`...`) $\rightarrow$ **Import from file**.
   * Selecciona el workflow deseado de `n8n/workflows/`.
4. **Configurar Credencial de IA:**
   * En el nodo `Groq Chat Model` (o `Google Gemini Chat Model`), asigna tu API Key en las credenciales de n8n.
5. **Activar el Workflow:**
   * En la esquina superior derecha, cambia el switch a **Active** (Verde).
