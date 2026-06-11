"""Módulo interno para envío y difusión de mensajes"""

import json
from redes_juego.protocolo.codec import TCPCodec, MensajeError
from redes_juego.logging_config import logger

class MensajeriaMixin:
    """Mixin con métodos para enviar y difundir mensajes a clientes"""
    
    def difundir(self, mensaje):
        """Envía un mensaje a todos los clientes conectados"""
        for cliente in self.clientes:
            try:
                codec = TCPCodec(cliente['socket'])
                codec.send(mensaje)
            except MensajeError as e:
                logger.error(f"Error al enviar mensaje al cliente {cliente['id']}: {e}")
            except Exception as e:
                logger.error(f"Excepción inesperada al difundir al cliente {cliente['id']}: {e}")
    
    def difundir_excepcion(self, id_jugador, mensaje):
        """Envía un mensaje a todos los clientes excepto al especificado"""
        for cliente in self.clientes:
            if cliente['id'] != id_jugador:  # No enviar al emisor
                try: 
                    codec = TCPCodec(cliente['socket'])
                    codec.send(mensaje)
                except MensajeError as e:
                    logger.error(f"Error al enviar mensaje al cliente {cliente['id']}: {e}")
                except Exception as e:
                    logger.error(f"Excepción inesperada al difundir al cliente {cliente['id']}: {e}")

    def enviar_a_cliente(self, id_jugador, mensaje):
        """Envía un mensaje a un cliente específico"""
        for cliente in self.clientes:
            if cliente['id'] == id_jugador:
                try:
                    codec = TCPCodec(cliente['socket'])
                    codec.send(mensaje)
                except MensajeError as e:
                    logger.error(f"Error al enviar mensaje al cliente {id_jugador}: {e}")
                    logger.debug(f"Jugadores desconectados actuales: {self.jugadores_desconectados}")
                except Exception as e:
                    logger.error(f"Excepción inesperada al enviar al cliente {id_jugador}: {e}")
