import logging
import os
from datetime import datetime

# Crear carpeta log en la raíz si no existe
LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 🔹 Limpiar logs antiguos (mantener solo los 5 más recientes)
def cleanup_logs(log_dir, max_files=5):
    files = [
        os.path.join(log_dir, f)
        for f in os.listdir(log_dir)
        if f.endswith(".log")
    ]

    # Ordenar por fecha de modificación (más antiguos primero)
    files.sort(key=os.path.getmtime)

    # Eliminar los más antiguos si hay más de max_files
    while len(files) >= max_files:
        oldest = files.pop(0)
        try:
            os.remove(oldest)
        except Exception as e:
            print(f"No se pudo eliminar {oldest}: {e}")

# Ejecutar limpieza antes de crear el nuevo log
cleanup_logs(LOG_DIR, max_files=5)

# Crear nombre único basado en fecha y hora de ejecución
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"{timestamp}.log"
LOG_FILE = os.path.join(LOG_DIR, log_filename)

def get_logger(name="log") -> logging.Logger:
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

    # Handler para archivo
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