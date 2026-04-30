import streamlit as st
import pandas as pd
from datetime import date
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Control de Obra - Masaveu", layout="centered")

# --- 1. LOGO DE LA EMPRESA ---
# Puedes usar una URL directa de tu logo o un archivo local en el repo de GitHub
# st.image("logo_empresa.png", width=200) 
st.markdown("### 🏗️ SISTEMA DE SEGUIMIENTO DE OBRA")

# --- 2. LISTADO DE TAREAS ---
tareas = [
    "Trazado y marcado de cajas, tubos y cuadros",
    "Ejecución rozas en paredes y techos",
    "Montaje de soportes",
    "Colocación tubos y conductos",
    "Tendido de cables",
    "Identificación y etiquetado",
    "Conexionado de cables en bornes o regletas",
    "Instalación y conexionado de mecanismos",
    "Fijación de carril DIN y mecanismos en cuadro eléctrico",
    "Cableado interno del cuadro eléctrico",
    "Configuración de equipos domóticos y/o automáticos",
    "Conexionado de sensores/actuadores de equipos domóticos/automáticos",
    "Pruebas de continuidad",
    "Pruebas de aislamiento",
    "Verificación de tierras",
    "Programación del automatismo",
    "Pruebas de funcionamiento"
]

# --- 3. ESTADOS DE TAREA ---
estados = [
    "Avance de la tarea en torno al 25% aprox.",
    "Avance de la tarea en torno al 50% aprox.",
    "Avance de la tarea en torno al 75% aprox.",
    "OK, finalizado sin errores",
    "Finalizado, pero con errores pendientes de corregir",
    "Finalizado y corregidos los errores"
]

# --- INICIALIZACIÓN DE LA BASE DE DATOS TEMPORAL ---
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=["Fecha", "Trabajador", "Tarea", "Estado"])

# --- FORMULARIO DE ENTRADA ---
with st.form("nuevo_registro", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha del informe", date.today())
    with col2:
        trabajador = st.text_input("Nombre del trabajador")
    
    tarea_seleccionada = st.selectbox("Seleccione la tarea:", tareas)
    estado_seleccionado = st.selectbox("Estado de la tarea:", estados)
    
    boton_añadir = st.form_submit_button("Añadir al registro local")

if boton_añadir:
    if trabajador:
        nuevo_dato = pd.DataFrame([[fecha, trabajador, tarea_seleccionada, estado_seleccionado]], 
                                 columns=["Fecha", "Trabajador", "Tarea", "Estado"])
        st.session_state.db = pd.concat([st.session_state.db, nuevo_dato], ignore_index=True)
        st.success("Registro añadido a la tabla temporal.")
    else:
        st.error("Por favor, introduzca el nombre del trabajador.")

# --- MOSTRAR TABLA ACTUAL ---
st.subheader("Registros actuales")
st.dataframe(st.session_state.db, use_container_width=True)

# --- GENERACIÓN DE EXCEL ---
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Seguimiento')
    return output.getvalue()

excel_data = to_excel(st.session_state.db)

# --- BOTONES DE ACCIÓN ---
col_descarga, col_correo = st.columns(2)

with col_descarga:
    st.download_button(
        label="📥 Descargar Excel",
        data=excel_data,
        file_name=f"informe_obra_{date.today()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col_correo:
    if st.button("📧 Enviar por Correo"):
        # CONFIGURACIÓN DE CORREO (Debe ser una cuenta Gmail o similar con contraseña de app)
        EMAIL_EMPRESA = "fmo@fundacionmasaveu.com" 
        REMITENTE = "tu_correo@gmail.com"
        PASSWORD = "tu_password_de_aplicacion" # No es tu contraseña normal, es una generada en Google

        msg = MIMEMultipart()
        msg['From'] = REMITENTE
        msg['To'] = EMAIL_EMPRESA
        msg['Subject'] = f"Informe de Obra - {date.today()} - {trabajador}"

        part = MIMEBase('application', "octet-stream")
        part.set_payload(excel_data)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="informe_{date.today()}.xlsx"')
        msg.attach(part)

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(REMITENTE, PASSWORD)
            server.send_message(msg)
            server.quit()
            st.success("Correo enviado con éxito a la empresa.")
        except Exception as e:
            st.error(f"Error al enviar: {e}")
