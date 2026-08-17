def crear_imagen_con_etiqueta_abajo(img_base, texto1, texto2, escala=1.0):
    W,H = img_base.size
    # 13.5% alto - misma proporcion optima
    label_h = int(H * 0.135)
    nueva_h = H + label_h
    nueva = Image.new("RGB", (W, nueva_h), (255,255,255))
    if img_base.mode == "RGBA":
        nueva.paste(img_base, (0,0), img_base)
    else:
        nueva.paste(img_base, (0,0))
    draw = ImageDraw.Draw(nueva)
    draw.rectangle([0,H,W,nueva_h], fill=(255,255,255))
    draw.line([0,H,W,H], fill=(230,230,230), width=1)

    # REDUCIDO A LA MITAD - antes 0.028 y 0.019 -> ahora 0.014 y 0.0095
    font_size_1 = int(W * 0.014) # Standard 14px / 8K 107px (mitad)
    font_size_2 = int(W * 0.0095) # Standard 9px / 8K 73px (mitad)

    font1 = get_font_bold_fixed(font_size_1)
    font2 = get_font_mono_fixed(font_size_2)
    pad_x = int(W * 0.018)
    pad_y1 = int(label_h * 0.18)
    pad_y2 = int(label_h * 0.08) # entre lineas mas compacto

    draw.text((pad_x, H+pad_y1), texto1, fill=(0,0,0), font=font1)
    try:
        bbox1 = draw.textbbox((0,0), texto1, font=font1)
        h1 = bbox1[3]-bbox1[1]
    except:
        h1 = font_size_1
    draw.text((pad_x, H+pad_y1+h1+pad_y2), texto2, fill=(15,15,15), font=font2)
    return nueva
    
