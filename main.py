import streamlit as st
import pandas as pd
from datetime import date
import io

# 1. Configuración de la página
st.set_page_config(page_title="App de Seguimiento de Obra", page_icon="🏗️")

st.title("🏗️ App de Seguimiento de Obra")
st.write("Complete los datos y envíe el informe por email.")

# 2. Inicializar el estado de la sesión (para que los datos no se borren)
if 'datos_obra' not in st.session_state:
    st.session_state.datos_obra = pd.DataFrame(columns=["Fecha", "Trabajador", "Tarea", "Estado"])

# --- FORMULARIO DE ENTRADA ---
with st.container():
    nombre = st.text_input("Nombre del trabajador:", value="raul")
    fecha = st.date_input("Fecha del informe:", value=date.today())
    
    tarea = st.selectbox(
        "Seleccione la tarea realizada:",
        [
            "Trazado y marcado de cajas, tubos y cuadros",
            "Instalación de tubería",
            "Cableado",
            "Montaje de mecanismos",
            "Pruebas de continuidad"
        ]
    )
    
    estado = st.selectbox(
        "Estado de la tarea:",
        ["Avance 25% aprox.", "Avance 50% aprox.", "Avance 75% aprox.", "Tarea finalizada"]
    )

    if st.button("Añadir a la lista"):
        nueva_fila = pd.DataFrame({
            "Fecha": [fecha.strftime("%Y-%m-%d")],
            "Trabajador": [nombre],
            "Tarea": [tarea],
            "Estado": [estado]
        })
        st.session_state.datos_obra = pd.concat([st.session_state.datos_obra, nueva_fila], ignore_index=True)
        st.success("Registro añadido correctamente.")

st.divider()

# --- TABLA DE REGISTROS ---
st.subheader("Registros actuales:")

if not st.session_state.datos_obra.empty:
    st.dataframe(st.session_state.datos_obra, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    # Lógica para descargar Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        st.session_state.datos_obra.to_excel(writer, index=False)
        
    with col1:
        st.download_button(
            label="📥 Descargar Informe Excel",
            data=buffer.getvalue(),
            file_name=f"informe_{date.today()}.xlsx",
            mime="application/vnd.ms-excel"
        )
    
    with col2:
        if st.button("📧 Enviar por Email"):
            st.info("Sistema de envío preparado (requiere configurar correo).")
else:
    st.info("No hay registros todavía.")
