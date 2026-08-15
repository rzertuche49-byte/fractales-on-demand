import streamlit as st
import numpy as np
from PIL import Image
import io
import math

st.set_page_config(layout="wide", page_title="V50 NEON REAL")
st.title("FRACTALES BAJO DEMANDA - V50 NEON REAL")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 258)
    zoom = st.slider("ZOOM", 0.2, 4.0, 0.85, 0.05)
    iters = st.slider("CALIDAD", 200, 3000, 1500)
    resolucion = st.selectbox("Resolucion", [1000, 2000, 3000, 4000], index=2)
    ciclos = st.slider("Detalle bandas", 5.0, 50.0, 28.0, 0.5)

def dia_to_c(dia):
    t = dia / 365.0 * 2 * math.pi
    r = 0.05
    cx = -0.065 + r*math.cos(t)
    cy = 0.566 + r*math.sin(t)
    return complex(cx, cy)

c = dia_to_c(dia)
st.caption(f"DIA {dia} -> c = {c.real:.5f} + {c.imag:.5f}i | PALETA NEON REF")

def julia_neon(w,h,c,zoom,iters,ciclos):
    x = np.linspace(-1.8/zoom, 1.8/zoom, w)
    y = np.linspace(-1.8/zoom, 1.8/zoom, h)
    X,Y = np.meshgrid(x,y)
    Z = X + 1j*Y
    M = np.full(Z.shape, iters, dtype=float)

    for i in range(iters):
        mask = np.abs(Z) < 1000
        esc = mask & (np.abs(Z) > 2) & (M==iters)
        if np.any(esc):
            M[esc] = i + 1 - np.log2(np.log(np.abs(Z[esc])+1e-10)+1)
        Z[mask] = Z[mask]**2 + c
        if not np.any(mask):
            break

    valid = M < iters
    # Bandas super finas
    t = (M[valid] * ciclos * 0.08) % 1.0

    # PALETA NEON REAL: fucsia, amarillo, turquesa, rosa, morado
    # Interpolacion coseno con colores puros
    # fucsia 255,20,147 | amarillo 255,255,0 | turquesa 0,255,255 | morado 180,0,255
    r = (128 + 127*np.sin(2*math.pi*t + 0.0)).astype(float)
    g = (128 + 127*np.sin(2*math.pi*t + 2.0)).astype(float)
    b = (128 + 127*np.sin(2*math.pi*t + 4.0)).astype(float)

    # Boost neón para que no se haga olivo
    r = np.clip(r*1.5, 0, 255)
    g = np.clip(g*1.3, 0, 255)
    b = np.clip(b*1.5, 0, 255)

    # Mezcla a colores exactos de tu ref
    # Cuando t esta en 0-0.25 = fucsia, 0.25-0.5=amarillo, 0.5-0.75=turquesa, 0.75-1=morado
    mask_f = t < 0.25
    mask_y = (t >= 0.25) & (t < 0.5)
    mask_c = (t >= 0.5) & (t < 0.75)
    mask_m = t >= 0.75

    r[mask_f] = 255
    g[mask_f] = 20 + 100*(t[mask_f]/0.25)
    b[mask_f] = 147 + 50*(t[mask_f]/0.25)

    r[mask_y] = 255
    g[mask_y] = 255
    b[mask_y] = 0 + 100*((t[mask_y]-0.25)/0.25)

    r[mask_c] = 0 + 100*((t[mask_c]-0.5)/0.25)
    g[mask_c] = 255
    b[mask_c] = 255

    r[mask_m] = 120 + 135*((t[mask_m]-0.75)/0.25)
    g[mask_m] = 0 + 80*((t[mask_m]-0.75)/0.25)
    b[mask_m] = 255

    img = np.zeros((h,w,3), dtype=np.uint8)
    img[valid] = np.stack([r.astype(np.uint8), g.astype(np.uint8), b.astype(np.uint8)], axis=1)
    img[~valid] = [0,0,0]
    return img

W=900; H=900
img = julia_neon(W,H,c,zoom,iters,ciclos)
st.image(img, use_container_width=True, channels="RGB")

with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_neon(resolucion,resolucion,c,zoom,iters,ciclos)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_NEON_DIA{dia}.png",mime="image/png")
