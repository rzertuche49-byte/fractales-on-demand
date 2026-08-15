import streamlit as st
import numpy as np
from PIL import Image
import io
st.set_page_config(layout="wide", page_title="V33 3 NEON GORDAS REAL")
st.title("FRACTALES BAJO DEMANDA - V33 3 VETAS GORDAS REAL")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 75)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.25, 0.05)
    iters = st.slider("CALIDAD", 200, 2000, 800)
    resolucion = st.selectbox("Resolucion", [1000, 2000, 3000, 4000], index=2)
    ancho_vetas = st.slider("Ancho vetas gordas", 0.5, 3.0, 1.5, 0.1)
    brillo = st.slider("Brillo neon", 0.5, 3.0, 1.80, 0.05)

c = complex(-0.74543, 0.11301)

def julia_3gordas(w, h, c, zoom, iters, ancho, brillo):
    x=np.linspace(-3.0/zoom,3.0/zoom,w)
    y=np.linspace(-3.0/zoom,3.0/zoom,h)
    X,Y=np.meshgrid(x,y)
    Z=X+1j*Y
    M=np.zeros(Z.shape)
    Zfinal=np.zeros(Z.shape, dtype=complex)
    for i in range(iters):
        mask=np.abs(Z)<=10
        if not np.any(mask): break
        Z[mask]=Z[mask]**2+c
        M[mask]=i
        Zfinal[mask]=Z[mask]

    # distancia real para 3 vetas gordas - NO modulo repetido
    dist = np.log(np.abs(Zfinal)+1)
    dist = np.nan_to_num(dist, nan=0)
    # normaliza y solo 3 bandas
    d_norm = np.clip(dist / (dist.max()*0.5), 0, 1)
    # invierte para que adentro sea fucsia
    d_norm = 1 - d_norm

    r=np.zeros_like(d_norm); g=np.zeros_like(d_norm); b=np.zeros_like(d_norm)

    # 3 VETAS GORDAS SOLIDAS
    m0 = d_norm < 0.33
    m1 = (d_norm >=0.33) & (d_norm <0.66)
    m2 = d_norm >=0.66

    r[m0]=255; g[m0]=20; b[m0]=147 # Fucsia
    r[m1]=0; g[m1]=255; b[m1]=255 # Turquesa
    r[m2]=255; g[m2]=255; b[m2]=0 # Amarillo

    img=np.stack([r,g,b],axis=-1).astype(np.uint8)

    # negro interior y exterior grueso como tu ref
    interior = M > 20
    exterior = M < 1.5
    img[interior]=[0,0,0]
    img[exterior]=[0,0,0]

    fade = np.clip((M-1.5)/15.0,0,1)
    img = (img.astype(float) * fade[:,:,None] * brillo).astype(np.uint8)
    img[interior]=[0,0,0]
    img[exterior]=[0,0,0]
    return img

W=900; H=900
img = julia_3gordas(W,H,c,zoom,iters,ancho_vetas,brillo)
st.image(img, use_container_width=True, channels="RGB")
with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_3gordas(resolucion,resolucion,c,zoom,iters,ancho_vetas,brillo)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_3GORDAS_DIA{dia}.png",mime="image/png")
