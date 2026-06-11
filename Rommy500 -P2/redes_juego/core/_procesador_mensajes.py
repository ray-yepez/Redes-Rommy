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
            except OSError as e:
                # Socket cerrado o inválido
                print(f"Socket cerrado para cliente {id_jugador}: {e}")
                break
            except Exception as e:
                print(f"Error recibiendo datos de cliente {id_jugador}: {e}")
                break
                
            if not data:
                # Cliente cerró conexión normalmente
                print(f"Cliente {id_jugador} cerró la conexión")
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
                        self.cola_mensajes.append((id_jugador, mensaje, socket_cliente))
                except json.JSONDecodeError as e:
                    logger.error(f"JSON inválido de cliente {id_jugador}: {e}")
                    continue
        except Exception as e:
           logger.error(f"Error en recepción de cliente {id_jugador}: {e}")
        finally:
        # Notificar desconexión solo si el id_jugador es válido y el servidor sigue ejecutándose
           if id_jugador is not None and self.ejecutandose:
             print(f"Cliente {id_jugador} desconectado, enviando notificación...")
             with self.candado:
                 self.cola_mensajes.append((id_jugador, {'type': 'ClienteDesconectado'}, socket_cliente))