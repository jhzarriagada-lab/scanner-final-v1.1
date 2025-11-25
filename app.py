import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import unicodedata

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Scanner Digital", page_icon="🚀", layout="centered")

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    h1, h2, h3 { color: #0A2A43 !important; }
    div.stButton > button { background-color: #4BB7A1; color: white; border: none; border-radius: 5px; }
    div.stButton > button:hover { background-color: #3AA690; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE LOGO EN LA APP ---
if os.path.exists("logo.png"): st.sidebar.image("logo.png", use_container_width=True)
elif os.path.exists("logo.jpg"): st.sidebar.image("logo.jpg", use_container_width=True)

st.sidebar.write("### ⏱️ Test Rápido")
st.sidebar.info("Diagnóstico simple para entender tu negocio.")

# --- FUNCIÓN DE LIMPIEZA ---
def limpiar_texto(texto):
    if not isinstance(texto, str):
        texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto.encode('latin-1', 'replace').decode('latin-1')

# --- FUNCIÓN: GUARDAR EN GOOGLE SHEETS ---
def guardar_en_sheets(datos):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("Base de Datos Scanner").sheet1
        
        fila = [
            str(datetime.now()),
            datos['nombre'],
            datos['empresa'],
            datos['email'],
            datos['whatsapp'],
            datos['web'],
            datos['puntaje']
        ]
        sheet.append_row(fila)
        return True
    except Exception as e:
        return False

# --- FUNCIÓN GRÁFICO ---
def crear_grafico_comparativo(puntajes_usuario):
    categorias = list(puntajes_usuario.keys())
    valores_usuario = list(puntajes_usuario.values())
    valores_mercado = [12, 10, 8, 5, 5] 
    
    x = np.arange(len(categorias))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width/2, valores_usuario, width, label='Tu Negocio', color='#0A2A43')
    ax.bar(x + width/2, valores_mercado, width, label='Promedio de otros', color='#CCCCCC')
    
    ax.set_ylabel('Puntaje')
    ax.set_title('Comparativa Simple', fontweight='bold', color='#333333')
    ax.set_xticks(x)
    ax.set_xticklabels(categorias)
    ax.legend()
    ax.set_ylim(0, 22)
    
    plt.tight_layout()
    nombre = "temp_chart.png"
    plt.savefig(nombre, dpi=100)
    plt.close()
    return nombre

# --- FUNCIÓN PDF (LOGO ABAJO A LA DERECHA) ---
def generar_pdf(cliente, score_total, recs, chart_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    
    # Espacio inicial
    pdf.ln(10)

    # 1. TÍTULO
    pdf.set_font("Arial", 'B', 22)
    pdf.set_text_color(10, 42, 67)
    pdf.cell(0, 10, txt="Informe de Estado Digital", ln=1, align='C')
    
    # 2. DATOS DEL CLIENTE
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(100, 100, 100)
    
    txt_empresa = limpiar_texto(f"Empresa: {cliente['empresa']}")
    txt_cliente = limpiar_texto(f"Preparado para: {cliente['nombre']}")
    
    pdf.cell(0, 6, txt=txt_empresa, ln=1, align='C')
    pdf.cell(0, 6, txt=txt_cliente, ln=1, align='C')
    pdf.ln(10) # Un poco más de espacio antes del gráfico

    # 3. GRÁFICO
    if os.path.exists(chart_path):
        pdf.image(chart_path, x=30, w=150)
        pdf.ln(10)

    # 4. PUNTAJE
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(10, 42, 67)
    pdf.cell(0, 10, txt=f"Tu Calificacion Final: {score_total}/100", ln=1, align='C')
    pdf.ln(10)
    
    # 5. RECOMENDACIONES
    pdf.set_fill_color(75, 183, 161)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="CONSEJOS PERSONALIZADOS", ln=1, align='C', fill=True)
    pdf.ln(8)
    
    pdf.set_font("Arial", size=11)
    pdf.set_text_color(50, 50, 50)
    
    for rec in recs:
        pdf.set_text_color(75, 183, 161)
        pdf.cell(8, 8, txt=">", align='C')
        pdf.set_text_color(0, 0, 0)
        
        txt_rec = limpiar_texto(rec)
        pdf.multi_cell(0, 8, txt=txt_rec)
        pdf.ln(2)

    # 6. LOGO AL FINAL (Abajo Derecha)
    # A4 mide 210x297mm. 
    # X=160 deja 20mm de margen derecho aprox (si el logo mide 30 de ancho).
    # Y=255 lo pone abajo pero deja espacio si la hoja se llena mucho.
    if os.path.exists("logo.png"):
        pdf.image("logo.png", x=160, y=255, w=30)
    elif os.path.exists("logo.jpg"):
        pdf.image("logo.jpg", x=160, y=255, w=30)
            
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.title("🚀 ¿Qué tan digital es tu negocio?")
st.markdown("Responde estas preguntas sencillas para recibir un informe gratuito.")

with st.expander("📝 Ingresa tus datos para recibir el informe", expanded=True):
    col_a, col_b = st.columns(2)
    nombre = col_a.text_input("Tu Nombre")
    empresa = col_b.text_input("Nombre de tu Negocio")
    col_c, col_d = st.columns(2)
    email = col_c.text_input("Correo Electrónico")
    whatsapp = col_d.text_input("WhatsApp / Teléfono (Opcional)")
    web_input = st.text_input("Sitio Web actual (Si tienes)")

with st.form("audit_simple"):
    st.subheader("1. Tu Imagen")
    p1 = st.radio("¿Tienes un logotipo oficial?", 
                  ["Sí, tengo logo, colores y tipos de letra definidos", 
                   "Solo tengo el logo", 
                   "No, uso cualquier imagen o color"])
    p2 = st.selectbox("Si alguien entra a tu perfil, ¿entiende rápido qué vendes?", 
                      ["Sí, en menos de 3 segundos", "Es un poco confuso", "No estoy seguro"])
    st.divider()
    st.subheader("2. Tu presencia en Internet")
    p3 = st.radio("¿Tienes página web?", 
                  ["Sí, una página profesional (o tienda online)", 
                   "Una página básica o Linktree (lista de enlaces)", 
                   "No, solo uso redes sociales"])
    p4 = st.checkbox("¿Si busco tu negocio en Google Maps, apareces?")
    st.divider()
    st.subheader("3. Tus Publicaciones")
    p5 = st.select_slider("¿Cada cuánto publicas en redes?", 
                          options=["Nunca", "1 vez al mes", "1 vez por semana", "2-3 veces por semana", "Casi todos los días"])
    p6 = st.radio("¿Subes videos cortos (tipo Reels o TikTok)?", 
                  ["Sí, es lo que más hago", "A veces", "Nunca, solo subo fotos"])
    p7 = st.radio("¿Muestras personas (tu equipo o tú) en las fotos?", 
                  ["Sí, nos gusta salir en cámara", "Solo mostramos los productos"])
    st.divider()
    st.subheader("4. Publicidad y Clientes")
    p8 = st.radio("¿Pagas publicidad para que te vea más gente?", 
                  ["Sí, hago campañas avanzadas todos los meses", 
                   "A veces uso el botón azul de 'Promocionar'", 
                   "No, solo publico gratis (orgánico)"])
    p10 = st.radio("¿Dónde anotas a los clientes que te preguntan o compran?", 
                   ["En un sistema especial (CRM) o Email Marketing", 
                    "En un Excel o cuaderno ordenado", 
                    "No los anoto, quedan en el chat"])
    st.divider()
    st.subheader("5. Atención")
    p11 = st.select_slider("¿Qué tan rápido respondes los mensajes?", 
                           options=["Tardo más de un día", "Durante el día", "Casi al instante"])
    st.markdown("---")
    submitted = st.form_submit_button("📊 Ver mis resultados")

# --- LÓGICA ---
if submitted:
    if not nombre or not email:
        st.error("⚠️ Por favor escribe tu nombre y correo arriba.")
    else:
        s_brand = 0; s_web = 0; s_cont = 0; s_ads = 0; s_ventas = 0
        recs = []
        if "definidos" in p1: s_brand += 10
        elif "Solo tengo el logo" in p1: s_brand += 5; recs.append("Imagen: Solo el logo no basta. Define tus colores oficiales.")
        else: recs.append("Imagen: Tu marca se ve desordenada. Define una identidad básica.")
        if "3 segundos" in p2: s_brand += 10
        else: recs.append("Mensaje: Tu perfil es confuso. Escribe claramente qué vendes en tu biografía.")
        if "profesional" in p3: s_web += 15
        elif "básica" in p3: s_web += 5; recs.append("Web: Estás listo para pasar de una página básica a una web profesional.")
        else: recs.append("Web: Depender solo de Instagram es peligroso. Crea una web propia.")
        if p4: s_web += 5
        else: recs.append("Google: ¡Es gratis aparecer en el mapa! Registra tu negocio hoy mismo.")
        if p5 == "Casi todos los días": s_cont += 8
        elif "2-3 veces" in p5: s_cont += 5
        else: recs.append("Constancia: Publicar poco hace que las redes te oculten.")
        if "más hago" in p6: s_cont += 7
        elif "A veces" in p6: s_cont += 3
        else: recs.append("Video: Las fotos ya no tienen alcance. Sube al menos un video (Reel) a la semana.")
        if "nos gusta salir" in p7: s_cont += 5
        else: recs.append("Confianza: La gente compra a personas. Muestra al equipo en cámara.")
        if "campañas avanzadas" in p8: s_ads += 20
        elif "botón azul" in p8: s_ads += 10; recs.append("Publicidad: El botón 'Promocionar' es caro. Usa el Administrador de Anuncios.")
        else: s_ads += 0; recs.append("Tráfico: Es muy difícil crecer gratis. Invierte un poco en publicidad.")
        if "sistema especial" in p10: s_ventas += 10
        elif "Excel" in p10: s_ventas += 5; recs.append("Datos: El cuaderno se pierde. Pasa tus contactos a un Excel.")
        else: recs.append("Clientes: Estás perdiendo dinero al no guardar los contactos.")
        if "instante" in p11: s_ventas += 10
        elif "Durante el día" in p11: s_ventas += 5
        else: recs.append("Atención: Responder tarde enfría la venta. Sé más veloz.")
        
        score_total = min(s_brand + s_web + s_cont + s_ads + s_ventas, 100)
        
        datos_sheet = {'nombre': nombre, 'empresa': empresa, 'email': email, 'whatsapp': whatsapp, 'web': web_input, 'puntaje': score_total}
        guardar_en_sheets(datos_sheet)
        
        dict_puntajes = {"Imagen": s_brand, "Web": s_web, "Contenido": s_cont, "Publicidad": s_ads, "Ventas": s_ventas}
        
        st.divider()
        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Tu Nota Digital", f"{score_total}/100")
            if score_total < 50: st.error("Hay mucho por mejorar")
            else: st.success("Vas por buen camino")
        with c2:
            chart_file = crear_grafico_comparativo(dict_puntajes)
            st.image(chart_file)
            
        cliente_data = {'nombre': nombre, 'empresa': empresa}
        pdf_bytes = generar_pdf(cliente_data, score_total, recs, chart_file)
        
        st.download_button("📥 Bajar mi Informe (PDF)", data=pdf_bytes, file_name="Mi_Diagnostico.pdf", mime="application/pdf")
        if os.path.exists(chart_file): os.remove(chart_file)
