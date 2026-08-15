import streamlit as st
import numpy as np
from PIL import Image
import io
import math
st.set_page_config(layout="wide", page_title="V37 3 ANILLOS PEGADOS")
st.title("FRACTALES BAJO DEMANDA - V37 3 ANILLOS PEGADOS REF")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 258)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.80, 0.05)
    iters = st.slider("CALIDAD", 200, 2000, 800)
    resolucion = st.selectbox("Resolucion", [1000, 2000, 3000, 4000], index=2)
    grosor = st.slider("Grosor anillos", 0.1, 2.0, 0.6, 0.1)
    brillo = st.slider("Brillo neon", 0.5, 3.0, 2.2, 0.05)

def dia_to_c(dia):
    t = dia / 365.0 * 2 * math.pi
    r = 0.7885
    return complex(r*math.cos(t)*0.8-0.4, r*math.sin(t)*0.6)

c = dia_to_c(dia)
st.caption(f"DIA {dia} -> c = {c.real:.5f} + {c.imag:.5f}i")

def julia_3anillos_pegados(w,h,c,zoom,iters,grosor,brillo):
    x=np.linspace(-3.0/zoom,3.0/zoom,w)
    y=np.linspace(-3.0/zoom,3.0/zoom,h)
    X,Y=np.meshgrid(x,y)
    Z=X+1j*Y
    M=np.zeros(Z.shape)
    Zabs=np.zeros(Z.shape)
    for i in range(iters):
        mask=np.abs(Z)<=10
        if not np.any(mask): break
        Z[mask]=Z[mask]**2+c
        M[mask]=i
        Zabs[mask]=np.abs(Z[mask])

    # DISTANCIA SUAVE - para anillos lisos
    smooth = M + 1 - np.log2(np.log(Zabs+1.1)+1)
    smooth = np.nan_to_num(smooth, nan=0)

    # Solo 3 anillos muy pegados al conjunto, resto negro
    # M entre 2 y 8 es pegado al borde
    dist = smooth

    img = np.zeros((h,w,3), dtype=np.uint8) # todo negro por defecto

    # Define 3 anillos delgados
    # El truco: usar modulo pero solo en ventana estrecha
    # 0-1 = Fucsia, 1-2 = Turquesa, 2-3 = Amarillo
    mask_borde = (M >= 1.5) & (M <= 12)

    t = (dist - dist.min()) / (np.percentile(dist[mask_borde], 90) - dist.min() + 1e-6)
    t = np.clip(t, 0, 1)
    # invierte para que adentro sea fucsia
    t = 1 - t
    # 3 bandas
    t = t * (3 * grosor)
    t = t % 3

    m1 = mask_borde & (t < 1)
    m2 = mask_borde & (t >=1) & (t <2)
    m3 = mask_borde & (t >=2)

    img[m1] = [255,20,147]
    img[m2] = [0,255,255]
    img[m3] = [255,255,0]

    return img

W=900; H=900
img = julia_3anillos_pegados(W,H,c,zoom,iters,grosor,brillo)
st.image(img, use_container_width=True, channels="RGB")
with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_3anillos_pegados(resolucion,resolucion,c,zoom,iters,grosor,brillo)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_3ANILLOS_DIA{dia}.png",mime="image/png")
