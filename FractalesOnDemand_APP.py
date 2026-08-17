import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io, math

st.set_page_config(layout="wide", page_title="Fractales V102.3 MODO SEGURO")

def hex_to_rgb(h):
    h=h.lstrip('#')
    return [int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)]

def get_font(size, bold=True):
    size=int(max(size,10))
    try:
        from matplotlib import font_manager
        fp=font_manager.findfont("DejaVu Sans" if bold else "DejaVu Sans Mono", fallback_to_default=True)
        return ImageFont.truetype(fp, size)
    except: return ImageFont.load_default()

def crear_imagen_con_etiqueta_abajo(img_base, texto1, texto2):
    W,H=img_base.size; label_h=int(H*0.14)
    nueva=Image.new("RGB",(W,H+label_h),(255,255,255))
    if img_base.mode=="RGBA": nueva.paste(img_base,(0,0),img_base)
    else: nueva.paste(img_base,(0,0))
    draw=ImageDraw.Draw(nueva); f1=int(W*0.016); f2=int(W*0.010)
    font1=get_font(f1,True); font2=get_font(f2,False)
    draw.text((int(W*0.02),H+int(label_h*0.15)),texto1,fill=(0,0,0),font=font1)
    try: bbox=draw.textbbox((0,0),texto1,font=font1); h1=bbox[3]-bbox[1]
    except: h1=f1
    draw.text((int(W*0.02),H+int(label_h*0.15)+h1+int(label_h*0.08)),texto2,fill=(0,0,0),font=font2)
    return nueva

def render_block(Wc,Hc,X,Y,c_var,tipo,it=60):
    if tipo=="MANDELBROT": C=(X-0.5)+1j*Y; Z=np.zeros_like(C);
    else:
        if tipo=="TRICORN": C=(X-0.5)+1j*Y; Z=np.zeros_like(C);
        else: Z=X+1j*Y; C=(X-0.5)+1j*Y if tipo in ("MANDELBROT","TRICORN","BURNING SHIP MANDELBROT","BUFFALO","CELTIC","MULTIBROT 3","MULTIBROT 4") else None
    if tipo=="MANDELBROT":
        for _ in range(it): Z=Z*Z+C
        return Z
    if tipo=="TRICORN":
        for _ in range(it): Z=np.conj(Z)**2+C
        return Z
    if tipo=="BURNING SHIP MANDELBROT": C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
    if tipo=="BURNING SHIP MANDELBROT":
        for _ in range(it): Z=(np.abs(Z.real)+1j*np.abs(Z.imag))**2+C
        return Z
    if tipo=="BUFFALO": C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
    if tipo=="BUFFALO":
        for _ in range(it): ZR=np.abs(Z.real); ZI=np.abs(Z.imag); Z=(ZR*ZR-ZI*ZI)+2*ZR*ZI*1j+C
        return Z
    if tipo=="CELTIC": C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
    if tipo=="CELTIC":
        for _ in range(it): Z2=Z*Z; Z=np.abs(Z2.real)+1j*Z2.imag+C
        return Z
    if tipo=="MULTIBROT 3": C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
    if tipo=="MULTIBROT 3":
        for _ in range(it): Z=Z**3+C
        return Z
    if tipo=="MULTIBROT 4": C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
    if tipo=="MULTIBROT 4":
        for _ in range(it): Z=Z**4+C
        return Z
    if tipo=="NEWTON": Z=X+1j*Y
    if tipo=="NEWTON":
        for _ in range(20): Z2=Z*Z; Z3=Z2*Z; d=np.where(np.abs(3*Z2)<1e-6,1e-6,3*Z2); Z=Z-(Z3-1)/d
        return Z
    if tipo=="NOVA": Z=X+1j*Y
    if tipo=="NOVA":
        for _ in range(40): Z2=Z*Z; Z3=Z2*Z; d=np.where(np.abs(3*Z2)<1e-6,1e-6,3*Z2); Z=Z-(Z3-1)/d+c_var
        return Z
    Z=X+1j*Y
    if tipo=="BURNING SHIP JULIA":
        for _ in range(it): Z=(np.abs(Z.real)+1j*np.abs(Z.imag))**2+c_var
    else:
        for _ in range(it): Z=Z*Z+c_var
    return Z

PALETAS={"Tu captura":["#00FFFF","#0064FF","#FF00C8","#FF6400","#FFFF00","#00FF64"],"Neon 80s":["#00FFFF","#FF00FF","#FFFF00","#00FF00","#FF0066","#6600FF"]}
FRACTALES={"HORSESHOE":{"c":complex(-0.74543,0.11301),"formula":"Zn+1=Zn2+C"},"RABBIT":{"c":complex(-0.123,0.745),"formula":"Zn+1=Zn2+C"},"FEATHER":{"c":complex(-0.8,0.156),"formula":"Zn+1=Zn2+C"},"MANDELBROT":{"c":complex(0,0),"formula":"Zn+1=Zn2+C"}}

