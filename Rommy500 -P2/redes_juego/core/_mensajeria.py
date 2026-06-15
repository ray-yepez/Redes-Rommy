"""Módulo interno para envío y difusión de mensajes con header de 10 bytes"""

from redes_juego.packets import pack_message

class MensajeriaMixin:
    """Mixin con métodos para enviar y difundir mensajes a clientes"""
    
    def difundir(self, mensaje):
        """Envía un mensaje a todos los clientes conectados con header de 10 bytes"""
        packet = pack_message(mensaje)
        for cliente in self.clientes:
            if cliente.get('status') != 'desconectado' and cliente.get('socket'):
                try:
                    cliente['socket'].sendall(packet)
                except Exception as e:
                    print(f"[Redes] No se pudo enviar difusión al ID {cliente.get('id')}: {e}")
    
    def difundir_excepcion(self, id_jugador, mensaje):
        """Envía un mensaje a todos los clientes excepto al especificado"""
        packet = pack_message(mensaje)
        for cliente in self.clientes:
            if cliente.get('id') != id_jugador and cliente.get('status') != 'desconectado':
                try:
                    cliente['socket'].sendall(packet)
                except Exception as e:
                    print(f"Error al enviar mensaje al cliente {cliente.get('id')}: {e}")

    def enviar_a_cliente(self, id_jugador, mensaje):
        """Envía un mensaje a un cliente específico con header de 10 bytes"""
        packet = pack_message(mensaje)
        for cliente in self.clientes:
            if cliente.get('id') == id_jugador:
                try:
                    cliente['socket'].sendall(packet)
                except Exception as e:
                    print(f"Error al enviar mensaje al cliente {id_jugador}: {e}")