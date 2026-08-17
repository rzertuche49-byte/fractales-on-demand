import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io, math

st.set_page_config(layout="wide", page_title="V98.2 - FIX")

def hex_to_rgb(h):
    h = h.lstrip('#')
    return [int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)]

def get_font_bold(size):
    try: return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except: return ImageFont.load_default()

def get_font_mono(size):
    try: return ImageFont.truetype("DejaVuSansMono-Bold.ttf", size)
    except:
        try: return ImageFont.truetype("DejaVuSansMono.ttf", size)
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

@st.cache_data(show_spinner=False)
def render_fractal_cached(W, H, tipo_fractal, cx, cy, tam, brillo, palette_tuple, fondo_transparente, umbral, zoom):
    c_var = complex(cx, cy)
    x = np.linspace(-1.5/zoom, 1.5/zoom, W)
    y = np.linspace(-1.0/zoom, 1.0/zoom, H)
    X,Y = np.meshgrid(x,y)
    if tipo_fractal == "MANDELBROT":
        C = (X-0.5) + 1j*Y; Z = np.zeros_like(C)
        for _ in range(80): Z = Z*Z + C
    elif tipo_fractal == "TRICORN":
        C = (X-0.5) + 1j*Y; Z = np.zeros_like(C)
        for _ in range(80): Z = np.conj(Z)**2 + C
    elif tipo_fractal == "NEWTON":
        Z = X + 1j*Y
        for _ in range(30):
            Z2=Z*Z; Z3=Z2*Z; d=np.where(np.abs(3*Z2)<1e-6,1e-6,3*Z2); Z=Z-(Z3-1)/d
    else:
        Z=X+1j*Y
        if tipo_fractal=="BURNING SHIP JULIA":
            for _ in range(80): Z=(np.abs(Z.real)+1j*np.abs(Z.imag))**2 + c_var
        else:
            for _ in range(80): Z=Z*Z + c_var
    s=(np.angle(Z)+np.pi)/(2*np.pi) if tipo_fractal=="NEWTON" else (np.angle(Z)*0.22+np.log(np.abs(Z)+1)*tam)*0.375 % 1.0
    palette=np.array([hex_to_rgb(c) for c in palette_tuple],float)
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
        if tipo_fractal=="NEWTON": alpha=np.where(brillo_pixel>(10+umbral*10),255,0).astype(np.uint8)
        else: alpha=np.where((magnitud<4)&(brillo_pixel>(10+umbral*10)),255,0).astype(np.uint8)
        img_base=Image.fromarray(np.dstack((out,alpha)),"RGBA")
    else: img_base=Image.fromarray(out,"RGB").convert("RGBA")
    return img_base, out

with st.sidebar:
    nombre_cliente = st.text_input("Nombre del cliente / proyecto", "ROBERTO ZERTUCHE")
    codigos = st.text_input("Códigos", "49/316/267")
    st.divider()
    tipo_fractal = st.selectbox("TIPO DE FRACTAL", list(FRACTALES.keys()), index=0)
    dia = st.slider("DIA", 1, 365, 283)
    zoom = st.slider("ZOOM", 0.2, 5.0, 0.88)
    paleta_nombre = st.selectbox("PALETA", list(PALETAS.keys()), index=0)
    base = PALETAS[paleta_nombre]
    st.write("**EDITA 6 COLORES**")
    c1 = st.color_picker("C1", base[0]); c2 = st.color_picker("C2", base[1]); c3 = st.color_picker("C3", base[2])
    c4 = st.color_picker("C4", base[3]); c5 = st.color_picker("C5", base[4]); c6 = st.color_picker("C6", base[5])
    colores_actuales = [c1,c2,c3,c4,c5,c6]
    st.write("---")
    tam = st.slider("Tamano mancha", 0.1, 3.0, 1.8)
    brillo = st.slider("Brillo", 0.5, 2.5, 1.4)
    st.divider()
    fondo_transparente = st.checkbox("Fondo transparente", value=False)
    umbral = st.slider("Limpieza fondo", 0.0, 5.0, 1.0)
    incluir_etiqueta_en_imagen = st.checkbox("Incrustar etiqueta en imagen", value=True)
    st.divider()
    formato = st.selectbox("Formato de impresion", ["Standard (1000x800)", "4K (3840x3072)", "8K (7680x6144)"], index=0)
    calidad_jpg = st.slider("Calidad JPG", 80, 100, 95)

st.title(nombre_cliente)
t = dia/365*2*math.pi
base_c = FRACTALES[tipo_fractal]["c"]
es_fijo = tipo_fractal in ("MANDELBROT", "TRICORN", "NEWTON")
if es_fijo: cx, cy = base_c.real, base_c.imag
else: cx, cy = base_c.real + 0.005*math.cos(t*3), base_c.imag + 0.005*math.sin(t*3)

