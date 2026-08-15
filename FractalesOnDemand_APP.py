import streamlit as st
import numpy as np
from PIL import Image
import io
import math
st.set_page_config(layout="wide", page_title="V39 3 ANILLOS FIN")
st.title("FRACTALES BAJO DEMANDA - V39 3 ANILLOS FINAL REF")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 258)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.80, 0.05)
    iters = st.slider("CALIDAD", 200, 2000, 800)
    resolucion = st.selectbox("Resolucion", [1000, 2000, 3000, 4000], index=2)
    grosor = st.slider("Grosor anillos", 0.2, 3.0, 1.2, 0.1)
    brillo = st.slider("Brillo neon", 0.5, 3.0, 2.2, 0.05)

def dia_to_c(dia):
    t = dia / 365.0 * 2 * math.pi
    r = 0.7885
    return complex(r*math.cos(t)*0.8-0.4, r*math.sin(t)*0.6)

c = dia_to_c(dia)
st.caption(f"DIA {dia} -> c = {c.real:.5f} + {c.imag:.5f}i")

def julia_3final(w,h,c,zoom,iters,grosor,brillo):
    x=np.linspace(-3.0/zoom,3.0/zoom,w)
    y=np.linspace(-3.0/zoom,3.0/zoom,h)
    X,Y=np.meshgrid(x,y)
    Z=X+1j*Y
    M=np.full(Z.shape, iters, dtype=float)
    Zabs=np.zeros(Z.shape)
    for i in range(iters):
        mask=np.abs(Z)<=100
        escaped = mask & (np.abs(Z) > 2) & (M==iters)
        M[escaped]=i
        Zabs[escaped]=np.abs(Z[escaped])
        Z[mask]=Z[mask]**2+c

    smooth = M - np.log2(np.log(Zabs+1e-10)+1)
    smooth = np.nan_to_num(smooth, nan=iters)

    img = np.zeros((h,w,3), dtype=np.uint8)

    # SOLO 3 ANILLOS - sin repeticion
    # Anillo 1: 0 a grosor = Fucsia pegado al negro
    # Anillo 2: grosor a 2*grosor = Turquesa
    # Anillo 3: 2*grosor a 3*grosor = Amarillo
    # Resto = Negro

    m1 = (smooth >= 0) & (smooth < grosor)
    m2 = (smooth >= grosor) & (smooth < 2*grosor)
    m3 = (smooth >= 2*grosor) & (smooth < 3*grosor)

    img[m1] = [255,20,147]
    img[m2] = [0,255,255]
    img[m3] = [255,255,0]

    return img

W=900; H=900
img = julia_3final(W,H,c,zoom,iters,grosor,brillo)
st.image(img, use_container_width=True, channels="RGB")
with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_3final(resolucion,resolucion,c,zoom,iters,grosor,brillo)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_FINAL_DIA{dia}.png",mime="image/png")
