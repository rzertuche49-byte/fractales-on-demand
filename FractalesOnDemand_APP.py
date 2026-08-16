import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V69 MIX FINAL")
st.title("FRACTALES BAJO DEMANDA - V69 MIX (BORDE + TRAP)")
st.latex(r"z_{n+1} = \left[ |z_n|^{\alpha} e^{i(\beta \arg z_n + \gamma \ln|z_n|) } \right]^p + c")

with st.sidebar:
    dia = st.slider("DIA", 1, 365, 283)
    zoom = st.slider("ZOOM", 0.2, 4.0, 4.00, 0.05)
    center_x = st.slider("Centro X", -0.8, 1.2, 0.80, 0.02)
    center_y = st.slider("Centro Y", -0.8, 0.8, 0.00, 0.02)
    picos = st.slider("PICOS / CALIDAD", 0, 100, 100)
    alpha = st.slider("α grosor pico", 0.5, 2.0, 2.00, 0.05)
    beta = st.slider("β torsion", 0.5, 2.0, 2.00, 0.05)
    gamma = st.slider("γ espiral", -1.0, 1.0, 0.80, 0.05)
    p_pow = st.slider("p num picos", 2, 5, 5)
    modo = st.selectbox("MODO COLOR", ["MIX - borde sigue picos (RECOMENDADO)", "TRAP LINE - rayos", "TRAP POINT - rodea", "ESCAPE TIME - clasico"])
    ciclos = st.slider("ciclos (NUM BANDAS)", 0.1, 5.0, 0.70, 0.05)
    resolucion = st.selectbox("Resolucion", [1000,2000,3000,4000], index=2)

def dia_to_c(dia, picos_pct):
    t = dia/365*2*math.pi
    r = 0.02 - (picos_pct/100)*0.016
    cx = -0.75 + r*math.cos(t*3)
    cy = 0.11 + r*math.sin(t*3)
    return complex(cx, cy), 1200, r

c, iters, _ = dia_to_c(dia, picos)
st.caption(f"V68 falló: CROSS/LINE dieron rayitos delgados. V69 MIX: usa ángulo final + log para bandas gruesas que SIGUEN el contorno. DIA {dia} ciclos={ciclos}")

def julia_v69(w,h,c,zoom,cx,cy,iters,alpha,beta,gamma,p_pow,modo,ciclos):
    x = np.linspace(-1.5/zoom + cx, 1.5/zoom + cx, w)
    y = np.linspace(-1.0/zoom + cy, 1.0/zoom + cy, h)
    X,Y = np.meshgrid(x,y)
    Z = X+1j*Y
    M = np.full(Z.shape, iters, dtype=float)
    arg_final = np.zeros(Z.shape)
    abs_final = np.zeros(Z.shape)

    for i in range(iters):
        absZ = np.abs(Z)
        mask = absZ <= 100
        if not np.any(mask): break
        absZm = np.clip(absZ[mask], 1e-10, 1e10)
        argZm = np.angle(Z[mask])
        mag = np.power(absZm, alpha * p_pow)
        theta = p_pow * (beta * argZm + gamma * np.log(absZm))
        Z_new_m = mag * (np.cos(theta) + 1j*np.sin(theta)) + c
        esc_m = (np.abs(Z_new_m) > 2) & (M[mask]==iters)
        if np.any(esc_m):
            iy, ix = np.where(mask)
            abs_esc = np.abs(Z_new_m[esc_m])
            M[iy[esc_m], ix[esc_m]] = i + 1 - np.log(np.log(abs_esc+1e-10))/np.log(2)
            arg_final[iy[esc_m], ix[esc_m]] = np.angle(Z_new_m[esc_m])
            abs_final[iy[esc_m], ix[esc_m]] = abs_esc
        Z[mask] = Z_new_m

    valid = M < iters
    if "MIX" in modo:
        # V69 MIX: el secreto de las refs virales
        # fase = arg_final * p + gamma*log|z| -> sigue contorno
        # + M*0.1 para que no sea totalmente radial
        fase = (p_pow * arg_final[valid] + gamma * np.log(abs_final[valid]+1e-6) + M[valid]*0.15)
    elif "LINE" in modo:
        fase = np.abs(np.sin(p_pow * arg_final[valid] * 0.5)) * 5
    elif "POINT" in modo:
        fase = M[valid] * 0.5
    else: # escape
        fase = M[valid]

    s = (fase * ciclos * 0.25) % 1.0
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
img=julia_v69(W,H,c,zoom,center_x,center_y,iters,alpha,beta,gamma,p_pow,modo,ciclos)
st.image(img,use_container_width=True,channels="RGB")
st.success(f"MODO={modo} | Para tu ref usa MIX con ciclos 0.6-0.9 | LINE daba rayitos delgados (tu captura CROSS/LINE) | MIX da bandas gruesas siguiendo contorno")

with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_v69(resolucion,resolucion,c,zoom,center_x,center_y,iters,alpha,beta,gamma,p_pow,modo,ciclos)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_V69_{modo}_DIA{dia}.png",mime="image/png")