# Preview rapido 1000x800
img_base_preview, out_preview = render_fractal_cached(1000, 800, tipo_fractal, cx, cy, tam, brillo, tuple(colores_actuales), fondo_transparente, umbral, zoom)

formula_txt=FRACTALES[tipo_fractal]["formula"]
SEP_GRANDE = " | "
SEP_NOMBRE = " "

if codigos.strip()!="":
    texto_linea1 = f"{nombre_cliente}{SEP_NOMBRE}{codigos}"
else:
    texto_linea1 = f"{nombre_cliente}"
texto_linea2 = f"{tipo_fractal}{SEP_GRANDE}C={cx:.4f}+{cy:.4f}i{SEP_GRANDE}{formula_txt}"

def add_labels(img_base, out):
    if incluir_etiqueta_en_imagen:
        img_final=img_base.copy(); W,H=img_final.size; draw=ImageDraw.Draw(img_final)
        muestra_inf=out[H-80:H,:].mean() if H>=80 else out.mean()
        es_oscuro=muestra_inf<100
        color_texto=(255,255,255,255) if es_oscuro else (0,0,0,255)
        scale = W/1000
        font1=get_font_bold(int(36*scale)); font2=get_font_mono(int(26*scale))
        x0=int(24*scale); y1=H-int(50*scale); y2=H-int(22*scale)
        draw.text((x0,y1),texto_linea1,fill=color_texto,font=font1)
        draw.text((x0,y2),texto_linea2,fill=color_texto,font=font2)
        return img_final
    else:
        return img_base

img_final_preview = add_labels(img_base_preview, out_preview)
st.image(img_final_preview, width=1000)

st.markdown(f"""
<div style="background:white; padding:14px 20px; border-radius:12px; border:1px solid #E0E0E0; line-height:1.1;">
<b style="color:black; font-size:22px; font-family:DejaVu Sans, Arial, sans-serif; font-weight:800;">{texto_linea1}</b><br>
<div style="height:4px;"></div>
<span style="color:black; font-family:DejaVu Sans Mono, monospace; font-size:17px;">{texto_linea2}</span>
</div>
""", unsafe_allow_html=True)

# --- EXPORTACION CON KEYS UNICAS (FIX removeChild) ---
st.sidebar.divider()
st.sidebar.write(f"**Descargar {formato}**")

if "8K" in formato: W_exp, H_exp = 7680, 6144
elif "4K" in formato: W_exp, H_exp = 3840, 3072
else: W_exp, H_exp = 1000, 800

# Solo genera alta resolucion cuando se pide descargar
with st.sidebar:
    if st.button(f"Generar {formato} para descargar", key="btn_gen"):
        st.session_state["gen_high"] = True

if st.session_state.get("gen_high", False):
    with st.spinner(f"Generando {formato}..."):
        img_base_high, out_high = render_fractal_cached(W_exp, H_exp, tipo_fractal, cx, cy, tam, brillo, tuple(colores_actuales), fondo_transparente, umbral, zoom)
        img_export = add_labels(img_base_high, out_high)

        buf_png = io.BytesIO(); img_export.save(buf_png, format="PNG")
        st.download_button(f"📥 PNG {formato}", buf_png.getvalue(), f"{nombre_cliente.replace(' ','_')}_{tipo_fractal}_{W_exp}x{H_exp}.png", "image/png", key="dl_png", type="primary")

        img_jpg = img_export.convert("RGB") if img_export.mode=="RGBA" else img_export
        buf_jpg = io.BytesIO(); img_jpg.save(buf_jpg, format="JPEG", quality=calidad_jpg)
        st.download_button(f"📥 JPG {formato}", buf_jpg.getvalue(), f"{nombre_cliente.replace(' ','_')}_{tipo_fractal}_{W_exp}x{H_exp}.jpg", "image/jpeg", key="dl_jpg")

        buf_pdf = io.BytesIO()
        img_rgb = img_export.convert("RGB")
        img_rgb.save(buf_pdf, format="PDF", resolution=300.0)
        st.download_button(f"📥 PDF {formato} 300dpi", buf_pdf.getvalue(), f"{nombre_cliente.replace(' ','_')}_{tipo_fractal}_{W_exp}x{H_exp}.pdf", "application/pdf", key="dl_pdf")
else:
    # Descargas en standard sin generar 4K pesado
    buf_png = io.BytesIO(); img_final_preview.save(buf_png, format="PNG")
    st.sidebar.download_button("📥 PNG Standard", buf_png.getvalue(), f"{nombre_cliente.replace(' ','_')}_{tipo_fractal}_1000x800.png", "image/png", key="dl_png_std")
