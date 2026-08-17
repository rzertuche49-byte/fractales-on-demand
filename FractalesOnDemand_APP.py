import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide")
st.title("FRACTALES V80 - ESTABLE")

def hex_to_rgb(h):
    h = h.lstrip('#')
    return [int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)]

PALETAS = {
    "Tu captura": ["#00FFFF","#0064FF","#FF00C8","#FF6400","#FFFF00","#00FF64"],
    "Fuego": ["#FF0000","#FF6600","#FFCC00","#FF3300","#CC0000","#FF9900"],
    "Pastel": ["#FFB5E8","#B5DEFF","#C3FF99","#FFF5BA","#FFC9DE","#D1BDFF"],
    "Oceano": ["#001F54","#034078","#1282A2","#00B4D8","#90E0EF","#CAF0F8"],
    "Neon": ["#00FFFF","#FF00FF","#FFFF00","#00FF00","#FF0066","#6600FF"],
}

with st.sidebar:
    dia = st.slider("DIA", 1, 365, 283)
    zoom = st.slider("ZOOM", 0.2, 5.0, 0.88)
    paleta = st.selectbox("PALETA 6 COLORES", list(PALETAS.keys()), index=0)
    tam = st.slider("Tamano", 0.1, 3.0, 1.8)
    brillo = st.slider("Brillo", 0.5, 2.0, 1.4)

t = dia/365*2*math.pi
c = complex(-0.745 + 0.005*math.cos(t*3), 0.11 + 0.005*math.sin(t*3))

x = np.linspace(-1.5/zoom, 1.5/zoom, 900)
y = np.linspace(-1.0/zoom, 1.0/zoom, 700)
X,Y = np.meshgrid(x,y)
Z = X+1j*Y
for _ in range(80):
    Z = Z*Z + c

fase = np.angle(Z)*0.22 + np.log(np.abs(Z)+1)*tam
s = (fase*0.375) % 1.0

palette = np.array([hex_to_rgb(c) for c in PALETAS[paleta]], float)
pos = s*6.0
i0 = np.floor(pos).astype(int) % 6
f = pos - np.floor(pos)
f = 0.5*(1-np.cos(f*np.pi))

out = np.zeros((700,900,3), float)
for k in range(6):
    m = i0==k
    nk = (k+1)%6
    out[m,0] = (1-f[m])*palette[k,0] + f[m]*palette[nk,0]
    out[m,1] = (1-f[m])*palette[k,1] + f[m]*palette[nk,1]
    out[m,2] = (1-f[m])*palette[k,2] + f[m]*palette[nk,2]

out = np.clip(out*brillo,0,255).astype(np.uint8)
st.image(out, use_container_width=True)

buf = io.BytesIO()
Image.fromarray(out).save(buf, format="PNG")
st.download_button("📥 Descargar PNG", buf.getvalue(), "fractal.png", "image/png")
