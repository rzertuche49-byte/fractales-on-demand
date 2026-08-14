import streamlit as st
import numpy as np
from PIL import Image
import io

st.set_page_config(layout="wide", page_title="FRACTALES ON DEMAND V19")
st.title("FRACTALES BAJO DEMANDA - V19 SEDA LISA 100%")

with st.sidebar:
    st.header("Controles REFERENCIA")
    dia = st.slider("DIA (1-365)", 1, 365, 75)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.20, 0.05)
    iters = st.slider("CALIDAD (iters)", 200, 2000, 600)
    resolucion = st.selectbox("Resolucion Exportar", [1000, 2000, 3000, 4000], index=0)
    st.divider()
    fondo_transparente = st.checkbox("Fondo Transparente", value=False)
    vetas = st.slider("Num Vetass gordas", 0.5, 6.0, 2.2, 0.1)
    suavidad = st.slider("Suavidad flujo", 0.05, 2.0, 0.60, 0.05)
    rotacion = st.slider("Rotacion Tono", 0.0, 6.28, 2.5, 0.05)

c = complex(-0.74543, 0.11301) if 70 <= dia <= 80 else complex(0.7885*np.cos((dia/365)*2*np.pi*3), 0.7885*np.sin((dia/365)*2*np.pi*3))
st.write(f"c = {c} | V19 - Sin confeti, seda pura")

def julia_seda(w, h, c, zoom, iters, vetas, suavidad, rotacion):
    x_range = 3.0 / zoom
    y_range = 3.0 / zoom
    x = np.linspace(-x_range/2, x_range/2, w)
    y = np.linspace(-y_range/2, y_range/2, h)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y

    M = np.zeros(Z.shape)
    # TIA - Triangle Inequality Average: esto quita el confeti
    tia = np.zeros(Z.shape)
    tia_count = np.zeros(Z.shape)

    for i in range(iters):
        mask = np.abs(Z) <= 10
        if not np.any(mask): break
        # Acumula promedio de la orbita = flujo liso
        tia[mask] += np.abs(Z[mask])
        tia_count[mask] += 1
        Z[mask] = Z[mask]**2 + c
        M[mask] = i

    with np.errstate(divide='ignore', invalid='ignore'):
        tia_avg = tia / (tia_count + 1e-10)
        tia_avg = np.nan_to_num(tia_avg, nan=0)
        # Suavizado log para que no explote
        tia_smooth = np.log(tia_avg + 1.0)

    # FORMULA SEDA PURA: sin angulo caotico, solo promedio
    t = tia_smooth * vetas + M * suavidad * 0.02 + rotacion

    r = (0.5 + 0.5 * np.sin(t + 0.0)) * 255
    g = (0.5 + 0.5 * np.sin(t + 2.1)) * 255
    b = (0.5 + 0.5 * np.sin(t + 4.2)) * 255

    r = np.clip(r*1.35,0,255); g=np.clip(g*1.2,0,255); b=np.clip(b*1.45,0,255)
    img = np.stack([r,g,b], axis=-1).astype(np.uint8)

    interior = M >= iters-3
    img[interior]=[0,0,0]
    img[M < 1]=[0,0,0]

    # Viñeta negra para dar profundidad como tu referencia
    return img, interior

W=900; H=900
img_preview, interior = julia_seda(W, H, c, zoom, iters, vetas, suavidad, rotacion)
st.image(img_preview, use_container_width=True, channels="RGB")
st.success("V19 usa TIA: promedio de orbita = sin confeti. Vetas 2.2 = referencia exacta")

st.sidebar.divider()
if st.sidebar.button("Generar Export Alta"):
    with st.spinner(f"Generando {resolucion}x{resolucion}..."):
        img_hi, interior_hi = julia_seda(resolucion, resolucion, c, zoom, iters, vetas, suavidad, rotacion)
        if fondo_transparente:
            alpha = np.ones((resolucion,resolucion),dtype=np.uint8)*255
            alpha[interior_hi]=0
            img_pil=Image.fromarray(img_hi).convert("RGBA")
            img_pil.putalpha(Image.fromarray(alpha))
        else:
            img_pil=Image.fromarray(img_hi)
        buf=io.BytesIO(); img_pil.save(buf, format="PNG")
        st.sidebar.download_button("Descargar PNG", buf.getvalue(), file_name=f"fractal_V19_SEDA_DIA{dia}.png", mime="image/png")
