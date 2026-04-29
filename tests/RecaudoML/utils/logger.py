import logging
import os
from datetime import datetime

# Crear carpeta log en la raíz si no existe
LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Crear nombre único basado en fecha y hora de ejecución
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"{timestamp}.log"
LOG_FILE = os.path.join(LOG_DIR, log_filename)

def get_logger(name: str) -> logging.Logger:
    """
    Retorna un logger configurado para escribir en un archivo
    único por ejecución, más salida en consola.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Evitar agregar handlers duplicados si el logger ya está configurado
    if logger.handlers:
        return logger

    # Formato del log
    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    # Handler para archivo (sin rotación porque ahora es uno por ejecución)
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Agregar handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger