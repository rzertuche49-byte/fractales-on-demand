import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io, math

st.set_page_config(layout="wide", page_title="Fractales V104 RESTAURADA ESTABLE")

def hex_to_rgb(h):
    h=h.lstrip('#')
    return [int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)]

def get_font(size, bold=True):
    size=int(max(size,10))
    try:
        from matplotlib import font_manager
        name="DejaVu Sans" if bold else "DejaVu Sans Mono"
        fp=font_manager.findfont(name, fallback_to_default=True)
        return ImageFont.truetype(fp, size)
    except:
        try: return ImageFont.truetype("DejaVuSans.ttf", size)
        except: return ImageFont.load_default()

def crear_imagen_con_etiqueta_abajo(img_base, texto1, texto2):
    W,H=img_base.size
    label_h=int(H*0.14)
    nueva=Image.new("RGB",(W,H+label_h),(255,255,255))
    if img_base.mode=="RGBA":
        nueva.paste(img_base,(0,0),img_base)
    else:
        nueva.paste(img_base,(0,0))
    draw=ImageDraw.Draw(nueva)
    f1=int(W*0.016); f2=int(W*0.010)
    font1=get_font(f1,True); font2=get_font(f2,False)
    draw.text((int(W*0.02), H+int(label_h*0.15)), texto1, fill=(0,0,0), font=font1)
    try:
        bbox=draw.textbbox((0,0), texto1, font=font1); h1=bbox[3]-bbox[1]
    except: h1=f1
    draw.text((int(W*0.02), H+int(label_h*0.15)+h1+int(label_h*0.08)), texto2, fill=(0,0,0), font=font2)
    return nueva

