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
        """Envía datos como un bloque atómico clásico de 4 bytes."""
        try:
            import pickle
            import struct
            
            pickled = pickle.dumps(data)
            length = len(pickled)
            
            if length > self.config.MAX_MESSAGE_SIZE:
                raise ValueError(f"Mensaje demasiado grande: {length} bytes")
            
            # Header de 4 bytes (Big-endian) con el tamaño exacto del pickle
            header = struct.pack('>I', length)
            sock.sendall(header)
            sock.sendall(pickled)
            
            logger.debug(f"Mensaje enviado con éxito: {length} bytes")
            return True
        except Exception as e:
            logger.error(f"Error en send_atomic: {e}")
            return False
    
    def recv_atomic(self, sock: socket.socket, timeout: Optional[int] = None) -> Optional[Any]:
        """Recibe un mensaje completo leyendo estrictamente el header de 4 bytes."""
        original_timeout = sock.gettimeout()
        try:
            if timeout is not None:
                sock.settimeout(timeout)
            
            # Forzamos a que lea directamente usando el método legacy de 4 bytes
            return self._recv_legacy(sock)
            
        except socket.timeout:
            raise TimeoutException("Timeout esperando datos en el socket")
        except Exception as e:
            logger.error(f"Error en recv_atomic: {e}")
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