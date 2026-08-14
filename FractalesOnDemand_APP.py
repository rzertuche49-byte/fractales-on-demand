import streamlit as st
import numpy as np
from PIL import Image
from matplotlib.colors import LinearSegmentedColormap
import io

st.set_page_config(layout="wide", page_title="FRACTALES ON DEMAND V12")
st.title("FRACTALES BAJO DEMANDA - V12 SEDA LISA")

with st.sidebar:
    st.header("Controles")
    dia = st.slider("DIA (1-365)", 1, 365, 75)
    zoom = st.slider("ZOOM", 0.2, 4.0, 0.65, 0.05)
    iters = st.slider("CALIDAD (iters)", 200, 2000, 1200)
    resolucion = st.selectbox("Resolucion Exportar", [1000, 2000, 3000, 4000], index=0)
    st.divider()
    fondo_transparente = st.checkbox("Fondo Transparente", value=False)
    ondas = st.slider("Ondas Suaves", 0.0, 3.0, 0.6)
    rotacion = st.slider("Rotacion Tono", 0.0, 1.0, 0.55)

def get_c(dia):
    return complex(-0.74543, 0.11301) if 70 <= dia <= 80 else complex(0.7885*np.cos((dia/365)*2*np.pi*3), 0.7885*np.sin((dia/365)*2*np.pi*3))

c = get_c(dia)
st.write(f"c = {c} | Ondas {ondas} - Para tu foto usa 0.5 a 0.8")

def crear_colormap():
    # Paleta exacta de tu foto original: fucsia, amarillo, turquesa, morado oscuro
    colors = ["#0d0221", "#2a0a4a", "#7a1fa2", "#d91a9e", "#ff006a", "#ff8a00", "#ffcc00", "#ffee88", "#00f5ff", "#00ffea", "#2a0a4a", "#ff006a", "#ffcc00"]
    return LinearSegmentedColormap.from_list("final", colors, N=8192)

def julia_lisa(w, h, c, zoom, iters, cmap, ondas, rotacion):
    x_range = 3.2 / zoom
    y_range = 3.2 / zoom
    x = np.linspace(-x_range/2, x_range/2, w)
    y = np.linspace(-y_range/2, y_range/2, h)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    M = np.full(Z.shape, iters, dtype=float)
    Az = np.zeros(Z.shape)

    for i in range(iters):
        mask = np.abs(Z) <= 4
        if not np.any(mask): break
        M[~mask & (M==iters)] = i
        Z[mask] = Z[mask]**2 + c
        Az[mask] = np.angle(Z[mask])

    with np.errstate(divide='ignore', invalid='ignore'):
        # Color liso real de tu foto
        mu = M + 1 - np.log(np.log(np.abs(Z)+1e-10)+1e-10)/np.log(2)
        mu = np.nan_to_num(mu, nan=0)
        # Solo un toquecito de onda, no rayos
        flow = np.sin(Az*ondas + mu*0.08) * 0.08 if ondas>0.1 else 0
        norm = (mu * 0.035 + flow + rotacion) % 1.0

    interior = M >= iters-2
    colored = cmap(norm)
    img = (colored[:,:,:3]*255).astype(np.uint8)
    img[interior] = [0,0,0]
    return img, interior

W=900; H=900
cmap=crear_colormap()
img_preview, mask = julia_lisa(W, H, c, zoom, iters, cmap, ondas, rotacion)
st.image(img_preview, use_container_width=True, channels="RGB")

st.sidebar.divider()
if st.sidebar.button("Generar Export Alta"):
    with st.spinner(f"Generando {resolucion}x{resolucion}..."):
        img_hi, mask_hi = julia_lisa(resolucion, resolucion, c, zoom, iters, cmap, ondas, rotacion)
        if fondo_transparente:
            alpha = np.ones((resolucion,resolucion),dtype=np.uint8)*255
            alpha[mask_hi]=0
            img_pil=Image.fromarray(img_hi).convert("RGBA")
            img_pil.putalpha(Image.fromarray(alpha))
        else:
            img_pil=Image.fromarray(img_hi)
        buf=io.BytesIO(); img_pil.save(buf, format="PNG")
        st.sidebar.download_button("Descargar PNG", buf.getvalue(), file_name=f"fractal_V12_DIA{dia}.png", mime="image/png")
