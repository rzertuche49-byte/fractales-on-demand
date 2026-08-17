import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io, math

st.set_page_config(layout="wide", page_title="V88")

def hex_to_rgb(h):
    h = h.lstrip('#')
    return [int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)]

PALETAS = {
    "Tu captura": ["#00FFFF","#0064FF","#FF00C8","#FF6400","#FFFF00","#00FF64"],
    "Neon 80s": ["#00FFFF","#FF00FF","#FFFF00","#00FF00","#FF0066","#6600FF"],
    "Fuego": ["#FF0000","#FF6600","#FFCC00","#FF3300","#CC0000","#FF9900"],
    "Oceano Profundo": ["#001F54","#034078","#1282A2","#00B4D8","#90E0EF","#CAF0F8"],
    "Pastel Dream": ["#FFB5E8","#B5DEFF","#C3FF99","#FFF5BA","#FFC9DE","#D1BDFF"],
    "Sunset": ["#F72585","#7209B7","#3A0CA3","#4361EE","#4CC9F0","#FFBE0B"],
    "Galaxy": ["#0B0C10","#1F2833","#45A29E","#66FCF1","#C5C6C7","#9D00FF"],
    "Toxic": ["#00FF00","#CCFF00","#00FFCC","#FFFF00","#FF00FF","#00FFFF"],
    "Candy": ["#FF70A6","#FF9770","#FFD670","#E9FF70","#70FFB2","#70D6FF"],
    "Bosque": ["#0A2F0A","#1B5E20","#2E7D32","#66BB6A","#A5D6A7","#C8E6C9"],
    "Volcan": ["#000000","#4A0000","#8B0000","#FF4500","#FF8C00","#FFD700"],
    "Aurora": ["#03045E","#0077B6","#00B4D8","#90E0EF","#ADE8F4","#CAF0F8"],
    "Miami Vice": ["#FF6BEC","#3EFFE2","#FFD93D","#FF6B6B","#6BCB77","#4D96FF"],
    "Cyberpunk": ["#FF003C","#00F0FF","#F0FF00","#FF00F0","#00FF9F","#7000FF"],
    "Helado": ["#FEC8D8","#FFDFD3","#FFF0B5","#D0F4DE","#A9DEF9","#E4C1F9"],
    "Matrix": ["#000000","#003B00","#008F11","#00FF41","#00FF00","#AAFF00"],
    "Desierto": ["#7F5539","#9C6644","#B08968","#DDB892","#E6CCB2","#EDE0D4"],
    "Joker": ["#3D087B","#5A189A","#7B2CBF","#9D4EDD","#C77DFF","#00F5D4"],
}

with st.sidebar:
    nombre_cliente = st.text_input("Nombre del cliente / proyecto", "FRACTALES ON DEMAND")
    firma = st.text_input("Firma", "© 2026")
    st.divider()
    dia = st.slider("DIA", 1, 365, 283)
    zoom = st.slider("ZOOM", 0.2, 5.0, 0.88)
    paleta_nombre = st.selectbox("PALETA", list(PALETAS.keys()), index=0)
    base = PALETAS[paleta_nombre]
    st.write("**EDITA 6 COLORES**")
    c1 = st.color_picker("Color 1", base[0])
    c2 = st.color_picker("Color 2", base[1])
    c3 = st.color_picker("Color 3", base[2])
    c4 = st.color_picker("Color 4", base[3])
    c5 = st.color_picker("Color 5", base[4])
    c6 = st.color_picker("Color 6", base[5])
    colores_actuales = [c1,c2,c3,c4,c5,c6]
    st.write("---")
    tam = st.slider("Tamaño mancha", 0.1, 3.0, 1.8)
    brillo = st.slider("Brillo", 0.5, 2.5, 1.4)
    st.divider()
    fondo_transparente = st.checkbox("Fondo transparente", value=False)
    umbral = st.slider("Limpieza fondo", 0.0, 5.0, 1.0)
    st.divider()
    incluir_etiqueta_en_imagen = st.checkbox("Incrustar nombre técnico en la imagen", value=True)

