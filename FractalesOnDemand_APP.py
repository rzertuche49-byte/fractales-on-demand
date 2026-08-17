import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io, math

st.set_page_config(layout="wide", page_title="V99 STABLE")

def hex_to_rgb(h):
    h=h.lstrip('#')
    return [int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)]

def get_font_bold(size):
    try: return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except: return ImageFont.load_default()

def get_font_mono(size):
    try: return ImageFont.truetype("DejaVuSansMono-Bold.ttf", size)
    except: return ImageFont.load_default()

PALETAS = {"Tu captura": ["#00FFFF","#0064FF","#FF00C8","#FF6400","#FFFF00","#00FF64"]}
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
    nombre_cliente = st.text_input("Nombre", "ROBERTO ZERTUCHE")
    codigos = st.text_input("Codigos", "49/316/267")
    tipo_fractal = st.selectbox("TIPO DE FRACTAL", list(FRACTALES.keys()), 0)
    dia = st.slider("DIA", 1, 365, 283)
    zoom = st.slider("ZOOM", 0.2, 5.0, 0.88)
    tam = st.slider("Tamano mancha", 0.1, 3.0, 1.8)
    brillo = st.slider("Brillo", 0.5, 2.5, 1.4)
    fondo_transparente = st.checkbox("Fondo transparente", False)
    umbral = st.slider("Limpieza fondo", 0.0, 5.0, 1.0)
    incluir = st.checkbox("Incrustar etiqueta", True)
    st.divider()
    formato = st.selectbox("Formato impresion", ["Standard (1000x800)", "4K (3840x3072)", "8K (7680x6144)"], 0)
    calidad = st.slider("Calidad JPG", 80, 100, 95)

t=dia/365*2*math.pi
base_c=FRACTALES[tipo_fractal]["c"]
es_fijo=tipo_fractal in ("MANDELBROT","TRICORN","NEWTON")
cx,cy=(base_c.real,base_c.imag) if es_fijo else (base_c.real+0.005*math.cos(t*3), base_c.imag+0.005*math.sin(t*3))
c_var=complex(cx,cy)

W,H=1000,800
x=np.linspace(-1.5/zoom,1.5/zoom,W)
y=np.linspace(-1.0/zoom,1.0/zoom,H)
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
palette=np.array([[0,255,255],[0,100,255],[255,0,200],[255,100,0],[255,255,0],[0,255,100]],float)
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

formula=FRACTALES[tipo_fractal]["formula"]
texto1=f"{nombre_cliente} {codigos}" if codigos else nombre_cliente
texto2=f"{tipo_fractal} | C={cx:.4f}+{cy:.4f}i | {formula}"

if incluir:
    img_final=img_base.copy(); Wf,Hf=img_final.size; draw=ImageDraw.Draw(img_final)
    es_oscuro=out[Hf-80:Hf,:].mean()<100
    color=(255,255,255,255) if es_oscuro else (0,0,0,255)
    font1=get_font_bold(36); font2=get_font_mono(26)
    draw.text((24,Hf-50), texto1, fill=color, font=font1)
    draw.text((24,Hf-22), texto2, fill=color, font=font2)
else:
    img_final=img_base

st.image(img_final, width=1000)

st.markdown(f"""
<div style="background:white;padding:14px 20px;border-radius:12px;border:1px solid #E0E0E0;line-height:1.1;">
<b style="color:black;font-size:22px;font-family:Arial;font-weight:800;">{texto1}</b><br>
<div style="height:4px;"></div>
<span style="color:black;font-family:monospace;font-size:17px;">{texto2}</span>
</div>
""", unsafe_allow_html=True)

# EXPORT
if "8K" in formato: W2,H2=7680,6144
elif "4K" in formato: W2,H2=3840,3072
else: W2,H2=1000,800

if W2==1000:
    img_exp=img_final
else:
    img_exp=img_final.resize((W2,H2), Image.LANCZOS)

buf1=io.BytesIO(); img_exp.save(buf1, format="PNG")
st.sidebar.download_button("PNG", buf1.getvalue(), f"{nombre_cliente}_{W2}x{H2}.png", "image/png", key="png1")

buf2=io.BytesIO(); img_exp.convert("RGB").save(buf2, format="JPEG", quality=calidad)
st.sidebar.download_button("JPG", buf2.getvalue(), f"{nombre_cliente}_{W2}x{H2}.jpg", "image/jpeg", key="jpg1")

buf3=io.BytesIO(); img_exp.convert("RGB").save(buf3, format="PDF", resolution=300.0)
st.sidebar.download_button("PDF 300dpi", buf3.getvalue(), f"{nombre_cliente}_{W2}x{H2}.pdf", "application/pdf", key="pdf1")
