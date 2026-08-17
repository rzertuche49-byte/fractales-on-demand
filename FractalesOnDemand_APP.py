import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io, math

st.set_page_config(layout="wide", page_title="V99.2")

def hex_to_rgb(h):
    h=h.lstrip('#')
    return [int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)]

def get_font_bold(size):
    try: return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except: return ImageFont.load_default()

def get_font_mono(size):
    try: return ImageFont.truetype("DejaVuSansMono-Bold.ttf", size)
    except: return ImageFont.load_default()

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
    "Psicodelico": ["#FF00FF","#00FFFF","#FFFF00","#FF0000","#00FF00","#0000FF"],
    "Elegante": ["#000000","#1A1A1A","#D4AF37","#F5F5DC","#8B7355","#FFFFFF"],
}
FRACTALES = {
    "DENDRITE": {"c": complex(-0.745, 0.11), "formula": "Zn+1=Zn2+C"},
    "RABBIT": {"c": complex(-0.123, 0.745), "formula": "Zn+1=Zn2+C"},
    "SPIRAL": {"c": complex(-0.77568377, 0.13646737), "formula": "Zn+1=Zn2+C"},
    "SIEGEL DISK": {"c": complex(-0.391, -0.587), "formula": "Zn+1=Zn2+C"},
    "BURNING SHIP JULIA": {"c": complex(-0.5, -0.5), "formula": "Zn+1=(|Re|+i|Im|)2+C"},
    "FEATHER": {"c": complex(-0.8, 0.156), "formula": "Zn+1=Zn2+C"},
    "MANDELBROT": {"c": complex(0,0), "formula": "Zn+1=Zn2+C"},
    "TRICORN": {"c": complex(0,0), "formula": "Zn+1=conj(Zn)2+C"},
    "NEWTON": {"c": complex(0,0), "formula": "Zn+1=Zn-(Zn3-1)/3Zn2"},
}

with st.sidebar:
    nombre_cliente = st.text_input("Nombre del cliente / proyecto", "ROBERTO ZERTUCHE")
    codigos = st.text_input("Codigos", "49/316/267")
    st.divider()
    tipo_fractal = st.selectbox("TIPO DE FRACTAL", list(FRACTALES.keys()), 1)
    dia = st.slider("DIA", 1, 365, 49)
    zoom = st.slider("ZOOM", 0.2, 5.0, 1.0)
    paleta_nombre = st.selectbox("PALETA", list(PALETAS.keys()), 0)
    base = PALETAS[paleta_nombre]
    st.write("**EDITA 6 COLORES**")
    c1=st.color_picker("C1", base[0], key="c1"); c2=st.color_picker("C2", base[1], key="c2"); c3=st.color_picker("C3", base[2], key="c3")
    c4=st.color_picker("C4", base[3], key="c4"); c5=st.color_picker("C5", base[4], key="c5"); c6=st.color_picker("C6", base[5], key="c6")
    colores_actuales=[c1,c2,c3,c4,c5,c6]
    st.write("---")
    tam = st.slider("Tamano mancha", 0.1, 3.0, 1.8)
    brillo = st.slider("Brillo", 0.5, 2.5, 1.4)
    st.divider()
    fondo_transparente = st.checkbox("Fondo transparente", False)
    umbral = st.slider("Limpieza fondo", 0.0, 5.0, 1.0)
    incluir = st.checkbox("Incrustar etiqueta en imagen", True)
    calidad = st.slider("Calidad JPG", 80, 100, 95)
    st.divider()
    st.write("**GUARDAR**")

t=dia/365*2*math.pi
base_c=FRACTALES[tipo_fractal]["c"]
es_fijo=tipo_fractal in ("MANDELBROT","TRICORN","NEWTON")
cx,cy=(base_c.real,base_c.imag) if es_fijo else (base_c.real+0.005*math.cos(t*3), base_c.imag+0.005*math.sin(t*3))
c_var=complex(cx,cy)

W,H=1000,800
x=np.linspace(-1.5/zoom,1.5/zoom,W); y=np.linspace(-1.0/zoom,1.0/zoom,H)
X,Y=np.meshgrid(x,y)

if tipo_fractal=="MANDELBROT":
    C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
    for _ in range(60): Z=Z*Z+C
elif tipo_fractal=="TRICORN":
    C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
    for _ in range(60): Z=np.conj(Z)**2+C
elif tipo_fractal=="NEWTON":
    Z=X+1j*Y
    for _ in range(20):
        Z2=Z*Z; Z3=Z2*Z; d=np.where(np.abs(3*Z2)<1e-6,1e-6,3*Z2); Z=Z-(Z3-1)/d
