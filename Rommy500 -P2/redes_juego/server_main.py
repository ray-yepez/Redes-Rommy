
import time

def run_server(server_rummy,cliente_rummy,max_jugadores, nombre_jugador="Host", nombre_sala="Sala1",un_juego=None):
    server = server_rummy
    server.max_jugadores = max_jugadores
    server.nombre_host = nombre_jugador  # Guardar nombre en el servidor
    server.nombre_partida = nombre_sala  # Guardar nombre de la sala en el servidor
    server.un_juego = un_juego
    server.iniciar_servidor()
    time.sleep(1)
    cliente_host = cliente_rummy
    cliente_host.un_juego = un_juego
    if cliente_host.conectar_a_servidor('127.0.0.1', nombre_jugador=nombre_jugador):
        print("Host conectado al servidor local")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Cerrando servidor y cliente")
        finally:
            cliente_host.desconectar()
            server.desconectar()
            print("Servidor y cliente cerrados correctamente")
    else:
        print("Error: No se pudo conectar al servidor local")
        server.desconectar()

if __name__ == "__main__":
    run_server(7)  # Valor por defecto para pruebas

