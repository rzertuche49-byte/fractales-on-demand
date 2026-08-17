import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V79")
st.title("FRACTALES BAJO DEMANDA - V79 ESTABLE")

def hex_to_rgb(h):
    h=h.lstrip('#')
    return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

PALETAS = {
    "Neon": ["#00FFFF","#FF00FF","#FFFF00","#00FF00","#FF0066","#6600FF"],
    "Pastel": ["#FFB5E8","#B5DEFF","#C3FF99","#FFF5BA","#FFC9DE","#D1BDFF"],
    "Fuego": ["#FF0000","#FF6600","#FFCC00","#FF3300","#CC0000","#FF9900"],
    "Oceano": ["#001F54","#034078","#1282A2","#00B4D8","#90E0EF","#CAF0F8"],
    "Sunset": ["#F72585","#7209B7","#3A0CA3","#4361EE","#4CC9F0","#FFBE0B"],
    "Tu captura": ["#00FFFF","#0064FF","#FF00C8","#FF6400","#FFFF00","#00FF64"],
}

with st.sidebar:
    dia = st.slider("DIA", 1, 365, 283)
    zoom = st.slider("ZOOM", 0.2, 5.0, 0.88, 0.05)
    center_x = st.slider("Centro X", -1.5, 1.5, 0.01)
    center_y = st.slider("Centro Y", -1.5, 1.5, 0.0)
    picos = st.slider("PICOS", 0, 100, 85)

    st.divider()
    nombre = st.selectbox("PALETA", list(PALETAS.keys()), index=5)
    base = PALETAS[nombre]

    c1 = st.color_picker("Color 1", base[0])
    c2 = st.color_picker("Color 2", base[1])
    c3 = st.color_picker("Color 3", base[2])
    c4 = st.color_picker("Color 4", base[3])
    c5 = st.color_picker("Color 5", base[4])
    c6 = st.color_picker("Color 6", base[5])

    st.divider()
    tam = st.slider("Tamaño mancha", 0.1, 3.0, 1.8)
    brillo = st.slider("Brillo", 0.5, 2.0, 1.4)
    ciclos = st.slider("ciclos", 0.5, 4.0, 1.5)
    mezcla = st.slider("Espiral", 0.0, 1.0, 0.22)
    resol = st.selectbox("Export", [2000,3000,4000], index=2)
    suave = st.checkbox("Gama Suave", True)

def dia_to_c(dia, picos):
    t = dia/365*2*math.pi
    r = 0.02 - (picos/100)*0.016
    return complex(-0.75 + r*math.cos(t*3), 0.11 + r*math.sin(t*3))

c_julia = dia_to_c(dia, picos)

def render(w,h):
    x = np.linspace(-1.5/zoom + center_x, 1.5/zoom + center_x, w)
    y = np.linspace(-1.0/zoom + center_y, 1.0/zoom + center_y, h)
    X,Y = np.meshgrid(x,y)
    Z = X+1j*Y
    for _ in range(80):
        Z = Z*Z + c_julia
    ang = np.angle(Z)
    rad = np.log(np.abs(Z)+1)
    fase = ang*mezcla + rad*tam
    s = (fase * ciclos * 0.25) % 1.0

    palette = np.array([hex_to_rgb(c1), hex_to_rgb(c2), hex_to_rgb(c3), hex_to_rgb(c4), hex_to_rgb(c5), hex_to_rgb(c6)], float)

    if suave:
        pos = s*6.0
        i0 = np.floor(pos).astype(int) % 6
        f = pos - np.floor(pos)
        f = 0.5*(1-np.cos(f*np.pi))
        out = np.zeros((h,w,3), float)
        for k in range(6):
            mask = i0==k
            nk = (k+1)%6
            for ch in range(3):
                out[mask,ch] = (1-f[mask])*palette[k,ch] + f[mask]*palette[nk,ch]
    else:
        idx = (s*6).astype(int)%6
        out = np.zeros((h,w,3), float)
        for k in range(6):
            mask = idx==k
            out[mask] = palette[k]

    out = np.clip(out*brillo,0,255).astype(np.uint8)
    return out

img = render(1000,800)
st.image(img, use_container_width=True)

buf = io.BytesIO()
Image.fromarray(render(resol,resol)).save(buf, format="PNG")
st.sidebar.download_button("📥 Descargar PNG", buf.getvalue(), f"fractal_{nombre}_DIA{dia}.png", "image/png", type="primary")
