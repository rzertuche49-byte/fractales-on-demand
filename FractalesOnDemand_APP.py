import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V54 PICOS REAL")
st.title("FRACTALES BAJO DEMANDA - V54 PICOS QUE SI FUNCIONAN")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 273)
    zoom = st.slider("ZOOM", 0.2, 4.0, 2.90, 0.05)
    iters = st.slider("PICOS / CALIDAD", 100, 2500, 381, 50)
    ciclos = st.slider("Detalle bandas", 5.0, 50.0, 28.0, 0.5)
    profundidad = st.slider("Profundidad 3D", 0.0, 1.5, 0.60, 0.1)
    resolucion = st.selectbox("Resolucion", [1000,2000,3000,4000], index=1)

def dia_to_c_seguro(dia):
    t = dia/365*2*math.pi
    r = 0.008
    # c que da MUCHOS picos: -0.7269+0.1889 es famoso por dendritas
    cx = -0.7269 + r*math.cos(t*4)
    cy = 0.1889 + r*math.sin(t*4)
    return complex(cx, cy)

c = dia_to_c_seguro(dia)
st.caption(f"DIA {dia} -> c={c.real:.5f}+{c.imag:.5f}i | PICOS={iters} | ZOOM {zoom} | Si subes PICOS se alargan las ramitas")

def julia_picos_reales(w,h,c,zoom,iters,ciclos,profundidad):
    x = np.linspace(-1.5/zoom, 1.5/zoom, w)
    y = np.linspace(-1.5/zoom, 1.5/zoom, h)
    X,Y = np.meshgrid(x,y)
    Z = X+1j*Y
    M = np.full(Z.shape, iters, dtype=float)
    ang = np.zeros(Z.shape)
    # guardamos iter de escape para picos
    escaped_at = np.full(Z.shape, iters)

    for i in range(iters):
        mask = np.abs(Z) <= 10
        esc = mask & (np.abs(Z) > 2) & (M==iters)
        if np.any(esc):
            M[esc] = i + 1 - np.log2(np.log(np.abs(Z[esc])+1e-10))
            ang[esc] = np.angle(Z[esc])
            escaped_at[esc] = i
        Z[mask] = Z[mask]*Z[mask] + c
        if not np.any(mask):
            break

    valid = M < iters
    # ANTI-RUIDO INTELIGENTE: solo quitamos los que escapan en 0-2 iter Y estan muy lejos del centro
    # asi conservamos picos
    is_noise = (escaped_at <= 2) & (np.abs(X+1j*Y) > 0.8/zoom)
    limpio = valid & (~is_noise)

    t = (M[limpio] * ciclos * 0.06 + ang[limpio]*0.35) % 1.0

    r = np.empty_like(t); g = np.empty_like(t); b = np.empty_like(t)
    mf = t<0.25; my=(t>=0.25)&(t<0.5); mc=(t>=0.5)&(t<0.75); mm=t>=0.75
    r[mf]=255; g[mf]=30+180*t[mf]/0.25; b[mf]=180
    r[my]=255; g[my]=255; b[my]=0
    r[mc]=0; g[mc]=255; b[mc]=255
    r[mm]=160+95*(t[mm]-0.75)/0.25; g[mm]=0; b[mm]=255

    # sombra 3D que depende de PICOS: mas iters = sombra mas profunda
    shade = 0.55 + 0.45*np.cos(ang[limpio]*2 + 1.2)
    shade = np.clip(shade**(1.0 - profundidad*0.3), 0.35, 1.0)

    r = (r*shade).astype(np.uint8)
    g = (g*shade).astype(np.uint8)
    b = (b*shade).astype(np.uint8)

    img = np.zeros((h,w,3), dtype=np.uint8)
    img[limpio] = np.stack([r,g,b], axis=1)
    return img

W=800; H=800
img = julia_picos_reales(W,H,c,zoom,iters,ciclos,profundidad)
st.image(img, use_container_width=True, channels="RGB")
st.info(f"PICOS={iters}: con 300 ves tronquito pelon, con 1500+ ves arbol fractal completo como tu ref. Prueba subirlo a 1200")

with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_picos_reales(resolucion,resolucion,c,zoom,iters,ciclos,profundidad)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_V54_PICOS{iters}_DIA{dia}.png",mime="image/png")
