import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Scanner Pro", page_icon="📈", layout="centered")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    h1, h2, h3 { color: #0A2A43 !important; }
    [data-testid="stMetricValue"] { color: #0A2A43 !important; }
    div.stButton > button { background-color: #4BB7A1; color: white; border-radius: 5px; border: none; }
    div.stButton > button:hover { background-color: #3AA690; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE LOGO ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)
elif os.path.exists("logo.jpg"):
    st.sidebar.image("logo.jpg", use_container_width=True)

st.sidebar.write("### 📞 Contacto Directo")
st.sidebar.info("¿Dudas con tu resultado? \nEscríbenos al WhatsApp: +56912345678")

# --- FUNCIÓN: GENERAR GRÁFICO PARA EL PDF ---
def crear_grafico_imagen(puntaje_usuario):
    # Datos para comparar
    categorias = ['Tu Marca', 'Promedio Industria', 'Líderes de Mercado']
    valores = [puntaje_usuario, 55, 90] # 55 y 90 son valores de referencia
    colores = ['#4BB7A1', '#E8DCC8', '#0A2A43'] # Tus colores
    
    fig, ax = plt.subplots(figsize=(6, 4))
    barras = ax.bar(categorias, valores, color=colores)
    
    ax.set_ylim(0, 100)
    ax.set_ylabel('Nivel de Madurez Digital')
    ax.set_title('Comparativa de Competitividad', color='#333333', fontweight='bold')
    
    # Poner el valor encima de las barras
    for bar in barras:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}%', ha='center', va='bottom')
    
    # Guardar imagen temporalmente
    nombre_archivo = "temp_chart.png"
    plt.savefig(nombre_archivo, dpi=100, bbox_inches='tight')
    plt.close()
    return nombre_archivo

# --- FUNCIÓN: GENERAR PDF PREMIUM ---
def generar_pdf(datos_cliente, puntaje, recomendaciones, chart_path):
    pdf = FPDF()
    pdf.add_page()
    
    # Borde decorativo (Línea superior Turquesa)
    pdf.set_fill_color(75, 183, 161)
    pdf.rect(0, 0, 210, 15, 'F')
    
    # Título Principal
    pdf.ln(20)
    pdf.set_text_color(10, 42, 67) # Azul Marino
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 10, txt="Informe de Auditoria Digital", ln=1, align='C')
    
    # Datos del Cliente
    pdf.set_font("Arial", '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, txt=f"Empresa: {datos_cliente['empresa']}", ln=1, align='C')
    pdf.cell(0, 5, txt=f"Solicitante: {datos_cliente['nombre']} ({datos_cliente['email']})", ln=1, align='C')
    pdf.cell(0, 5, txt=f"Web analizada: {datos_cliente['web']}", ln=1, align='C')
    pdf.ln(10)

    # El Gráfico Visual (Imagen)
    # Centramos la imagen: (Ancho página 210 - Ancho imagen 100) / 2 = 55
    if os.path.exists(chart_path):
        pdf.image(chart_path, x=55, w=100) 
        pdf.ln(5)
    
    # Puntaje Grande
    pdf.set_text_color(10, 42, 67)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"Tu Calificacion: {puntaje}/100", ln=1, align='C')
    pdf.ln(5)
    
    # Recomendaciones
    pdf.set_fill_color(240, 240, 240) # Fondo gris claro para título
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="  PLAN DE ACCION INMEDIATO:", ln=1, align='L', fill=True)
    pdf.ln(5)
    
    pdf.set_text_color(50, 50, 50)
    pdf.set_font("Arial", size=11)
    for rec in recomendaciones:
        pdf.set_text_color(75, 183, 161) # Bullet point turquesa
        pdf.cell(5, 8, txt=">", align='R')
        pdf.set_text_color(0, 0, 0) # Texto negro
        pdf.multi_cell(0, 8, txt=rec.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(1)
            
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ PRINCIPAL ---
st.title("📈 Diagnóstico de Competitividad Digital")
st.markdown("Descubre qué tan preparada está tu marca frente a la competencia.")

# --- SECCIÓN 1: DATOS DE CONTACTO (LEAD GEN) ---
st.write("### 1. Datos del Negocio")
with st.container():
    col_a, col_b = st.columns(2)
    with col_a:
        nombre = st.text_input("Tu Nombre")
        email = st.text_input("Correo Electrónico")
    with col_b:
        empresa = st.text_input("Nombre de la Empresa")
        telefono = st.text_input("WhatsApp")
    
    web_url = st.text_input("Link de tu Sitio Web (o escribe 'No tengo')")
    rrss_url = st.text_input("Link de tu Red Social principal (Instagram/LinkedIn)")

st.divider()

# --- SECCIÓN 2: EL FORMULARIO ---
with st.form("audit_form"):
    st.write("### 2. Análisis de Estrategia")
    
    # Preguntas rápidas
    identidad = st.radio("Identidad Visual", ("Sí, manual completo", "Solo logotipo", "No tengo identidad definida"))
    frecuencia = st.select_slider("Frecuencia de Posteo", options=["Nunca", "1/mes", "1/semana", "3/semana", "Diario"])
    ads = st.radio("Inversión en Publicidad (Ads)", ("Nunca", "A veces (Botón promocionar)", "Estrategia Mensual (Business Manager)"))
    
    st.write("### 3. Activos Digitales")
    col1, col2 = st.columns(2)
    with col1:
        video = st.checkbox("¿Haces contenido en Video (Reels/TikTok)?")
        email_mkt = st.checkbox("¿Haces Email Marketing?")
    with col2:
        crm = st.checkbox("¿Usas CRM para ventas?")
        pixel = st.checkbox("¿Tienes instalado el Píxel de seguimiento?")

    submitted = st.form_submit_button("🚀 Generar Diagnóstico y Gráficos")

# --- LÓGICA Y RESULTADOS ---
if submitted:
    if not nombre or not email:
        st.error("⚠️ Por favor completa tu nombre y correo para enviarte el informe.")
    else:
        # Puntuación simple (para el ejemplo)
        score = 0
        recs = []
        
        # Lógica resumida
        if identidad == "Sí, manual completo": score += 20
        else: recs.append("Identidad: Tu marca necesita un manual visual para generar confianza premium.")
        
        if frecuencia in ["3/semana", "Diario"]: score += 20
        elif frecuencia == "1/semana": score += 10; recs.append("Frecuencia: Aumenta la intensidad. Una vez a la semana no es suficiente.")
        else: recs.append("Visibilidad: Estás invisible. El algoritmo necesita constancia.")
        
        if ads == "Estrategia Mensual (Business Manager)": score += 20
        elif ads == "A veces (Botón promocionar)": score += 10; recs.append("Ads: Deja de usar el botón 'Promocionar', estás tirando dinero. Usa Business Manager.")
        else: recs.append("Tráfico: Sin publicidad pagada, tu crecimiento será extremadamente lento.")
        
        if video: score += 10
        else: recs.append("Formato: El video corto es el rey hoy en día. Empieza con Reels simples.")
        
        if email_mkt: score += 10
        else: recs.append("Retención: Estás perdiendo ventas por no usar Email Marketing.")
        
        if crm: score += 10
        if pixel: score += 10
        
        score_final = min(score, 100)
        
        # --- VISUALIZACIÓN EN PANTALLA ---
        st.divider()
        st.subheader(f"Resultado para: {empresa}")
        
        # Columnas: Métrica a la izq, Gráfico a la derecha
        col_res1, col_res2 = st.columns([1, 2])
        
        with col_res1:
            st.metric("Puntaje Digital", f"{score_final}/100")
            if score_final < 60:
                st.error("ESTADO: CRÍTICO")
                st.write("Tu competencia te está superando.")
            else:
                st.success("ESTADO: COMPETITIVO")
        
        with col_res2:
            st.write("**Comparativa de Mercado**")
            # Datos para el gráfico de pantalla
            chart_data = pd.DataFrame({
                "Entidad": ["Tu Marca", "Promedio Industria", "Líderes"],
                "Puntaje": [score_final, 55, 90]
            })
            st.bar_chart(chart_data.set_index("Entidad"), color="#4BB7A1")

        # --- GENERACIÓN DE PDF ---
        # 1. Crear imagen del gráfico
        chart_file = crear_grafico_imagen(score_final)
        
        # 2. Empaquetar datos del cliente
        info_cliente = {'nombre': nombre, 'email': email, 'empresa': empresa, 'web': web_url}
        
        # 3. Crear PDF
        pdf_bytes = generar_pdf(info_cliente, score_final, recs, chart_file)
        
        st.success("✅ ¡Diagnóstico completado con éxito!")
        
        st.download_button(
            label="📥 Descargar Informe Profesional (PDF)",
            data=pdf_bytes,
            file_name=f"Auditoria_{empresa}.pdf",
            mime="application/pdf"
        )
        
        # Limpieza (borrar la imagen temporal para no llenar el servidor)
        if os.path.exists(chart_file):
            os.remove(chart_file)
