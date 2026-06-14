"""Módulo interno para envío y difusión de mensajes"""

import json

class MensajeriaMixin:
    """Mixin con métodos para enviar y difundir mensajes a clientes"""
    
    def difundir(self, mensaje):
        """Envía un mensaje a todos los clientes conectados"""
        for cliente in self.clientes:
            try: 
                cliente['socket'].send((json.dumps(mensaje) + '\n').encode('utf-8'))
            except Exception as e:
                print(f"Error al enviar mensaje al cliente {cliente['id']}: {e}")
    
    def difundir_excepcion(self, id_jugador, mensaje):
        """Envía un mensaje a todos los clientes excepto al especificado"""
        for cliente in self.clientes:
            if cliente['id'] != id_jugador:  # No enviar al emisor
                try: 
                    cliente['socket'].send((json.dumps(mensaje) + '\n').encode('utf-8'))
                except Exception as e:
                    print(f"Error al enviar mensaje al cliente {cliente['id']}: {e}")

    def enviar_a_cliente(self, id_jugador, mensaje):
        """Envía un mensaje a un cliente específico"""
        for cliente in self.clientes:
            if cliente['id'] == id_jugador:
                try:
                    cliente['socket'].sendall((json.dumps(mensaje) + '\n').encode('utf-8'))
                except Exception as e:
                    print(f"Error al enviar mensaje al cliente {id_jugador}: {e}")
                    print(self.jugadores_desconectados)
    

