# **Propuesta de Stack Tecnológico y Herramientas para CommunityLab (Borrador)**

# **1. Arquitectura en la Nube e Infraestructura**

* **Proveedor Cloud:** Oracle Cloud Infrastructure (OCI), limitando el uso estrictamente a los recursos de la capa *Always Free*.
* **Instancia de Cómputo:** Máquina Virtual (VM) con sistema operativo Ubuntu.
* **Gestión de Memoria y Rendimiento:** Implementación de instancias AMD configuradas con memoria SWAP para contrarrestar la limitación de 1 GB de RAM, manteniendo en evaluación el uso alternativo de instancias ARM (Ampere A1).
* **Almacenamiento Persistente:** OCI Object Storage para almacenar los activos generados, informes y archivos JSON, lo cual representa un requerimiento obligatorio para la evaluación del MVP.
* **Exposición y Acceso:** Configuración de un túnel temporal mediante Cloudflare para el acceso web y gestión de credenciales SSH seguras para los desarrolladores.

# **2. Orquestación y Backend**

* **Motor de Flujos y Automatización:** n8n ejecutado en un entorno contenerizado, destinado a la gestión de disparadores, nodos de inteligencia artificial y bifurcación condicional.
* **Alternativas de Orquestación (Fase de Evaluación):** Desarrollo de pipelines en Python utilizando LangChain o LangGraph.
* **Base de Datos y Vectores:** PostgreSQL con la extensión pgvector, sirviendo como alternativa viable frente a opciones de pago como OpenSearch.

# **3. Inteligencia Artificial y Procesamiento**

* **Modelos de Lenguaje Principales:** Integración con LLMs como Google Gemini (vía API con Google AI Studio), OpenAI (ChatGPT) o Anthropic Claude para las tareas de orquestación, redacción de copys persuasivos y análisis de sentimientos.
* **Estrategia de Optimización de Tokens:** Procesos de lematización y generación de resúmenes por fragmentos (*chunks*) para minimizar el consumo de cuotas en las APIs.
* **Modelos Locales (Opcional):** Despliegue de Ollama a través de Docker para habilitar modelos *open-source* y reducir dependencias de terceros.

# **4. Interfaz de Usuario (UI) y Curaduría**

* **Desarrollo del Panel Web:** Interfaz gráfica e interactiva construida con Streamlit o Gradio.
* **Funcionalidad:** Visualización de los datos procesados de la comunidad y un entorno amigable para que los usuarios aprueben, editen o descarten los activos de publicación.

# **5. Prácticas DevOps y Control de Versiones**

* **Repositorio Central:** Gestión del código en GitHub dentro de la organización "G10 Latam, equipo 6, Community Lab", asegurando que los archivos sensibles o credenciales queden excluidos del control de versiones.
* **Infraestructura como Código (IaC):** Utilización de Terraform (OCI Terraform Provider HCL) para la creación, conexión y estandarización de las instancias.
* **Contenerización:** Docker para encapsular el entorno de trabajo, abarcando PostgreSQL, n8n y componentes locales de Python.

# **6. Simulación e Ingestión de Datos (MVP)**

* **Fuentes de Entrada:** Archivos en formato JSON, CSV o un canal de Discord controlado.
* **Lote de Prueba:** Uso de un aproximado de 15 interacciones reales o controladas simulando canales para validar el producto mínimo viable sin saturar la infraestructura.