with st.sidebar:
    nombre_cliente=st.text_input("Nombre cliente", "ROBERTO ZERTUCHE")
    codigos=st.text_input("Codigos","49/316/267")
    tipo_fractal=st.selectbox("TIPO FRACTAL", list(FRACTALES.keys()),0)
    dia=st.slider("DIA",1,365,49); zoom=st.slider("ZOOM",0.2,5.0,1.0)
    paleta_nombre=st.selectbox("PALETA", list(PALETAS.keys()),0); base=PALETAS[paleta_nombre]
    c1=st.color_picker("C1",base[0]); c2=st.color_picker("C2",base[1]); c3=st.color_picker("C3",base[2]); c4=st.color_picker("C4",base[3]); c5=st.color_picker("C5",base[4]); c6=st.color_picker("C6",base[5])
    colores_actuales=[c1,c2,c3,c4,c5,c6]
    tam=st.slider("Tamano",0.1,3.0,1.8); brillo=st.slider("Brillo",0.5,2.5,1.4)
    fondo_mode=st.selectbox("FONDO",["Negro","Blanco","Transparente"],0)
    umbral=st.slider("Limpieza",0.0,5.0,1.0)
    presentar_etiqueta=st.checkbox("Etiqueta",True)
    st.divider(); st.subheader("ANIMACION SEGURA")
    anim_tipo=st.selectbox("Tipo", ["Crecimiento 12 frames - SI funciona en nube","365 dias - Generar LOCAL en tu PC"],0)

if fondo_mode=="Negro": bg_rgb=[0,0,0]
else: bg_rgb=[255,255,255] if fondo_mode=="Blanco" else [0,0,0]

t=dia/365*2*math.pi; base_c=FRACTALES[tipo_fractal]["c"]
if tipo_fractal in ("MANDELBROT",): cx=base_c.real; cy=base_c.imag
else: cx=base_c.real+0.005*math.cos(t*3); cy=base_c.imag+0.005*math.sin(t*3)
c_var=complex(cx,cy)

W,H=800,600
x=np.linspace(-1.5/zoom,1.5/zoom,W); y=np.linspace(-1.0/zoom,1.0/zoom,H); X,Y=np.meshgrid(x,y)
Z=render_block(W,H,X,Y,c_var,tipo_fractal,60)
s=(np.angle(Z)*0.22+np.log(np.abs(Z)+1)*tam)*0.375 % 1.0
palette=np.array([hex_to_rgb(c) for c in colores_actuales],float)
pos=s*6.0; i0=np.floor(pos).astype(int)%6; f=pos-np.floor(pos); f=0.5*(1-np.cos(f*np.pi))
out=np.zeros((H,W,3),float)
for k in range(6):
    m=i0==k; nk=(k+1)%6
    out[m,0]=(1-f[m])*palette[k,0]+f[m]*palette[nk,0]; out[m,1]=(1-f[m])*palette[k,1]+f[m]*palette[nk,1]; out[m,2]=(1-f[m])*palette[k,2]+f[m]*palette[nk,2]
out=np.clip(out*brillo,0,255); mag=np.abs(Z)
mask=mag<4
if fondo_mode!="Transparente": out[~mask]=bg_rgb
img_base=Image.fromarray(out.astype(np.uint8),"RGB").convert("RGBA")
texto1=f"{nombre_cliente} {codigos}" if codigos else nombre_cliente
texto2=f"{tipo_fractal} | C={cx:.4f}+{cy:.4f}i"
st.image(img_base,width=800)
if presentar_etiqueta:
    img_export=crear_imagen_con_etiqueta_abajo(img_base,texto1,texto2)
else: img_export=img_base

with st.sidebar:
    buf=io.BytesIO(); img_export.save(buf,format="PNG")
    st.download_button("PNG Standard",buf.getvalue(),f"{nombre_cliente}_STD.png","image/png")

st.divider()
if "Crecimiento" in anim_tipo:
    st.subheader("Animacion segura 12 frames - SI funciona en Streamlit Cloud")
    if st.button("Generar 12 frames"):
        frames=[]; palette_anim=np.array([hex_to_rgb(c) for c in colores_actuales],float)
        it_steps=np.linspace(2,60,12,dtype=int)
        prog=st.progress(0)
        for idx,it in enumerate(it_steps):
            Xg,Yg=np.meshgrid(np.linspace(-1.5/zoom,1.5/zoom,320), np.linspace(-1.0/zoom,1.0/zoom,240))
            Zg=Xg+1j*Yg
            for _ in range(int(it)): Zg=Zg*Zg+c_var
            s=(np.angle(Zg)*0.22+np.log(np.abs(Zg)+1)*tam)*0.375 % 1.0
            pos=s*6.0; i0=np.floor(pos).astype(int)%6; f=pos-np.floor(pos); f=0.5*(1-np.cos(f*np.pi))
            out=np.zeros((240,320,3),float)
            for k in range(6):
                m=i0==k; nk=(k+1)%6
                out[m,0]=(1-f[m])*palette_anim[k,0]+f[m]*palette_anim[nk,0]; out[m,1]=(1-f[m])*palette_anim[k,1]+f[m]*palette_anim[nk,1]; out[m,2]=(1-f[m])*palette_anim[k,2]+f[m]*palette_anim[nk,2]
            out=np.clip(out*brillo,0,255); out[np.abs(Zg)>=4]=bg_rgb
            frames.append(Image.fromarray(out.astype(np.uint8),"RGB"))
            prog.progress((idx+1)/12)
        gif_buf=io.BytesIO(); frames[0].save(gif_buf,format="GIF",save_all=True,append_images=frames[1:],duration=120,loop=0,optimize=True)
        st.image(frames[-1],width=400); st.download_button("⬇️ GIF 12 frames",gif_buf.getvalue(),f"{nombre_cliente}_12frames.gif","image/gif")
