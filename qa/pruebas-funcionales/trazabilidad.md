# Matriz de trazabilidad - CommunityLab (pruebas funcionales QA)

- Fecha de generación: 2026-10-11 23:14 -03:00
- Commit probado: 36f8ca8
- Entorno: local (Windows y Docker Desktop), salvo INF-06 contra el servidor del equipo

## Resumen por estado
| Estado | Casos |
|---|---|
| Pendiente | 45 |
| Bloqueado | 6 |
| Parcial | 2 |
| No concluyente | 2 |
| Falló | 1 |
| En curso | 1 |

## Matriz: backlog, caso, evidencia
| ID | Historia del backlog | Prueba | Estado | Evidencias | Última evidencia | Nota |
|---|---|---|---|---|---|---|
| INF-01 | Infraestructura y setup base | Terraform fmt, init, validate y plan | No concluyente | - | - | validate corrió sin confirmar que existan archivos tf. Plan pendiente |
| INF-02 | Infraestructura y setup base | Aprovisionamiento de la VM | Pendiente | - | - |  |
| INF-03 | Infraestructura y setup base | Acceso SSH | Pendiente | - | - |  |
| INF-04 | Infraestructura y setup base | Recursos y SWAP | Pendiente | - | - |  |
| INF-05 | Infraestructura y setup base | Seguridad del repositorio (secretos) | Pendiente | - | - |  |
| INF-06 | Infraestructura y setup base | Exposición de puertos | Parcial | INF-06.txt | 2026-10-11 19:18 | 22 5678 y 8501 abiertos y 5432 cerrado. Falta verificar login en N8N-01 y UI-07 |
| DOC-01 | Contenedores Docker | Levantar entorno Docker | Parcial | DOC-01_diagnostico_volumen.txt, DOC-01_ps.txt, DOC-01_up.txt, DOC-01_volumen_creado.txt | 2026-10-11 20:34 | Falló al inicio por volumen externo inexistente. Con el volumen creado a mano n8n quedó Up. El compose solo define n8n |
| DOC-02 | Contenedores Docker | Logs limpios | Pendiente | - | - |  |
| DOC-03 | Contenedores Docker | Reproducibilidad desde cero | Pendiente | - | - | El primer intento falló por el volumen externo |
| DOC-04 | Contenedores Docker | Persistencia tras restart | Bloqueado | - | - | Sin servicio de base de datos en el compose actual (por confirmar) |
| DB-01 | PostgreSQL + pgvector | Conexión a PostgreSQL | Bloqueado | - | - | Sin servicio PostgreSQL en el compose actual (por confirmar) |
| DB-02 | PostgreSQL + pgvector | Extensión vector | Bloqueado | - | - | Depende de DB-01 |
| DB-03 | PostgreSQL + pgvector | Esquema | Bloqueado | - | - | Depende de DB-01 |
| DB-04 | PostgreSQL + pgvector | Búsqueda semántica | Bloqueado | - | - | Depende de DB-01 |
| DB-05 | PostgreSQL + pgvector | Datos inválidos | Bloqueado | - | - | Depende de DB-01 |
| N8N-01 | Orquestador n8n | Acceso y autenticación | Pendiente | N8N-01.txt | 2026-10-11 20:58 |  |
| N8N-02 | Orquestador n8n | Workflows importados y activos | En curso | N8N-02.txt, N8N-02_activacion.txt | 2026-10-11 22:31 | 8 workflows en el repo con rutas duplicadas. Falta confirmar importación y activación |
| N8N-03 | Orquestador n8n | Webhook con mensaje válido | Falló | - | - | HTTP 500 Error in workflow en entorno local. Causa por determinar |
| N8N-04 | Orquestador n8n | Webhook con entradas inválidas | No concluyente | N8N-04.csv, N8N-04.txt, N8N-04_contenedor.txt, N8N-04_respuesta_control.txt | 2026-10-11 22:58 | El control dio 500. JSON malformado 422 y GET 404 |
| N8N-05 | Orquestador n8n | Entrada y salida por nodo | Pendiente | - | - |  |
| PY-01 | Sistema dual: pipelines Python (fallback) | Entorno Python | Pendiente | - | - |  |
| PY-02 | Sistema dual: pipelines Python (fallback) | Ejecución aislada | Pendiente | - | - |  |
| PY-03 | Sistema dual: pipelines Python (fallback) | Paridad n8n vs Python | Pendiente | - | - |  |
| PY-04 | Sistema dual: pipelines Python (fallback) | Failover real | Pendiente | - | - |  |
| PY-05 | Sistema dual: pipelines Python (fallback) | Recuperación | Pendiente | - | - |  |
| PY-06 | Sistema dual: pipelines Python (fallback) | Sobrecarga | Pendiente | - | - |  |
| PY-07 | Sistema dual: pipelines Python (fallback) | Tests existentes | Pendiente | - | - |  |
| IA-01 | APIs de IA, prompts e imágenes | Conexión Gemini | Pendiente | - | - |  |
| IA-02 | APIs de IA, prompts e imágenes | Respaldo OpenAI | Pendiente | - | - |  |
| IA-03 | APIs de IA, prompts e imágenes | Análisis de sentimiento | Pendiente | - | - |  |
| IA-04 | APIs de IA, prompts e imágenes | Voz de marca | Pendiente | - | - |  |
| IA-05 | APIs de IA, prompts e imágenes | Respuesta al usuario | Pendiente | - | - |  |
| IA-06 | APIs de IA, prompts e imágenes | Chunking y lematización | Pendiente | - | - |  |
| IA-07 | APIs de IA, prompts e imágenes | Prompt injection | Pendiente | - | - |  |
| IA-08 | APIs de IA, prompts e imágenes | Límites de API | Pendiente | - | - |  |
| IA-09 | APIs de IA, prompts e imágenes | Imágenes Pollinations | Pendiente | - | - |  |
| LOG-01 | Lógica condicional | Pregunta frecuente a FAQ | Pendiente | - | - |  |
| LOG-02 | Lógica condicional | Elogio genera post | Pendiente | - | - |  |
| LOG-03 | Lógica condicional | Queja grave emite alerta | Pendiente | - | - |  |
| LOG-04 | Lógica condicional | Mensaje ambiguo | Pendiente | - | - |  |
| LOG-05 | Lógica condicional | Mensaje en dos categorías | Pendiente | - | - |  |
| UI-01 | Panel Streamlit | Carga de Streamlit | Pendiente | - | - |  |
| UI-02 | Panel Streamlit | Lista de publicaciones | Pendiente | - | - |  |
| UI-03 | Panel Streamlit | Aprobar, rechazar y editar | Pendiente | - | - |  |
| UI-04 | Panel Streamlit | Lista vacía | Pendiente | - | - |  |
| UI-05 | Panel Streamlit | Textos largos y acentos | Pendiente | - | - |  |
| UI-06 | Panel Streamlit | Responsive | Pendiente | - | - |  |
| UI-07 | Panel Streamlit | Acceso sin autenticación | Pendiente | - | - |  |
| OBJ-01 | JSON en OCI Object Storage | JSON en el bucket | Pendiente | - | - |  |
| OBJ-02 | JSON en OCI Object Storage | JSON válido | Pendiente | - | - |  |
| OBJ-03 | JSON en OCI Object Storage | Nombres sin colisión | Pendiente | - | - |  |
| OBJ-04 | JSON en OCI Object Storage | Bucket privado | Pendiente | - | - |  |
| OBJ-05 | JSON en OCI Object Storage | Fallo de conexión al bucket | Pendiente | - | - |  |
| E2E-01 | Flujo extremo a extremo | Flujo completo con mensaje positivo | Pendiente | - | - |  |
| E2E-02 | Flujo extremo a extremo | Flujo completo con queja | Pendiente | - | - |  |
| E2E-03 | Flujo extremo a extremo | Flujo completo con pregunta frecuente | Pendiente | - | - |  |
| E2E-04 | Flujo extremo a extremo | Flujo completo con n8n apagado | Pendiente | - | - |  |

