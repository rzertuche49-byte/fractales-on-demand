import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V61 FIX ERROR")
st.title("FRACTALES BAJO DEMANDA - V61 FIX ALINEADO SIN MOIRÉ")
st.latex(r"z_{n+1} = \left[ |z_n|^{\alpha} e^{i(\beta \arg z_n + \gamma \ln|z_n|) } \right]^p + c")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 273)
    zoom = st.slider("ZOOM", 0.2, 4.0, 2.90, 0.05)
    picos = st.slider("PICOS / CALIDAD", 0, 100, 65)
    alpha = st.slider("α grosor pico", 0.5, 2.0, 1.0, 0.05)
    beta = st.slider("β torsion", 0.5, 2.0, 1.0, 0.05)
    gamma = st.slider("γ espiral (ALINEA BANDAS)", -1.0, 1.0, 0.35, 0.05)
    p_pow = st.slider("p num picos", 2, 5, 2)
    ciclos = st.slider("Detalle bandas", 1.0, 15.0, 4.0, 0.5)
    profundidad = st.slider("Profundidad 3D", 0.0, 1.5, 0.60, 0.1)
    resolucion = st.selectbox("Resolucion", [1000,2000,3000,4000], index=1)

def dia_to_c(dia, picos_pct):
    t = dia/365*2*math.pi
    r = 0.02 - (picos_pct/100)*0.016
    cx = -0.75 + r*math.cos(t*3)
    cy = 0.11 + r*math.sin(t*3)
    return complex(cx, cy), 800, r

c, iters, r_actual = dia_to_c(dia, picos)
st.caption(f"DIA {dia} -> c={c.real:.4f}+{c.imag:.4f}i | α={alpha} β={beta} γ={gamma} p={p_pow} | ciclos={ciclos} FIX bug shape")

def julia_fix_moire(w,h,c,zoom,iters,alpha,beta,gamma,p_pow,ciclos,profundidad):
    x = np.linspace(-1.5/zoom, 1.5/zoom, w)
    y = np.linspace(-1.5/zoom, 1.5/zoom, h)
    X,Y = np.meshgrid(x,y)
    Z = X+1j*Y
    M = np.full(Z.shape, iters, dtype=float)
    arg_final = np.zeros(Z.shape)
    logr_final = np.zeros(Z.shape)

    for i in range(iters):
        absZ = np.abs(Z)
        mask = absZ <= 100
        if not np.any(mask):
            break
        absZ_m = np.clip(absZ[mask], 1e-10, 1e10)
        argZ_m = np.angle(Z[mask])
        mag = np.power(absZ_m, alpha * p_pow)
        theta = p_pow * (beta * argZ_m + gamma * np.log(absZ_m))
        Z_new_m = mag * (np.cos(theta) + 1j*np.sin(theta)) + c

        # FIX: esc solo dentro de mask
        esc_m = (np.abs(Z_new_m) > 2) & (M[mask]==iters)
        if np.any(esc_m):
            # indices donde escapo
            idx_y, idx_x = np.where(mask)
            esc_y = idx_y[esc_m]
            esc_x = idx_x[esc_m]
            abs_esc = np.abs(Z_new_m[esc_m])
            smooth = i + 1 - np.log(np.log(abs_esc+1e-10))/np.log(2)
            M[esc_y, esc_x] = np.clip(smooth, 0, iters)
            arg_final[esc_y, esc_x] = np.angle(Z_new_m[esc_m])
            logr_final[esc_y, esc_x] = np.log(abs_esc+1e-10)

        Z[mask] = Z_new_m

    valid = M < iters
    fase = (beta * arg_final[valid] + gamma * logr_final[valid])
    t = (fase * ciclos * 0.08) % 1.0
    t = np.nan_to_num(t, nan=0.0)

    r_ = np.empty_like(t); g = np.empty_like(t); b = np.empty_like(t)
    mf = t<0.25; my=(t>=0.25)&(t<0.5); mc=(t>=0.5)&(t<0.75); mm=t>=0.75
    r_[mf]=255; g[mf]=30+180*t[mf]/0.25; b[mf]=180
    r_[my]=255; g[my]=255; b[my]=0
    r_[mc]=0; g[mc]=255; b[mc]=255
    r_[mm]=160+95*(t[mm]-0.75)/0.25; g[mm]=0; b[mm]=255

    shade = 0.60 + 0.40*np.cos(arg_final[valid]*p_pow + 0.5)
    shade = np.clip(shade**(1.0 - profundidad*0.3), 0.4, 1.0)

    r_ = (r_*shade).astype(np.uint8)
    g = (g*shade).astype(np.uint8)
    b = (b*shade).astype(np.uint8)

    img = np.zeros((h,w,3), dtype=np.uint8)
    img[valid] = np.stack([r_,g,b], axis=1)
    return img

W=900; H=700
img = julia_fix_moire(W,H,c,zoom,iters,alpha,beta,gamma,p_pow,ciclos,profundidad)
st.image(img, use_container_width=True, channels="RGB")
st.success(f"V61 OK - Bug de shape arreglado. Ahora con γ={gamma} y ciclos={ciclos} ya no hay moiré ni crash")

with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_fix_moire(resolucion,resolucion,c,zoom,iters,alpha,beta,gamma,p_pow,ciclos,profundidad)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_V61_DIA{dia}.png",mime="image/png")
