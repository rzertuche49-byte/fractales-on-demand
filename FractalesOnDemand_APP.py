import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io, math, gc

st.set_page_config(layout="wide", page_title="Fractales V102.2 FIX OH NO")

def hex_to_rgb(h):
    h=h.lstrip('#')
    return [int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)]

def get_font(size, bold=True):
    size = int(max(size, 10))
    try:
        from matplotlib import font_manager
        name = "DejaVu Sans" if bold else "DejaVu Sans Mono"
        fp = font_manager.findfont(name, fallback_to_default=True)
        return ImageFont.truetype(fp, size)
    except:
        try: return ImageFont.truetype("DejaVuSans.ttf", size)
        except: return ImageFont.load_default()

def crear_imagen_con_etiqueta_abajo(img_base, texto1, texto2):
    W,H = img_base.size
    label_h = int(H * 0.14)
    nueva = Image.new("RGB", (W, H+label_h), (255,255,255))
    if img_base.mode == "RGBA":
        nueva.paste(img_base, (0,0), img_base)
    else:
        nueva.paste(img_base, (0,0))
    draw = ImageDraw.Draw(nueva)
    f1 = int(W * 0.016); f2 = int(W * 0.010)
    font1 = get_font(f1, True); font2 = get_font(f2, False)
    draw.text((int(W*0.02), H+int(label_h*0.15)), texto1, fill=(0,0,0), font=font1)
    try:
        bbox = draw.textbbox((0,0), texto1, font=font1); h1 = bbox[3]-bbox[1]
    except: h1 = f1
    draw.text((int(W*0.02), H+int(label_h*0.15)+h1+int(label_h*0.08)), texto2, fill=(0,0,0), font=font2)
    return nueva

def render_block(Wc, Hc, X, Y, c_var, tipo, it=60):
    if tipo=="MANDELBROT":
        C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
        for _ in range(it): Z=Z*Z+C
        return Z
    if tipo=="TRICORN":
        C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
        for _ in range(it): Z=np.conj(Z)**2+C
        return Z
    if tipo=="BURNING SHIP MANDELBROT":
        C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
        for _ in range(it): Z=(np.abs(Z.real)+1j*np.abs(Z.imag))**2+C
        return Z
    if tipo=="BUFFALO":
        C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
        for _ in range(it):
            ZR=np.abs(Z.real); ZI=np.abs(Z.imag)
            Z=(ZR*ZR-ZI*ZI)+2*ZR*ZI*1j+C
        return Z
    if tipo=="CELTIC":
        C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
        for _ in range(it):
            Z2=Z*Z; Z=np.abs(Z2.real)+1j*Z2.imag+C
        return Z
    if tipo=="MULTIBROT 3":
        C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
        for _ in range(it): Z=Z**3+C
        return Z
    if tipo=="MULTIBROT 4":
        C=(X-0.5)+1j*Y; Z=np.zeros_like(C)
        for _ in range(it): Z=Z**4+C
        return Z
    if tipo=="NEWTON":
        Z=X+1j*Y
        for _ in range(20):
            Z2=Z*Z; Z3=Z2*Z; d=np.where(np.abs(3*Z2)<1e-6,1e-6,3*Z2); Z=Z-(Z3-1)/d
        return Z
    if tipo=="NOVA":
        Z=X+1j*Y
        for _ in range(40):
            Z2=Z*Z; Z3=Z2*Z; d=np.where(np.abs(3*Z2)<1e-6,1e-6,3*Z2); Z=Z-(Z3-1)/d+c_var
        return Z
    if tipo=="SINE":
        Z=X+1j*Y
        for _ in range(it): Z=np.sin(Z)+c_var
        return Z
    if tipo=="COSINE":
        Z=X+1j*Y
        for _ in range(it): Z=np.cos(Z)+c_var
        return Z
    Z=X+1j*Y
    if tipo=="BURNING SHIP JULIA":
        for _ in range(it): Z=(np.abs(Z.real)+1j*np.abs(Z.imag))**2+c_var
    else:
        for _ in range(it): Z=Z*Z+c_var
    return Z

