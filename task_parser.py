"""Normalización de tareas a partir de texto pegado, sin API externa."""
from __future__ import annotations

import re
import uuid

ZONES = (
    "Sin clasificar", "Do Now", "Schedule", "Delegate to Human",
    "Delegate to AI", "Eliminate",
)

HEADINGS = {
    "do now", "schedule", "delegate", "delegate to human", "delegate to ai",
    "eliminate", "no importante", "importante", "urgente", "no urgente",
    "tareas", "lista de tareas", "pendientes", "tareas pendientes",
    "automatizaciones e inteligencia artificial", "automatizaciones y ia",
}


def new_task(text: str, zone: str = "Sin clasificar", notes: str = "") -> dict:
    return {
        "id": uuid.uuid4().hex,
        "text": text.strip(),
        "zone": zone if zone in ZONES else "Sin clasificar",
        "notes": notes.strip(),
    }


def _strip_bullet(line: str) -> str:
    line = line.strip()
    line = re.sub(r"^\s*(?:[-*•●◦☐✅✓]\s*|\d{1,3}[.)]\s+)", "", line)
    return line.strip()


def _heading(line: str) -> bool:
    clean = re.sub(r"^#+\s*", "", line).rstrip(":").strip().lower()
    return clean in HEADINGS or (line.strip().endswith(":") and len(line.strip()) < 55)


def proposed_subtasks(text: str) -> list[str]:
    """Extrae enumeraciones explícitas tras dos puntos; no inventa contenido."""
    if ":" not in text:
        return []
    title, rest = text.split(":", 1)
    # Solo en enumeraciones claras; no divide comas de una oración cualquiera.
    if "," not in rest and ";" not in rest:
        return []
    items = [i.strip(" .;\t") for i in re.split(r"\s*[,;]\s*|\s+y\s+", rest) if i.strip(" .;\t")]
    if len(items) < 2 or len(items) > 8:
        return []
    title = title.strip(" .")
    return [f"{title} — {item}" for item in items]


def extract_tasks(text: str, expand_lists: bool = False) -> list[str]:
    """Convierte renglones, viñetas y frases en tareas independientes."""
    tasks = []
    for line in text.replace("\r\n", "\n").split("\n"):
        line = _strip_bullet(line)
        if not line or _heading(line):
            continue
        # Acepta varios pendientes en un mismo párrafo separados por frases.
        pieces = re.split(r";\s*(?=[A-Za-zÁÉÍÓÚÑáéíóúñ])|(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡])", line)
        for raw in pieces:
            item = _strip_bullet(raw).strip(" \t")
            if not item:
                continue
            if expand_lists:
                subtasks = proposed_subtasks(item)
                if subtasks:
                    tasks.extend(subtasks)
                    continue
            tasks.append(item)
    return tasks


def normalize_import(payload: object) -> list[dict]:
    """Importa JSON de esta versión o exportaciones anteriores."""
    if not isinstance(payload, list):
        raise ValueError("El archivo debe contener una lista de tareas.")
    if len(payload) > 2000:
        raise ValueError("Máximo 2000 tareas por importación.")
    out = []
    for row in payload:
        if not isinstance(row, dict):
            raise ValueError("Cada tarea debe ser un objeto JSON.")
        value = row.get("text", row.get("task", ""))
        if not isinstance(value, str) or not value.strip():
            continue
        zone = row.get("zone", "Sin clasificar")
        if zone not in ZONES:
            zone = "Sin clasificar"
        notes = row.get("notes", "")
        out.append(new_task(value, zone, str(notes) if notes is not None else ""))
    return out
