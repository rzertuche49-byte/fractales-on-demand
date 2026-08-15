import streamlit as st
import numpy as np
from PIL import Image
import io
import math
st.set_page_config(layout="wide", page_title="V40 ORDEN CORRECTO")
st.title("FRACTALES BAJO DEMANDA - V40 ORDEN CORRECTO - FUCSIA DENTRO")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 258)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.25, 0.05)
    iters = st.slider("CALIDAD", 200, 2000, 800)
    resolucion = st.selectbox("Resolucion", [1000, 2000, 3000, 4000], index=2)
    grosor = st.slider("Grosor anillos", 0.1, 3.0, 0.9, 0.1)
    brillo = st.slider("Brillo neon", 0.5, 3.0, 2.2, 0.05)

def dia_to_c(dia):
    t = dia / 365.0 * 2 * math.pi
    r = 0.7885
    return complex(r*math.cos(t)*0.8-0.4, r*math.sin(t)*0.6)

c = dia_to_c(dia)
st.caption(f"DIA {dia} -> c = {c.real:.5f} + {c.imag:.5f}i | Negro - Fucsia - Turquesa - Amarillo - Negro")

def julia_orden_correcto(w,h,c,zoom,iters,grosor,brillo):
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

    # CORREGIDO: Como M crece hacia adentro (cerca escapa tarde)
    # Entonces:
    # FUCSIA = mas adentro (smooth grande) = 2*grosor a 3*grosor
    # TURQUESA = medio
    # AMARILLO = mas afuera (smooth chico)

    # Usa ventana cerca del borde
    base = np.percentile(smooth[M < iters], 85) # cerca del conjunto
    # Distancia hacia afuera
    d = base - smooth
    # Solo d positivo y pequeño = cerca del borde
    m_fucsia = (d >= 0) & (d < grosor)
    m_turquesa = (d >= grosor) & (d < 2*grosor)
    m_amarillo = (d >= 2*grosor) & (d < 3*grosor)

    img[m_fucsia] = [255,20,147] # pegado al negro
    img[m_turquesa] = [0,255,255]
    img[m_amarillo] = [255,255,0] # afuera

    return img

W=900; H=900
img = julia_orden_correcto(W,H,c,zoom,iters,grosor,brillo)
st.image(img, use_container_width=True, channels="RGB")
with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_orden_correcto(resolucion,resolucion,c,zoom,iters,grosor,brillo)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_CORRECTO_DIA{dia}.png",mime="image/png")