def render_fractal_true(W, H, zoom, c_var, tipo_fractal, colores_rgb, tam, brillo_val, bg_mode, bg_rgb, umbral, texto1, texto2, incluir_etiqueta):
    out_full = np.zeros((H, W, 3), dtype=np.uint8)
    mask_full = np.zeros((H, W), dtype=bool)
    ys = np.linspace(-1.0/zoom, 1.0/zoom, H); xs = np.linspace(-1.5/zoom, 1.5/zoom, W)
    palette = np.array(colores_rgb, float); CHUNK=320
    for y0 in range(0,H,CHUNK):
        y1=min(y0+CHUNK,H)
        X,Y = np.meshgrid(xs, ys[y0:y1])
        Z = render_block(W, y1-y0, X, Y, c_var, tipo_fractal)
        if tipo_fractal in ("NEWTON","NOVA"): s=(np.angle(Z)+np.pi)/(2*np.pi)
        else: s=(np.angle(Z)*0.22+np.log(np.abs(Z)+1)*tam)*0.375 % 1.0
        pos=s*6.0; i0=np.floor(pos).astype(int)%6; f=pos-np.floor(pos); f=0.5*(1-np.cos(f*np.pi))
        out_chunk=np.zeros((y1-y0,W,3),float)
        for k in range(6):
            m=i0==k; nk=(k+1)%6
            out_chunk[m,0]=(1-f[m])*palette[k,0]+f[m]*palette[nk,0]; out_chunk[m,1]=(1-f[m])*palette[k,1]+f[m]*palette[nk,1]; out_chunk[m,2]=(1-f[m])*palette[k,2]+f[m]*palette[nk,2]
        out_chunk=np.clip(out_chunk*brillo_val,0,255)
        brillo_pix=np.mean(out_chunk, axis=2); mag=np.abs(Z)
        if tipo_fractal in ("NEWTON","NOVA"): mask=brillo_pix>(10+umbral*10)
        else: mask=np.logical_and(mag<4, brillo_pix>(10+umbral*10))
        if bg_mode!="Transparente":
            bg_arr=np.zeros_like(out_chunk); bg_arr[:,:]=bg_rgb; out_chunk=np.where(mask[:,:,None], out_chunk, bg_arr)
        out_full[y0:y1]=out_chunk.astype(np.uint8); mask_full[y0:y1]=mask
    if bg_mode=="Transparente":
        alpha=np.where(mask_full,255,0).astype(np.uint8); img_true=Image.fromarray(np.dstack((out_full,alpha)), "RGBA")
    else:
        img_true=Image.fromarray(out_full, "RGB").convert("RGBA")
    if incluir_etiqueta: img_true=crear_imagen_con_etiqueta_abajo(img_true, texto1, texto2)
    return img_true

