import asyncio
from fpdf import FPDF   
from playwright.async_api import async_playwright


async def validar_otp_yopmail(otp, logger, screenshot_path, correo):

    async with async_playwright() as p:
        # Abrir navegador
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Ir a Yopmail
        await page.goto("https://yopmail.com")

        # Escribir en el input con id="login"
        await page.fill("#login", correo)

        # Click en botón
        await page.click('button[title="Revisa el correo @yopmail.com"]')

        # Seleccionar TODOS los divs con clase "m" el cual es un correo
        logger.info("Esperando por la pagina...")
        await page.wait_for_selector("iframe#ifinbox", timeout=20000)
        inbox = page.frame(name="ifinbox")
        if inbox is None:
            raise Exception("No se pudo acceder al iframe...")
        logger.info("Esperando correos...")

        await inbox.wait_for_selector(".m", timeout=20000)
        correos = await inbox.locator(".m").all()
        logger.info(f"Correos totales encontrados: {len(correos)}")
        for correo in correos:
            
            remitente = await correo.locator(".lmf").inner_text()
            asunto = await correo.locator(".lms").inner_text()
            logger.info(f"Remitente encontrado: {remitente}")
            logger.info(f"Asunto encontrado: {asunto}")
            remitente = remitente.strip().lower()
            asunto = asunto.strip().lower()

            #Filtro de correos olimpia
            if 'olimpiaotp@olimpiait.com' in remitente and 'pin generado' in asunto:
                #Hacer click en el contenido del correo 
                await correo.locator("button.lm").click()
                #Los correos se abren en un iframe llamado 'ifmail'
                iframe = page.frame(name='ifmail')
                #Esperar a que cargue el mensaje
                await iframe.wait_for_selector("body")
                #Una vez carga obtener todo el contenido del correo
                texto_correo = await iframe.locator("#mail div").inner_text()

                logger.info(f"Texto correo: {texto_correo}")
                if otp in texto_correo:
                    logger.info(f"OTP Recibido en Yopmail")
                    #Toma de screenshot
                    
                    await page.screenshot(path=screenshot_path)
                    await browser.close()
                    return texto_correo, screenshot_path
                else:
                    logger.info(f"OTP No encontrado en yopmail")
                    await browser.close()
                    return None, None
        
        logger.info("❌ No se encontró el OTP en Yopmail")
        await browser.close()
        return None, None