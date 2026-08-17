with st.sidebar:
    nombre_cliente = st.text_input("Nombre del cliente / proyecto", "ROBERTO ZERTUCHE")
    codigos = st.text_input("Codigos", "49/316/267")
    st.divider()
    tipo_fractal = st.selectbox("TIPO DE FRACTAL", list(FRACTALES.keys()), 1)
    dia = st.slider("DIA", 1, 365, 49)
    zoom = st.slider("ZOOM", 0.2, 5.0, 1.0)

    # FIX PALETA: el key incluye el nombre de la paleta para que se refresque
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
    fondo_transparente = st.checkbox("Fondo transparente", False)
    umbral = st.slider("Limpieza fondo", 0.0, 5.0, 1.0)
    incluir = st.checkbox("Incrustar etiqueta en imagen", True)
    calidad = st.slider("Calidad JPG", 80, 100, 95)
    st.divider()
    st.write("**GUARDAR**")