PALETAS = {"Tu captura": ["#00FFFF","#0064FF","#FF00C8","#FF6400","#FFFF00","#00FF64"],"Neon 80s": ["#00FFFF","#FF00FF","#FFFF00","#00FF00","#FF0066","#6600FF"],"Fuego": ["#FF0000","#FF6600","#FFCC00","#FF3300","#CC0000","#FF9900"],"Oceano Profundo": ["#001F54","#034078","#1282A2","#00B4D8","#90E0EF","#CAF0F8"],"Pastel Dream": ["#FFB5E8","#B5DEFF","#C3FF99","#FFF5BA","#FFC9DE","#D1BDFF"],"Sunset": ["#F72585","#7209B7","#3A0CA3","#4361EE","#4CC9F0","#FFBE0B"],"Galaxy": ["#0B0C10","#1F2833","#45A29E","#66FCF1","#C5C6C7","#9D00FF"],"Toxic": ["#00FF00","#CCFF00","#00FFCC","#FFFF00","#FF00FF","#00FFFF"],"Candy": ["#FF70A6","#FF9770","#FFD670","#E9FF70","#70FFB2","#70D6FF"],"Bosque": ["#0A2F0A","#1B5E20","#2E7D32","#66BB6A","#A5D6A7","#C8E6C9"],"Volcan": ["#000000","#4A0000","#8B0000","#FF4500","#FF8C00","#FFD700"],"Aurora": ["#03045E","#0077B6","#00B4D8","#90E0EF","#ADE8F4","#CAF0F8"],"Miami Vice": ["#FF6BEC","#3EFFE2","#FFD93D","#FF6B6B","#6BCB77","#4D96FF"],"Cyberpunk": ["#FF003C","#00F0FF","#F0FF00","#FF00F0","#00FF9F","#7000FF"],"Helado": ["#FEC8D8","#FFDFD3","#FFF0B5","#D0F4DE","#A9DEF9","#E4C1F9"],"Matrix": ["#000000","#003B00","#008F11","#00FF41","#00FF00","#AAFF00"],"Desierto": ["#7F5539","#9C6644","#B08968","#DDB892","#E6CCB2","#EDE0D4"],"Joker": ["#3D087B","#5A189A","#7B2CBF","#9D4EDD","#C77DFF","#00F5D4"],"Psicodelico": ["#FF00FF","#00FFFF","#FFFF00","#FF0000","#00FF00","#0000FF"],"Elegante": ["#000000","#1A1A1A","#D4AF37","#F5F5DC","#8B7355","#FFFFFF"],}
FRACTALES = {"RABBIT": {"c": complex(-0.123, 0.745), "formula": "Zn+1=Zn2+C"},"DENDRITE": {"c": complex(-0.745, 0.11), "formula": "Zn+1=Zn2+C"},"SPIRAL": {"c": complex(-0.77568377, 0.13646737), "formula": "Zn+1=Zn2+C"},"SIEGEL DISK": {"c": complex(-0.391, -0.587), "formula": "Zn+1=Zn2+C"},"FEATHER": {"c": complex(-0.8, 0.156), "formula": "Zn+1=Zn2+C"},"DOUADY RABBIT V2": {"c": complex(-0.12256, 0.74486), "formula": "Zn+1=Zn2+C"},"SAN MARCO DRAGON": {"c": complex(-0.75, 0.0), "formula": "Zn+1=Zn2+C"},"HORSESHOE": {"c": complex(-0.74543, 0.11301), "formula": "Zn+1=Zn2+C"},"HEART": {"c": complex(-0.1, 0.651), "formula": "Zn+1=Zn2+C"},"DOUBLE SPIRAL": {"c": complex(-0.5251993, 0.5251993), "formula": "Zn+1=Zn2+C"},"BURNING SHIP JULIA": {"c": complex(-0.5, -0.5), "formula": "Zn+1=(|Re|+i|Im|)2+C"},"MANDELBROT": {"c": complex(0,0), "formula": "Zn+1=Zn2+C"},"TRICORN": {"c": complex(0,0), "formula": "Zn+1=conj(Zn)2+C"},"BURNING SHIP MANDELBROT": {"c": complex(0,0), "formula": "Zn+1=(|Re|+i|Im|)2+C"},"BUFFALO": {"c": complex(0,0), "formula": "Zn+1=|Zn|2+C"},"CELTIC": {"c": complex(0,0), "formula": "Zn+1=|Re(Z2)|+i*Im(Z2)+C"},"MULTIBROT 3": {"c": complex(0,0), "formula": "Zn+1=Zn3+C"},"MULTIBROT 4": {"c": complex(0,0), "formula": "Zn+1=Zn4+C"},"NEWTON": {"c": complex(0,0), "formula": "Zn+1=Zn-(Z3-1)/3Z2"},"NOVA": {"c": complex(-0.5, 0.0), "formula": "Zn+1=NOVA(Zn)+C"},"SINE": {"c": complex(0.5, 0.5), "formula": "Zn+1=sin(Zn)+C"},"COSINE": {"c": complex(0.5, 0.5), "formula": "Zn+1=cos(Zn)+C"},}

