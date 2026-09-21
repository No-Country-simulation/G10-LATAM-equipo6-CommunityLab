# Workflows de n8n (JSON Exports)

Este directorio almacena los flujos de n8n exportados para control de versiones en Git:

## 📦 Flujos Disponibles:

### 1. `communitylab_ingesta_llm.json`
* **Descripción:** Pipeline completo de ingesta, normalización, inferencia LLM y enriquecimiento de metadatos.
* **Componentes:**
  * Ingesta de 15 registros de `data/interacciones_ejemplo.json`.
  * `Loop Over Items` secuencial (Batch Size: 1).
  * `Basic LLM Chain` + `Groq Chat Model` (`openai/gpt-oss-20b`) / Gemini.
  * `Structured Output Parser` con validación estricta de JSON Schema.
  * `Edit Fields (Set)`: Fusión de metadatos de autor (`id`, `autor`, `canal`, `texto_original`) con los activos generados (`sentimiento`, `tipo_contenido`, `temas_clave`, `post_linkedin`, `tip_tecnico_faq`).
  * `Route by Content Type (Switch)`: Enrutamiento exclusivo por `tipo_contenido` con cuatro categorías conocidas y una salida fallback. En esta fase, todas las salidas regresan directamente a `Wait`; la preparación especializada y la persistencia OCI quedan pendientes.
  * `Wait` (12s) para control estricto de cuota (TPM/RPM).

### 2. `ingestion_groq_subflow.json`
* **Descripción:** Pipeline end-to-end con clasificación LLM (Groq Compound), enrutamiento condicional y persistencia en OCI Object Storage.
* **Componentes de Persistencia OCI:**
  * `Consolidar Paquete OCI`: Genera 4 paquetes estructurados e independientes (uno por categoría):
    1. `activos/{fecha}/marketing_linkedin_logros.json` (Historias de éxito para LinkedIn y Newsletter).
    2. `activos/{fecha}/faqs_soporte_tecnico.json` (FAQs y tips técnicos de soporte).
    3. `activos/{fecha}/marketing_showcase.json` (Proyectos y bots de la comunidad).
    4. `activos/{fecha}/metricas_feedback_comunidad.json` (Métricas de sentimiento y salud de comunidad).
  * `Convert to File`: Convierte cada uno de los 4 paquetes en binario en memoria (`mode: each`).
  * `Upload a file (S3)`: Sube los 4 objetos directamente al bucket `communitylab-activos-marketing` de OCI.

