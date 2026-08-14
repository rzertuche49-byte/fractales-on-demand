import streamlit as st
import numpy as np
from PIL import Image
from matplotlib.colors import LinearSegmentedColormap
import io

st.set_page_config(layout="wide", page_title="FRACTALES ON DEMAND V10")
st.title("FRACTALES BAJO DEMANDA - V10 SEDA FIX")

with st.sidebar:
    st.header("Controles")
    dia = st.slider("DIA (1-365)", 1, 365, 75)
    zoom = st.slider("ZOOM", 0.2, 4.0, 0.65, 0.05)
    iters = st.slider("CALIDAD (iters)", 200, 2000, 800)
    resolucion = st.selectbox("Resolucion Exportar", [1000, 2000, 3000, 4000], index=0)
    st.divider()
    estilo = st.selectbox("Estilo", ["SEDA PSICODELICA (tu foto)", "ARCOIRIS PURO"])
    fondo_transparente = st.checkbox("Fondo Transparente", value=False)
    suavidad = st.slider("Suavidad Flujo", 1.0, 20.0, 3.5)
    rotacion = st.slider("Rotacion Tono", 0.0, 1.0, 0.55)

def get_c(dia):
    if 70 <= dia <= 80:
        return complex(-0.74543, 0.11301)
    angle = (dia / 365.0) * 2 * np.pi * 3
    r = 0.7885
    return complex(r * np.cos(angle), r * np.sin(angle))

c = get_c(dia)
st.write(f"c = {c} | DIA {dia} - ZOOM {zoom} - Esta es la forma de tu foto")

def crear_colormap(estilo):
    colors = ["#1a0b3e", "#5d0e8a", "#b5179e", "#ff006a", "#ff7a00", "#ffcc00", "#00f5ff", "#00ffea", "#7a1fa2", "#ff00aa"]
    return LinearSegmentedColormap.from_list("seda", colors, N=4096)

def julia_seda_fix(w, h, c, zoom, iters, cmap, suavidad, rotacion, transparente):
    x_range = 3.5 / zoom
    y_range = 3.5 / zoom
    x = np.linspace(-x_range/2, x_range/2, w)
    y = np.linspace(-y_range/2, y_range/2, h)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    M = np.zeros(Z.shape)
    # Para seda necesitamos el ultimo angulo ANTES de escapar, no despues
    Ang = np.zeros(Z.shape)

    for i in range(iters):
        mask = np.abs(Z) <= 4
        if not np.any(mask):
            break
        # Guardamos angulo solo de los que van a escapar
        Ang[mask] = np.angle(Z[mask])
        Z[mask] = Z[mask]**2 + c
        M[mask] = i

    with np.errstate(divide='ignore', invalid='ignore'):
        # smooth continuo clasico sin ruido
        smooth = M + 1 - np.log(np.log(np.abs(Z)+1e-10)+1e-10)/np.log(2)
        smooth = np.nan_to_num(smooth, nan=0, posinf=0)
        # FIX DEL RUIDO: flujo suave = smooth*pequeño + angulo*suavidad
        # Antes multiplicabamos por log, ahora solo angulo
        flow = Ang * suavidad * 0.2
        norm = (smooth * 0.08 + flow) / 10.0 + rotacion
        norm = norm % 1.0

    interior_mask = M >= iters-2
    colored = cmap(norm)
    img_array = (colored[:, :, :3] * 255).astype(np.uint8)
    img_array[interior_mask] = [0,0,0]
    return img_array, interior_mask

W = 900
H = 900
cmap = crear_colormap(estilo)
img_preview, mask = julia_seda_fix(W, H, c, zoom, iters, cmap, suavidad, rotacion, fondo_transparente)
st.image(img_preview, use_container_width=True, channels="RGB")

st.sidebar.divider()
if st.sidebar.button("Generar Export Alta"):
    with st.spinner(f"Generando {resolucion}x{resolucion}..."):
        img_hi, mask_hi = julia_seda_fix(resolucion, resolucion, c, zoom, iters, cmap, suavidad, rotacion, fondo_transparente)
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
