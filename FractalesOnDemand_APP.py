
    img=np.zeros((h,w,3),dtype=np.uint8)
    img[valid]=np.stack([r_.astype(np.uint8),g_.astype(np.uint8),b_.astype(np.uint8)],axis=1)
    return img

W=1200; H=1200
img=julia_target(W,H,c,zoom,center_x,center_y,iters,ciclos,mezcla,suavizado,modo)
st.image(img,use_container_width=True,channels="RGB")
st.success(f"MODO={modo} | Para EL QUE BUSCO: p=2 α=1 β=1 γ=0 ciclos=7.0 mezcla=0.6 zoom=1.0 | Tus 5 capturas eran con p=5 -> por eso salian planos")

with st.sidebar:
    if st.button("Generar Export Alta"):
        img_hi=julia_target(resolucion,resolucion,c,zoom,center_x,center_y,iters,ciclos,mezcla,suavizado,modo)
        buf=io.BytesIO()
        Image.fromarray(img_hi).save(buf,format="PNG")
        st.download_button("Descargar PNG",buf.getvalue(),file_name=f"fractal_V74_TARGET_DIA{dia}.png",mime="image/png")
