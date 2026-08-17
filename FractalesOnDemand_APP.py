import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io, math

st.set_page_config(layout="wide", page_title="Fractales On Demand V101 ANIMACION + ZOOM")

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

def crear_imagen_con_etiqueta_abajo(img_base, texto1, texto2, escala=1.0):
    W,H = img_base.size
    label_h = int(H * 0.14)
    nueva = Image.new("RGB", (W, H+label_h), (255,255,255))
    if img_base.mode == "RGBA":
        nueva.paste(img_base, (0,0), img_base)
    else:
        nueva.paste(img_base, (0,0))
    draw = ImageDraw.Draw(nueva)
    f1 = int(W * 0.016)
    f2 = int(W * 0.010)
    font1 = get_font(f1, True)
    font2 = get_font(f2, False)
    draw.text((int(W*0.02), H+int(label_h*0.15)), texto1, fill=(0,0,0), font=font1)
    try:
        bbox = draw.textbbox((0,0), texto1, font=font1)
        h1 = bbox[3]-bbox[1]
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
            Z2=Z*Z
            Z=np.abs(Z2.real)+1j*Z2.imag+C
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
            Z2=Z*Z; Z3=Z2*Z
            d=np.where(np.abs(3*Z2)<1e-6,1e-6,3*Z2)
            Z=Z-(Z3-1)/d
        return Z
    if tipo=="NOVA":
        Z=X+1j*Y
        for _ in range(40):
            Z2=Z*Z; Z3=Z2*Z
            d=np.where(np.abs(3*Z2)<1e-6,1e-6,3*Z2)
            Z=Z-(Z3-1)/d+c_var
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
    ys = np.linspace(-1.0/zoom, 1.0/zoom, H)
    xs = np.linspace(-1.5/zoom, 1.5/zoom, W)
    palette = np.array(colores_rgb, float)
    CHUNK=320
    for y0 in range(0,H,CHUNK):
        y1=min(y0+CHUNK,H)
        X,Y = np.meshgrid(xs, ys[y0:y1])
        Z = render_block(W, y1-y0, X, Y, c_var, tipo_fractal)
        s=(np.angle(Z)+np.pi)/(2*np.pi) if tipo_fractal in ("NEWTON","NOVA") else (np.angle(Z)*0.22+np.log(np.abs(Z)+1)*tam)*0.375 % 1.0
        pos=s*6.0; i0=np.floor(pos).astype(int)%6; f=pos-np.floor(pos); f=0.5*(1-np.cos(f*np.pi))
        out_chunk=np.zeros((y1-y0,W,3),float)
        for k in range(6):
            m=i0==k; nk=(k+1)%6
            out_chunk[m,0]=(1-f[m])*palette[k,0]+f[m]*palette[nk,0]
            out_chunk[m,1]=(1-f[m])*palette[k,1]+f[m]*palette[nk,1]
            out_chunk[m,2]=(1-f[m])*palette[k,2]+f[m]*palette[nk,2]
        out_chunk=np.clip(out_chunk*brillo_val,0,255)
        brillo_pix=out_chunk.mean(axis=2)
        mag=np.abs(Z)
        mask = brillo_pix>(10+umbral*10) if tipo_fractal in ("NEWTON","NOVA") else (mag<4) & (brillo_pix>(10+umbral*10))
        if bg_mode!="Transparente":
            bg_arr=np.zeros_like(out_chunk); bg_arr[:,:]=bg_rgb
            out_chunk=np.where(mask[:,:,None], out_chunk, bg_arr)
        out_full[y0:y1]=out_chunk.astype(np.uint8)
        mask_full[y0:y1]=mask
    if bg_mode=="Transparente":
        alpha=np.where(mask_full,255,0).astype(np.uint8)
        img_true=Image.fromarray(np.dstack((out_full,alpha)), "RGBA")
    else:
        img_true=Image.fromarray(out_full, "RGB").convert("RGBA")
    if incluir_etiqueta:
        img_true=crear_imagen_con_etiqueta_abajo(img_true, texto1, texto2, W/1000)
    return img_true

def generar_animacion(W, H, zoom, c_var, tipo_fractal, colores_rgb, tam, brillo_val, bg_mode, bg_rgb, umbral, anim_tipo, num_frames, zoom_start, texto1, texto2, incluir_etiqueta):
    palette = np.array(colores_rgb, float)
    frames = []
    # pasos de iteracion
    if anim_tipo == "Crecimiento por iteraciones":
        it_steps = np.linspace(2, 60, num_frames, dtype=int)
        x = np.linspace(-1.5/zoom, 1.5/zoom, W)
        y = np.linspace(-1.0/zoom, 1.0/zoom, H)
        X,Y = np.meshgrid(x,y)
        Z0 = X+1j*Y
        for idx, it in enumerate(it_steps):
            Z = Z0.copy()
            if tipo_fractal=="BURNING SHIP JULIA":
                for _ in range(it): Z=(np.abs(Z.real)+1j*np.abs(Z.imag))**2+c_var
            else:
                for _ in range(it): Z=Z*Z+c_var
            s=(np.angle(Z)+np.pi)/(2*np.pi) if tipo_fractal in ("NEWTON","NOVA") else (np.angle(Z)*0.22+np.log(np.abs(Z)+1)*tam)*0.375 % 1.0
            pos=s*6.0; i0=np.floor(pos).astype(int)%6; f=pos-np.floor(pos); f=0.5*(1-np.cos(f*np.pi))
            out=np.zeros((H,W,3),float)
            for k in range(6):
                m=i0==k; nk=(k+1)%6
                out[m,0]=(1-f[m])*palette[k,0]+f[m]*palette[nk,0]
                out[m,1]=(1-f[m])*palette[k,1]+f[m]*palette[nk,1]
                out[m,2]=(1-f[m])*palette[k,2]+f[m]*palette[nk,2]
            out=np.clip(out*brillo_val,0,255)
            mag=np.abs(Z)
            mask = out.mean(axis=2)>(10+umbral*10) if tipo_fractal in ("NEWTON","NOVA") else
            