@st.cache_data
def render_preview_cached(W,H,zoom,cx,cy,tipo,tam,brillo,colores_tuple,bg_tuple,umbral):
    xs=np.linspace(-1.5/zoom,1.5/zoom,W)
    ys=np.linspace(-1.0/zoom,1.0/zoom,H)
    X,Y=np.meshgrid(xs,ys)
    Z=X+1j*Y
    c_var=complex(cx,cy)
    # PREVIEW rapido 40 iteraciones
    it=20 if tipo in ("NEWTON","NOVA") else 40
    if tipo=="MANDELBROT":
        C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
        for _ in range(it): Z=Z*Z+C
    elif tipo=="TRICORN":
        C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
        for _ in range(it): Z=np.conj(Z)**2+C
    elif tipo=="BURNING SHIP MANDELBROT":
        C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
        for _ in range(it): Z=(np.abs(Z.real)+1j*np.abs(Z.imag))**2+C
    elif tipo=="BUFFALO":
        C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
        for _ in range(it):
            ZR=np.abs(Z.real); ZI=np.abs(Z.imag)
            Z=(ZR*ZR-ZI*ZI)+2*ZR*ZI*1j+C
    elif tipo=="CELTIC":
        C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
        for _ in range(it):
            Z2=Z*Z; Z=np.abs(Z2.real)+1j*Z2.imag+C
    elif tipo=="MULTIBROT 3":
        C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
        for _ in range(it): Z=Z**3+C
    elif tipo=="MULTIBROT 4":
        C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
        for _ in range(it): Z=Z**4+C
    elif tipo=="NEWTON":
        for _ in range(20):
            Z2=Z*Z; Z3=Z2*Z; d=np.where(np.abs(3*Z2)<1e-6,1e-6,3*Z2); Z=Z-(Z3-1)/d
    elif tipo=="NOVA":
        for _ in range(40):
            Z2=Z*Z; Z3=Z2*Z; d=np.where(np.abs(3*Z2)<1e-6,1e-6,3*Z2); Z=Z-(Z3-1)/d+c_var
    elif tipo=="BURNING SHIP JULIA":
        for _ in range(it): Z=(np.abs(Z.real)+1j*np.abs(Z.imag))**2+c_var
    else:
        for _ in range(it): Z=Z*Z+c_var

    if tipo in ("NEWTON","NOVA"):
        s=(np.angle(Z)+np.pi)/(2*np.pi)
    else:
        s=(np.angle(Z)*0.22+np.log(np.abs(Z)+1)*tam)*0.375 % 1.0

    palette=np.array([hex_to_rgb(c) for c in colores_tuple],float)
    pos=s*6.0; i0=np.floor(pos).astype(int)%6; f=pos-np.floor(pos); f=0.5*(1-np.cos(f*np.pi))
    out=np.zeros((H,W,3),float)
    for k in range(6):
        m=i0==k; nk=(k+1)%6
        out[m,0]=(1-f[m])*palette[k,0]+f[m]*palette[nk,0]
        out[m,1]=(1-f[m])*palette[k,1]+f[m]*palette[nk,1]
        out[m,2]=(1-f[m])*palette[k,2]+f[m]*palette[nk,2]
    out=np.clip(out*brillo,0,255)
    mag=np.abs(Z); br_pix=np.mean(out,axis=2)
    if tipo in ("NEWTON","NOVA"):
        mask=br_pix>(10+umbral*10)
    else:
        mask=np.logical_and(mag<4, br_pix>(10+umbral*10))

    # Manejo fondo
    if len(bg_tuple)==4 and bg_tuple[3]==0: # Transparente flag
        alpha=np.where(mask,255,0).astype(np.uint8)
        img=Image.fromarray(np.dstack((out.astype(np.uint8),alpha)),"RGBA")
    else:
        out_bg=out.copy()
        out_bg[~mask]=bg_tuple[:3]
        img=Image.fromarray(out_bg.astype(np.uint8),"RGB").convert("RGBA")
    return img

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
    "HORSESHOE": {"c": complex(-0.74543, 0.11301), "formula": "HERRADURA | C=-0,745+0,113i"},
    "RABBIT": {"c": complex(-0.123, 0.745), "formula": "Zn+1=Zn2+C"},
    "DENDRITE": {"c": complex(-0.745, 0.11), "formula": "Zn+1=Zn2+C"},
    "SPIRAL": {"c": complex(-0.77568377, 0.13646737), "formula": "Zn+1=Zn2+C"},
    "SIEGEL DISK": {"c": complex(-0.391, -0.587), "formula": "Zn+1=Zn2+C"},
    "FEATHER": {"c": complex(-0.8, 0.156), "formula": "Zn+1=Zn2+C"},
    "DOUADY RABBIT V2": {"c": complex(-0.12256, 0.74486), "formula": "Zn+1=Zn2+C"},
    "SAN MARCO DRAGON": {"c": complex(-0.75, 0.0), "formula": "Zn+1=Zn2+C"},
    "HEART": {"c": complex(-0.1, 0.651), "formula": "Zn+1=Zn2+C"},
    "DOUBLE SPIRAL": {"c": complex(-0.5251993, 0.5251993), "formula": "Zn+1=Zn2+C"},
    "BURNING SHIP JULIA": {"c": complex(-0.5, -0.5), "formula": "Zn+1=(|Re|+i|Im|)2+C"},
    "MANDELBROT": {"c": complex(0,0), "formula": "Zn+1=Zn2+C"},
    "TRICORN": {"c": complex(0,0), "formula": "Zn+1=conj(Zn)2+C"},
    "BURNING SHIP MANDELBROT": {"c": complex(0,0), "formula": "Zn+1=(|Re|+i|Im|)2+C"},
    "BUFFALO": {"c": complex(0,0), "formula": "Zn+1=|Zn|2+C"},
    "CELTIC": {"c": complex(0,0), "formula": "Zn+1=|Re(Z2)|+i*Im(Z2)+C"},
    "MULTIBROT 3": {"c": complex(0,0), "formula": "Zn+1=Zn3+C"},
    "MULTIBROT 4": {"c": complex(0,0), "formula": "Zn+1=Zn4+C"},
    "NEWTON": {"c": complex(0,0), "formula": "Zn+1=Zn-(Z3-1)/3Z2"},
    "NOVA": {"c": complex(-0.5, 0.0), "formula": "Zn+1=NOVA(Zn)+C"},
    "SINE": {"c": complex(0.5, 0.5), "formula": "Zn+1=sin(Zn)+C"},
}

