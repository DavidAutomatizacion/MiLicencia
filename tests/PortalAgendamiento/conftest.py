# d:\Automatizaciones\ABIS_FACIAL\conftest.py
import requests, pytest, sys, os
from pathlib import Path
from utils.logger import get_logger

# Agregar rutas
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "web"))

# Declarar variables globales
usuarioCRC = os.getenv("USUARIO_CRC")
passwordCRC = os.getenv("PASSWORD_CRC")
usuarioCEA = os.getenv("USUARIO_CEA")
passwordCEA = os.getenv("PASSWORD_CEA")
correoOlimpia = os.getenv("CORREO_OLIMPIA")
tipoCentro = os.getenv("TIPO_CENTRO")


@pytest.fixture
def logger():
    """Logger para tests"""
    return get_logger("MI_LICENCIA_AGENDAMIENTO")


@pytest.fixture
def credenciales():
    return {
        "usuario": usuarioCRC,
        "contraseña": passwordCRC,
        "tipoCentro": tipoCentro
    }

@pytest.fixture(scope="session")
def portal_logeado(browser, credenciales):
    context = browser.new_context()
    page = context.new_page()

    # Ir a login
    page.goto("https://olnlbprewtssi01:7000/")

    # Llenar formulario
    page.fill('#usuario', credenciales["usuario"])
    page.fill('#password', credenciales["contraseña"])
    page.select_option("#tipocentro", credenciales["tipoCentro"])

    # Enviar
    page.click('button[type="submit"]')

    # Esperar que login termine (IMPORTANTE)
    page.wait_for_url("**/dashboard")

    yield page

    context.close()