st.title(f"{nombre_cliente}")

# Motor fractal
t = dia/365*2*math.pi
cx = -0.745 + 0.005*math.cos(t*3)
cy = 0.11 + 0.005*math.sin(t*3)
c = complex(cx, cy)
x = np.linspace(-1.5/zoom, 1.5/zoom, 1000)
y = np.linspace(-1.0/zoom, 1.0/zoom, 800)
X,Y = np.meshgrid(x,y)
Z = X+1j*Y
for _ in range(80):
    Z = Z*Z + c
fase = np.angle(Z)*0.22 + np.log(np.abs(Z)+1)*tam
s = (fase*0.375) % 1.0
palette = np.array([hex_to_rgb(c) for c in colores_actuales], float)
pos = s*6.0
i0 = np.floor(pos).astype(int) % 6
f = pos - np.floor(pos)
f = 0.5*(1-np.cos(f*np.pi))
out = np.zeros((800,1000,3), float)
for k in range(6):
    m = i0==k
    nk = (k+1)%6
    out[m,0] = (1-f[m])*palette[k,0] + f[m]*palette[nk,0]
    out[m,1] = (1-f[m])*palette[k,1] + f[m]*palette[nk,1]
    out[m,2] = (1-f[m])*palette[k,2] + f[m]*palette[nk,2]
out = np.clip(out*brillo,0,255).astype(np.uint8)

# Transparencia base
magnitud = np.abs(Z)
brillo_pixel = out.mean(axis=2)
if fondo_transparente:
    alpha = np.where((magnitud < 4) & (brillo_pixel > (10 + umbral*10)), 255, 0).astype(np.uint8)
    out_rgba = np.dstack((out, alpha))
    img_base = Image.fromarray(out_rgba, "RGBA")
else:
    img_base = Image.fromarray(out, "RGB").convert("RGBA")

# --- NUEVO: INCRUSTAR ETIQUETA EN LA BASE DE LA IMAGEN ---
if incluir_etiqueta_en_imagen:
    W,H = img_base.size
    etiqueta_h = 55
    nueva = Image.new("RGBA", (W, H+etiqueta_h), (0,0,0,0) if fondo_transparente else (0,0,0,255))
    nueva.paste(img_base, (0,0))
    draw = ImageDraw.Draw(nueva)
    # fondo etiqueta negro
    draw.rectangle([(0,H),(W,H+etiqueta_h)], fill=(17,17,17,255))
    # linea de color
    try:
        rgb_c1 = hex_to_rgb(c1)
        draw.rectangle([(0,H),(8,H+etiqueta_h)], fill=tuple(rgb_c1)+(255,))
    except: pass
    texto = f"{nombre_cliente} | {firma} | JULIA SET - DENDRITE | C={cx:.4f}+{cy:.4f}i | {paleta_nombre}"
    # fuente por defecto
    draw.text((18, H+8), texto, fill=(255,255,255,255))
    draw.text((18, H+28), f"Zn+1 = Zn^2 + C | DIA {dia} | Escape-Time Fractal", fill=(170,170,170,255))
    img_final = nueva
else:
    img_final = img_base

st.image(img_final, use_container_width=True)

# Etiqueta visual en la web (igual que antes)
st.markdown(f"""
<div style="background:#111; padding:12px; border-radius:10px; border-left:5px solid {c1}">
<b style="color:white;">{nombre_cliente} | {firma}</b><br>
<span style="color:#AAA; font-family:monospace; font-size:12px;">
JULIA SET - DENDRITE | Fórmula: Z(n+1)=Z(n)²+C | C={cx:.4f}+{cy:.4f}i | DIA {dia} | Paleta: {paleta_nombre}
</span>
</div>
""", unsafe_allow_html=True)

buf = io.BytesIO()
img_final.save(buf, format="PNG")
st.sidebar.download_button("📥 Descargar PNG con etiqueta", buf.getvalue(), f"{nombre_cliente.replace(' ','_')}_JULIA.png", "image/png", type="primary")
