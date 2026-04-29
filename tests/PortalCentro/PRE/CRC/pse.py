import asyncio, random, time
from faker import Faker
from playwright.async_api import async_playwright, expect
from utils.helpers import generar_documento, captura_pantalla, generar_pdf_con_portada, obtener_pin_yopmail
from utils.logger import get_logger
from datetime import datetime
from fpdf import FPDF  #Librería para generar pdf con las capturas 

logger = get_logger()
#===========================================
# Generación de datos aleatorios para el formulario
#===========================================
fake = Faker("es_ES") # inicializa faker en español, faker ayuda a generar nombres y datos aleatorios
genero = random.choice(["Hombre", "Mujer"])
primer_nombre = "Certificación"
segundo_nombre = fake.first_name()
nombres_completos = primer_nombre + " " + segundo_nombre
primer_apellido = fake.last_name()
segundo_apellido = fake.last_name()
apellidos_completos = primer_apellido + " " + segundo_apellido
tipo_documento = "Nit"
documento = generar_documento()
correo = "david.castro@yopmail.com"
correoPSE = "usuariopse@yopmail.com"
celular = "3192097403"
fecha_nacimiento = fake.date_of_birth(minimum_age=18, maximum_age=80)

dia = str(fecha_nacimiento.day)
mes = str(fecha_nacimiento.month)
año = str(fecha_nacimiento.year)

async def seleccionar_crc(page):
    try:
        popup_body = page.locator("#popup-info-whatsapp .popup-modal-body")

        # Esperar brevemente a ver si aparece el popup
        try:
            await popup_body.wait_for(state="visible", timeout=60000)
            await popup_body.click()
        except:
            pass  # no apareció, continua normal

        captura_pantalla("captura01")

        await page.locator("main.centros_main").click(timeout=60000)

        await page.locator("select#tipoCentro").select_option(label="CRC")
        await page.fill("#nombreCentro", "CERTIFICACION - CRC")
        await page.click("text=CERTIFICACION - CRC")
        await page.get_by_role("button", name=" Seleccionar ").click()

    except Exception as e:
        logger.info(f"[WARN] seleccionar_crc falló pero continúa: {e}")

