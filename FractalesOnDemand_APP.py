import streamlit as st
import numpy as np
from PIL import Image
import io
import math

st.set_page_config(layout="wide", page_title="V35 NEON PURO")
st.title("FRACTALES BAJO DEMANDA - V35 NEON PURO - 3 VETAS GORDAS")

with st.sidebar:
    dia = st.slider("DIA", 1, 365, 258)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.80, 0.05)
    iters = st.slider("CALIDAD", 200, 2000, 800)
    resolucion = st.selectbox("Resolucion", [1000, 2000, 3000, 4000], index=2)
    ancho_vetas = st.slider("Ancho vetas gordas", 0.5, 3.0, 1.50, 0.1)
    brillo = st.slider("Brillo neon", 0.5, 3.0, 2.2, 0.05)

def dia_to_c(dia):
    t = dia / 365.0 * 2 * math.pi
    r = 0.7885
    cx = r * math.cos(t) * 0.8 - 0.4
    cy = r * math.sin(t) * 0.6
    return complex(cx, cy)

c = dia_to_c(dia)
st.caption(f"DIA {dia} -> c = {c.real:.5f} + {c.imag:.5f}i")

def julia_neon_puro(w, h, c, zoom, iters, ancho, brillo):
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

    # Distancia para 3 anillos gordos
    smooth = M + 5 - np.log2(np.log(np.abs(Z)+1)+1)
    smooth = np.nan_to_num(smooth, nan=0)

    # Normaliza a 0-1 para 3 bandas gordas
    # Usa solo la parte exterior
    band = (smooth % 30) / 30.0
    band = np.power(band, ancho)

    r=np.zeros_like(band); g=np.zeros_like(band); b=np.zeros_like(band)

    m0 = band < 0.33
    m1 = (band >=0.33) & (band <0.66)
    m2 = band >=0.66

    # NEON PURO - sin oscurecer
    r[m0]=255; g[m0]=20; b[m0]=147
    r[m1]=0; g[m1]=255; b[m1]=255
    r[m2]=255; g[m2]=255; b[m2]=0

    img=np.stack([r,g,b],axis=-1).astype(np.uint8)

    # Fondo negro limpio
    img[M < 1] = [0,0,0]
    img[M > 28] = [0,0,0]

    return img

W=900; H=900
img = julia_neon_puro(W,H,c,zoom,iters,ancho_vetas,brillo)
st.image(img, use_container_width=True, channels="RGB")

with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_neon_puro(resolucion,resolucion,c,zoom,iters,ancho_vetas,brillo)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_NEON_DIA{dia}.png",mime="image/png")
