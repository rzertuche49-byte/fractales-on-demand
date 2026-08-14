import streamlit as st
import numpy as np
from PIL import Image
import io

st.set_page_config(layout="wide", page_title="FRACTALES ON DEMAND V15")
st.title("FRACTALES BAJO DEMANDA - V15 FONDO NEGRO REAL")

with st.sidebar:
    st.header("Controles")
    dia = st.slider("DIA (1-365)", 1, 365, 75)
    zoom = st.slider("ZOOM", 0.2, 4.0, 0.65, 0.05)
    iters = st.slider("CALIDAD (iters)", 200, 2000, 1200)
    resolucion = st.selectbox("Resolucion Exportar", [1000, 2000, 3000, 4000], index=0)
    st.divider()
    fondo_transparente = st.checkbox("Fondo Transparente (solo playera)", value=False)
    densidad = st.slider("Densidad Color", 0.01, 0.80, 0.35, 0.01)
    rotacion = st.slider("Rotacion Tono", 0.0, 6.28, 4.00, 0.05)
    aura = st.slider("Tamano Aura", 5, 100, 30)

c = complex(-0.74543, 0.11301) if 70 <= dia <= 80 else complex(0.7885*np.cos((dia/365)*2*np.pi*3), 0.7885*np.sin((dia/365)*2*np.pi*3))
st.write(f"c = {c} | V15 Fondo negro real como tu foto")

def julia_negro(w, h, c, zoom, iters, densidad, rotacion, aura):
    x_range = 3.2 / zoom
    y_range = 3.2 / zoom
    x = np.linspace(-x_range/2, x_range/2, w)
    y = np.linspace(-y_range/2, y_range/2, h)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    M = np.zeros(Z.shape)
    for i in range(iters):
        mask = np.abs(Z) <= 4
        if not np.any(mask): break
        Z[mask] = Z[mask]**2 + c
        M[mask] = i
    with np.errstate(divide='ignore', invalid='ignore'):
        mu = M + 1 - np.log(np.log(np.abs(Z)+1e-10)+1e-10)/np.log(2)
        mu = np.nan_to_num(mu, nan=0)

    t = mu * densidad + rotacion
    r = (0.5 + 0.5 * np.sin(t * 1.0 + 0.0)) * 255
    g = (0.5 + 0.5 * np.sin(t * 1.0 + 2.1)) * 255
    b = (0.5 + 0.5 * np.sin(t * 1.2 + 4.2)) * 255
    r = np.clip(r * 1.3, 0, 255); g = np.clip(g * 1.2, 0, 255); b = np.clip(b * 1.4, 0, 255)
    img = np.stack([r,g,b], axis=-1).astype(np.uint8)

    # FONDO NEGRO REAL - clave de tu foto
    interior = M >= iters-2
    fondo_lejano = M < aura # Todo lo que escapa muy rapido = fondo negro
    img[interior] = [0,0,0]
    img[fondo_lejano] = [0,0,0]

    return img, interior, fondo_lejano

W=900; H=900
img_preview, interior, fondo = julia_negro(W, H, c, zoom, iters, densidad, rotacion, aura)
st.image(img_preview, use_container_width=True, channels="RGB")

st.sidebar.divider()
if st.sidebar.button("Generar Export Alta"):
    with st.spinner(f"Generando {resolucion}x{resolucion}..."):
        img_hi, interior_hi, fondo_hi = julia_negro(resolucion, resolucion, c, zoom, iters, densidad, rotacion, aura)
        if fondo_transparente:
            alpha = np.ones((resolucion,resolucion),dtype=np.uint8)*255
            alpha[interior_hi]=0
            alpha[fondo_hi]=0
            img_pil=Image.fromarray(img_hi).convert("RGBA")
            img_pil.putalpha(Image.fromarray(alpha))
        else:
            img_pil=Image.fromarray(img_hi)
        buf=io.BytesIO(); img_pil.save(buf, format="PNG")
        st.sidebar.download_button("Descargar PNG", buf.getvalue(), file_name=f"fractal_V15_DIA{dia}.png", mime="image/png")
