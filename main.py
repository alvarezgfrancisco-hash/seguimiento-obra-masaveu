import streamlit as st
import pandas as pd
from datetime import date
import io

# Configuración para móvil
st.set_page_config(page_title="Control de Obra", layout="centered")

st.title("🏗️ Seguimiento de Obra")

# Listado oficial de tareas
tareas = [
    "Trazado y marcado de cajas, tubos y cuadros", "Ejecución rozas en paredes y techos",
    "Montaje de soportes", "Colocación tubos y conductos", "Tendido de cables",
    "Identificación y etiquetado", "Conexionado de cables en bornes o regletas",
    "Instalación y conexionado de mecanismos", "Fijación de carril DIN y mecanismos en cuadro eléctrico",
    "Cableado interno del cuadro eléctrico", "Configuración de equipos domóticos y/o automáticos",
    "Conexionado de sensores/actuadores de equipos domóticos/automáticos",
    "Pruebas de continuidad", "Pruebas de aislamiento", "Verificación de tierras",
    "Programación del automatismo", "Pruebas de funcionamiento"
]

estados = [
    "Avance de la tarea en torno al 25% aprox.", "Avance de la tarea en torno al 50% aprox.",
    "Avance de la tarea en torno al 75% aprox.", "OK, finalizado sin errores",
    "Finalizado, pero con errores pendientes de corregir", "Finalizado y corregidos los errores"
]

# Base de datos en la sesión
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=["Fecha", "Trabajador", "Tarea", "Estado"])

# Formulario de entrada
with st.form("nuevo_registro", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha", date.today())
    with col2:
        trabajador = st.text_input("Nombre del trabajador")
    
    tarea = st.selectbox("Seleccione la tarea:", tareas)
    estado = st.selectbox("Estado de la tarea:", estados)
    
    enviar = st.form_submit_button("Añadir al registro local")

if enviar:
    if trabajador:
        nuevo_dato = pd.DataFrame([[fecha, trabajador, tarea, estado]], 
                                 columns=["Fecha", "Trabajador", "Tarea", "Estado"])
        st.session_state.db = pd.concat([st.session_state.db, nuevo_dato], ignore_index=True)
        st.success("Añadido correctamente")
    else:
        st.error("Por favor, pon tu nombre")

# Tabla de resultados
st.markdown("---")
st.subheader("Registros actuales")
st.dataframe(st.session_state.db, use_container_width=True)

# Botón de descarga
if not st.session_state.db.empty:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        st.session_state.db.to_excel(writer, index=False, sheet_name='Informe')
    
    st.download_button(
        label="📥 Descargar Excel para enviar",
        data=output.getvalue(),
        file_name=f"informe_obra_{date.today()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
