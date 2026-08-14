import streamlit as st
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import io

st.set_page_config(layout="wide", page_title="FRACTALES ON DEMAND V6")
st.title("FRACTALES ON DEMAND - V6 PSYCHEDELIC")

with st.sidebar:
    st.header("Controles")
    dia = st.slider("DIA (1-365)", 1, 365, 200)
    zoom = st.slider("ZOOM", 0.5, 3.0, 1.15, 0.05)
    iters = st.slider("CALIDAD (iters)", 100, 1500, 800)
    resolucion = st.selectbox("Resolucion Export", [1000, 2000, 3000, 4000], index=2)
    st.divider()
    paleta_nombre = st.selectbox("Estilo de Color", ["PSICODELICO (como tu foto)", "ARCOIRIS PURO", "FUEGO NEON", "OCEANO ACIDO", "ORIGINAL ROSA"])
    fondo_transparente = st.checkbox("Fondo Transparente", value=True)
    potencia_color = st.slider("Intensidad Color", 0.5, 5.0, 2.5)
    rotacion_color = st.slider("Rotacion de Tono", 0.0, 1.0, 0.0)

angle = (dia / 365.0) * 2 * np.pi * 3
r = 0.7885
c = complex(r * np.cos(angle), r * np.sin(angle))
if dia == 200:
    c = complex(-0.148469, 0.741099)

st.write(f"DIA {dia} | c={c} | Paleta={paleta_nombre}")

def crear_colormap(nombre):
    if nombre == "PSICODELICO (como tu foto)":
        colors = ["#2a0a4a", "#7a1fa2", "#ff00cc", "#ffcc00", "#00ffea", "#7a1fa2", "#ff00cc", "#ff0066"]
        return LinearSegmentedColormap.from_list("psy", colors, N=1024)
    elif nombre == "ARCOIRIS PURO":
        return plt.cm.hsv
    elif nombre == "FUEGO NEON":
        colors = ["#ff0000", "#ff8800", "#ffff00", "#ffffff", "#ff00ff", "#ff0000"]
        return LinearSegmentedColormap.from_list("fuego", colors, N=1024)
    elif nombre == "OCEANO ACIDO":
        return plt.cm.turbo
    else:
        colors = ["#ff0040", "#ff8a00", "#e63e8a", "#ff0040"]
        return LinearSegmentedColormap.from_list("rosa", colors, N=1024)

def julia_psy(w, h, c, zoom, iters, cmap, potencia, rotacion, transparente):
    x_range = 3.0 / zoom
    y_range = 3.0 / zoom
    x = np.linspace(-x_range/2, x_range/2, w)
    y = np.linspace(-y_range/2, y_range/2, h)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    M = np.zeros(Z.shape)
    for i in range(iters):
        mask = np.abs(Z) <= 2
        if not np.any(mask):
            break
        Z[mask] = Z[mask]**2 + c
        M[mask] = i
    with np.errstate(divide='ignore', invalid='ignore'):
        smooth = M + 1 - np.log(np.log(np.abs(Z)+1e-10))/np.log(2)
        smooth = np.nan_to_num(smooth, nan=0)
    # FIX: normalizacion que no empieza en negro
    norm = (smooth / iters) * potencia + rotacion
    norm = norm % 1.0
    interior_mask = M >= iters-1
    colored = cmap(norm)
    img_array = (colored[:, :, :3] * 255).astype(np.uint8)
    # Si quiere transparente, pon interior negro puro para que luego sea alpha 0
    if transparente:
        img_array[interior_mask] = [0,0,0]
    return img_array, interior_mask

W = 800
H = 800
cmap = crear_colormap(paleta_nombre)
img_preview, mask = julia_psy(W, H, c, zoom, iters, cmap, potencia_color, rotacion_color, fondo_transparente)
st.image(img_preview, use_container_width=True, channels="RGB")

st.sidebar.divider()
if st.sidebar.button("Generar Export Alta"):
    with st.spinner(f"Generando {resolucion}x{resolucion}..."):
        img_hi, mask_hi = julia_psy(resolucion, resolucion, c, zoom, iters, cmap, potencia_color, rotacion_color, fondo_transparente)
        if fondo_transparente:
            alpha = np.ones((resolucion, resolucion), dtype=np.uint8) * 255
            alpha[mask_hi] = 0
            img_pil = Image.fromarray(img_hi).convert("RGBA")
            img_pil.putalpha(Image.fromarray(alpha))
        else:
            img_pil = Image.fromarray(img_hi)
        buf = io.BytesIO()
        img_pil.save(buf, format="PNG")
        st.sidebar.download_button("Descargar PNG", buf.getvalue(), file_name=f"fractal_DIA{dia}_{paleta_nombre}.png", mime="image/png")
