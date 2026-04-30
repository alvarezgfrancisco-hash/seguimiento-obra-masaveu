import streamlit as st
import pandas as pd
from datetime import date
import io

# Configuración de la página
st.set_page_config(page_title="Seguimiento de Obra", layout="centered")

st.title("🏗️ Control de Actividad de Obra")

# Listado de tareas (Tus requisitos)
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

# Base de datos temporal
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=["Fecha", "Trabajador", "Tarea", "Estado"])

# Formulario
with st.form("nuevo_registro", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        fecha_inf = st.date_input("Fecha", date.today())
    with col2:
        nombre_operario = st.text_input("Nombre del trabajador")
    
    tarea_sel = st.selectbox("Tarea realizada:", tareas)
    estado_sel = st.selectbox("Estado actual:", estados)
    
    btn_add = st.form_submit_button("Añadir al registro")

if btn_add:
    if nombre_operario:
        nuevo = pd.DataFrame([[fecha_inf, nombre_operario, tarea_sel, estado_sel]], 
                             columns=["Fecha", "Trabajador", "Tarea", "Estado"])
        st.session_state.db = pd.concat([st.session_state.db, nuevo], ignore_index=True)
        st.success("✅ Añadido a la lista")
    else:
        st.error("⚠️ Escribe tu nombre antes de añadir")

# Mostrar tabla
st.markdown("---")
st.subheader("📋 Registros de hoy")
st.dataframe(st.session_state.db, use_container_width=True)

# Descarga de Excel
if not st.session_state.db.empty:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        st.session_state.db.to_excel(writer, index=False, sheet_name='Obra')
    
    st.download_button(
        label="📥 Descargar Excel para enviar",
        data=output.getvalue(),
        file_name=f"informe_{date.today()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
        except Exception as e:
            st.error(f"Error al enviar: {e}")
