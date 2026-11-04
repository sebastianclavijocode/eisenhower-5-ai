"""Utilidades para separar listas masivas de tareas, sin servicios externos."""
from __future__ import annotations

import re
import uuid

ZONES = (
    "Sin clasificar",
    "Do Now",
    "Schedule",
    "Delegate to Human",
    "Delegate to AI",
    "Eliminate",
)

HEADINGS = {
    "do now", "schedule", "delegate", "delegate to human", "delegate to ai",
    "eliminate", "no importante", "importante", "urgente", "no urgente",
    "tareas", "lista de tareas", "pendientes", "tareas pendientes",
    "automatizaciones e inteligencia artificial", "automatizaciones y ia",
}


def new_task(
    text: str,
    zone: str = "Sin clasificar",
    notes: str = "",
    tags: list[str] | None = None,
) -> dict:
    return {
        "id": uuid.uuid4().hex,
        "text": text.strip(),
        "zone": zone if zone in ZONES else "Sin clasificar",
        "notes": notes.strip(),
        "tags": list(tags or []),
        "completed": False,
        "completed_at": "",
        "last_zone": "Sin clasificar",
    }


def _strip_bullet(line: str) -> str:
    return re.sub(r"^\s*(?:[-*•●◦☐✅✓]\s*|\d{1,3}[.)]\s+)", "", line.strip()).strip()


def _heading(line: str) -> bool:
    plain = re.sub(r"^#+\s*", "", line).rstrip(":").strip().lower()
    return plain in HEADINGS or (line.strip().endswith(":") and len(line.strip()) < 55)


def proposed_subtasks(text: str) -> list[str]:
    """Divide una enumeración clara; no hace promesas de descomposición con IA."""
    if ":" not in text:
        return []
    title, rest = text.split(":", 1)
    if "," not in rest and ";" not in rest:
        return []
    pieces = [p.strip(" .;\t") for p in re.split(r"\s*[,;]\s*|\s+y\s+", rest) if p.strip(" .;\t")]
    if not 2 <= len(pieces) <= 8:
        return []
    title = title.strip(" .")
    return [f"{title} — {part}" for part in pieces]


def extract_tasks(text: str, expand_lists: bool = False) -> list[str]:
    tasks: list[str] = []
    for line in text.replace("\r\n", "\n").split("\n"):
        line = _strip_bullet(line)
        if not line or _heading(line):
            continue
        pieces = re.split(r";\s*(?=[A-Za-zÁÉÍÓÚÑáéíóúñ])|(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡])", line)
        for raw in pieces:
            item = _strip_bullet(raw)
            if not item:
                continue
            subtasks = proposed_subtasks(item) if expand_lists else []
            tasks.extend(subtasks or [item])
    return tasks


def parse_tags(value: str) -> list[str]:
    """La barra vertical separa los mini-tags: '👥 Miriam | 💳 Compra'."""
    tags = [v.strip() for v in value.split("|")]
    return list(dict.fromkeys(tag for tag in tags if tag))[:8]


def normalize_import(payload: object) -> list[dict]:
    """Admite JSON de la app actual y de las versiones anteriores."""
    if not isinstance(payload, list):
        raise ValueError("El JSON debe contener una lista de tareas.")
    if len(payload) > 2000:
        raise ValueError("Máximo 2000 tareas por importación.")
    out = []
    seen: set[str] = set()
    for row in payload:
        if not isinstance(row, dict):
            raise ValueError("Cada tarea debe ser un objeto JSON.")
        text = row.get("text", row.get("task", ""))
        if not isinstance(text, str) or not text.strip():
            continue
        zone = row.get("zone", "Sin clasificar")
        if zone not in ZONES:
            zone = "Sin clasificar"
        notes = row.get("notes", "")
        raw_tags = row.get("tags", [])
        if isinstance(raw_tags, str):
            tags = parse_tags(raw_tags)
        elif isinstance(raw_tags, list):
            tags = [str(x).strip() for x in raw_tags if str(x).strip()][:8]
        else:
            tags = []
        task = new_task(text, zone=zone, notes=str(notes or ""), tags=tags)
        existing_id = row.get("id")
        if isinstance(existing_id, str) and re.fullmatch(r"[a-zA-Z0-9_-]{6,64}", existing_id) and existing_id not in seen:
            task["id"] = existing_id
        seen.add(task["id"])
        task["completed"] = bool(row.get("completed", False))
        task["completed_at"] = str(row.get("completed_at") or "")
        last = row.get("last_zone", zone)
        task["last_zone"] = last if last in ZONES else zone
        out.append(task)
    return out
