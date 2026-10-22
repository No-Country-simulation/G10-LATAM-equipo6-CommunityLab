# Pruebas pendientes y bloqueos - CommunityLab (QA funcional)

- **Fecha:** 2026-10-12
- **Commit probado:** 36f8ca8
- **Autor:** Raúl Gallardo (QA funcional)
- **Detalle de lo ejecutado:** ver `trazabilidad.md` y la carpeta `evidencias/`

## 1. Resumen

Se ejecutaron las pruebas de infraestructura, Docker, n8n y tests existentes en Python (ver matriz). Los bloques de abajo **no se han podido probar todavía**. En cada uno se indica por qué y qué se necesita para completarlo. No son fallos del proyecto: son pruebas **no ejecutadas**.

## 2. Pendientes por bloque

| Bloque | Estado | Qué se necesita para probarlo | Prioridad |
|---|---|---|---|---|
| 5 - IA (Gemini, OpenAI, prompts, imágenes) | Bloqueado | Clave de API de prueba y límites de cuota; guía de marca para evaluar el tono; criterio de aceptación del sentimiento | Alta |
| 6 - Lógica condicional (post, FAQ, alerta) | Por confirmar | Confirmar si ya está implementada y dónde (el backlog la marca como pendiente) | Media |
| 7 - Streamlit, panel de curaduría | Por confirmar | Cómo levantar la app en local y con qué datos de ejemplo | Alta |
| 8 - OCI Object Storage (JSON aprobados) | Bloqueado | Acceso de prueba al bucket (solo lectura o un bucket de pruebas) | Media |
| 9 - Prueba end-to-end | Bloqueado | Los bloques 5, 7 y 8 operativos y un n8n que responda con éxito | Alta |

## 3. Preguntas para el equipo

**IA (bloque 5)**
1. ¿Qué proveedor es el vigente: Gemini, OpenAI o Groq? El backlog y el repositorio no coinciden.
2. ¿Hay una clave de pruebas con cuota limitada que pueda usar sin exponerla en las evidencias?
3. ¿Cuál es el criterio de aceptación del análisis de sentimiento (por ejemplo, un porcentaje mínimo de aciertos)?
4. ¿Existe una guía de la "voz de marca" para evaluar el tono de los posts?
5. ¿Cuál es el criterio de paridad aceptado entre n8n y Python (misma estructura, misma clasificación)?

**Lógica condicional (bloque 6)**
6. ¿La decisión entre crear un post, actualizar una FAQ o emitir una alerta ya está implementada? ¿En qué archivo o workflow?
7. ¿Qué debe pasar con un mensaje ambiguo o que encaja en dos categorías?

**Streamlit (bloque 7)**
8. ¿Cómo se levanta el panel en local y qué datos usa?
9. ¿El panel tendrá autenticación? Hoy no consta en lo que revisé.
10. Los 2 tests de Selenium (`test_ui_streamlit.py`) fallan en mi equipo: ¿necesitan la app en marcha o un navegador específico?

**OCI Object Storage (bloque 8)**
11. No alcance a ingresar al bucket.
12. ¿Cuál es el formato y la nomenclatura esperada de los JSON aprobados?

**General**
13. ¿Qué compose está vigente? El archivo que revisé solo levanta n8n; el backlog menciona PostgreSQL.
14. ¿Qué workflows de n8n deben estar activos? Varios comparten la misma ruta de webhook.
15. ¿Cuál es el criterio que activa el cambio automático a Python (fallback)?

## 4. Hallazgos ya identificados (por confirmar con el equipo)

Ver el detalle y las evidencias en `trazabilidad.md`. Resumen: volumen externo de n8n que debe crearse a mano, rutas de webhook duplicadas entre workflows, 2 de 81 tests fallando en mi entorno, y desajustes entre el backlog y lo implementado.

## 5. Propuesta de siguientes pasos

1. En próximas reuniones afinar detalles.
2. QA - repetir las pruebas bloqueadas y actualiza la matriz de trazabilidad.
