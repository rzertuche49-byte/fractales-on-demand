import streamlit as st
import numpy as np
from PIL import Image
import io, math

st.set_page_config(layout="wide", page_title="V55 PICOS REALES")
st.title("FRACTALES BAJO DEMANDA - V55 PICOS REALES")
with st.sidebar:
    dia = st.slider("DIA", 1, 365, 273)
    zoom = st.slider("ZOOM", 0.2, 4.0, 2.90, 0.05)
    picos = st.slider("PICOS / CALIDAD", 100, 2500, 2500, 50)
    ciclos = st.slider("Detalle bandas", 5.0, 50.0, 28.0, 0.5)
    profundidad = st.slider("Profundidad 3D", 0.0, 1.5, 0.60, 0.1)
    resolucion = st.selectbox("Resolucion", [1000,2000,3000,4000], index=1)

def dia_to_c_con_picos(dia, picos_val):
    t = dia/365*2*math.pi
    # TRUCO REAL: PICOS controla que tan cerca del borde esta el c
    # 100 = lejos = sin picos, pelon
    # 2500 = pegadito al borde = arbol gigante como tu ref
    # Formula: r = 0.08 a 0.0005
    r = 0.08 - (picos_val/2500)*0.0795
    # c base del dendrite
    base_cx, base_cy = -0.7269, 0.1889
    cx = base_cx + r*math.cos(t*4)*0.5
    cy = base_cy + r*math.sin(t*4)*0.5
    # iteraciones fijas altas para que no haya ruido
    iters = 1200
    return complex(cx, cy), iters, r

c, iters, r_actual = dia_to_c_con_picos(dia, picos)
st.caption(f"DIA {dia} -> c={c.real:.5f}+{c.imag:.5f}i | PICOS={picos} | r={r_actual:.5f} (0.08=pelon, 0.0005=arbol gigante) | ZOOM {zoom}")

def julia_picos_control(w,h,c,zoom,iters,ciclos,profundidad):
    x = np.linspace(-1.5/zoom, 1.5/zoom, w)
    y = np.linspace(-1.5/zoom, 1.5/zoom, h)
    X,Y = np.meshgrid(x,y)
    Z = X+1j*Y
    M = np.full(Z.shape, iters, dtype=float)
    ang = np.zeros(Z.shape)
    escaped_at = np.full(Z.shape, iters)

    for i in range(iters):
        mask = np.abs(Z) <= 10
        esc = mask & (np.abs(Z) > 2) & (M==iters)
        if np.any(esc):
            M[esc] = i + 1 - np.log2(np.log(np.abs(Z[esc])+1e-10))
            ang[esc] = np.angle(Z[esc])
            escaped_at[esc] = i
        Z[mask] = Z[mask]*Z[mask] + c
        if not np.any(mask):
            break

    valid = M < iters
    is_noise = (escaped_at <= 2) & (np.abs(X+1j*Y) > 0.8/zoom)
    limpio = valid & (~is_noise)

    t = (M[limpio] * ciclos * 0.06 + ang[limpio]*0.35) % 1.0

    r_ = np.empty_like(t); g = np.empty_like(t); b = np.empty_like(t)
    mf = t<0.25; my=(t>=0.25)&(t<0.5); mc=(t>=0.5)&(t<0.75); mm=t>=0.75
    r_[mf]=255; g[mf]=30+180*t[mf]/0.25; b[mf]=180
    r_[my]=255; g[my]=255; b[my]=0
    r_[mc]=0; g[mc]=255; b[mc]=255
    r_[mm]=160+95*(t[mm]-0.75)/0.25; g[mm]=0; b[mm]=255

    shade = 0.55 + 0.45*np.cos(ang[limpio]*2 + 1.2)
    shade = np.clip(shade**(1.0 - profundidad*0.3), 0.35, 1.0)

    r_ = (r_*shade).astype(np.uint8)
    g = (g*shade).astype(np.uint8)
    b = (b*shade).astype(np.uint8)

    img = np.zeros((h,w,3), dtype=np.uint8)
    img[limpio] = np.stack([r_,g,b], axis=1)
    return img

W=800; H=800
img = julia_picos_control(W,H,c,zoom,iters,ciclos,profundidad)
st.image(img, use_container_width=True, channels="RGB")
st.info(f"Con PICOS={picos}, r={r_actual:.5f}. Prueba: pon PICOS en 100 y veras tronco pelon. Ponlo en 2500 y veras arbol gigante. Ahora SI funciona.")

with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_picos_control(resolucion,resolucion,c,zoom,iters,ciclos,profundidad)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_V55_PICOS{picos}_DIA{dia}.png",mime="image/png")
