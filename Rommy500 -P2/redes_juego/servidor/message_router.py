"""Enrutador central de mensajes del servidor (Consumidor)"""

import threading
from redes_juego.protocolo.mensajes import MessageType
from redes_juego.logging_config import logger
import copy

from redes_juego import archivo_de_importaciones

importar_desde_carpeta = archivo_de_importaciones.importar_desde_carpeta
Carta = importar_desde_carpeta(
    nombre_archivo="cartas_interfaz.py",
    nombre_clase="Cartas_interfaz",
    nombre_carpeta="logica_interfaz",
)

class MessageRouter:
    def __init__(self, server_instance):
        self.server = server_instance

    def route_message(self, id_jugador, mensaje, socket_cliente):
        import time
        
        # Registrar actividad para el heartbeat
        existing = next((c for c in self.server.clientes if c.get('id') == id_jugador), None)
        if existing:
            existing['last_activity'] = time.time()

        if mensaje.get('type') == 'Ping':
            return # Es solo un heartbeat, no procesar más
        
        if mensaje.get('type') == 'ClienteDesconectado':
            print(f"Mensaje del cliente: {mensaje}")
            # Guardar datos del jugador desconectado
            self.server.jugadores_desconectados[id_jugador] = {
                'estado_juego': self.server.estado_juego,
                'nombre': self.server.clientes[id_jugador-1]['nombre'] if id_jugador-1 < len(self.server.clientes) else mensaje.get('nombre', '')
            }
            print(self.server.clientes)


            self.server.difundir({
                'type': 'JugadorDesconectado',
                'id_jugador': id_jugador,
                'TotalJugadores': len(self.server.clientes),
                "nombre": self.server.clientes[id_jugador-1]['nombre'] if id_jugador-1 < len(self.server.clientes) else mensaje.get('nombre', ''),
                "lista_jugadores": [c['nombre'] for c in self.server.clientes]
            })
            print(f"cantidad de clietnes{self.server.clientes}")

            print(self.server.jugadores_desconectados)
            self.server.clientes[id_jugador-1]["status"] = "desconectado"

            if self.server.estado_partida:
                if self.server.anunciar_servidor_estado != True:
                    self.server.aceptar_conexiones_estado = True
                    self.server.anunciar_servidor_estado = False
                    self.server.anunciar_servidor_estado = True
                    hilo_servidor = threading.Thread(target=self.server.aceptar_conexiones)
                    hilo_servidor.daemon = True
                    hilo_servidor.start()

                    hilo_anuncio = threading.Thread(target=self.server.anunciar_servidor)
                    hilo_anuncio.daemon = True
                    hilo_anuncio.start()
        if mensaje.get('type') == 'Reconectar':
            # Procesar reconexión
            id_jugador_reconectar = mensaje.get('id_jugador')
            datos_guardados = self.server.jugadores_desconectados.get(id_jugador_reconectar)
            if datos_guardados:
                # Reasignar el mismo ID y restaurar datos
                    self.server.clientes[id_jugador_reconectar-1].update({
                        'socket': socket_cliente,
                        'id': id_jugador_reconectar,
                        'nombre': datos_guardados['nombre'],
                        'thread': threading.current_thread(),
                        "status": "activo"
                    })
                    if len(self.server.puntos_acumulados) > 0:
                        print(self.server.puntos_acumulados)
                        try:
                            if self.server.puntos_acumulados[id_jugador] >= 500:
                                self.server.clientes[id_jugador_reconectar-1].update({
                                'socket': socket_cliente,
                                'id': id_jugador_reconectar,
                                'nombre': datos_guardados['nombre'],
                                'thread': threading.current_thread(),
                                "status": "inactivo"
                                })
                        except:
                            pass

                    self.server.enviar_a_cliente(id_jugador_reconectar, {
                        'type': 'Reconectado',
                        'id_jugador': id_jugador_reconectar,
                        'estado_juego': datos_guardados['estado_juego'],
                        'nombre': datos_guardados['nombre']
                    })
                    del self.server.jugadores_desconectados[id_jugador_reconectar]
                    # Difundir la reconexión a otros jugadores
                    self.server.difundir({
                        'type': 'JugadorReconectado',
                        'id_jugador': id_jugador_reconectar,
                        'nombre': datos_guardados['nombre'],
                        "lista_jugadores": [c['nombre'] for c in self.server.clientes]
                    })
                    mano = self.server.manos[id_jugador_reconectar - 1]
                    try:
                        datos_serializables_mano = [c.to_dict() for c in mano]
                    except:
                        datos_serializables_mano = [c for c in mano]
                    if self.server.mesa_juego.elementos_mesa["dato_carta_descarte"] and len(self.server.mesa_juego.elementos_mesa["dato_carta_descarte"]) != 1:
                        descarte = self.server.mesa_juego.elementos_mesa["dato_carta_descarte"] 
                    elif self.server.mesa_juego.elementos_mesa["dato_carta_descarte"] == None:
                        descarte = None
                    else:
                        descarte = self.server.mesa_juego.elementos_mesa["dato_carta_descarte"][0]
                    if self.server.estado_partida:
                        self.server.enviar_a_cliente(id_jugador_reconectar,{
                        'type': 'Reconectar_partida',
                        "id_jugador" : id_jugador_reconectar,
                        "jugador_mano": self.server.mesa_juego.elementos_mesa["jugador_mano"],
                        "mano": datos_serializables_mano,
                        "jugada": self.server.jugadas_por_jugador[id_jugador_reconectar],
                        "jugadas_jugadores": self.server.jugadas_por_jugador,
                        "cantidad_manos_jugadores": self.server.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                        "datos_lista_jugadores": self.server.mesa_juego.elementos_mesa["datos_lista_jugadores"],
                        "dato_carta_descarte": descarte,
                        "dato_carta_quema": self.server.mesa_juego.elementos_mesa["dato_carta_quema"],
                        "mazo": len(self.server.mazo.cartas),
                        })
                    id_jugador = id_jugador_reconectar
                    if len(self.server.clientes)-len(self.server.jugadores_desconectados) == self.server.max_jugadores:
                        self.server.anunciar_servidor_estado = False
                        self.server.aceptar_conexiones_estado = False
            else: # Mensaje no es 'Reconectar'
                        # Si no hay id_jugador asignado, calcular uno nuevo
                        if id_jugador is None:
                            id_jugador = len(self.server.clientes) + len(self.server.jugadores_desconectados) + 1
                        existing = next((c for c in self.server.clientes if c.get('id') == id_jugador), None)
                        if existing:
                            existing.update({
                                'id': id_jugador,
                                'nombre': mensaje.get('nombre'),
                                'thread': threading.current_thread(),
                                "status": "activo",
                            })
                        else:
                            self.server.clientes.append({
                                'socket': socket_cliente,
                                'id': id_jugador,
                                'nombre': mensaje.get('nombre'),
                                'thread': threading.current_thread(),
                                "status": "activo",
                            })
                        self.server.enviar_a_cliente(id_jugador, {
                            'type': 'Bienvenido',
                            'id_jugador': id_jugador,
                            'nombre': mensaje.get('nombre'),
                            'game_state': self.server.estado_juego
                        })
                        # Difundir la nueva conexión a otros jugadores
                        self.server.difundir({
                            'type': 'NuevoJugador',
                            'id_jugador': id_jugador,
                            'nombre': mensaje.get('nombre'),
                            'TotalJugadores': len(self.server.clientes),
                            "lista_jugadores": [c['nombre'] for c in self.server.clientes]
                        })
            self.server.verificar_inicio_partida()

        if mensaje.get('type') == 'NuevoJugador':
                print(f"Mensaje del cliente: {mensaje}")
                # Preferir el id_jugador ya asociado al socket; si no existe, calcular uno nuevo
                if id_jugador is None:
                    id_jugador = len(self.server.clientes) + len(self.server.jugadores_desconectados) + 1
                existing = next((c for c in self.server.clientes if c.get('id') == id_jugador), None)
                if existing:
                    existing.update({
                        'id': id_jugador,
                        'nombre': mensaje.get('nombre'),
                        'thread': threading.current_thread(),
                        "status": "activo",
                    })
                else:
                    self.server.clientes.append({
                        'socket': socket_cliente,
                        'id': id_jugador,
                        'nombre': mensaje.get('nombre'),
                        'thread': threading.current_thread(),
                        "status": "activo",
                    })
                self.server.enviar_a_cliente(id_jugador, {
                    'type': 'Bienvenido',
                    'id_jugador': id_jugador,
                    'nombre': mensaje.get('nombre'),
                    'game_state': self.server.estado_juego
                })
                # Difundir la nueva conexión a otros jugadores
                self.server.difundir({
                    'type': 'NuevoJugador',
                    'id_jugador': id_jugador,
                    'nombre': mensaje.get('nombre'),
                    'TotalJugadores': len(self.server.clientes),
                    "lista_jugadores": [c['nombre'] for c in self.server.clientes]
                })
                self.server.verificar_inicio_partida()
        if mensaje.get('type') == 'Tomar_Carta_Descarte':
            print(f"Mensaje del cliente {id_jugador}: {mensaje}")
            if id_jugador == self.server.mesa_juego.elementos_mesa["jugador_mano"][0]:
                print("jugador mano correcto")
                try:# Tomar carta del descarte
                    if self.server.mesa_juego.elementos_mesa["dato_carta_descarte"]:
                        print("hay datos de descarte")
                        self.server.mesa_juego.elementos_mesa["dato_carta_descarte"] = None
                        print(self.server.descarte)
                        carta_tomada = self.server.descarte.pop()
                        # Actualiza mano jugador 
                        self.server.manos[id_jugador-1].append(carta_tomada)
                        self.server.ultimo_descarte.append(carta_tomada)
                        # Actualiza cantidad de cartas en mesa
                        self.server.modificar_cartas(id_jugador,+1)
                        # Difundir actualización a todos los jugadores
                        self.server.enviar_a_cliente(id_jugador, {
                            "type": "Actualizacion_Toma_Descarte",
                        })
                        self.server.difundir_excepcion(id_jugador,{
                            'type': 'Actualizacion_Carta_Descarte',
                            'cantidad_manos_jugadores': self.server.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                            "dato_carta_descarte": self.server.mesa_juego.elementos_mesa["dato_carta_descarte"],
                        })
                except Exception as e:
                    print(e)
        if mensaje.get("type") =="Descarte_Carta":
            if id_jugador == self.server.mesa_juego.elementos_mesa["jugador_mano"][0]:
                print(f"Mensaje del cliente {id_jugador}: {mensaje}")
                carta_descartar = mensaje.get("carta_descartada")

                # Validar que carta_descartar no sea None
                if carta_descartar is None:
                    print(f"ERROR: El jugador {id_jugador} intentó descartar sin seleccionar una carta")
                    # Enviar mensaje de error al cliente
                    self.server.enviar_a_cliente(id_jugador, {
                        "type": "Error_Descartar",
                        "mensaje": "Debes seleccionar una carta para descartar"
                    })
                    return  # Salir de esta función para este mensaje

                cartas = []
                for carta in self.server.manos[id_jugador-1]:
                    cartas.append(carta.to_dict())
                print(f"cartas del jugador {cartas}")
                if carta_descartar["numero"] == "Joker" and self.server.jugadas_por_jugador[id_jugador] == []:
                    self.server.enviar_a_cliente(id_jugador, {
                        "type": "No_Puede_Descartar_Joker",
                    })
                    print("esto no se puede :P")
                elif (self.server.ultimo_descarte and carta_descartar != None) or (len(self.server.manos[id_jugador-1]) == 1) and len(carta_descartar) == 1:
                    print(self.server.ultimo_descarte[-1])
                    carta_descarte_serealizada = self.server.ultimo_descarte[-1].to_dict()
                    print(carta_descarte_serealizada)
                    # Validar si intenta descartar la misma carta que tomó del descarte anterior
                    if (carta_descartar["numero"] == carta_descarte_serealizada["numero"] and 
                        carta_descartar["figura"] == carta_descarte_serealizada["figura"] and 
                        len(self.server.manos[id_jugador-1]) > 1):
                        # Enviar mensaje especial solo al jugador que está descartando
                        self.server.enviar_a_cliente(id_jugador, {
                            "type": "No_Puede_Descartar_Misma_Carta",
                        })
                    elif id_jugador == self.server.mesa_juego.elementos_mesa["jugador_mano"][0] and ((carta_descartar["numero"] != carta_descarte_serealizada["numero"] or carta_descartar["figura"] != carta_descarte_serealizada["figura"]) or len(self.server.manos[id_jugador-1]) == 1):
                        print(self.server.ultimo_descarte[-1])
                        for carta in self.server.manos[id_jugador-1]:
                            try:
                                carta_serealizada = carta.to_dict()
                            except:
                                carta_serealizada = carta
                            if carta_serealizada["numero"] == carta_descartar["numero"] and carta_serealizada["figura"] == carta_descartar["figura"]:
                                self.server.manos[id_jugador-1].remove(carta)
                                print(str(self.server.manos[id_jugador-1]))
                                self.server.mesa_juego.elementos_mesa["dato_carta_descarte"] = mensaje.get("carta_descartada")
                                self.server.modificar_cartas(id_jugador,-1) 
                                print(self.server.mesa_juego.elementos_mesa["cantidad_manos_jugadores"])
                                # Actualiza la carta de descarte en la mesa
                                self.server.descarte.append(carta)
                                carta_ = carta
                                # Guardar el ID del jugador que descartó esta carta
                                self.server.jugador_que_descarto = id_jugador
                                break
                        cartas = []
                        for carta in self.server.manos[id_jugador-1]:
                            cartas.append(carta.to_dict())
                        print(f"cartas del jugador {cartas}")
                        if carta_:# Difundir actualización a todos los jugadores
                            self.server.difundir_excepcion(id_jugador,
                                {
                                    "type" : "Actualizacion_Decartar_Carta",
                                    "cantidad_manos_jugadores": self.server.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                                    "dato_carta_descarte": self.server.mesa_juego.elementos_mesa["dato_carta_descarte"],
                                    }
                            )
                            self.server.enviar_a_cliente(id_jugador, {
                                "type": "Descartar_Carta",
                            })
                            #======Jesua:Verificar que la mano quedó vacia en el descarte
                            try:
                                if len(self.server.manos.get(id_jugador-1, [])) == 0:
                                    print(f"Jugador {id_jugador} se quedó sin cartas: difundir puntuaciones finales")
                                    self.server.difundir_puntuaciones_finales(id_jugador)
                            except Exception as e:
                                print(f"Error al verificar mano vacía para jugador {id_jugador}: {e}")

                            resultado_quema = self.server.quema_del_mono(id_jugador, carta_descartar)
                            if resultado_quema[0]:
                                self.server.enviar_a_cliente(id_jugador, resultado_quema[1])
                            else:
                                jugadores = self.server.mesa_juego.elementos_mesa["datos_lista_jugadores"]
                                idx_actual = next((i for i, j in enumerate(jugadores) if j[0] == id_jugador), None)
                                num = 0
                                if idx_actual is not None:
                                    for jugador in jugadores:
                                        # Calcula el índice del siguiente jugador (circular)
                                        idx_siguiente = (idx_actual +num + 1) % len(jugadores)
                                        id_siguiente = jugadores[idx_siguiente][0]
                                        nombre = jugadores[idx_siguiente][1]
                                        num =+ 1
                                        if self.server.clientes[id_siguiente-1]["status"] == "activo":
                                            break
                                self.server.mesa_juego.elementos_mesa.update({"jugador_mano":(id_siguiente,nombre)})
                                self.server.finalizar_turno(id_jugador,id_siguiente)
                elif (self.server.contador_turno_compra == 0 and carta_descartar != None) or (len(self.server.manos[id_jugador-1]) == 1) :
                    cartas = []
                    for carta in self.server.manos[id_jugador-1]:
                        cartas.append(carta.to_dict())
                    print(f"cartas del jugador {cartas}")
                    for carta in self.server.manos[id_jugador-1]:
                        try:
                            carta_serealizada = carta.to_dict()
                        except:
                            carta_serealizada = carta
                        if carta_serealizada["numero"] == carta_descartar["numero"] and carta_serealizada["figura"] == carta_descartar["figura"]:
                            self.server.manos[id_jugador-1].remove(carta)
                            print(str(self.server.manos[id_jugador-1]))
                            self.server.mesa_juego.elementos_mesa["dato_carta_descarte"] = mensaje.get("carta_descartada")
                            self.server.modificar_cartas(id_jugador,-1)
                            # Actualiza la carta de descarte en la mesa
                            self.server.descarte.append(carta)
                            carta_ = carta
                            # Guardar el ID del jugador que descartó esta carta
                            self.server.jugador_que_descarto = id_jugador
                            break

                        # Difundir actualización a todos los jugadores
                    cartas = []
                    for carta in self.server.manos[id_jugador-1]:
                        cartas.append(carta.to_dict())
                    print(f"cartas del jugador {cartas}")
                    print(self.server.mesa_juego.elementos_mesa["dato_carta_descarte"])
                    if carta_:
                        self.server.difundir_excepcion(id_jugador,
                            {
                            "type" : "Actualizacion_Decartar_Carta",
                            "cantidad_manos_jugadores": self.server.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                            "dato_carta_descarte": self.server.mesa_juego.elementos_mesa["dato_carta_descarte"],
                            }
                        )
                        self.server.enviar_a_cliente(id_jugador, {
                            "type": "Descartar_Carta",
                        })
                        resultado_quema = self.server.quema_del_mono(id_jugador, carta_descartar)
                        mano_vacia = self.server.verificar_mano_vacia_y_difundir(id_jugador)
                        if resultado_quema[0] and mano_vacia == None :
                            self.server.enviar_a_cliente(id_jugador, resultado_quema[1])
                        elif mano_vacia == None :
                            jugadores = self.server.mesa_juego.elementos_mesa["datos_lista_jugadores"]
                            idx_actual = next((i for i, j in enumerate(jugadores) if j[0] == id_jugador), None)
                            num = 0
                            if idx_actual is not None:
                                for jugador in jugadores:
                                    # Calcula el índice del siguiente jugador (circular)
                                    idx_siguiente = (idx_actual +num + 1) % len(jugadores)
                                    id_siguiente = jugadores[idx_siguiente][0]
                                    nombre = jugadores[idx_siguiente][1]
                                    num =+ 1
                                    if self.server.clientes[id_siguiente-1]["status"] == "activo":
                                        break
                            self.server.mesa_juego.elementos_mesa.update({"jugador_mano":(id_siguiente,nombre)})
                            self.server.finalizar_turno(id_jugador,id_siguiente)

        if mensaje.get("type") == "No_tomar_descarte":
            print(f"Mensaje del cliente {id_jugador}: {mensaje}")
            # Encuentra el índice del jugador actual en la lista de jugadores
            if self.server.contador_turno_compra != len(self.server.clientes)-1:
                jugadores = self.server.mesa_juego.elementos_mesa["datos_lista_jugadores"]
                idx_actual = next((i for i, j in enumerate(jugadores) if j[0] == id_jugador), None)
                if idx_actual is not None:
                    num= 0
                    for jugador in jugadores:
                        # Calcula el índice del siguiente jugador (circular)
                        idx_siguiente = (idx_actual +num + 1) % len(jugadores)
                        id_siguiente = jugadores[idx_siguiente][0]
                        nombre = jugadores[idx_siguiente][1]
                        num =+ 1
                        if self.server.clientes[id_siguiente-1]["status"] == "activo":
                            break
                    print(f"Siguiente jugador para oferta de descarte: {id_siguiente}")
                    # Verificar si el siguiente jugador es el que descartó la carta
                    if id_siguiente == self.server.jugador_que_descarto and id_siguiente != id_jugador or id_siguiente == self.server.mesa_juego.elementos_mesa["jugador_mano"][0]:
                        print(f"El siguiente jugador ({id_siguiente}) es el que descartó la carta o hay jugadores desconectados. Terminando ronda de compra.")
                        # Guardar el ID del jugador que descartó antes de limpiarlo
                        id_jugador_que_descarto = self.server.jugador_que_descarto

                        # Quemar la carta y terminar la ronda de compra
                        if self.server.descarte:
                            self.server.quema.append(self.server.descarte.pop())
                        self.server.ultimo_descarte = []
                        self.server.mesa_juego.elementos_mesa["dato_carta_descarte"] = None
                        self.server.mesa_juego.elementos_mesa["cantidad_cartas_quema"] += 1
                        self.server.mesa_juego.elementos_mesa["dato_carta_quema"] = self.server.quema[-1].to_dict()
                        self.server.contador_turno_compra = 0
                        self.server.jugador_compra = None
                        self.server.jugador_que_descarto = None  # Limpiar la referencia

                        # Calcular el siguiente jugador después del que descartó (vuelve el turno)
                        idx_jugador_que_descarto = next((i for i, j in enumerate(jugadores) if j[0] == id_jugador_que_descarto), None)
                        if idx_jugador_que_descarto is not None and id_siguiente != self.server.mesa_juego.elementos_mesa["jugador_mano"][0]:
                            print("caso mismo jugador que descarto")
                            idx_siguiente_despues_descarte = (idx_jugador_que_descarto + 1) % len(jugadores)
                            id_siguiente_despues_descarte = jugadores[idx_siguiente_despues_descarte][0]
                            nombre_siguiente = jugadores[idx_siguiente_despues_descarte][1]
                            self.server.mesa_juego.elementos_mesa.update({"jugador_mano": (id_siguiente_despues_descarte, nombre_siguiente)})

                            # Enviar mensajes a los jugadores
                            self.server.enviar_a_cliente(id_jugador, {
                                "type": "No_descartar",
                                "turno_robar": False,
                            })
                            self.server.enviar_a_cliente(id_siguiente_despues_descarte, {
                                "type": "Actualizar_botones",
                                "turno_robar": True,
                                "dato_carta_descarte": None,
                                "cantidad_cartas_quema": self.server.mesa_juego.elementos_mesa["cantidad_cartas_quema"],
                                "dato_carta_quema": self.server.mesa_juego.elementos_mesa["dato_carta_quema"]
                            })
                            self.server.difundir_excepcion(id_siguiente_despues_descarte, {
                                "type": "Actualizar_botones",
                                "turno_robar": False,
                                "dato_carta_descarte": None,
                                "cantidad_cartas_quema": self.server.mesa_juego.elementos_mesa["cantidad_cartas_quema"],
                                "dato_carta_quema": self.server.mesa_juego.elementos_mesa["dato_carta_quema"]
                            })
                            # Reactivar botones del jugador que descartó (ya no es su carta)
                            if id_jugador_que_descarto != id_siguiente_despues_descarte:
                                self.server.enviar_a_cliente(id_jugador_que_descarto, {
                                    "type": "Reactivar_Botones_No_Turno",
                                })
                        elif id_siguiente == self.server.mesa_juego.elementos_mesa["jugador_mano"][0]:

                            self.server.enviar_a_cliente(self.server.mesa_juego.elementos_mesa["jugador_mano"][0],
                                {
                                    "type":"Actualizar_botones",
                                    "turno_robar" : True,
                                    "dato_carta_descarte" : None,
                                    "cantidad_cartas_quema" : self.server.mesa_juego.elementos_mesa["cantidad_cartas_quema"],
                                    "dato_carta_quema": self.server.mesa_juego.elementos_mesa["dato_carta_quema"]
                                })
                            self.server.difundir_excepcion(self.server.mesa_juego.elementos_mesa["jugador_mano"][0],
                                {
                                    "type": "Actualizar_botones",
                                    "turno_robar" : False,
                                    "dato_carta_descarte" : None,
                                    "cantidad_cartas_quema": self.server.mesa_juego.elementos_mesa["cantidad_cartas_quema"],
                                    "dato_carta_quema": self.server.mesa_juego.elementos_mesa["dato_carta_quema"]
                                })

                    elif id_jugador==id_siguiente:
                        print("Todos los jugadores rechazaron comprar la carta descartada.")
                        self.server.quema.append(self.server.descarte.pop())
                        self.server.ultimo_descarte = []
                        self.server.mesa_juego.elementos_mesa["dato_carta_descarte"] = None
                        self.server.mesa_juego.elementos_mesa["cantidad_cartas_quema"] += 1
                        self.server.mesa_juego.elementos_mesa["dato_carta_quema"] = self.server.quema[-1].to_dict()
                        self.server.contador_turno_compra = 0
                        self.server.enviar_a_cliente(self.server.mesa_juego.elementos_mesa["jugador_mano"][0],
                            {
                                "type":"Actualizar_botones",
                                "turno_robar" : True,
                                "dato_carta_descarte" : None,
                                "cantidad_cartas_quema" : self.server.mesa_juego.elementos_mesa["cantidad_cartas_quema"],
                                "dato_carta_quema": self.server.mesa_juego.elementos_mesa["dato_carta_quema"]
                            })
                        self.server.difundir_excepcion(self.server.mesa_juego.elementos_mesa["jugador_mano"][0],
                            {
                                "type": "Actualizar_botones",
                                "turno_robar" : False,
                                "dato_carta_descarte" : None,
                                "cantidad_cartas_quema": self.server.mesa_juego.elementos_mesa["cantidad_cartas_quema"],
                                "dato_carta_quema": self.server.mesa_juego.elementos_mesa["dato_carta_quema"]
                            })
                        self.server.contador_turno_compra = 0    
                        self.server.jugador_compra = None
                        # Reactivar botones del jugador que descartó (ya no es su carta)
                        if self.server.jugador_que_descarto and self.server.jugador_que_descarto != self.server.mesa_juego.elementos_mesa["jugador_mano"][0]:
                            self.server.enviar_a_cliente(self.server.jugador_que_descarto, {
                                "type": "Reactivar_Botones_No_Turno",
                            })
                        self.server.jugador_que_descarto = None  # Limpiar referencia cuando se quema la carta
                        self.server.ultimo_descarte = []
                    elif (self.server.jugador_compra is None and id_jugador == self.server.mesa_juego.elementos_mesa["jugador_mano"][0]) or id_jugador == self.server.jugador_compra:
                        self.server.jugador_compra = id_siguiente
                        if self.server.contador_turno_compra == 0:
                            self.server.enviar_a_cliente(id_jugador, {
                                "type": "Rechazar_descarte",
                                "turno_robar": False,
                            })
                            self.server.enviar_a_cliente(id_siguiente, {
                                "type": "No_descartar",
                                "turno_robar": True,
                            })
                        else:
                            self.server.enviar_a_cliente(id_jugador, {
                                "type": "No_descartar",
                                "turno_robar": False,
                            })
                            self.server.enviar_a_cliente(id_siguiente, {
                                "type": "No_descartar",
                                "turno_robar": True,
                            })
                        self.server.contador_turno_compra += 1
                    elif idx_actual is not None and self.server.clientes[id_jugador-1]["status"] != "activo":
                        self.server.jugador_compra = id_siguiente
                        if self.server.contador_turno_compra == 0:
                            self.server.enviar_a_cliente(id_jugador, {
                                "type": "Rechazar_descarte",
                                "turno_robar": False,
                            })
                            self.server.enviar_a_cliente(id_siguiente, {
                                "type": "No_descartar",
                                "turno_robar": True,
                            })
                        else:
                            self.server.enviar_a_cliente(id_jugador, {
                                "type": "No_descartar",
                                "turno_robar": False,
                            })
                            self.server.enviar_a_cliente(id_siguiente, {
                                "type": "No_descartar",
                                "turno_robar": True,
                            })
                        self.server.contador_turno_compra += 1
            else:
                print("Funciona :P, ya eres el ultimo en comprar")
                self.server.quema.append(self.server.descarte.pop())
                self.server.ultimo_descarte = []
                self.server.mesa_juego.elementos_mesa["dato_carta_descarte"] = None
                self.server.mesa_juego.elementos_mesa["cantidad_cartas_quema"] += 1
                self.server.mesa_juego.elementos_mesa["dato_carta_quema"] = self.server.quema[-1].to_dict()
                self.server.contador_turno_compra = 0
                self.server.enviar_a_cliente(self.server.mesa_juego.elementos_mesa["jugador_mano"][0],
                    {
                        "type":"Actualizar_botones",
                        "turno_robar" : True,
                        "dato_carta_descarte" : None,
                        "cantidad_cartas_quema" : self.server.mesa_juego.elementos_mesa["cantidad_cartas_quema"],
                        "dato_carta_quema": self.server.mesa_juego.elementos_mesa["dato_carta_quema"]
                    })
                self.server.difundir_excepcion(self.server.mesa_juego.elementos_mesa["jugador_mano"][0],
                    {
                        "type": "Actualizar_botones",
                        "turno_robar" : False,
                        "dato_carta_descarte" : None,
                        "cantidad_cartas_quema": self.server.mesa_juego.elementos_mesa["cantidad_cartas_quema"],
                        "dato_carta_quema": self.server.mesa_juego.elementos_mesa["dato_carta_quema"]
                    })
                self.server.contador_turno_compra = 0    
                self.server.jugador_compra = None
                # Reactivar botones del jugador que descartó (ya no es su carta)
                if self.server.jugador_que_descarto and self.server.jugador_que_descarto != self.server.mesa_juego.elementos_mesa["jugador_mano"][0]:
                    self.server.enviar_a_cliente(self.server.jugador_que_descarto, {
                        "type": "Reactivar_Botones_No_Turno",
                    })
                self.server.jugador_que_descarto = None  # Limpiar referencia cuando se quema la carta
                self.server.ultimo_descarte = []
        if mensaje.get("type") == "comprar":
            print(mensaje)
            print(f"Tipo de self.server.descarte: {type(self.server.descarte)}")
            print(f"Contenido de self.server.descarte: {self.server.descarte}")
            self.server.mazo_nuevo(dir = "comprar")
            # PRIMERO: Serializar la carta ANTES de limpiar el descarte
            if self.server.descarte:
                print(f"Tipo de self.server.descarte[0]: {type(self.server.descarte[0])}")
                print(f"Contenido de self.server.descarte[0]: {self.server.descarte[0]}")
                carta_descarte_serealizada = self.server.descarte[0].to_dict()
            else:
                carta_descarte_serealizada = None
            print(self.server.mazo.cartas[-1])
            if id_jugador == self.server.jugador_compra:
                # LUEGO: Limpiar el descarte
                carta_extra = self.server.mazo.cartas.pop() # Toma la ultima carta del mazo
                self.server.manos[id_jugador-1].append(carta_extra) # Agrega la Carta a la mano del jugador en el server
                self.server.manos[id_jugador-1].append(self.server.descarte[-1]) # Agrega la Carta a la mano del jugador en el server
                self.server.descarte = []
                self.server.modificar_cartas(id_jugador,+2)
                print(self.server.mesa_juego.elementos_mesa["cantidad_manos_jugadores"])
                print(f"Mensaje del cliente {id_jugador}: {mensaje}") # Envio de actualizacion a los jugadores
                #Para el jugador de la accion
                self.server.enviar_a_cliente(id_jugador, {
                    "type": "comprar",
                    "carta_extra" : carta_extra.to_dict(),
                })
                #Para los demas xd
                self.server.difundir_excepcion(id_jugador,{
                    "type":"Actualizacion_Carta_Descarte",
                    'cantidad_manos_jugadores': self.server.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "dato_carta_descarte": self.server.mesa_juego.elementos_mesa["dato_carta_descarte"],
                })

                self.server.enviar_a_cliente(self.server.mesa_juego.elementos_mesa["jugador_mano"][0],{
                    "type" : "Compra_realizada"
                })
                nombre_cliente = next((c['nombre'] for c in self.server.clientes if c['id'] == id_jugador), None)
                self.server.difundir_excepcion(id_jugador,{
                    "type": "Ciert_jugador_compro_carta_del_descarte",
                    "jugador_compro": nombre_cliente
                })
                self.server.jugador_compra = None # Se borra el jugador que puede comprar, para evitar peos 
                self.server.contador_turno_compra = 0
                # Reactivar botones del jugador que descartó (ya no es su carta)
                if self.server.jugador_que_descarto and self.server.jugador_que_descarto != self.server.mesa_juego.elementos_mesa["jugador_mano"][0]:
                    self.server.enviar_a_cliente(self.server.jugador_que_descarto, {
                        "type": "Reactivar_Botones_No_Turno",
                    })
                self.server.jugador_que_descarto = None  # Limpiar referencia cuando se compra la carta
                self.server.ultimo_descarte = []

        if mensaje.get("type") == "Tomar_carta_mazo":
            print(id_jugador)
            """aqui hay un error muy feo, el jugador compra sin querer le da a comprar cuando es su carta la del descarte"""
            if id_jugador == self.server.mesa_juego.elementos_mesa["jugador_mano"][0]:
                print("viendo si hay mazo nuevo")
                self.server.mazo_nuevo()
                carta_extra = self.server.mazo.cartas.pop() # Toma la ultima carta del mazo
                self.server.manos[id_jugador-1].append(carta_extra) # Agrega la Carta a la mano del jugador en el server
                self.server.modificar_cartas(id_jugador,+1)
                print(self.server.mesa_juego.elementos_mesa["cantidad_manos_jugadores"])
                jugadores = self.server.mesa_juego.elementos_mesa["datos_lista_jugadores"]
                idx_actual = next((i for i, j in enumerate(jugadores) if j[0] == id_jugador), None)

                self.server.enviar_a_cliente(id_jugador,{
                    "type":"Tomar_carta_mazo",
                    "carta_extra": carta_extra.to_dict(),
                    "jugador_mano": self.server.mesa_juego.elementos_mesa["jugador_mano"],
                    "cantidad_mano_jugadores": self.server.mesa_juego.elementos_mesa["cantidad_manos_jugadores"]
                })
        if mensaje.get("type") ==  "mono_quemado":
            carta_descartes = self.server.descarte[-1].to_dict()
            carta_descartada = mensaje.get("carta_descartada")
            if id_jugador == self.server.mesa_juego.elementos_mesa["jugador_mano"][0] and (carta_descartes["numero"] != carta_descartada["numero"] or carta_descartes["figura"] != carta_descartada["figura"]):
                self.server.quema.append(self.server.descarte.pop())
                for carta in self.server.manos[id_jugador-1]:
                    try:
                        carta_mono_serealizada = carta.to_dict()
                    except:
                        carta_mono_serealizada = carta
                    if carta_mono_serealizada["numero"] == carta_descartada["numero"] and carta_mono_serealizada["figura"] == carta_descartada["figura"]:
                        self.server.manos[id_jugador-1].remove(carta)
                        print(str(self.server.manos[id_jugador-1]))
                        self.server.mesa_juego.elementos_mesa["dato_carta_descarte"] = mensaje.get("carta_descartada")
                        self.server.modificar_cartas(id_jugador,-1) 
                        print(self.server.mesa_juego.elementos_mesa["cantidad_manos_jugadores"])
                        # Actualiza la carta de descarte en la mesa
                        self.server.descarte.append(carta)
                        # Guardar el ID del jugador que descartó esta carta
                        self.server.jugador_que_descarto = id_jugador
                        print("carta mono quemada")
                        self.server.mesa_juego.elementos_mesa["dato_carta_quema"] = self.server.quema[-1].to_dict()
                        print(self.server.descarte)
                        carta_ = carta
                        break
                if carta_:# Difundir actualización a todos los jugadores
                    self.server.mesa_juego.elementos_mesa["cantidad_cartas_quema"] += 1
                    self.server.difundir({
                        "type": "Actualizar_quema_descarte",
                        "cantidad_cartas_quema" : self.server.mesa_juego.elementos_mesa["cantidad_cartas_quema"]
                    })
                    self.server.difundir_excepcion(id_jugador,
                        {
                        "type" : "actualizar_mono",
                        "cantidad_manos_jugadores": self.server.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                        "dato_carta_descarte": self.server.mesa_juego.elementos_mesa["dato_carta_descarte"],
                        "dato_carta_quema": self.server.mesa_juego.elementos_mesa["dato_carta_quema"],
                        }
                    )
                    self.server.enviar_a_cliente(id_jugador, {
                        "type": "descartar_mono",
                        "dato_carta_quema": self.server.mesa_juego.elementos_mesa["dato_carta_quema"],
                    })
                    #====Jesua: Verificar si la mano quedó vacía por esta acción y difundir puntuaciones
                    try:
                        self.server.verificar_mano_vacia_y_difundir(id_jugador)
                    except Exception:
                        pass

                    jugadores = self.server.mesa_juego.elementos_mesa["datos_lista_jugadores"]
                    idx_actual = next((i for i, j in enumerate(jugadores) if j[0] == id_jugador), None)
                    if idx_actual is not None:
                        # Calcula el índice del siguiente jugador (circular)
                        idx_siguiente = (idx_actual + 1) % len(jugadores)
                        id_siguiente = jugadores[idx_siguiente][0]
                        nombre = jugadores[idx_siguiente][1]
                    self.server.mesa_juego.elementos_mesa.update({"jugador_mano":(id_siguiente,nombre)})
                    self.server.finalizar_turno(id_jugador,id_siguiente)
        if mensaje["type"] == "validar_seleccion":
            if id_jugador == self.server.mesa_juego.elementos_mesa["jugador_mano"][0]:
                cartas_a_bajar_ = mensaje["datos_cartas"]
                resultado_validacion = self.server.validar_seleccion(cartas_a_bajar_, id_jugador)
                # Enviar mensajes según el resultado
                for mensaje_a_enviar in resultado_validacion[1]:
                    self.server.enviar_a_cliente(id_jugador, mensaje_a_enviar)
        if mensaje["type"] == "bajarse":
            resultado_jugada = self.server.validar_jugada(id_jugador)
            # Enviar mensajes según el resultado
            for mensaje_a_enviar in resultado_jugada[1]:
                self.server.enviar_a_cliente(id_jugador, mensaje_a_enviar)
            for mensaje_a_difundir in resultado_jugada[2]:
                self.server.difundir_excepcion(id_jugador, mensaje_a_difundir)
            try:
                self.server.verificar_mano_vacia_y_difundir(id_jugador)
            except Exception as _:
                pass
        if mensaje["type"] == "elegir_posicion_seguidilla":
            posicion_elegida = mensaje["posicion_elegida"]
            if posicion_elegida in ["inicio","punta"] and self.server.seguidilla != {} and self.server.ronda==1 or self.server.ronda==4:
                if posicion_elegida == "inicio":
                    joker = self.server.seguidilla.pop()
                    print(joker)
                    self.server.seguidilla.insert(0, joker)
                    print("Seguidilla posicionada al inicio")
                    self.server.enviar_a_cliente(id_jugador,{
                        "type" : "seleccion_valida",
                        "actualizar" : True
                    })
                elif posicion_elegida == "punta":
                    joker = self.server.seguidilla.pop()
                    print(joker)
                    self.server.seguidilla.append(joker)
                    print("Seguidilla posicionada al final")
                    self.server.enviar_a_cliente(id_jugador,{
                        "type" : "seleccion_valida",
                        "actualizar" : True
                    })
                print(self.server.seguidilla)
            elif posicion_elegida in ["inicio","punta"] and self.server.seguidilla != ({} and []) and self.server.ronda==2:
                print(self.server.seguidilla)
                if posicion_elegida == "inicio":
                    joker = self.server.seguidilla[-1].pop()
                    print(joker)
                    self.server.seguidilla[-1].insert(0, joker)
                    print("Seguidilla posicionada al inicio")
                    if len(self.server.seguidilla) == 2:
                        print(self.server.seguidilla)
                        prueba_separacion_ = self.server.valor_joker2(self.server.jugada_numeros(self.server.seguidilla[0])) + self.server.valor_joker2(self.server.jugada_numeros(self.server.seguidilla[-1]))
                        print(prueba_separacion_)
                        prueba_separacion = prueba_separacion_
                        print(prueba_separacion)
                        validacion = self.server.validar_segudilla(prueba_separacion)
                        if validacion != False:
                            print("No se puede dividir dos seguidillas continuas")
                            self.server.seleccionando = False
                            self.server.enviar_a_cliente(id_jugador, {
                            "type": "Seleccion_cancelada",
                            })
                            self.server.seguidilla = []

                        else:
                            self.server.enviar_a_cliente(id_jugador,{
                            "type" : "seleccion_valida",
                            "actualizar" : True
                            })
                    elif len(self.server.jugadas_por_jugador[id_jugador]) == 1:
                        print(self.server.jugada_numeros(self.server.seguidilla[-1]))
                        print("atras de esto esta el error")
                        prueba_separacion_ = self.server.valor_joker2(self.server.jugada_numeros(self.server.jugadas_por_jugador[id_jugador][-1][-1])) + self.server.valor_joker2(self.server.jugada_numeros(self.server.seguidilla[-1]))
                        print(prueba_separacion_)
                        prueba_separacion = prueba_separacion_
                        print(prueba_separacion)
                        validacion = self.server.validar_segudilla(prueba_separacion)
                        print(validacion)
                        if validacion != False:
                            print("No se puede dividir dos seguidillas continuas")
                            self.server.seleccionando = False
                            self.server.enviar_a_cliente(id_jugador, {
                            "type": "Seleccion_cancelada",
                            })
                            self.server.seguidilla = []
                        else:
                            self.server.enviar_a_cliente(id_jugador,{
                                "type" : "seleccion_valida",
                                "actualizar" : True
                                })
                    else:
                        self.server.enviar_a_cliente(id_jugador,{
                            "type" : "seleccion_valida",
                            "actualizar" : True
                            })
                elif posicion_elegida == "punta":
                    joker = self.server.seguidilla[-1].pop()
                    print(joker)
                    self.server.seguidilla[-1].append(joker)
                    print("Seguidilla posicionada al final")
                    if len(self.server.seguidilla) == 2:
                        print(self.server.jugada_numeros(self.server.seguidilla[0]))

                        prueba_separacion_ = self.server.valor_joker2(self.server.jugada_numeros(self.server.seguidilla[0])) + self.server.valor_joker2(self.server.jugada_numeros(self.server.seguidilla[-1]))
                        print(prueba_separacion_)
                        prueba_separacion = prueba_separacion_
                        print(prueba_separacion)
                        validacion = self.server.validar_segudilla(prueba_separacion)
                        if validacion != False:
                            print("No se puede dividir dos seguidillas continuas")
                            self.server.seleccionando = False
                            self.server.enviar_a_cliente(id_jugador, {
                            "type": "Seleccion_cancelada",
                            })
                            self.server.enviar_a_cliente(id_jugador, {
                            "type": "mensaje_seguidillas_continuas",
                            })
                            self.server.seguidilla = []

                        else:
                            self.server.enviar_a_cliente(id_jugador,{
                            "type" : "seleccion_valida",
                            "actualizar" : True
                            })
                    elif len(self.server.jugadas_por_jugador[id_jugador]) == 1:
                        print("atras de esto esta el error")
                        prueba_separacion_ = self.server.valor_joker2(self.server.jugada_numeros(self.server.jugadas_por_jugador[id_jugador][-1][-1])) + self.server.valor_joker2(self.server.jugada_numeros(self.server.seguidilla[-1]))
                        print(prueba_separacion_)
                        prueba_separacion = prueba_separacion_
                        print(prueba_separacion)
                        validacion = self.server.validar_segudilla(prueba_separacion)
                        if validacion != False:
                            print("No se puede dividir dos seguidillas continuas")
                            self.server.seleccionando = False
                            self.server.enviar_a_cliente(id_jugador, {
                            "type": "Seleccion_cancelada",
                            })
                            self.server.seguidilla = []
                            self.server.enviar_a_cliente(id_jugador, {
                            "type": "mensaje_seguidillas_continuas",
                            })
                        else:
                            self.server.enviar_a_cliente(id_jugador,{
                                "type" : "seleccion_valida",
                                "actualizar" : True
                                })
                    else:
                        self.server.enviar_a_cliente(id_jugador,{
                            "type" : "seleccion_valida",
                            "actualizar" : True
                    })
                print(self.server.seguidilla)
                print("holaaa")


        if mensaje["type"] == "cancelar_jugada":
            print("no se")
            if self.server.seleccionando == True:
                self.server.trio = {}
                self.server.seguidilla = {}
                self.server.enviar_a_cliente(id_jugador,{
                    "type" : "Seleccion_cancelada",
                })
                self.server.seleccionando = False
            elif self.server.jugadas_por_jugador.get(id_jugador) not in ([], None) and not self.server.cancelar:
                self.server.cancelar = True
                # trabajar con copia para evitar mutar estructuras compartidas
                ultima_jugada = copy.deepcopy(self.server.ultima_jugada)

                # eliminar de jugadas_por_jugador todas las entradas cuyo grupo coincida (por valor)
                actuales = self.server.jugadas_por_jugador.get(id_jugador, [])
                self.server.jugadas_por_jugador[id_jugador] = [
                    (tag, grupo) for (tag, grupo) in actuales
                    if not any(grupo == jug for jug in ultima_jugada)
                ]

                # convertir dicts a objetos Carta solo al devolverlas a la mano del jugador
                print(ultima_jugada)
                for grupo in ultima_jugada:
                    cartas_obj = []
                    for carta in grupo:
                        # usar los mismos kwargs que en el resto del código
                        cartas_obj.append(Carta(un_juego=None, numero=carta["numero"], figura=carta["figura"]))
                    self.server.manos[id_jugador-1].extend(cartas_obj)

                # limpiar y notificar
                cantidad_devuelta = []
                for grupo in ultima_jugada:
                    for carta in grupo:
                        cantidad_devuelta.append(carta)
                self.server.seleccionando = False

                self.server.ultima_jugada = []
                self.server.actualizar_mano_y_notificar(
                    id_jugador,
                    len(cantidad_devuelta),
                    {
                        "type" : "jugada_cancelada",
                        "cantidad_manos_jugadores": self.server.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                        "datos_mano_jugador": None,  # Se actualizará automáticamente
                        "jugada" : self.server.jugadas_por_jugador[id_jugador],
                        "jugadas_jugadores":self.server.jugadas_por_jugador,
                    },
                    {
                        "type" : "se_extendio",
                        "cantidad_manos_jugadores": self.server.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                        "jugadas_jugadores":self.server.jugadas_por_jugador,   
                    }
                )
                if self.server.ronda == 2:
                    self.server.seguidilla = []
                if len(self.server.jugadas_por_jugador[id_jugador]) == 0:
                    self.server.cancelar = False
            elif self.server.cancelar == True:
                print("pipipip")
            elif self.server.cancelar == False and len(self.server.jugadas_por_jugador[id_jugador]) == 0:
                print("No tienes jugadas para cancelar")
                self.server.enviar_a_cliente(id_jugador,{
                    "type" : "regresando_menu",
                })
        if mensaje["type"] == "extender_en":
            print(mensaje)
            cartas_expandir = None
            if len(mensaje["cartas_expandir"]) == 1:
                cartas_expandir = mensaje["cartas_expandir"]
            else:
                cartas_expandir = False
            id_donde_bajarse = mensaje["id_jugador"]
            jugada = None
            print(self.server.jugadas_por_jugador)
            if self.server.ronda == 1:
                for x,y in self.server.jugadas_por_jugador.items():
                    if x == id_donde_bajarse:
                        if y:
                            jugada = y
                            jugada_trio = y[0]
                            jugada_seguidilla = y[-1]
                            break
                if jugada and cartas_expandir != False :
                    print(jugada)
                    validacion_ext_seguidilla = self.server.validar_extender_seguidilla(cartas_expandir[0],jugada_seguidilla[-1])
                    validacion_ext_trio = self.server.validar_extender_trio(cartas_expandir[0],jugada_trio[-1])
                    print(validacion_ext_seguidilla)
                    print(validacion_ext_trio)
                    if  validacion_ext_seguidilla != False and validacion_ext_trio != False: 
                        print("Ahora se elige donde extender")
                        if validacion_ext_seguidilla == "ambos":
                            pos = "ambos"
                        else:
                            pos = validacion_ext_seguidilla    
                        self.server.enviar_a_cliente(id_jugador,{
                            "type" : "elejir_donde_extender",
                            "posicion_seguidilla" : pos,
                            "trio_seguidilla" : True,
                            "seguidilla_seguidilla" : False,
                        })
                        self.server.informacion_extender = [mensaje["id_jugador"],cartas_expandir]

                    elif validacion_ext_seguidilla != False:
                        if validacion_ext_seguidilla == "inicio":
                            for carta in cartas_expandir:
                                for i, _carta in enumerate(self.server.manos[id_jugador-1]):
                                    _carta = _carta.to_dict()
                                    if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                        self.server.manos[id_jugador-1].pop(i)
                                        break
                            self.server.jugadas_por_jugador[id_donde_bajarse][-1][-1].insert(0, cartas_expandir[0])
                            print("Seguidilla extendida al inicio")
                            self.server.extender_confirmado(id_jugador,id_donde_bajarse)
                        elif validacion_ext_seguidilla == "final":
                            for carta in cartas_expandir:
                                for i, _carta in enumerate(self.server.manos[id_jugador-1]):
                                    _carta = _carta.to_dict()
                                    if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                        self.server.manos[id_jugador-1].pop(i)
                                        break
                            self.server.jugadas_por_jugador[id_donde_bajarse][-1][-1].extend(cartas_expandir)
                            print("Seguidilla extendida al final")
                            self.server.extender_confirmado(id_jugador,id_donde_bajarse)      
                        elif validacion_ext_seguidilla == "ambos":
                            print("Se debe elegir donde extender la seguidilla")
                            self.server.enviar_a_cliente(id_jugador,{
                            "type" : "elejir_donde_extender",
                            "posicion_seguidilla" : "ambos",
                            "trio_seguidilla" : False,
                            "seguidilla_seguidilla" : False,
                            })
                            self.server.informacion_extender = [mensaje["id_jugador"],cartas_expandir]
                    elif validacion_ext_trio != False:
                        for carta in cartas_expandir:
                            for i, _carta in enumerate(self.server.manos[id_jugador-1]):
                                _carta = _carta.to_dict()
                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                    self.server.manos[id_jugador-1].pop(i)
                                    break
                        self.server.jugadas_por_jugador[id_donde_bajarse][0][-1].extend(cartas_expandir)
                        self.server.extender_confirmado(id_jugador,id_donde_bajarse)
                    print(self.server.jugadas_por_jugador)
            elif self.server.ronda == 2:
                print(self.server.jugadas_por_jugador)
                for x,y in self.server.jugadas_por_jugador.items():
                    if x == id_donde_bajarse:
                        if y:
                            jugada = y
                            jugada_seguidilla1 = y[0]
                            jugada_seguidilla2 = y[-1]
                            break
                if jugada and cartas_expandir != False :
                    print(jugada)
                    validacion_ext_seguidilla1 = self.server.validar_extender_seguidilla(cartas_expandir[0],jugada_seguidilla1[-1])
                    validacion_ext_seguidilla2 = self.server.validar_extender_seguidilla(cartas_expandir[0],jugada_seguidilla2[-1])
                    if validacion_ext_seguidilla2 != False and validacion_ext_seguidilla1 != False:
                        print("Ahora se elige en cual seguidilla extender")
                        if validacion_ext_seguidilla1 == "ambos":
                            pos = "ambos"
                        else:
                            pos = validacion_ext_seguidilla1   
                        self.server.enviar_a_cliente(id_jugador,{
                            "type" : "elejir_donde_extender",
                            "posicion_seguidilla1" : pos,
                            "posicion_seguidilla2" : validacion_ext_seguidilla2,
                            "trio_seguidilla" : False,
                            "seguidilla_seguidilla" : True,
                            "ronda": self.server.ronda,
                        })
                        informacion = [mensaje["id_jugador"],cartas_expandir]
                    elif validacion_ext_seguidilla1 != False:
                        if validacion_ext_seguidilla1 == "inicio":
                            for carta in cartas_expandir:
                                for i, _carta in enumerate(self.server.manos[id_jugador-1]):
                                    _carta = _carta.to_dict()
                                    if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                        self.server.manos[id_jugador-1].pop(i)
                                        break
                            self.server.jugadas_por_jugador[id_donde_bajarse][0][-1].insert(0, cartas_expandir[0])
                            print("Seguidilla extendida al inicio")
                            mano_nueva = self.server.convertir_mano_dic(id_jugador)
                            self.server.extender_confirmado(id_jugador,id_donde_bajarse)
                        elif validacion_ext_seguidilla1 == "final":
                            for carta in cartas_expandir:
                                for i, _carta in enumerate(self.server.manos[id_jugador-1]):
                                    _carta = _carta.to_dict()
                                    if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                        self.server.manos[id_jugador-1].pop(i)
                                        break
                            self.server.jugadas_por_jugador[id_donde_bajarse][0][-1].extend(cartas_expandir)
                            print("Seguidilla extendida al final")
                            self.server.extender_confirmado(id_jugador,id_donde_bajarse)      
                        elif validacion_ext_seguidilla1 == "ambos":
                            print("Se debe elegir donde extender la seguidilla")
                            self.server.enviar_a_cliente(id_jugador,{
                            "type" : "elejir_donde_extender",
                            "posicion_seguidilla" : "seguidilla1",
                            "trio_seguidilla" : False,
                            "seguidilla_seguidilla" : False,
                            })
                            informacion = [mensaje["id_jugador"],cartas_expandir]
                    elif validacion_ext_seguidilla2 != False:
                        if validacion_ext_seguidilla2 == "inicio":
                            for carta in cartas_expandir:
                                for i, _carta in enumerate(self.server.manos[id_jugador-1]):
                                    _carta = _carta.to_dict()
                                    if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                        self.server.manos[id_jugador-1].pop(i)
                                        break
                            self.server.jugadas_por_jugador[id_donde_bajarse][-1][-1].insert(0, cartas_expandir[0])
                            print("Seguidilla extendida al inicio")
                            mano_nueva = self.server.convertir_mano_dic(id_jugador)
                            self.server.extender_confirmado(id_jugador,id_donde_bajarse)
                        elif validacion_ext_seguidilla2 == "final":
                            for carta in cartas_expandir:
                                for i, _carta in enumerate(self.server.manos[id_jugador-1]):
                                    _carta = _carta.to_dict()
                                    if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                        self.server.manos[id_jugador-1].pop(i)
                                        break
                            self.server.jugadas_por_jugador[id_donde_bajarse][-1][-1].extend(cartas_expandir)
                            print("Seguidilla extendida al final")
                            self.server.extender_confirmado(id_jugador,id_donde_bajarse)      
                        elif validacion_ext_seguidilla2 == "ambos":
                            print("Se debe elegir donde extender la seguidilla")
                            self.server.enviar_a_cliente(id_jugador,{
                            "type" : "elejir_donde_extender",
                            "posicion_seguidilla" : "seguidilla2",
                            "trio_seguidilla" : False,
                            "seguidilla_seguidilla" : False,
                            })
                            informacion = [mensaje["id_jugador"],cartas_expandir]
            elif self.server.ronda == 3:
                print(self.server.jugadas_por_jugador)
                for x,y in self.server.jugadas_por_jugador.items():
                    if x == id_donde_bajarse:
                        if y:
                            jugada = y
                            jugada_trio1 = y[0]
                            jugada_trio2 = y[-1]
                            jugada_trio3 = y[-2]
                            break
                if jugada and cartas_expandir != False :
                    print(jugada)
                    validacion_ext_trio1 = self.server.validar_extender_trio(cartas_expandir[0],jugada_trio1[-1])
                    validacion_ext_trio2 = self.server.validar_extender_trio(cartas_expandir[0],jugada_trio2[-1])
                    validacion_ext_trio3 = self.server.validar_extender_trio(cartas_expandir[0],jugada_trio3[-1])
                    if validacion_ext_trio1 != False:
                        for carta in cartas_expandir:
                            for i, _carta in enumerate(self.server.manos[id_jugador-1]):
                                _carta = _carta.to_dict()
                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                    self.server.manos[id_jugador-1].pop(i)
                                    break
                        self.server.jugadas_por_jugador[id_donde_bajarse][0][-1].extend(cartas_expandir)
                        self.server.extender_confirmado(id_jugador,id_donde_bajarse)
                    elif validacion_ext_trio2 != False:
                        for carta in cartas_expandir:
                            for i, _carta in enumerate(self.server.manos[id_jugador-1]):
                                _carta = _carta.to_dict()
                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                    self.server.manos[id_jugador-1].pop(i)
                                    break
                        self.server.jugadas_por_jugador[id_donde_bajarse][1][-1].extend(cartas_expandir)
                        self.server.extender_confirmado(id_jugador,id_donde_bajarse)
                    elif validacion_ext_trio3 != False:
                        for carta in cartas_expandir:
                            for i, _carta in enumerate(self.server.manos[id_jugador-1]):
                                _carta = _carta.to_dict()
                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                    self.server.manos[id_jugador-1].pop(i)
                                    break
                        self.server.jugadas_por_jugador[id_donde_bajarse][2][-1].extend(cartas_expandir)
                        self.server.extender_confirmado(id_jugador,id_donde_bajarse)
                        return


        if mensaje["type"] == "elecion_donde_extender":
            print(mensaje)
            if self.server.ronda == 1:
                if mensaje["donde_extender"] == "trio":
                    id_donde_bajarse = self.server.informacion_extender[0]
                    cartas_expandir = self.server.informacion_extender[-1]
                    for carta in cartas_expandir:
                        for i, _carta in enumerate(self.server.manos[id_jugador-1]):
                            _carta = _carta.to_dict()
                            if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                self.server.manos[id_jugador-1].pop(i)
                                break
                    self.server.jugadas_por_jugador[id_donde_bajarse][0][-1].extend(cartas_expandir)
                    self.server.extender_confirmado(id_jugador,id_donde_bajarse)
                if mensaje["donde_extender"] == "seguidilla":
                    if mensaje["posicion_seguidilla"] == "inicio":
                        id_donde_bajarse = self.server.informacion_extender[0]
                        cartas_expandir = self.server.informacion_extender[-1]
                        for carta in cartas_expandir:
                            for i, _carta in enumerate(self.server.manos[id_jugador-1]):
                                _carta = _carta.to_dict()
                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                    self.server.manos[id_jugador-1].pop(i)
                                    break
                        self.server.jugadas_por_jugador[id_donde_bajarse][-1][-1].insert(0, cartas_expandir[0])
                        print("Seguidilla extendida al inicio")
                        self.server.extender_confirmado(id_jugador,id_donde_bajarse)
                    elif mensaje["posicion_seguidilla"] == "final":
                        id_donde_bajarse = self.server.informacion_extender[0]
                        cartas_expandir = self.server.informacion_extender[-1]
                        for carta in cartas_expandir:
                            for i, _carta in enumerate(self.server.manos[id_jugador-1]):
                                _carta = _carta.to_dict()
                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                    self.server.manos[id_jugador-1].pop(i)
                                    break
                        self.server.jugadas_por_jugador[id_donde_bajarse][-1][-1].extend(cartas_expandir)
                        print("Seguidilla extendida al final")
                        self.server.extender_confirmado(id_jugador,id_donde_bajarse)
            elif self.server.ronda == 2:
                if mensaje["donde_extender"] == "seguidilla1":
                    if mensaje["posicion_seguidilla"] == "inicio":
                        id_donde_bajarse = informacion[0]
                        cartas_expandir = informacion[-1]
                        for carta in cartas_expandir:
                            for i, _carta in enumerate(self.server.manos[id_jugador-1]):
                                _carta = _carta.to_dict()
                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                    self.server.manos[id_jugador-1].pop(i)
                                    break
                        self.server.jugadas_por_jugador[id_donde_bajarse][0][-1].insert(0, cartas_expandir[0])
                        print("Seguidilla extendida al inicio")
                        mano_nueva = self.server.convertir_mano_dic(id_jugador)
                        self.server.extender_confirmado(id_jugador,id_donde_bajarse)
                    elif mensaje["posicion_seguidilla"] == "final":
                        id_donde_bajarse = informacion[0]
                        cartas_expandir = informacion[-1]
                        for carta in cartas_expandir:
                            for i, _carta in enumerate(self.server.manos[id_jugador-1]):
                                _carta = _carta.to_dict()
                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                    self.server.manos[id_jugador-1].pop(i)
                                    break
                        self.server.jugadas_por_jugador[id_donde_bajarse][0][-1].extend(cartas_expandir)
                        print("Seguidilla extendida al final")
                        self.server.extender_confirmado(id_jugador,id_donde_bajarse)
                elif mensaje["donde_extender"] == "seguidilla2":
                    if mensaje["posicion_seguidilla"] == "inicio":
                        id_donde_bajarse = informacion[0]
                        cartas_expandir = informacion[-1]
                        for carta in cartas_expandir:
                            for i, _carta in enumerate(self.server.manos[id_jugador-1]):
                                _carta = _carta.to_dict()
                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                    self.server.manos[id_jugador-1].pop(i)
                                    break
                        self.server.jugadas_por_jugador[id_donde_bajarse][-1][-1].insert(0, cartas_expandir[0])
                        print("Seguidilla extendida al inicio")
                        mano_nueva = self.server.convertir_mano_dic(id_jugador)
                        self.server.extender_confirmado(id_jugador,id_donde_bajarse)
                    elif mensaje["posicion_seguidilla"] == "final":
                        id_donde_bajarse = informacion[0]
                        cartas_expandir = informacion[-1]
                        for carta in cartas_expandir:
                            for i, _carta in enumerate(self.server.manos[id_jugador-1]):
                                _carta = _carta.to_dict()
                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                    self.server.manos[id_jugador-1].pop(i)
                                    break
                        self.server.jugadas_por_jugador[id_donde_bajarse][-1][-1].extend(cartas_expandir)
                        print("Seguidilla extendida al final")
                        self.server.extender_confirmado(id_jugador,id_donde_bajarse)
            elif self.server.ronda == 3:
                if mensaje["donde_extender"] == "trio1":
                    id_donde_bajarse = informacion[0]
                    cartas_expandir = informacion[-1]
                    for carta in cartas_expandir:
                        for i, _carta in enumerate(self.server.manos[id_jugador-1]):
                            _carta = _carta.to_dict()
                            if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                self.server.manos[id_jugador-1].pop(i)
                                break
                    self.server.jugadas_por_jugador[id_donde_bajarse][0][-1].extend(cartas_expandir)
                    self.server.extender_confirmado(id_jugador,id_donde_bajarse)
                if mensaje["donde_extender"] == "trio2":
                    id_donde_bajarse = informacion[0]
                    cartas_expandir = informacion[-1]
                    for carta in cartas_expandir:
                        for i, _carta in enumerate(self.server.manos[id_jugador-1]):
                            _carta = _carta.to_dict()
                            if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                self.server.manos[id_jugador-1].pop(i)
                                break
                    self.server.jugadas_por_jugador[id_donde_bajarse][1][-1].extend(cartas_expandir)
                    self.server.extender_confirmado(id_jugador,id_donde_bajarse)
                if mensaje["donde_extender"] == "trio3":
                    id_donde_bajarse = informacion[0]
                    cartas_expandir = informacion[-1]
                    for carta in cartas_expandir:
                        for i, _carta in enumerate(self.server.manos[id_jugador-1]):
                            _carta = _carta.to_dict()
                            if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                self.server.manos[id_jugador-1].pop(i)
                                break
                    self.server.jugadas_por_jugador[id_donde_bajarse][2][-1].extend(cartas_expandir)
                    self.server.extender_confirmado(id_jugador,id_donde_bajarse)
        if mensaje["type"] == "reemplazar":
            print(mensaje)
            print("sei llega el msj")
            carta_a_remplazar = []
            if mensaje["carta_descartada"] != None:
                id_jugador_reemplazado = None
                carta_a_remplazar.append(mensaje["carta_descartada"])
                print("carta valida")
                validaciones_extender = []
                for id_j, jugadas_list in list(self.server.jugadas_por_jugador.items()):
                    for idx, entry in enumerate(jugadas_list):
                        # entry expected to be (tag, grupo)
                        try:
                            tag, grupo = entry
                        except Exception:
                            continue
                        if tag == "Seguidilla":
                            valor = self.server.validar_reemplazar_joker_seguidilla(mensaje["carta_descartada"], grupo)                                        
                            if valor is not None:
                                # guardar validación y reemplazar la jugada en la estructura original
                                validaciones_extender.append(valor)
                                self.server.jugadas_por_jugador[id_j][idx] = (tag, valor)
                                id_jugador_reemplazado = id_j
                                break
                if validaciones_extender != []:
                    for carta in self.server.manos[id_jugador-1]:
                        try:
                            carta_serealizada = carta.to_dict()
                        except:
                            carta_serealizada = carta
                        if carta_serealizada["numero"] == mensaje["carta_descartada"]["numero"] and carta_serealizada["figura"] == mensaje["carta_descartada"]["figura"]:
                            self.server.manos[id_jugador-1].remove(carta) 
                            self.server.manos[id_jugador-1].append(Carta(un_juego=None, numero="Joker", figura="Especial"))
                            break
                    self.server.difundir_excepcion(id_jugador_reemplazado,{
                        "type": "se_extendio",
                        "cantidad_manos_jugadores": self.server.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                        "jugadas_jugadores": self.server.jugadas_por_jugador,
                    })
                    self.server.enviar_a_cliente(id_jugador,{
                        "type": "reemplazar_valido",
                        "nueva_mano": self.server.convertir_mano_dic(id_jugador),
                        "jugadas_jugadores": self.server.jugadas_por_jugador,
                        "jugada" :self.server.jugadas_por_jugador[id_jugador],
                        })
                    self.server.enviar_a_cliente(id_jugador_reemplazado,{
                        "type": "reemplazaron_tu_jugada",
                        "cantidad_manos_jugadores": self.server.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                        "jugadas_jugadores": self.server.jugadas_por_jugador,
                        "jugadas_jugadores": self.server.jugadas_por_jugador,
                        "jugada" :self.server.jugadas_por_jugador[id_jugador_reemplazado],
                        })
