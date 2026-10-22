# Matriz de trazabilidad - CommunityLab (pruebas funcionales QA)

- Fecha de generación: 2026-10-21 22:14 -03:00
- Commit probado: 798dd2d
- Entorno: local (Windows y Docker Desktop), salvo INF-06 contra el servidor del equipo

## Resumen por estado
| Estado | Casos |
|---|---|
| Pendiente | 20 |
| Parcial | 12 |
| Bloqueado | 12 |
| Pasó | 10 |
| No concluyente | 3 |
| Falló | 1 |
| En curso | 1 |

## Matriz: backlog, caso, evidencia
| ID | Historia del backlog | Prueba | Estado | Evidencias | Última evidencia | Nota |
|---|---|---|---|---|---|---|
| INF-01 | Infraestructura y setup base | Terraform fmt init validate y plan | No concluyente | - | - | validate corrió sin confirmar que existan archivos tf. Plan pendiente |
| INF-02 | Infraestructura y setup base | Aprovisionamiento de la VM | Pendiente | - | - |  |
| INF-03 | Infraestructura y setup base | Acceso SSH | Parcial | INF-03_04_servidor.txt | 2026-10-19 22:35 | Acceso SSH logrado en el servidor. Falta documentar con qué llave y acordar una llave personal de QA autorizada por el equipo |
| INF-04 | Infraestructura y setup base | Recursos y SWAP | Pasó | - | - | Servidor: Ubuntu 22.04, 956 MiB de RAM, SWAP de 6 GiB y disco al 42 por ciento. Coincide con lo documentado. Unos 325 MiB de RAM disponibles |
| INF-05 | Infraestructura y setup base | Seguridad del repositorio (secretos) | Pendiente | INF-05.txt | 2026-10-20 19:38 |  |
| INF-06 | Infraestructura y setup base | Exposición de puertos | Parcial | INF-06.txt | 2026-10-20 21:43 | 22 5678 y 8501 abiertos y 5432 cerrado. Falta verificar login en N8N-01 y UI-07 |
| DOC-01 | Contenedores Docker | Levantar entorno Docker | Parcial | DOC-01_diagnostico_volumen.txt, DOC-01_ps.txt, DOC-01_servidor.txt, DOC-01_sincronizacion_main.txt, DOC-01_up.txt, DOC-01_volumen_creado.txt | 2026-10-20 20:03 | Local: falló por volumen externo inexistente. Servidor: n8n arriba hace 4 semanas y el volumen existe. Falta comparar el contenedor con el compose actual |
| DOC-02 | Contenedores Docker | Logs limpios | Parcial | DOC-02.txt, DOC-02_servidor.txt | 2026-10-19 22:37 | Sin reinicios en bucle. Advertencia al arrancar por el runner de Python. Errores de Groq por fallo de DNS puntual no reproducido |
| DOC-03 | Contenedores Docker | Reproducibilidad desde cero | Pendiente | - | - | El primer intento falló por el volumen externo |
| DOC-04 | Contenedores Docker | Persistencia tras restart | Bloqueado | - | - | Sin servicio de base de datos en el compose actual (por confirmar) |
| DB-01 | PostgreSQL con pgvector | Conexión a PostgreSQL | Bloqueado | - | - | Sin servicio PostgreSQL en el compose actual (por confirmar) |
| DB-02 | PostgreSQL con pgvector | Extensión vector | Bloqueado | - | - | Depende de DB-01 |
| DB-03 | PostgreSQL con pgvector | Esquema | Bloqueado | - | - | Depende de DB-01 |
| DB-04 | PostgreSQL con pgvector | Búsqueda semántica | Bloqueado | - | - | Depende de DB-01 |
| DB-05 | PostgreSQL con pgvector | Datos inválidos | Bloqueado | - | - | Depende de DB-01 |
| N8N-01 | Orquestador n8n | Acceso y autenticación | Pasó | N8N-01.txt | 2026-10-14 20:22 | n8n 2.42.5 local. La API devuelve 401 sin credenciales. Falta captura de la pantalla de login. Servidor del equipo no probado |
| N8N-02 | Orquestador n8n | Workflows importados y activos | En curso | N8N-02.txt, N8N-02_activacion.txt, N8N-02_servidor.txt | 2026-10-19 22:37 | 8 workflows en el repo con rutas de webhook repetidas. Falta confirmar importación y activación |
| N8N-03 | Orquestador n8n | Webhook con mensaje válido | Falló | N8N-03_reintento.txt | 2026-10-18 20:39 | HTTP 500 en entorno local con mensaje de prueba y con lote real. Causa por determinar en Executions |
| N8N-04 | Orquestador n8n | Webhook con entradas inválidas | No concluyente | N8N-04.csv, N8N-04.txt, N8N-04_contenedor.txt, N8N-04_respuesta_control.txt | 2026-10-13 19:48 | El control dio 500. JSON malformado 422 y GET 404 |
| N8N-05 | Orquestador n8n | Entrada y salida por nodo | Pendiente | - | - |  |
| PY-01 | Sistema dual con pipelines Python | Entorno Python | Parcial | - | - | El entorno virtual existente ejecuta el pipeline. Instalación desde cero no probada |
| PY-02 | Sistema dual con pipelines Python | Ejecución aislada | Parcial | - | - | Pipeline ejecutado en local con 18 registros y código de salida 0. Comparación con n8n pendiente |
| PY-03 | Sistema dual con pipelines Python | Paridad n8n vs Python | Bloqueado | - | - | n8n responde 500 y no hay salida que comparar |
| PY-04 | Sistema dual con pipelines Python | Failover real | Pendiente | - | - |  |
| PY-05 | Sistema dual con pipelines Python | Recuperación | Pendiente | - | - |  |
| PY-06 | Sistema dual con pipelines Python | Sobrecarga | Pendiente | PY-06.csv, PY-06.txt, PY-06_stats.txt | 2026-10-13 19:48 |  |
| PY-07 | Sistema dual con pipelines Python | Tests existentes | Parcial | PY-07.txt, PY-07b.txt, PY-07c.txt, PY-07_diagnostico.txt, PY-07_junit.xml, PY-07_main.txt | 2026-10-21 21:28 | 77 passed 2 failed (Selenium) 2 skipped. El README indica 73 al 100 por ciento |
| IA-01 | APIs de IA, prompts e imágenes | Conexión Gemini | Parcial | IA-01_02.txt | 2026-10-13 21:18 | Gemini responde a través del pipeline. Llamada mínima aislada pendiente |
| IA-02 | APIs de IA, prompts e imágenes | Respaldo OpenAI | Parcial | - | - | Cambio automático entre modelos de Gemini observado. Groq u OpenAI por confirmar con el equipo |
| IA-03 | APIs de IA, prompts e imágenes | Análisis de sentimiento | No concluyente | IA-03.txt, IA-03_comparacion.csv, IA-03_log.txt, IA-03_log_aislado.txt, IA-03_log_rerun.txt, IA-03_referencia.csv | 2026-10-20 20:57 | Referencia propia en etiquetado. Actualizar con el porcentaje cuando termine |
| IA-04 | APIs de IA, prompts e imágenes | Voz de marca | Pendiente | IA-04.txt, IA-04_log_a.txt, IA-04_log_b.txt | 2026-10-20 20:57 |  |
| IA-05 | APIs de IA, prompts e imágenes | Respuesta al usuario | Pendiente | - | - |  |
| IA-06 | APIs de IA, prompts e imágenes | Chunking y lematización | Pendiente | - | - |  |
| IA-07 | APIs de IA, prompts e imágenes | Prompt injection | Pasó | - | - | 4 entradas hostiles procesadas sin fuga de instrucciones. La estructura de salida se mantiene |
| IA-08 | APIs de IA, prompts e imágenes | Límites de API | Parcial | IA-08_fallback_modelo.txt | 2026-10-13 22:18 | Cambio automático de modelo ante error 503 observado en el log. Falta probar clave inválida y cuota agotada |
| IA-09 | APIs de IA, prompts e imágenes | Imágenes Pollinations | Pendiente | IA-09_1.jpg, IA-09_2.img, IA-09_3.img | 2026-10-18 21:10 |  |
| LOG-01 | Lógica condicional | Pregunta frecuente a FAQ | Pendiente | - | - |  |
| LOG-02 | Lógica condicional | Elogio genera post | Pendiente | - | - |  |
| LOG-03 | Lógica condicional | Queja grave emite alerta | Pendiente | - | - |  |
| LOG-04 | Lógica condicional | Mensaje ambiguo | Pendiente | - | - |  |
| LOG-05 | Lógica condicional | Mensaje en dos categorías | Pendiente | - | - |  |
| UI-01 | Panel Streamlit | Carga de Streamlit | Pasó | UI-01.png | 2026-10-14 20:31 | Panel cargado en local sobre la version integrada con main. Captura UI-01.png |
| UI-02 | Panel Streamlit | Lista de publicaciones | Pasó | - | - | Panel cargado en local sobre la version integrada con main. Captura en UI-02.png |
| UI-03 | Panel Streamlit | Aprobar rechazar y editar | Pasó | - | - | Panel cargado en local sobre la version integrada con main. Captura en UI-03.png |
| UI-04 | Panel Streamlit | Lista vacía | Pasó | - | - | Panel cargado en local sobre la version integrada con main. Captura en UI-04.png |
| UI-05 | Panel Streamlit | Textos largos y acentos | Pasó | - | - | Panel cargado en local sobre la version integrada con main. Captura en UI-05.png |
| UI-06 | Panel Streamlit | Responsive | Pasó | - | - | Panel cargado en local sobre la version integrada con main. Captura en UI-06.png |
| UI-07 | Panel Streamlit | Acceso sin autenticación | Parcial | UI-07_servidor.txt | 2026-10-19 22:37 | En local entra sin login. Servidor no probado. Hallazgo por confirmar con el equipo |
| OBJ-01 | JSON en OCI Object Storage | JSON en el bucket | Bloqueado | - | - | Sin llave de OCI en el equipo de QA |
| OBJ-02 | JSON en OCI Object Storage | JSON válido | Bloqueado | - | - | Sin llave de OCI en el equipo de QA |
| OBJ-03 | JSON en OCI Object Storage | Nombres sin colisión | Bloqueado | - | - | Sin llave de OCI en el equipo de QA |
| OBJ-04 | JSON en OCI Object Storage | Bucket privado | Bloqueado | - | - | Sin llave de OCI en el equipo de QA |
| OBJ-05 | JSON en OCI Object Storage | Fallo de conexión al bucket | Bloqueado | - | - | Sin llave de OCI en el equipo de QA |
| E2E-01 | Flujo extremo a extremo | Flujo completo con mensaje positivo | Pendiente | - | - | Depende de n8n funcional y de los bloques 5 7 y 8 |
| E2E-02 | Flujo extremo a extremo | Flujo completo con queja | Pendiente | - | - | Depende de n8n funcional y de los bloques 5 7 y 8 |
| E2E-03 | Flujo extremo a extremo | Flujo completo con pregunta frecuente | Pendiente | - | - | Depende de n8n funcional y de los bloques 5 7 y 8 |
| E2E-04 | Flujo extremo a extremo | Flujo completo con n8n apagado | Pendiente | - | - | Depende de PY-04 |
| VAL-01 | Validacion de datos del backend | Validador ante entradas invalidas (12 casos) | Parcial | VAL-01.txt | 2026-10-21 22:13 | Detecta registros sin texto y con tipos incorrectos. Acepta texto en blanco, ids repetidos, tipo desconocido y lista vacia (por confirmar con schemas.py). Falla con BOM y muestra traceback ante archivos rotos |
| VAL-02 | Validacion de datos del backend | CLI del pipeline ante entradas invalidas a nivel de archivo | Pasó | VAL-02.txt | 2026-10-21 22:02 | Con JSON cortado, archivo vacio y ruta inexistente termina con codigo 1, sin traceback, sin llamadas a la IA y sin crear salida |

