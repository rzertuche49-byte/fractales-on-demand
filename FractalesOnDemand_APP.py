import streamlit as st
import numpy as np
from PIL import Image
import io
import math
st.set_page_config(layout="wide", page_title="V38 DENTADO REAL")
st.title("FRACTALES BAJO DEMANDA - V38 3 ANILLOS DENTADOS REF")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 258)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.80, 0.05)
    iters = st.slider("CALIDAD", 200, 2000, 800)
    resolucion = st.selectbox("Resolucion", [1000, 2000, 3000, 4000], index=2)
    grosor = st.slider("Grosor anillos", 0.1, 2.0, 0.5, 0.05)
    brillo = st.slider("Brillo neon", 0.5, 3.0, 2.2, 0.05)

def dia_to_c(dia):
    t = dia / 365.0 * 2 * math.pi
    r = 0.7885
    return complex(r*math.cos(t)*0.8-0.4, r*math.sin(t)*0.6)

c = dia_to_c(dia)
st.caption(f"DIA {dia} -> c = {c.real:.5f} + {c.imag:.5f}i")

def julia_dentado(w,h,c,zoom,iters,grosor,brillo):
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
        if not np.any(mask): break

    # Suavizado real - esto hace que siga el borde fractal
    smooth = M - np.log2(np.log(Zabs+1e-10)+1)
    smooth = np.nan_to_num(smooth, nan=iters, neginf=iters)

    img = np.zeros((h,w,3), dtype=np.uint8)

    # Solo cerca del conjunto: entre iter 0 y 8
    mask_borde = (M >=0) & (M < 15) & (smooth < 20)

    # 3 anillos que siguen la forma - divide smooth
    # Cada anillo = grosor iteraciones
    bands = np.floor(smooth / grosor) % 3

    m1 = mask_borde & (bands == 0)
    m2 = mask_borde & (bands == 1)
    m3 = mask_borde & (bands == 2)

    img[m1] = [255,20,147] # fucsia pegado al negro
    img[m2] = [0,255,255] # turquesa en medio
    img[m3] = [255,255,0] # amarillo afuera

    return img

W=900; H=900
img = julia_dentado(W,H,c,zoom,iters,grosor,brillo)
st.image(img, use_container_width=True, channels="RGB")
with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_dentado(resolucion,resolucion,c,zoom,iters,grosor,brillo)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_DENTADO_DIA{dia}.png",mime="image/png")
