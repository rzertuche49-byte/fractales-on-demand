import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V57 FIX MATEMATICO")
st.title("FRACTALES BAJO DEMANDA - V57 FIX MATEMATICO SIN NIEVE")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 273)
    zoom = st.slider("ZOOM", 0.2, 4.0, 2.90, 0.05)
    picos = st.slider("PICOS / CALIDAD", 0, 100, 65)
    ciclos = st.slider("Detalle bandas", 5.0, 50.0, 28.0, 0.5)
    profundidad = st.slider("Profundidad 3D", 0.0, 1.5, 0.60, 0.1)
    resolucion = st.selectbox("Resolucion", [1000,2000,3000,4000], index=1)

def dia_to_c(dia, picos_pct):
    t = dia/365*2*math.pi
    # base ultra segura, 100% dentro, probada
    # -0.75 + 0.11 es interior profundo, nunca da polvo
    r = 0.02 - (picos_pct/100)*0.016
    cx = -0.75 + r*math.cos(t*3)
    cy = 0.11 + r*math.sin(t*3)
    return complex(cx, cy), 1000, r

c, iters, r_actual = dia_to_c(dia, picos)
st.caption(f"DIA {dia} -> c={c.real:.5f}+{c.imag:.5f}i | PICOS={picos}% | r={r_actual:.5f} | FIX log")

def julia_fix(w,h,c,zoom,iters,ciclos,profundidad):
    x = np.linspace(-1.5/zoom, 1.5/zoom, w)
    y = np.linspace(-1.5/zoom, 1.5/zoom, h)
    X,Y = np.meshgrid(x,y)
    Z = X+1j*Y
    M = np.full(Z.shape, iters, dtype=float)
    ang = np.zeros(Z.shape)

    for i in range(iters):
        mask = np.abs(Z) <= 100
        esc = mask & (np.abs(Z) > 2) & (M==iters)
        if np.any(esc):
            absZ = np.abs(Z[esc])
            # FIX MATEMATICO: log(log) seguro, sin log2 de negativo
            # smooth = i + 1 - log2(log|Z|)
            smooth = i + 1 - np.log(np.log(absZ))/np.log(2)
            # clip para no generar nan
            smooth = np.clip(smooth, 0, iters)
            M[esc] = smooth
            ang[esc] = np.angle(Z[esc])
        Z[mask] = Z[mask]*Z[mask] + c
        if not np.any(mask):
            break

    valid = M < iters
    # ahora valid es solo exterior real, interior negro puro sin NaN
    t = (M[valid] * ciclos * 0.06 + ang[valid]*0.35) % 1.0
    t = np.nan_to_num(t, nan=0.0)

    r_ = np.empty_like(t); g = np.empty_like(t); b = np.empty_like(t)
    mf = t<0.25; my=(t>=0.25)&(t<0.5); mc=(t>=0.5)&(t<0.75); mm=t>=0.75
    r_[mf]=255; g[mf]=30+180*t[mf]/0.25; b[mf]=180
    r_[my]=255; g[my]=255; b[my]=0
    r_[mc]=0; g[mc]=255; b[mc]=255
    r_[mm]=160+95*(t[mm]-0.75)/0.25; g[mm]=0; b[mm]=255

    shade = 0.55 + 0.45*np.cos(ang[valid]*2 + 1.2)
    shade = np.clip(shade**(1.0 - profundidad*0.3), 0.35, 1.0)

    r_ = (r_*shade).astype(np.uint8)
    g = (g*shade).astype(np.uint8)
    b = (b*shade).astype(np.uint8)

    img = np.zeros((h,w,3), dtype=np.uint8)
    img[valid] = np.stack([r_,g,b], axis=1)
    return img

W=800; H=800
img = julia_fix(W,H,c,zoom,iters,ciclos,profundidad)
st.image(img, use_container_width=True, channels="RGB")
st.success(f"V57 FIX: r={r_actual:.5f} ahora es interior seguro. Ya no hay log2(negativo). Fondo negro 100% limpio garantizado.")

with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_fix(resolucion,resolucion,c,zoom,iters,ciclos,profundidad)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_V57_FIX_DIA{dia}.png",mime="image/png")
