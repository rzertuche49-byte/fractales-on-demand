import streamlit as st
import numpy as np
from PIL import Image
import io
import math
st.set_page_config(layout="wide", page_title="V42 FIX NEGRO")
st.title("FRACTALES BAJO DEMANDA - V42 FIX NEGRO - DENTADO + ORDEN")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 258)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.35, 0.05)
    iters = st.slider("CALIDAD", 200, 2000, 1000)
    resolucion = st.selectbox("Resolucion", [1000, 2000, 3000, 4000], index=2)
    grosor = st.slider("Grosor anillos", 0.1, 3.0, 0.60, 0.05)
    detalle = st.slider("Detalle fractal", 0.5, 4.0, 2.2, 0.1)

def dia_to_c(dia):
    # FORMULA V40 QUE SI FUNCIONABA - no la del V41
    t = dia / 365.0 * 2 * math.pi
    r = 0.7885
    cx = r * math.cos(t) * 0.8 - 0.4
    cy = r * math.sin(t) * 0.6
    return complex(cx, cy)

c = dia_to_c(dia)
st.caption(f"DIA {dia} -> c = {c.real:.5f} + {c.imag:.5f}i | Negro -> Fucsia -> Turquesa -> Amarillo")

def julia_fix(w,h,c,zoom,iters,grosor,detalle):
    x=np.linspace(-3.0/zoom,3.0/zoom,w)
    y=np.linspace(-3.0/zoom,3.0/zoom,h)
    X,Y=np.meshgrid(x,y)
    Z=X+1j*Y
    M=np.full(Z.shape, iters, dtype=float)
    for i in range(iters):
        mask = np.abs(Z) <= 100
        escaped = mask & (np.abs(Z) > 2) & (M == iters)
        # smooth iteration
        M[escaped] = i - np.log2(np.log(np.abs(Z[escaped])+1e-10)+1) + 1
        Z[mask] = Z[mask]**2 + c

    smooth = M
    img = np.zeros((h,w,3), dtype=np.uint8)

    # Solo puntos que escaparon
    valid = smooth < iters
    if not np.any(valid):
        return img

    max_escape = np.max(smooth[valid])
    # Distancia desde el borde hacia afuera
    d = (max_escape - smooth) * detalle * 0.5
    d = np.clip(d, 0, 100)

    m_fucsia = valid & (d >= 0) & (d < grosor)
    m_turquesa = valid & (d >= grosor) & (d < 2*grosor)
    m_amarillo = valid & (d >= 2*grosor) & (d < 3*grosor)

    img[m_fucsia] = [255,20,147]
    img[m_turquesa] = [0,255,255]
    img[m_amarillo] = [255,255,0]
    return img

W=900; H=900
img = julia_fix(W,H,c,zoom,iters,grosor,detalle)
st.image(img, use_container_width=True, channels="RGB")
with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_fix(resolucion,resolucion,c,zoom,iters,grosor,detalle)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_V42_DIA{dia}.png",mime="image/png")
