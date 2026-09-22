# 🔄 n8n — Orquestador de Flujos en CommunityLab

Este directorio contiene la documentación, flujos versionados y guías operativas de **n8n**, el motor de orquestación central de CommunityLab.

---

## 🌐 Instancia Central del Equipo (OCI Cloud)

El equipo cuenta con una instancia activa de n8n desplegada en una máquina virtual Linux Always Free en **Oracle Cloud Infrastructure (OCI)**:

* **URL de acceso:** [http://147.15.9.116:5678](http://147.15.9.116:5678)
* **Entorno VM:** Ubuntu Linux en OCI (`/home/ubuntu/G10-LATAM-equipo6-CommunityLab`)
* **Responsables Infra / n8n:** José Medina & César Cely

### 👥 Acceso para Miembros del Equipo
1. Solicita a José Medina o César Cely la invitación a tu correo electrónico desde el panel de n8n (`Settings > Users > Invite User`).
2. Una vez aceptada la invitación, podrás ver y editar los flujos compartidos en el proyecto de la Hackathon.

---

## 💻 Ejecución Local (Alternativa para desarrollo offline)

Si deseas probar flujos o nodos en tu máquina local sin afectar la instancia compartida:

```bash
# 1. Levantar el servicio
docker compose up -d

# 2. Abrir en el navegador
http://localhost:5678
```

---

## 🚀 Patrones Arquitectónicos del Pipeline en n8n

### 1. Ingesta Integrada vía Webhook HTTP (Interacción directa con Streamlit)
Utilizado para el disparo interactivo desde la UI ([`n8n/workflows/communitylab_ingesta_local_webhook.json`](workflows/communitylab_ingesta_local_webhook.json)):
1. **Webhook Trigger:** Expone el endpoint `POST /webhook/communitylab-ingesta` que recibe el lote de interacciones pre-filtrado por Streamlit.
2. **Normalización & Batching:** Procesa las interacciones individualmente o en micro-lotes sin generar archivos locales temporales.
3. **Inferencia LLM:** Emplea Google Gemini o Groq con esquemas estructurados para clasificar y generar copys.
4. **Bifurcación y Enrutamiento:** Separa los activos en los 4 formatos especializados:
   - `marketing_linkedin_logros.json`
   - `marketing_showcase.json`
   - `faqs_soporte_tecnico.json`
   - `metricas_feedback_comunidad.json`
5. **Persistencia en OCI Object Storage:** Carga directa al Bucket `communitylab-activos-marketing` bajo el prefijo `activos/{YYYY-MM-DD}/`.
6. **Respuesta al Webhook:** Retorna el paquete consolidado a Streamlit para su inspección inmediata.

### 2. Flujo Autónomo en Lote (Batching con Rate Limiting)
Para procesar interacciones directamente en lote desde el almacenamiento:
1. **Ingesta de Datos:** Nodo `Code` que lee y emite individualmente los registros del dataset.
2. **Control de Flujo:** Nodo `Loop Over Items` con `Batch Size: 1` para procesamiento secuencial.
3. **Inferencia LLM:** Nodo `Basic LLM Chain` conectado a Groq o Gemini con System Prompt estandarizado.
4. **Validación Estructurada:** Subnodo `Structured Output Parser` que valida y extrae tipadamente `sentimiento`, `tipo_contenido`, `temas_clave`, `post_linkedin` y `tip_tecnico_faq`.
5. **Consolidación (Metadata):** Nodo `Edit Fields (Set)` que fusiona los datos del autor original con los activos generados.
6. **Resiliencia & Rate Limiting:** Nodo `Wait` para proteger el límite de TPM/RPM de la API.
7. **Cierre de Ciclo:** La salida de `Wait` regresa al loop hasta completar el lote.

---


## 📁 Convención de Versionado de Flujos (`workflows/`)

Para asegurar que los workflows no queden únicamente en la base de datos de la VM y podamos versionarlos con Git:

1. Cuando termines o actualices un workflow en n8n:
   * Haz clic en el menú del workflow (tres puntos `...`) $\rightarrow$ **Download**.
2. Guarda el archivo `.json` exportado en la carpeta `n8n/workflows/` con un nombre representativo:
   * `communitylab_main_pipeline.json` (Pipeline principal E2E)
   * `ingestion_gemini_subflow.json` (Subflujo de ingesta y análisis)
   * `oci_storage_subflow.json` (Subflujo de persistencia en OCI)
3. Haz `git add`, `git commit` y `git push` a tu rama.
4. **IMPORTANTE:** Nunca guardes credenciales de API (Gemini API Key, OCI Keys) embebidas en los nodos de texto. Configúralas siempre en el gestor de **Credentials** de n8n.

---

## ⚙️ Configuración Oficial en la VM de OCI

En la VM, el servicio corre en `/home/ubuntu/G10-LATAM-equipo6-CommunityLab/docker-compose.yml`:

```yaml
services:
  n8n:
    image: docker.n8n.io/n8nio/n8n:latest
    container_name: communitylab-n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=${N8N_WEBHOOK_URL:-http://localhost:5678/}
      - NODE_ENV=production
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=24
      - NODE_OPTIONS=--max-old-space-size=512
      - N8N_SECURE_COOKIE=false
      - GENERIC_TIMEZONE=America/Bogota
      - N8N_DEFAULT_BINARY_DATA_MODE=filesystem
      - N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=false
      - N8N_ALLOWED_FILE_PATHS=/home/node/data/
    volumes:
      - n8n_data:/home/node/.n8n
      - ./data:/home/node/data:ro

volumes:
  n8n_data:
    external: true
    name: n8n-hackathon_n8n_data
```

