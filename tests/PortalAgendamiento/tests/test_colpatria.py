import pytest, os


@pytest.mark.asyncio
async def test_compra_pin_colpatria(logger, datos_usuario):
    logger.info("Iniciando flujo de compra de pin Colpatria")


    correo = datos_usuario["correo"]
    telefono = datos_usuario["telefono"]

    logger.info(f"Ejecutando test con correo={correo} y teléfono={telefono}")

    timestamp = generar_timestamp()
    base_dir = f"evidencias/{timestamp}"
    os.makedirs(base_dir, exist_ok=True)


    # Paths
    html_path = f"{base_dir}/reporte_otp.html"
    pdf_path = f"{base_dir}/reporte_otp.pdf"
    screenshot_path = f"{base_dir}/yopmail.png"

    #=============================
    #    API POSTMAN
    #=============================
    resp_generacion, url_generacion = generar_otp_postman(
        logger=logger,
        correo=correo,
        telefono=telefono
        )
    json_generacion = resp_generacion.json()
    assert resp_generacion.status_code == 200
    
    data = resp_generacion.json()
    otp = data.get("TextoOTP")
    identificador = data.get("Identificador")

    logger.info(f"OTP generado = {otp}")
    assert otp is not None

    
    resp_validacion, url_validacion = validar_otp_postman(identificador, otp, logger)
    json_validacion = resp_generacion.json()
    
    assert resp_validacion.status_code == 200


    #=============================
    #    WEB CORREO - YOPMAIL
    #=============================
    texto_correo, screenshot_path = await validar_otp_yopmail(
        otp, 
        logger=logger, 
        screenshot_path=screenshot_path,
        correo=correo
        )
    

    #=============================
    #    GENERACIÓN DE REPORTES
    #=============================

    
    generar_html_otp(
        api_generacion=json_generacion,
        api_validacion=json_validacion,
        otp=otp,
        evidencia_yopmail=texto_correo,
        screenshot_path="yopmail.png",
        output_path=html_path,
        url_generacion=url_generacion,
        url_validacion=url_validacion
    )


    generar_pdf_otp(
            api_generacion=json_generacion,
            api_validacion=json_validacion,
            otp=otp,
            evidencia_yopmail=texto_correo,
            screenshot_path=screenshot_path,
            output_path=pdf_path,
            url_generacion=url_generacion,
            url_validacion=url_validacion
        )


    logger.info("Flujo completo de generación y validación OTP OK")