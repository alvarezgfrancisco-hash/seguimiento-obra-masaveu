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
    import streamlit as st
import pandas as pd
from datetime import date
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Control de Obra", page_icon="🏗️")
st.title("🏗️ Seguimiento de Obra")

# 2. ESTADO DE LOS DATOS
if 'datos_obra' not in st.session_state:
    st.session_state.datos_obra = pd.DataFrame(columns=["Fecha", "Trabajador", "Tarea", "Estado"])

# 3. FUNCIÓN DE ENVÍO (Usa tus Secrets)
def enviar_correo_obra(archivo_excel):
    try:
        remitente = st.secrets["email_usuario"]
        password = st.secrets["email_password"].replace(" ", "") # Por si acaso hay espacios
        destinatario = st.secrets["email_profe"]

        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = f"Parte de Obra - {date.today()}"

        cuerpo = f"Hola Ana,\n\nAdjunto envío el registro de Seguimiento de Obra actualizado a fecha {date.today()}."
        msg.attach(MIMEText(cuerpo, 'plain'))

        adjunto = MIMEBase('application', 'octet-stream')
        adjunto.set_payload(archivo_excel)
        encoders.encode_base64(adjunto)
        adjunto.add_header('Content-Disposition', "attachment; filename= seguimiento_obra.xlsx")
        msg.attach(adjunto)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error al enviar: {e}")
        return False

# 4. FORMULARIO (Basado en tu imagen)
with st.form("form_obra", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha", date.today())
    with col2:
        trabajador = st.text_input("Nombre del trabajador")
    
    tarea = st.selectbox("Seleccione la tarea:", [
        "Trazado y marcado de cajas, tubos y cuadros",
        "Instalación de canalizaciones",
        "Cableado de circuitos",
        "Montaje de mecanismos",
        "Pruebas y verificación"
    ])
    
    estado = st.selectbox("Estado de la tarea:", [
        "Iniciada",
        "Avance en torno al 25% aprox.",
        "Avance en torno al 50% aprox.",
        "Avance en torno al 75% aprox.",
        "Finalizada"
    ])
    
    if st.form_submit_button("Añadir al registro local"):
        if trabajador:
            nueva_fila = {
                "Fecha": fecha.strftime("%Y/%m/%d"),
                "Trabajador": trabajador,
                "Tarea": tarea,
                "Estado": estado
            }
            st.session_state.datos_obra = pd.concat([st.session_state.datos_obra, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.success("Añadido correctamente")
        else:
            st.error("Escribe el nombre del trabajador")

st.divider()

# 5. TABLA Y ENVÍO
st.subheader("Registros actuales")
st.dataframe(st.session_state.datos_obra, use_container_width=True)

if not st.session_state.datos_obra.empty:
    # Generar Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        st.session_state.datos_obra.to_excel(writer, index=False)
    excel_data = output.getvalue()

    col_desc, col_env = st.columns(2)
    with col_desc:
        st.download_button("📥 Descargar Excel", data=excel_data, file_name="seguimiento_obra.xlsx")
    
    with col_env:
        if st.button("🚀 Enviar Obra a la profe"):
            with st.spinner("Enviando..."):
                if enviar_correo_obra(excel_data):
                    st.success("✅ ¡Enviado a Ana!")
