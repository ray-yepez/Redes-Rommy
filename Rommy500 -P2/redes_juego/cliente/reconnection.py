"""Manejador de reconexión del cliente"""

import time

class ReconnectionManager:
    def __init__(self, client_instance):
        self.client = client_instance

    def intentar_reconexion(self, ip_servidor, intentos=5, espera=3):
        """
        Intenta reconectar automáticamente al servidor usando el id_jugador anterior.
        """
        # Cargar el ID local antes de intentar reconectar
        id_local = self.client.cargar_id_local()
        if id_local:
            self.client.id_jugador = id_local
            
        for intento in range(intentos):
            print(f"Intentando reconectar a {ip_servidor}... (Intento {intento + 1}/{intentos})")
            exito = self.client.conectar_a_servidor(ip_servidor, id_jugador_reconectar=self.client.id_jugador)
            if exito:
                print("Reconexión exitosa.")
                return True
            time.sleep(espera)
            
        print("No se pudo reconectar después de varios intentos.")
        return False
