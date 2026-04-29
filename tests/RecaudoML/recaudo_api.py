import requests
from utils.logger import get_logger

logger = get_logger("RECAUDO_PIN")

#========================================
# CREDENCIALES API
#========================================

usuarioAPI = "PruebaEs1"
contraseñaAPI = "PruebaEs1"
urlAuth = "http://olnlbpreapss01:9005/ApiProxy/api/login/authenticate"

credenciales = {
    "usuario": usuarioAPI,
    "contraseña": contraseñaAPI,
    "url_auth": urlAuth
}

#========================================
# DATOS PIN A RECAUDAR
#========================================

idCliente = 3 # CRC, 8: CEAS
tipoIdentificacion = 1 # 1: CC, 3:TI 2:CE, 5:Pasaporte
numeroIdentificacion = "23423423"
pin = "945510891211106"
fechaTransaccion = "2026-04-15T10:09:03.444Z"
idRunt = "9080701230" # PRECertificacion 9080701230
datos = {
    "url": "http://olnlbpreapss01:9005/ApiProxy/api/pines/Recaudo",
    "IdCliente": idCliente,
    "TipoIdentificacion": tipoIdentificacion, 
    "NumeroIdentificacion": numeroIdentificacion,
    "NumeroPin": pin,
    "FechaTransaccion": fechaTransaccion,
    "NumeroAutorizacion": 0,
    "ValorTransaccion": 200000,
    "IdRunt": idRunt,
    "IdConvenio": 16

}

def autenticar_api(logger, credenciales):
    logger.info("Autenticando en API...")
    usuario = credenciales["usuario"]
    contraseña = credenciales["contraseña"]
    url_auth = credenciales["url_auth"]
    payload = {
    "Username": usuario,
    "Password": contraseña
    }
    logger.info(f"Payload login: {payload}")
    headers = {
        "Content-Type": "application/json"
    }
    logger.info("Recaudando via API...")
    response = requests.post(url_auth, json=payload, headers=headers)

    logger.info(f"Código de respuesta:, {response.status_code}")
    logger.info("Respuesta del servicio:")
    logger.info(response.text)

    return response

def recaudar_pin(logger, datos):
    logger.info(f"Recaudando PIN: {datos['NumeroPin']}")
    url = datos["url"]
    #Genera el token en crudo
    response_auth = autenticar_api(logger, credenciales)
    token = response_auth.json()
    payload = {
    "IdCliente": datos["IdCliente"],
    "Data": {
        "TipoIdentificacion": datos["TipoIdentificacion"],
        "NumeroIdentificacion": datos["NumeroIdentificacion"],
        "NumeroPin": datos["NumeroPin"],
        "FechaTransaccion": datos["FechaTransaccion"],
        "NumeroAutorizacion": 0,
        "ValorTransaccion": 200000,
        "IdRunt": datos["IdRunt"],
        "IdConvenio": datos["IdConvenio"]
        }
    }
    logger.info(f"Payload: {payload}")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    logger.info("Recaudando via API...")
    response = requests.post(url, json=payload, headers=headers)

    logger.info(f"Código de respuesta:, {response.status_code}")
    logger.info("Respuesta del servicio:")
    logger.info(response.text)

    return response, url

recaudar_pin(logger, datos)

