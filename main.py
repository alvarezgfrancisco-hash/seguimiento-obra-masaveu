import streamlit as st
import pandas as pd
from datetime import date
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- CONFIGURACIÓN DE CORREO (RELLENA ESTO) ---
EMAIL_EMISOR = "tu_correo@gmail.com"
PASSWORD_APP = "tu_codigo_de_16_letras"
EMAIL_RECEPTOR = "correo_del_jefe@gmail.com"

def enviar_correo(df):
    try:
        # Crear el mensaje
        msg = MIMEMultipart()
        msg['From'] = EMAIL_EMISOR
        msg['To'] = EMAIL_RECEPTOR
        msg['Subject'] = f"Informe de Obra - {date.today()}"

        cuerpo = "Hola, adjunto envío el informe de seguimiento de obra generado hoy."
        msg.attach(MIMEText(cuerpo, 'plain'))

        # Crear el Excel en memoria
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        
        # Adjuntar el archivo
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(buffer.getvalue())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename=informe_{date.today()}.xlsx")
        msg.attach(part)

        # Conectar al servidor y enviar
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_EMISOR, PASSWORD_APP)
        server.sendmail(EMAIL_EMISOR, EMAIL_RECEPTOR, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# --- APP DE STREAMLIT ---
st.set_page_config(page_title="App de Seguimiento de Obra", page_icon="🏗️")
st.title("🏗️ App de Seguimiento de Obra")

if 'datos_obra' not in st.session_state:
    st.session_state.datos_obra = pd.DataFrame(columns=["Fecha", "Trabajador", "Tarea", "Estado"])

# Formulario (Igual que antes)
with st.container():
    nombre = st.text_input("Nombre del trabajador:", value="raul")
    fecha = st.date_input("Fecha del informe:", value=date.today())
    tarea = st.selectbox("Tarea:", ["Trazado", "Instalación", "Cableado"])
    estado = st.selectbox("Estado:", ["25%", "50%", "75%", "Finalizada"])

    if st.button("Añadir a la lista"):
        nueva_fila = pd.DataFrame({"Fecha": [str(fecha)], "Trabajador": [nombre], "Tarea": [tarea], "Estado": [estado]})
        st.session_state.datos_obra = pd.concat([st.session_state.datos_obra, nueva_fila], ignore_index=True)
        st.success("Añadido.")

st.divider()

# Tabla y Botones
if not st.session_state.datos_obra.empty:
    st.dataframe(st.session_state.datos_obra, use_container_width=True)
    col1, col2 = st.columns(2)
    
    with col1:
        # Botón descarga Excel (Funcional)
        buffer_descarga = io.BytesIO()
        with pd.ExcelWriter(buffer_descarga, engine='xlsxwriter') as writer:
            st.session_state.datos_obra.to_excel(writer, index=False)
        st.download_button("📥 Descargar Excel", buffer_descarga.getvalue(), f"obra_{date.today()}.xlsx")
        
    with col2:
        # Botón de Email (¡Ahora con envío!)
        if st.button("📧 Enviar por Email"):
            with st.spinner("Enviando correo..."):
                if enviar_correo(st.session_state.datos_obra):
                    st.success("¡Correo enviado con éxito!")
