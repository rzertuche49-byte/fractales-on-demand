import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V84 Transparente")
st.title("FRACTALES V84 - TRANSPARENTE PARA IMPRESION")

def hex_to_rgb(h):
    h = h.lstrip('#')
    return [int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)]

PALETAS = {
    "Tu captura": ["#00FFFF","#0064FF","#FF00C8","#FF6400","#FFFF00","#00FF64"],
    "Neon 80s": ["#00FFFF","#FF00FF","#FFFF00","#00FF00","#FF0066","#6600FF"],
    "Cyberpunk": ["#FF003C","#00F0FF","#F0FF00","#FF00F0","#00FF9F","#7000FF"],
    "Toxic": ["#00FF00","#CCFF00","#00FFCC","#FFFF00","#FF00FF","#00FFFF"],
    "Miami Vice": ["#FF6BEC","#3EFFE2","#FFD93D","#FF6B6B","#6BCB77","#4D96FF"],
}

with st.sidebar:
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

    st.divider()
    tam = st.slider("Tamaño mancha", 0.1, 3.0, 1.8)
    brillo = st.slider("Brillo", 0.5, 2.5, 1.4)

    st.divider()
    st.write("🖨️ **MODO IMPRESION**")
    fondo_transparente = st.checkbox("Fondo transparente PNG", value=False)
    umbral = st.slider("Limpieza fondo", 0.0, 5.0, 1.0, help="Sube si quieres que quite mas fondo negro")

# Motor fractal
t = dia/365*2*math.pi
cx = -0.745 + 0.005*math.cos(t*3)
cy = 0.11 + 0.005*math.sin(t*3)
c = complex(cx, cy)

x = np.linspace(-1.5/zoom, 1.5/zoom, 1000)
y = np.linspace(-1.0/zoom, 1.0/zoom, 800)
X,Y = np.meshgrid(x,y)
Z = X+1j*Y

# Guardamos magnitud final para mascara
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

# CREAR ALPHA PARA TRANSPARENCIA
# Donde el fractal es casi negro o muy poco brillante, lo hacemos transparente
magnitud = np.abs(Z)
# Si magnitud > 4 es fondo, si < 4 es fractal
brillo_pixel = out.mean(axis=2) # 0-255

if fondo_transparente:
    # Alpha: 0 transparente, 255 solido
    alpha = np.where((magnitud < 4) & (brillo_pixel > (10 + umbral*10)), 255, 0).astype(np.uint8)
    # Suavizado de borde
    out_rgba = np.dstack((out, alpha))
    img_final = Image.fromarray(out_rgba, "RGBA")
    st.image(out_rgba, use_container_width=True, caption="MODO TRANSPARENTE - Fondo eliminado")
else:
    img_final = Image.fromarray(out, "RGB")
    st.image(out, use_container_width=True)

# Etiqueta
