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

### 2. `communitylab_ingesta_local_webhook.json` (Adaptación para Desarrollo Local y Streamlit)
* **Descripción:** Adaptación clonada del flujo original para recibir interacciones dinámicamente vía HTTP Webhook desde Streamlit o scripts locales y responder síncronamente.
* **Diferencias con el flujo original:**
  * **Disparador:** Nodo `Webhook` (`POST /webhook/communitylab-ingesta`) en lugar de `manualTrigger`.
  * **Entrada dinámica:** Recibe las interacciones seleccionadas en Streamlit (`$json.body.interacciones`) en lugar de datos fijos en código.
  * **Respuesta síncrona:** Nodo `Respond to Webhook` al completar el loop para devolver el paquete de activos estructurado a la UI.

### 3. `jmedinag_WF_002.json`
* **Descripción:** Flujo de trabajo de referencia desarrollado por José Medina.

### 4. `ingestion_groq_subflow.json`
* **Descripción:** Subflujo de inferencia rápida con Groq Cloud.

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
   * Selecciona `n8n/workflows/communitylab_ingesta_local_webhook.json`.
4. **Configurar Credencial de IA:**
   * En el nodo `Groq Chat Model` (o `Google Gemini Chat Model`), asigna tu API Key en las credenciales de n8n.
5. **Activar el Workflow:**
   * En la esquina superior derecha, cambia el switch a **Active** (Verde).
6. **Probar desde Streamlit:**
   * Abre `http://localhost:8501`, ve a **⚡ Ejecutar Pipeline** y presiona **🌐 Ejecutar con Orquestador n8n**.

