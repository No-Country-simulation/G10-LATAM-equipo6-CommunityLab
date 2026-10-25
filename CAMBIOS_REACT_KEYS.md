# Documentación de Cambios para Solución de Error NotFoundError: removeChild

## Resumen Ejecutivo
Se añaden atributos key únicos a elementos HTML dinámicos inyectados con unsafe_allow_html=True. Esto permite que React (motor interno de Streamlit) rastree correctamente la identidad de elementos durante los re-renders, evitando errores removeChild cuando la estructura DOM cambia entre renders consecutivos.

## Contexto del Error
El error NotFoundError: Error al ejecutar removeChild en Node: El nodo que se va a eliminar no es un hijo de este nodo es un error de React DOM que ocurre cuando React intenta remover un nodo del DOM que, según su árbol virtual, ya no es hijo directo del nodo padre actual.

**Stack trace típico (del reporte del usuario):**

NotFoundError: Error al ejecutar removeChild en Node: El nodo que se va a eliminar no es un hijo de este nodo.
at Fc (http://localhost:8501/static/js/react-dom.CbzydqoA.js:8:25826)
at Lc (http://localhost:8501/static/js/react-dom.CbzydqoA.js:8:27100)
...
Estado de Canales:
🎮 Discord: Verificado en OCI
💬 Slack: Verificado en OCI
✈️ Telegram: Verific...


## Causa Raíz Técnica Profunda

### ¿Por qué Streamlit + React falla con HTML inyectado?
1. Streamlit usa React internamente para renderizar su interfaz
2. Tu código usa unsafe_allow_html=True para inyectar HTML personalizado (st.markdown(..., unsafe_allow_html=True) o la función H() de utils.py)
3. React mantiene un Virtual DOM - representación en memoria de cómo debería verse el DOM
4. Al re-renderizar (cambio de filtro, vista, toggle de tema, actualización de bots), React compara el Virtual DOM anterior vs nuevo, calcula diferencias mínimas (diffing) y aplica solo los cambios necesarios al DOM real.

### El Problema: Sin key, React no puede identificar elementos
Cuando renderizas elementos HTML sin atributo key, React usa el índice del array como identificador implícito:

// Render 1 - 3 posts           Render 2 - filtro cambió, solo 2 posts
┌────────────────────┐            ┌─────────────────────┐
│div class=pcard     │ idx 0  →   │div class=pcard      │ idx 0 → React piensa: 
│  Post A           │            │  Post A            │  índice 0 = Post A ✓
│div class=pcard     │ idx 1  →   │div class=pcard      │ idx 1 → React piensa:
│  Post B ← BORRAR  │            │  Post C            │  índice 1 = Post B ❌ ERROR
│div class=pcard     │ idx 2  →   │(Post B desapareció)│  → Intenta remover Post B
│  Post C           │            │                     │  pero donde está? 
└────────────────────┘            └─────────────────────┘  → removeChild falla

### Con key único, React rastrea identidad real:
// Con keys - React identifica POR CONTENIDO no por posición
┌────────────────────────────────┐     ┌────────────────────────────────┐
│div class=pcard key=post_1      │     │div class=pcard key=post_1      │
│  Post A                       │  →  │  Post A                       │
│div class=pcard key=post_2      │     │(Post B filtrado: key gone)    │
│  Post B                       │  →  │                               │
│div class=pcard key=post_3      │     │div class=pcard key=post_3      │
│  Post C                       │     │  Post C                       │
└────────────────────────────────┘     └────────────────────────────────┘
