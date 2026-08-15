import streamlit as st
import numpy as np
from PIL import Image
import io
import math
st.set_page_config(layout="wide", page_title="V36 3 ANILLOS")
st.title("FRACTALES BAJO DEMANDA - V36 3 ANILLOS NEON REAL")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 258)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.80, 0.05)
    iters = st.slider("CALIDAD", 200, 2000, 800)
    resolucion = st.selectbox("Resolucion", [1000, 2000, 3000, 4000], index=2)
    grosor = st.slider("Grosor anillos", 1.0, 10.0, 4.0, 0.5)
    brillo = st.slider("Brillo neon", 0.5, 3.0, 2.2, 0.05)

def dia_to_c(dia):
    t = dia / 365.0 * 2 * math.pi
    r = 0.7885
    return complex(r*math.cos(t)*0.8-0.4, r*math.sin(t)*0.6)

c = dia_to_c(dia)
st.caption(f"DIA {dia} -> c = {c.real:.5f} + {c.imag:.5f}i")

def julia_3anillos(w,h,c,zoom,iters,grosor,brillo):
    x=np.linspace(-3.0/zoom,3.0/zoom,w)
    y=np.linspace(-3.0/zoom,3.0/zoom,h)
    X,Y=np.meshgrid(x,y)
    Z=X+1j*Y
    M=np.zeros(Z.shape)
    for i in range(iters):
        mask=np.abs(Z)<=10
        if not np.any(mask): break
        Z[mask]=Z[mask]**2+c
        M[mask]=i

    # Solo anillos cerca del borde (2 a 2+grosor*3)
    img = np.zeros((h,w,3), dtype=np.uint8)

    # 3 anillos gordos - cada uno de grosor
    # Anillo 1 = Fucsia, Anillo 2 = Turquesa, Anillo 3 = Amarillo
    a1_min, a1_max = 2, 2+grosor
    a2_min, a2_max = a1_max, a1_max+grosor
    a3_min, a3_max = a2_max, a2_max+grosor

    m1 = (M >= a1_min) & (M < a1_max)
    m2 = (M >= a2_min) & (M < a2_max)
    m3 = (M >= a3_min) & (M < a3_max)

    img[m1] = [255,20,147]
    img[m2] = [0,255,255]
    img[m3] = [255,255,0]

    # interior y exterior lejano = negro
    return img

W=900; H=900
img = julia_3anillos(W,H,c,zoom,iters,grosor,brillo)
st.image(img, use_container_width=True, channels="RGB")
with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_3anillos(resolucion,resolucion,c,zoom,iters,grosor,brillo)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_3ANILLOS_DIA{dia}.png",mime="image/png")
