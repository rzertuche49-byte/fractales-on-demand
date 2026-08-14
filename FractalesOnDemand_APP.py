import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image
import io

st.set_page_config(page_title="Fractales On Demand V5", layout="wide")
st.title("FRACTALES ON DEMAND - V5 LIMPIO")

# --- CONTROLES ON DEMAND ---
with st.sidebar:
    st.header("Controles")
    DIA = st.slider("DIA (1-365)", 1, 365, 200)
    ZOOM = st.slider("ZOOM", 0.8, 2.0, 1.15, 0.05)
    ITERS = st.slider("CALIDAD (iters)", 300, 1500, 800, 100)
    SIZE_PREVIEW = 800
    SIZE_EXPORT = st.selectbox("Resolucion Export", [2000, 3000, 5000, 8000], index=1)
    FONDO_TRANSP = st.checkbox("Fondo Transparente (para lona)", value=False)
    COLOR_SOLIDO = st.color_picker("Color Interior", "#E93A8D")

    st.markdown("---")
    st.subheader("Paleta Fuego")
    c1 = st.color_picker("Color 1", "#000000")
    c2 = st.color_picker("Color 2", "#1A0A3A")
    c3 = st.color_picker("Color 3", "#4A0C7A")
    c4 = st.color_picker("Color 4", "#C80082")
    c5 = st.color_picker("Color 5", "#FF3C00")
    c6 = st.color_picker("Color 6", "#FF8A00")

COLORES_GLOW = [c1,c2,c3,c4,c5,c6]

# --- MOTOR ---

def julia_calc(c, size, iters, zoom):
    x = np.linspace(-zoom, zoom, size)
    y = np.linspace(-zoom, zoom, size)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j*Y
    M = np.zeros(Z.shape, dtype=float)
    for i in range(iters):
        mask = np.abs(Z) < 4
        if not np.any(mask): break
        Z[mask] = Z[mask]**2 + c
        M[mask] = i - np.log2(np.log2(np.abs(Z[mask]) + 1.0001))
    return M, Z, X, Y

# Mapa 6 petalos
thetas = np.arange(1,366)/365 * 2*np.pi
base_c = -0.12 + 0.75j
MAPA = {d: complex(base_c.real + 0.03*np.cos(thetas[d-1]), base_c.imag + 0.03*np.sin(thetas[d-1])) for d in range(1,366)}
c = MAPA[DIA]

st.write(f"Generando DIA {DIA} | c={c:.6f} | ZOOM={ZOOM}")

# Preview rapido
M, Z, X, Y = julia_calc(c, SIZE_PREVIEW, ITERS, ZOOM)

interior = np.abs(Z) < 4
escaped = ~interior
final = np.zeros((M.shape[0], M.shape[1], 4))

# Hex to RGB
def hex2rgb(h):
    h=h.lstrip('#')
    return tuple(int(h[i:i+2], 16)/255 for i in (0,2,4))

final[interior] = [*hex2rgb(COLOR_SOLIDO), 1]

cmap_glow = LinearSegmentedColormap.from_list("glow", COLORES_GLOW, N=1024)
glow_mask = escaped & (M < 50)
if np.any(glow_mask):
    norm = plt.Normalize(vmin=0, vmax=50)
    final[glow_mask] = cmap_glow(norm(M[glow_mask]))

if FONDO_TRANSP:
    far = escaped & (M >= 50)
    final[far] = [0,0,0,0]
else:
    bg = escaped & (M >= 50)
    if np.any(bg):
        final[bg] = [0.02, 0.01, 0.08, 1]

sep = escaped & (M >= 18) & (M < 22)
final[sep] = [0,0,0,1]

# Mostrar
st.image(final, caption=f"FRACTAL DIA {DIA}", use_container_width=True)

# Exportar 8K
if st.button(f"EXPORTAR EN {SIZE_EXPORT}x{SIZE_EXPORT} 8K"):
    with st.spinner("Generando 8K... tarda 1-2 min"):
        Mh, Zh, Xh, Yh = julia_calc(c, SIZE_EXPORT, ITERS, ZOOM)
        interior_h = np.abs(Zh) < 4
        escaped_h = ~interior_h
        final_h = np.zeros((Mh.shape[0], Mh.shape[1], 4))
        final_h[interior_h] = [*hex2rgb(COLOR_SOLIDO), 1]
        glow_h = escaped_h & (Mh < 50)
        if np.any(glow_h):
            norm = plt.Normalize(vmin=0, vmax=50)
            final_h[glow_h] = cmap_glow(norm(Mh[glow_h]))
        if FONDO_TRANSP:
            final_h[escaped_h & (Mh >= 50)] = [0,0,0,0]
        else:
            final_h[escaped_h & (Mh >= 50)] = [0.02, 0.01, 0.08, 1]
        final_h[escaped_h & (Mh >= 18) & (Mh < 22)] = [0,0,0,1]

        buf = io.BytesIO()
        plt.imsave(buf, final_h, dpi=600, format='png')
        st.download_button("DESCARGAR PNG 8K", buf.getvalue(), file_name=f"FRACTAL_V5_DIA{DIA}_{SIZE_EXPORT}.png", mime="image/png")
