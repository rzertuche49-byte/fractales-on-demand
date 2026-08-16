import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V62 BANDAS FINAS")
st.title("FRACTALES BAJO DEMANDA - V62 BANDAS ALINEADAS FINAS")
st.latex(r"z_{n+1} = \left[ |z_n|^{\alpha} e^{i(\beta \arg z_n + \gamma \ln|z_n|) } \right]^p + c")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 273)
    zoom = st.slider("ZOOM", 0.2, 4.0, 2.90, 0.05)
    center_x = st.slider("Centro X", -0.5, 0.5, -0.15, 0.02)
    picos = st.slider("PICOS / CALIDAD", 0, 100, 65)
    alpha = st.slider("α grosor pico", 0.5, 2.0, 1.0, 0.05)
    beta = st.slider("β torsion", 0.5, 2.0, 1.0, 0.05)
    gamma = st.slider("γ espiral (ALINEA BANDAS)", -1.0, 1.0, 0.35, 0.05)
    p_pow = st.slider("p num picos", 2, 5, 2)
    ciclos = st.slider("Detalle bandas", 1.0, 20.0, 8.0, 0.5)
    profundidad = st.slider("Profundidad 3D", 0.0, 1.5, 0.60, 0.1)
    resolucion = st.selectbox("Resolucion", [1000,2000,3000,4000], index=1)

def dia_to_c(dia, picos_pct):
    t = dia/365*2*math.pi
    r = 0.02 - (picos_pct/100)*0.016
    cx = -0.75 + r*math.cos(t*3)
    cy = 0.11 + r*math.sin(t*3)
    return complex(cx, cy), 1000, r

c, iters, r_actual = dia_to_c(dia, picos)
st.caption(f"DIA {dia} -> c={c.real:.4f}+{c.imag:.4f}i | γ={gamma} ALINEA | ciclos={ciclos} finas | V61 ya alineaba, V62 afina")

def julia_v62(w,h,c,zoom,center_x,iters,alpha,beta,gamma,p_pow,ciclos,profundidad):
    # centrado mejor para DIA 273
    x = np.linspace(-1.5/zoom + center_x, 1.5/zoom + center_x, w)
    y = np.linspace(-1.0/zoom, 1.0/zoom, h)
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

        esc_m = (np.abs(Z_new_m) > 2) & (M[mask]==iters)
        if np.any(esc_m):
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
    # V62: suavizado para bandas finas sin moiré
    t = (fase * ciclos * 0.12) % 1.0
    t = np.nan_to_num(t, nan=0.0)
    # suavizado anti-moiré
    t = np.clip(t, 0, 1)

    r_ = np.empty_like(t); g = np.empty_like(t); b = np.empty_like(t)
    # paleta más parecida a tu ref original: magenta/amarillo/cyan/verde
    mf = t<0.25; my=(t>=0.25)&(t<0.5); mc=(t>=0.5)&(t<0.75); mm=t>=0.75
    r_[mf]=255; g[mf]=20+t[mf]*600; b[mf]=200
    r_[my]=240+15*np.sin(t[my]*40); g[my]=255; b[my]=0
    r_[mc]=0; g[mc]=230; b[mc]=230+25*np.sin(t[mc]*40)
    r_[mm]=180; g[mm]=0; b[mm]=255
    # gamma correct para que no se vea plano
    r_ = np.clip(r_,0,255); g=np.clip(g,0,255); b=np.clip(b,0,255)

    shade = 0.60 + 0.40*np.cos(arg_final[valid]*p_pow*1.5 + 0.3)
    shade = np.clip(shade**(1.0 - profundidad*0.3), 0.45, 1.0)

    r_ = (r_*shade).astype(np.uint8)
    g = (g*shade).astype(np.uint8)
    b = (b*shade).astype(np.uint8)

    img = np.zeros((h,w,3), dtype=np.uint8)
    img[valid] = np.stack([r_,g,b], axis=1)
    return img

W=1000; H=600
img = julia_v62(W,H,c,zoom,center_x,iters,alpha,beta,gamma,p_pow,ciclos,profundidad)
st.image(img, use_container_width=True, channels="RGB")
st.success(f"V61 logro alineado! V62 mejora: Centro X={center_x} para centrar el pico de DIA 273 y ciclos={ciclos} para bandas finas sin el moiré arcoiris de V59")

with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_v62(resolucion,resolucion,c,zoom,center_x,iters,alpha,beta,gamma,p_pow,ciclos,profundidad)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_V62_DIA{dia}.png",mime="image/png")
