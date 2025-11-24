import streamlit as st
from fpdf import FPDF
import os

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Scanner de Marca", page_icon="🚀", layout="centered")

# --- 2. ESTILOS PERSONALIZADOS (CSS - Colores de tu marca) ---
st.markdown("""
    <style>
    /* Títulos H1, H2, H3 en Azul Marino Profundo */
    h1, h2, h3 {
        color: #0A2A43 !important;
    }
    /* Métricas grandes en Azul Marino */
    [data-testid="stMetricValue"] {
        color: #0A2A43 !important;
    }
    /* Botones personalizados (Turquesa con texto blanco) */
    div.stButton > button {
        background-color: #4BB7A1;
        color: white;
        border: none;
        border-radius: 5px;
    }
    div.stButton > button:hover {
        background-color: #3AA690;
        color: white;
    }
    /* Ajuste de color texto en la barra lateral (Arena) */
    [data-testid="stSidebar"] {
        color: #333333;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CARGA DEL LOGO ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)
elif os.path.exists("logo.jpg"):
    st.sidebar.image("logo.jpg", use_container_width=True)
else:
    st.sidebar.header("Tu Empresa")

st.sidebar.markdown("---")
st.sidebar.write("Esta herramienta realiza un diagnóstico 360° de tu presencia digital.")

# --- 4. FUNCIÓN GENERADORA DE PDF ---
def generar_pdf(empresa, puntaje, recomendaciones):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado (Azul Marino)
    pdf.set_text_color(10, 42, 67) 
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"Informe: {empresa}".encode('latin-1', 'replace').decode('latin-1'), ln=1, align='C')
    pdf.ln(5)
    
    # Reset color a negro
    pdf.set_text_color(0, 0, 0)
    
    # Puntaje
    pdf.set_font("Arial", 'B', 12)
    estado = "EXCELENTE" if puntaje > 80 else "BUENO" if puntaje > 50 else "CRITICO"
    pdf.cell(0, 10, txt=f"Puntaje Final: {puntaje}/100 - Estado: {estado}", ln=1, align='L')
    pdf.ln(5)
    
    # Recomendaciones (Título Turquesa)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(75, 183, 161)
    pdf.cell(0, 10, txt="Plan de Accion Recomendado:", ln=1, align='L')
    
    pdf.set_text_color(51, 51, 51)
    pdf.set_font("Arial", size=11)
    for rec in recomendaciones:
        texto = f"- {rec}"
        pdf.multi_cell(0, 8, txt=texto.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(2)
            
    return pdf.output(dest='S').encode('latin-1')

# --- 5. INTERFAZ ---
st.title("🚀 Scanner de Marca 360°")
st.markdown("Diagnóstico profesional de presencia digital e identidad de marca.")

with st.form("audit_form"):
    st.subheader("1. Identidad y Activos")
    col1, col2 = st.columns(2)
    with col1:
        identidad = st.radio("¿Identidad visual definida?", ("Sí, manual completo", "Solo logotipo", "No, uso colores al azar"))
    with col2:
        web = st.selectbox("¿Estado del sitio web?", ("No tengo", "Básico / Informativo", "Tienda Online Optimizada"))

    st.divider()
    st.subheader("2. Estrategia de Contenidos")
    frecuencia = st.select_slider("Frecuencia de publicación", options=["Casi nunca", "1 vez/semana", "2-3 veces/semana", "Diario"])
    calidad = st.slider("Calidad de foto/video (1-10)", 1, 10, 5)
    canales = st.multiselect("Canales activos", ["Instagram", "LinkedIn", "TikTok", "Facebook", "YouTube", "Email Marketing"])

    st.divider()
    st.subheader("3. Inversión y Gestión")
    col3, col4 = st.columns(2)
    with col3:
        inversion = st.radio("Publicidad Pagada (Ads)", ("Nunca", "Esporádica", "Mensual Constante"))
    with col4:
        crm = st.checkbox("¿Usas CRM / Base de Datos?")

    st.markdown("---")
    submitted = st.form_submit_button("📊 Generar Informe Profesional")

# --- 6. RESULTADOS ---
if submitted:
    score = 0
    recomendaciones = []

    # Lógica
    if identidad == "Sí, manual completo": score += 15
    elif identidad == "Solo logotipo": score += 5; recomendaciones.append("Identidad: Define tipografias y colores fijos.")
    else: recomendaciones.append("URGENTE: Crea un manual de identidad visual.")

    if web == "Tienda Online Optimizada": score += 10
    elif web == "Básico / Informativo": score += 5
    else: recomendaciones.append("Web: Necesitas un sitio web para credibilidad.")

    if frecuencia == "Diario": score += 20
    elif frecuencia == "2-3 veces/semana": score += 15
    elif frecuencia == "1 vez/semana": score += 5; recomendaciones.append("Frecuencia: Sube a 3 posts semanales.")
    else: recomendaciones.append("Constancia: Publicar 'casi nunca' mata tu alcance.")

    score += calidad
    if calidad < 6: recomendaciones.append("Contenido: Mejora iluminacion y audio.")

    score += min(len(canales) * 4, 20)
    if len(canales) < 2: recomendaciones.append("Diversificacion: No dependas de una sola red.")

    if inversion == "Mensual Constante": score += 20
    elif inversion == "Esporádica": score += 10
    else: recomendaciones.append("Ads: Invierte mensualmente en publicidad.")

    if crm: score += 5
    else: recomendaciones.append("Gestion: Implementa un CRM.")

    score_final = min(score, 100)
    
    st.divider()
    c1, c2 = st.columns([1,2])
    c1.metric("Puntaje", f"{score_final}/100")
    if score_final >= 80: c2.success("LÍDER DE MERCADO 🏆")
    elif score_final >= 50: c2.warning("EN CRECIMIENTO 🚧")
    else: c2.error("INVISIBLE 👻")
    c2.progress(score_final)

    st.write("### 💡 Hoja de Ruta")
    for rec in recomendaciones: st.info(rec)
    
    pdf_bytes = generar_pdf("Cliente", score_final, recomendaciones)
    st.download_button("📥 Descargar PDF", data=pdf_bytes, file_name="Auditoria.pdf", mime="application/pdf")