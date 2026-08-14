import streamlit as st
import numpy as np
from PIL import Image
import io

st.set_page_config(layout="wide", page_title="FRACTALES ON DEMAND V18")
st.title("FRACTALES BAJO DEMANDA - V18 REFERENCIA REAL")

with st.sidebar:
    st.header("Controles REFERENCIA")
    dia = st.slider("DIA (1-365)", 1, 365, 75)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.20, 0.05)
    iters = st.slider("CALIDAD (iters)", 200, 2000, 800)
    resolucion = st.selectbox("Resolucion Exportar", [1000, 2000, 3000, 4000], index=0)
    st.divider()
    fondo_transparente = st.checkbox("Fondo Transparente", value=False)
    vetas = st.slider("Num Vetass gordas", 1.0, 8.0, 2.2, 0.1)
    suavidad = st.slider("Suavidad flujo", 0.1, 2.0, 0.8, 0.1)
    rotacion = st.slider("Rotacion Tono", 0.0, 6.28, 2.5, 0.05)

c = complex(-0.74543, 0.11301) if 70 <= dia <= 80 else complex(0.7885*np.cos((dia/365)*2*np.pi*3), 0.7885*np.sin((dia/365)*2*np.pi*3))
st.write(f"c = {c} | V18 - Vetas gordas sin cebra")

def julia_referencia(w, h, c, zoom, iters, vetas, suavidad, rotacion):
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

    with np.errstate(divide='ignore', invalid='ignore'):
        # log suave, NO mu con 800 vueltas
        log_r = np.log(np.abs(Zf)+1e-10)
        log_r = np.nan_to_num(log_r, nan=0)

    # FORMULA DE TU REFERENCIA REAL
    # Solo angulo + log chiquito = vetas gordas que fluyen
    # vetas = cuantas veces da la vuelta el color (2.2 = 2-3 vetas como tu foto)
    t = Af * vetas + log_r * suavidad + rotacion

    # Paleta de tu foto: fucsia, amarillo, turquesa, morado
    r = (0.5 + 0.5 * np.sin(t + 0.0)) * 255
    g = (0.5 + 0.5 * np.sin(t + 2.1)) * 255
    b = (0.5 + 0.5 * np.sin(t + 4.3)) * 255

    # Contraste como tu referencia
    r = np.clip((r-128)*1.4+128, 0, 255)
    g = np.clip((g-128)*1.4+128, 0, 255)
    b = np.clip((b-128)*1.4+128, 0, 255)

    img = np.stack([r,g,b], axis=-1).astype(np.uint8)

    # Fondo negro limpio como tu referencia
    interior = M >= iters-2
    img[interior] = [0,0,0]
    # Quita el confeti del centro: si escapo muy rapido, negro
    img[M < 2] = [0,0,0]

    # Sombreado suave para dar volumen 3D como tu referencia
    sombra = np.clip((M / 40.0), 0, 1)
    sombra = sombra[:,:,None]
    img = (img * (0.5 + 0.5*sombra)).astype(np.uint8)
    img[interior] = [0,0,0]

    return img, interior

W=900; H=900
img_preview, interior = julia_referencia(W, H, c, zoom, iters, vetas, suavidad, rotacion)
st.image(img_preview, use_container_width=True, channels="RGB")
st.success("VETAS 2.2 = 2-3 vetas gordas como tu foto | Suavidad 0.8 = ondas seda")

st.sidebar.divider()
if st.sidebar.button("Generar Export Alta"):
    with st.spinner(f"Generando {resolucion}x{resolucion}..."):
        img_hi, interior_hi = julia_referencia(resolucion, resolucion, c, zoom, iters, vetas, suavidad, rotacion)
        if fondo_transparente:
            alpha = np.ones((resolucion,resolucion),dtype=np.uint8)*255
            alpha[interior_hi]=0
            img_pil=Image.fromarray(img_hi).convert("RGBA")
            img_pil.putalpha(Image.fromarray(alpha))
        else:
            img_pil=Image.fromarray(img_hi)
        buf=io.BytesIO(); img_pil.save(buf, format="PNG")
        st.sidebar.download_button("Descargar PNG", buf.getvalue(), file_name=f"fractal_V18_REF_DIA{dia}.png", mime="image/png")
