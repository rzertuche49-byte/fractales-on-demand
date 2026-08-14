import streamlit as st
import numpy as np
from PIL import Image
import io

st.set_page_config(layout="wide", page_title="FRACTALES ON DEMAND V16")
st.title("FRACTALES BAJO DEMANDA - V16 FLUJO SEDA REFERENCIA")

with st.sidebar:
    st.header("Controles REFERENCIA")
    dia = st.slider("DIA (1-365)", 1, 365, 75)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.2, 0.05)
    iters = st.slider("CALIDAD (iters)", 200, 2000, 800)
    resolucion = st.selectbox("Resolucion Exportar", [1000, 2000, 3000, 4000], index=0)
    st.divider()
    fondo_transparente = st.checkbox("Fondo Transparente", value=False)
    flujo = st.slider("Fuerza Flujo (ondas seda)", 0.5, 8.0, 3.5)
    densidad = st.slider("Densidad Color", 0.05, 1.0, 0.35)
    rotacion = st.slider("Rotacion Tono", 0.0, 6.28, 1.0)

# c que clona tu referencia: espiral doble
c = complex(-0.74543, 0.11301) if 70 <= dia <= 80 else complex(0.7885*np.cos((dia/365)*2*np.pi*3), 0.7885*np.sin((dia/365)*2*np.pi*3))
st.write(f"c = {c} | V16 - Flujo tipo tu referencia")

def julia_flujo(w, h, c, zoom, iters, flujo, densidad, rotacion):
    x_range = 3.0 / zoom
    y_range = 3.0 / zoom
    x = np.linspace(-x_range/2, x_range/2, w)
    y = np.linspace(-y_range/2, y_range/2, h)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y

    M = np.zeros(Z.shape)
    Z_final = np.zeros(Z.shape, dtype=complex)
    Arg_final = np.zeros(Z.shape)

    for i in range(iters):
        mask = np.abs(Z) <= 100
        if not np.any(mask): break
        Z[mask] = Z[mask]**2 + c
        M[mask] = i
        Z_final[mask] = Z[mask]
        Arg_final[mask] = np.angle(Z[mask])

    with np.errstate(divide='ignore', invalid='ignore'):
        # Suavizado
        log_zn = np.log(np.abs(Z_final)+1e-10) / 2
        nu = np.log(log_zn / np.log(2)) / np.log(2)
        mu = M + 1 - nu
        mu = np.nan_to_num(mu, nan=0, posinf=0)

    # TECNICA DE TU REFERENCIA: FIELD LINES
    # Potencial + Angulo = rios de seda
    potencial = np.log(np.abs(Z_final)+1e-10)
    angulo = Arg_final

    # Esto crea las vetas que fluyen como tu imagen
    flow = angulo * flujo + potencial * densidad + rotacion

    # Paleta de tu referencia: fucsia, amarillo, turquesa, morado
    t = flow
    r = (0.5 + 0.5 * np.sin(t * 0.8 + 0.0)) * 255
    g = (0.5 + 0.5 * np.sin(t * 0.8 + 2.0)) * 255
    b = (0.5 + 0.5 * np.sin(t * 0.8 + 4.0)) * 255

    # Saturacion extra para que reviente como tu ref
    r = np.clip(r * 1.4, 0, 255)
    g = np.clip(g * 1.2, 0, 255)
    b = np.clip(b * 1.5, 0, 255)

    img = np.stack([r,g,b], axis=-1).astype(np.uint8)

    interior = M >= iters-3
    fondo_lejano = M < 3
    img[interior] = [0,0,0]
    img[fondo_lejano] = [0,0,0]
    # Fondo negro puro como tu referencia
    img[M < 2] = [0,0,0]

    return img, interior

W=900; H=900
img_preview, interior = julia_flujo(W, H, c, zoom, iters, flujo, densidad, rotacion)
st.image(img_preview, use_container_width=True, channels="RGB")
st.info("Para clonar tu referencia: ZOOM 1.2, Flujo 3.5, Densidad 0.35, Rotacion 1.0")

st.sidebar.divider()
if st.sidebar.button("Generar Export Alta"):
    with st.spinner(f"Generando {resolucion}x{resolucion}..."):
        img_hi, interior_hi = julia_flujo(resolucion, resolucion, c, zoom, iters, flujo, densidad, rotacion)
        if fondo_transparente:
            alpha = np.ones((resolucion,resolucion),dtype=np.uint8)*255
            alpha[interior_hi]=0
            img_pil=Image.fromarray(img_hi).convert("RGBA")
            img_pil.putalpha(Image.fromarray(alpha))
        else:
            img_pil=Image.fromarray(img_hi)
        buf=io.BytesIO(); img_pil.save(buf, format="PNG")
        st.sidebar.download_button("Descargar PNG", buf.getvalue(), file_name=f"fractal_V16_REF_DIA{dia}.png", mime="image/png")
