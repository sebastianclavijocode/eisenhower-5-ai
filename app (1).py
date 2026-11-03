
import json
import streamlit as st

st.set_page_config(
    page_title="Automatizaciones e Inteligencia Artificial",
    page_icon="🤖",
    layout="wide",
)

# -----------------------------
# ESTILOS
# -----------------------------
st.markdown("""
<style>
    .main {
        background-color: #111827;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3, p, label {
        color: white;
    }

    .task-card {
        border-radius: 16px;
        padding: 14px 16px;
        margin-bottom: 12px;
        color: #1d2433;
        box-shadow: 0 8px 18px rgba(0,0,0,.15);
        min-height: 115px;
    }

    .do-now {
        background: #f4b8b8;
    }

    .schedule {
        background: #bfe6f4;
    }

    .human {
        background: #f6e59a;
    }

    .ai {
        background: #d9ccff;
    }

    .eliminate {
        background: #ececec;
    }

    .task-title {
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .pill {
        display: inline-block;
        background: rgba(255,255,255,.65);
        border-radius: 999px;
        padding: 4px 8px;
        margin: 3px 4px 0 0;
        font-size: 11px;
        font-weight: 700;
    }

    .zone-title {
        text-align:center;
        font-weight: 800;
        font-size: 20px;
        margin-bottom: 3px;
    }

    .zone-desc {
        text-align:center;
        color:#dce3f6;
        font-size:12px;
        margin-bottom:12px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# DATOS INICIALES
# -----------------------------
DEFAULT_TASKS = [
    {
        "task": "Generar el reporte financiero mensual con videos ganadores, fuentes de matrículas y presupuesto publicitario.",
        "zone": "Do Now",
        "delegate": "IA + Humano",
        "notes": "IA prepara borrador; humano valida cifras."
    },
    {
        "task": "Crear y configurar en Stripe el enlace de pago de $500 MXN para la evaluación.",
        "zone": "Do Now",
        "delegate": "Humano",
        "notes": "Acción en cuenta financiera."
    },
    {
        "task": "Actualizar el presupuesto de remarketing y estimar las metas de alcance y gasto.",
        "zone": "Do Now",
        "delegate": "IA + Humano",
        "notes": "IA analiza; humano decide."
    },
    {
        "task": "Cambiar a amarillo los botones de la página de aterrizaje.",
        "zone": "Do Now",
        "delegate": "IA + Humano",
        "notes": "IA/desarrollador puede ejecutar; humano valida visualmente."
    },
    {
        "task": "Realizar pruebas de validación de videos y landing page.",
        "zone": "Do Now",
        "delegate": "IA + Humano",
        "notes": "IA hace QA inicial; humano prueba el resultado final."
    },
    {
        "task": "Corregir el formato de los números telefónicos para que las llamadas automatizadas lleguen correctamente.",
        "zone": "Schedule",
        "delegate": "IA",
        "notes": "Ideal para limpieza y normalización estructurada."
    },
    {
        "task": "Ajustar los flujos del webinar: enlaces de pago después de la grabación, recordatorios 10 minutos antes y mensajes de seguimiento.",
        "zone": "Schedule",
        "delegate": "IA + Humano",
        "notes": "Humano configura; IA redacta mensajes."
    },
    {
        "task": "Programar la sección de rutas de carreras y el carrusel dinámico.",
        "zone": "Schedule",
        "delegate": "IA + Humano",
        "notes": "Desarrollador ejecuta; IA puede asistir con código."
    },
    {
        "task": "Adquirir y configurar técnicamente la cuenta de Zoom, coordinando la compra con Miriam.",
        "zone": "Delegate to Human",
        "delegate": "Humano",
        "notes": "Requiere compra, acceso y coordinación."
    },
    {
        "task": "Indicar a Diana que organice los videos por mes, promoción y carrera.",
        "zone": "Delegate to Human",
        "delegate": "Humano",
        "notes": "Organización operativa."
    },
    {
        "task": "Normalizar y validar el formato de los números telefónicos antes de cargarlos al sistema.",
        "zone": "Delegate to AI",
        "delegate": "IA",
        "notes": "Alta delegabilidad; revisar una muestra."
    },
    {
        "task": "Crear el primer borrador del reporte financiero mensual a partir de las fuentes disponibles.",
        "zone": "Delegate to AI",
        "delegate": "IA",
        "notes": "IA resume y clasifica; humano valida finanzas."
    },
    {
        "task": "Localizar el video anterior de maestros y evaluar su posible reutilización.",
        "zone": "Delegate to AI",
        "delegate": "IA + Humano",
        "notes": "IA puede localizar/analizar si tiene acceso; humano decide."
    },
    {
        "task": "Redactar recordatorios, mensajes post-webinar y variantes de seguimiento.",
        "zone": "Delegate to AI",
        "delegate": "IA",
        "notes": "Generación de copy con revisión humana."
    },
]

ZONES = [
    "Do Now",
    "Schedule",
    "Delegate to Human",
    "Delegate to AI",
    "Eliminate",
]

DELEGATE_OPTIONS = [
    "Humano",
    "IA",
    "IA + Humano",
    "No aplica",
]

ZONE_META = {
    "Do Now": {
        "emoji": "⚡",
        "css": "do-now",
        "desc": "Urgente + importante · Resolver ahora",
    },
    "Schedule": {
        "emoji": "📅",
        "css": "schedule",
        "desc": "Importante + no urgente · Programar con fecha",
    },
    "Delegate to Human": {
        "emoji": "👥",
        "css": "human",
        "desc": "Coordinación, acceso o criterio humano",
    },
    "Delegate to AI": {
        "emoji": "🤖",
        "css": "ai",
        "desc": "Repetitivo, estructurado, analítico o generativo",
    },
    "Eliminate": {
        "emoji": "🗑",
        "css": "eliminate",
        "desc": "No urgente + no importante · Eliminar o reducir",
    },
}

if "tasks" not in st.session_state:
    st.session_state.tasks = DEFAULT_TASKS.copy()


# -----------------------------
# HELPERS
# -----------------------------
def task_card(task):
    meta = ZONE_META[task["zone"]]
    return f"""
    <div class="task-card {meta['css']}">
        <div class="task-title">{task['task']}</div>
        <span class="pill">👤 {task['delegate']}</span>
        <span class="pill">📝 {task['notes']}</span>
    </div>
    """


def zone_block(zone_name):
    meta = ZONE_META[zone_name]
    st.markdown(
        f"""
        <div class="zone-title">{meta['emoji']} {zone_name.upper()}</div>
        <div class="zone-desc">{meta['desc']}</div>
        """,
        unsafe_allow_html=True,
    )

    zone_tasks = [
        (idx, task)
        for idx, task in enumerate(st.session_state.tasks)
        if task["zone"] == zone_name
    ]

    if not zone_tasks:
        st.info("No hay tareas en esta zona.")

    for idx, task in zone_tasks:
        st.markdown(task_card(task), unsafe_allow_html=True)

        with st.expander("Editar tarea", expanded=False):
            edited_task = st.text_area(
                "Tarea",
                value=task["task"],
                key=f"task_{idx}",
            )

            edited_zone = st.selectbox(
                "Zona",
                ZONES,
                index=ZONES.index(task["zone"]),
                key=f"zone_{idx}",
            )

            edited_delegate = st.selectbox(
                "Delegación",
                DELEGATE_OPTIONS,
                index=DELEGATE_OPTIONS.index(task["delegate"]),
                key=f"delegate_{idx}",
            )

            edited_notes = st.text_input(
                "Notas",
                value=task["notes"],
                key=f"notes_{idx}",
            )

            c1, c2 = st.columns(2)

            if c1.button("💾 Guardar", key=f"save_{idx}", use_container_width=True):
                st.session_state.tasks[idx] = {
                    "task": edited_task,
                    "zone": edited_zone,
                    "delegate": edited_delegate,
                    "notes": edited_notes,
                }
                st.rerun()

            if c2.button("🗑 Eliminar", key=f"delete_{idx}", use_container_width=True):
                st.session_state.tasks.pop(idx)
                st.rerun()


# -----------------------------
# TÍTULO
# -----------------------------
st.title("Automatizaciones e Inteligencia Artificial")
st.caption("Matriz editable de 5 zonas para priorizar y decidir qué ejecutar, delegar a personas o delegar a IA.")


# -----------------------------
# PANEL SUPERIOR
# -----------------------------
with st.expander("➕ Agregar nueva tarea", expanded=False):
    new_task = st.text_area("Descripción de la tarea", key="new_task")
    c1, c2 = st.columns(2)

    new_zone = c1.selectbox("Zona", ZONES, key="new_zone")
    new_delegate = c2.selectbox("Delegación", DELEGATE_OPTIONS, key="new_delegate")

    new_notes = st.text_input(
        "Notas / criterio",
        placeholder="Ej: IA prepara borrador y humano valida",
        key="new_notes",
    )

    if st.button("Agregar tarea", type="primary"):
        if new_task.strip():
            st.session_state.tasks.append(
                {
                    "task": new_task.strip(),
                    "zone": new_zone,
                    "delegate": new_delegate,
                    "notes": new_notes.strip() or "Sin notas",
                }
            )
            st.rerun()
        else:
            st.warning("Escribe una tarea antes de agregarla.")


# -----------------------------
# MATRIZ VISUAL
# -----------------------------
top_left, top_right = st.columns(2, gap="large")

with top_left:
    zone_block("Do Now")

with top_right:
    zone_block("Schedule")

st.markdown("---")

bottom_1, bottom_2, bottom_3 = st.columns(3, gap="large")

with bottom_1:
    zone_block("Delegate to Human")

with bottom_2:
    zone_block("Delegate to AI")

with bottom_3:
    zone_block("Eliminate")


# -----------------------------
# IMPORTAR / EXPORTAR
# -----------------------------
st.markdown("---")
st.subheader("Importar / exportar datos")

export_json = json.dumps(
    st.session_state.tasks,
    ensure_ascii=False,
    indent=2,
)

c1, c2, c3 = st.columns(3)

c1.download_button(
    "⬇️ Descargar tareas.json",
    data=export_json,
    file_name="tasks.json",
    mime="application/json",
    use_container_width=True,
)

uploaded = c2.file_uploader(
    "Importar JSON",
    type=["json"],
    label_visibility="collapsed",
)

if uploaded is not None:
    try:
        imported = json.load(uploaded)
        if isinstance(imported, list):
            st.session_state.tasks = imported
            st.success("Tareas importadas correctamente.")
            st.rerun()
        else:
            st.error("El JSON debe contener una lista de tareas.")
    except Exception as e:
        st.error(f"No se pudo leer el archivo: {e}")

if c3.button("↩️ Restaurar ejemplo", use_container_width=True):
    st.session_state.tasks = DEFAULT_TASKS.copy()
    st.rerun()

st.caption(
    "Nota: en Streamlit Community Cloud el almacenamiento local no es permanente. "
    "Usa Exportar/Importar JSON o conecta una base de datos si necesitas persistencia real."
)
