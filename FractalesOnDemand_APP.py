import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V75 PSY")
st.title("FRACTALES BAJO DEMANDA - V75 FINAL PSICODELICO")

with st.sidebar:
    dia = st.slider("DIA", 1, 365, 135)
    zoom = st.slider("ZOOM", 0.2, 10.0, 1.1, 0.05)
    center_x = st.slider("Centro X", -1.5, 1.5, 0.55, 0.005)
    center_y = st.slider("Centro Y", -1.5, 1.5, 0.13, 0.005)
    picos = st.slider("PICOS / CALIDAD", 0, 100, 85)
    ciclos = st.slider("ciclos", 0.1, 5.0, 1.5, 0.1) # IMPORTANTE: 1.5 no 3.2
    mezcla = st.slider("Detalle espiral", 0.0, 1.0, 0.22, 0.02)
    tamano_mancha = st.slider("Tamaño mancha", 0.1, 3.0, 1.2, 0.1) # NUEVO
    brillo = st.slider("Brillo", 0.5, 2.0, 1.2, 0.05)
    iters = st.slider("Iteraciones", 10, 500, 80, 10) # NUEVO: solo 80!
    resolucion = st.selectbox("Export", [2000,3000,4000,6000], index=2)

def dia_to_c(dia, picos_pct):
    t = dia/365*2*math.pi
    r = 0.02 - (picos_pct/100)*0.016
    cx = -0.75 + r*math.cos(t*3)
    cy = 0.11 + r*math.sin(t*3)
    return complex(cx, cy)

c = dia_to_c(dia, picos)

def julia_psy(w,h,c,zoom,cx,cy,iters,ciclos,mezcla,tam,brillo):
    x = np.linspace(-1.5/zoom + cx, 1.5/zoom + cx, w, dtype=np.float64)
    y = np.linspace(-1.0/zoom + cy, 1.0/zoom + cy, h, dtype=np.float64)
    X,Y = np.meshgrid(x,y)
    Z = X+1j*Y
    # Solo pocas iteraciones para manchas grandes
    for i in range(iters):
        Z = Z*Z + c
    # Color por ángulo + distancia = manchas lisas
    ang = np.angle(Z)
    rad = np.log(np.abs(Z)+1)
    fase = ang*mezcla + rad*tam
    s = (fase * ciclos * 0.25) % 1.0
    t_ = s * 7.0
    i0 = np.floor(t_).astype(int) % 7
    f = (1 - np.cos((t_ - np.floor(t_))*np.pi))/2
    cols = np.array([[0,255,255],[0,100,255],[255,0,200],[255,100,0],[255,255,0],[0,255,100],[180,0,255]], float)
    img = np.zeros((h,w,3), float)
    for k in range(7):
        m = i0==k; nk=(k+1)%7
        img[m,0] = (1-f[m])*cols[k,0]+f[m]*cols[nk,0]
        img[m,1] = (1-f[m])*cols[k,1]+f[m]*cols[nk,1]
        img[m,2] = (1-f[m])*cols[k,2]+f[m]*cols[nk,2]
    img = np.clip(img*brillo,0,255).astype(np.uint8)
    return img

W=1200; H=900
img=julia_psy(W,H,c,zoom,center_x,center_y,iters,ciclos,mezcla,tamano_mancha,brillo)
st.image(img,use_container_width=True,channels="RGB")
st.success("V75 - Manchas lisas sin confeti. Este es EL QUE BUSCO.")

with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_psy(resolucion,resolucion,c,zoom,center_x,center_y,iters,ciclos,mezcla,tamano_mancha,brillo)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG 4K",buf.getvalue(),file_name=f"fractal_V75_PSY_DIA{dia}.png",mime="image/png")
