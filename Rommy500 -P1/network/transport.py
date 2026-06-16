import socket
import struct
import pickle
import logging
from typing import Optional, Any
# pyrefly: ignore [missing-import]
from .config import DEFAULT_CONFIG
# pyrefly: ignore [missing-import]
from .exceptions import TimeoutException, ConnectionResetException
from .constants import pack_message, unpack_message, HEADER_SIZE

logger = logging.getLogger(__name__)

class Transport:
    """Capa de transporte: envío/recepción confiable con pickle."""
    
    def __init__(self, config=None):
        
        self.config = config or DEFAULT_CONFIG
    
    def send_atomic(self, sock: socket.socket, data: Any) -> bool:
        """Envía datos con header de 10 bytes."""
        try:
            # Si es un diccionario con type, empaquetar con header nuevo
            if isinstance(data, dict) and "type" in data:
                packet = pack_message(data)
            else:
                # Fallback para mensajes antiguos (como tuplas de chat)
                import pickle
                import struct
                pickled = pickle.dumps(data)
                header = struct.pack('>I', len(pickled))
                packet = header + pickled
            
            sock.sendall(packet)
            return True
        except Exception as e:
            logger.error(f"Error en send_atomic: {e}")
            return False
    
    def recv_atomic(self, sock: socket.socket, timeout: Optional[int] = None) -> Optional[Any]:
        """Recibe un mensaje completo en formato atómico, manejando dinámicamente

        el nuevo header de 10 bytes y el antiguo de 4 bytes sin corromper el stream.
        """
        import socket
        import struct
        from .constants import PROTOCOL_VERSION, unpack_message

        original_timeout = sock.gettimeout()
        
        try:
            if timeout is not None:
                sock.settimeout(timeout)
            
            # 1. Espiamos (PEEK) los primeros 10 bytes sin removerlos del búfer de red
            header_peek = sock.recv(10, socket.MSG_PEEK)
            if len(header_peek) < 4:
                return None  # Conexión incompleta o cerrada prematuramente
            
            is_modern = False
            if len(header_peek) == 10:
                # Desempaquetamos temporalmente para verificar si coincide con el protocolo nuevo
                length, type_hash, flags = struct.unpack('>I I H', header_peek)
                version = flags & 0xFF
                if version == PROTOCOL_VERSION:
                    is_modern = True
            
            # 2. Enrutamos el flujo según el tipo de paquete detectado
            if is_modern:
                # Deja que unpack_message (de constants.py) consuma los 10 bytes completos y valide el diccionario
                message, error = unpack_message(sock, timeout)
                if error:
                    logger.error(f"Validación de paquete denegada: {error}")
                    return None
                return message
            else:
                # Es un paquete con formato antiguo (como la tupla de credenciales inicial)
                return self._recv_legacy(sock)
                
        except socket.timeout:
            return None
        except Exception as e:
            logger.error(f"Error crítico en recv_atomic: {e}")
            return None
        finally:
            if timeout is not None:
                sock.settimeout(original_timeout)

    def _recv_exact(self, sock: socket.socket, n: int) -> Optional[bytes]:
        """Recibe exactamente n bytes garantizando que no se queden fragmentos en el camino."""
        data = b''
        retries = 0
        while len(data) < n:
            try:
                chunk = sock.recv(n - len(data))
                if not chunk:
                    return None
                data += chunk
                retries = 0
            except socket.timeout:
                if len(data) == 0:
                    raise
                retries += 1
                if retries >= self.config.MAX_RECV_RETRIES:
                    raise TimeoutException("Max retries alcanzado leyendo datos parciales")
                continue
            except Exception:
                return None
        return data

    def _recv_legacy(self, sock):
        """Recibe mensaje con formato antiguo (4 bytes de header original)."""
        import pickle
        import struct
        
        # CORRECCIÓN: Leer exactamente 4 bytes que corresponden al tamaño en formato antiguo
        header = self._recv_exact(sock, 4)
        if header is None:
            return None
        
        length = struct.unpack('>I', header)[0]
        data = self._recv_exact(sock, length)
        if data is None:
            return None
        
        return pickle.loads(data)