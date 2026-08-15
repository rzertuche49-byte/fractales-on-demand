import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V59 FORMULA REAL")
st.title("FRACTALES BAJO DEMANDA - V59 FORMULA α β γ p")
st.latex(r"z_{n+1} = \left[ |z_n|^{\alpha} e^{i(\beta \arg z_n + \gamma \ln|z_n|) } \right]^p + c")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 273)
    zoom = st.slider("ZOOM", 0.2, 4.0, 2.90, 0.05)
    picos = st.slider("PICOS / CALIDAD", 0, 100, 65)
    alpha = st.slider("α grosor pico", 0.5, 2.0, 1.0, 0.05)
    beta = st.slider("β torsion", 0.5, 2.0, 1.0, 0.05)
    gamma = st.slider("γ espiral (ALINEA BANDAS)", -1.0, 1.0, 0.35, 0.05)
    p_pow = st.slider("p num picos", 1, 5, 2)
    ciclos = st.slider("Detalle bandas", 5.0, 50.0, 28.0, 0.5)
    profundidad = st.slider("Profundidad 3D", 0.0, 1.5, 0.60, 0.1)
    resolucion = st.selectbox("Resolucion", [1000,2000,3000,4000], index=1)

def dia_to_c(dia, picos_pct):
    t = dia/365*2*math.pi
    r = 0.02 - (picos_pct/100)*0.016
    cx = -0.75 + r*math.cos(t*3)
    cy = 0.11 + r*math.sin(t*3)
    return complex(cx, cy), 1000, r

c, iters, r_actual = dia_to_c(dia, picos)
st.caption(f"DIA {dia} -> c={c.real:.4f}+{c.imag:.4f}i | α={alpha} β={beta} γ={gamma} p={p_pow} | γ>0 alinea bandas con picos")

def julia_formula_real(w,h,c,zoom,iters,alpha,beta,gamma,p_pow,ciclos,profundidad):
    x = np.linspace(-1.5/zoom, 1.5/zoom, w)
    y = np.linspace(-1.5/zoom, 1.5/zoom, h)
    X,Y = np.meshgrid(x,y)
    Z = X+1j*Y
    M = np.full(Z.shape, iters, dtype=float)
    ang = np.zeros(Z.shape)

    for i in range(iters):
        mask = np.abs(Z) <= 100
        absZ = np.abs(Z[mask])
        argZ = np.angle(Z[mask])
        # FORMULA REAL que me mandaste
        # |Zn|^α * e^{i(β arg + γ ln|Zn|)} ^p
        # = |Zn|^{α*p} * e^{i p(β arg + γ ln|Zn|)}
        absZ = np.clip(absZ, 1e-10, 1e10)
        mag = np.power(absZ, alpha * p_pow)
        theta = p_pow * (beta * argZ + gamma * np.log(absZ))
        Z_new = mag * (np.cos(theta) + 1j*np.sin(theta)) + c

        esc = mask & (np.abs(Z) > 2) & (M==iters)
        if np.any(esc):
            absZ_esc = np.abs(Z[esc])
            smooth = i + 1 - np.log(np.log(absZ_esc+1e-10))/np.log(2)
            M[esc] = np.clip(smooth, 0, iters)
            ang[esc] = np.angle(Z[esc])

        Z[mask] = Z_new
        if not np.any(mask):
            break

    valid = M < iters
    # AHORA con gamma, las bandas siguen la espiral logarítmica
    t = (ang[valid] * ciclos * 0.15 + M[valid]*0.01) % 1.0
    t = np.nan_to_num(t, nan=0.0)

    r_ = np.empty_like(t); g = np.empty_like(t); b = np.empty_like(t)
    mf = t<0.25; my=(t>=0.25)&(t<0.5); mc=(t>=0.5)&(t<0.75); mm=t>=0.75
    r_[mf]=255; g[mf]=30+180*t[mf]/0.25; b[mf]=180
    r_[my]=255; g[my]=255; b[my]=0
    r_[mc]=0; g[mc]=255; b[mc]=255
    r_[mm]=160+95*(t[mm]-0.75)/0.25; g[mm]=0; b[mm]=255

    shade = 0.55 + 0.45*np.cos(ang[valid]*p_pow + 0.5)
    shade = np.clip(shade**(1.0 - profundidad*0.3), 0.35, 1.0)

    r_ = (r_*shade).astype(np.uint8)
    g = (g*shade).astype(np.uint8)
    b = (b*shade).astype(np.uint8)

    img = np.zeros((h,w,3), dtype=np.uint8)
    img[valid] = np.stack([r_,g,b], axis=1)
    return img

W=800; H=800
img = julia_formula_real(W,H,c,zoom,iters,alpha,beta,gamma,p_pow,ciclos,profundidad)
st.image(img, use_container_width=True, channels="RGB")
st.info(f"Con γ={gamma}: γ=0 da anillos rodeando picos (V57 bug). γ=0.35 da bandas a lo largo de picos como tu ref. Prueba subir γ a 0.5")

with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_formula_real(resolucion,resolucion,c,zoom,iters,alpha,beta,gamma,p_pow,ciclos,profundidad)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_V59_FORMULA_DIA{dia}.png",mime="image/png")