with st.sidebar:
    st.title("Fractales V104 RESTAURADA")
    nombre_cliente = st.text_input("Cliente", "ROBERTO ZERTUCHE")
    codigos = st.text_input("Códigos", "49/316/267")
    st.divider()
    tipo_fractal = st.selectbox("TIPO DE FRACTAL (21)", list(FRACTALES.keys()), 0)
    dia = st.slider("DIA", 1, 365, 49)
    zoom = st.slider("ZOOM FINAL", 0.2, 5.0, 1.0)
    paleta_nombre = st.selectbox("PALETA", list(PALETAS.keys()), 0)
    base = PALETAS[paleta_nombre]
    st.write("**EDITA 6 COLORES**")
    c1=st.color_picker("C1", base[0], key=f"c1_{paleta_nombre}")
    c2=st.color_picker("C2", base[1], key=f"c2_{paleta_nombre}")
    c3=st.color_picker("C3", base[2], key=f"c3_{paleta_nombre}")
    c4=st.color_picker("C4", base[3], key=f"c4_{paleta_nombre}")
    c5=st.color_picker("C5", base[4], key=f"c5_{paleta_nombre}")
    c6=st.color_picker("C6", base[5], key=f"c6_{paleta_nombre}")
    colores_actuales=[c1,c2,c3,c4,c5,c6]
    st.write("---")
    tam = st.slider("Tamano mancha", 0.1, 3.0, 1.8)
    brillo = st.slider("Brillo", 0.5, 2.5, 1.4)
    st.divider()
    fondo_mode = st.selectbox("FONDO", ["Negro", "Blanco", "Transparente", "Color de paleta"], 0)
    fondo_color_custom = "#FF00C8"
    if fondo_mode == "Color de paleta":
        fondo_color_custom = st.color_picker("Elige color de fondo", base[0], key=f"bg_{paleta_nombre}")
    umbral = st.slider("Limpieza fondo", 0.0, 5.0, 1.0)
    presentar_etiqueta = st.checkbox("Presentar etiqueta debajo (mitad)", True)
    st.divider()
    anim_tipo = st.selectbox("Animacion en nube", ["Crecimiento 12 frames", "Crecimiento 60 frames"], 0)
    st.caption("365 dias se genera local - ver abajo")

# Fondos
if fondo_mode == "Negro": bg_tuple=(0,0,0)
elif fondo_mode == "Blanco": bg_tuple=(255,255,255)
elif fondo_mode == "Transparente": bg_tuple=(0,0,0,0)
else: bg_tuple=tuple(hex_to_rgb(fondo_color_custom))

t=dia/365*2*math.pi
base_c=FRACTALES[tipo_fractal]["c"]
es_fijo=tipo_fractal in ("MANDELBROT","TRICORN","BURNING SHIP MANDELBROT","BUFFALO","CELTIC","MULTIBROT 3","MULTIBROT 4","NEWTON")
if es_fijo or tipo_fractal=="NOVA":
    cx=base_c.real; cy=base_c.imag
else:
    cx=base_c.real+0.005*math.cos(t*3); cy=base_c.imag+0.005*math.sin(t*3)

# PREVIEW 800x600 CACHEADO - ESTO EVITA EL OH NO
W,H=800,600
img_preview = render_preview_cached(W,H,zoom,cx,cy,tipo_fractal,tam,brillo,tuple(colores_actuales),bg_tuple,umbral)

texto1=f"{nombre_cliente} {codigos}" if codigos.strip() else nombre_cliente
texto2=FRACTALES[tipo_fractal]["formula"]+f" | C={cx:.4f}+{cy:.4f}i"

# Mostrar
st.image(img_preview, width=800)
if presentar_etiqueta:
    img_final=crear_imagen_con_etiqueta_abajo(img_preview, texto1, texto2)
else:
    img_final=img_preview

