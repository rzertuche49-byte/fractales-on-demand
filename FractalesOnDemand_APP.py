import streamlit as st
import numpy as np
from PIL import Image
import io
import math

st.set_page_config(layout="wide", page_title="V49 REF EXACTA FIX")
st.title("FRACTALES BAJO DEMANDA - V49 REF EXACTA")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 258)
    zoom = st.slider("ZOOM", 0.2, 4.0, 0.85, 0.05)
    iters = st.slider("CALIDAD", 200, 3000, 1500)
    resolucion = st.selectbox("Resolucion", [1000, 2000, 3000, 4000], index=2)
    ciclos = st.slider("Detalle bandas", 5.0, 40.0, 22.0, 0.5)

def dia_to_c(dia):
    t = dia / 365.0 * 2 * math.pi
    r = 0.05
    cx = -0.065 + r*math.cos(t)
    cy = 0.566 + r*math.sin(t)
    return complex(cx, cy)

c = dia_to_c(dia)
st.caption(f"DIA {dia} -> c = {c.real:.5f} + {c.imag:.5f}i | REF: fucsia/amarillo/turquesa/morado")

def julia_ref(w,h,c,zoom,iters,ciclos):
    x = np.linspace(-1.8/zoom, 1.8/zoom, w)
    y = np.linspace(-1.8/zoom, 1.8/zoom, h)
    X,Y = np.meshgrid(x,y)
    Z = X + 1j*Y
    M = np.full(Z.shape, iters, dtype=float)

    for i in range(iters):
        mask = np.abs(Z) < 1000
        esc = mask & (np.abs(Z) > 2) & (M==iters)
        if np.any(esc):
            M[esc] = i + 1 - np.log2(np.log(np.abs(Z[esc])+1e-10)+1e-10)
        Z[mask] = Z[mask]**2 + c
        if not np.any(mask):
            break

    valid = M < iters
    t = (M[valid] * ciclos * 0.05) % 1.0

    r = (255 * (0.5 + 0.5*np.cos(2*math.pi*(0.90*t + 0.10)))).astype(np.uint8)
    g = (255 * (0.5 + 0.5*np.cos(2*math.pi*(0.70*t + 0.15)))).astype(np.uint8)
    b = (255 * (0.5 + 0.5*np.cos(2*math.pi*(0.85*t + 0.25)))).astype(np.uint8)

    img = np.zeros((h,w,3), dtype=np.uint8)
    img[valid] = np.stack([r,g,b], axis=1)
    img[~valid] = [0,0,0]
    return img

W=900; H=900
img = julia_ref(W,H,c,zoom,iters,ciclos)
st.image(img, use_container_width=True, channels="RGB")

with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_ref(resolucion,resolucion,c,zoom,iters,ciclos)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_REF_DIA{dia}.png",mime="image/png")
