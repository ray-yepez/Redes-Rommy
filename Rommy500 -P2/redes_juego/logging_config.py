import logging
import sys

def setup_logging():
    """
    Configura el sistema de logging estándar de Python para la aplicación.
    Establece un formato unificado para todos los subsistemas (redes, lógica, interfaz).
    """
    # Formato: [TIEMPO] [NIVEL] [MODULO] - Mensaje
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%H:%M:%S'
    )

    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Handler opcional para archivo si es necesario en el futuro
    # file_handler = logging.FileHandler('rommy_server.log', encoding='utf-8')
    # file_handler.setFormatter(formatter)

    # Configuración del logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)  # Cambiar a DEBUG para ver más detalles
    
    # Limpiar handlers existentes por si se llama múltiples veces
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.addHandler(console_handler)
    # root_logger.addHandler(file_handler)

    return root_logger

# Se puede importar este logger ya configurado
logger = logging.getLogger("redes")