else:
    st.subheader("365 dias - Generador LOCAL")
    st.error("Streamlit Cloud no puede generar 365 frames, lo corta a los 60s y te da Oh, no. Genera el GIF en tu PC.")
    st.code(f'''
# Guarda esto como genera_365.py y corre: python genera_365.py
import numpy as np
from PIL import Image
import math

W,H=400,300
zoom={zoom}
tam={tam}
brillo={brillo}
c_base={FRACTALES[tipo_fractal]["c"]}
colores={colores_actuales}
bg={bg_rgb}
tipo="{tipo_fractal}"

def hex_to_rgb(h):
    h=h.lstrip('#'); return [int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)]

palette=np.array([hex_to_rgb(c) for c in colores],float)
frames=[]

for dia in range(1,366):
    t=dia/365*2*math.pi
    cx=c_base.real+0.005*math.cos(t*3)
    cy=c_base.imag+0.005*math.sin(t*3)
    c_var=complex(cx,cy)
    x=np.linspace(-1.5/zoom,1.5/zoom,W)
    y=np.linspace(-1.0/zoom,1.0/zoom,H)
    X,Y=np.meshgrid(x,y)
    Z=X+1j*Y
    for _ in range(30): Z=Z*Z+c_var
    s=(np.angle(Z)*0.22+np.log(np.abs(Z)+1)*tam)*0.375 % 1.0
    pos=s*6.0; i0=np.floor(pos).astype(int)%6; f=pos-np.floor(pos); f=0.5*(1-np.cos(f*np.pi))
    out=np.zeros((H,W,3),float)
    for k in range(6):
        m=i0==k; nk=(k+1)%6
        out[m,0]=(1-f[m])*palette[k,0]+f[m]*palette[nk,0]
        out[m,1]=(1-f[m])*palette[k,1]+f[m]*palette[nk,1]
        out[m,2]=(1-f[m])*palette[k,2]+f[m]*palette[nk,2]
    out=np.clip(out*brillo,0,255)
    out[np.abs(Z)>=4]=bg
    frames.append(Image.fromarray(out.astype(np.uint8),"RGB"))
    print(f"Frame {{dia}}/365")

frames[0].save("ROBERTO_ZERTUCHE_365DIAS.gif", save_all=True, append_images=frames[1:], duration=80, loop=0, optimize=True)
print("GIF 365 listo")
''', language='python')

    st.download_button("⬇️ Descargar genera_365.py", f'''
import numpy as np
from PIL import Image
import math
W,H=400,300; zoom={zoom}; tam={tam}; brillo={brillo}
c_base={FRACTALES[tipo_fractal]["c"]}; colores={colores_actuales}; bg={bg_rgb}
def hex_to_rgb(h): h=h.lstrip('#'); return [int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)]
palette=np.array([hex_to_rgb(c) for c in colores],float); frames=[]
for dia in range(1,366):
    t=dia/365*2*math.pi; cx=c_base.real+0.005*math.cos(t*3); cy=c_base.imag+0.005*math.sin(t*3); c_var=complex(cx,cy)
    x=np.linspace(-1.5/zoom,1.5/zoom,W); y=np.linspace(-1.0/zoom,1.0/zoom,H); X,Y=np.meshgrid(x,y); Z=X+1j*Y
    for _ in range(30): Z=Z*Z+c_var
    s=(np.angle(Z)*0.22+np.log(np.abs(Z)+1)*tam)*0.375 % 1.0; pos=s*6.0; i0=np.floor(pos).astype(int)%6; f=pos-np.floor(pos); f=0.5*(1-np.cos(f*np.pi))
    out=np.zeros((H,W,3),float)
    for k in range(6): m=i0==k; nk=(k+1)%6; out[m,0]=(1-f[m])*palette[k,0]+f[m]*palette[nk,0]; out[m,1]=(1-f[m])*palette[k,1]+f[m]*palette[nk,1]; out[m,2]=(1-f[m])*palette[k,2]+f[m]*palette[nk,2]
    out=np.clip(out*brillo,0,255); out[np.abs(Z)>=4]=bg; frames.append(Image.fromarray(out.astype(np.uint8),"RGB")); print(dia)
frames[0].save("ROBERTO_ZERTUCHE_365DIAS.gif", save_all=True, append_images=frames[1:], duration=80, loop=0, optimize=True)
'''.encode(), file_name="genera_365.py", mime="text/x-python")
