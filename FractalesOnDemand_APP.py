import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V74.2 BLACK")
st.title("FRACTALES BAJO DEMANDA - V74.2 FONDO NEGRO")
st.caption("Sin polvo gris - solo manchas clean")

with st.sidebar:
    dia = st.slider("DIA", 1, 365, 135)
    zoom = st.slider("ZOOM", 0.2, 50.0, 12.0, 0.05) # bajale de 50 a 12
    center_x = st.slider("Centro X", -1.5, 1.5, 0.55, 0.005)
    center_y = st.slider("Centro Y", -1.5, 1.5, -0.13, 0.005)
    picos = st.slider("PICOS / CALIDAD", 0, 100, 85)
    ciclos = st.slider("ciclos", 0.5, 15.0, 3.2, 0.1)
    mezcla = st.slider("Detalle espiral", 0.0, 1.0, 0.22, 0.02)
    suavizado = st.slider("Suavizado", 0.1, 2.0, 0.45, 0.05)
    brillo = st.slider("Brillo", 0.5, 1.5, 1.2, 0.05)
    iters_extra = st.slider("Iteraciones", 0, 3000, 1800, 100)
    umbral_polvo = st.slider("Limpieza polvo", 0, 50, 12) # NUEVO
    resolucion = st.selectbox("Export", [2000,3000,4000,6000,8000], index=2)

def dia_to_c(dia, picos_pct):
    t = dia/365*2*math.pi
    r = 0.02 - (picos_pct/100)*0.016
    cx = -0.75 + r*math.cos(t*3)
    cy = 0.11 + r*math.sin(t*3)
    return complex(cx, cy), 1000, r

c, base_iters, _ = dia_to_c(dia, picos)
iters = base_iters + iters_extra

def julia_black(w,h,c,zoom,cx,cy,iters,ciclos,mezcla,suavizado,brillo,umbral):
    x = np.linspace(-1.5/zoom + cx, 1.5/zoom + cx, w, dtype=np.float64)
    y = np.linspace(-1.0/zoom + cy, 1.0/zoom + cy, h, dtype=np.float64)
    X,Y = np.meshgrid(x,y)
    Z = X+1j*Y
    M = np.full(Z.shape, iters, dtype=np.float64)
    Arg = np.zeros(Z.shape, dtype=np.float64)
    for i in range(iters):
        mask = np.abs(Z) <= 1e4
        if not np.any(mask): break
        Z_new = Z[mask]*Z[mask] + c
        esc = (np.abs(Z_new) > 4) & (M[mask]==iters)
        if np.any(esc):
            iy,ix = np.where(mask)
            abs_esc = np.abs(Z_new[esc])
            M[iy[esc], ix[esc]] = i + 1 - np.log(np.log(abs_esc+1e-10))/np.log(2)
            Arg[iy[esc], ix[esc]] = np.angle(Z_new[esc])
        Z[mask] = Z_new
    # FIX POLVO: solo colorea si escapó después del umbral
    valid = (M < iters) & (M > umbral)
    fase = M[valid] * 0.55 + np.sin(Arg[valid]*0.8) * mezcla
    fase = fase * suavizado
    s = (fase * ciclos * 0.12) % 1.0
    t = s * 7.0
    i0 = np.floor(t).astype(int) % 7
    f = (1 - np.cos((t - np.floor(t))*np.pi))/2
    cols = np.array([[0,255,255],[0,100,255],[255,0,200],[255,100,0],[255,255,0],[0,255,100],[180,0,255]], float)
    r_=np.zeros_like(s); g_=np.zeros_like(s); b_=np.zeros_like(s)
    for k in range(7):
        m = i0==k; nk=(k+1)%7
        r_[m]=(1-f[m])*cols[k,0]+f[m]*cols[nk,0]
        g_[m]=(1-f[m])*cols[k,1]+f[m]*cols[nk,1]
        b_[m]=(1-f[m])*cols[k,2]+f[m]*cols[nk,2]
    r_ = np.clip(r_*brillo,0,255); g_ = np.clip(g_*brillo,0,255); b_ = np.clip(b_*brillo,0,255)
    img=np.zeros((h,w,3),dtype=np.uint8) # FONDO NEGRO PURO
    img[valid]=np.stack([r_.astype(np.uint8),g_.astype(np.uint8),b_.astype(np.uint8)],axis=1)
    return img

W=1200; H=1200
img=julia_black(W,H,c,zoom,center_x,center_y,iters,ciclos,mezcla,suavizado,brillo,umbral_polvo)
st.image(img,use_container_width=True,channels="RGB")

with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_black(resolucion,resolucion,c,zoom,center_x,center_y,iters,ciclos,mezcla,suavizado,brillo,umbral_polvo)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG 4K",buf.getvalue(),file_name=f"fractal_V74_2_BLACK_DIA{dia}.png",mime="image/png")