with st.sidebar:
    nombre_cliente = st.text_input("Nombre del cliente / proyecto", "ROBERTO ZERTUCHE")
    codigos = st.text_input("Codigos", "49/316/267")
    st.divider()
    tipo_fractal = st.selectbox("TIPO DE FRACTAL (21)", list(FRACTALES.keys()), 7)
    dia = st.slider("DIA", 1, 365, 49)
    zoom = st.slider("ZOOM FINAL", 0.2, 5.0, 1.0)
    paleta_nombre = st.selectbox("PALETA", list(PALETAS.keys()), 0)
    base = PALETAS[paleta_nombre]
    st.write("**EDITA 6 COLORES**")
    c1=st.color_picker("C1", base[0], key=f"c1_{paleta_nombre}"); c2=st.color_picker("C2", base[1], key=f"c2_{paleta_nombre}"); c3=st.color_picker("C3", base[2], key=f"c3_{paleta_nombre}")
    c4=st.color_picker("C4", base[3], key=f"c4_{paleta_nombre}"); c5=st.color_picker("C5", base[4], key=f"c5_{paleta_nombre}"); c6=st.color_picker("C6", base[5], key=f"c6_{paleta_nombre}")
    colores_actuales=[c1,c2,c3,c4,c5,c6]
    tam = st.slider("Tamano mancha", 0.1, 3.0, 1.8); brillo = st.slider("Brillo", 0.5, 2.5, 1.4)
    fondo_mode = st.selectbox("FONDO", ["Negro", "Blanco", "Transparente", "Color de paleta"], 0)
    fondo_color_custom="#FF00C8"
    if fondo_mode=="Color de paleta": fondo_color_custom=st.color_picker("Elige color de fondo", base[0], key=f"bg_{paleta_nombre}")
    umbral = st.slider("Limpieza fondo", 0.0, 5.0, 1.0)
    presentar_etiqueta = st.checkbox("Presentar etiqueta debajo de la imagen", True)
    st.divider()
    st.subheader("ANIMACION")
    anim_tipo = st.selectbox("Tipo animacion", ["Crecimiento por iteraciones", "Zoom progresivo", "365 dias - año completo (OPTIMIZADO)"], 2)
    num_frames = st.slider("Numero de frames", 10, 365, 60, help="Para 365 dias usa 60 o 122, NO 365 si no crashea")
    duracion = st.slider("Duracion por frame ms", 50, 300, 100)
    anim_w = st.selectbox("Resolucion animacion", ["320x240 ULTRA LIGERA - para 365 dias", "400x300 ligera", "800x600 rapida"], 0)
    render_real_8k = st.checkbox("Render 8K REAL para imprenta", value=True)

if fondo_mode=="Negro": bg_rgb=[0,0,0]
elif fondo_mode=="Blanco": bg_rgb=[255,255,255]
elif fondo_mode=="Transparente": bg_rgb=[0,0,0]
else: bg_rgb=hex_to_rgb(fondo_color_custom)

t=dia/365*2*math.pi; base_c=FRACTALES[tipo_fractal]["c"]
es_fijo=tipo_fractal in ("MANDELBROT","TRICORN","BURNING SHIP MANDELBROT","BUFFALO","CELTIC","MULTIBROT 3","MULTIBROT 4","NEWTON")
es_nova=tipo_fractal=="NOVA"
if es_fijo or es_nova: cx=base_c.real; cy=base_c.imag
else: cx=base_c.real+0.005*math.cos(t*3); cy=base_c.imag+0.005*math.sin(t*3)
c_var=complex(cx,cy)

