import streamlit as st
import numpy as np
from PIL import Image
import io

st.set_page_config(layout="wide", page_title="FRACTALES ON DEMAND V20")
st.title("FRACTALES BAJO DEMANDA - V20 FINAL REFERENCIA")

with st.sidebar:
    st.header("Controles REFERENCIA")
    dia = st.slider("DIA (1-365)", 1, 365, 75)
    zoom = st.slider("ZOOM", 0.2, 4.0, 0.75, 0.05)
    iters = st.slider("CALIDAD (iters)", 200, 2000, 700)
    resolucion = st.selectbox("Resolucion Exportar", [1000, 2000, 3000, 4000], index=0)
    st.divider()
    fondo_transparente = st.checkbox("Fondo Transparente", value=False)
    vetas = st.slider("Num Vetass gordas", 0.5, 6.0, 1.4, 0.1)
    suavidad = st.slider("Suavidad flujo", 0.05, 2.0, 0.35, 0.05)
    rotacion = st.slider("Rotacion Tono", 0.0, 6.28, 5.8, 0.05)

c = complex(-0.74543, 0.11301) if 70 <= dia <= 80 else complex(0.7885*np.cos((dia/365)*2*np.pi*3), 0.7885*np.sin((dia/365)*2*np.pi*3))
st.write(f"c = {c} | V20 paleta referencia original")

def julia_final_ref(w, h, c, zoom, iters, vetas, suavidad, rotacion):
    x_range = 3.0 / zoom
    y_range = 3.0 / zoom
    x = np.linspace(-x_range/2, x_range/2, w)
    y = np.linspace(-y_range/2, y_range/2, h)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    M = np.zeros(Z.shape)
    tia = np.zeros(Z.shape)
    cnt = np.zeros(Z.shape)
    for i in range(iters):
        mask = np.abs(Z) <= 10
        if not np.any(mask): break
        tia[mask] += np.abs(Z[mask])
        cnt[mask] += 1
        Z[mask] = Z[mask]**2 + c
        M[mask] = i
    with np.errstate(divide='ignore', invalid='ignore'):
        tia_avg = tia / (cnt + 1e-10)
        tia_s = np.log(tia_avg + 1.0)
        tia_s = np.nan_to_num(tia_s, nan=0)

    t = tia_s * vetas + M * suavidad * 0.015 + rotacion

    # PALETA NEON EXACTA DE TU FOTO 1: fucsia #ff006a, amarillo #ffcc00, turquesa #00ffea, morado #7a1fa2
    r = (0.5 + 0.5 * np.sin(t + 0.0)) * 255
    g = (0.5 + 0.5 * np.sin(t + 2.0)) * 255
    b = (0.5 + 0.5 * np.sin(t + 4.0)) * 255
    # Boost neon
    r = np.clip(r*1.5,0,255); g=np.clip(g*1.35,0,255); b=np.clip(b*1.5,0,255)

    img = np.stack([r,g,b], axis=-1).astype(np.uint8)
    interior = M >= iters-5
    img[interior]=[0,0,0]
    # Fondo negro limpio
    img[M < 2]=[0,0,0]
    # Sombreado para relieve
    shade = np.clip(M/80.0, 0, 1)
    img = (img * (0.3 + 0.7*shade[:,:,None])).astype(np.uint8)
    img[interior]=[0,0,0]
    return img, interior

W=900; H=900
img_preview, interior = julia_final_ref(W, H, c, zoom, iters, vetas, suavidad, rotacion)
st.image(img_preview, use_container_width=True, channels="RGB")
st.success("CONFIG REFERENCIA ORIGINAL: ZOOM 0.75, VETAS 1.4, SUAVIDAD 0.35, ROTACION 5.8")

st.sidebar.divider()
if st.sidebar.button("Generar Export Alta"):
    with st.spinner(f"Generando {resolucion}x{resolucion}..."):
        img_hi, interior_hi = julia_final_ref(resolucion, resolucion, c, zoom, iters, vetas, suavidad, rotacion)
        if fondo_transparente:
            alpha = np.ones((resolucion,resolucion),dtype=np.uint8)*255
            alpha[interior_hi]=0
            img_pil=Image.fromarray(img_hi).convert("RGBA")
            img_pil.putalpha(Image.fromarray(alpha))
        else:
            img_pil=Image.fromarray(img_hi)
        buf=io.BytesIO(); img_pil.save(buf, format="PNG")
        st.sidebar.download_button("Descargar PNG", buf.getvalue(), file_name=f"fractal_V20_FINAL_DIA{dia}.png", mime="image/png")
