import streamlit as st
import numpy as np
from PIL import Image
from matplotlib.colors import LinearSegmentedColormap
import io

st.set_page_config(layout="wide", page_title="FRACTALES ON DEMAND V11")
st.title("FRACTALES BAJO DEMANDA - V11 SEDA REAL")

with st.sidebar:
    st.header("Controles")
    dia = st.slider("DIA (1-365)", 1, 365, 75)
    zoom = st.slider("ZOOM", 0.2, 4.0, 0.65, 0.05)
    iters = st.slider("CALIDAD (iters)", 200, 2000, 800)
    resolucion = st.selectbox("Resolucion Exportar", [1000, 2000, 3000, 4000], index=0)
    st.divider()
    fondo_transparente = st.checkbox("Fondo Transparente", value=False)
    detalle = st.slider("Detalle Espiral", 0.5, 10.0, 3.0)
    rotacion = st.slider("Rotacion Tono", 0.0, 1.0, 0.55)

def get_c(dia):
    if 70 <= dia <= 80:
        return complex(-0.74543, 0.11301)
    angle = (dia / 365.0) * 2 * np.pi * 3
    r = 0.7885
    return complex(r * np.cos(angle), r * np.sin(angle))

c = get_c(dia)
st.write(f"c = {c} | ZOOM {zoom}")

def crear_colormap():
    # Colores exactos de tu foto: magenta, amarillo, cyan, morado
    colors = ["#1a0b3e", "#8a2be2", "#ff1493", "#ffcc00", "#ffaa00", "#00f5ff", "#00ced1", "#8a2be2", "#ff1493", "#ffcc00", "#00f5ff"]
    return LinearSegmentedColormap.from_list("seda_real", colors, N=4096)

def julia_real(w, h, c, zoom, iters, cmap, detalle, rotacion):
    x_range = 3.2 / zoom
    y_range = 3.2 / zoom
    x = np.linspace(-x_range/2, x_range/2, w)
    y = np.linspace(-y_range/2, y_range/2, h)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    M = np.zeros(Z.shape)
    Arg = np.zeros(Z.shape)

    for i in range(iters):
        mask = np.abs(Z) <= 4
        if not np.any(mask):
            break
        Z[mask] = Z[mask]**2 + c
        M[mask] = i
        Arg[mask] = np.angle(Z[mask])

    with np.errstate(divide='ignore', invalid='ignore'):
        # Suavizado continuo real
        log_zn = np.log(np.abs(Z)+1e-10) / np.log(2)
        smooth = M + 1 - np.log(log_zn+1e-10)/np.log(2)
        smooth = np.nan_to_num(smooth, nan=0)

        # TRUCO SEDA REAL: seno para que no haya corte de bloques
        # Esto crea el flujo ondulado de tu foto
        flow = np.sin(Arg * detalle + smooth * 0.15) * 0.5 + 0.5
        # Combina smooth + flow para bandas suaves continuas
        norm = (smooth * 0.04 + flow * 0.25 + rotacion) % 1.0

    interior = M >= iters-2
    colored = cmap(norm)
    img = (colored[:, :, :3] * 255).astype(np.uint8)
    img[interior] = [0,0,0]
    return img, interior

W = 900
H = 900
cmap = crear_colormap()
img_preview, mask = julia_real(W, H, c, zoom, iters, cmap, detalle, rotacion)
st.image(img_preview, use_container_width=True, channels="RGB")

st.sidebar.divider()
if st.sidebar.button("Generar Export Alta"):
    with st.spinner(f"Generando {resolucion}x{resolucion}..."):
        img_hi, mask_hi = julia_real(resolucion, resolucion, c, zoom, iters, cmap, detalle, rotacion)
        if fondo_transparente:
            alpha = np.ones((resolucion, resolucion), dtype=np.uint8) * 255
            alpha[mask_hi] = 0
            img_pil = Image.fromarray(img_hi).convert("RGBA")
            img_pil.putalpha(Image.fromarray(alpha))
        else:
            img_pil = Image.fromarray(img_hi)
        buf = io.BytesIO()
        img_pil.save(buf, format="PNG")
        st.sidebar.download_button("Descargar PNG", buf.getvalue(), file_name=f"fractal_V11_DIA{dia}.png", mime="image/png")
