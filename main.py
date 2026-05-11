import streamlit as st

# Configuración de la página (opcional pero recomendada)
st.set_page_config(page_title="Seguimiento de Obra - Masaveu", layout="wide")

# Título principal
st.title("🏗️ Seguimiento de Obra - Masaveu")

# Ejemplo de estructura básica
st.sidebar.header("Opciones")
opcion = st.sidebar.selectbox("Selecciona una sección", ["Resumen", "Fotos", "Presupuesto"])

if opcion == "Resumen":
    st.subheader("Estado Actual del Proyecto")
    st.write("Aquí puedes añadir los detalles de la obra.")
    
elif opcion == "Fotos":
    st.subheader("Galería de Avances")
    st.info("Sube las imágenes de la semana aquí.")

else:
    st.subheader("Control de Gastos")
    st.write("Tabla de presupuesto y materiales.")

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
