import os
import sys
import importlib.util

def importar_desde_carpeta(nombre_archivo, nombre_clase=None, nombre_carpeta="logica_juego"):
    """
    Importa un módulo, clase o devuelve la ruta de un recurso desde una carpeta hermana.
    
    Args:
        nombre_carpeta (str): Nombre de la carpeta raíz (hermana a la actual)
        nombre_archivo (str): Ruta relativa del archivo (con o sin extensión)
        nombre_clase (str, optional): Nombre de la clase específica a importar (si es módulo)
    
    Returns:
        Módulo, clase o ruta absoluta del recurso.
    """
    # Ruta base
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    ruta_carpeta = os.path.join(parent_dir, nombre_carpeta)

    if not os.path.exists(ruta_carpeta):
        raise ImportError(f"La carpeta '{nombre_carpeta}' no existe en {parent_dir}")

    ruta_archivo = os.path.join(ruta_carpeta, nombre_archivo)

    if not os.path.exists(ruta_archivo):
        raise ImportError(f"No se encontró el archivo '{ruta_archivo}'")

    # Detectar extensión
    extension = os.path.splitext(ruta_archivo)[1].lower()

    if extension == ".py" or extension == "":
        # Importar como módulo Python
        nombre_modulo = os.path.splitext(os.path.basename(ruta_archivo))[0]
        spec = importlib.util.spec_from_file_location(nombre_modulo, ruta_archivo)
        if spec is None or spec.loader is None:
            raise ImportError(f"No se pudo cargar el módulo desde {ruta_archivo}")
        modulo = importlib.util.module_from_spec(spec)
        sys.modules[nombre_modulo] = modulo
        spec.loader.exec_module(modulo)

        if nombre_clase:
            if hasattr(modulo, nombre_clase):
                return getattr(modulo, nombre_clase)
            else:
                raise ImportError(f"La clase '{nombre_clase}' no existe en {ruta_archivo}")
        return modulo
    else:
        # Es un recurso → devolver ruta absoluta
        return ruta_archivo
