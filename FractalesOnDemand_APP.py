import streamlit as st
import numpy as np
from PIL import Image
import io

st.set_page_config(layout="wide", page_title="FRACTALES ON DEMAND V24")
st.title("FRACTALES BAJO DEMANDA - V24 VETAS GORDAS")

with st.sidebar:
    st.header("Controles REFERENCIA")
    modo = st.radio("Modo", ["Silueta Negra (tu ref original)", "Relleno Amarillo"], index=0)
    dia = st.slider("DIA (1-365)", 1, 365, 75)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.25, 0.05)
    iters = st.slider("CALIDAD (iters)", 200, 2000, 700)
    resolucion = st.selectbox("Resolucion Exportar", [1000, 2000, 3000, 4000], index=0)
    st.divider()
    fondo_transparente = st.checkbox("Fondo Transparente", value=False)
    vetas = st.slider("Num Vetass gordas", 0.05, 2.0, 0.35, 0.05)
    suavidad = st.slider("Suavidad flujo", 0.02, 1.0, 0.10, 0.02)
    rotacion = st.slider("Rotacion Tono", 0.0, 6.28, 5.80, 0.05)
    brillo = st.slider("Brillo neon", 0.5, 2.5, 1.3, 0.1)

c = complex(-0.74543, 0.11301) if 70 <= dia <= 80 else complex(0.7885*np.cos((dia/365)*2*np.pi*3), 0.7885*np.sin((dia/365)*2*np.pi*3))

def julia_v24(w, h, c, zoom, iters, vetas, suavidad, rotacion, brillo, modo):
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
        log_r = np.log(np.abs(Zf)+1e-10)
        mu = M + 5 - np.log(log_r+1e-10)/np.log(2) # suavizado continuo
        mu = np.nan_to_num(mu, nan=0)
        Af = np.nan_to_num(Af, nan=0)

    if "Silueta" in modo:
        # VETAS GORDAS: mu*0.08 + Af*0.3 = 2-3 ondas gigantes
        t = mu * suavidad + Af * vetas + rotacion
    else:
        t = mu * suavidad * 0.2 + Af * vetas + rotacion

    # Paleta de tu ref 1: fucsia-amarillo-turquesa, no arcoiris completo
    r = (0.5 + 0.5 * np.sin(t + 0.0)) * 255
    g = (0.5 + 0.5 * np.sin(t + 2.0)) * 255
    b = (0.5 + 0.5 * np.sin(t + 4.0)) * 255
    r = np.clip(r*1.5*brillo,0,255); g=np.clip(g*1.35*brillo,0,255); b=np.clip(b*1.5*brillo,0,255)
    img = np.stack([r,g,b], axis=-1).astype(np.uint8)

    if "Silueta" in modo:
        interior = M > 35
        img[interior] = [0,0,0]
        img[M < 3] = [0,0,0]
        fade = np.clip((M - 3) / 10.0, 0, 1)[:,:,None]
        img = (img * fade).astype(np.uint8)
        img[interior] = [0,0,0]
    else:
        interior = M >= iters-5
        img[interior] = [0,0,0]

    return img, interior

W=900; H=900
img_preview, interior = julia_v24(W, H, c, zoom, iters, vetas, suavidad, rotacion, brillo, modo)
st.image(img_preview, use_container_width=True, channels="RGB")
st.success("V24: 0.35 vetas + 0.10 suavidad = 2-3 vetas gordas como tu ref original")

st.sidebar.divider()
if st.sidebar.button("Generar Export Alta"):
    with st.spinner(f"Generando {resolucion}x{resolucion}..."):
        img_hi, interior_hi = julia_v24(resolucion, resolucion, c, zoom, iters, vetas, suavidad, rotacion, brillo, modo)
        if fondo_transparente:
            alpha = np.ones((resolucion,resolucion),dtype=np.uint8)*255
            alpha[interior_hi]=0
            img_pil=Image.fromarray(img_hi).convert("RGBA")
            img_pil.putalpha(Image.fromarray(alpha))
        else:
            img_pil=Image.fromarray(img_hi)
        buf=io.BytesIO(); img_pil.save(buf, format="PNG")
        st.sidebar.download_button("Descargar PNG", buf.getvalue(), file_name=f"fractal_V24_SILUETA_DIA{dia}.png", mime="image/png")
