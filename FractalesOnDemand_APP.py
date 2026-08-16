import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V67 ORBIT TRAP")
st.title("FRACTALES BAJO DEMANDA - V67 ORBIT TRAP")
st.latex(r"z_{n+1} = \left[ |z_n|^{\alpha} e^{i(\beta \arg z_n + \gamma \ln|z_n|) } \right]^p + c")
st.markdown("**Orbit Trap:** mide que tan cerca pasa la órbita de una trampa. Escape Time mide cuando escapa.")

with st.sidebar:
    dia = st.slider("DIA", 1, 365, 135)
    zoom = st.slider("ZOOM", 0.2, 4.0, 0.80, 0.05)
    center_x = st.slider("Centro X", -0.8, 1.2, 0.80, 0.02)
    center_y = st.slider("Centro Y", -0.8, 0.8, 0.00, 0.02)
    picos = st.slider("PICOS / CALIDAD", 0, 100, 100)
    alpha = st.slider("α grosor pico", 0.5, 2.0, 2.00, 0.05)
    beta = st.slider("β torsion", 0.5, 2.0, 2.00, 0.05)
    gamma = st.slider("γ espiral", -1.0, 1.0, 1.00, 0.05)
    p_pow = st.slider("p num picos", 2, 5, 5)
    trap_type = st.selectbox("TIPO DE TRAMPA (ORBIT TRAP)", ["line - sigue picos", "cross - sigue ramitas", "point - rodea", "circle - anillos"])
    ciclos = st.slider("ciclos (NUM BANDAS)", 0.1, 8.0, 0.50, 0.05)
    resolucion = st.selectbox("Resolucion", [1000,2000,3000,4000], index=2)

def dia_to_c(dia, picos_pct):
    t = dia/365*2*math.pi
    r = 0.02 - (picos_pct/100)*0.016
    cx = -0.75 + r*math.cos(t*3)
    cy = 0.11 + r*math.sin(t*3)
    return complex(cx, cy), 800, r

c, iters, _ = dia_to_c(dia, picos)
st.caption(f"DIA {dia} | TRAP={trap_type} | γ={gamma} ciclos={ciclos} | line/cross = bandas alineadas con picos | point/circle = bandas rodeando")

def julia_trap(w,h,c,zoom,cx,cy,iters,alpha,beta,gamma,p_pow,trap_type,ciclos):
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

        # ORBIT TRAP: medir distancia a la trampa en cada iteracion
        if "line" in trap_type:
            d = np.abs(Z[mask].imag) # distancia a eje real -> bandas horizontales que siguen picos
        elif "cross" in trap_type:
            d = np.minimum(np.abs(Z[mask].real), np.abs(Z[mask].imag)) # cruz
        elif "point" in trap_type:
            d = absZ[mask] # distancia al origen
        else: # circle
            d = np.abs(absZ[mask] - 0.5)

        # guardar distancia minima
        idx_y, idx_x = np.where(mask)
        trap_dist[idx_y, idx_x] = np.minimum(trap_dist[idx_y, idx_x], d)

        absZ_m = np.clip(absZ[mask], 1e-10, 1e10)
        argZ_m = np.angle(Z[mask])
        mag = np.power(absZ_m, alpha * p_pow)
        theta = p_pow * (beta * argZ_m + gamma * np.log(absZ_m))
        Z_new_m = mag * (np.cos(theta) + 1j*np.sin(theta)) + c
        esc_m = (np.abs(Z_new_m) > 2) & (M[mask]==iters)
        if np.any(esc_m):
            iy, ix = np.where(mask)
            M[iy[esc_m], ix[esc_m]] = i
        Z[mask] = Z_new_m

    valid = M < iters
    # COLOR POR TRAP, no por escape
    td = trap_dist[valid]
    td = np.clip(td, 1e-6, 10)
    # log para suavizar
    fase = np.log(td + 1e-6) * -1 # invertir: cerca = alto
    if "line" in trap_type or "cross" in trap_type:
        # para line/cross usamos fase de tu formula + trap para alinear perfecto
        fase = fase * 0.5 + (np.angle(Z[valid]) if False else 0)

    s = (fase * ciclos) % 1.0
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
img=julia_trap(W,H,c,zoom,center_x,center_y,iters,alpha,beta,gamma,p_pow,trap_type,ciclos)
st.image(img,use_container_width=True,channels="RGB")
st.info(f"TRAP={trap_type} | Si quieres bandas ALINEADAS con picos usa 'line' o 'cross'. Si quieres que RODEEN usa 'point' o 'circle'. Tu captura V65 era escape time, esto es orbit trap")

with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_trap(resolucion,resolucion,c,zoom,center_x,center_y,iters,alpha,beta,gamma,p_pow,trap_type,ciclos)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_V67_TRAP_{trap_type}_DIA{dia}.png",mime="image/png")
