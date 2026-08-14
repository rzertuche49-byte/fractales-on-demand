import streamlit as st
import numpy as np
from PIL import Image
import io

st.set_page_config(layout="wide", page_title="FRACTALES ON DEMAND V14")
st.title("FRACTALES BAJO DEMANDA - V14 FINAL")

with st.sidebar:
    st.header("Controles")
    dia = st.slider("DIA (1-365)", 1, 365, 75)
    zoom = st.slider("ZOOM", 0.2, 4.0, 0.65, 0.05)
    iters = st.slider("CALIDAD (iters)", 200, 2000, 1200)
    resolucion = st.selectbox("Resolucion Exportar", [1000, 2000, 3000, 4000], index=0)
    st.divider()
    fondo_transparente = st.checkbox("Fondo Transparente (solo para playera)", value=False)
    densidad = st.slider("Densidad Color", 0.01, 0.50, 0.28, 0.01)
    rotacion = st.slider("Rotacion Tono", 0.0, 6.28, 4.00, 0.05)

c = complex(-0.74543, 0.11301) if 70 <= dia <= 80 else complex(0.7885*np.cos((dia/365)*2*np.pi*3), 0.7885*np.sin((dia/365)*2*np.pi*3))
st.write(f"c = {c} | Fondo NEGRO = como tu foto original | Fondo Transparente solo para exportar playera")

def julia_final(w, h, c, zoom, iters, densidad, rotacion, transparente):
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
    # Paleta psicodelica real fucsia-verde-azul de tu foto
    r = (0.5 + 0.5 * np.sin(t * 1.0 + 0.0)) * 255
    g = (0.5 + 0.5 * np.sin(t * 1.0 + 2.1)) * 255
    b = (0.5 + 0.5 * np.sin(t * 1.2 + 4.2)) * 255
    r = np.clip(r * 1.2, 0, 255); g = np.clip(g * 1.1, 0, 255); b = np.clip(b * 1.3, 0, 255)
    img = np.stack([r,g,b], axis=-1).astype(np.uint8)
    interior = M >= iters-2
    if transparente:
        # Para playera: interior negro se hace transparente en preview se ve rosa pero en PNG si es transparente
        # En preview mostramos negro para no confundir
        img[interior] = [0,0,0]
    else:
        img[interior] = [0,0,0]
    return img, interior

W=900; H=900
img_preview, mask = julia_final(W, H, c, zoom, iters, densidad, rotacion, fondo_transparente)
st.image(img_preview, use_container_width=True, channels="RGB")
st.info("TIP: Para clonar tu foto, deja Fondo Transparente DESACTIVADO. Solo activalo al exportar para playera.")

st.sidebar.divider()
if st.sidebar.button("Generar Export Alta"):
    with st.spinner(f"Generando {resolucion}x{resolucion}..."):
        img_hi, mask_hi = julia_final(resolucion, resolucion, c, zoom, iters, densidad, rotacion, fondo_transparente)
        if fondo_transparente:
            alpha = np.ones((resolucion,resolucion),dtype=np.uint8)*255
            alpha[mask_hi]=0
            # Tambien haz transparente el fondo lejano si quieres solo fractal
            # alpha[mu < 2] = 0 # descomenta si quieres solo la forma sin fondo
            img_pil=Image.fromarray(img_hi).convert("RGBA")
            img_pil.putalpha(Image.fromarray(alpha))
        else:
            img_pil=Image.fromarray(img_hi)
        buf=io.BytesIO(); img_pil.save(buf, format="PNG")
        st.sidebar.download_button("Descargar PNG", buf.getvalue(), file_name=f"fractal_V14_DIA{dia}.png", mime="image/png")
