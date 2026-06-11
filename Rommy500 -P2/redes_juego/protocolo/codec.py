import json
import socket
from typing import List

class MensajeError(Exception):
    """Excepción lanzada cuando hay un error en la serialización o deserialización de un mensaje."""
    pass

class TCPCodec:
    """
    Buffer acumulador para streams TCP con delimitador '\\n'.
    Maneja la serialización y envío seguro de mensajes JSON a través de sockets TCP.
    """
    
    def __init__(self, socket_obj: socket.socket):
        self._socket = socket_obj
        self._buffer = ""
    
    def send(self, mensaje_dict: dict) -> None:
        """
        Codifica un diccionario como JSON, añade el delimitador y lo envía por el socket.
        """
        try:
            # Asegurarse de que el diccionario es serializable
            json_str = json.dumps(mensaje_dict)
            data = (json_str + '\n').encode('utf-8')
            self._socket.sendall(data)
        except Exception as e:
            raise MensajeError(f"Error al enviar mensaje: {e}")
    
    def receive_chunk(self, chunk_size: int = 65536) -> List[dict]:
        """
        Lee datos del socket, los acumula en el buffer y extrae todos los mensajes JSON completos.
        Debe llamarse en un ciclo mientras la conexión esté activa.
        
        Retorna:
            Una lista de diccionarios (mensajes) decodificados.
        """
        try:
            chunk = self._socket.recv(chunk_size)
            if not chunk:
                # Conexión cerrada
                return []
                
            self._buffer += chunk.decode('utf-8')
        except BlockingIOError:
            # Socket no bloqueante sin datos
            return []
        except socket.timeout:
            return []
        except OSError as e:
            raise MensajeError(f"Error de socket al recibir: {e}")
            
        mensajes = []
        while '\n' in self._buffer:
            linea, self._buffer = self._buffer.split('\n', 1)
            linea = linea.strip()
            if not linea:
                continue
            try:
                mensaje = json.loads(linea)
                mensajes.append(mensaje)
            except json.JSONDecodeError as e:
                # Se loguea el error pero se descarta el mensaje corrupto
                import logging
                logging.getLogger("redes.protocolo").error(f"JSON inválido recibido: {e} | {linea[:100]}")
                continue
                
        return mensajes
