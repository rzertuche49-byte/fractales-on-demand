import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V81 Paletas")
st.title("FRACTALES V81 - 18 PALETAS")

def hex_to_rgb(h):
    h = h.lstrip('#')
    return [int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)]

PALETAS = {
    "Tu captura": ["#00FFFF","#0064FF","#FF00C8","#FF6400","#FFFF00","#00FF64"],
    "Neon 80s": ["#00FFFF","#FF00FF","#FFFF00","#00FF00","#FF0066","#6600FF"],
    "Fuego": ["#FF0000","#FF6600","#FFCC00","#FF3300","#CC0000","#FF9900"],
    "Oceano Profundo": ["#001F54","#034078","#1282A2","#00B4D8","#90E0EF","#CAF0F8"],
    "Pastel Dream": ["#FFB5E8","#B5DEFF","#C3FF99","#FFF5BA","#FFC9DE","#D1BDFF"],
    "Sunset": ["#F72585","#7209B7","#3A0CA3","#4361EE","#4CC9F0","#FFBE0B"],
    "Galaxy": ["#0B0C10","#1F2833","#45A29E","#66FCF1","#C5C6C7","#9D00FF"],
    "Toxic": ["#00FF00","#CCFF00","#00FFCC","#FFFF00","#FF00FF","#00FFFF"],
    "Candy": ["#FF70A6","#FF9770","#FFD670","#E9FF70","#70FFB2","#70D6FF"],
    "Bosque": ["#0A2F0A","#1B5E20","#2E7D32","#66BB6A","#A5D6A7","#C8E6C9"],
    "Volcan": ["#000000","#4A0000","#8B0000","#FF4500","#FF8C00","#FFD700"],
    "Aurora": ["#03045E","#0077B6","#00B4D8","#90E0EF","#ADE8F4","#CAF0F8"],
    "Miami Vice": ["#FF6BEC","#3EFFE2","#FFD93D","#FF6B6B","#6BCB77","#4D96FF"],
    "Cyberpunk": ["#FF003C","#00F0FF","#F0FF00","#FF00F0","#00FF9F","#7000FF"],
    "Helado": ["#FEC8D8","#FFDFD3","#FFF0B5","#D0F4DE","#A9DEF9","#E4C1F9"],
    "Matrix": ["#000000","#003B00","#008F11","#00FF41","#00FF00","#AAFF00"],
    "Desierto": ["#7F5539","#9C6644","#B08968","#DDB892","#E6CCB2","#EDE0D4"],
    "Joker": ["#3D087B","#5A189A","#7B2CBF","#9D4EDD","#C77DFF","#00F5D4"],
}

with st.sidebar:
    dia = st.slider("DIA", 1, 365, 283)
    zoom = st.slider("ZOOM", 0.2, 5.0, 0.88)
    paleta_nombre = st.selectbox("PALETA 6 COLORES", list(PALETAS.keys()), index=0)
    tam = st.slider("Tamaño", 0.1, 3.0, 1.8)
    brillo = st.slider("Brillo", 0.5, 2.5, 1.4)
    st.divider()
    st.write("💡 Tip: Prueba Neon 80s, Cyberpunk y Toxic para tu diseño")

# Motor fractal
t = dia/365*2*math.pi
c = complex(-0.745 + 0.005*math.cos(t*3), 0.11 + 0.005*math.sin(t*3))

x = np.linspace(-1.5/zoom, 1.5/zoom, 1000)
y = np.linspace(-1.0/zoom, 1.0/zoom, 800)
X,Y = np.meshgrid(x,y)
Z = X+1j*Y
for _ in range(80):
    Z = Z*Z + c

fase = np.angle(Z)*0.22 + np.log(np.abs(Z)+1)*tam
s = (fase*0.375) % 1.0

palette = np.array([hex_to_rgb(c) for c in PALETAS[paleta_nombre]], float)
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
st.image(out, use_container_width=True, caption=f"Paleta: {paleta_nombre}")

buf = io.BytesIO()
Image.fromarray(out).save(buf, format="PNG")
st.sidebar.download_button("📥 Descargar PNG 1000x800", buf.getvalue(), f"fractal_{paleta_nombre}.png", "image/png", type="primary")
