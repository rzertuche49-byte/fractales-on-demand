import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V52 FIX ZOOM")
st.title("FRACTALES BAJO DEMANDA - V52 FIX ZOOM + PICOS REALES")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 258)
    zoom = st.slider("ZOOM", 0.2, 4.0, 2.90, 0.05)
    iters = st.slider("PICOS / CALIDAD", 500, 4000, 1500)
    ciclos = st.slider("Detalle bandas", 5.0, 50.0, 28.0, 0.5)
    profundidad = st.slider("Profundidad 3D", 0.0, 1.5, 0.6, 0.1)
    resolucion = st.selectbox("Resolucion", [1000,2000,3000,4000], index=1)

def dia_to_c(dia):
    t = dia/365*2*math.pi
    # c perfecto para picos: -0.78+0.15 es el rey de los picos, lo orbitamos
    r = 0.02
    cx = -0.78 + r*math.cos(t*2)
    cy = 0.15 + r*math.sin(t*2)
    return complex(cx, cy)

c = dia_to_c(dia)
st.caption(f"DIA {dia} -> c={c:.5f} | ZOOM {zoom} | REF LIMPIA SIN RUIDO")

def julia_clean(w,h,c,zoom,iters,ciclos,profundidad):
    x = np.linspace(-1.5/zoom, 1.5/zoom, w)
    y = np.linspace(-1.5/zoom, 1.5/zoom, h)
    X,Y = np.meshgrid(x,y)
    Z = X+1j*Y
    M = np.full(Z.shape, iters, dtype=float)
    angle = np.zeros(Z.shape)

    for i in range(iters):
        mask = np.abs(Z) < 1e4
        esc = mask & (np.abs(Z) > 4) & (M==iters)
        if np.any(esc):
            # smooth correcto sin ruido
            M[esc] = i + 1 - np.log(np.log(np.abs(Z[esc])))/np.log(2)
            angle[esc] = np.angle(Z[esc])
        Z[mask] = Z[mask]*Z[mask] + c
        if not np.any(mask):
            break

    valid = M < iters
    # bandas + flujo para espirales como tu ref
    t = (M[valid] * ciclos * 0.06 + angle[valid]*0.4) % 1.0

    r = np.empty_like(t); g = np.empty_like(t); b = np.empty_like(t)
    mf = t<0.25; my=(t>=0.25)&(t<0.5); mc=(t>=0.5)&(t<0.75); mm=t>=0.75
    r[mf]=255; g[mf]=20+200*t[mf]/0.25; b[mf]=180
    r[my]=255; g[my]=255; b[my]=0
    r[mc]=0; g[mc]=255; b[mc]=255
    r[mm]=150+100*(t[mm]-0.75)/0.25; g[mm]=0; b[mm]=255

    # sombra suave real, sin ruido
    shade = 0.5 + 0.5*np.cos(angle[valid]*2 + 1.5)
    shade = shade ** (1.0 - profundidad*0.3)
    shade = np.clip(shade, 0.3, 1.0)

    r = (r*shade).astype(np.uint8)
    g = (g*shade).astype(np.uint8)
    b = (b*shade).astype(np.uint8)

    img = np.zeros((h,w,3), dtype=np.uint8)
    img[valid] = np.stack([r,g,b], axis=1)
    img[~valid] = [0,0,0]
    return img

W=800; H=800
img = julia_clean(W,H,c,zoom,iters,ciclos,profundidad)
st.image(img, use_container_width=True, channels="RGB")

with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_clean(resolucion,resolucion,c,zoom,iters,ciclos,profundidad)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_V52_DIA{dia}_Z{zoom}.png",mime="image/png")
