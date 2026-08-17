import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io, math

st.set_page_config(layout="wide", page_title="Fractales V103 ESTABLE")

# --- CACHE PARA QUE NO SE RE-RENDERICE Y TUMBE LA APP ---
@st.cache_data
def hex_to_rgb(h):
    h=h.lstrip('#')
    return [int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)]

@st.cache_data
def render_fractal_cache(W,H,zoom,cx,cy,tipo,tam,brillo,colores_tuple,bg_tuple,umbral):
    colores_rgb=[hex_to_rgb(c) for c in colores_tuple]
    palette=np.array(colores_rgb,float)
    x=np.linspace(-1.5/zoom,1.5/zoom,W)
    y=np.linspace(-1.0/zoom,1.0/zoom,H)
    X,Y=np.meshgrid(x,y)
    Z=X+1j*Y
    c_var=complex(cx,cy)
    # 40 iteraciones max para preview, no 60
    for _ in range(40):
        Z=Z*Z+c_var
    s=(np.angle(Z)*0.22+np.log(np.abs(Z)+1)*tam)*0.375 % 1.0
    pos=s*6.0; i0=np.floor(pos).astype(int)%6; f=pos-np.floor(pos); f=0.5*(1-np.cos(f*np.pi))
    out=np.zeros((H,W,3),float)
    for k in range(6):
        m=i0==k; nk=(k+1)%6
        out[m,0]=(1-f[m])*palette[k,0]+f[m]*palette[nk,0]
        out[m,1]=(1-f[m])*palette[k,1]+f[m]*palette[nk,1]
        out[m,2]=(1-f[m])*palette[k,2]+f[m]*palette[nk,2]
    out=np.clip(out*brillo,0,255)
    mag=np.abs(Z)
    mask=mag<4
    if bg_tuple!=(0,0,0) or True:
        out_bg=out.copy()
        out_bg[~mask]=bg_tuple
        img=Image.fromarray(out_bg.astype(np.uint8),"RGB")
    else:
        img=Image.fromarray(out.astype(np.uint8),"RGB")
    return img

def get_font(size):
    size=int(max(size,10))
    try:
        from matplotlib import font_manager
        fp=font_manager.findfont("DejaVu Sans", fallback_to_default=True)
        return ImageFont.truetype(fp, size)
    except:
        return ImageFont.load_default()

def add_label(img, t1, t2):
    W,H=img.size; lh=int(H*0.14)
    nueva=Image.new("RGB",(W,H+lh),(255,255,255))
    nueva.paste(img,(0,0))
    draw=ImageDraw.Draw(nueva)
    f1=get_font(int(W*0.016)); f2=get_font(int(W*0.010))
    draw.text((int(W*0.02),H+int(lh*0.15)),t1,fill=(0,0,0),font=f1)
    draw.text((int(W*0.02),H+int(lh*0.55)),t2,fill=(0,0,0),font=f2)
    return nueva

FRACTALES={"HORSESHOE":complex(-0.74543,0.11301),"RABBIT":complex(-0.123,0.745),"FEATHER":complex(-0.8,0.156)}
PALETAS={"Tu captura":["#00FFFF","#0064FF","#FF00C8","#FF6400","#FFFF00","#00FF64"]}

with st.sidebar:
    st.title("Fractales V103 ESTABLE")
    nombre=st.text_input("Cliente","ROBERTO ZERTUCHE")
    codigos=st.text_input("Codigos","49/316/267")
    tipo=st.selectbox("Fractal",list(FRACTALES.keys()),0)
    dia=st.slider("DIA",1,365,49)
    zoom=st.slider("ZOOM",0.2,5.0,1.0)
    base=PALETAS["Tu captura"]
    c1=st.color_picker("C1",base[0]); c2=st.color_picker("C2",base[1]); c3=st.color_picker("C3",base[2])
    c4=st.color_picker("C4",base[3]); c5=st.color_picker("C5",base[4]); c6=st.color_picker("C6",base[5])
    colores_actuales=(c1,c2,c3,c4,c5,c6)
    tam=st.slider("Tamano",0.1,3.0,1.8); brillo=st.slider("Brillo",0.5,2.5,1.4)
    bg=st.selectbox("Fondo",["Negro","Blanco"],0)
    bg_tuple=(0,0,0) if bg=="Negro" else (255,255,255)

