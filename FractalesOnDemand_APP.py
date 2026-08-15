import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V58 BANDAS ALINEADAS")
st.title("FRACTALES BAJO DEMANDA - V58 BANDAS ALINEADAS CON PICOS")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 273)
    zoom = st.slider("ZOOM", 0.2, 4.0, 2.90, 0.05)
    picos = st.slider("PICOS / CALIDAD", 0, 100, 65)
    ciclos = st.slider("Detalle bandas", 5.0, 50.0, 28.0, 0.5)
    profundidad = st.slider("Profundidad 3D", 0.0, 1.5, 0.60, 0.1)
    direccion = st.slider("Direccion bandas", -1.0, 1.0, 0.8, 0.1)
    resolucion = st.selectbox("Resolucion", [1000,2000,3000,4000], index=1)

def dia_to_c(dia, picos_pct):
    t = dia/365*2*math.pi
    r = 0.02 - (picos_pct/100)*0.016
    cx = -0.75 + r*math.cos(t*3)
    cy = 0.11 + r*math.sin(t*3)
    return complex(cx, cy), 1200, r

c, iters, r_actual = dia_to_c(dia, picos)
st.caption(f"DIA {dia} -> c={c.real:.5f}+{c.imag:.5f}i | PICOS={picos}% | DIRECCION={direccion} | BANDAS ALINEADAS")

def julia_alineado(w,h,c,zoom,iters,ciclos,profundidad,direccion):
    x = np.linspace(-1.5/zoom, 1.5/zoom, w)
    y = np.linspace(-1.5/zoom, 1.5/zoom, h)
    X,Y = np.meshgrid(x,y)
    Z = X+1j*Y
    M = np.full(Z.shape, iters, dtype=float)
    ang = np.zeros(Z.shape)
    final_z = np.zeros(Z.shape, dtype=complex)

    for i in range(iters):
        mask = np.abs(Z) <= 100
        esc = mask & (np.abs(Z) > 2) & (M==iters)
        if np.any(esc):
            absZ = np.abs(Z[esc])
            smooth = i + 1 - np.log(np.log(absZ))/np.log(2)
            M[esc] = np.clip(smooth, 0, iters)
            ang[esc] = np.angle(Z[esc])
            final_z[esc] = Z[esc]
        Z[mask] = Z[mask]*Z[mask] + c
        if not np.any(mask):
            break

    valid = M < iters
    # FIX DIRECCION: ahora el ANGULO domina, no las iteraciones
    # direccion=0.8 -> bandas van a lo largo del pico
    # direccion=-0.8 -> bandas van cruzadas (tu bug de V57)
    # formula nueva: t = ang*ciclos + M*pequeño
    t_ang = ang[valid] / (2*np.pi) # 0-1
    t_rad = M[valid] * 0.008 # muy pequeño
    # combinacion alineada con picos
    t = (t_ang * ciclos * 0.3 + t_rad * direccion) % 1.0
    t = np.nan_to_num(t, nan=0.0)

    r_ = np.empty_like(t); g = np.empty_like(t); b = np.empty_like(t)
    mf = t<0.25; my=(t>=0.25)&(t<0.5); mc=(t>=0.5)&(t<0.75); mm=t>=0.75
    r_[mf]=255; g[mf]=30+180*t[mf]/0.25; b[mf]=180
    r_[my]=255; g[my]=255; b[my]=0
    r_[mc]=0; g[mc]=255; b[mc]=255
    r_[mm]=160+95*(t[mm]-0.75)/0.25; g[mm]=0; b[mm]=255

    # sombra 3D que sigue los picos
    shade = 0.55 + 0.45*np.cos(ang[valid]*3 + 0.5)
    shade = np.clip(shade**(1.0 - profundidad*0.3), 0.35, 1.0)

    r_ = (r_*shade).astype(np.uint8)
    g = (g*shade).astype(np.uint8)
    b = (b*shade).astype(np.uint8)

    img = np.zeros((h,w,3), dtype=np.uint8)
    img[valid] = np.stack([r_,g,b], axis=1)
    return img

W=800; H=800
img = julia_alineado(W,H,c,zoom,iters,ciclos,profundidad,direccion)
st.image(img, use_container_width=True, channels="RGB")
st.info(f"DIRECCION={direccion}: 0.8=bandas a lo largo del pico (como tu ref), 0=bandas rectas, -0.8=bandas rodeando el pico (bug de V57). Dejalo en 0.7-0.9")

with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_alineado(resolucion,resolucion,c,zoom,iters,ciclos,profundidad,direccion)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_V58_ALINEADO_DIA{dia}.png",mime="image/png")
