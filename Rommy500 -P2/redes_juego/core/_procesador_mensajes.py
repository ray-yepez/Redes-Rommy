"""Módulo interno para recepción de mensajes del juego (Productor)"""

import json
from redes_juego.logging_config import logger

class ProcesadorMensajesMixin:
    """Mixin con métodos para recibir mensajes y encolarlos (Productor)"""
    
    def _manejar_cliente_mensajes(self, socket_cliente, id_jugador):
        """Lee del socket y encola (id_jugador, mensaje, socket_cliente). No procesa la lógica."""
        buffer = ""
        try:
            while self.ejecutandose:
                try:
                    data = socket_cliente.recv(65536)
                except OSError:
                    break
                if not data:
                    break

                buffer += data.decode('utf-8')

                while '\n' in buffer:
                    linea, buffer = buffer.split('\n', 1)
                    linea = linea.strip()
                    if not linea:
                        continue
                    try:
                        mensaje = json.loads(linea)
                        with self.candado:
                            # Encolar (id_jugador, mensaje, socket) para que el router tenga el socket
                            self.cola_mensajes.append((id_jugador, mensaje, socket_cliente))
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON inválido de cliente {id_jugador}: {e}")
                        continue
        except Exception as e:
            logger.error(f"Error en recepción de cliente {id_jugador}: {e}")