## Hallazgos vinculados a casos
| ID | Severidad | Caso | Detalle | Seguimiento |
|---|---|---|---|---|
| H-01 | Media | DOC-01 | El volumen externo n8n-hackathon_n8n_data debe crearse a mano antes del primer arranque. Por confirmar si el README lo indica | Por confirmar con el equipo |
| H-02 | Media | N8N-02 | La misma ruta POST se repite en varios workflows del repo (communitylab-ingesta en 3, discord en 2 y slack en 2). En el servidor solo hay 2 workflows activos (Generador_Imagenes_Post) y ese conflicto no se da alli. Por confirmar cual es el conjunto vigente | Por confirmar con el equipo |
| H-03 | Media | N8N-03 | El webhook devuelve 500 en el entorno local. Causa por determinar en Executions | Por investigar |
| H-04 | Baja | DOC-01 | docker-compose.yml define NODE_FUNCTION_ALLOW_EXTERNAL=* y permite importar cualquier módulo externo en nodos de código | Por confirmar con el equipo |
| H-05 | Baja | DOC-03 | La imagen de n8n usa la etiqueta latest y la versión puede cambiar entre despliegues | Por confirmar con el equipo |
| H-06 | Baja | INF-06 | n8n se sirve por HTTP sin cifrado | Por confirmar con el equipo |
| H-07 | Baja | N8N-02 | El backlog menciona Gemini y OpenAI pero el repo trae un subflujo de Groq y el .env usa Groq y no OpenAI | Por confirmar con el equipo |
| H-08 | Media | E2E-01 | paquete_procesado.json del repo indica 15 registros de origen y 3 procesados. En una corrida local el pipeline proceso 18 de 18 sin fallos, lo que sugiere que ese archivo viene de una corrida parcial | Por confirmar con el equipo |
| H-09 | Media | DB-01 | El compose solo levanta n8n. El backlog menciona PostgreSQL y Streamlit | Por confirmar con el equipo |
| H-10 | Informativo | INF-06 | PostgreSQL (puerto 5432) no es accesible desde internet | Conforme |
| H-11 | Baja | PY-07 | El README indica 73 tests aprobados. Tras integrar main, pytest recolecta 86 tests de la suite del equipo, ademas de 4 de archivos agregados por la rama de QA. El README parece desactualizado. Por confirmar | Por confirmar con el equipo |
| H-12 | Media | IA-03 | Una corrida completa del pipeline se detuvo en el registro 15 sin mensaje de error. La repetición terminó bien con 18 de 18. Incidencia no reproducida | Por confirmar con el equipo |
| H-13 | Informativo | IA-08 | El pipeline cambió automáticamente de modelo ante un error 503 de alta demanda y siguió procesando | Conforme |
| H-14 | Media | INF-05 | El .env local trae credenciales reales de IA OCI y un webhook de Discord. Se recomienda un entorno de pruebas aislado | Por confirmar con el equipo |
| H-15 | Baja | DOC-02 | El runner de tareas de Python de n8n no inicia en modo interno porque falta Python 3 en la imagen. n8n recomienda el modo externo en produccion | Por confirmar con el equipo |
| H-16 | Media | N8N-03 | Los logs de n8n registraron ENOTFOUND api.groq.com durante las pruebas. Una comprobacion posterior resolvio el nombre sin problema. Causa del error 500 por determinar | Por investigar |
| H-17 | Baja | DOC-01 | El servidor usa Docker 29.1.3 con docker-compose 1.29.2 (v1 obsoleta) y sin el plugin docker compose. La documentación y el entorno local usan docker compose | Por confirmar con el equipo |
| H-18 | Media | DB-01 | En el servidor no hay PostgreSQL ni puerto 5432. Solo corre n8n en Docker y Streamlit fuera de Docker | Por confirmar con el equipo |
| H-19 | Media | DOC-03 | El contenedor de n8n del servidor se creo el 16 de septiembre y es anterior a cambios posteriores del compose. El servidor corre el commit 829cabc, ya integrado en main. Pruebas locales hechas sobre una version de la rama del QA. Ver DOC-01_sincronizacion_main.txt | Por confirmar con el equipo |
| H-20 | Media | UI-07 | Streamlit corre fuera de Docker y escucha en todas las interfaces del puerto 8501 desde un proceso iniciado el 17 de octubre. Por confirmar si exige login y si se reinicia solo | Por confirmar con el equipo |
| H-21 | Media | N8N-02 | El n8n del servidor tiene 27 workflows cargados y solo 2 activos. Hay duplicados por nombre (4 copias de jmedinag_WF_002 y 3 de CCely_WF_003) y copias personales de prueba. Los workflows de ingesta y el master estan cargados pero inactivos, por lo que el webhook de ingesta no responderia alli | Por confirmar con el equipo |
| H-22 | Baja | N8N-02 | Hay dos workflows activos con el mismo nombre (Generador_Imagenes_Post) en el servidor. Por confirmar si usan rutas distintas o si una es una version anterior. El workflow CommunityLab_Slack_Dinamico del repo no aparece en el servidor | Por confirmar con el equipo |
| H-23 "Baja" "INF-05" "La IP del servidor, el usuario y el directorio del proyecto figuran en archivos versionados de main (.env.example y PM_Files). Ya que el repositorio es publico, conviene sacarlos de la documentacion" "Por confirmar con el equipo" |  |  |  |  |
| H-24 | Media | UI-07 | El panel Streamlit abre sin pedir autenticacion en el entorno local y escucha en todas las interfaces. Por confirmar si tendra login en el entorno desplegado | Por confirmar con el equipo |
| H-2306 | Baja | VAL-01 | El validador falla con JSONDecodeError en un JSON guardado con BOM UTF-8, que es el formato por defecto al guardar con PowerShell 5.1 o con el Bloc de notas clasico. El archivo debe abrirse con utf-8-sig. Por confirmar si el pipeline tambien falla | Por confirmar con el equipo |
| H-2307 | Baja | VAL-01 | El validador muestra un traceback completo ante JSON malformado, archivo vacio o ruta inexistente, mientras el CLI del pipeline termina con un error limpio en los mismos casos | Por confirmar con el equipo |
| H-2308 | Media | VAL-01 | El validador acepta un texto de solo espacios, ids repetidos, un tipo desconocido y una lista vacia (con exito y 0 registros validados). Por confirmar con schemas.py si es diseno intencional. Un texto en blanco llegaria a la IA y consumiria cuota | Por confirmar con el equipo |
| H-2309 | Informativo | VAL-02 | El CLI del pipeline rechaza archivos rotos con codigo 1, sin traceback, sin llamadas a la IA y sin crear archivo de salida | Conforme |

