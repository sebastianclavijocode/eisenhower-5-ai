"""Eisenhower 5 + IA — tareas masivas, etiquetas, Kanban y completadas."""
from __future__ import annotations

import html
import json
from datetime import datetime

import streamlit as st

from task_parser import ZONES, extract_tasks, new_task, normalize_import, parse_tags, proposed_subtasks

try:
    from streamlit_dnd import dnd, apply_move
except ImportError:
    dnd = None
    apply_move = None

st.set_page_config(
    page_title="Eisenhower 5 + IA",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ACTIVE_ZONES = list(ZONES)
MATRIX_ZONES = list(ZONES[1:])
DONE = "Completadas"
ALL_ZONES = ACTIVE_ZONES + [DONE]
ZONE_KEYS = {
    "Sin clasificar": "zone_inbox",
    "Do Now": "zone_now",
    "Schedule": "zone_schedule",
    "Delegate to Human": "zone_human",
    "Delegate to AI": "zone_ai",
    "Eliminate": "zone_eliminate",
}
META = {
    "Do Now": ("⚡", "Urgente · Importante", "#F5B9BF"),
    "Schedule": ("📅", "Importante · No urgente", "#BFE7F5"),
    "Delegate to Human": ("👥", "Asignar a una persona", "#F9E6A3"),
    "Delegate to AI": ("🤖", "Asignar a IA / automatización", "#D9CAFF"),
    "Eliminate": ("🗑️", "Eliminar o reducir", "#E9EAED"),
}

EXAMPLE = """Automatizaciones e inteligencia artificial
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

CSS = """
<style>
  :root { --board:#303B60; --muted:#dce5fb; }
  .block-container { max-width:1530px; padding-top:1.2rem; padding-bottom:2rem; }
  .eai-intro { display:flex; align-items:center; gap:10px; margin-bottom:5px; }
  .eai-intro strong { font-size:27px; letter-spacing:-.5px; }
  .eai-lead { opacity:.78; font-size:14px; margin-bottom:10px; }
  .st-key-matrix_shell {background:var(--board);padding:18px 18px 20px;border-radius:21px;box-shadow:0 14px 30px #0002;}
  .st-key-matrix_shell .st-key-zone_now,
  .st-key-matrix_shell .st-key-zone_schedule,
  .st-key-matrix_shell .st-key-zone_human,
  .st-key-matrix_shell .st-key-zone_ai,
  .st-key-matrix_shell .st-key-zone_eliminate {
    background:#ffffff10;border-radius:16px;border:1px solid #ffffff30;
    padding:12px 12px 10px;min-width:0;
  }
  .st-key-matrix_shell .eai-zone-head { font-size:17px; text-align:center; font-weight:800; color:white; }
  .st-key-matrix_shell .eai-zone-sub { font-size:11px; text-align:center; color:var(--muted); padding-bottom:9px; }
  .st-key-matrix_shell [class*='st-key-card_'],
  .st-key-zone_inbox [class*='st-key-card_'] {
    border-radius:14px!important;border:1px solid #00000012!important;
    padding:10px 11px 8px!important;margin-bottom:9px;
    box-shadow:0 7px 13px #07163127;
    color:#1a2635!important;
  }
  .st-key-matrix_shell .st-key-zone_now [class*='st-key-card_'] {background:#F5B9BF;}
  .st-key-matrix_shell .st-key-zone_schedule [class*='st-key-card_'] {background:#BFE7F5;}
  .st-key-matrix_shell .st-key-zone_human [class*='st-key-card_'] {background:#F9E6A3;}
  .st-key-matrix_shell .st-key-zone_ai [class*='st-key-card_'] {background:#D9CAFF;}
  .st-key-matrix_shell .st-key-zone_eliminate [class*='st-key-card_'] {background:#E9EAED;}
  .st-key-zone_inbox [class*='st-key-card_'] {background:#f5f4ef;}
  .eai-card-title{font-size:12.5px;line-height:1.38;font-weight:700;color:#243044;overflow-wrap:anywhere;}
  .eai-card-note{font-size:11px;color:#3c4655;margin:5px 0 3px;overflow-wrap:anywhere;}
  .eai-chips{display:flex;flex-wrap:wrap;gap:5px;margin-top:7px;}
  .eai-chip{display:inline-flex;align-items:center;border-radius:100px;background:#ffffffb0;color:#263045;font-size:10px;font-weight:700;padding:3px 8px;max-width:100%;overflow-wrap:anywhere;}
  .eai-zone-empty{font-size:12px;color:#dce3fa;text-align:center;border:1px dashed #ffffff50;border-radius:10px;padding:15px 6px;}
  .eai-zone-number{border-radius:20px;padding:2px 8px;background:#ffffff34;color:white;font-size:12px;margin-left:4px}
  .eai-mini {font-size:12px;color:#c1cae2;}
  .st-key-matrix_shell [class*='st-key-card_'] button,
  .st-key-zone_inbox [class*='st-key-card_'] button {font-size:11px!important;padding:3px 7px!important;min-height:28px!important;}
  .st-key-matrix_shell [class*='st-key-card_'] [data-testid='stHorizontalBlock'] {gap:5px;}
  .st-key-matrix_shell [class*='st-key-card_'] [data-testid='stVerticalBlock'] {gap:4px;}
  .st-key-zone_inbox [class*='st-key-card_'] [data-testid='stVerticalBlock']{gap:4px;}
  .eai-status{font-size:12px;opacity:.72;}
  .eai-help{font-size:12px;opacity:.75;margin-top:3px;}
</style>
"""
st.html(CSS)

if "board" not in st.session_state:
    st.session_state.board = {zone: [] for zone in ALL_ZONES}
if "bulk_input" not in st.session_state:
    st.session_state.bulk_input = ""
if "flash" not in st.session_state:
    st.session_state.flash = ""


def all_tasks() -> list[dict]:
    return [task for tasks in st.session_state.board.values() for task in tasks]


def find_task(task_id: str) -> tuple[str | None, dict | None]:
    for zone, items in st.session_state.board.items():
        for task in items:
            if task["id"] == task_id:
                return zone, task
    return None, None


def move_task(task_id: str, destination: str) -> None:
    if destination not in ALL_ZONES:
        return
    origin, task = find_task(task_id)
    if not task or origin is None or origin == destination:
        return
    st.session_state.board[origin].remove(task)
    if destination == DONE:
        task["last_zone"] = origin if origin != DONE else task.get("last_zone", "Sin clasificar")
        task["completed"] = True
        task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    else:
        task["completed"] = False
        task["completed_at"] = ""
        task["zone"] = destination
    st.session_state.board[destination].append(task)


def complete_task(task_id: str) -> None:
    move_task(task_id, DONE)


def restore_task(task_id: str) -> None:
    _, task = find_task(task_id)
    if task:
        move_task(task_id, task.get("last_zone", "Sin clasificar"))


def remove_task(task_id: str) -> None:
    zone, task = find_task(task_id)
    if zone and task:
        st.session_state.board[zone].remove(task)


def save_task(task_id: str, text: str, tags: str, note: str, destination: str) -> None:
    _, task = find_task(task_id)
    if task and text.strip():
        task["text"] = text.strip()
        task["tags"] = parse_tags(tags)
        task["notes"] = note.strip()
        move_task(task_id, destination)


def fill_example() -> None:
    st.session_state.bulk_input = EXAMPLE


def add_bulk() -> None:
    text = st.session_state.get("bulk_input", "")
    split = st.session_state.get("bulk_split", False)
    extracted = extract_tasks(text, expand_lists=split)
    if not extracted:
        st.session_state.flash = "Pega al menos una tarea (una por línea o una lista con viñetas)."
        return
    existing = {t["text"].strip().casefold() for t in all_tasks()}
    added = 0
    for sentence in extracted:
        if sentence.strip().casefold() in existing:
            continue
        task = new_task(sentence)
        st.session_state.board["Sin clasificar"].append(task)
        existing.add(sentence.strip().casefold())
        added += 1
    st.session_state.bulk_input = ""  # en callback: seguro para el text_area
    st.session_state.flash = f"Se agregaron {added} tareas nuevas a Sin clasificar. Las repetidas se omitieron."


def import_json() -> None:
    content = st.session_state.get("json_input", "")
    try:
        imported = normalize_import(json.loads(content))
    except (ValueError, json.JSONDecodeError) as exc:
        st.session_state.flash = f"No fue posible importar: {exc}"
        return
    st.session_state.board = {zone: [] for zone in ALL_ZONES}
    for task in imported:
        group = DONE if task.get("completed", False) else task["zone"]
        st.session_state.board[group].append(task)
    st.session_state.flash = f"Se recuperaron {len(imported)} tareas."


def render_card(task: dict, zone: str) -> None:
    title = html.escape(task["text"])
    note = html.escape(task.get("notes", ""))
    chips = "".join(f'<span class="eai-chip">{html.escape(t)}</span>' for t in task.get("tags", []))
    with st.container(key=f"card_{task['id']}", border=True):
        st.html(f'<div class="eai-card-title">{title}</div>'
                + (f'<div class="eai-chips">{chips}</div>' if chips else "")
                + (f'<div class="eai-card-note">📝 {note}</div>' if note else ""))
        col_complete, col_move, col_edit = st.columns(3, gap="small")
        if col_complete.button("✓ Hecha", key=f"done_{task['id']}", use_container_width=True):
            complete_task(task["id"])
            st.rerun()
        with col_move.popover("↔ Mover", use_container_width=True):
            destination = st.selectbox(
                "Mover a la zona",
                ACTIVE_ZONES,
                index=ACTIVE_ZONES.index(zone),
                key=f"move_dest_{task['id']}_{ZONE_KEYS[zone]}",
            )
            if st.button("Aplicar cambio", key=f"move_apply_{task['id']}", use_container_width=True):
                move_task(task["id"], destination)
                st.rerun()
        with col_edit.popover("✏️ Editar", use_container_width=True):
            with st.form(key=f"edit_form_{task['id']}"):
                edited_text = st.text_area("Tarea", value=task["text"], height=100)
                edited_tags = st.text_input("Mini tags (separados por |)", value=" | ".join(task.get("tags", [])),
                                            placeholder="👥 Diana | 📁 Organización")
                edited_note = st.text_area("Nota opcional", value=task.get("notes", ""), height=80)
                edited_zone = st.selectbox("Zona", ACTIVE_ZONES, index=ACTIVE_ZONES.index(zone))
                if st.form_submit_button("Guardar cambios", type="primary", use_container_width=True):
                    if edited_text.strip():
                        save_task(task["id"], edited_text, edited_tags, edited_note, edited_zone)
                        st.rerun()
                    else:
                        st.warning("La descripción no puede estar vacía.")


def render_zone(zone: str) -> None:
    icon, hint, _ = META[zone]
    zone_id = ZONE_KEYS[zone]
    with st.container(key=zone_id, border=True, height=306):
        st.html(f'<div class="eai-zone-head">{icon} {html.escape(zone.upper())} '
                f'<span class="eai-zone-number">{len(st.session_state.board[zone])}</span></div>'
                f'<div class="eai-zone-sub">{html.escape(hint)}</div>')
        if not st.session_state.board[zone]:
            st.html('<div class="eai-zone-empty">Arrastra una tarjeta aquí</div>')
        for task in st.session_state.board[zone]:
            render_card(task, zone)


st.title("🧠 Automatizaciones e Inteligencia Artificial")
st.caption("Pega tareas en bloque · Etiquétalas · Muévelas entre cinco zonas · Marca las completadas")

with st.sidebar:
    st.header("💾 Guardar y recuperar")
    st.caption("Tus cambios viven en esta sesión. Descarga un JSON para no perderlos entre visitas.")
    snapshot = []
    for zone, rows in st.session_state.board.items():
        for task in rows:
            record = dict(task)
            record["completed"] = zone == DONE
            if zone != DONE:
                record["zone"] = zone
            snapshot.append(record)
    st.download_button("⬇️ Descargar tareas.json", json.dumps(snapshot, ensure_ascii=False, indent=2),
                       file_name="eisenhower_tareas.json", mime="application/json", use_container_width=True)
    with st.expander("📥 Restaurar desde JSON"):
        st.text_area("Pega aquí el contenido del archivo JSON", key="json_input", height=160)
        st.button("Restaurar tareas", on_click=import_json, use_container_width=True, type="primary")
    st.divider()
    st.markdown("**Mini tags**\n\n" "Puedes agregar etiquetas como `👥 Miriam`, `💳 Compra / acceso` o `🤖 IA`. "
                "Sepáralas con `|`. Las etiquetas explican una tarea: **la zona** define su prioridad o destino.")
    st.caption("Arrastrar tarjetas usa el componente comunitario streamlit-dnd. Si no funciona en tu navegador, usa ↔ Mover.")

with st.expander("➕ Pegar nuevas tareas masivas", expanded=not bool(all_tasks())):
    st.write("Pega toda la lista. Las tareas nuevas entran a **Sin clasificar**; las que ya existen se conservan.")
    st.text_area("Lista de tareas", key="bulk_input", height=150,
                 placeholder="- Corregir números telefónicos\n- Crear enlace de pago en Stripe\n- Programar recordatorios del webinar")
    st.checkbox("Dividir enumeraciones claras en subtareas (sin usar IA externa)", key="bulk_split")
    bc1, bc2 = st.columns([2, 1])
    bc1.button("➕ Agregar todas las tareas", key="bulk_add", type="primary", on_click=add_bulk,
               use_container_width=True)
    bc2.button("📋 Usar texto de ejemplo", on_click=fill_example, use_container_width=True)

if st.session_state.flash:
    st.info(st.session_state.flash)
    st.session_state.flash = ""

active_count = sum(len(st.session_state.board[z]) for z in ACTIVE_ZONES)
done_count = len(st.session_state.board[DONE])
pending_count = len(st.session_state.board["Sin clasificar"])
total = active_count + done_count
k1, k2, k3, k4 = st.columns(4)
k1.metric("Activas", active_count)
k2.metric("Sin clasificar", pending_count)
k3.metric("Completadas", done_count)
k4.metric("Avance", f"{(100*done_count/total):.0f}%" if total else "0%")

view = st.segmented_control("Vista", ["🧩 Matriz", "🏷️ Clasificar", "✅ Completadas"],
                            default="🧩 Matriz", key="view", label_visibility="collapsed")

if view == "🏷️ Clasificar":
    st.subheader("🏷️ Etiqueta tus tareas")
    st.caption("Selecciona una zona para cada tarea. El cambio es inmediato y la tarea aparecerá en ese cuadro de la matriz.")
    active = [t for z in ACTIVE_ZONES for t in st.session_state.board[z]]
    if not active:
        st.info("No hay tareas activas. Agrégalas desde la sección de tareas masivas.")
    else:
        show_only_pending = st.checkbox("Solo mostrar sin clasificar", value=True)
        selected = [t for t in active if t["zone"] == "Sin clasificar"] if show_only_pending else active
        if not selected:
            st.success("Todas tus tareas tienen una zona. Desactiva el filtro para verlas todas.")
        for task in selected:
            current_zone, _ = find_task(task["id"])
            with st.container(border=True):
                left, right = st.columns([2.1, 1])
                left.write(task["text"])
                key = f"classify_{task['id']}"
                st.session_state[key] = current_zone
                def _on_classify(tid=task["id"], widget_key=key):
                    move_task(tid, st.session_state[widget_key])
                right.selectbox("Zona", ACTIVE_ZONES,
                                index=ACTIVE_ZONES.index(current_zone),
                                key=key, on_change=_on_classify)
                with st.expander("✏️ Editar texto, mini tags o dividir en subtareas"):
                    with st.form(key=f"class_edit_{task['id']}"):
                        txt = st.text_area("Texto", value=task["text"])
                        mini = st.text_input("Mini tags (separar con |)", value=" | ".join(task.get("tags", [])))
                        note = st.text_input("Nota opcional", value=task.get("notes", ""))
                        if st.form_submit_button("Guardar", type="primary"):
                            save_task(task["id"], txt, mini, note, current_zone)
                            st.rerun()
                    suggested = proposed_subtasks(task["text"])
                    if suggested:
                        st.caption("Subtareas sugeridas por enumeración (puedes editarlas):")
                    pieces = st.text_area("Una subtarea por línea", value="\n".join(suggested),
                                         key=f"split_{task['id']}", height=100,
                                         placeholder="Subtarea 1\nSubtarea 2")
                    if st.button("Crear subtareas y reemplazar la tarea principal", key=f"split_submit_{task['id']}"):
                        parts = extract_tasks(pieces)
                        if len(parts) < 2:
                            st.warning("Escribe al menos dos subtareas.")
                        else:
                            idx = st.session_state.board[current_zone].index(task)
                            st.session_state.board[current_zone][idx:idx + 1] = [
                                new_task(s, zone=current_zone, notes=task.get("notes", ""),
                                         tags=task.get("tags", [])) for s in parts
                            ]
                            st.rerun()

elif view == "✅ Completadas":
    st.subheader(f"✅ Completadas ({done_count})")
    st.caption("Cuando marcas una tarea como hecha, sale de la matriz y queda aquí. Puedes restaurarla a su zona anterior.")
    if not done_count:
        st.info("Todavía no has completado tareas.")
    for task in st.session_state.board[DONE]:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"**{task['text']}**")
            chips = "".join(f'<span class="eai-chip">{html.escape(tag)}</span>' for tag in task.get("tags", []))
            if chips:
                c1.html(f'<div class="eai-chips">{chips}</div>')
            if task.get("notes"):
                c1.caption(f"📝 {task['notes']}")
            c1.caption(f"Terminada: {task.get('completed_at') or 'Sin fecha'} · Antes: {task.get('last_zone', 'Sin clasificar')}")
            if c2.button("↩ Restaurar", key=f"restore_{task['id']}", use_container_width=True):
                restore_task(task["id"])
                st.rerun()

else:
    st.markdown("#### 🧩 Matriz de 5 zonas — arrastra las tarjetas como en un pipeline")
    st.caption("Arrastra por la esquina de cada tarjeta para cambiarla de cuadro. También puedes usar ↔ Mover o ✓ Hecha.")
    draggable_keys: list[str] = []
    if pending_count:
        with st.expander(f"📥 Bandeja sin clasificar · {pending_count} tareas (puedes arrastrarlas a la matriz)", expanded=True):
            with st.container(key=ZONE_KEYS["Sin clasificar"], border=True, height=235):
                draggable_keys.append(ZONE_KEYS["Sin clasificar"])
                for task in st.session_state.board["Sin clasificar"]:
                    render_card(task, "Sin clasificar")
    with st.container(key="matrix_shell", border=False):
        upper_left, upper_right = st.columns(2, gap="small")
        with upper_left:
            render_zone("Do Now")
        with upper_right:
            render_zone("Schedule")
        lower_left, lower_mid, lower_right = st.columns(3, gap="small")
        with lower_left:
            render_zone("Delegate to Human")
        with lower_mid:
            render_zone("Delegate to AI")
        with lower_right:
            render_zone("Eliminate")
    draggable_keys.extend(ZONE_KEYS[zone] for zone in MATRIX_ZONES)

    if dnd is not None:
        try:
            move_event = dnd(*draggable_keys, handle=True, handle_icon="⠿",
                             indicator="ghost", color="#90d3ff", key="eai_dragdrop")
            if move_event:
                mapping = {ZONE_KEYS[zone]: st.session_state.board[zone] for zone in ACTIVE_ZONES
                           if ZONE_KEYS[zone] in draggable_keys}
                apply_move(move_event, mapping)
                for zone in ACTIVE_ZONES:
                    for item in st.session_state.board[zone]:
                        item["zone"] = zone
                st.rerun()
        except Exception as exc:
            st.warning(f"El arrastre no está disponible en esta sesión: {exc}. Usa el botón ↔ Mover.")
    else:
        st.info("Para activar el arrastre instala streamlit-dnd==0.2.0. Mientras tanto puedes usar ↔ Mover.")

    with st.expander(f"✅ Completadas ({done_count}) · historial", expanded=False):
        if not done_count:
            st.caption("Al pulsar ✓ Hecha, la tarea desaparecerá de la matriz y quedará guardada aquí.")
        for task in st.session_state.board[DONE]:
            r1, r2 = st.columns([5, 1])
            r1.write(f"✓ {task['text']}")
            if r2.button("↩ Restaurar", key=f"quick_restore_{task['id']}", use_container_width=True):
                restore_task(task["id"])
                st.rerun()

st.caption("Los mini tags son notas cortas; no mueven tareas. La zona decide dónde aparece cada tarjeta. "
           "Los datos se guardan durante la sesión; usa el JSON de la barra lateral para conservarlos.")