## Hallazgos vinculados a casos
| ID | Severidad | Caso | Detalle | Seguimiento |
|---|---|---|---|---|
| H-01 | Media | DOC-01 | El volumen externo n8n-hackathon_n8n_data debe crearse a mano antes del primer arranque. Por confirmar si el README lo indica | Por confirmar con el equipo |
| H-02 | Media | N8N-02 | La misma ruta POST se repite en varios workflows (communitylab-ingesta en 3, discord en 2 y slack en 2) y normalmente no pueden estar activos a la vez | Por confirmar con el equipo |
| H-03 | Media | N8N-03 | El webhook devuelve 500 con un mensaje válido en el entorno local. Causa por determinar en Executions | Por investigar |
| H-04 | Baja | DOC-01 | docker-compose.yml línea 42 define NODE_FUNCTION_ALLOW_EXTERNAL=* y permite importar cualquier módulo externo en nodos de código | Por confirmar con el equipo |
| H-05 | Baja | DOC-03 | La imagen de n8n usa la etiqueta latest y la versión puede cambiar entre despliegues | Por confirmar con el equipo |
| H-06 | Baja | INF-06 | n8n se sirve por HTTP sin cifrado | Por confirmar con el equipo |
| H-07 | Baja | N8N-02 | El backlog menciona Gemini y OpenAI pero el repo trae un subflujo de Groq y canales de Discord, Slack y Telegram | Por confirmar con el equipo |
| H-08 | Media | E2E-01 | paquete_procesado.json indica 15 registros de origen, 3 procesados y 0 fallidos. Quedan 12 sin contabilizar | Por confirmar con el equipo |
| H-09 | Media | DB-01 | El compose solo levanta n8n. El backlog menciona PostgreSQL y Streamlit | Por confirmar con el equipo |
| H-10 | Informativo | INF-06 | PostgreSQL (puerto 5432) no es accesible desde internet | Conforme |

## Integridad de evidencias (SHA-256, primeros 12 caracteres)
| Archivo | Hash | Fecha | KB |
|---|---|---|---|
| DOC-01_diagnostico_volumen.txt | C1C5B72C472D | 2026-10-11 20:07 | 0.7 |
| DOC-01_ps.txt | A1A836C8E89A | 2026-10-11 20:34 | 0.6 |
| DOC-01_up.txt | DFF4FC1C98E1 | 2026-10-11 20:34 | 0.1 |
| DOC-01_volumen_creado.txt | 123859220CC2 | 2026-10-11 20:31 | 0 |
| INF-06.txt | 6A87F2E03BC5 | 2026-10-11 19:18 | 0.4 |
| N8N-01.txt | 4225D6901014 | 2026-10-11 20:58 | 0.3 |
| N8N-02.txt | DBBDCB50E5EF | 2026-10-11 21:32 | 2.2 |
| N8N-02_activacion.txt | 3C91E18CD6A4 | 2026-10-11 22:31 | 0.5 |
| N8N-04.csv | A8B235C8002A | 2026-10-11 22:38 | 0.7 |
| N8N-04.txt | 5E9665027ACC | 2026-10-11 22:38 | 1.3 |
| N8N-04_contenedor.txt | 3A9AF6E56C22 | 2026-10-11 22:49 | 6.8 |
| N8N-04_respuesta_control.txt | D5B1062CD7D5 | 2026-10-11 22:58 | 0.5 |
