import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V68 TRAP FIX")
st.title("FRACTALES BAJO DEMANDA - V68 ORBIT TRAP CORREGIDO")
st.latex(r"z_{n+1} = \left[ |z_n|^{\alpha} e^{i(\beta \arg z_n + \gamma \ln|z_n|) } \right]^p + c")

with st.sidebar:
    dia = st.slider("DIA", 1, 365, 283)
    zoom = st.slider("ZOOM", 0.2, 4.0, 0.75, 0.05)
    center_x = st.slider("Centro X", -0.8, 1.2, 0.80, 0.02)
    center_y = st.slider("Centro Y", -0.8, 0.8, 0.00, 0.02)
    picos = st.slider("PICOS / CALIDAD", 0, 100, 100)
    alpha = st.slider("α grosor pico", 0.5, 2.0, 2.00, 0.05)
    beta = st.slider("β torsion", 0.5, 2.0, 2.00, 0.05)
    gamma = st.slider("γ espiral", -1.0, 1.0, 0.80, 0.05)
    p_pow = st.slider("p num picos", 2, 5, 5)
    trap_type = st.selectbox("TIPO DE TRAMPA", ["line - sigue picos (FIX)", "cross - sigue ramitas", "point - rodea (viejo)", "circle - anillos"])
    ciclos = st.slider("ciclos (NUM BANDAS)", 0.1, 8.0, 2.5, 0.1)
    resolucion = st.selectbox("Resolucion", [1000,2000,3000,4000], index=2)

def dia_to_c(dia, picos_pct):
    t = dia/365*2*math.pi
    r = 0.02 - (picos_pct/100)*0.016
    cx = -0.75 + r*math.cos(t*3)
    cy = 0.11 + r*math.sin(t*3)
    return complex(cx, cy), 1000, r

c, iters, _ = dia_to_c(dia, picos)
st.caption(f"V67 hacia bandas horizontales (bug). V68 FIX: distancia angular a los {p_pow} rayos de los picos. DIA {dia} | γ={gamma} ciclos={ciclos}")

def julia_v68(w,h,c,zoom,cx,cy,iters,alpha,beta,gamma,p_pow,trap_type,ciclos):
    x = np.linspace(-1.5/zoom + cx, 1.5/zoom + cx, w)
    y = np.linspace(-1.0/zoom + cy, 1.0/zoom + cy, h)
    X,Y = np.meshgrid(x,y)
    Z = X+1j*Y
    M = np.full(Z.shape, iters, dtype=float)
    trap_dist = np.full(Z.shape, 1e10, dtype=float)

    for i in range(iters):
        absZ = np.abs(Z)
        mask = absZ <= 100
        if not np.any(mask): break
        Zm = Z[mask]
        absZm = absZ[mask]

        # V68 FIX: orbit trap que sigue picos
        ang = np.angle(Zm)
        if "line" in trap_type:
            # distancia angular minima a cualquiera de los p rayos
            # ej p=5 -> rayos en 0°, 72°, 144° etc
            # sin(p*ang/2) = 0 cuando ang = k*2pi/p
            d = np.abs(np.sin(p_pow * ang * 0.5)) * (absZm*0.5 + 0.5)
        elif "cross" in trap_type:
            d = np.abs(np.sin(p_pow * ang)) * (absZm*0.5 + 0.5)
        elif "point" in trap_type:
            d = absZm
        else: # circle
            d = np.abs(absZm - 0.7)

        iy, ix = np.where(mask)
        trap_dist[iy, ix] = np.minimum(trap_dist[iy, ix], d)

        absZ_m = np.clip(absZm, 1e-10, 1e10)
        argZ_m = ang
        mag = np.power(absZ_m, alpha * p_pow)
        theta = p_pow * (beta * argZ_m + gamma * np.log(absZ_m))
        Z_new_m = mag * (np.cos(theta) + 1j*np.sin(theta)) + c
        esc_m = (np.abs(Z_new_m) > 2) & (M[mask]==iters)
        if np.any(esc_m):
            M[iy[esc_m], ix[esc_m]] = i
        Z[mask] = Z_new_m

    valid = M < iters
    td = trap_dist[valid]
    td = np.clip(td, 1e-5, 10)
    fase = -np.log(td + 1e-6)

    # V68: color por trap con ciclos altos para bandas gruesas siguiendo pico
    s = (fase * ciclos * 0.3) % 1.0
    t = s * 4.0
    i0 = np.floor(t).astype(int) % 4
    f = (1 - np.cos((t - np.floor(t))*np.pi))/2
    cols = np.array([[255,0,230],[255,235,0],[0,255,240],[0,220,90]], float)
    r_=np.zeros_like(s); g_=np.zeros_like(s); b_=np.zeros_like(s)
    for k in range(4):
        m = i0==k; nk=(k+1)%4
        r_[m]=(1-f[m])*cols[k,0]+f[m]*cols[nk,0]
        g_[m]=(1-f[m])*cols[k,1]+f[m]*cols[nk,1]
        b_[m]=(1-f[m])*cols[k,2]+f[m]*cols[nk,2]

    img=np.zeros((h,w,3),dtype=np.uint8)
    img[valid]=np.stack([r_.astype(np.uint8),g_.astype(np.uint8),b_.astype(np.uint8)],axis=1)
    return img

W=1200; H=700
img=julia_v68(W,H,c,zoom,center_x,center_y,iters,alpha,beta,gamma,p_pow,trap_type,ciclos)
st.image(img,use_container_width=True,channels="RGB")
st.success(f"V68 FIX: 'line' ahora usa sin(p*ang/2) -> distancia a los {p_pow} rayos. Bandas siguen el pico, no horizontales. Prueba ciclos 2.0-3.0")

with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_v68(resolucion,resolucion,c,zoom,center_x,center_y,iters,alpha,beta,gamma,p_pow,trap_type,ciclos)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_V68_TRAPFIX_DIA{dia}.png",mime="image/png")
