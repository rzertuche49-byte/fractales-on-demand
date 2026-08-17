import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V77.2 FIX")
st.title("FRACTALES BAJO DEMANDA - V77.2 FIX PALETAS")

def hex_to_rgb(h):
    h=h.lstrip('#')
    return tuple(int(h[i:i+2],16) for i in (0,2,4))

PALETAS = {
    "Neón Psicodélico": ["#00FFFF","#FF00FF","#FFFF00","#00FF00","#FF0066","#6600FF"],
    "Pastel Suave": ["#FFB5E8","#B5DEFF","#C3FF99","#FFF5BA","#FFC9DE","#D1BDFF"],
    "Fuego": ["#FF0000","#FF6600","#FFFF00","#FF3300","#CC0000","#FF9900"],
    "Océano": ["#001F54","#034078","#1282A2","#00B4D8","#90E0EF","#CAF0F8"],
    "Bosque Neón": ["#004B23","#007200","#38B000","#70E000","#CCFF33","#00FFFF"],
    "Sunset": ["#F72585","#7209B7","#3A0CA3","#4361EE","#4CC9F0","#FFBE0B"],
    "Tu captura": ["#00FFFF","#0064FF","#FF00C8","#FF6400","#FFFF00","#00FF64"],
}

if 'colores' not in st.session_state:
    st.session_state.colores = PALETAS["Tu captura"]
    for i,c in enumerate(st.session_state.colores):
        st.session_state[f"cp_{i}"] = c

def aplicar_paleta(nombre):
    pal = PALETAS[nombre]
    st.session_state.colores = pal
    for i,c in enumerate(pal):
        st.session_state[f"cp_{i}"] = c

with st.sidebar:
    st.subheader("DIA / FORMA")
    dia = st.slider("DIA", 1, 365, 283)
    zoom = st.slider("ZOOM", 0.2, 10.0, 0.88, 0.05)
    center_x = st.slider("Centro X", -1.5, 1.5, 0.01, 0.005)
    center_y = st.slider("Centro Y", -1.5, 1.5, 0.0, 0.005)
    picos = st.slider("PICOS / CALIDAD", 0, 100, 85)
    st.divider()
    st.subheader("🎨 PALETAS 1-CLICK")
    cols = st.columns(2)
    for idx, (nombre, pal) in enumerate(PALETAS.items()):
        if cols[idx%2].button(nombre, use_container_width=True, key=f"btn_{nombre}"):
            aplicar_paleta(nombre)
            st.rerun()
    st.divider()
    st.subheader("TUS 6 COLORES")
    c_inputs=[]
    for i in range(6):
        # usa el valor de session_state
        col = st.color_picker(f"Color {i+1}", key=f"cp_{i}")
        c_inputs.append(col)
    st.session_state.colores = c_inputs
    st.divider()
    ciclos = st.slider("ciclos", 0.1, 5.0, 1.50, 0.1)
    mezcla = st.slider("Detalle espiral", 0.0, 1.0, 0.22, 0.02)
    tamano_mancha = st.slider("Tamaño mancha", 0.1, 3.0, 1.80, 0.05)
    brillo = st.slider("Brillo", 0.5, 2.0, 1.40, 0.05)
    iteraciones = st.slider("Iteraciones", 10, 500, 80, 10)
    resolucion = st.selectbox("Export", [2000,3000,4000,6000,8000], index=2)
    suavizado_gama = st.checkbox("Gama Suave", value=True)

def dia_to_c(dia, picos_pct):
    t = dia/365*2*math.pi
    r = 0.02 - (picos_pct/100)*0.016
    cx = -0.75 + r*math.cos(t*3)
    cy = 0.11 + r*math.sin(t*3)
    return complex(cx, cy)

c = dia_to_c(dia, picos)

def julia_custom(w,h,c,zoom,cx,cy,iters,ciclos,mezcla,tam,brillo, palette, suave):
    x = np.linspace(-1.5/zoom + cx, 1.5/zoom + cx, w, dtype=np.float64)
    y = np.linspace(-1.0/zoom + cy, 1.0/zoom + cy, h, dtype=np.float64)
    X,Y = np.meshgrid(x,y)
    Z = X+1j*Y
    for i in range(iters):
        Z = Z*Z + c
    ang = np.angle(Z)
    rad = np.log(np.abs(Z)+1)
    fase = ang*mezcla + rad*tam
    s = (fase * ciclos * 0.25) % 1.0
    if suave:
        t_ = s * 6.0
        i0 = np.floor(t_).astype(int) % 6
        f = (1 - np.cos((t_ - np.floor(t_))*np.pi))/2
        img = np.zeros((h,w,3), float)
        for k in range(6):
            m = i0==k
            nk=(k+1)%6
            img[m,0] = (1-f[m])*palette[k,0]+f[m]*palette[nk,0]
            img[m,1] = (1-f[m])*palette[k,1]+f[m]*palette[nk,1]
            img[m,2] = (1-f[m])*palette[k,2]+f[m]*palette[nk,2]
    else:
        t_ = (s * 6.0).astype(int) % 6
        img = np.zeros((h,w,3), float)
        for k in range(6):
            m = t_==k
            img[m]=palette[k]
    img = np.clip(img*brillo,0,255).astype(np.uint8)
    return img

pal = np.array([hex_to_rgb(c) for c in st.session_state.colores], float)
W=1200; H=900
img=julia_custom(W,H,c,zoom,center_x,center_y,iteraciones,ciclos,mezcla,tamano_mancha,brillo,pal,suavizado_gama)
st.image(img,use_container_width=True,channels="RGB")

img_hi=julia_custom(resolucion,resolucion,c,zoom,center_x,center_y,iteraciones,ciclos,mezcla,tamano_mancha,brillo,pal,suavizado_gama)
buf=io.BytesIO()
Image.fromarray(img_hi).save(buf,format="PNG")
st.sidebar.download_button("📥 Descargar PNG 4K",buf.getvalue(),file_name=f"fractal_V77_DIA{dia}.png",mime="image/png", type="primary")
