import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V65 CICLOS CLARO")
st.title("FRACTALES BAJO DEMANDA - V65 CICLOS PARAM")
st.latex(r"z_{n+1} = \left[ |z_n|^{\alpha} e^{i(\beta \arg z_n + \gamma \ln|z_n|) } \right]^p + c")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 273)
    zoom = st.slider("ZOOM", 0.2, 4.0, 1.20, 0.05)
    center_x = st.slider("Centro X", -0.8, 0.8, -0.15, 0.02)
    center_y = st.slider("Centro Y", -0.8, 0.8, 0.0, 0.02)
    picos = st.slider("PICOS / CALIDAD", 0, 100, 65)
    alpha = st.slider("α grosor pico", 0.5, 2.0, 1.0, 0.05)
    beta = st.slider("β torsion", 0.5, 2.0, 1.0, 0.05)
    gamma = st.slider("γ espiral (ALINEA BANDAS)", -1.0, 1.0, 0.35, 0.05)
    p_pow = st.slider("p num picos", 2, 5, 2)
    ciclos = st.slider("ciclos (NUM BANDAS)", 0.5, 15.0, 2.2, 0.1)
    profundidad = st.slider("Profundidad 3D", 0.0, 1.5, 0.60, 0.1)
    resolucion = st.selectbox("Resolucion", [1000,2000,3000,4000], index=1)

def dia_to_c(dia, picos_pct):
    t = dia/365*2*math.pi
    r = 0.02 - (picos_pct/100)*0.016
    cx = -0.75 + r*math.cos(t*3)
    cy = 0.11 + r*math.sin(t*3)
    return complex(cx, cy), 1000, r

c, iters, _ = dia_to_c(dia, picos)
st.caption(f"DIA {dia} | γ={gamma} alinea bandas con picos | ciclos={ciclos} controla grosor | V63 tenias ciclos=8=delgadas, baja a 2.2=gruesas")

def julia_v65(w,h,c,zoom,cx,cy,iters,alpha,beta,gamma,p_pow,ciclos,profundidad):
    x = np.linspace(-1.5/zoom + cx, 1.5/zoom + cx, w)
    y = np.linspace(-1.0/zoom + cy, 1.0/zoom + cy, h)
    X,Y = np.meshgrid(x,y)
    Z = X+1j*Y
    M = np.full(Z.shape, iters, dtype=float)
    arg_final = np.zeros(Z.shape)
    logr_final = np.zeros(Z.shape)
    for i in range(iters):
        absZ = np.abs(Z)
        mask = absZ <= 100
        if not np.any(mask): break
        absZ_m = np.clip(absZ[mask], 1e-10, 1e10)
        argZ_m = np.angle(Z[mask])
        mag = np.power(absZ_m, alpha * p_pow)
        theta = p_pow * (beta * argZ_m + gamma * np.log(absZ_m))
        Z_new_m = mag * (np.cos(theta) + 1j*np.sin(theta)) + c
        esc_m = (np.abs(Z_new_m) > 2) & (M[mask]==iters)
        if np.any(esc_m):
            iy, ix = np.where(mask)
            ey = iy[esc_m]; ex = ix[esc_m]
            abs_esc = np.abs(Z_new_m[esc_m])
            M[ey, ex] = np.clip(i + 1 - np.log(np.log(abs_esc+1e-10))/np.log(2), 0, iters)
            arg_final[ey, ex] = np.angle(Z_new_m[esc_m])
            logr_final[ey, ex] = np.log(abs_esc+1e-10)
        Z[mask] = Z_new_m
    valid = M < iters
    fase = (beta * arg_final[valid] + gamma * logr_final[valid])
    s = (fase * ciclos * 0.25) % 1.0
    t = s * 4.0
    i0 = np.floor(t).astype(int) % 4
    f = (1 - np.cos((t - np.floor(t))*np.pi))/2
    cols = np.array([[255,0,255],[255,255,0],[0,255,255],[0,200,80]], float)
    r_=np.zeros_like(s); g_=np.zeros_like(s); b_=np.zeros_like(s)
    for k in range(4):
        m = i0==k; nk=(k+1)%4
        r_[m]=(1-f[m])*cols[k,0]+f[m]*cols[nk,0]
        g_[m]=(1-f[m])*cols[k,1]+f[m]*cols[nk,1]
        b_[m]=(1-f[m])*cols[k,2]+f[m]*cols[nk,2]
    shade = 0.65 + 0.35*np.cos(arg_final[valid]*p_pow*0.8 + 0.5)
    shade = np.clip(shade**(1.0-profundidad*0.25),0.55,1.0)
    r_=(r_*shade).astype(np.uint8); g_=(g_*shade).astype(np.uint8); b_=(b_*shade).astype(np.uint8)
    img=np.zeros((h,w,3),dtype=np.uint8)
    img[valid]=np.stack([r_,g_,b_],axis=1)
    return img

W=1100; H=700
img=julia_v65(W,H,c,zoom,center_x,center_y,iters,alpha,beta,gamma,p_pow,ciclos,profundidad)
st.image(img,use_container_width=True,channels="RGB")
st.success(f"ciclos={ciclos}: 2.0=bandas gruesas como tu ref | 8.0=bandas delgaditas arcoiris como tu captura V63 | 15=moiré")

with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_v65(resolucion,resolucion,c,zoom,center_x,center_y,iters,alpha,beta,gamma,p_pow,ciclos,profundidad)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_V65_ciclos{ciclos}_DIA{dia}.png",mime="image/png")
