
import time
def run_client(cliente_rummy=None, nombre_jugador=None,un_juego=None,ip_servidor=None):
    client = cliente_rummy 
    client.un_juego = un_juego

    id_local = client.cargar_id_local()
    nombre_cliente = nombre_jugador
    # Solo reconectar si el ID es válido
    if id_local is not None and id_local > 0:
        print(f"ID local encontrado: {id_local}. Intentando reconexión...")
    else:
        print("No hay ID local válido. Conectando como nuevo jugador...")
        id_local = None
        client.guardar_nombre_local(nombre_cliente)    # Guarda el nombre localmente

    if ip_servidor and client.conectar_a_servidor(
        ip_servidor, id_jugador_reconectar=id_local, nombre_jugador=nombre_cliente
    ): 
        try:
            while True:
                if not client.conectado:
                    print("Desconectado del servidor. Intentando reconectar...")
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            print("Cliente desconectándose...")
        finally:
            client.desconectar()
    else:
        print("Fallo al conectar con el servidor.")

if __name__ == "__main__":
    run_client()

