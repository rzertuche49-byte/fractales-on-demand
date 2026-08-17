import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V74 EL QUE BUSCO")
st.title("FRACTALES BAJO DEMANDA - V74 TARGET - EL QUE BUSCO")
st.latex(r"z_{n+1}=z_n^2 + c \quad \text{(modo target)}")

with st.sidebar:
    dia = st.slider("DIA", 1, 365, 283)
    zoom = st.slider("ZOOM", 0.2, 50.0, 1.0, 0.05)
    center_x = st.slider("Centro X", -1.5, 1.5, 0.0, 0.005)
    center_y = st.slider("Centro Y", -1.5, 1.5, 0.0, 0.005)
    picos = st.slider("PICOS / CALIDAD", 0, 100, 100)

    st.divider()
    st.markdown("### MODO")
    modo = st.selectbox("Modo", ["TARGET - El que busco (RECOMENDADO)", "Orbit Trap Line", "Orbit Trap Cross", "Mix clasico V71"])
    p_pow = st.slider("p (para TARGET pon 2)", 2, 5, 2)
    alpha = st.slider("α (para TARGET pon 1.0)", 0.5, 2.0, 1.0, 0.05)
    beta = st.slider("β (para TARGET pon 1.0)", 0.5, 2.0, 1.0, 0.05)
    gamma = st.slider("γ (para TARGET pon 0.0)", -1.0, 1.0, 0.0, 0.05)

    st.divider()
    ciclos = st.slider("ciclos - NUM COLORES (subelo para target)", 0.5, 15.0, 7.0, 0.5)
    mezcla = st.slider("Detalle espiral", 0.0, 1.0, 0.60, 0.05)
    suavizado = st.slider("Suavizado bandas", 0.1, 2.0, 1.0, 0.1)
    iters_extra = st.slider("Iteraciones", 0, 3000, 1200, 100)
    resolucion = st.selectbox("Export", [2000,3000,4000,6000,8000], index=2)

def dia_to_c(dia, picos_pct):
    t = dia/365*2*math.pi
    r = 0.02 - (picos_pct/100)*0.016
    cx = -0.75 + r*math.cos(t*3)
    cy = 0.11 + r*math.sin(t*3)
    return complex(cx, cy), 1000, r

c, base_iters, _ = dia_to_c(dia, picos)
iters = base_iters + iters_extra

def julia_target(w,h,c,zoom,cx,cy,iters,ciclos,mezcla,suavizado, modo):
    x = np.linspace(-1.5/zoom + cx, 1.5/zoom + cx, w, dtype=np.float64)
    y = np.linspace(-1.0/zoom + cy, 1.0/zoom + cy, h, dtype=np.float64)
    X,Y = np.meshgrid(x,y)
    Z = X+1j*Y
    M = np.full(Z.shape, iters, dtype=np.float64)
    Arg = np.zeros(Z.shape, dtype=np.float64)
    Abs = np.zeros(Z.shape, dtype=np.float64)

    # TARGET usa z^2 + c clasico, no tu formula con alpha/beta
    use_target = "TARGET" in modo

    for i in range(iters):
        absZ = np.abs(Z)
        mask = absZ <= 1e4
        if not np.any(mask): break
        if use_target:
            Z_new = Z[mask]*Z[mask] + c
        else:
            # modo viejo con p=5 para comparar
            absZm = np.clip(absZ[mask],1e-12,1e12)
            ang = np.angle(Z[mask])
            mag = np.power(absZm, 2.0*2)
            theta = 2*(ang)
            Z_new = mag*(np.cos(theta)+1j*np.sin(theta)) + c

        esc = (np.abs(Z_new) > 4) & (M[mask]==iters)
        if np.any(esc):
            iy,ix = np.where(mask)
            # smooth iteration + angulo
            abs_esc = np.abs(Z_new[esc])
            M[iy[esc], ix[esc]] = i + 1 - np.log(np.log(abs_esc+1e-10))/np.log(2)
            Arg[iy[esc], ix[esc]] = np.angle(Z_new[esc])
            Abs[iy[esc], ix[esc]] = abs_esc
        Z[mask] = Z_new

    valid = M < iters
    if use_target:
        # SECRETO del que buscas: M + sin(arg)*mezcla
        # ciclos 7.0 = muchos colores como tu ref
        fase = M[valid] + mezcla*3.0*np.sin(Arg[valid]*2.5)
        fase = fase * suavizado
    elif "Line" in modo:
        fase = np.abs(np.sin(5*Arg[valid]*0.5))*5 + M[valid]*0.1
    elif "Cross" in modo:
        fase = np.abs(np.sin(5*Arg[valid]))*5 + M[valid]*0.1
    else:
        fase = M[valid]

    s = (fase * ciclos * 0.08) % 1.0
    # paleta arcoiris del que buscas - 7 colores
    # no 4 colores como antes, 7 como tu imagen
    t = s * 7.0
    i0 = np.floor(t).astype(int) % 7
    f = (1 - np.cos((t - np.floor(t))*np.pi))/2
    # colores de tu ref: azul cyan amarillo naranja rosa morado
    cols = np.array([
        [0, 255, 255], # cyan
        [0, 100, 255], # azul
        [255, 0, 200], # magenta
        [255, 100, 0], # naranja
        [255, 255, 0], # amarillo
        [0, 255, 100], # verde
        [180, 0, 255] # morado
    ], float)
    r_=np.zeros_like(s); g_=np.zeros_like(s); b_=np.zeros_like(s)
    for k in range(7):
        m = i0==k; nk=(k+1)%7
        r_[m]=(1-f[m])*cols[k,0]+f[m]*cols[nk,0]
        g_[m]=(1-f[m])*cols[k,1]+f[m]*cols[nk,1]
        b_[m]=(1-f[m])*cols[k,2]+f[m]*cols[nk,2]

    img=np.zeros((h,w,3),dtype=np.uint8)
    img[valid]=np.stack([r_.astype(np.uint8),g_.astype(np.uint8),b_.astype(np.uint8)],axis=1)
    return img

W=1200; H=1200
img=julia_target(W,H,c,zoom,center_x,center_y,iters,ciclos,mezcla,suavizado,modo)
st.image(img,use_container_width=True,channels="RGB")
st.success(f"MODO={modo} | Para EL QUE BUSCO: p=2 α=1 β=1 γ=0 ciclos=7.0 mezcla=0.6 zoom=1.0 | Tus 5 capturas eran con p=5 -> por eso salian planos")

with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_target(resolucion,resolucion,c,zoom,center_x,center_y,iters,ciclos,mezcla,suavizado,modo)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_V74_TARGET_DIA{dia}.png",mime="image/png")
