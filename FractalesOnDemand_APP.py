import streamlit as st
import numpy as np
from PIL import Image
import io
import math
st.set_page_config(layout="wide", page_title="V41 DENTADO + ORDEN")
st.title("FRACTALES BAJO DEMANDA - V41 DENTADO REAL ORDEN CORRECTO")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 258)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.35, 0.05)
    iters = st.slider("CALIDAD", 200, 2000, 1000)
    resolucion = st.selectbox("Resolucion", [1000, 2000, 3000, 4000], index=2)
    grosor = st.slider("Grosor anillos", 0.1, 3.0, 0.50, 0.05)
    detalle = st.slider("Detalle fractal", 0.5, 3.0, 1.8, 0.1)

def dia_to_c_dentado(dia):
    # Fuerza siempre forma dentada tipo dendrita
    t = dia / 365.0 * 2 * math.pi * 1.5
    # Radio cerca del borde para siempre dendrita
    r = 0.78 + 0.04 * math.sin(dia * 0.1)
    cx = r * math.cos(t) * 0.9 - 0.45
    cy = r * math.sin(t) * 0.75
    return complex(cx, cy)

c = dia_to_c_dentado(dia)
st.caption(f"DIA {dia} -> c = {c.real:.5f} + {c.imag:.5f}i | Orden: Negro -> Fucsia -> Turquesa -> Amarillo")

def julia_dentado_orden(w,h,c,zoom,iters,grosor,detalle):
    x=np.linspace(-3.0/zoom,3.0/zoom,w)
    y=np.linspace(-3.0/zoom,3.0/zoom,h)
    X,Y=np.meshgrid(x,y)
    Z=X+1j*Y
    M=np.full(Z.shape, iters, dtype=float)
    Zabs=np.zeros(Z.shape)
    for i in range(iters):
        mask=np.abs(Z)<=100
        escaped = mask & (np.abs(Z) > 2) & (M==iters)
        M[escaped]=i + 1 - np.log2(np.log(np.abs(Z[escaped])+1e-10)+1)
        Z[mask]=Z[mask]**2+c

    smooth = M
    smooth = np.nan_to_num(smooth, nan=iters)

    img = np.zeros((h,w,3), dtype=np.uint8)

    # Ventana cerca del borde para dentado fino
    # Cuanto mas grande detalle, mas piquitos
    base = np.max(smooth[smooth < iters]) - 1
    d = (base - smooth) * detalle

    m_fucsia = (d >= 0) & (d < grosor)
    m_turquesa = (d >= grosor) & (d < 2*grosor)
    m_amarillo = (d >= 2*grosor) & (d < 3*grosor)

    img[m_fucsia] = [255,20,147]
    img[m_turquesa] = [0,255,255]
    img[m_amarillo] = [255,255,0]

    return img

W=900; H=900
img = julia_dentado_orden(W,H,c,zoom,iters,grosor,detalle)
st.image(img, use_container_width=True, channels="RGB")
with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_dentado_orden(resolucion,resolucion,c,zoom,iters,grosor,detalle)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_DENTADO_DIA{dia}.png",mime="image/png")
