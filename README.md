# Eisenhower 5 + IA — Matriz editable

App de Streamlit para convertir una lista de texto en tareas, etiquetarlas una por una y visualizar las 5 zonas en un solo tablero.

## Cómo funciona

1. **Pega todo el texto** en la caja principal; soporta viñetas, números, saltos de línea y varios enunciados.
2. Pulsa **Separar texto en tareas**. La extracción inicial se hace mediante reglas locales, sin API ni pago.
3. **Etiqueta cada tarea** en `Do Now`, `Schedule`, `Delegate to Human`, `Delegate to AI` o `Eliminate`. La nota es opcional.
4. La **matriz se actualiza en tiempo real** al cambiar las etiquetas.
5. Si una tarea agrupa varias acciones, usa **Dividir esta tarea en subtareas**. Hay propuesta automática para listas claras del tipo `Flujo: pagos, recordatorios y seguimiento`; también puedes escribir las subtareas manualmente.

La app empieza sin tareas; el botón **Usar mis tareas del ejemplo** pega la lista original para probarla.

## Proyecto

```text
app.py
requirements.txt
task_parser.py
.streamlit/config.toml
README.md
```

## Ejecución local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Actualizar tu app de Streamlit Cloud

En tu repositorio `eisenhower-5-ai`, **reemplaza `app.py`** y **sube `task_parser.py`** junto a él. Actualiza `requirements.txt` si quieres. Conserva el despliegue apuntando a `app.py`, rama `main`.

Streamlit Cloud desplegará los cambios del repositorio automáticamente. Si hay problemas de caché, usa `Manage app` → `Reboot app` y actualiza la página.

## Guardado de datos

La app usa `st.session_state`: **no guarda automáticamente los cambios entre sesiones, dispositivos o reinicios**. Antes de cerrar, usa **Descargar tareas.json**. Al regresar, abre el archivo descargado, copia su contenido y pégalo en **Recuperar tareas desde JSON** en la barra lateral. Esta alternativa evita el error de carga de archivos del navegador. Un equipo multiusuario necesita una base de datos externa para compartir y persistir tareas.

## Nota sobre la IA

`Delegate to AI` es **una etiqueta organizativa**, no una conexión real a ChatGPT ni una automatización activa. El desglose automático disponible usa reglas simples y puede requerir correcciones, especialmente si pegas un párrafo largo sin viñetas.

## Privacidad y seguridad

Los textos escritos se renderizan en la matriz con escape de HTML. Evita cargar claves de acceso, información de pago o datos personales sensibles en una app pública. El JSON exportado contendrá tus textos.
