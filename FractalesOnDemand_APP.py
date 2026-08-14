import streamlit as st
import numpy as np
from PIL import Image
import io

st.set_page_config(layout="wide", page_title="FRACTALES ON DEMAND V13")
st.title("FRACTALES BAJO DEMANDA - V13 FINAL LISO")

with st.sidebar:
    st.header("Controles")
    dia = st.slider("DIA (1-365)", 1, 365, 75)
    zoom = st.slider("ZOOM", 0.2, 4.0, 0.65, 0.05)
    iters = st.slider("CALIDAD (iters)", 200, 2000, 1200)
    resolucion = st.selectbox("Resolucion Exportar", [1000, 2000, 3000, 4000], index=0)
    st.divider()
    fondo_transparente = st.checkbox("Fondo Transparente", value=False)
    densidad = st.slider("Densidad Color", 0.01, 0.20, 0.06, 0.01)
    rotacion = st.slider("Rotacion Tono", 0.0, 6.28, 2.0)

c = complex(-0.74543, 0.11301) if 70 <= dia <= 80 else complex(0.7885*np.cos((dia/365)*2*np.pi*3), 0.7885*np.sin((dia/365)*2*np.pi*3))
st.write(f"c = {c} | Ya sin bloques - flujo continuo")

def julia_final(w, h, c, zoom, iters, densidad, rotacion):
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
        # Smooth continuo sin cortes
        mu = M + 1 - np.log(np.log(np.abs(Z)+1e-10)+1e-10)/np.log(2)
        mu = np.nan_to_num(mu, nan=0)

    # COLOR SEDA CONTINUO - SIN % BRUSCO, CON SENO
    # Esto es lo que usa tu foto: seno suave, no paleta cortada
    t = mu * densidad + rotacion
    # Formula seda psicodelica: 3 senos desfasados = tu fucsia-amarillo-turquesa
    r = (0.5 + 0.5 * np.sin(t * 1.0 + 0.0)) * 255
    g = (0.5 + 0.5 * np.sin(t * 1.0 + 2.1)) * 255
    b = (0.5 + 0.5 * np.sin(t * 1.2 + 4.2)) * 255
    # Boost para colores de tu foto: mas saturacion
    r = np.clip(r * 1.2, 0, 255)
    g = np.clip(g * 1.1, 0, 255)
    b = np.clip(b * 1.3, 0, 255)

    img = np.stack([r,g,b], axis=-1).astype(np.uint8)
    interior = M >= iters-2
    img[interior] = [0,0,0]
    return img, interior

W=900; H=900
img_preview, mask = julia_final(W, H, c, zoom, iters, densidad, rotacion)
st.image(img_preview, use_container_width=True, channels="RGB")

st.sidebar.divider()
if st.sidebar.button("Generar Export Alta"):
    with st.spinner(f"Generando {resolucion}x{resolucion}..."):
        img_hi, mask_hi = julia_final(resolucion, resolucion, c, zoom, iters, densidad, rotacion)
        if fondo_transparente:
            alpha = np.ones((resolucion,resolucion),dtype=np.uint8)*255
            alpha[mask_hi]=0
            img_pil=Image.fromarray(img_hi).convert("RGBA")
            img_pil.putalpha(Image.fromarray(alpha))
        else:
            img_pil=Image.fromarray(img_hi)
        buf=io.BytesIO(); img_pil.save(buf, format="PNG")
        st.sidebar.download_button("Descargar PNG", buf.getvalue(), file_name=f"fractal_V13_DIA{dia}.png", mime="image/png")
