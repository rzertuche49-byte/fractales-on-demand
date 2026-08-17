import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V73 TRAP + ZOOM")
st.title("FRACTALES BAJO DEMANDA - V73 ORBIT TRAP + ZOOM 50X")
st.latex(r"z_{n+1} = \left[ |z_n|^{\alpha} e^{i(\beta \arg z_n + \gamma \ln|z_n|) } \right]^p + c")

with st.sidebar:
    dia = st.slider("DIA", 1, 365, 283)
    zoom = st.slider("ZOOM", 0.2, 50.0, 10.00, 0.05)
    center_x = st.slider("Centro X", -1.5, 1.5, 0.69, 0.005)
    center_y = st.slider("Centro Y", -1.5, 1.5, 0.46, 0.005)
    picos = st.slider("PICOS / CALIDAD", 0, 100, 100)
    alpha = st.slider("α grosor pico", 0.5, 2.0, 2.00, 0.05)
    beta = st.slider("β torsion", 0.5, 2.0, 1.00, 0.05)
    gamma = st.slider("γ espiral (0 para zoom >15x)", -1.0, 1.0, 0.00, 0.05)
    p_pow = st.slider("p num picos", 2, 5, 5)

    st.divider()
    st.markdown("### ORBIT TRAP")
    use_trap = st.checkbox("Activar ORBIT TRAP", value=True)
    trap_type = st.selectbox("Tipo TRAP", ["line angular - sigue picos", "cross angular - ramitas", "point - rodea suave", "circle - anillos", "MIX (sin trap) - clasico"])
    trap_radius = st.slider("Radio TRAP (circle)", 0.1, 2.0, 0.5, 0.1)
    trap_blend = st.slider("Mezcla TRAP / BORDE", 0.0, 1.0, 0.70, 0.05)
    st.caption("70% trap = bandas siguen picos. 0% = solo borde")

    st.divider()
    mezcla = st.slider("Mezcla borde/contorno", 0.0, 1.0, 0.20, 0.05)
    ciclos = st.slider("ciclos (BAJALO para gruesas)", 0.05, 5.0, 0.35, 0.05)
    iters_extra = st.slider("Iteraciones (1500+ para zoom alto)", 0, 3000, 1500, 100)
    preview_res = st.selectbox("Preview", [800,1200,1600], index=1)
    resolucion = st.selectbox("Export", [2000,3000,4000,6000,8000], index=2)

def dia_to_c(dia, picos_pct):
    t = dia/365*2*math.pi
    r = 0.02 - (picos_pct/100)*0.016
    cx = -0.75 + r*math.cos(t*3)
    cy = 0.11 + r*math.sin(t*3)
    return complex(cx, cy), 1000, r

c, base_iters, _ = dia_to_c(dia, picos)
iters = base_iters + iters_extra

def julia_v73(w,h,c,zoom,cx,cy,iters,alpha,beta,gamma,p_pow,trap_type,trap_radius,trap_blend,mezcla,ciclos,use_trap):
    x = np.linspace(-1.5/zoom + cx, 1.5/zoom + cx, w, dtype=np.float64)
    y = np.linspace(-1.0/zoom + cy, 1.0/zoom + cy, h, dtype=np.float64)
    X,Y = np.meshgrid(x,y)
    Z = X+1j*Y
    M = np.full(Z.shape, iters, dtype=np.float64)
    arg_final = np.zeros(Z.shape, dtype=np.float64)
    trap_dist = np.full(Z.shape, 1e10, dtype=np.float64)

    for i in range(iters):
        absZ = np.abs(Z)
        mask = absZ <= 1e4
        if not np.any(mask): break
        Zm = Z[mask]
        absZm = absZ[mask]
        ang = np.angle(Zm)

        if use_trap:
            if "line" in trap_type:
                d = np.abs(np.sin(p_pow * ang * 0.5)) * (absZm*0.3 + 0.7)
            elif "cross" in trap_type:
                d = np.abs(np.sin(p_pow * ang)) * (absZm*0.3 + 0.7)
            elif "point" in trap_type:
                d = absZm
            elif "circle" in trap_type:
                d = np.abs(absZm - trap_radius)
            else:
                d = absZm
            iy, ix = np.where(mask)
            trap_dist[iy, ix] = np.minimum(trap_dist[iy, ix], d)

        absZm_c = np.clip(absZm, 1e-12, 1e12)
        mag = np.power(absZm_c, alpha * p_pow)
        theta = p_pow * (beta * ang + gamma * np.log(absZm_c))
        Z_new_m = mag * (np.cos(theta) + 1j*np.sin(theta)) + c
        esc_m = (np.abs(Z_new_m) > 256) & (M[mask]==iters)
        if np.any(esc_m):
            iy, ix = np.where(mask)
            M[iy[esc_m], ix[esc_m]] = i + 1 - np.log(np.log(np.abs(Z_new_m[esc_m])+1e-10))/np.log(2)
            arg_final[iy[esc_m], ix[esc_m]] = np.angle(Z_new_m[esc_m])
        Z[mask] = Z_new_m

    valid = M < iters
    fase_borde = (1-mezcla)*(p_pow*arg_final[valid]) + mezcla*M[valid]

    if use_trap and "MIX" not in trap_type:
        td = np.clip(trap_dist[valid], 1e-5, 10)
        fase_trap = -np.log(td + 1e-6) * 2.0
        if "point" in trap_type or "circle" in trap_type:
            fase_trap = fase_trap * 0.5
        fase = (1-trap_blend)*fase_borde*0.5 + trap_blend*fase_trap
    else:
        fase = fase_borde*0.5

    s = (fase * ciclos * 0.15) % 1.0
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

W=preview_res; H=int(W*0.58)
img=julia_v73(W,H,c,zoom,center_x,center_y,iters,alpha,beta,gamma,p_pow,trap_type,trap_radius,trap_blend,mezcla,ciclos,use_trap)
st.image(img,use_container_width=True,channels="RGB")
st.info(f"V73 | TRAP={'ON '+trap_type if use_trap else 'OFF'} | Blend {trap_blend} | Zoom {zoom}x {iters} iters | line angular = bandas siguen picos | point/circle = rodea")

with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_v73(resolucion,int(resolucion*0.58),c,zoom,center_x,center_y,iters,alpha,beta,gamma,p_pow,trap_type,trap_radius,trap_blend,mezcla,ciclos,use_trap)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_V73_{trap_type}_ZOOM{zoom}_DIA{dia}.png",mime="image/png")
