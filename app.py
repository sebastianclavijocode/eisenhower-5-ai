"""Eisenhower + IA: pegar → desglosar → etiquetar → ver matriz (5 zonas)."""
from __future__ import annotations

import html
import json

import streamlit as st

from task_parser import ZONES, extract_tasks, new_task, normalize_import, proposed_subtasks

st.set_page_config(
    page_title="Eisenhower 5 + IA | Matriz editable",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

SAMPLE = """Automatizaciones e inteligencia artificial
Schedule
- Corregir el formato de los números telefónicos para que las llamadas automatizadas lleguen correctamente.
- Ajustar los flujos del webinar: enlaces de pago después de la grabación, recordatorios 10 minutos antes y mensajes de seguimiento.
- Programar la sección de rutas de carreras y el carrusel dinámico.

Do Now
- Generar el reporte financiero mensual con videos ganadores, fuentes de matrículas y presupuesto publicitario.
- Crear y configurar en Stripe el enlace de pago de $500 MXN para la evaluación.
- Actualizar el presupuesto de remarketing y estimar las metas de alcance y gasto.
- Cambiar a amarillo los botones de la página de aterrizaje.
- Realizar pruebas de validación de videos y landing page.

No importante
- Adquirir y configurar técnicamente la cuenta de Zoom, coordinando la compra con Miriam.
- Indicar a Diana que organice los videos por mes, promoción y carrera.
- Localizar el video anterior de maestros y evaluar su reutilización."""

META = {
    "Do Now": ("⚡", "Urgente + importante", "now"),
    "Schedule": ("📅", "Importante + no urgente", "schedule"),
    "Delegate to Human": ("👥", "Delegar a una persona", "human"),
    "Delegate to AI": ("🤖", "Delegar tareas aptas para IA", "ai"),
    "Eliminate": ("🗑️", "Reducir o descartar", "eliminate"),
}

if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "paste_text" not in st.session_state:
    st.session_state.paste_text = ""


def find_task(task_id: str) -> dict | None:
    return next((item for item in st.session_state.tasks if item["id"] == task_id), None)


def update_field(task_id: str, field: str, widget_key: str) -> None:
    item = find_task(task_id)
    if item is not None:
        item[field] = st.session_state[widget_key]


def use_example() -> None:
    st.session_state.paste_text = SAMPLE


def sync_focus() -> None:
    st.session_state.focus_target = st.session_state.focus_select


def short(text: str, limit: int = 74) -> str:
    return text if len(text) <= limit else text[:limit - 1] + "…"


def matrix_markup(tasks: list[dict]) -> str:
    css = """
    <style>
      .eai-board{background:#303b60;border-radius:22px;padding:25px 23px 26px;color:#fff;font-family:Inter,ui-sans-serif,Arial,sans-serif;box-shadow:0 12px 35px #0b122840}
      .eai-heading{text-align:center;font-size:27px;font-weight:800;margin:0 0 5px}
      .eai-subheading{text-align:center;color:#d8e0f3;font-size:13px;margin:0 0 22px}
      .eai-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:14px}
      .eai-zone{grid-column:span 3;min-width:0;background:#ffffff0c;border:1px solid #ffffff22;border-radius:17px;padding:15px 14px;min-height:294px}
      .eai-zone.bottom{grid-column:span 2;min-height:274px}
      .eai-zhead{text-align:center;font-size:16px;font-weight:800;margin-bottom:4px;letter-spacing:.1px}
      .eai-caption{text-align:center;color:#dee5fa;font-size:11px;min-height:18px;margin-bottom:12px}
      .eai-count{background:#ffffff2b;border-radius:20px;padding:2px 8px;margin-left:5px;font-size:11px;white-space:nowrap}
      .eai-cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:11px;max-height:262px;overflow-y:auto;scrollbar-width:thin;padding:2px 2px 5px}
      .eai-zone.bottom .eai-cards{grid-template-columns:1fr;max-height:249px}
      .eai-card{border-radius:12px;color:#1b2434;padding:12px 12px 10px;min-height:76px;box-shadow:0 5px 12px #09132328;font-size:12px;line-height:1.4;overflow-wrap:anywhere}
      .eai-card-title{font-weight:700}
      .eai-note{margin-top:8px;padding-top:7px;border-top:1px solid #0002;font-size:11px}
      .now .eai-card{background:#f4b7b9}.schedule .eai-card{background:#bfe8f7}.human .eai-card{background:#ffe99a}.ai .eai-card{background:#d8caff}.eliminate .eai-card{background:#ececec}
      .eai-empty{border:1px dashed #ffffff5a;border-radius:12px;padding:20px;color:#dce3f5;text-align:center;font-size:12px}
      .eai-footer{font-size:11px;color:#e1e6f5b8;margin-top:13px;text-align:center}
      @media(max-width:900px){.eai-zone{grid-column:span 6}.eai-zone.bottom{grid-column:span 6}.eai-grid{gap:12px}.eai-board{padding:16px}.eai-cards,.eai-zone.bottom .eai-cards{grid-template-columns:repeat(2,minmax(0,1fr));max-height:220px}}
      @media(max-width:520px){.eai-cards,.eai-zone.bottom .eai-cards{grid-template-columns:1fr}}
    </style>
    """
    html_parts = [
        css,
        '<section class="eai-board">',
        '<div class="eai-heading">Matriz Eisenhower + IA</div>',
        '<div class="eai-subheading">Cinco zonas, todas visibles en un solo tablero · Clasificación personalizada</div>',
        '<div class="eai-grid">',
    ]
    for key, (icon, desc, class_name) in META.items():
        elements = [task for task in tasks if task["zone"] == key]
        bottom_class = " bottom" if key not in ("Do Now", "Schedule") else ""
        html_parts.append(f'<section class="eai-zone {class_name}{bottom_class}">')
        html_parts.append(f'<div class="eai-zhead">{icon} {html.escape(key.upper())} <span class="eai-count">{len(elements)}</span></div>')
        html_parts.append(f'<div class="eai-caption">{html.escape(desc)}</div><div class="eai-cards">')
        if not elements:
            html_parts.append('<div class="eai-empty">Sin tareas asignadas</div>')
        for task in elements:
            title = html.escape(task["text"])
            note = html.escape(task.get("notes", ""))
            html_parts.append('<div class="eai-card">')
            html_parts.append(f'<div class="eai-card-title">{title}</div>')
            if note:
                html_parts.append(f'<div class="eai-note">📝 {note}</div>')
            html_parts.append('</div>')
        html_parts.append('</div></section>')
    html_parts.extend([
        '</div>',
        '<div class="eai-footer">Las notas son opcionales. “Delegate to AI” indica a quién asignar la tarea, no que ya esté automatizada.</div>',
        '</section>',
    ])
    return "".join(html_parts)


# --------- Cabecera ---------
st.title("🧠 Automatizaciones e Inteligencia Artificial")
st.caption("Flujo: **1. Pegar tareas → 2. Separar → 3. Etiquetar una por una → 4. Matriz de cinco zonas en vivo.**")

with st.sidebar:
    st.header("📁 Guardar y recuperar")
    st.caption("Esta versión guarda cambios durante la sesión. Para conservarlos entre visitas, exporta JSON.")
    export = json.dumps(st.session_state.tasks, ensure_ascii=False, indent=2)
    st.download_button(
        "⬇️ Descargar tareas.json",
        export,
        file_name="tareas_eisenhower_ia.json",
        mime="application/json",
        use_container_width=True,
    )
    with st.expander("📥 Recuperar tareas desde JSON"):
        st.caption("Abre el JSON que descargaste, copia su contenido y pégalo aquí. Se evita la carga de archivos que fallaba en tu navegador.")
        pasted_json = st.text_area("Contenido del archivo JSON", height=110, key="import_json_text")
        if st.button("Restaurar tareas del JSON", disabled=not pasted_json.strip(), use_container_width=True):
            try:
                imported = normalize_import(json.loads(pasted_json))
                st.session_state.tasks = imported
                st.session_state.pop("focus_target", None)
                st.success(f"Se importaron {len(imported)} tareas.")
                st.rerun()
            except (ValueError, json.JSONDecodeError) as exc:
                st.error(f"No se pudo importar el JSON: {exc}")
    st.divider()
    st.info("**¿Qué significa cada etiqueta?**\n\n" 
            "**Do Now:** resolver tú ahora.\n\n"
            "**Schedule:** poner fecha.\n\n"
            "**Delegate to Human:** asignar a otra persona.\n\n"
            "**Delegate to AI:** pasar a una automatización o herramienta de IA.\n\n"
            "**Eliminate:** evitar lo que no aporta valor.")

# --------- Paso 1 ---------
st.subheader("1 · Pega la lista completa")
st.write("Pega un párrafo, varias líneas o una lista con viñetas. No hace falta que clasifiques nada todavía.")
st.text_area(
    "Todas tus tareas",
    key="paste_text",
    height=180,
    placeholder="Ejemplo:\n- Crear enlace de pago\n- Corregir números telefónicos\n- Ajustar los flujos del webinar: enlace de pago, recordatorios y seguimiento",
    label_visibility="collapsed",
)
with st.expander("⚙️ Opciones al separar el texto", expanded=False):
    expand_lists = st.checkbox(
        "Separar enumeraciones después de dos puntos en subtareas",
        help="Por ejemplo, 'Webinar: enlace de pago, recordatorios y seguimiento' se convierte en tres tareas editables. No utiliza IA externa.",
    )
    paste_mode = st.radio("Al procesar", ["Reemplazar tareas actuales", "Agregar a las existentes"], horizontal=True)

btn1, btn2 = st.columns([1, 1])
if btn1.button("✂️ Separar texto en tareas", type="primary", use_container_width=True):
    extracted = extract_tasks(st.session_state.paste_text, expand_lists=expand_lists)
    if not extracted:
        st.warning("Pega al menos una tarea para comenzar.")
    else:
        prepared = [new_task(t) for t in extracted]
        if paste_mode.startswith("Reemplazar"):
            st.session_state.tasks = prepared
        else:
            st.session_state.tasks.extend(prepared)
        st.session_state.pop("focus_target", None)
        st.toast(f"Se detectaron {len(prepared)} tareas. Ahora puedes etiquetarlas.")
        st.rerun()
btn2.button("📋 Usar mis tareas del ejemplo", use_container_width=True, on_click=use_example)

st.divider()

# --------- Paso 2 ---------
st.subheader("2 · Revisa y etiqueta cada tarea")
total = len(st.session_state.tasks)
classified = sum(item["zone"] != "Sin clasificar" for item in st.session_state.tasks)
a, b, c = st.columns(3)
a.metric("Tareas detectadas", total)
b.metric("Clasificadas", classified)
c.metric("Pendientes de etiqueta", total - classified)
if total:
    st.progress(classified / total)

if not total:
    st.info("Tu lista todavía está vacía. Pega tareas arriba y pulsa **Separar texto en tareas**.")
else:
    show_filter = st.radio("Mostrar", ["Sin clasificar", "Todas las tareas"], horizontal=True)
    visible = [task for task in st.session_state.tasks if task["zone"] == "Sin clasificar"] if show_filter == "Sin clasificar" else st.session_state.tasks

    if not visible:
        st.success("🎉 Todas las tareas tienen una zona. Usa 'Todas las tareas' para revisarlas o editarlas.")
    else:
        ids = [task["id"] for task in visible]
        if st.session_state.get("focus_target") not in ids:
            st.session_state.focus_target = ids[0]
        # Se sincroniza antes de crear el widget: evita modificar su estado después de instanciarlo.
        st.session_state.focus_select = st.session_state.focus_target
        selected_id = st.selectbox(
            "Selecciona la tarea que vas a etiquetar",
            ids,
            format_func=lambda task_id: f"{ids.index(task_id) + 1}/{len(ids)} · {short(find_task(task_id)['text'])}",
            key="focus_select",
            on_change=sync_focus,
        )
        item = find_task(selected_id)
        pos = ids.index(selected_id)
        st.caption(f"Tarea {pos + 1} de {len(ids)} en esta vista · Los cambios se guardan al editar y la matriz se actualiza en cada cambio.")

        edit_key = f"edit_{selected_id}"
        zone_key = f"zone_{selected_id}"
        note_key = f"note_{selected_id}"
        if edit_key not in st.session_state:
            st.session_state[edit_key] = item["text"]
        if zone_key not in st.session_state:
            st.session_state[zone_key] = item["zone"]
        if note_key not in st.session_state:
            st.session_state[note_key] = item["notes"]

        st.text_area("Descripción (editable)", key=edit_key, height=100,
                     on_change=update_field, args=(selected_id, "text", edit_key))
        st.selectbox("🏷️ Etiqueta / zona", ZONES, key=zone_key,
                     on_change=update_field, args=(selected_id, "zone", zone_key),
                     help="Selecciona una de las cinco zonas; también puedes dejarla Sin clasificar.")
        st.text_input("📝 Nota opcional (¿quién lo hace, cómo o por qué?)", key=note_key,
                      on_change=update_field, args=(selected_id, "notes", note_key),
                      placeholder="Ejemplo: Diana lo organiza; revisar resultado el viernes")

        nav1, nav2, nav3 = st.columns([1, 1, 1])
        if nav1.button("⬅️ Anterior", disabled=pos == 0, use_container_width=True):
            st.session_state.focus_target = ids[pos - 1]
            st.rerun()
        if nav2.button("Siguiente ➡️", disabled=pos == len(ids) - 1, use_container_width=True):
            st.session_state.focus_target = ids[pos + 1]
            st.rerun()
        if nav3.button("🗑️ Quitar tarea", use_container_width=True):
            st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != selected_id]
            st.session_state.pop("focus_target", None)
            st.rerun()

        with st.expander("🧩 Dividir esta tarea en subtareas", expanded=False):
            st.caption("Escribe una subtarea por línea. Puedes usar la propuesta como punto de partida y corregirla.")
            split_key = f"splits_{selected_id}"
            if split_key not in st.session_state:
                st.session_state[split_key] = ""
            suggestion = proposed_subtasks(item["text"])
            if st.button("✨ Proponer subtareas desde una enumeración", key=f"suggest_{selected_id}"):
                if suggestion:
                    st.session_state[split_key] = "\n".join(suggestion)
                    st.rerun()
                else:
                    st.info("No encontré una enumeración clara. Escríbelas manualmente, una por línea.")
            st.text_area("Subtareas", key=split_key, height=130,
                         placeholder="Primera subtarea\nSegunda subtarea\nTercera subtarea")
            if st.button("Aplicar desglose", key=f"apply_{selected_id}"):
                parts = extract_tasks(st.session_state[split_key])
                if len(parts) < 2:
                    st.warning("Escribe al menos dos subtareas, una por línea.")
                else:
                    index = next(i for i, t in enumerate(st.session_state.tasks) if t["id"] == selected_id)
                    replacements = [new_task(txt, zone=item["zone"], notes=item["notes"]) for txt in parts]
                    st.session_state.tasks[index:index + 1] = replacements
                    st.session_state.focus_target = replacements[0]["id"]
                    st.toast(f"Tarea desglosada en {len(replacements)} subtareas editables.")
                    st.rerun()

    with st.expander("➕ Agregar una tarea manualmente"):
        with st.form("manual_add", clear_on_submit=True):
            add_text = st.text_input("Nueva tarea")
            add_zone = st.selectbox("Zona inicial", ZONES)
            add_note = st.text_input("Nota (opcional)")
            if st.form_submit_button("Agregar a la lista", type="primary"):
                if add_text.strip():
                    new = new_task(add_text, zone=add_zone, notes=add_note)
                    st.session_state.tasks.append(new)
                    st.session_state.focus_target = new["id"]
                    st.rerun()
                else:
                    st.warning("Escribe una tarea.")

    with st.expander("📋 Ver lista completa en tabla"):
        st.dataframe(
            [{"#": i + 1, "Tarea": t["text"], "Zona": t["zone"], "Nota": t["notes"]}
             for i, t in enumerate(st.session_state.tasks)],
            hide_index=True,
            use_container_width=True,
        )

st.divider()

# --------- Paso 3 ---------
st.subheader("3 · Matriz de cinco zonas en tiempo real")
st.caption("Las tareas etiquetadas aparecen en su zona. Si hay muchas, puedes desplazarte dentro de cada cuadro sin perder la vista de los cinco.")
st.html(matrix_markup(st.session_state.tasks))
pending = [task for task in st.session_state.tasks if task["zone"] == "Sin clasificar"]
if pending:
    st.info(f"Quedan **{len(pending)} tareas sin clasificar**. No se muestran dentro de la matriz hasta que les asignes una zona.")
else:
    st.caption("✅ Todas las tareas actuales están clasificadas." if total else "Agrega tareas para llenar la matriz.")