# Calculo C
t=dia/365*2*math.pi
base_c=FRACTALES[tipo]
cx=base_c.real+0.005*math.cos(t*3)
cy=base_c.imag+0.005*math.sin(t*3)

# RENDER ULTRA LIGERO 640x480 PARA QUE ABRA
W,H=640,480
img_preview=render_fractal_cache(W,H,zoom,cx,cy,tipo,tam,brillo,colores_actuales,bg_tuple,1.0)

texto1=f"{nombre} {codigos}" if codigos else nombre
texto2=f"{tipo} | C={cx:.4f}+{cy:.4f}i"

st.image(img_preview, width=640)
img_final=add_label(img_preview, texto1, texto2)
st.markdown(f"<div style='background:white;padding:8px;border:1px solid #ddd'><b>{texto1}</b><br><span style='font-size:10px'>{texto2}</span></div>", unsafe_allow_html=True)

with st.sidebar:
    buf=io.BytesIO(); img_final.save(buf,format="PNG")
    st.download_button("⬇️ PNG 640 con etiqueta mitad", buf.getvalue(), f"{nombre}_640.png","image/png")
    st.divider()
    if st.button("Generar 8K REAL (solo cuando lo necesites)"):
        with st.spinner("Generando 8K... 20 seg"):
            img_8k=render_fractal_cache(3840,3072,zoom,cx,cy,tipo,tam,brillo,colores_actuales,bg_tuple,1.0)
            img_8k_label=add_label(img_8k,texto1,texto2)
            buf8=io.BytesIO(); img_8k_label.save(buf8,format="PNG")
            st.download_button("⬇️ PNG 8K REAL", buf8.getvalue(), f"{nombre}_8K.png","image/png", key="8k")

st.divider()
st.subheader("Animacion 365 dias - FUERA DE LA NUBE")
st.info("El Oh, no. sale porque Streamlit Cloud corta a los 60s. El 365 NO se puede generar ahi. Genera el GIF en tu PC:")
st.code(f"""
# pip install pillow numpy
# python genera_365.py
import numpy as np
from PIL import Image
import math

W,H=400,300
zoom={zoom}
tam={tam}
brillo={brillo}
colores={list(colores_actuales)}
bg={bg_tuple}

def hex_to_rgb(h):
    h=h.lstrip('#')
    return [int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)]

palette=np.array([hex_to_rgb(c) for c in colores],float)
frames=[]

for dia in range(1,366):
    t=dia/365*2*math.pi
    cx={FRACTALES[tipo].real}+0.005*math.cos(t*3)
    cy={FRACTALES[tipo].imag}+0.005*math.sin(t*3)
    c_var=complex(cx,cy)
    x=np.linspace(-1.5/zoom,1.5/zoom,W)
    y=np.linspace(-1.0/zoom,1.0/zoom,H)
    X,Y=np.meshgrid(x,y)
    Z=X+1j*Y
    for _ in range(30):
        Z=Z*Z+c_var
    s=(np.angle(Z)*0.22+np.log(np.abs(Z)+1)*tam)*0.375 % 1.0
    pos=s*6.0
    i0=np.floor(pos).astype(int)%6
    f=pos-np.floor(pos)
    f=0.5*(1-np.cos(f*np.pi))
    out=np.zeros((H,W,3),float)
    for k in range(6):
        m=i0==k
        nk=(k+1)%6
        out[m,0]=(1-f[m])*palette[k,0]+f[m]*palette[nk,0]
        out[m,1]=(1-f[m])*palette[k,1]+f[m]*palette[nk,1]
        out[m,2]=(1-f[m])*palette[k,2]+f[m]*palette[nk,2]
    out=np.clip(out*brillo,0,255)
    out[np.abs(Z)>=4]=bg
    frames.append(Image.fromarray(out.astype(np.uint8),"RGB"))
    print(f"{{dia}}/365")

frames[0].save("{nombre}_365DIAS.gif", save_all=True, append_images=frames[1:], duration=80, loop=0, optimize=True)
""", language="python")

