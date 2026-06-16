import socket
import struct
import pickle
from typing import Optional, Any

from .constants import HEADER_SIZE, PROTOCOL_VERSION, MESSAGE_SCHEMA




def validate_message(message: dict) -> tuple[bool, str]:
    """
    Valida un mensaje contra el diccionario maestro.
    
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(message, dict):
        return False, "El mensaje debe ser un diccionario"
    
    if "type" not in message:
        return False, "El mensaje no tiene campo 'type'"
    
    msg_type = message["type"]
    
    if msg_type not in MESSAGE_SCHEMA:
        # Tipos no registrados (como CHAT) se permiten pero se registran
        print(f"Advertencia: Tipo de mensaje no registrado: {msg_type}")
        return True, ""
    
    schema = MESSAGE_SCHEMA[msg_type]
    
    # Verificar campos requeridos
    required = schema.get("required", [])
    missing = [f for f in required if f not in message]
    if missing:
        return False, f"Campos requeridos ausentes: {missing}"
    
    return True, ""


def pack_message(data: dict) -> bytes:
    """
    Empaqueta un mensaje con header de 10 bytes.
    
    Formato: [4 bytes: longitud] [4 bytes: tipo_hash] [2 bytes: version] + payload
    """

    
    pickled = pickle.dumps(data)
    length = len(pickled)
    
    # Calcular hash del tipo para identificar rápido
    msg_type = data.get("type", "UNKNOWN")
    type_hash = hash(msg_type) & 0xFFFFFFFF
    
    # Flags: versión en bits bajos (0-7)
    flags = PROTOCOL_VERSION
    
    header = struct.pack('>I I H', length, type_hash, flags)
    
    return header + pickled


def unpack_message(sock, timeout=None):
    from .transport import recv_exact
    
    original_timeout = sock.gettimeout()
    
    try:
        if timeout is not None:
            sock.settimeout(timeout)
        
        # Leer header de 10 bytes
        header = recv_exact(sock, HEADER_SIZE)
        if header is None:
            return None, "Header incompleto"
        
        length, type_hash, flags = struct.unpack('>I I H', header)
        
        
        version = flags & 0xFF
        if version != PROTOCOL_VERSION:
            return None, f"Versión no soportada: {version}"
        
        # Validar tamaño (máximo 10MB)
        if length > 10_000_000:
            return None, f"Mensaje demasiado grande: {length} bytes"
        
       
        payload = recv_exact(sock, length)
        if payload is None:
            return None, "Payload incompleto"
        
        
        message = pickle.loads(payload)
        
     
        valid, error = validate_message(message)
        if not valid:
            return None, error
        
        return message, None
        
    except socket.timeout:
        return None, "Timeout"
    except Exception as e:
        return None, str(e)
    finally:
        if timeout is not None:
            sock.settimeout(original_timeout)


