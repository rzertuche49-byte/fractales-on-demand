import streamlit as st
import numpy as np
from PIL import Image
import io
st.set_page_config(layout="wide", page_title="FRACTALES ON DEMAND V26")
st.title("FRACTALES BAJO DEMANDA - V26")
with st.sidebar:
    modo = st.radio("Modo", ["Silueta Negra (tu ref original)", "Relleno Seda"], index=0)
    dia = st.slider("DIA (1-365)", 1, 365, 75)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.25, 0.05)
    iters = st.slider("CALIDAD (iters)", 200, 2000, 800)
    resolucion = st.selectbox("Resolucion Exportar", [1000, 2000, 3000, 4000], index=0)
    fondo_transparente = st.checkbox("Fondo Transparente", value=False)
    vetas = st.slider("Num Vetass gordas", 0.05, 2.0, 0.35, 0.05)
    suavidad = st.slider("Suavidad flujo", 0.02, 1.0, 0.25, 0.02)
    rotacion = st.slider("Rotacion Tono", 0.0, 6.28, 5.80, 0.05)
    brillo = st.slider("Brillo neon", 0.5, 2.5, 1.40, 0.05)
c = complex(-0.74543, 0.11301) if 70 <= dia <= 80 else complex(0.7885*np.cos((dia/365)*2*np.pi*3), 0.7885*np.sin((dia/365)*2*np.pi*3))
def julia_v26(w, h, c, zoom, iters, vetas, suavidad, rotacion, brillo, modo):
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
        mask = np.abs(Z) <= 10
        if not np.any(mask): break
        Z[mask] = Z[mask]**2 + c
        M[mask] = i
        Zf[mask] = Z[mask]
        Af[mask] = np.angle(Z[mask])
    log_r = np.log(np.abs(Zf)+1e-10)
    log_r = np.nan_to_num(log_r, nan=0)
    Af = np.nan_to_num(Af, nan=0)
    t = Af * vetas * 2.2 + log_r * suavidad * 0.6 + rotacion
    r = (0.5 + 0.5 * np.sin(t + 0.0)) * 255
    g = (0.5 + 0.5 * np.sin(t + 2.0)) * 255
    b = (0.5 + 0.5 * np.sin(t + 4.0)) * 255
    r = np.clip(r*1.5*brillo,0,255); g=np.clip(g*1.35*brillo,0,255); b=np.clip(b*1.5*brillo,0,255)
    img = np.stack([r,g,b], axis=-1).astype(np.uint8)
    if "Silueta" in modo:
        interior_gordo = M > 25
        img[interior_gordo] = [0,0,0]
        img[M < 2] = [0,0,0]
        fade = np.sqrt(np.clip((M - 2) / 23.0, 0, 1))
        img = (img.astype(float) * fade[:,:,None]).astype(np.uint8)
        img[interior_gordo] = [0,0,0]
        img[M < 2] = [0,0,0]
        return img, interior_gordo
    else:
        interior_real = M >= iters-10
        img[interior_real] = [0,0,0]
        return img, interior_real
W=900; H=900
img_preview, interior = julia_v26(W, H, c, zoom, iters, vetas, suavidad, rotacion, brillo, modo)
st.image(img_preview, use_container_width=True, channels="RGB")
with st.sidebar:
    st.divider()
    if st.button("Generar Export Alta"):
        with st.spinner(f"Generando {resolucion}x{resolucion}..."):
            img_hi, interior_hi = julia_v26(resolucion, resolucion, c, zoom, iters, vetas, suavidad, rotacion, brillo, modo)
            img_pil=Image.fromarray(img_hi)
            buf=io.BytesIO(); img_pil.save(buf, format="PNG")
            st.download_button("Descargar PNG", buf.getvalue(), file_name=f"fractal_V26_DIA{dia}.png", mime="image/png")
