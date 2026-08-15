import streamlit as st
import numpy as np
from PIL import Image
import io
import math
st.set_page_config(layout="wide", page_title="V47 REF REAL PSICODELICO")
st.title("FRACTALES BAJO DEMANDA - V47 REF REAL ESPIRALES")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 258)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.0, 0.05)
    iters = st.slider("CALIDAD", 200, 3000, 1500)
    resolucion = st.selectbox("Resolucion", [1000, 2000, 3000, 4000], index=2)
    ciclos = st.slider("Ciclos color", 1.0, 20.0, 8.0, 0.5)

def dia_to_c_psy(dia):
    # c para espirales como la ref: cerca de -0.04 + 0.67i es la clave
    # mapeamos DIA a anillo de espirales
    t = dia / 365.0 * 2 * math.pi
    # radio 0.65-0.70 da espirales de tu ref
    r = 0.62 + 0.08 * math.sin(dia*0.05)
    # centro en -0.04 + 0.66i que es la ref exacta
    cx = -0.04 + r * 0.15 * math.cos(t)
    cy = 0.66 + r * 0.15 * math.sin(t)
    return complex(cx, cy)

c = dia_to_c_psy(dia)
st.caption(f"DIA {dia} -> c = {c.real:.5f} + {c.imag:.5f}i | REF PSICODELICA ESPIRALES")

def julia_psy(w,h,c,zoom,iters,ciclos):
    x = np.linspace(-1.8/zoom, 1.8/zoom, w)
    y = np.linspace(-1.8/zoom, 1.8/zoom, h)
    X,Y = np.meshgrid(x,y)
    Z = X + 1j*Y
    M = np.full(Z.shape, iters, dtype=float)
    # para sombreado 3D
    angle = np.zeros(Z.shape)

    for i in range(iters):
        mask = np.abs(Z) <= 1000
        escaped = mask & (np.abs(Z) > 2) & (M==iters)
        M[escaped] = i - np.log2(np.log(np.abs(Z[escaped])+1e-10)+1) + 1
        angle[escaped] = np.angle(Z[escaped])
        Z[mask] = Z[mask]**2 + c

    img = np.zeros((h,w,3), dtype=np.uint8)
    valid = M < iters

    # COLORACION PSICODELICA COMO LA REF
    # Ciclos rapidos para crear bandas finas de color
    t = (M[valid] * ciclos * 0.08) % 1.0

    # Paleta ref: Fucsia -> Amarillo -> Turquesa -> Morado -> Fucsia
    # Creamos 4 ondas desfasadas
    r = (127 * (np.sin(2*np.pi*t*2.0 + 0.0)+1) + 50 * np.sin(2*np.pi*t*8)).clip(0,255)
    g = (127 * (np.sin(2*np.pi*t*2.0 + 2.0)+1) * 0.8 + 30).clip(0,255)
    b = (127 * (np.sin(2*np.pi*t*2.0 + 4.0)+1) + 50).clip(0,255)

    # Ajuste para que sean exactamente tus colores
    # Magenta / Amarillo / Cyan / Morado
    r = (255 * (0.5 + 0.5*np.sin(2*math.pi*t*1.5 + 0))).astype(int)
    g = (255 * (0.5 + 0.5*np.sin(2*math.pi*t*1.5 + 2.1))).astype(int)
    b = (255 * (0.5 + 0.5*np.sin(2*math.pi*t*1.5 + 4.2))).astype(int)

    # Boost saturacion
    r = np.clip(r*1.2, 0, 255)
    g = np.clip(g*1.1, 0, 255)
    b = np.clip(b*1.3, 0, 255)

    # Sombreado por angulo para efecto 3D liquido de la ref
    shade = 0.7 + 0.3*np.sin(angle[valid]*3 + M[valid]*0.5)
    r = (r*shade).astype(np.uint8)
    g = (g*shade).astype(np.uint8)
    b = (b*shade).astype(np.uint8)

    img[valid] = np.stack([r,g,b], axis=1)

    # Fondo negro puro
    img[M >= iters-1] = [0,0,0]
    return img

W=900; H=900
img = julia_psy(W,H,c,zoom,iters,ciclos)
st.image(img, use_container_width=True, channels="RGB")
with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_psy(resolucion,resolucion,c,zoom,iters,ciclos)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_PSY_DIA{dia}.png",mime="image/png")