async def main():
    async with async_playwright() as p:
        logger.info("Iniciando el proceso de automatización con Playwright")
        # Carpeta donde se guardarán los datos de usuario
        user_data_dir = "./cookies"
        
        # Inicia Chromium con contexto persistente (NO incógnito)
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,  # muestra el navegador
            viewport={"width":1420, "height":900}
        )
        
        # Borrar todas las cookies
        await context.clear_cookies()

        # Obtiene la primera página abierta o crea una nueva
        page = context.pages[0] if context.pages else await context.new_page()

        start_time = time.time() #Inicia captura de tiempo
        
        # Navega a Mi Licencia Centro
        await page.goto("https://milicenciaprecentro.sisec.co:7112")
        
        await seleccionar_crc(page)


        # Esperar a que el botón "Comprar PIN" esté visible antes de hacer clic
        btn = page.locator("a.button-primary", has_text="Comprar PIN")
        await btn.wait_for(state="visible", timeout=10000)
        await btn.click()

        captura_pantalla("captura02")

        await page.get_by_role("radio", name=genero).click()
        await page.fill("#day", dia)
        await page.fill("#month", mes)
        await page.fill("#year", año)
        await page.click("text=Siguiente")

        btnPrimeraVez = page.locator('input[name="opcionTramite"][id="1"]')
        await btnPrimeraVez.wait_for(state="visible", timeout=10000)
        await btnPrimeraVez.click()        
        btnSiguiente = page.locator("button.button-primary", has_text="Siguiente")
        await btnSiguiente.wait_for(state="visible")

        captura_pantalla("captura03")

        await btnSiguiente.click()

        
        await page.click("text=Primera vez o licencia adicional")
        await page.click("text=Siguiente")
        await page.click("text=Automóviles, cuatrimotos, camionetas y microbuses")
        
        captura_pantalla("captura04")
        
        await page.click("text=Siguiente")
        
        await page.fill("#email", correo)
        await page.fill("#celular", celular)
        await page.fill("#nombres", nombres_completos)
        await page.fill("#apellidos", apellidos_completos)
        await page.locator("select#tipoDocumento").select_option("2: 1")
        await page.fill("#documento", documento)        

        # Activar Formulario de facturación electronica
        await page.locator("span.slider").click()
        await page.wait_for_timeout(1000)

        captura_pantalla("captura05")

        await page.click("text=Siguiente")
        
        page.set_default_timeout(30000)  # 5 segundos
        
        # Formulario factura electrónica
        await page.fill("#correoFE", correo)
        await page.fill("#nombresFE", nombres_completos)
        await page.fill("#apellidosFE", apellidos_completos)
        await page.locator("#tipoDocumentoFE").click()
        await page.locator("#tipoDocumentoFE").select_option(label=tipo_documento)
        await page.fill("#documentoFE", documento)

        captura_pantalla("captura06")

        await page.click("text=Siguiente")

        #await page.click("text= Pago único de")

        captura_pantalla("captura07")

        await page.click("text=Siguiente")
        await page.locator("label:text('PSE')").click()
        await page.locator("select#tipoPersona").select_option("N")
        # Selección "BANCO UNION COLOMBIANO" value 1022
        await page.locator("select#banco").select_option("1022")
        
        captura_pantalla("captura08")
        
        await page.click("text=Continuar")
        
                
        await page.locator("label:text('Acepto los términos y condiciones')").click()
        await page.click("text= Pagar con PSE ")
               
        captura_pantalla("captura09")

        #================================
        # Formulario prueba PSE
        #================================

        btnPSE = page.locator("#PNEMail")
        await btnPSE.wait_for(state="visible", timeout=60000)
        await page.fill("#PNEMail", correoPSE)
        await page.locator("button#btnSeguir").click()
        await page.locator("input#btnPay").click()
        await page.locator("h6", has_text="Resumen del Pago").wait_for()
        captura_pantalla("captura09")
        await page.locator("input#VolverComercio").click()

        #================================
        # Captura del PIN generado
        #================================
        pin = None

        try:
            await page.locator("h3.nombre", has_text="PIN generado").wait_for()
            pin_raw = await page.locator("h3:has-text('PIN generado')").inner_text()
            pin = pin_raw.split("PIN generado")[1].strip(" :")
            logger.info(f"PIN generado: {pin}")
        except Exception as e:
            logger.error(f"No se pudo capturar el PIN: {e}")
        
        captura_pantalla("captura10")

        await page.click("text=Volver al sitio")

        #================================
        # Consulta estado del pin
        #================================

        await seleccionar_crc(page)

        await page.click("text= Consulta de estado del PIN")
        await page.locator("#tipoDocumento").select_option(value="1")
        await page.fill("#documentoActual", documento)
        # Obtener fecha actual en formato deseado
        fecha_actual = datetime.now().strftime("%d-%m-%y")  # Ejemplo: 2026-03-10
        # Llenar un campo con la fecha actual
        await page.fill("#fechaCompra", fecha_actual)

        captura_pantalla("captura11")

        await page.locator("button.button-primary", has_text="Continuar").click()


        #================================
        # Visualización de correo - YOPMAIL
        #================================

        pin = await obtener_pin_yopmail(
            p, 
            correo, 
            logger=logger
            )

        tiempo_total = time.time() - start_time #Finaliza captura de tiempos
        logger.info(f"⏱️ Tiempo total    : {tiempo_total:.2f} segundos") #Imprime tiempos en consola
        captura_pantalla("captura15")
        
        #====================================   
        # CAPTURAS PDF
        #====================================

        generar_pdf_con_portada(
            tiempo_total=tiempo_total
            ,carpeta="screenshot/Pin_pdp_crc_centro"
            ,archivo_pdf="Evidencias_Centro_CRC.pdf"
            ,archivo_texto="portada_crc.txt"
            ,logger=logger)
                
        await context.close()

asyncio.run(main())
