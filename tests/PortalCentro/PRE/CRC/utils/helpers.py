import random, os, pyautogui, datetime, time, re
from faker import Faker
from PIL import Image, ImageDraw, ImageFont
import img2pdf
def generar_documento(maxDigitos=10):
    """Genera un número de documento aleatorio con 10 dígitos evitando 0 como primer numero."""
    faker = Faker("es_ES")
    maxDigitos = maxDigitos - 1 
    primer_numero = random.randint(1, 9) # Genera 1 numero aleatorio del 1 al 9
    resto = faker.random_number(digits=maxDigitos, fix_len=True) # Genera 9 numeros aleatorios
    resultado = str(primer_numero) + str(resto)
    return resultado


# === Función para capturar pantalla completa ===
async def captura_pantalla(page, nombre_base, carpeta):
    import os
    from datetime import datetime

    os.makedirs(carpeta, exist_ok=True)

    nombre = f"{nombre_base}_{datetime.now().strftime('%H-%M-%S')}"
    ruta = os.path.join(carpeta, f"{nombre}.png")

    await page.screenshot(path=ruta, full_page=True)

    print(f"📸 Captura guardada: {ruta}")

# === Función para generar PDF con portada desde archivo ===


def generar_pdf_con_portada(tiempo_total, carpeta=None, archivo_pdf=None, archivo_texto=None, logger=None):
    imagenes = [os.path.join(carpeta, f) for f in os.listdir(carpeta) if f.endswith(".png")]
    imagenes.sort()

    if archivo_pdf is None:
        archivo_pdf = "Evidencias.pdf"
    if archivo_texto is None:
        archivo_texto = "portada.txt"

    if not imagenes:
        if logger:
            logger.warning("⚠️ No se encontraron imágenes para unir en PDF.")
        return

    # Leer texto
    if os.path.exists(archivo_texto):
        with open(archivo_texto, "r", encoding="utf-8") as f:
            lineas = [line.strip() for line in f.readlines() if line.strip()]
    else:
        lineas = ["Evidencias de Pin PDP CEA Centro"]

    lineas.append("")
    lineas.append("Fecha: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    lineas.append("")
    lineas.append(f"Tiempo total: {tiempo_total:.2f} segundos")

    # Crear portada
    ancho, alto = 1450, 900
    portada = Image.new("RGB", (ancho, alto), "white")
    draw = ImageDraw.Draw(portada)

    try:
        font_titulo = ImageFont.truetype("arial.ttf", 60)
        font_texto = ImageFont.truetype("arial.ttf", 45)
    except:
        font_titulo = ImageFont.load_default()
        font_texto = ImageFont.load_default()

    y = 100
    for i, linea in enumerate(lineas):
        font = font_titulo if i == 0 else font_texto
        bbox = draw.textbbox((0, 0), linea, font=font)
        w = bbox[2] - bbox[0]
        x = (ancho - w) // 2
        draw.text((x, y), linea, fill="black", font=font)
        y += 60

    # Guardar portada temporal
    portada_path = os.path.join(carpeta, "portada_temp.png")
    portada.save(portada_path)

    # Lista completa (portada + imágenes)
    todas = [portada_path] + imagenes

    archivo_final = os.path.join(carpeta, archivo_pdf)

    # Crear PDF con img2pdf (SIN JPEG issues)
    with open(archivo_final, "wb") as f:
        f.write(img2pdf.convert(todas))

    # Limpiar portada temporal
    os.remove(portada_path)

    if logger:
        logger.info(f"📄 PDF generado con portada: {archivo_final}")
    else:
        print(f"📄 PDF generado con portada: {archivo_final}")

        # Generar PDF con todas las capturas y portada personalizada


async def obtener_pin_yopmail(p, correo, timeout=20, logger=None):
    browser = await p.chromium.launch(
        headless=False,
        args=["--start-maximized"]
    )

    context = await browser.new_context(
        viewport={"width": 1420, "height": 900}
    )

    page = await context.new_page()

    await page.goto("https://yopmail.com/es/", wait_until="domcontentloaded")
    await page.fill("#login", correo)
    await page.keyboard.press("Enter")

    inicio = time.time()
    pin_encontrado = None

    while time.time() - inicio < timeout:

        await page.wait_for_timeout(3000)

        try:
            inbox = page.frame(name="ifinbox")

            if inbox:
                correos = await inbox.locator(".m").all()

                for correo_item in correos:
                    try:
                        remitente = (await correo_item.locator(".lmf").inner_text()).strip().lower()
                        asunto = (await correo_item.locator(".lms").inner_text()).strip().lower()

                        # 🔎 ajusta este filtro si quieres
                        if "pin" in asunto or "olimpia" in remitente:

                            await correo_item.locator("button.lm").click()

                            iframe = page.frame(name="ifmail")

                            if iframe:
                                await iframe.wait_for_selector("body", timeout=5000)

                                texto = await iframe.locator("body").inner_text()

                                # 🔥 detectar PIN (6 dígitos, ajustable)
                                match = re.search(r"\b\d{4,8}\b", texto)

                                if match:
                                    pin_encontrado = match.group()

                                    if logger:
                                        logger.info(f"✅ PIN encontrado: {pin_encontrado}")
                                    else:
                                        print(f"✅ PIN encontrado: {pin_encontrado}")

                                    captura_pantalla("captura13")

                                    await context.close()
                                    await browser.close()

                                    return pin_encontrado

                    except Exception as e:
                        if logger:
                            logger.warning(f"Error leyendo correo: {e}")
                        else:
                            print("Error leyendo correo:", e)

        except Exception as e:
            if logger:
                logger.warning(f"Error en inbox: {e}")

        # 🔁 refrescar
        await page.reload()

    # ❌ no encontrado
    if logger:
        logger.warning("❌ No se encontró el PIN en el tiempo esperado")
    else:
        print("❌ No se encontró el PIN")

    captura_pantalla("captura14")

    await context.close()
    await browser.close()

    return None