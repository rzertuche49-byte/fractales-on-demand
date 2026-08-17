import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V83 Pro Portfolio")
st.title("FRACTALES V83 - PORTFOLIO PRO")

def hex_to_rgb(h):
    h = h.lstrip('#')
    return [int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)]

PALETAS = {
    "Tu captura": ["#00FFFF","#0064FF","#FF00C8","#FF6400","#FFFF00","#00FF64"],
    "Neon 80s": ["#00FFFF","#FF00FF","#FFFF00","#00FF00","#FF0066","#6600FF"],
    "Cyberpunk": ["#FF003C","#00F0FF","#F0FF00","#FF00F0","#00FF9F","#7000FF"],
    "Toxic": ["#00FF00","#CCFF00","#00FFCC","#FFFF00","#FF00FF","#00FFFF"],
    "Miami Vice": ["#FF6BEC","#3EFFE2","#FFD93D","#FF6B6B","#6BCB77","#4D96FF"],
    "Sunset": ["#F72585","#7209B7","#3A0CA3","#4361EE","#4CC9F0","#FFBE0B"],
    "Oceano": ["#001F54","#034078","#1282A2","#00B4D8","#90E0EF","#CAF0F8"],
    "Pastel": ["#FFB5E8","#B5DEFF","#C3FF99","#FFF5BA","#FFC9DE","#D1BDFF"],
}

with st.sidebar:
    dia = st.slider("DIA", 1, 365, 283)
    zoom = st.slider("ZOOM", 0.2, 5.0, 0.88)
    paleta_nombre = st.selectbox("PALETA BASE", list(PALETAS.keys()), index=0)
    base = PALETAS[paleta_nombre]
    st.write("---")
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
    firma = st.text_input("Firma portafolio", "FRACTALES ON DEMAND © 2026")

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

# MOSTRAR IMAGEN
st.image(out, use_container_width=True)

# ETIQUETA CIENTIFICA PRO
st.markdown(f"""
<div style="background:#111; padding:15px; border-radius:10px; border-left:5px solid {c1}">
<b style="color:white; font-size:18px;">{firma} | JULIA SET - DENDRITE</b><br>
<span style="color:#AAA; font-family:monospace; font-size:13px;">
Fórmula: Z<sub>n+1</sub> = Z<sub>n</sub>² + C &nbsp;|&nbsp; C = {cx:.4f} + {cy:.4f}i &nbsp;|&nbsp; DIA: {dia} &nbsp;|&nbsp; ZOOM: {zoom}x &nbsp;|&nbsp; Iteraciones: 80<br>
Clasificación: Conjunto de Julia Conectado / Escape-Time Fractal / Arte Generativo<br>
Paleta: {paleta_nombre} {colores_actuales}
</span>
</div>
""", unsafe_allow_html=True)

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.info("**¿Qué es?** Un Conjunto de Julia tipo Dendrita. Se genera iterando números complejos. Cada punto de color es cuánto tarda en escapar al infinito.")

buf = io.BytesIO()
Image.fromarray(out).save(buf, format="PNG")

with col2:
    st.download_button("📥 Descargar PNG para cliente (1000x800)", buf.getvalue(), f"fractal_JULIA_C_{cx:.3f}_{cy:.3f}.png", "image/png", type="primary", use_container_width=True)