st.markdown(f"""
<div style="background:white;padding:8px 14px 10px 14px;border:1px solid #E5E5E5;border-top:none;margin-top:-4px;border-radius:0 0 10px 10px;max-width:800px">
    <div style="color:black;font-weight:800;font-size:12px;">{texto1}</div>
    <div style="color:#222;font-family:monospace;font-size:9px;margin-top:3px;">{texto2}</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    buf=io.BytesIO(); img_final.save(buf, format="PNG")
    st.download_button("⬇️ PNG 800 con etiqueta mitad", buf.getvalue(), f"{nombre_cliente}_800_ETIQUETA.png", "image/png")
    st.divider()
    st.write("**8K REAL - solo cuando lo necesites**")
    if st.button("Generar 8K REAL 7680x6144"):
        with st.spinner("Generando 8K... 25 seg"):
            img_8k=render_preview_cached(7680,6144,zoom,cx,cy,tipo_fractal,tam,brillo,tuple(colores_actuales),bg_tuple,umbral)
            if presentar_etiqueta:
                img_8k=crear_imagen_con_etiqueta_abajo(img_8k,texto1,texto2)
            buf8=io.BytesIO(); img_8k.save(buf8,format="PNG")
            st.download_button("⬇️ PNG 8K REAL", buf8.getvalue(), f"{nombre_cliente}_8K.png", "image/png", key="8k")

st.divider()
col1,col2=st.columns(2)
with col1:
    st.subheader("Animacion segura en nube")
    num_frames=12 if "12" in anim_tipo else 60
    if st.button(f"Generar {anim_tipo}"):
        frames=[]; prog=st.progress(0)
        it_steps=np.linspace(2,40,num_frames,dtype=int)
        for idx,it in enumerate(it_steps):
            # Truco: iteraciones variables para efecto crecimiento
            # Reusamos cache variando brillo levemente para forzar recalculo con it
            xs=np.linspace(-1.5/zoom,1.5/zoom,400)
            ys=np.linspace(-1.0/zoom,1.0/zoom,300)
            X,Y=np.meshgrid(xs,ys)
            Z=X+1j*Y; c_var=complex(cx,cy)
            for _ in range(int(it)): Z=Z*Z+c_var
            s=(np.angle(Z)*0.22+np.log(np.abs(Z)+1)*tam)*0.375 % 1.0
            palette=np.array([hex_to_rgb(c) for c in colores_actuales],float)
            pos=s*6.0; i0=np.floor(pos).astype(int)%6; f=pos-np.floor(pos); f=0.5*(1-np.cos(f*np.pi))
            out=np.zeros((300,400,3),float)
            for k in range(6):
                m=i0==k; nk=(k+1)%6
                out[m,0]=(1-f[m])*palette[k,0]+f[m]*palette[nk,0]
                out[m,1]=(1-f[m])*palette[k,1]+f[m]*palette[nk,1]
                out[m,2]=(1-f[m])*palette[k,2]+f[m]*palette[nk,2]
            out=np.clip(out*brillo,0,255)
            out[np.abs(Z)>=4]=bg_tuple[:3] if len(bg_tuple)>=3 else (0,0,0)
            frames.append(Image.fromarray(out.astype(np.uint8),"RGB"))
            prog.progress((idx+1)/num_frames)
        gif_buf=io.BytesIO()
        frames[0].save(gif_buf,format="GIF",save_all=True,append_images=frames[1:],duration=120,loop=0,optimize=True)
        st.image(frames[-1],width=400)
        st.download_button("⬇️ Descargar GIF", gif_buf.getvalue(), f"{nombre_cliente}_{num_frames}frames.gif","image/gif")

with col2:
    st.subheader("365 dias - Generador LOCAL (evita Oh no)")
    st.caption("Este no se puede generar en Streamlit Cloud porque lo corta a 60s")
    st.download_button("⬇️ Descargar genera_365.py", f'''
import numpy as np
from PIL import Image
import math
W,H=400,300
zoom={zoom}
tam={tam}
brillo={brillo}
colores={colores_actuales}
bg={bg_tuple[:3]}
cx_base={FRACTALES[tipo_fractal]["c"].real}
cy_base={FRACTALES[tipo_fractal]["c"].imag}
tipo="{tipo_fractal}"

def hex_to_rgb(h):
    h=h.lstrip('#')
    return [int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)]

palette=np.array([hex_to_rgb(c) for c in colores],float)
frames=[]
for dia in range(1,366):
    t=dia/365*2*math.pi
    if tipo in ("MANDELBROT","TRICORN","BURNING SHIP MANDELBROT","BUFFALO","CELTIC","MULTIBROT 3","MULTIBROT 4","NEWTON","NOVA"):
        cx=cx_base; cy=cy_base
    else:
        cx=cx_base+0.005*math.cos(t*3); cy=cy_base+0.005*math.sin(t*3)
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
    print(f"{{dia}}/365")
frames[0].save("365DIAS_{nombre_cliente}.gif", save_all=True, append_images=frames[1:], duration=80, loop=0, optimize=True)
print("LISTO")
'''.encode(), file_name="genera_365.py", mime="text/x-python")