W,H=1000,800
x=np.linspace(-1.5/zoom,1.5/zoom,W); y=np.linspace(-1.0/zoom,1.0/zoom,H); X,Y=np.meshgrid(x,y)
Z=render_block(W,H,X,Y,c_var,tipo_fractal)
if tipo_fractal in ("NEWTON","NOVA"): s=(np.angle(Z)+np.pi)/(2*np.pi)
else: s=(np.angle(Z)*0.22+np.log(np.abs(Z)+1)*tam)*0.375 % 1.0
palette=np.array([hex_to_rgb(c) for c in colores_actuales],float)
pos=s*6.0; i0=np.floor(pos).astype(int)%6; f=pos-np.floor(pos); f=0.5*(1-np.cos(f*np.pi))
out=np.zeros((H,W,3),float)
for k in range(6):
    m=i0==k; nk=(k+1)%6
    out[m,0]=(1-f[m])*palette[k,0]+f[m]*palette[nk,0]; out[m,1]=(1-f[m])*palette[k,1]+f[m]*palette[nk,1]; out[m,2]=(1-f[m])*palette[k,2]+f[m]*palette[nk,2]
out=np.clip(out*brillo,0,255); mag=np.abs(Z); br=np.mean(out, axis=2)
if tipo_fractal in ("NEWTON","NOVA"): mask=br>(10+umbral*10)
else: mask=np.logical_and(mag<4, br>(10+umbral*10))
if fondo_mode=="Transparente": alpha=np.where(mask,255,0).astype(np.uint8); img_base=Image.fromarray(np.dstack((out.astype(np.uint8),alpha)), "RGBA")
else: out_bg=out.copy(); out_bg[~mask]=bg_rgb; img_base=Image.fromarray(out_bg.astype(np.uint8), "RGB").convert("RGBA")

if codigos.strip()!="": texto1=f"{nombre_cliente} {codigos}"
else: texto1=nombre_cliente
texto2=f"{tipo_fractal} | C={cx:.4f}+{cy:.4f}i | {FRACTALES[tipo_fractal]['formula']}"

st.image(img_base, width=1000)
if presentar_etiqueta:
    st.markdown(f"""<div style="background:white;padding:8px 14px 10px 14px;border:1px solid #E5E5E5;border-top:none;margin-top:-4px;border-radius:0 0 10px 10px;"><div style="color:black;font-weight:800;font-size:12px;">{texto1}</div><div style="color:#222;font-family:monospace;font-size:9px;margin-top:3px;">{texto2}</div></div>""", unsafe_allow_html=True)
    img_export_preview=crear_imagen_con_etiqueta_abajo(img_base, texto1, texto2)
else: img_export_preview=img_base
colores_rgb=[hex_to_rgb(c) for c in colores_actuales]

with st.sidebar:
    buf=io.BytesIO(); img_export_preview.save(buf, format="PNG")
    st.download_button("PNG Standard con etiqueta (mitad)", buf.getvalue(), f"{nombre_cliente}_STD_{fondo_mode}_ETIQUETA.png", "image/png", key="png_std")
    if render_real_8k and st.button("Generar 8K REAL", key="gen8k"):
        img_e=render_fractal_true(7680,6144,zoom,c_var,tipo_fractal,colores_rgb,tam,brillo,fondo_mode,bg_rgb,umbral,texto1,texto2,presentar_etiqueta)
        buf=io.BytesIO(); img_e.save(buf, format="PNG"); st.download_button("PNG 8K REAL mitad", buf.getvalue(), f"{nombre_cliente}_8K_REAL.png", "image/png", key="png_8k")

st.divider()
st.subheader(f"Animacion {anim_tipo} - {num_frames} frames")

if "320" in anim_w: aW,aH=320,240
elif "400" in anim_w: aW,aH=400,300
else: aW,aH=800,600

