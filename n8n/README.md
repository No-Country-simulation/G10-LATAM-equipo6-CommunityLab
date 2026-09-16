# 🔄 n8n — Orquestador de Flujos en CommunityLab

Este directorio contiene la documentación, flujos versionados y guías operativas de **n8n**, el motor de orquestación central de CommunityLab.

---

## 🌐 Instancia Central del Equipo (OCI Cloud)

El equipo cuenta con una instancia activa de n8n desplegada en una máquina virtual Linux Always Free en **Oracle Cloud Infrastructure (OCI)**:

* **URL de acceso:** [http://147.15.9.116:5678](http://147.15.9.116:5678)
* **Entorno VM:** Ubuntu Linux en OCI (`/home/ubuntu/n8n-hackathon`)
* **Responsables Infra / n8n:** José Medina & César Cely

### 👥 Acceso para Miembros del Equipo
1. Solicita a José Medina o César Cely la invitación a tu correo electrónico desde el panel de n8n (`Settings > Users > Invite User`).
2. Una vez aceptada la invitación, podrás ver y editar los flujos compartidos en el proyecto de la Hackathon.

---

## 💻 Ejecución Local (Alternativa para desarrollo offline)

Si deseas probar flujos o nodos en tu máquina local sin afectar la instancia compartida:

```bash
# 1. Asegúrate de tener Docker y Docker Compose instalados
docker compose up -d

# 2. Abrir en el navegador
http://localhost:5678
```

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

## ⚙️ Configuración Recomendada en la VM de OCI

Para la instancia en producción en la VM, el archivo `/home/ubuntu/n8n-hackathon/docker-compose.yml` debe contemplar:

```yaml
version: "3"
services:
  n8n:
    image: docker.n8n.io/n8nio/n8n:latest
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://147.15.9.116:5678/
      - NODE_ENV=production
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=24
      - NODE_OPTIONS=--max-old-space-size=512
      - N8N_SECURE_COOKIE=false
      - GENERIC_TIMEZONE=America/Bogota
      - N8N_DEFAULT_BINARY_DATA_MODE=filesystem
    volumes:
      - n8n_data:/home/node/.n8n
volumes:
  n8n_data:
```