## Integridad de evidencias (SHA-256, primeros 12 caracteres)
| Archivo | Hash | Fecha | KB |
|---|---|---|---|
| DOC-01_diagnostico_volumen.txt | C1C5B72C472D | 2026-10-13 19:48 | 0.7 |
| DOC-01_ps.txt | A1A836C8E89A | 2026-10-13 19:48 | 0.6 |
| DOC-01_servidor.txt | 0477E001AEBC | 2026-10-19 22:37 | 0.7 |
| DOC-01_sincronizacion_main.txt | 07683D609FBD | 2026-10-20 20:03 | 1.3 |
| DOC-01_up.txt | DFF4FC1C98E1 | 2026-10-13 19:48 | 0.1 |
| DOC-01_volumen_creado.txt | 123859220CC2 | 2026-10-13 19:48 | 0 |
| DOC-02.txt | 873B2AAD3BB0 | 2026-10-14 20:19 | 2.4 |
| DOC-02_servidor.txt | 5E8FDC3C4B48 | 2026-10-19 22:37 | 0.9 |
| INF-03_04_servidor.txt | 6EE995F5D094 | 2026-10-19 22:35 | 2.5 |
| INF-05.txt | 894481290CA1 | 2026-10-20 19:38 | 0.9 |
| INF-06.txt | 11619510D0EF | 2026-10-20 21:43 | 0.4 |
| N8N-01.txt | 286894CB1EB7 | 2026-10-14 20:22 | 0.5 |
| N8N-02.txt | 3B1056CA8AA4 | 2026-10-13 19:48 | 2.2 |
| N8N-02_activacion.txt | 603198B52873 | 2026-10-13 19:48 | 0.6 |
| N8N-02_servidor.txt | DE3C0C8F5158 | 2026-10-19 22:37 | 1.3 |
| N8N-03_reintento.txt | E459DA926289 | 2026-10-18 20:39 | 0.2 |
| N8N-04.csv | A8B235C8002A | 2026-10-13 19:48 | 0.7 |
| N8N-04.txt | 5E9665027ACC | 2026-10-13 19:48 | 1.3 |
| N8N-04_contenedor.txt | 09EA5BE42EFE | 2026-10-13 19:48 | 6.9 |
| N8N-04_respuesta_control.txt | 96B64309FFB2 | 2026-10-13 19:48 | 0.5 |
| PY-06.csv | 85F21A1AD1B1 | 2026-10-13 19:48 | 0.6 |
| PY-06.txt | 0F642DA3482D | 2026-10-13 19:48 | 1.2 |
| PY-06_stats.txt | 39F593AB753F | 2026-10-13 19:48 | 5.7 |
| PY-07.txt | 0FD5B72462DD | 2026-10-20 20:57 | 23.5 |
| PY-07b.txt | CD7E0906E625 | 2026-10-20 21:45 | 7.7 |
| PY-07c.txt | 497CE0F92E6D | 2026-10-21 21:28 | 7.7 |
| PY-07_diagnostico.txt | E6D0D1397481 | 2026-10-13 19:48 | 1.5 |
| PY-07_junit.xml | 4B9017219834 | 2026-10-13 19:48 | 25.6 |
| PY-07_main.txt | 9C9ACE59BCB5 | 2026-10-20 21:17 | 1.2 |
| UI-01.png | 055334591FA8 | 2026-10-14 20:31 | 186.6 |
| UI-07_servidor.txt | C7EF5155BF43 | 2026-10-19 22:37 | 0.3 |
| IA\entrada_IA03.json | 9B0AA35BBE0A | 2026-10-13 22:01 | 8.9 |
| IA\entrada_IA03_aislado.json | 6A3968FFEDF1 | 2026-10-13 22:07 | 1.7 |
| IA\entrada_IA04.json | 89621A50B80B | 2026-10-14 19:34 | 2.4 |
| IA\entrada_IA06.json | 5896444880AE | 2026-10-18 21:06 | 35.5 |
| IA\entrada_IA07.json | 23C289C61E1D | 2026-10-18 21:08 | 1.7 |
| IA\IA-01_02.txt | ED8710229D28 | 2026-10-13 21:18 | 0.2 |
| IA\IA-03.txt | C5DDBA1ACA4C | 2026-10-14 19:15 | 1.3 |
| IA\IA-03_comparacion.csv | B079FA9A625D | 2026-10-14 19:15 | 1 |
| IA\IA-03_log.txt | B5B8517BB2F2 | 2026-10-13 21:43 | 10.2 |
| IA\IA-03_log_aislado.txt | 895F8D8E5A8F | 2026-10-20 20:57 | 3.7 |
| IA\IA-03_log_rerun.txt | CC8773151328 | 2026-10-20 20:57 | 12.8 |
| IA\IA-03_referencia.csv | 011D6205EB87 | 2026-10-14 19:15 | 3.8 |
| IA\IA-04.txt | E5BE60C15AB3 | 2026-10-14 19:52 | 2.5 |
| IA\IA-04_log_a.txt | 8A474D81305F | 2026-10-20 20:57 | 4.6 |
| IA\IA-04_log_b.txt | 07BE36362480 | 2026-10-20 20:57 | 4.7 |
| IA\IA-08_fallback_modelo.txt | 67FF8E202E31 | 2026-10-13 22:18 | 2.9 |
| IA\IA-09_1.jpg | 8B025928C37D | 2026-10-18 21:10 | 58.6 |
| IA\IA-09_2.img | CDFEB6030F49 | 2026-10-18 21:10 | 0.3 |
| IA\IA-09_3.img | 6DADE2E64B79 | 2026-10-18 21:10 | 0.3 |
| IA\IA06_log.txt | 94A7AFD494FF | 2026-10-20 20:57 | 2 |
| IA\IA07_log.txt | 3C8695D3B63B | 2026-10-20 20:57 | 3.7 |
| IA\salida_IA03.json | 16CB8B4BB6A8 | 2026-10-13 22:14 | 35.6 |
| IA\salida_IA03_aislado.json | 91FE5A8C26B3 | 2026-10-13 22:07 | 8.5 |
| IA\salida_IA04_a.json | DE8FC98F98D7 | 2026-10-14 19:34 | 8.5 |
| IA\salida_IA04_b.json | 5A0F1643EC34 | 2026-10-14 19:35 | 8.7 |
| IA\salida_IA06.json | F809E15BB49C | 2026-10-18 21:06 | 36.7 |
| IA\salida_IA07.json | 1023BC171EFE | 2026-10-18 21:08 | 5.2 |
| PY-03\entrada_5.json | 8BAF97B8C8D8 | 2026-10-13 20:41 | 2.8 |
| VAL\pipeline_VAL_02_json_malformado.log | E421C8A38A34 | 2026-10-21 22:02 | 0.3 |
| VAL\pipeline_VAL_03_vacio.log | 297927993904 | 2026-10-21 22:02 | 0.3 |
| VAL\pipeline_VAL_99_no_existe.log | E5C3659E8619 | 2026-10-21 22:13 | 0.4 |
| VAL\salida_VAL_01_valido.txt | 2FFE82A2BEEB | 2026-10-21 22:13 | 0.4 |
| VAL\salida_VAL_02_json_malformado.txt | 9AECF80A3C80 | 2026-10-21 22:13 | 1.7 |
| VAL\salida_VAL_03_vacio.txt | 246EDF1CE91A | 2026-10-21 22:13 | 1.7 |
| VAL\salida_VAL_04_sin_texto.txt | 6E62380D0899 | 2026-10-21 22:13 | 0.4 |
| VAL\salida_VAL_05_tipos_incorrectos.txt | BCC9A4B75FBE | 2026-10-21 22:13 | 0.4 |
| VAL\salida_VAL_06_lista_vacia.txt | 09E492934D55 | 2026-10-21 22:13 | 0.4 |
| VAL\salida_VAL_07_ids_duplicados.txt | 37577912C6B8 | 2026-10-21 22:13 | 0.4 |
| VAL\salida_VAL_08_texto_en_blanco.txt | 6C14C9DCE6F0 | 2026-10-21 22:13 | 0.4 |
| VAL\salida_VAL_09_tipo_invalido.txt | 8766922EB7E0 | 2026-10-21 22:13 | 0.4 |
| VAL\salida_VAL_10_texto_largo.txt | 52149900578B | 2026-10-21 22:13 | 0.4 |
| VAL\salida_VAL_11_unicode.txt | F09B23F96648 | 2026-10-21 22:13 | 0.4 |
| VAL\salida_VAL_12_con_BOM.txt | 20AC942CE9AD | 2026-10-21 22:13 | 1.4 |
| VAL\salida_VAL_99_no_existe.txt | 997C589C5846 | 2026-10-21 22:13 | 1.1 |
| VAL\VAL-01.txt | D692A99F6A6B | 2026-10-21 22:13 | 2.2 |
| VAL\VAL-02.txt | FBE5F8871DD9 | 2026-10-21 22:02 | 0.5 |
| VAL\entradas\VAL_01_valido.json | 9327BBCDA168 | 2026-10-21 21:58 | 1.7 |
| VAL\entradas\VAL_02_json_malformado.json | 63EADBE411E5 | 2026-10-21 21:58 | 0.1 |
| VAL\entradas\VAL_03_vacio.json | E3B0C44298FC | 2026-10-21 21:58 | 0 |
| VAL\entradas\VAL_04_sin_texto.json | FC18A372DF04 | 2026-10-21 21:58 | 1.4 |
| VAL\entradas\VAL_05_tipos_incorrectos.json | 9C13676AF147 | 2026-10-21 21:58 | 1.6 |
| VAL\entradas\VAL_06_lista_vacia.json | 37E187832275 | 2026-10-21 21:58 | 0.2 |
| VAL\entradas\VAL_07_ids_duplicados.json | C5C14F80B23E | 2026-10-21 21:58 | 1.7 |
| VAL\entradas\VAL_08_texto_en_blanco.json | 9ACBA2F415CB | 2026-10-21 21:58 | 1.5 |
| VAL\entradas\VAL_09_tipo_invalido.json | 231613F0A38D | 2026-10-21 21:58 | 1.7 |
| VAL\entradas\VAL_10_texto_largo.json | 64EBE689314D | 2026-10-21 21:58 | 11.3 |
| VAL\entradas\VAL_11_unicode.json | F4D3D87B64DC | 2026-10-21 21:58 | 1.5 |
| VAL\entradas\VAL_12_con_BOM.json | 15EB6ABDDD61 | 2026-10-21 21:58 | 1.7 |

Archivos de apoyo sin caso propio (entradas, salidas y logs): 42
