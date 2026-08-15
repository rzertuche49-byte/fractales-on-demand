import streamlit as st
import numpy as np
from PIL import Image
import io
import math
st.set_page_config(layout="wide", page_title="V48 REF EXACTA")
st.title("FRACTALES BAJO DEMANDA - V48 REF EXACTA")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 258)
    zoom = st.slider("ZOOM", 0.2, 4.0, 0.85, 0.05)
    iters = st.slider("CALIDAD", 200, 3000, 1500)
    resolucion = st.selectbox("Resolucion", [1000, 2000, 3000, 4000], index=2)
    ciclos = st.slider("Detalle bandas", 5.0, 40.0, 22.0, 0.5)

def dia_to_c(dia):
    t = dia / 365.0 * 2 * math.pi
    # c de tu ref: -0.065 + 0.56 es bueno, lo hacemos orbitar ahi
    r = 0.05
    cx = -0.065 + r*math.cos(t)
    cy = 0.566 + r*math.sin(t)
    return complex(cx, cy)

c = dia_to_c(dia)
st.caption(f"DIA {dia} -> c = {c.real:.5f} + {c.imag:.5f}i | REF: fucsia/amarillo/turquesa/morado")

def palette(t):
    # Paleta Inigo Quilez ajustada a tus colores
    # a + b * cos(2pi*(c*t + d))
    # Truco para sacar fucsia->amarillo->turquesa->morado
    a = np.array([0.5, 0.5, 0.5])
    b = np.array([0.5, 0.5, 0.5])
    c_ = np.array([0.90, 0.70, 0.85])
    d = np.array([0.10, 0.15, 0.25])
    return a + b * np.cos(2*math.pi*(c_[:,None]*t + d[:,None]))

def julia_ref(w,h,c,zoom,iters,ciclos):
    x = np.linspace(-1.8/zoom, 1.8/zoom, w)
    y = np.linspace(-1.8/zoom, 1.8/zoom, h)
    X,Y = np.meshgrid(x,y)
    Z = X + 1j*Y
    M = np.full(Z.shape, iters, dtype=float)
    for i in range(iters):
        mask = np.abs(Z) < 1000
        esc = mask & (np.abs(Z) > 2) & (M==iters)
        M[esc] = i - math.log2(math.log(abs(Z[esc]).max()+2.718)) + 1
        # smooth individual
        M[esc] = i + 1 - np.log2(np.log(np.abs(Z[esc])+1e-10)+1)
        Z[mask] = Z[mask]**2 + c

    valid = M < iters
    # Normaliza y cicla muchas veces
    smooth = M
    # t con muchos ciclos = bandas delgadas como tu ref
    t = (smooth[valid] * ciclos * 0.05) % 1.0

    # Paleta
    r = (255 * (0.5 + 0.5*np.cos(2*math.pi*(0.9*t + 0.10)))).astype(int)
    g = (255 * (0.5 + 0.5*np.cos(2*math.pi*(0.7*t + 0.15)))).astype(int)
    b = (255 * (0.5 + 0.5*np.cos(2*math.pi*(0.85*t + 0.25)))).astype(int)

    # Empuja a fucsia/amarillo/turquesa/morado neón
    r = np.clip(r*1.1 + 20*np.sin(t*30), 0,255)
    g = np.clip(g*0.95 + 10*np.sin(t*25+1), 0,255)
    b = np.clip(b*1.25, 0,255)

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
