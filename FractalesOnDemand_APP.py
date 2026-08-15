import streamlit as st
import numpy as np
from PIL import Image
import io
import math
st.set_page_config(layout="wide", page_title="V45 GORDO FINAL")
st.title("FRACTALES BAJO DEMANDA - V45 GORDO FINAL - REF")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 258)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.45, 0.05)
    iters = st.slider("CALIDAD", 200, 2000, 1000)
    resolucion = st.selectbox("Resolucion", [1000, 2000, 3000, 4000], index=2)
    grosor = st.slider("Grosor anillos", 0.1, 5.0, 1.80, 0.10)

def dia_to_c(dia):
    t = dia / 365.0 * 2 * math.pi
    r = 0.82
    return complex(r*math.cos(t)*0.85-0.35, r*math.sin(t)*0.70)

c = dia_to_c(dia)
st.caption(f"DIA {dia} -> c = {c.real:.5f} + {c.imag:.5f}i | ORDEN: Negro->Fucsia->Turquesa->Amarillo")

def julia_final(w,h,c,zoom,iters,grosor):
    x=np.linspace(-3.0/zoom,3.0/zoom,w)
    y=np.linspace(-3.0/zoom,3.0/zoom,h)
    X,Y=np.meshgrid(x,y)
    Z=X+1j*Y
    M=np.full(Z.shape, iters, dtype=float)
    Zc=np.zeros(Z.shape, dtype=complex)
    for i in range(iters):
        mask=np.abs(Z)<=200
        esc = mask & (np.abs(Z) > 2) & (M==iters)
        M[esc]=i
        Zc[esc]=Z[esc]
        Z[mask]=Z[mask]**2+c
    valid = M < iters
    smooth = M - np.log2(np.log(np.abs(Zc)+1e-10)+1)
    smooth = np.nan_to_num(smooth, nan=iters)
    base = np.percentile(smooth[valid], 92)
    d = base - smooth
    img = np.zeros((h,w,3), dtype=np.uint8)
    img[valid & (d >= 0) & (d < grosor)] = [255,20,147]
    img[valid & (d >= grosor) & (d < 2*grosor)] = [0,255,255]
    img[valid & (d >= 2*grosor) & (d < 3*grosor)] = [255,255,0]
    return img

W=900; H=900
img = julia_final(W,H,c,zoom,iters,grosor)
st.image(img, use_container_width=True, channels="RGB")
with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_final(resolucion,resolucion,c,zoom,iters,grosor)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_FINAL_DIA{dia}.png",mime="image/png")
