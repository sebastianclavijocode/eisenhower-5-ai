# Eisenhower 5 + IA — Pipeline editable

App de Streamlit para pegar tareas en bloque, clasificarlas en cinco zonas, arrastrarlas entre zonas como en un pipeline, completar tareas y conservar un historial.

## Funciones

- **Pega tareas masivas en cualquier momento.** Las nuevas quedan en **Sin clasificar**; las existentes se conservan. Evita duplicados textuales.
- **Clasifica** cada tarea como Do Now, Schedule, Delegate to Human, Delegate to AI o Eliminate.
- **Arrastra y suelta** tarjetas entre las cinco zonas y reordena las que están en una misma zona (con el componente `streamlit-dnd`).
- **Mover alternativo:** cada tarjeta tiene **↔ Mover**, por si el navegador no permite arrastrar.
- **Completar:** pulsar **✓ Hecha** saca la tarea de la matriz y la guarda en **Completadas**, con opción de **Restaurar**.
- **Mini tags y notas:** desde **✏️ Editar** puedes incluir etiquetas como `👥 Responsable operativo | 💳 Compra / acceso` y notas.
- **Subtareas:** en la vista **Clasificar**, puedes dividir una tarea en subtareas editables.
- **Exportar / importar JSON** para conservar el trabajo y recuperar versiones anteriores.

## Subir a GitHub y actualizar Streamlit

Reemplaza **`app.py`**, **`task_parser.py`** y **`requirements.txt`** en la raíz de tu repositorio `eisenhower-5-ai`. Asegúrate de que los nombres no tengan sufijos como `(1)`.

Archivos:

```text
eisenhower-5-ai/
├── app.py
├── task_parser.py
├── requirements.txt
└── README.md
```

Haz **Commit changes**. Si tu aplicación de Streamlit Community Cloud apunta a `app.py`, debería actualizarse automáticamente después del commit.

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Alcances y limitaciones

- El desglose automático de enumeraciones usa reglas; **no llama a un modelo de IA** ni decide la prioridad por ti.
- La sesión de Streamlit **no es almacenamiento permanente**. Descarga `tareas.json` antes de cerrar y vuelve a importarlo después, o conecta una base de datos.
- Arrastrar y soltar requiere `streamlit-dnd==0.2.0`. Para mayor compatibilidad el archivo `requirements.txt` usa `streamlit==1.63.0`, versión dentro del rango probado por el autor del componente. Cada tarjeta incluye **↔ Mover** como alternativa si el navegador no permite arrastrar.
- El botón **✓ Hecha** no borra la tarea. Solo la archiva en el historial, desde donde se puede restaurar.
