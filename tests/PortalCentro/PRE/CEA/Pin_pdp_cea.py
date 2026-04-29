import asyncio
from playwright.async_api import async_playwright
import datetime
import pyautogui # iNFORMES
from PIL import Image, ImageDraw, ImageFont # iNFORMES
import os
import time


# === Función para capturar pantalla completa ===
def captura_pantalla(nombre_base, carpeta="screenshot/Pin_pdp_cea_centro"):
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f"{nombre_base}.png")
    screenshot = pyautogui.screenshot()
    screenshot.save(ruta)
    print(f"✅ Captura guardada: {ruta}")



async def main():
    async with async_playwright() as p:
        # Carpeta donde se guardarán los datos de usuario
        user_data_dir = "./cookies"
        
        # Inicia Chromium con contexto persistente (NO incógnito)
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            viewport={"width":1420, "height":900}
        )
        
        # Borrar todas las cookies
        await context.clear_cookies()

        # Obtiene la primera página abierta o crea una nueva
        page = context.pages[0] if context.pages else await context.new_page()

        start_time = time.time() #Inicia captura de tiempo

        # Navega a un sitio web
        await page.goto("https://centro.milicencia.co")
        captura_pantalla("captura1.1")
           
        
        await page.locator("main.centros_main").click(force=True)
        
        await page.locator("select#tipoCentro").select_option(label="CEA")
        await page.fill("#nombreCentro", "Olimpiapru2")
        await page.click("text=Olimpiapru2")
        await page.get_by_role("button", name=" Seleccionar ").click()
        captura_pantalla("captura1.2")
        #await page.wait_for_selector("# Comprar PIN")


        

        await page.locator("//a[text()=' Comprar PIN']").click()
        
        
        
        await page.get_by_role("radio", name="Hombre").click()
        await page.fill("#day", "15")
        await page.fill("#month", "03")
        await page.fill("#year", "1990")
        await page.click("text=Siguiente")
        await page.click("text=Primera vez o licencia adicional")
        await page.click("text=Siguiente")
        await page.click("text=Motos de más 125c.c.")
        captura_pantalla("captura1.3")
        
        
        
        await page.click("text=Siguiente")
        
        await page.fill("#email", "einar.automatizacion@yopmail.com")
        await page.fill("#celular", "3142666698")
        await page.fill("#nombres", "Einar PDP")
        await page.fill("#apellidos", "Cea Centro")
        await page.locator("select#tipoDocumento").select_option("2: 1")
        await page.fill("#documento", "11223399")
        
        #einar1
        await page.locator("span.slider").click()
        await page.wait_for_timeout(1000)
        await asyncio.sleep(5)
        captura_pantalla("captura1.4")
        #einar1fin



        await page.click("text=Siguiente")
        

        page.set_default_timeout(30000)  # 5 segundos
        

        # Formulario factura electrónica

        await page.fill("#correoFE", "einar.automatizacion@yopmail.com")
        await page.fill("#nombresFE", "Einar Prueba")
        await page.fill("#apellidosFE", "FE")
        await page.locator("#tipoDocumentoFE").click()
        await page.locator("#tipoDocumentoFE").select_option(label="Nit")
        await page.fill("#documentoFE", "999999999")
        captura_pantalla("captura1.5")


        await page.click("text=Siguiente")

                
        await page.click("text= Pago único de")
        captura_pantalla("captura1.6")
        
        await page.click("text=Siguiente")
        await page.locator("label:text('Efectivo')").click()
        await page.locator("label:text('Punto Pago')").click()
        await asyncio.sleep(4)
        captura_pantalla("captura1.7")
        
        
        await page.click("text=Continuar")
       
        
        
        
        await page.locator("label:text('Acepto los términos y condiciones')").click()
        await page.click("text= Generar referencia ")
        captura_pantalla("captura1.8")
        
        await asyncio.sleep(15)
        
        

        # CAPTURA DEL PIN DESDE CONFIRMACIÓN DE COMPRA
        # -----------------------------------------------------
        pin_encontrado = None

        try:
            pin_texto = await page.locator("h3:has-text('PIN:')").inner_text()
            pin_encontrado = pin_texto.split("PIN:")[-1].strip()
            print(f"🔑 PIN capturado desde confirmación de compra: {pin_encontrado}")
        except Exception as e:
            print(f"❌ No se pudo capturar el PIN desde la confirmación: {e}")
        captura_pantalla("captura1.9")
       
        await asyncio.sleep(5)
        await page.click("text=Volver al inicio")
        await page.click("text= Consulta de estado del PIN")
        await page.locator("#tipoDocumento").select_option(label="Cédula de Ciudadanía")
        await page.fill("#documentoActual", "11223399")
        # Obtener fecha actual en formato deseado
        fecha_actual = datetime.datetime.now().strftime("%d-%m-%y")  # Ejemplo: 2026-03-10
        # Llenar un campo con la fecha actual
        await page.fill("#fechaCompra", fecha_actual)
       

        await page.click("text=Continuar")

                # VISUALIZACIÓN DE CORREO - YOPMAIL 
       

        yopmail_browser = await p.chromium.launch(
            headless=False,
            args=["--start-maximized"]
        )

        yopmail_context = await yopmail_browser.new_context(
            viewport={"width": 1420, "height": 900}
)

        yopmail_page = await yopmail_context.new_page()

        await yopmail_page.goto("https://yopmail.com/es/", wait_until="domcontentloaded")
        await yopmail_page.fill("#login", "einar.automatizacion")
        await yopmail_page.keyboard.press("Enter")

        inicio_visualizacion = time.time()
        while time.time() - inicio_visualizacion < 20:
            await yopmail_page.wait_for_timeout(4000)
            await yopmail_page.keyboard.press("F5")

        await asyncio.sleep(4)
        captura_pantalla("captura2.0")

        await yopmail_context.close()
        await yopmail_browser.close()

        tiempo_total = time.time() - start_time #Finaliza captura de tiempos
        print(f"⏱️ Tiempo total    : {tiempo_total:.2f} segundos") #Imprime tiempos en consola
        captura_pantalla("captura2.1")


       

                # === Función para generar PDF con portada desde archivo ===
        def generar_pdf_con_portada(carpeta="screenshot/Pin_pdp_cea_centro", archivo_pdf="Evidencias.pdf", archivo_texto="portada.txt"):
            imagenes = [os.path.join(carpeta, f) for f in os.listdir(carpeta) if f.endswith(".png")]
            imagenes.sort()
            
            if imagenes:
                # Leer líneas de texto desde archivo
                if os.path.exists(archivo_texto):
                    with open(archivo_texto, "r", encoding="utf-8") as f:
                        lineas = [line.strip() for line in f.readlines() if line.strip()]
                else:
                    lineas = ["Evidencias de Pin PDP CEA Centro"] #Titulo del PDF
                lineas.append("")        
                # Agregar fecha/hora automáticamente
                lineas.append("Fecha: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                lineas.append("") 
                lineas.append(f" Tiempo total : {tiempo_total:.2f} segundos")

                
        
                # Crear portada en blanco
                ancho, alto = 1450, 900
                portada = Image.new("RGB", (ancho, alto), color="white")
                draw = ImageDraw.Draw(portada)


        
                try:
                    font_titulo = ImageFont.truetype("arial.ttf", 60)
                    font_texto = ImageFont.truetype("arial.ttf", 45)
                except OSError:
                    font_titulo = ImageFont.load_default()
                    font_texto = ImageFont.load_default()
        
                # Dibujar cada línea en la portada
                y = 100
                for i, linea in enumerate(lineas):
                    font = font_titulo if i == 0 else font_texto
                    bbox = draw.textbbox((0, 0), linea, font=font)
                    w = bbox[2] - bbox[0]
                    x = (ancho - w) // 2
                    draw.text((x, y), linea, fill="black", font=font)
                    y += 60
        
                portada = portada.convert("RGB")
                resto = [Image.open(img).convert("RGB") for img in imagenes]
        
                archivo_final = os.path.join(carpeta, archivo_pdf)
                portada.save(archivo_final, save_all=True, append_images=resto)
                print(f"📄 PDF generado con portada: {archivo_final}")
            else:
                print("⚠️ No se encontraron imágenes para unir en PDF.")

                # Generar PDF con todas las capturas y portada personalizada
        generar_pdf_con_portada()

        await asyncio.sleep(10)
                
        await context.close()
        

asyncio.run(main())