if st.button("Generar Animacion", key="gen_anim"):
    # LIMITE DE SEGURIDAD PARA NO TUMBAR APP
    if anim_tipo.startswith("365") and num_frames==365 and aW>320:
        st.error("365 frames a 800x600 tumba la app con Oh no. Cambia a 320x240 o baja a 122 frames.")
        st.stop()

    progress = st.progress(0); status = st.empty()
    frames = []
    palette_anim = np.array(colores_rgb, float)

    # Para 365 dias bajamos iteraciones a 30 para que no pese
    it_use = 30 if anim_tipo.startswith("365") else 60

    dias_anim = np.linspace(1, 365, num_frames)

    for idx in range(num_frames):
        if anim_tipo.startswith("365"):
            d = dias_anim[idx]; t_anim = d/365*2*math.pi
            base_c_anim = FRACTALES[tipo_fractal]["c"]
            if tipo_fractal in ("MANDELBROT","TRICORN","BURNING SHIP MANDELBROT","BUFFALO","CELTIC","MULTIBROT 3","MULTIBROT 4","NEWTON","NOVA"):
                cx_a=base_c_anim.real; cy_a=base_c_anim.imag
            else:
                cx_a=base_c_anim.real+0.005*math.cos(t_anim*3); cy_a=base_c_anim.imag+0.005*math.sin(t_anim*3)
            c_var_a=complex(cx_a, cy_a)
            zm=zoom
        else:
            c_var_a=c_var; zm=zoom if "Crecimiento" in anim_tipo else np.linspace(0.3, zoom, num_frames)[idx]

        ys = np.linspace(-1.0/zm, 1.0/zm, aH); xs = np.linspace(-1.5/zm, 1.5/zm, aW)
        Xg,Yg=np.meshgrid(xs, ys)
        Z = render_block(aW, aH, Xg, Yg, c_var_a, tipo_fractal, it_use)

        if tipo_fractal in ("NEWTON","NOVA"): s=(np.angle(Z)+np.pi)/(2*np.pi)
        else: s=(np.angle(Z)*0.22+np.log(np.abs(Z)+1)*tam)*0.375 % 1.0
        pos=s*6.0; i0=np.floor(pos).astype(int)%6; f=pos-np.floor(pos); f=0.5*(1-np.cos(f*np.pi))
        out=np.zeros((aH,aW,3),float)
        for k in range(6):
            m=i0==k; nk=(k+1)%6
            out[m,0]=(1-f[m])*palette_anim[k,0]+f[m]*palette_anim[nk,0]; out[m,1]=(1-f[m])*palette_anim[k,1]+f[m]*palette_anim[nk,1]; out[m,2]=(1-f[m])*palette_anim[k,2]+f[m]*palette_anim[nk,2]
        out=np.clip(out*brillo,0,255)
        mag=np.abs(Z); br_pix=np.mean(out, axis=2)
        if tipo_fractal in ("NEWTON","NOVA"): mask=br_pix>(10+umbral*10)
        else: mask=np.logical_and(mag<4, br_pix>(10+umbral*10))
        out[~mask]=bg_rgb if fondo_mode!="Transparente" else 0
        img=Image.fromarray(out.astype(np.uint8), "RGB")
        frames.append(img)

        # Liberar memoria cada 20 frames
        del Z, Xg, Yg, out, mag, br_pix
        if idx % 10 == 0:
            gc.collect()
            progress.progress((idx+1)/num_frames)
            status.text(f"Frame {idx+1}/{num_frames} - DIA {int(dias_anim[idx])} - Memoria OK")

    progress.progress(1.0); status.text("Compilando GIF final...")
    gif_buf = io.BytesIO()
    # optimize=True reduce 70% el peso
    frames[0].save(gif_buf, format="GIF", save_all=True, append_images=frames[1:], duration=duracion, loop=0, optimize=True)

    st.success(f"Listo: {len(frames)} frames {aW}x{aH} - {len(gif_buf.getvalue())/1024/1024:.1f} MB")
    st.image(frames[-1], caption=f"Ultimo frame DIA {int(dias_anim[-1])}", width=600)
    st.download_button("⬇️ Descargar GIF 365 DIAS", gif_buf.getvalue(), f"{nombre_cliente}_365DIAS_{aW}x{aH}.gif", "image/gif", key="gif_anim")

    # Limpiar
    del frames; gc.collect()
