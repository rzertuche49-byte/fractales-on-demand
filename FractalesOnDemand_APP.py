import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V51 ULTRA 3D")
st.title("FRACTALES BAJO DEMANDA - V51 ULTRA 3D + PICOS + SOMBRAS")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 258)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.1, 0.05)
    potencia = st.slider("POTENCIA (espirales)", 2, 5, 3)
    iters = st.slider("PICOS / CALIDAD", 500, 4000, 2500)
    ciclos = st.slider("Detalle bandas", 5.0, 50.0, 28.0, 0.5)
    profundidad = st.slider("Profundidad 3D", 0.0, 1.5, 0.8, 0.1)
    luz = st.slider("Angulo luz sombra", 0.0, 6.28, 2.5, 0.1)
    resolucion = st.selectbox("Resolucion", [1000,2000,3000,4000], index=2)

def dia_to_c(dia):
    t = dia/365*2*math.pi
    # c exacto para espirales como tu ref: -0.12 + 0.75i es el corazon
    r = 0.015
    cx = -0.12 + r*math.cos(t*3)
    cy = 0.75 + r*math.sin(t*3)
    return complex(cx, cy)

c = dia_to_c(dia)
st.caption(f"DIA {dia} -> c={c} | Potencia={potencia} | Picos={iters}")

def julia_ultra(w,h,c,zoom,iters,ciclos,profundidad,luz,potencia):
    x = np.linspace(-1.8/zoom, 1.8/zoom, w)
    y = np.linspace(-1.8/zoom, 1.8/zoom, h)
    X,Y = np.meshgrid(x,y)
    Z = X+1j*Y
    M = np.full(Z.shape, iters, dtype=float)
    # para 3D
    dr = np.ones(Z.shape, dtype=complex)
    last_angle = np.zeros(Z.shape)

    for i in range(iters):
        mask = np.abs(Z) < 100
        esc = mask & (np.abs(Z) > 2) & (M==iters)
        if np.any(esc):
            M[esc] = i + 1 - np.log2(np.log(np.abs(Z[esc])+1e-10)+1)
            last_angle[esc] = np.angle(Z[esc])
        # derivada para 3D
        dr[mask] = dr[mask]*potencia* (Z[mask]**(potencia-1))
        Z[mask] = Z[mask]**potencia + c
        if not np.any(mask):
            break

    valid = M < iters
    t = (M[valid] * ciclos * 0.08 + last_angle[valid]*0.3) % 1.0

    # paleta neon ref
    r = np.empty_like(t); g = np.empty_like(t); b = np.empty_like(t)
    mf = t<0.25; my=(t>=0.25)&(t<0.5); mc=(t>=0.5)&(t<0.75); mm=t>=0.75
    r[mf]=255; g[mf]=20+200*t[mf]/0.25; b[mf]=147
    r[my]=255; g[my]=255; b[my]=200*(t[my]-0.25)/0.25
    r[mc]=100*(t[mc]-0.5)/0.25; g[mc]=255; b[mc]=255
    r[mm]=120+135*(t[mm]-0.75)/0.25; g[mm]=20; b[mm]=255

    # SOMBRAS 3D - distance estimation
    dist = np.abs(Z) * np.log(np.abs(Z)+1e-10) / (np.abs(dr)+1e-10)
    dist = dist[valid]
    normal_x = np.cos(last_angle[valid])
    normal_y = np.sin(last_angle[valid])
    light_x = math.cos(luz); light_y = math.sin(luz)
    shade = 0.4 + 0.6 * (normal_x*light_x + normal_y*light_y)
    shade = np.clip(shade, 0.2, 1.0)
    # picos = mas oscuro en grietas
    shade *= (0.6 + 0.4*np.clip(1 - dist*2, 0, 1)) ** profundidad

    r = (r*shade).astype(np.uint8)
    g = (g*shade).astype(np.uint8)
    b = (b*shade).astype(np.uint8)

    img = np.zeros((h,w,3), dtype=np.uint8)
    img[valid] = np.stack([r,g,b], axis=1)
    img[~valid] = [0,0,0]
    return img

W=900; H=900
img = julia_ultra(W,H,c,zoom,iters,ciclos,profundidad,luz,potencia)
st.image(img, use_container_width=True, channels="RGB")
with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_ultra(resolucion,resolucion,c,zoom,iters,ciclos,profundidad,luz,potencia)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_ULTRA_DIA{dia}.png",mime="image/png")
