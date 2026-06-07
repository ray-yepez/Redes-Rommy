import socket
import struct
import pickle
import logging
from typing import Optional, Any
# pyrefly: ignore [missing-import]
from .config import DEFAULT_CONFIG
# pyrefly: ignore [missing-import]
from .exceptions import TimeoutException, ConnectionResetException

logger = logging.getLogger(__name__)

class Transport:
    """Capa de transporte: envío/recepción confiable con pickle."""
    
    def __init__(self, config=None):
        self.config = config or DEFAULT_CONFIG
    
    def send_atomic(self, sock: socket.socket, data: Any) -> bool:
        """Envía datos como un bloque atómico.
        
        Formato: [4 bytes longitud big-endian][datos pickle]
        """
        try:
            pickled = pickle.dumps(data)
            length = len(pickled)
            
            if length > self.config.MAX_MESSAGE_SIZE:
                raise ValueError(f"Mensaje demasiado grande: {length} bytes (límite {self.config.MAX_MESSAGE_SIZE})")
            
            header = struct.pack('>I', length)
            sock.sendall(header)
            sock.sendall(pickled)
            
            logger.debug(f"Mensaje enviado: {length} bytes")
            return True
        except Exception as e:
            logger.error(f"Error en send_atomic: {e}")
            return False
    
    def recv_atomic(self, sock: socket.socket, timeout: Optional[int] = None) -> Optional[Any]:
        """Recibe un mensaje completo en formato atómico."""
        original_timeout = sock.gettimeout()
        
        try:
            if timeout is not None:
                sock.settimeout(timeout)
            
            # Recibir cabecera (4 bytes)
            header = self._recv_exact(sock, 4)
            if header is None:
                return None
            
            length = struct.unpack('>I', header)[0]
            
            # Recibir payload
            data = self._recv_exact(sock, length)
            if data is None:
                return None
            
            logger.debug(f"Mensaje recibido: {length} bytes")
            return pickle.loads(data)
            
        except socket.timeout:
            # Permitir que el timeout natural (idle) suba al loop principal
            raise
        except TimeoutException as e:
            logger.error(f"TimeoutException en recv_atomic: {e}")
            return None
        except Exception as e:
            logger.error(f"Error en recv_atomic: {e}")
            return None
        finally:
            if timeout is not None:
                sock.settimeout(original_timeout)
    
    def _recv_exact(self, sock: socket.socket, n: int) -> Optional[bytes]:
        """Recibe exactamente n bytes, reintentando en caso de timeout."""
        data = b''
        retries = 0
        
        while len(data) < n:
            try:
                chunk = sock.recv(n - len(data))
                if not chunk:
                    logger.warning("Socket cerrado remotamente")
                    return None
                data += chunk
                retries = 0
            except socket.timeout:
                if len(data) == 0:
                    # Si no hemos leído nada aún, es un timeout normal por inactividad
                    raise
                
                retries += 1
                logger.warning(f"Timeout de paquete roto en _recv_exact ({retries}/{self.config.MAX_RECV_RETRIES})")
                if retries >= self.config.MAX_RECV_RETRIES:
                    raise TimeoutException(f"Max retries ({self.config.MAX_RECV_RETRIES}) alcanzado leyendo datos parciales")
                continue
            except Exception as e:
                logger.error(f"Error en _recv_exact: {e}")
                return None
        
        return data
