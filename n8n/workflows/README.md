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
  * `Wait` (12s) para control estricto de cuota (TPM/RPM).