else:
    Z=X+1j*Y
    if tipo_fractal=="BURNING SHIP JULIA":
        for _ in range(60): Z=(np.abs(Z.real)+1j*np.abs(Z.imag))**2+c_var
    else:
        for _ in range(60): Z=Z*Z+c_var

s=(np.angle(Z)+np.pi)/(2*np.pi) if tipo_fractal=="NEWTON" else (np.angle(Z)*0.22+np.log(np.abs(Z)+1)*tam)*0.375 % 1.0
palette=np.array([hex_to_rgb(c) for c in colores_actuales],float)
pos=s*6.0; i0=np.floor(pos).astype(int)%6; f=pos-np.floor(pos); f=0.5*(1-np.cos(f*np.pi))
out=np.zeros((H,W,3),float)
for k in range(6):
    m=i0==k; nk=(k+1)%6
    out[m,0]=(1-f[m])*palette[k,0]+f[m]*palette[nk,0]
    out[m,1]=(1-f[m])*palette[k,1]+f[m]*palette[nk,1]
    out[m,2]=(1-f[m])*palette[k,2]+f[m]*palette[nk,2]
out=np.clip(out*brillo,0,255).astype(np.uint8)

magnitud=np.abs(Z); brillo_pixel=out.mean(axis=2)
if fondo_transparente:
    alpha=np.where(brillo_pixel>(10+umbral*10),255,0).astype(np.uint8) if tipo_fractal=="NEWTON" else np.where((magnitud<4)&(brillo_pixel>(10+umbral*10)),255,0).astype(np.uint8)
    img_base=Image.fromarray(np.dstack((out,alpha)),"RGBA")
else:
    img_base=Image.fromarray(out,"RGB").convert("RGBA")

texto1=f"{nombre_cliente} {codigos}" if codigos.strip()!="" else nombre_cliente
texto2=f"{tipo_fractal} | C={cx:.4f}+{cy:.4f}i | {FRACTALES[tipo_fractal]['formula']}"

if incluir:
    img_final=img_base.copy(); draw=ImageDraw.Draw(img_final)
    es_oscuro=out[720:800,:].mean()<100
    color=(255,255,255,255) if es_oscuro else (0,0,0,255)
    font1=get_font_bold(36); font2=get_font_mono(26)
    draw.text((24,H-50), texto1, fill=color, font=font1)
    draw.text((24,H-22), texto2, fill=color, font=font2)
else:
    img_final=img_base

st.image(img_final, width=1000)
st.markdown(f"""
<div style="background:white;padding:14px 20px;border-radius:12px;border:1px solid #E0E0E0;line-height:1.1;">
<b style="color:black;font-size:22px;">{texto1}</b><br><div style="height:4px;"></div>
<span style="color:black;font-family:monospace;font-size:17px;">{texto2}</span>
</div>
""", unsafe_allow_html=True)

# --- EXPORTACION DIRECTA SIN SELECTOR ---
def get_export(w,h):
    return img_final if (w==1000 and h==800) else img_final.resize((w,h), Image.LANCZOS)

# PNG
with st.sidebar:
    st.write("PNG")
    for w,h,label in [(1000,800,"Standard"), (3840,3072,"4K"), (7680,6144,"8K")]:
        img_e=get_export(w,h)
        buf=io.BytesIO(); img_e.save(buf, format="PNG")
        st.download_button(f"PNG {label} ({w}x{h})", buf.getvalue(), f"{nombre_cliente}_{label}_{w}x{h}.png", "image/png", key=f"png_{label}")

    st.write("JPG")
    for w,h,label in [(1000,800,"Standard"), (3840,3072,"4K"), (7680,6144,"8K")]:
        img_e=get_export(w,h).convert("RGB")
        buf=io.BytesIO(); img_e.save(buf, format="JPEG", quality=calidad)
        st.download_button(f"JPG {label} ({w}x{h})", buf.getvalue(), f"{nombre_cliente}_{label}_{w}x{h}.jpg", "image/jpeg", key=f"jpg_{label}")

    st.write("PDF 300dpi")
    for w,h,label in [(1000,800,"Standard"), (3840,3072,"4K"), (7680,6144,"8K")]:
        img_e=get_export(w,h).convert("RGB")
        buf=io.BytesIO(); img_e.save(buf, format="PDF", resolution=300.0)
        st.download_button(f"PDF {label} ({w}x{h})", buf.getvalue(), f"{nombre_cliente}_{label}_{w}x{h}.pdf", "application/pdf", key=f"pdf_{label}")
