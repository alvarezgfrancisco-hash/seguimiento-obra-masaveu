import streamlit as st
import pandas as pd
from datetime import date
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- FUNCIÓN DE ENVÍO MEJORADA ---
def enviar_correo(df):
    try:
        # Extraemos los datos de los Secrets
        usuario = st.secrets["email_user"]
        clave = st.secrets["email_pass"]
        destino = st.secrets["email_to"]

        msg = MIMEMultipart()
        msg['From'] = usuario
        msg['To'] = destino
        msg['Subject'] = f"Informe de Obra - {date.today()}"
        msg.attach(MIMEText(f"Se adjunta el reporte de obra del día {date.today()}.", 'plain'))

        # Crear Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(buffer.getvalue())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename=informe_{date.today()}.xlsx")
        msg.attach(part)

        # CONEXIÓN DIRECTA SSL (Puerto 465)
        # Esto es más seguro y evita el error 535 en la mayoría de los casos
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(usuario, clave)
        server.sendmail(usuario, destino, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error crítico: {e}")
        return False

# --- APP INTERFAZ ---
st.set_page_config(page_title="App Seguimiento Masaveu", page_icon="🏗️")
st.title("🏗️ App de Seguimiento de Obra")

if 'datos_obra' not in st.session_state:
    st.session_state.datos_obra = pd.DataFrame(columns=["Fecha", "Trabajador", "Tarea", "Estado"])

with st.container():
    nombre = st.text_input("Nombre del trabajador:", value="raul")
    fecha = st.date_input("Fecha del informe:", value=date.today())
    tarea = st.selectbox("Tarea:", ["Trazado y marcado", "Instalación", "Cableado", "Montaje"])
    estado = st.selectbox("Estado:", ["25% aprox.", "50% aprox.", "75% aprox.", "Finalizada"])

    if st.button("Añadir a la lista"):
        nueva_fila = pd.DataFrame({"Fecha": [str(fecha)], "Trabajador": [nombre], "Tarea": [tarea], "Estado": [estado]})
        st.session_state.datos_obra = pd.concat([st.session_state.datos_obra, nueva_fila], ignore_index=True)
        st.success("Registro añadido")

st.divider()

if not st.session_state.datos_obra.empty:
    st.subheader("Registros actuales:")
    st.dataframe(st.session_state.datos_obra, use_container_width=True)
    
    c1, c2 = st.columns(2)
    with c1:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            st.session_state.datos_obra.to_excel(writer, index=False)
        st.download_button("📥 Descargar Excel", buf.getvalue(), "informe.xlsx")
        
    with c2:
        if st.button("📧 Enviar por Email"):
            with st.spinner("Conectando con Gmail..."):
                if enviar_correo(st.session_state.datos_obra):
                    st.success("¡Enviado correctamente!")
