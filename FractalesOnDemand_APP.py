import streamlit as st
import numpy as np
from PIL import Image
import io
st.set_page_config(layout="wide", page_title="V32 3 NEON REAL")
st.title("FRACTALES BAJO DEMANDA - V32 3 NEON REAL - 3 VETAS GORDAS")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 75)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.25, 0.05)
    iters = st.slider("CALIDAD", 200, 2000, 800)
    resolucion = st.selectbox("Resolucion", [1000, 2000, 3000, 4000], index=2)
    num_vetas = st.slider("Num Vetass gordas", 1, 6, 3)
    brillo = st.slider("Brillo neon", 0.5, 3.0, 1.80, 0.05)
c = complex(-0.74543, 0.11301)
def julia_3neon(w, h, c, zoom, iters, num_vetas, brillo):
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
    log_r = np.log(np.log(np.abs(Zfinal)+1)+1)
    log_r = np.nan_to_num(log_r, nan=0)
    t = log_r * (num_vetas * 1.8)
    t = t % num_vetas
    r=np.zeros_like(t); g=np.zeros_like(t); b=np.zeros_like(t)
    m0 = t < 1
    m1 = (t >=1) & (t <2)
    m2 = t >=2
    r[m0]=255; g[m0]=20; b[m0]=147
    r[m1]=0; g[m1]=255; b[m1]=255
    r[m2]=255; g[m2]=255; b[m2]=0
    img=np.stack([r,g,b],axis=-1).astype(np.uint8)
    interior = M > 25
    exterior = M < 2
    img[interior]=[0,0,0]
    img[exterior]=[0,0,0]
    fade = np.clip((M-2)/25.0,0,1) ** 0.6
    img = (img.astype(float) * fade[:,:,None] * brillo).astype(np.uint8)
    img[interior]=[0,0,0]
    img[exterior]=[0,0,0]
    return img
W=900; H=900
img = julia_3neon(W,H,c,zoom,iters,num_vetas,brillo)
st.image(img, use_container_width=True, channels="RGB")
with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_3neon(resolucion,resolucion,c,zoom,iters,num_vetas,brillo)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG 3000px",buf.getvalue(),file_name=f"fractal_3NEON_DIA{dia}.png",mime="image/png")
