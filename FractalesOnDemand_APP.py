import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V86 Personalizado")

PALETAS = {
    "Tu captura": ["#00FFFF","#0064FF","#FF00C8","#FF6400","#FFFF00","#00FF64"],
    "Neon 80s": ["#00FFFF","#FF00FF","#FFFF00","#00FF00","#FF0066","#6600FF"],
    "Cyberpunk": ["#FF003C","#00F0FF","#F0FF00","#FF00F0","#00FF9F","#7000FF"],
    "Toxic": ["#00FF00","#CCFF00","#00FFCC","#FFFF00","#FF00FF","#00FFFF"],
    "Miami Vice": ["#FF6BEC","#3EFFE2","#FFD93D","#FF6B6B","#6BCB77","#4D96FF"],
}

def hex_to_rgb(h):
    h = h.lstrip('#')
    return [int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)]

with st.sidebar:
    st.write("👤 **PERSONALIZACIÓN CLIENTE**")
    nombre_cliente = st.text_input("Nombre del cliente / proyecto", "FRACTALES ON DEMAND")
    firma = st.text_input("Firma portafolio", "© 2026")

    st.divider()
    dia = st.slider("DIA", 1, 365, 283)
    zoom = st.slider("ZOOM", 0.2, 5.0, 0.88)
    paleta_nombre = st.selectbox("PALETA BASE", list(PALETAS.keys()), index=0)
    base = PALETAS[paleta_nombre]
    st.write("**EDITA 6 COLORES**")
    c1 = st.color_picker("Color 1", base[0])
    c2 = st.color_picker("Color 2", base[1])
    c3 = st.color_picker("Color 3", base[2])
    c4 = st.color_picker("Color 4", base[3])
    c5 = st.color_picker("Color 5", base[4])
    c6 = st.color_picker("Color 6", base[5])
    colores_actuales = [c1,c2,c3,c4,c5,c6]
    st.write("---")
    tam = st.slider("Tamaño mancha", 0.1, 3.0, 1.8)
    brillo = st.slider("Brillo", 0.5, 2.5, 1.4)
    st.divider()
    fondo_transparente = st.checkbox("Fondo transparente PNG", value=False)
    umbral = st.slider("Limpieza fondo", 0.0, 5.0, 1.0)

# TITULO DINAMICO CON NOMBRE DEL CLIENTE
st.title(f"{nombre_cliente} - JULIA SET")
st.caption(f"Proyecto personalizado para {nombre_cliente}")

# Motor fractal
t = dia/365*2*math.pi
cx = -0.745 + 0.005*math.cos(t*3)
cy = 0.11 + 0.005*math.sin(t*3)
c = complex(cx, cy)
x = np.linspace(-1.5/zoom, 1.5/zoom, 1000)
y = np.linspace(-1.0/zoom, 1.0/zoom, 800)
X,Y = np.meshgrid(x,y)
Z = X+1j*Y
for _ in range(80):
    Z = Z*Z + c
fase = np.angle(Z)*0.22 + np.log(np.abs(Z)+1)*tam
s = (fase*0.375) % 1.0
palette = np.array([hex_to_rgb(c) for c in colores_actuales], float)
pos = s*6.0
i0 = np.floor(pos).astype(int) % 6
f = pos - np.floor(pos)
f = 0.5*(1-np.cos(f*np.pi))
out = np.zeros((800,1000,3), float)
for k in range(6):
    m = i0==k
    nk = (k+1)%6
    out[m,0] = (1-f[m])*palette[k,0] + f[m]*palette[nk,0]
    out[m,1] = (1-f[m])*palette[k,1] + f[m]*palette[nk,1]
    out[m,2] = (1-f[m])*palette[k,2] + f[m]*palette[nk,2]
out = np.clip(out*brillo,0,255).astype(np.uint8)

magnitud = np.abs(Z)
brillo_pixel = out.mean(axis=2)
if fondo_transparente:
    alpha = np.where((magnitud < 4) & (brillo_pixel > (10 + umbral*10)), 255, 0).astype(np.uint8)
    out_rgba = np.dstack((out, alpha))
    img_final = Image.fromarray(out_rgba, "RGBA")
    st.image(out_rgba, use_container_width=True)
else:
    img_final = Image.fromarray(out, "RGB")
    st.image(out, use_container_width=True)

st.markdown(f"""
<div style="background:#111; padding:15px; border-radius:10px; border-left:5px solid {c1}">
<b style="color:white; font-size:18px;">{nombre_cliente} | {firma} | JULIA SET - DENDRITE</b><br>
<span style="color:#AAA; font-family:monospace; font-size:13px;">
Fórmula: Z(n+1) = Z(n)² + C | C = {cx:.4f} + {cy:.4f}i | DIA: {dia} | ZOOM: {zoom}x<br>
Paleta: {paleta_nombre} | Modo: {'TRANSPARENTE' if fondo_transparente else 'SOLIDO'}
</span>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.success(f"Listo para entregar a: {nombre_cliente}")
with col2:
    buf = io.BytesIO()
    img_final.save(buf, format="PNG")
    st.download_button(f"📥 Descargar para {nombre_cliente}", buf.getvalue(), f"fractal_{nombre_cliente.replace(' ','_')}.png", "image/png", type="primary", use_container_width=True)
