# Matriz Eisenhower + AI en Streamlit

Aplicación editable para organizar tareas en cinco zonas:

- Do Now
- Schedule
- Delegate to Human
- Delegate to AI
- Eliminate

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Subir a GitHub

Sube estos archivos a un repositorio:

```text
eisenhower_ai_streamlit/
├── app.py
├── requirements.txt
└── README.md
```

Luego puedes desplegarlo desde Streamlit Community Cloud seleccionando `app.py`.

## Edición

Desde la interfaz puedes:

- agregar tareas;
- editar tareas;
- moverlas entre zonas;
- elegir Humano, IA o IA + Humano;
- eliminar tareas;
- exportar la matriz a JSON;
- importar un JSON previamente guardado.

## Persistencia

Streamlit Community Cloud puede reiniciar la aplicación, por lo que `st.session_state`
no funciona como almacenamiento permanente. Para persistencia real puedes conectar
Supabase, Google Sheets, Airtable, SQLite externo o una base de datos.
