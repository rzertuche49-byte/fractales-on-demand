import streamlit as st
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import io

st.set_page_config(layout="wide", page_title="FRACTALES ON DEMAND V9")
st.title("FRACTALES ON DEMAND - V9 ESPIRALES SEDA")

with st.sidebar:
    st.header("Controles")
    # Este DIA es el que da tu forma de espiral
    dia = st.slider("DIA (1-365)", 1, 365, 75)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.0, 0.05)
    iters = st.slider("CALIDAD (iters)", 200, 2000, 1200)
    resolucion = st.selectbox("Resolucion Export", [1000, 2000, 3000, 4000], index=2)
    st.divider()
    estilo = st.selectbox("Estilo", ["SEDA PSICODELICA (tu foto)", "ARCOIRIS"])
    fondo_transparente = st.checkbox("Fondo Transparente", value=False)
    suavidad = st.slider("Suavidad Flujo", 1.0, 20.0, 8.0)
    rotacion = st.slider("Rotacion Tono", 0.0, 1.0, 0.55)

# c que genera la forma de tu foto - 3 espirales centrales
def get_c(dia):
    if 70 <= dia <= 80: # Sweet spot para tu foto
        return complex(-0.74543, 0.11301)
    angle = (dia / 365.0) * 2 * np.pi * 3
    r = 0.7885
    return complex(r * np.cos(angle), r * np.sin(angle))

c = get_c(dia)
st.write(f"c = {c} | ESTA es la forma de tu foto")

def crear_colormap(estilo):
    if estilo == "SEDA PSICODELICA (tu foto)":
        # Paleta exacta de tu foto: magenta, morado, turquesa, amarillo
        colors = ["#000000", "#1a0b3e", "#7a1fa2", "#ff00aa", "#ffcc00", "#00ffea", "#7a1fa2", "#ff00aa", "#ffcc00"]
        # Quitamos negro inicial para flujo
        colors = ["#3d0a6e", "#7a1fa2", "#d91a9e", "#ff00aa", "#ffaa00", "#ffcc00", "#00e5ff", "#00ffea", "#7a1fa2"]
        return LinearSegmentedColormap.from_list("seda", colors, N=4096)
    else:
        return plt.cm.hsv

def julia_seda(w, h, c, zoom, iters, cmap, suavidad, rotacion, transparente):
    x_range = 3.5 / zoom
    y_range = 3.5 / zoom
    x = np.linspace(-x_range/2, x_range/2, w)
    y = np.linspace(-y_range/2, y_range/2, h)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    M = np.zeros(Z.shape)
    # Guardamos angulo final para efecto seda
    Z_final = np.zeros(Z.shape, dtype=complex)
    for i in range(iters):
        mask = np.abs(Z) <= 4
        if not np.any(mask):
            break
        Z[mask] = Z[mask]**2 + c
        M[mask] = i
        Z_final[mask] = Z[mask]

    with np.errstate(divide='ignore', invalid='ignore'):
        # TRUCO DE TU FOTO: orbit trap + smooth
        smooth = M + 1 - np.log(np.log(np.abs(Z)+1e-10))/np.log(2)
        # Flujo de seda: mezcla de potencial y angulo final
        flow = np.log(np.abs(Z_final)+1e-10) * 0.5 + np.angle(Z_final) * suavidad * 0.1
        norm = (smooth * 0.05 + flow * 0.15) + rotacion
        norm = norm % 1.0
        norm = np.nan_to_num(norm, nan=0)

    interior_mask = M >= iters-5
    colored = cmap(norm)
    img_array = (colored[:, :, :3] * 255).astype(np.uint8)
    # Fondo negro puro como tu foto
    if not transparente:
        img_array[interior_mask] = [0,0,0]
    else:
        img_array[interior_mask] = [0,0,0]
    return img_array, interior_mask

W = 900
H = 900
cmap = crear_colormap(estilo)
img_preview, mask = julia_seda(W, H, c, zoom, iters, cmap, suavidad, rotacion, fondo_transparente)
st.image(img_preview, use_container_width=True, channels="RGB")

st.sidebar.divider()
if st.sidebar.button("Generar Export Alta"):
    with st.spinner(f"Generando {resolucion}x{resolucion}..."):
        img_hi, mask_hi = julia_seda(resolucion, resolucion, c, zoom, iters, cmap, suavidad, rotacion, fondo_transparente)
        if fondo_transparente:
            alpha = np.ones((resolucion, resolucion), dtype=np.uint8) * 255
            alpha[mask_hi] = 0
            img_pil = Image.fromarray(img_hi).convert("RGBA")
            img_pil.putalpha(Image.fromarray(alpha))
        else:
            img_pil = Image.fromarray(img_hi)
        buf = io.BytesIO()
        img_pil.save(buf, format="PNG")
        st.sidebar.download_button("Descargar PNG", buf.getvalue(), file_name=f"fractal_SEDA_DIA{dia}.png", mime="image/png")
