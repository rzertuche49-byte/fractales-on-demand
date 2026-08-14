import streamlit as st
import numpy as np
from PIL import Image
import io
st.set_page_config(layout="wide", page_title="FRACTALES V31 FINAL")
st.title("FRACTALES BAJO DEMANDA - V31 FINAL NEON REF")
with st.sidebar:
    paleta = st.selectbox("Paleta", ["3 Colores Neon (Fucsia/Turquesa/Amarillo) - REF ORIGINAL", "1 Color Neon (Fucsia actual)", "1 Color Turquesa", "Arcoiris Seda"], index=0)
    dia = st.slider("DIA (1-365)", 1, 365, 75)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.25, 0.05)
    iters = st.slider("CALIDAD", 200, 2000, 800)
    resolucion = st.selectbox("Resolucion Exportar", [1000, 2000, 3000, 4000], index=2)
    vetas = st.slider("Num Vetass gordas", 0.01, 0.2, 0.05, 0.005)
    brillo = st.slider("Brillo neon", 0.5, 2.5, 1.8, 0.05)
    rotacion = st.slider("Rotacion Tono", 0.0, 6.28, 1.2, 0.05)

c = complex(-0.74543, 0.11301) if 70 <= dia <= 80 else complex(0.7885*np.cos((dia/365)*2*np.pi*3), 0.7885*np.sin((dia/365)*2*np.pi*3))

def julia_final(w, h, c, zoom, iters, vetas, rotacion, brillo, paleta):
    x=np.linspace(-3.0/zoom,3.0/zoom,w); y=np.linspace(-3.0/zoom,3.0/zoom,h)
    X,Y=np.meshgrid(x,y); Z=X+1j*Y
    M=np.zeros(Z.shape); Zabs=np.zeros(Z.shape)
    for i in range(iters):
        mask=np.abs(Z)<=10
        if not np.any(mask): break
        Z[mask]=Z[mask]**2+c; M[mask]=i; Zabs[mask]=np.abs(Z[mask])
    smooth = M + 1 - np.log(np.log(Zabs+1)+1)/np.log(2)
    smooth = np.nan_to_num(smooth, nan=0)
    t = (smooth * vetas * 6.28 + rotacion) % 6.28
    r=np.zeros_like(t); g=np.zeros_like(t); b=np.zeros_like(t)
    if "3 Colores" in paleta:
        m1=t<2.09; m2=(t>=2.09)&(t<4.18); m3=t>=4.18
        r[m1]=255; g[m1]=20; b[m1]=147
        r[m2]=0; g[m2]=255; b[m2]=255
        r[m3]=255; g[m3]=255; b[m3]=0
    elif "Fucsia actual" in paleta:
        r[:]=255; g[:]=20; b[:]=147
        shade = 0.7 + 0.3*np.sin(t*2)
        r=r*shade; g=g*shade*0.4; b=b*shade
    elif "Turquesa" in paleta:
        r[:]=0; g[:]=220; b[:]=255
    else:
        r=(0.5+0.5*np.sin(t))*255; g=(0.5+0.5*np.sin(t+2.094))*255; b=(0.5+0.5*np.sin(t+4.188))*255
    img=np.stack([r,g,b],axis=-1).astype(np.uint8)
    interior=M>25; exterior=M<2
    img[interior]=[0,0,0]; img[exterior]=[0,0,0]
    fade=np.clip((M-2)/20.0,0,1)
    img=(img.astype(float)*fade[:,:,None]*brillo).astype(np.uint8)
    img[interior]=[0,0,0]; img[exterior]=[0,0,0]
    return img

W=900; H=900
img = julia_final(W,H,c,zoom,iters,vetas,rotacion,brillo,paleta)
st.image(img, use_container_width=True)
with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_final(resolucion,resolucion,c,zoom,iters,vetas,rotacion,brillo,paleta)
        buf=io.BytesIO(); Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_V31_DIA{dia}.png",mime="image/png")