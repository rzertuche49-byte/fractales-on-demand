import streamlit as st
import numpy as np
from PIL import Image
import io

st.set_page_config(layout="wide", page_title="FRACTALES ON DEMAND V17")
st.title("FRACTALES BAJO DEMANDA - V17 VETAS GORDAS")

with st.sidebar:
    st.header("Controles REFERENCIA")
    dia = st.slider("DIA (1-365)", 1, 365, 75)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.20, 0.05)
    iters = st.slider("CALIDAD (iters)", 200, 2000, 800)
    resolucion = st.selectbox("Resolucion Exportar", [1000, 2000, 3000, 4000], index=0)
    st.divider()
    fondo_transparente = st.checkbox("Fondo Transparente", value=False)
    flujo = st.slider("Fuerza Flujo (ondas seda)", 0.1, 3.0, 0.85, 0.05)
    densidad = st.slider("Densidad Color", 0.02, 0.5, 0.12, 0.01)
    rotacion = st.slider("Rotacion Tono", 0.0, 6.28, 2.5, 0.05)

c = complex(-0.74543, 0.11301) if 70 <= dia <= 80 else complex(0.7885*np.cos((dia/365)*2*np.pi*3), 0.7885*np.sin((dia/365)*2*np.pi*3))
st.write(f"c = {c} | V17 vetas gordas como referencia")

def julia_vetas(w, h, c, zoom, iters, flujo, densidad, rotacion):
    x_range = 3.0 / zoom
    y_range = 3.0 / zoom
    x = np.linspace(-x_range/2, x_range/2, w)
    y = np.linspace(-y_range/2, y_range/2, h)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    M = np.zeros(Z.shape)
    Zf = np.zeros(Z.shape, dtype=complex)
    Af = np.zeros(Z.shape)
    for i in range(iters):
        mask = np.abs(Z) <= 100
        if not np.any(mask): break
        Z[mask] = Z[mask]**2 + c
        M[mask] = i
        Zf[mask] = Z[mask]
        Af[mask] = np.angle(Z[mask])
    with np.errstate(divide='ignore', invalid='ignore'):
        log_zn = np.log(np.abs(Zf)+1e-10)
        mu = M + 2 - log_zn / np.log(2)
        mu = np.nan_to_num(mu, nan=0)

    # VETAS GORDAS: flujo bajo = pocas vetas, flujo alto = muchas rayas finas
    t = Af * flujo + mu * densidad * 0.15 + rotacion

    # Paleta exacta referencia: rosa, amarillo, cian, morado
    r = (0.5 + 0.5 * np.sin(t * 1.0 + 0.0)) * 255
    g = (0.5 + 0.5 * np.sin(t * 1.0 + 2.1)) * 255
    b = (0.5 + 0.5 * np.sin(t * 1.0 + 4.1)) * 255
    r = np.clip(r*1.3,0,255); g=np.clip(g*1.15,0,255); b=np.clip(b*1.4,0,255)
    img = np.stack([r,g,b], axis=-1).astype(np.uint8)
    interior = M >= iters-3
    img[interior]=[0,0,0]
    img[M < 1.5]=[0,0,0]
    return img, interior

W=900; H=900
img_preview, interior = julia_vetas(W, H, c, zoom, iters, flujo, densidad, rotacion)
st.image(img_preview, use_container_width=True, channels="RGB")

st.sidebar.divider()
if st.sidebar.button("Generar Export Alta"):
    with st.spinner(f"Generando {resolucion}x{resolucion}..."):
        img_hi, interior_hi = julia_vetas(resolucion, resolucion, c, zoom, iters, flujo, densidad, rotacion)
        if fondo_transparente:
            alpha = np.ones((resolucion,resolucion),dtype=np.uint8)*255
            alpha[interior_hi]=0
            img_pil=Image.fromarray(img_hi).convert("RGBA")
            img_pil.putalpha(Image.fromarray(alpha))
        else:
            img_pil=Image.fromarray(img_hi)
        buf=io.BytesIO(); img_pil.save(buf, format="PNG")
        st.sidebar.download_button("Descargar PNG", buf.getvalue(), file_name=f"fractal_V17_DIA{dia}.png", mime="image/png")
