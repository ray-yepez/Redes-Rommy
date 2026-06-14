import time

def run_server(server_rummy, cliente_rummy, max_jugadores, nombre_jugador="Host", nombre_sala="Sala1", un_juego=None):
    server = server_rummy
    server.max_jugadores = max_jugadores
    server.nombre_host = nombre_jugador
    server.nombre_partida = nombre_sala
    server.un_juego = un_juego

    # Bandera para controlar el ciclo del servidor
    server.activo = True

    server.iniciar_servidor()
    time.sleep(1)

    cliente_host = cliente_rummy
    cliente_host.un_juego = un_juego
    cliente_host.activo = True

    if cliente_host.conectar_a_servidor("127.0.0.1", nombre_jugador=nombre_jugador):
        print("Host conectado al servidor local")

        try:
            while getattr(server, "activo", True) and getattr(cliente_host, "activo", True):
                time.sleep(1)

        except KeyboardInterrupt:
            print("Cerrando servidor y cliente")

        finally:
            try:
                cliente_host.activo = False
                cliente_host.desconectar()
            except Exception as e:
                print(f"Error cerrando cliente host: {e}")

            try:
                server.activo = False
                server.desconectar()
            except Exception as e:
                print(f"Error cerrando servidor: {e}")

            print("Servidor y cliente cerrados correctamente")

    else:
        print("Error: No se pudo conectar al servidor local")
        try:
            server.activo = False
            server.desconectar()
        except Exception as e:
            print(f"Error cerrando servidor tras fallo: {e}")


if __name__ == "__main__":
    print("Este archivo debe ejecutarse desde controladores.py con sus argumentos reales.")

