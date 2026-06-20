"""Módulo interno para procesamiento de mensajes del juego"""

import socket
import threading
import json
import copy
import time
from redes_juego import archivo_de_importaciones
from redes_juego.packets import unpack_message, validate_message_schema, pack_message

importar_desde_carpeta = archivo_de_importaciones.importar_desde_carpeta
Carta = importar_desde_carpeta(
    nombre_archivo="cartas_interfaz.py",
    nombre_clase="Cartas_interfaz",
    nombre_carpeta="logica_interfaz"
)

class ProcesadorMensajesMixin:
    """Mixin con métodos para procesar mensajes del juego"""

    def _ejecutar_limpieza_jugador(self, id_jugador):
        """Maneja el estado, la persistencia de red y la inyección en la lógica Core"""
        with self.candado:
            if id_jugador - 1 < len(self.clientes) and self.clientes[id_jugador-1].get("status") == "desconectado":
                return

            nombre_jugador = self.clientes[id_jugador-1]['nombre'] if id_jugador-1 < len(self.clientes) else f"Jugador {id_jugador}"
            print(f"[Redes] Ejecutando limpieza preventiva para {nombre_jugador} (ID: {id_jugador})")

            # =====================================================================
            # INJECCIÓN DE LOGICA CORE: Limpieza de cartas y rebarajado automático
            # =====================================================================
            try:
                # Invocación directa a la lógica de negocio solicitada en el memorándum
                self.mesa_juego.gestionar_desconexion_jugador(id_jugador, self.manos, self.mazo)
                print(f"[Redes] Conexión core sincronizada: Cartas de ID {id_jugador} devueltas al mazo.")
            except Exception as e:
                print(f"[Redes] Advertencia al inyectar limpieza en Core: {e}")
            # =====================================================================

            # Guardar datos del jugador desconectado en la persistencia del servidor
            self.jugadores_desconectados[id_jugador] = {
                'estado_juego': getattr(self, 'estado_juego', None),
                'nombre': nombre_jugador
            }

            if id_jugador == 1:
                print("[Redes] Host desconectado. Cerrando servidor de juego...")
                try: self.desconectar_servidor()
                except Exception as e: print(f"[Redes] Error en shutdown: {e}")
                return

            if id_jugador - 1 < len(self.clientes):
                self.clientes[id_jugador-1]["status"] = "desconectado"

            jugadores_activos = [
                c for c in self.clientes
                if c.get("status") != "desconectado"
            ]

            lista_jugadores_activos = [
                c["nombre"] for c in jugadores_activos
            ]

            if self.mesa_juego:
                self.mesa_juego.elementos_mesa["datos_lista_jugadores"] = [
                    (c["id"], c["nombre"]) for c in jugadores_activos
                ]

                self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = [
                    item for item in self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"]
                    if item["id"] != id_jugador
                ]

            ids_activos = [c["id"] for c in jugadores_activos]

            jugador_mano_actual = self.mesa_juego.elementos_mesa.get("jugador_mano")

            if jugador_mano_actual and jugador_mano_actual[0] not in ids_activos:
                if ids_activos:
                    siguiente = ids_activos[0]
                    nombre_siguiente = next(c["nombre"] for c in jugadores_activos if c["id"] == siguiente)
                    self.mesa_juego.elementos_mesa["jugador_mano"] = (siguiente, nombre_siguiente)

            print("=== SERVIDOR DIFUNDIENDO DESCONEXIÓN ===")
            print("id desconectado:", id_jugador)
            print("jugadores_activos:", jugadores_activos)
            print("datos_lista_jugadores:", self.mesa_juego.elementos_mesa.get("datos_lista_jugadores") if self.mesa_juego else None)
            print("cantidad_manos_jugadores:", self.mesa_juego.elementos_mesa.get("cantidad_manos_jugadores") if self.mesa_juego else None)
            print("jugador_mano:", self.mesa_juego.elementos_mesa.get("jugador_mano") if self.mesa_juego else None)

            self.difundir({
                "type": "JugadorDesconectado",
                "id_jugador": id_jugador,
                "TotalJugadores": len(lista_jugadores_activos),
                "nombre": nombre_jugador,
                "lista_jugadores": lista_jugadores_activos,
                "datos_lista_jugadores": self.mesa_juego.elementos_mesa["datos_lista_jugadores"] if self.mesa_juego else [],
                "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] if self.mesa_juego else [],
                "jugador_mano": self.mesa_juego.elementos_mesa["jugador_mano"]
            })

            if len(jugadores_activos) == 1 and getattr(self, 'estado_partida', False):
                print("[Redes] Sala vacía detectada. Cerrando el servidor automáticamente...")
                try: self.desconectar_servidor()
                except Exception as e: print(f"[Redes] Error al cerrar por sala vacía: {e}")
                return
    
    def _manejar_cliente_mensajes(self, socket_cliente, id_jugador):
        """Procesa todos los mensajes recibidos de un cliente con header de 10 bytes"""
        buffer = b""
        try:
            while self.ejecutandose:
                try:
                    data = socket_cliente.recv(4096)
                    if not data:
                        print(f"[Redes] Socket cerrado limpiamente por el cliente {id_jugador}.")
                        break
                except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError) as e:
                    print(f"[Redes] Ruptura de socket detectada en cliente {id_jugador}: {e}")
                    break
                except socket.timeout:
                    continue

                buffer += data
                
                # Procesar mensajes completos
                while True:
                    mensaje, error = unpack_message(buffer)
                    if error:
                        if "insuficiente" in error.lower() or "incompleto" in error.lower():
                            break
                        print(f"Error al desempaquetar mensaje del cliente {id_jugador}: {error}")
                        buffer = b""
                        break
                    
                    if mensaje is None:
                        break
                    
                    # Calcular bytes consumidos
                    json_bytes = json.dumps(mensaje, ensure_ascii=False).encode('utf-8')
                    bytes_consumidos = 10 + len(json_bytes)
                    buffer = buffer[bytes_consumidos:]
                    
                    # Validar esquema del mensaje
                    valido, error_schema = validate_message_schema(mensaje)
                    if not valido:
                        print(f"Esquema inválido de cliente {id_jugador}: {error_schema}")
                        continue
                    
                    # Manejar PING_HOST especial
                    if mensaje.get('type') == 'PING_HOST':
                        socket_cliente.sendall(pack_message({'type': 'PONG_HOST'}))
                        continue
                    
                    if mensaje.get('type') == 'PONG_HOST':
                        tiempo_final = time.perf_counter()
                        if id_jugador - 1 < len(self.clientes):
                            cliente = self.clientes[id_jugador-1]
                            latencia = (tiempo_final - cliente.get('tiempo_ping_enviado', tiempo_final)) * 1000
                            cliente['latencia'] = latencia
                            print(f"Monitor Heartbeat - Latencia Jugador {id_jugador}: {latencia:.2f} ms")
                        continue

                    # ============================================================
                    # PROCESAMIENTO DE MENSAJES DEL JUEGO
                    # ============================================================
                    
                    nombre_jugador = mensaje.get('nombre', f'Jugador{id_jugador}')
                    with self.candado:
                        self.cola_mensajes.append((id_jugador, mensaje))

                        # RECONECTAR
                        if mensaje.get('type') == 'Reconectar':
                            print(f"[Reconectar] Procesando reconexión para ID: {mensaje.get('id_jugador')}")
                            id_jugador_reconectar = mensaje.get('id_jugador')
                            datos_guardados = self.jugadores_desconectados.get(id_jugador_reconectar)
                            if datos_guardados:
                                # Reasignar el mismo ID y restaurar datos
                                self.clientes[id_jugador_reconectar-1].update({
                                    'socket': socket_cliente,
                                    'id': id_jugador_reconectar,
                                    'nombre': datos_guardados['nombre'],
                                    'thread': threading.current_thread(),
                                    "status": "activo"
                                })

                                if len(self.puntos_acumulados) > 0:
                                    print(self.puntos_acumulados)
                                    try:
                                        if self.puntos_acumulados[id_jugador] >= 500:
                                            self.clientes[id_jugador_reconectar-1].update({
                                                'socket': socket_cliente,
                                                'id': id_jugador_reconectar,
                                                'nombre': datos_guardados['nombre'],
                                                'thread': threading.current_thread(),
                                                "status": "inactivo"
                                            })
                                    except:
                                        pass

                                self.enviar_a_cliente(id_jugador_reconectar, {
                                    'type': 'Reconectado',
                                    'id_jugador': id_jugador_reconectar,
                                    'estado_juego': datos_guardados['estado_juego'],
                                    'nombre': datos_guardados['nombre']
                                })
                                del self.jugadores_desconectados[id_jugador_reconectar]
                                # Difundir la reconexión a otros jugadores
                                self.difundir({
                                    'type': 'JugadorReconectado',
                                    'id_jugador': id_jugador_reconectar,
                                    'nombre': datos_guardados['nombre'],
                                    "lista_jugadores": [c['nombre'] for c in self.clientes]
                                })
                                mano = self.manos[id_jugador_reconectar - 1]
                                try:
                                    datos_serializables_mano = [c.to_dict() for c in mano]
                                except:
                                    datos_serializables_mano = [c for c in mano]
                                if self.mesa_juego and self.mesa_juego.elementos_mesa.get("dato_carta_descarte") and len(self.mesa_juego.elementos_mesa["dato_carta_descarte"]) != 1:
                                    descarte = self.mesa_juego.elementos_mesa["dato_carta_descarte"] 
                                elif self.mesa_juego and self.mesa_juego.elementos_mesa.get("dato_carta_descarte") == None:
                                    descarte = None
                                else:
                                    descarte = self.mesa_juego.elementos_mesa["dato_carta_descarte"][0] if self.mesa_juego else None
                                if self.estado_partida and self.mesa_juego:
                                    self.enviar_a_cliente(id_jugador_reconectar, {
                                        'type': 'Reconectar_partida',
                                        "id_jugador": id_jugador_reconectar,
                                        "jugador_mano": self.mesa_juego.elementos_mesa["jugador_mano"],
                                        "mano": datos_serializables_mano,
                                        "jugada": self.jugadas_por_jugador.get(id_jugador_reconectar, []),
                                        "jugadas_jugadores": self.jugadas_por_jugador,
                                        "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                                        "datos_lista_jugadores": self.mesa_juego.elementos_mesa["datos_lista_jugadores"],
                                        "dato_carta_descarte": descarte,
                                        "dato_carta_quema": self.mesa_juego.elementos_mesa.get("dato_carta_quema"),
                                        "mazo": len(self.mazo.cartas) if self.mazo else 0,
                                    })
                                id_jugador = id_jugador_reconectar
                                if len(self.clientes) - len(self.jugadores_desconectados) == self.max_jugadores:
                                    self.anunciar_servidor_estado = False
                                    self.aceptar_conexiones_estado = False
                            else:
                                # No hay datos guardados, tratar como nuevo jugador
                                id_jugador = len(self.clientes) + len(self.jugadores_desconectados) + 1 
                                self.clientes.append({
                                    'socket': socket_cliente,
                                    'id': id_jugador,
                                    'nombre': mensaje.get('nombre'),
                                    'thread': threading.current_thread(),
                                    "status": "activo",
                                })
                                self.enviar_a_cliente(id_jugador, {
                                    'type': 'Bienvenido',
                                    'id_jugador': id_jugador,
                                    'nombre': mensaje.get('nombre'),
                                    'game_state': self.estado_juego
                                })
                                # Difundir la nueva conexión a otros jugadores
                                self.difundir({
                                    'type': 'NuevoJugador',
                                    'id_jugador': id_jugador,
                                    'nombre': mensaje.get('nombre'),
                                    'TotalJugadores': len(self.clientes),
                                    "lista_jugadores": [c['nombre'] for c in self.clientes]
                                })
                            self.verificar_inicio_partida()
                        
                        # NUEVO JUGADOR
                        elif mensaje.get('type') == 'NuevoJugador':
                            print(f"[NuevoJugador] Procesando nuevo jugador: {mensaje.get('nombre')}")
                            id_jugador = len(self.clientes) + len(self.jugadores_desconectados) + 1 
                            self.clientes.append({
                                'socket': socket_cliente,
                                'id': id_jugador,
                                'nombre': mensaje.get('nombre'),
                                'thread': threading.current_thread(),
                                "status": "activo",
                            })
                            self.enviar_a_cliente(id_jugador, {
                                'type': 'Bienvenido',
                                'id_jugador': id_jugador,
                                'nombre': mensaje.get('nombre'),
                                'game_state': self.estado_juego
                            })
                            # Difundir la nueva conexión a otros jugadores
                            self.difundir({
                                'type': 'NuevoJugador',
                                'id_jugador': id_jugador,
                                'nombre': mensaje.get('nombre'),
                                'TotalJugadores': len(self.clientes),
                                "lista_jugadores": [c['nombre'] for c in self.clientes]
                            })
                            self.verificar_inicio_partida()
                        
                        # CLIENTE DESCONECTADO
                        elif mensaje.get('type') == 'ClienteDesconectado':
                            print(f"[ClienteDesconectado] Cliente {id_jugador} desconectado")
                            id_jugador = mensaje.get("id_jugador", id_jugador)
                            break
                            # Guardar datos del jugador desconectado
                            self.jugadores_desconectados[id_jugador] = {
                                'estado_juego': self.estado_juego,
                                'nombre': self.clientes[id_jugador-1]['nombre'] if id_jugador-1 < len(self.clientes) else nombre_jugador
                            }

                            if id_jugador == 1:
                                print("Host desconectado, desconectando a todos los jugadores...")
                                try:
                                    self.desconectar_servidor()
                                except Exception as e:
                                    print(f"Error durante shutdown: {e}")
                                return
                            
                            if id_jugador - 1 < len(self.clientes):
                                self.clientes[id_jugador-1]["status"] = "desconectado"
                            
                            jugadores_activos = [c['nombre'] for c in self.clientes if c.get('status') == 'activo']
                            
                            self.difundir({
                                'type': 'JugadorDesconectado',
                                'id_jugador': id_jugador,
                                'TotalJugadores': len(jugadores_activos),
                                "nombre": self.clientes[id_jugador-1]['nombre'] if id_jugador-1 < len(self.clientes) else nombre_jugador,
                                "lista_jugadores": jugadores_activos
                            })
                            
                            if self.estado_partida:
                                if self.anunciar_servidor_estado != True:
                                    self.aceptar_conexiones_estado = True
                                    self.anunciar_servidor_estado = True
                                    hilo_servidor = threading.Thread(target=self.aceptar_conexiones)
                                    hilo_servidor.daemon = True
                                    hilo_servidor.start()
                                    
                                    hilo_anuncio = threading.Thread(target=self.anunciar_servidor)
                                    hilo_anuncio.daemon = True
                                    hilo_anuncio.start()
                        
                        # TOMAR CARTA DEL DESCARTE
                        elif mensaje.get('type') == 'Tomar_Carta_Descarte':
                            print(f"Mensaje del cliente {id_jugador}: {mensaje}")
                            if id_jugador == self.mesa_juego.elementos_mesa["jugador_mano"][0]:
                                print("jugador mano correcto")
                                try:
                                    if self.mesa_juego.elementos_mesa["dato_carta_descarte"]:
                                        print("hay datos de descarte")
                                        self.mesa_juego.elementos_mesa["dato_carta_descarte"] = None
                                        print(self.descarte)
                                        carta_tomada = self.descarte.pop()
                                        self.manos[id_jugador-1].append(carta_tomada)
                                        self.ultimo_descarte.append(carta_tomada)
                                        self.modificar_cartas(id_jugador, +1)
                                        self.enviar_a_cliente(id_jugador, {
                                            "type": "Actualizacion_Toma_Descarte",
                                        })
                                        self.difundir_excepcion(id_jugador, {
                                            'type': 'Actualizacion_Carta_Descarte',
                                            'cantidad_manos_jugadores': self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                                            "dato_carta_descarte": self.mesa_juego.elementos_mesa["dato_carta_descarte"],
                                        })
                                except Exception as e:
                                    print(e)
                        
                        # DESCARTE CARTA
                        elif mensaje.get("type") == "Descarte_Carta":
                            if id_jugador == self.mesa_juego.elementos_mesa["jugador_mano"][0]:
                                print(f"Mensaje del cliente {id_jugador}: {mensaje}")
                                carta_descartar = mensaje.get("carta_descartada")
                                
                                if carta_descartar is None:
                                    print(f"ERROR: El jugador {id_jugador} intentó descartar sin seleccionar una carta")
                                    self.enviar_a_cliente(id_jugador, {
                                        "type": "Error_Descartar",
                                        "mensaje": "Debes seleccionar una carta para descartar"
                                    })
                                    continue
                                
                                cartas = []
                                for carta in self.manos[id_jugador-1]:
                                    cartas.append(carta.to_dict())
                                print(f"cartas del jugador {cartas}")
                                
                                if carta_descartar["numero"] == "Joker" and self.jugadas_por_jugador[id_jugador] == []:
                                    self.enviar_a_cliente(id_jugador, {
                                        "type": "No_Puede_Descartar_Joker",
                                    })
                                    print("esto no se puede :P")
                                elif (self.ultimo_descarte and carta_descartar != None) or (len(self.manos[id_jugador-1]) == 1) and len(carta_descartar) == 1:
                                    print(self.ultimo_descarte[-1])
                                    carta_descarte_serealizada = self.ultimo_descarte[-1].to_dict()
                                    print(carta_descarte_serealizada)
                                    
                                    if (carta_descartar["numero"] == carta_descarte_serealizada["numero"] and 
                                        carta_descartar["figura"] == carta_descarte_serealizada["figura"] and 
                                        len(self.manos[id_jugador-1]) > 1):
                                        self.enviar_a_cliente(id_jugador, {
                                            "type": "No_Puede_Descartar_Misma_Carta",
                                        })
                                    elif id_jugador == self.mesa_juego.elementos_mesa["jugador_mano"][0] and ((carta_descartar["numero"] != carta_descarte_serealizada["numero"] or carta_descartar["figura"] != carta_descarte_serealizada["figura"]) or len(self.manos[id_jugador-1]) == 1):
                                        print(self.ultimo_descarte[-1])
                                        carta_ = None
                                        for carta in self.manos[id_jugador-1]:
                                            try:
                                                carta_serealizada = carta.to_dict()
                                            except:
                                                carta_serealizada = carta
                                            if carta_serealizada["numero"] == carta_descartar["numero"] and carta_serealizada["figura"] == carta_descartar["figura"]:
                                                self.manos[id_jugador-1].remove(carta)
                                                print(str(self.manos[id_jugador-1]))
                                                self.mesa_juego.elementos_mesa["dato_carta_descarte"] = mensaje.get("carta_descartada")
                                                self.modificar_cartas(id_jugador, -1) 
                                                print(self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"])
                                                self.descarte.append(carta)
                                                carta_ = carta
                                                self.jugador_que_descarto = id_jugador
                                                break
                                        cartas = []
                                        for carta in self.manos[id_jugador-1]:
                                            cartas.append(carta.to_dict())
                                        print(f"cartas del jugador {cartas}")
                                        if carta_:
                                            self.difundir_excepcion(id_jugador, {
                                                "type": "Actualizacion_Decartar_Carta",
                                                "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                                                "dato_carta_descarte": self.mesa_juego.elementos_mesa["dato_carta_descarte"],
                                            })
                                            self.enviar_a_cliente(id_jugador, {
                                                "type": "Descartar_Carta",
                                            })
                                            try:
                                                if len(self.manos.get(id_jugador-1, [])) == 0:
                                                    print(f"Jugador {id_jugador} se quedó sin cartas: difundir puntuaciones finales")
                                                    self.difundir_puntuaciones_finales(id_jugador)
                                            except Exception as e:
                                                print(f"Error al verificar mano vacía para jugador {id_jugador}: {e}")

                                            resultado_quema = self.quema_del_mono(id_jugador, carta_descartar)
                                            if resultado_quema[0]:
                                                self.enviar_a_cliente(id_jugador, resultado_quema[1])
                                            else:
                                                jugadores = self.mesa_juego.elementos_mesa["datos_lista_jugadores"]
                                                idx_actual = next((i for i, j in enumerate(jugadores) if j[0] == id_jugador), None)
                                                num = 0
                                                if idx_actual is not None:
                                                    for jugador in jugadores:
                                                        idx_siguiente = (idx_actual + num + 1) % len(jugadores)
                                                        id_siguiente = jugadores[idx_siguiente][0]
                                                        nombre = jugadores[idx_siguiente][1]
                                                        num += 1
                                                        if self.clientes[id_siguiente-1]["status"] == "activo":
                                                            break
                                                self.mesa_juego.elementos_mesa.update({"jugador_mano": (id_siguiente, nombre)})
                                                self.finalizar_turno(id_jugador, id_siguiente)
                                
                                elif (self.contador_turno_compra == 0 and carta_descartar != None) or (len(self.manos[id_jugador-1]) == 1):
                                    cartas = []
                                    for carta in self.manos[id_jugador-1]:
                                        cartas.append(carta.to_dict())
                                    print(f"cartas del jugador {cartas}")
                                    carta_ = None
                                    for carta in self.manos[id_jugador-1]:
                                        try:
                                            carta_serealizada = carta.to_dict()
                                        except:
                                            carta_serealizada = carta
                                        if carta_serealizada["numero"] == carta_descartar["numero"] and carta_serealizada["figura"] == carta_descartar["figura"]:
                                            self.manos[id_jugador-1].remove(carta)
                                            print(str(self.manos[id_jugador-1]))
                                            self.mesa_juego.elementos_mesa["dato_carta_descarte"] = mensaje.get("carta_descartada")
                                            self.modificar_cartas(id_jugador, -1)
                                            self.descarte.append(carta)
                                            carta_ = carta
                                            self.jugador_que_descarto = id_jugador
                                            break
                                    cartas = []
                                    for carta in self.manos[id_jugador-1]:
                                        cartas.append(carta.to_dict())
                                    print(f"cartas del jugador {cartas}")
                                    print(self.mesa_juego.elementos_mesa["dato_carta_descarte"])
                                    if carta_:
                                        self.difundir_excepcion(id_jugador, {
                                            "type": "Actualizacion_Decartar_Carta",
                                            "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                                            "dato_carta_descarte": self.mesa_juego.elementos_mesa["dato_carta_descarte"],
                                        })
                                        self.enviar_a_cliente(id_jugador, {
                                            "type": "Descartar_Carta",
                                        })
                                        resultado_quema = self.quema_del_mono(id_jugador, carta_descartar)
                                        mano_vacia = self.verificar_mano_vacia_y_difundir(id_jugador)
                                        if resultado_quema[0] and mano_vacia is None:
                                            self.enviar_a_cliente(id_jugador, resultado_quema[1])
                                        elif mano_vacia is None:
                                            jugadores = self.mesa_juego.elementos_mesa["datos_lista_jugadores"]
                                            idx_actual = next((i for i, j in enumerate(jugadores) if j[0] == id_jugador), None)
                                            num = 0
                                            if idx_actual is not None:
                                                for jugador in jugadores:
                                                    idx_siguiente = (idx_actual + num + 1) % len(jugadores)
                                                    id_siguiente = jugadores[idx_siguiente][0]
                                                    nombre = jugadores[idx_siguiente][1]
                                                    num += 1
                                                    if self.clientes[id_siguiente-1]["status"] == "activo":
                                                        break
                                            self.mesa_juego.elementos_mesa.update({"jugador_mano": (id_siguiente, nombre)})
                                            self.finalizar_turno(id_jugador, id_siguiente)
                        
                        # NO TOMAR DESCARTE
                        elif mensaje.get("type") == "No_tomar_descarte":
                            print(f"Mensaje del cliente {id_jugador}: {mensaje}")
                            if self.contador_turno_compra != len(self.clientes)-1:
                                jugadores = self.mesa_juego.elementos_mesa["datos_lista_jugadores"]
                                idx_actual = next((i for i, j in enumerate(jugadores) if j[0] == id_jugador), None)
                                if idx_actual is not None:
                                    num = 0
                                    for jugador in jugadores:
                                        idx_siguiente = (idx_actual + num + 1) % len(jugadores)
                                        id_siguiente = jugadores[idx_siguiente][0]
                                        nombre = jugadores[idx_siguiente][1]
                                        num += 1
                                        if self.clientes[id_siguiente-1]["status"] == "activo":
                                            break
                                    print(f"Siguiente jugador para oferta de descarte: {id_siguiente}")
                                    
                                    if id_siguiente == self.jugador_que_descarto and id_siguiente != id_jugador or id_siguiente == self.mesa_juego.elementos_mesa["jugador_mano"][0]:
                                        print(f"El siguiente jugador ({id_siguiente}) es el que descartó la carta o hay jugadores desconectados. Terminando ronda de compra.")
                                        id_jugador_que_descarto = self.jugador_que_descarto
                                        
                                        if self.descarte:
                                            self.quema.append(self.descarte.pop())
                                        self.ultimo_descarte = []
                                        self.mesa_juego.elementos_mesa["dato_carta_descarte"] = None
                                        self.mesa_juego.elementos_mesa["cantidad_cartas_quema"] += 1
                                        self.mesa_juego.elementos_mesa["dato_carta_quema"] = self.quema[-1].to_dict()
                                        self.contador_turno_compra = 0
                                        self.jugador_compra = None
                                        self.jugador_que_descarto = None
                                        
                                        idx_jugador_que_descarto = next((i for i, j in enumerate(jugadores) if j[0] == id_jugador_que_descarto), None)
                                        if idx_jugador_que_descarto is not None and id_siguiente != self.mesa_juego.elementos_mesa["jugador_mano"][0]:
                                            print("caso mismo jugador que descarto")
                                            idx_siguiente_despues_descarte = (idx_jugador_que_descarto + 1) % len(jugadores)
                                            id_siguiente_despues_descarte = jugadores[idx_siguiente_despues_descarte][0]
                                            nombre_siguiente = jugadores[idx_siguiente_despues_descarte][1]
                                            self.mesa_juego.elementos_mesa.update({"jugador_mano": (id_siguiente_despues_descarte, nombre_siguiente)})
                                            
                                            self.enviar_a_cliente(id_jugador, {
                                                "type": "No_descartar",
                                                "turno_robar": False,
                                            })
                                            self.enviar_a_cliente(id_siguiente_despues_descarte, {
                                                "type": "Actualizar_botones",
                                                "turno_robar": True,
                                                "dato_carta_descarte": None,
                                                "cantidad_cartas_quema": self.mesa_juego.elementos_mesa["cantidad_cartas_quema"],
                                                "dato_carta_quema": self.mesa_juego.elementos_mesa["dato_carta_quema"]
                                            })
                                            self.difundir_excepcion(id_siguiente_despues_descarte, {
                                                "type": "Actualizar_botones",
                                                "turno_robar": False,
                                                "dato_carta_descarte": None,
                                                "cantidad_cartas_quema": self.mesa_juego.elementos_mesa["cantidad_cartas_quema"],
                                                "dato_carta_quema": self.mesa_juego.elementos_mesa["dato_carta_quema"]
                                            })
                                            if id_jugador_que_descarto != id_siguiente_despues_descarte:
                                                self.enviar_a_cliente(id_jugador_que_descarto, {
                                                    "type": "Reactivar_Botones_No_Turno",
                                                })
                                        elif id_siguiente == self.mesa_juego.elementos_mesa["jugador_mano"][0]:
                                            self.enviar_a_cliente(self.mesa_juego.elementos_mesa["jugador_mano"][0], {
                                                "type": "Actualizar_botones",
                                                "turno_robar": True,
                                                "dato_carta_descarte": None,
                                                "cantidad_cartas_quema": self.mesa_juego.elementos_mesa["cantidad_cartas_quema"],
                                                "dato_carta_quema": self.mesa_juego.elementos_mesa["dato_carta_quema"]
                                            })
                                            self.difundir_excepcion(self.mesa_juego.elementos_mesa["jugador_mano"][0], {
                                                "type": "Actualizar_botones",
                                                "turno_robar": False,
                                                "dato_carta_descarte": None,
                                                "cantidad_cartas_quema": self.mesa_juego.elementos_mesa["cantidad_cartas_quema"],
                                                "dato_carta_quema": self.mesa_juego.elementos_mesa["dato_carta_quema"]
                                            })
                                    elif id_jugador == id_siguiente:
                                        print("Todos los jugadores rechazaron comprar la carta descartada.")
                                        self.quema.append(self.descarte.pop())
                                        self.ultimo_descarte = []
                                        self.mesa_juego.elementos_mesa["dato_carta_descarte"] = None
                                        self.mesa_juego.elementos_mesa["cantidad_cartas_quema"] += 1
                                        self.mesa_juego.elementos_mesa["dato_carta_quema"] = self.quema[-1].to_dict()
                                        self.contador_turno_compra = 0
                                        self.enviar_a_cliente(self.mesa_juego.elementos_mesa["jugador_mano"][0], {
                                            "type": "Actualizar_botones",
                                            "turno_robar": True,
                                            "dato_carta_descarte": None,
                                            "cantidad_cartas_quema": self.mesa_juego.elementos_mesa["cantidad_cartas_quema"],
                                            "dato_carta_quema": self.mesa_juego.elementos_mesa["dato_carta_quema"]
                                        })
                                        self.difundir_excepcion(self.mesa_juego.elementos_mesa["jugador_mano"][0], {
                                            "type": "Actualizar_botones",
                                            "turno_robar": False,
                                            "dato_carta_descarte": None,
                                            "cantidad_cartas_quema": self.mesa_juego.elementos_mesa["cantidad_cartas_quema"],
                                            "dato_carta_quema": self.mesa_juego.elementos_mesa["dato_carta_quema"]
                                        })
                                        self.contador_turno_compra = 0    
                                        self.jugador_compra = None
                                        if self.jugador_que_descarto and self.jugador_que_descarto != self.mesa_juego.elementos_mesa["jugador_mano"][0]:
                                            self.enviar_a_cliente(self.jugador_que_descarto, {
                                                "type": "Reactivar_Botones_No_Turno",
                                            })
                                        self.jugador_que_descarto = None
                                        self.ultimo_descarte = []
                                    elif (self.jugador_compra is None and id_jugador == self.mesa_juego.elementos_mesa["jugador_mano"][0]) or id_jugador == self.jugador_compra:
                                        self.jugador_compra = id_siguiente
                                        if self.contador_turno_compra == 0:
                                            self.enviar_a_cliente(id_jugador, {
                                                "type": "Rechazar_descarte",
                                                "turno_robar": False,
                                            })
                                            self.enviar_a_cliente(id_siguiente, {
                                                "type": "No_descartar",
                                                "turno_robar": True,
                                            })
                                        else:
                                            self.enviar_a_cliente(id_jugador, {
                                                "type": "No_descartar",
                                                "turno_robar": False,
                                            })
                                            self.enviar_a_cliente(id_siguiente, {
                                                "type": "No_descartar",
                                                "turno_robar": True,
                                            })
                                        self.contador_turno_compra += 1
                            else:
                                print("Funciona :P, ya eres el ultimo en comprar")
                                self.quema.append(self.descarte.pop())
                                self.ultimo_descarte = []
                                self.mesa_juego.elementos_mesa["dato_carta_descarte"] = None
                                self.mesa_juego.elementos_mesa["cantidad_cartas_quema"] += 1
                                self.mesa_juego.elementos_mesa["dato_carta_quema"] = self.quema[-1].to_dict()
                                self.contador_turno_compra = 0
                                self.enviar_a_cliente(self.mesa_juego.elementos_mesa["jugador_mano"][0], {
                                    "type": "Actualizar_botones",
                                    "turno_robar": True,
                                    "dato_carta_descarte": None,
                                    "cantidad_cartas_quema": self.mesa_juego.elementos_mesa["cantidad_cartas_quema"],
                                    "dato_carta_quema": self.mesa_juego.elementos_mesa["dato_carta_quema"]
                                })
                                self.difundir_excepcion(self.mesa_juego.elementos_mesa["jugador_mano"][0], {
                                    "type": "Actualizar_botones",
                                    "turno_robar": False,
                                    "dato_carta_descarte": None,
                                    "cantidad_cartas_quema": self.mesa_juego.elementos_mesa["cantidad_cartas_quema"],
                                    "dato_carta_quema": self.mesa_juego.elementos_mesa["dato_carta_quema"]
                                })
                                self.contador_turno_compra = 0    
                                self.jugador_compra = None
                                if self.jugador_que_descarto and self.jugador_que_descarto != self.mesa_juego.elementos_mesa["jugador_mano"][0]:
                                    self.enviar_a_cliente(self.jugador_que_descarto, {
                                        "type": "Reactivar_Botones_No_Turno",
                                    })
                                self.jugador_que_descarto = None
                                self.ultimo_descarte = []
                        
                        # COMPRAR
                        elif mensaje.get("type") == "comprar":
                            print(mensaje)
                            self.mazo_nuevo(dir="comprar")
                            if self.descarte:
                                carta_descarte_serealizada = self.descarte[0].to_dict()
                            else:
                                carta_descarte_serealizada = None
                            print(self.mazo.cartas[-1])
                            if id_jugador == self.jugador_compra:
                                carta_extra = self.mazo.cartas.pop()
                                self.manos[id_jugador-1].append(carta_extra)
                                self.manos[id_jugador-1].append(self.descarte[-1])
                                self.descarte = []
                                self.modificar_cartas(id_jugador, +2)
                                print(self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"])
                                print(f"Mensaje del cliente {id_jugador}: {mensaje}")
                                self.enviar_a_cliente(id_jugador, {
                                    "type": "comprar",
                                    "carta_extra": carta_extra.to_dict(),
                                })
                                self.difundir_excepcion(id_jugador, {
                                    "type": "Actualizacion_Carta_Descarte",
                                    'cantidad_manos_jugadores': self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                                    "dato_carta_descarte": self.mesa_juego.elementos_mesa["dato_carta_descarte"],
                                })
                                self.enviar_a_cliente(self.mesa_juego.elementos_mesa["jugador_mano"][0], {
                                    "type": "Compra_realizada"
                                })
                                nombre_cliente = next((c['nombre'] for c in self.clientes if c['id'] == id_jugador), None)
                                self.difundir_excepcion(id_jugador, {
                                    "type": "Ciert_jugador_compro_carta_del_descarte",
                                    "jugador_compro": nombre_cliente
                                })
                                self.jugador_compra = None
                                self.contador_turno_compra = 0
                                if self.jugador_que_descarto and self.jugador_que_descarto != self.mesa_juego.elementos_mesa["jugador_mano"][0]:
                                    self.enviar_a_cliente(self.jugador_que_descarto, {
                                        "type": "Reactivar_Botones_No_Turno",
                                    })
                                self.jugador_que_descarto = None
                                self.ultimo_descarte = []
                        
                        # TOMAR CARTA DEL MAZO
                        elif mensaje.get("type") == "Tomar_carta_mazo":
                            print(id_jugador)
                            if id_jugador == self.mesa_juego.elementos_mesa["jugador_mano"][0]:
                                print("viendo si hay mazo nuevo")
                                self.mazo_nuevo()
                                carta_extra = self.mazo.cartas.pop()
                                self.manos[id_jugador-1].append(carta_extra)
                                self.modificar_cartas(id_jugador, +1)
                                print(self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"])
                                self.enviar_a_cliente(id_jugador, {
                                    "type": "Tomar_carta_mazo",
                                    "carta_extra": carta_extra.to_dict(),
                                    "jugador_mano": self.mesa_juego.elementos_mesa["jugador_mano"],
                                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"]
                                })
                                # ---> NUEVO: Avisar a los demás que el jugador robó
                                self.difundir_excepcion(id_jugador, {
                                    "type": "Actualizacion_Carta_Descarte",
                                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                                    "dato_carta_descarte": self.mesa_juego.elementos_mesa["dato_carta_descarte"],
                                })
                        
                        # MONO QUEMADO
                        elif mensaje.get("type") == "mono_quemado":
                            carta_descartes = self.descarte[-1].to_dict()
                            carta_descartada = mensaje.get("carta_descartada")
                            if id_jugador == self.mesa_juego.elementos_mesa["jugador_mano"][0] and (carta_descartes["numero"] != carta_descartada["numero"] or carta_descartes["figura"] != carta_descartada["figura"]):
                                self.quema.append(self.descarte.pop())
                                carta_ = None
                                for carta in self.manos[id_jugador-1]:
                                    try:
                                        carta_mono_serealizada = carta.to_dict()
                                    except:
                                        carta_mono_serealizada = carta
                                    if carta_mono_serealizada["numero"] == carta_descartada["numero"] and carta_mono_serealizada["figura"] == carta_descartada["figura"]:
                                        self.manos[id_jugador-1].remove(carta)
                                        print(str(self.manos[id_jugador-1]))
                                        self.mesa_juego.elementos_mesa["dato_carta_descarte"] = mensaje.get("carta_descartada")
                                        self.modificar_cartas(id_jugador, -1) 
                                        print(self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"])
                                        self.descarte.append(carta)
                                        self.jugador_que_descarto = id_jugador
                                        print("carta mono quemada")
                                        self.mesa_juego.elementos_mesa["dato_carta_quema"] = self.quema[-1].to_dict()
                                        print(self.descarte)
                                        carta_ = carta
                                        break
                                if carta_:
                                    self.mesa_juego.elementos_mesa["cantidad_cartas_quema"] += 1
                                    self.difundir({
                                        "type": "Actualizar_quema_descarte",
                                        "cantidad_cartas_quema": self.mesa_juego.elementos_mesa["cantidad_cartas_quema"]
                                    })
                                    self.difundir_excepcion(id_jugador, {
                                        "type": "actualizar_mono",
                                        "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                                        "dato_carta_descarte": self.mesa_juego.elementos_mesa["dato_carta_descarte"],
                                        "dato_carta_quema": self.mesa_juego.elementos_mesa["dato_carta_quema"],
                                    })
                                    self.enviar_a_cliente(id_jugador, {
                                        "type": "descartar_mono",
                                        "dato_carta_quema": self.mesa_juego.elementos_mesa["dato_carta_quema"],
                                    })
                                    try:
                                        self.verificar_mano_vacia_y_difundir(id_jugador)
                                    except Exception:
                                        pass

                                    jugadores = self.mesa_juego.elementos_mesa["datos_lista_jugadores"]
                                    idx_actual = next((i for i, j in enumerate(jugadores) if j[0] == id_jugador), None)
                                    if idx_actual is not None:
                                        idx_siguiente = (idx_actual + 1) % len(jugadores)
                                        id_siguiente = jugadores[idx_siguiente][0]
                                        nombre = jugadores[idx_siguiente][1]
                                    self.mesa_juego.elementos_mesa.update({"jugador_mano": (id_siguiente, nombre)})
                                    self.finalizar_turno(id_jugador, id_siguiente)
                        
                        # VALIDAR SELECCION
                        elif mensaje["type"] == "validar_seleccion":
                            if id_jugador == self.mesa_juego.elementos_mesa["jugador_mano"][0]:
                                cartas_a_bajar_ = mensaje["datos_cartas"]
                                resultado_validacion = self.validar_seleccion(cartas_a_bajar_, id_jugador)
                                for mensaje_a_enviar in resultado_validacion[1]:
                                    self.enviar_a_cliente(id_jugador, mensaje_a_enviar)
                        
                        # BAJARSE
                        elif mensaje["type"] == "bajarse":
                            resultado_jugada = self.validar_jugada(id_jugador)
                            for mensaje_a_enviar in resultado_jugada[1]:
                                self.enviar_a_cliente(id_jugador, mensaje_a_enviar)
                            for mensaje_a_difundir in resultado_jugada[2]:
                                self.difundir_excepcion(id_jugador, mensaje_a_difundir)
                            try:
                                self.verificar_mano_vacia_y_difundir(id_jugador)
                            except Exception:
                                pass
                        
                        # ELEGIR POSICION SEGUIDILLA
                        elif mensaje["type"] == "elegir_posicion_seguidilla":
                            posicion_elegida = mensaje["posicion_elegida"]
                            if posicion_elegida in ["inicio", "punta"] and self.seguidilla != {} and self.ronda == 1 or self.ronda == 4:
                                if posicion_elegida == "inicio":
                                    joker = self.seguidilla.pop()
                                    print(joker)
                                    self.seguidilla.insert(0, joker)
                                    print("Seguidilla posicionada al inicio")
                                    self.enviar_a_cliente(id_jugador, {
                                        "type": "seleccion_valida",
                                        "actualizar": True
                                    })
                                elif posicion_elegida == "punta":
                                    joker = self.seguidilla.pop()
                                    print(joker)
                                    self.seguidilla.append(joker)
                                    print("Seguidilla posicionada al final")
                                    self.enviar_a_cliente(id_jugador, {
                                        "type": "seleccion_valida",
                                        "actualizar": True
                                    })
                                print(self.seguidilla)
                            elif posicion_elegida in ["inicio", "punta"] and self.seguidilla != ({} and []) and self.ronda == 2:
                                # Código existente para ronda 2...
                                pass
                        
                        # CANCELAR JUGADA
                        elif mensaje["type"] == "cancelar_jugada":
                            if self.seleccionando == True:
                                self.trio = {}
                                self.seguidilla = {}
                                self.enviar_a_cliente(id_jugador, {
                                    "type": "Seleccion_cancelada",
                                })
                                self.seleccionando = False
                            elif self.jugadas_por_jugador.get(id_jugador) not in ([], None) and not self.cancelar:
                                self.cancelar = True
                                ultima_jugada = copy.deepcopy(self.ultima_jugada)
                                actuales = self.jugadas_por_jugador.get(id_jugador, [])
                                self.jugadas_por_jugador[id_jugador] = [
                                    (tag, grupo) for (tag, grupo) in actuales
                                    if not any(grupo == jug for jug in ultima_jugada)
                                ]
                                for grupo in ultima_jugada:
                                    cartas_obj = []
                                    for carta in grupo:
                                        cartas_obj.append(Carta(un_juego=None, numero=carta["numero"], figura=carta["figura"]))
                                    self.manos[id_jugador-1].extend(cartas_obj)
                                cantidad_devuelta = []
                                for grupo in ultima_jugada:
                                    for carta in grupo:
                                        cantidad_devuelta.append(carta)
                                self.seleccionando = False
                                self.ultima_jugada = []
                                self.actualizar_mano_y_notificar(
                                    id_jugador,
                                    len(cantidad_devuelta),
                                    {
                                        "type": "jugada_cancelada",
                                        "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                                        "datos_mano_jugador": None,
                                        "jugada": self.jugadas_por_jugador[id_jugador],
                                        "jugadas_jugadores": self.jugadas_por_jugador,
                                    },
                                    {
                                        "type": "se_extendio",
                                        "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                                        "jugadas_jugadores": self.jugadas_por_jugador,   
                                    }
                                )
                                if self.ronda == 2:
                                    self.seguidilla = []
                                if len(self.jugadas_por_jugador[id_jugador]) == 0:
                                    self.cancelar = False
                            elif self.cancelar == False and len(self.jugadas_por_jugador[id_jugador]) == 0:
                                print("No tienes jugadas para cancelar")
                                self.enviar_a_cliente(id_jugador, {
                                    "type": "regresando_menu",
                                })
                        
                        # EXTENDER EN
                        elif mensaje["type"] == "extender_en":
                            print(mensaje)
                            cartas_expandir = None
                            if len(mensaje["cartas_expandir"]) == 1:
                                cartas_expandir = mensaje["cartas_expandir"]
                            else:
                                cartas_expandir = False
                            id_donde_bajarse = mensaje["id_jugador"]
                            jugada = None
                            print(self.jugadas_por_jugador)
                            if self.ronda == 1:
                                for x,y in self.jugadas_por_jugador.items():
                                    if x == id_donde_bajarse:
                                        if y:
                                            jugada = y
                                            jugada_trio = y[0]
                                            jugada_seguidilla = y[-1]
                                            break
                                if jugada and cartas_expandir != False :
                                    print(jugada)
                                    validacion_ext_seguidilla = self.validar_extender_seguidilla(cartas_expandir[0],jugada_seguidilla[-1])
                                    validacion_ext_trio = self.validar_extender_trio(cartas_expandir[0],jugada_trio[-1])
                                    print(validacion_ext_seguidilla)
                                    print(validacion_ext_trio)
                                    if  validacion_ext_seguidilla != False and validacion_ext_trio != False:
                                        print("Ahora se elige donde extender")
                                        if validacion_ext_seguidilla == "ambos":
                                            pos = "ambos"
                                        else:
                                            pos = validacion_ext_seguidilla
                                        self.enviar_a_cliente(id_jugador,{
                                            "type" : "elejir_donde_extender",
                                            "posicion_seguidilla" : pos,
                                            "trio_seguidilla" : True,
                                            "seguidilla_seguidilla" : False,
                                        })
                                        self.informacion_extender = [mensaje["id_jugador"],cartas_expandir]
                            
                                    elif validacion_ext_seguidilla != False:
                                        if validacion_ext_seguidilla == "inicio":
                                            for carta in cartas_expandir:
                                                for i, _carta in enumerate(self.manos[id_jugador-1]):
                                                    _carta = _carta.to_dict()
                                                    if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                        self.manos[id_jugador-1].pop(i)
                                                        self.modificar_cartas(id_jugador, -1)
                                                        break
                                            self.jugadas_por_jugador[id_donde_bajarse][-1][-1].insert(0, cartas_expandir[0])
                                            print("Seguidilla extendida al inicio")
                                            self.extender_confirmado(id_jugador,id_donde_bajarse)
                                        elif validacion_ext_seguidilla == "final":
                                            for carta in cartas_expandir:
                                                for i, _carta in enumerate(self.manos[id_jugador-1]):
                                                    _carta = _carta.to_dict()
                                                    if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                        self.manos[id_jugador-1].pop(i)
                                                        self.modificar_cartas(id_jugador, -1)
                                                        break
                                            self.jugadas_por_jugador[id_donde_bajarse][-1][-1].extend(cartas_expandir)
                                            print("Seguidilla extendida al final")
                                            self.extender_confirmado(id_jugador,id_donde_bajarse)
                                        elif validacion_ext_seguidilla == "ambos":
                                            print("Se debe elegir donde extender la seguidilla")
                                            self.enviar_a_cliente(id_jugador,{
                                            "type" : "elejir_donde_extender",
                                            "posicion_seguidilla" : "ambos",
                                            "trio_seguidilla" : False,
                                            "seguidilla_seguidilla" : False,
                                            })
                                            self.informacion_extender = [mensaje["id_jugador"],cartas_expandir]
                                    elif validacion_ext_trio != False:
                                        for carta in cartas_expandir:
                                            for i, _carta in enumerate(self.manos[id_jugador-1]):
                                                _carta = _carta.to_dict()
                                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                    self.manos[id_jugador-1].pop(i)
                                                    self.modificar_cartas(id_jugador, -1)
                                                    break
                                        self.jugadas_por_jugador[id_donde_bajarse][0][-1].extend(cartas_expandir)
                                        self.extender_confirmado(id_jugador,id_donde_bajarse)
                                    print(self.jugadas_por_jugador)
                            elif self.ronda == 2:
                                print(self.jugadas_por_jugador)
                                for x,y in self.jugadas_por_jugador.items():
                                    if x == id_donde_bajarse:
                                        if y:
                                            jugada = y
                                            jugada_seguidilla1 = y[0]
                                            jugada_seguidilla2 = y[-1]
                                            break
                                if jugada and cartas_expandir != False :
                                    print(jugada)
                                    validacion_ext_seguidilla1 = self.validar_extender_seguidilla(cartas_expandir[0],jugada_seguidilla1[-1])
                                    validacion_ext_seguidilla2 = self.validar_extender_seguidilla(cartas_expandir[0],jugada_seguidilla2[-1])
                                    if validacion_ext_seguidilla2 != False and validacion_ext_seguidilla1 != False:
                                        print("Ahora se elige en cual seguidilla extender")
                                        if validacion_ext_seguidilla1 == "ambos":
                                            pos = "ambos"
                                        else:
                                            pos = validacion_ext_seguidilla1
                                        self.enviar_a_cliente(id_jugador,{
                                            "type" : "elejir_donde_extender",
                                            "posicion_seguidilla1" : pos,
                                            "posicion_seguidilla2" : validacion_ext_seguidilla2,
                                            "trio_seguidilla" : False,
                                            "seguidilla_seguidilla" : True,
                                            "ronda": self.ronda,
                                        })
                                        self.informacion_extender = [mensaje["id_jugador"],cartas_expandir]
                                    elif validacion_ext_seguidilla1 != False:
                                        if validacion_ext_seguidilla1 == "inicio":
                                            for carta in cartas_expandir:
                                                for i, _carta in enumerate(self.manos[id_jugador-1]):
                                                    _carta = _carta.to_dict()
                                                    if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                        self.manos[id_jugador-1].pop(i)
                                                        self.modificar_cartas(id_jugador, -1)
                                                        break
                                            self.jugadas_por_jugador[id_donde_bajarse][0][-1].insert(0, cartas_expandir[0])
                                            print("Seguidilla extendida al inicio")
                                            mano_nueva = self.convertir_mano_dic(id_jugador)
                                            self.extender_confirmado(id_jugador,id_donde_bajarse)
                                        elif validacion_ext_seguidilla1 == "final":
                                            for carta in cartas_expandir:
                                                for i, _carta in enumerate(self.manos[id_jugador-1]):
                                                    _carta = _carta.to_dict()
                                                    if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                        self.manos[id_jugador-1].pop(i)
                                                        self.modificar_cartas(id_jugador, -1)
                                                        break
                                            self.jugadas_por_jugador[id_donde_bajarse][0][-1].extend(cartas_expandir)
                                            print("Seguidilla extendida al final")
                                            self.extender_confirmado(id_jugador,id_donde_bajarse)
                                        elif validacion_ext_seguidilla1 == "ambos":
                                            print("Se debe elegir donde extender la seguidilla")
                                            self.enviar_a_cliente(id_jugador,{
                                            "type" : "elejir_donde_extender",
                                            "posicion_seguidilla" : "seguidilla1",
                                            "trio_seguidilla" : False,
                                            "seguidilla_seguidilla" : False,
                                            })
                                            self.informacion_extender = [mensaje["id_jugador"],cartas_expandir]
                                    elif validacion_ext_seguidilla2 != False:
                                        if validacion_ext_seguidilla2 == "inicio":
                                            for carta in cartas_expandir:
                                                for i, _carta in enumerate(self.manos[id_jugador-1]):
                                                    _carta = _carta.to_dict()
                                                    if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                        self.manos[id_jugador-1].pop(i)
                                                        self.modificar_cartas(id_jugador, -1)
                                                        break
                                            self.jugadas_por_jugador[id_donde_bajarse][-1][-1].insert(0, cartas_expandir[0])
                                            print("Seguidilla extendida al inicio")
                                            mano_nueva = self.convertir_mano_dic(id_jugador)
                                            self.extender_confirmado(id_jugador,id_donde_bajarse)
                                        elif validacion_ext_seguidilla2 == "final":
                                            for carta in cartas_expandir:
                                                for i, _carta in enumerate(self.manos[id_jugador-1]):
                                                    _carta = _carta.to_dict()
                                                    if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                        self.manos[id_jugador-1].pop(i)
                                                        self.modificar_cartas(id_jugador, -1)
                                                        break
                                            self.jugadas_por_jugador[id_donde_bajarse][-1][-1].extend(cartas_expandir)
                                            print("Seguidilla extendida al final")
                                            self.extender_confirmado(id_jugador,id_donde_bajarse)
                                        elif validacion_ext_seguidilla2 == "ambos":
                                            print("Se debe elegir donde extender la seguidilla")
                                            self.enviar_a_cliente(id_jugador,{
                                            "type" : "elejir_donde_extender",
                                            "posicion_seguidilla" : "seguidilla2",
                                            "trio_seguidilla" : False,
                                            "seguidilla_seguidilla" : False,
                                            })
                                            self.informacion_extender = [mensaje["id_jugador"],cartas_expandir]
                            elif self.ronda == 3:
                                print(self.jugadas_por_jugador)
                                for x,y in self.jugadas_por_jugador.items():
                                    if x == id_donde_bajarse:
                                        if y:
                                            jugada = y
                                            jugada_trio1 = y[0]
                                            jugada_trio2 = y[-1]
                                            jugada_trio3 = y[-2]
                                            break
                                if jugada and cartas_expandir != False :
                                    print(jugada)
                                    validacion_ext_trio1 = self.validar_extender_trio(cartas_expandir[0],jugada_trio1[-1])
                                    validacion_ext_trio2 = self.validar_extender_trio(cartas_expandir[0],jugada_trio2[-1])
                                    validacion_ext_trio3 = self.validar_extender_trio(cartas_expandir[0],jugada_trio3[-1])
                                    if validacion_ext_trio1 != False:
                                        for carta in cartas_expandir:
                                            for i, _carta in enumerate(self.manos[id_jugador-1]):
                                                _carta = _carta.to_dict()
                                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                    self.manos[id_jugador-1].pop(i)
                                                    self.modificar_cartas(id_jugador, -1)
                                                    break
                                        self.jugadas_por_jugador[id_donde_bajarse][0][-1].extend(cartas_expandir)
                                        self.extender_confirmado(id_jugador,id_donde_bajarse)
                                    elif validacion_ext_trio2 != False:
                                        for carta in cartas_expandir:
                                            for i, _carta in enumerate(self.manos[id_jugador-1]):
                                                _carta = _carta.to_dict()
                                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                    self.manos[id_jugador-1].pop(i)
                                                    self.modificar_cartas(id_jugador, -1)
                                                    break
                                        self.jugadas_por_jugador[id_donde_bajarse][1][-1].extend(cartas_expandir)
                                        self.extender_confirmado(id_jugador,id_donde_bajarse)
                                    elif validacion_ext_trio3 != False:
                                        for carta in cartas_expandir:
                                            for i, _carta in enumerate(self.manos[id_jugador-1]):
                                                _carta = _carta.to_dict()
                                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                    self.manos[id_jugador-1].pop(i)
                                                    self.modificar_cartas(id_jugador, -1)
                                                    break
                                        self.jugadas_por_jugador[id_donde_bajarse][2][-1].extend(cartas_expandir)
                                        self.extender_confirmado(id_jugador,id_donde_bajarse)
                                        break
                            
                        
                        # ELECCION DONDE EXTENDER
                        elif mensaje["type"] == "elecion_donde_extender":
                            print(mensaje)
                            if self.ronda == 1:
                                if mensaje["donde_extender"] == "trio":
                                    id_donde_bajarse = self.informacion_extender[0]
                                    cartas_expandir = self.informacion_extender[-1]
                                    for carta in cartas_expandir:
                                        for i, _carta in enumerate(self.manos[id_jugador-1]):
                                            _carta = _carta.to_dict()
                                            if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                self.manos[id_jugador-1].pop(i)
                                                self.modificar_cartas(id_jugador, -1)
                                                break
                                    self.jugadas_por_jugador[id_donde_bajarse][0][-1].extend(cartas_expandir)
                                    self.extender_confirmado(id_jugador,id_donde_bajarse)
                                if mensaje["donde_extender"] == "seguidilla":
                                    if mensaje["posicion_seguidilla"] == "inicio":
                                        id_donde_bajarse = self.informacion_extender[0]
                                        cartas_expandir = self.informacion_extender[-1]
                                        for carta in cartas_expandir:
                                            for i, _carta in enumerate(self.manos[id_jugador-1]):
                                                _carta = _carta.to_dict()
                                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                    self.manos[id_jugador-1].pop(i)
                                                    self.modificar_cartas(id_jugador, -1)
                                                    break
                                        self.jugadas_por_jugador[id_donde_bajarse][-1][-1].insert(0, cartas_expandir[0])
                                        print("Seguidilla extendida al inicio")
                                        self.extender_confirmado(id_jugador,id_donde_bajarse)
                                    elif mensaje["posicion_seguidilla"] == "final":
                                        id_donde_bajarse = self.informacion_extender[0]
                                        cartas_expandir = self.informacion_extender[-1]
                                        for carta in cartas_expandir:
                                            for i, _carta in enumerate(self.manos[id_jugador-1]):
                                                _carta = _carta.to_dict()
                                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                    self.manos[id_jugador-1].pop(i)
                                                    break
                                        self.jugadas_por_jugador[id_donde_bajarse][-1][-1].extend(cartas_expandir)
                                        print("Seguidilla extendida al final")
                                        self.extender_confirmado(id_jugador,id_donde_bajarse)
                            elif self.ronda == 2:
                                if mensaje["donde_extender"] == "seguidilla1":
                                    if mensaje["posicion_seguidilla"] == "inicio":
                                        id_donde_bajarse = self.informacion_extender[0]
                                        cartas_expandir = self.informacion_extender[-1]
                                        for carta in cartas_expandir:
                                            for i, _carta in enumerate(self.manos[id_jugador-1]):
                                                _carta = _carta.to_dict()
                                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                    self.manos[id_jugador-1].pop(i)
                                                    self.modificar_cartas(id_jugador, -1)
                                                    break
                                        self.jugadas_por_jugador[id_donde_bajarse][-1][-1].extend(cartas_expandir)
                                        print("Seguidilla extendida al final")
                                        self.extender_confirmado(id_jugador,id_donde_bajarse)
                            elif self.ronda == 2:
                                if mensaje["donde_extender"] == "seguidilla1":
                                    if mensaje["posicion_seguidilla"] == "inicio":
                                        id_donde_bajarse = self.informacion_extender[0]
                                        cartas_expandir = self.informacion_extender[-1]
                                        for carta in cartas_expandir:
                                            for i, _carta in enumerate(self.manos[id_jugador-1]):
                                                _carta = _carta.to_dict()
                                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                    self.manos[id_jugador-1].pop(i)
                                                    self.modificar_cartas(id_jugador, -1)
                                                    break
                                        self.jugadas_por_jugador[id_donde_bajarse][0][-1].insert(0, cartas_expandir[0])
                                        print("Seguidilla extendida al inicio")
                                        mano_nueva = self.convertir_mano_dic(id_jugador)
                                        self.extender_confirmado(id_jugador,id_donde_bajarse)
                                    elif mensaje["posicion_seguidilla"] == "final":
                                        id_donde_bajarse = self.informacion_extender[0]
                                        cartas_expandir = self.informacion_extender[-1]
                                        for carta in cartas_expandir:
                                            for i, _carta in enumerate(self.manos[id_jugador-1]):
                                                _carta = _carta.to_dict()
                                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                    self.manos[id_jugador-1].pop(i)
                                                    self.modificar_cartas(id_jugador, -1)
                                                    break
                                        self.jugadas_por_jugador[id_donde_bajarse][0][-1].extend(cartas_expandir)
                                        print("Seguidilla extendida al final")
                                        self.extender_confirmado(id_jugador,id_donde_bajarse)
                                elif mensaje["donde_extender"] == "seguidilla2":
                                    if mensaje["posicion_seguidilla"] == "inicio":
                                        id_donde_bajarse = self.informacion_extender[0]
                                        cartas_expandir = self.informacion_extender[-1]
                                        for carta in cartas_expandir:
                                            for i, _carta in enumerate(self.manos[id_jugador-1]):
                                                _carta = _carta.to_dict()
                                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                    self.manos[id_jugador-1].pop(i)
                                                    self.modificar_cartas(id_jugador, -1)
                                                    break
                                        self.jugadas_por_jugador[id_donde_bajarse][-1][-1].insert(0, cartas_expandir[0])
                                        print("Seguidilla extendida al inicio")
                                        mano_nueva = self.convertir_mano_dic(id_jugador)
                                        self.extender_confirmado(id_jugador,id_donde_bajarse)
                                    elif mensaje["posicion_seguidilla"] == "final":
                                        id_donde_bajarse = self.informacion_extender[0]
                                        cartas_expandir = self.informacion_extender[-1]
                                        for carta in cartas_expandir:
                                            for i, _carta in enumerate(self.manos[id_jugador-1]):
                                                _carta = _carta.to_dict()
                                                if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                    self.manos[id_jugador-1].pop(i)
                                                    self.modificar_cartas(id_jugador, -1)
                                                    break
                                        self.jugadas_por_jugador[id_donde_bajarse][-1][-1].extend(cartas_expandir)
                                        print("Seguidilla extendida al final")
                                        self.extender_confirmado(id_jugador,id_donde_bajarse)
                            elif self.ronda == 3:
                                if mensaje["donde_extender"] == "trio1":
                                    id_donde_bajarse = self.informacion_extender[0]
                                    cartas_expandir = self.informacion_extender[-1]
                                    for carta in cartas_expandir:
                                        for i, _carta in enumerate(self.manos[id_jugador-1]):
                                            _carta = _carta.to_dict()
                                            if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                self.manos[id_jugador-1].pop(i)
                                                self.modificar_cartas(id_jugador, -1)
                                                break
                                    self.jugadas_por_jugador[id_donde_bajarse][0][-1].extend(cartas_expandir)
                                    self.extender_confirmado(id_jugador,id_donde_bajarse)
                                if mensaje["donde_extender"] == "trio2":
                                    id_donde_bajarse = self.informacion_extender[0]
                                    cartas_expandir = self.informacion_extender[-1]
                                    for carta in cartas_expandir:
                                        for i, _carta in enumerate(self.manos[id_jugador-1]):
                                            _carta = _carta.to_dict()
                                            if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                self.manos[id_jugador-1].pop(i)
                                                self.modificar_cartas(id_jugador, -1)
                                                break
                                    self.jugadas_por_jugador[id_donde_bajarse][1][-1].extend(cartas_expandir)
                                    self.extender_confirmado(id_jugador,id_donde_bajarse)
                                if mensaje["donde_extender"] == "trio3":
                                    id_donde_bajarse = self.informacion_extender[0]
                                    cartas_expandir = self.informacion_extender[-1]
                                    for carta in cartas_expandir:
                                        for i, _carta in enumerate(self.manos[id_jugador-1]):
                                            _carta = _carta.to_dict()
                                            if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                                self.manos[id_jugador-1].pop(i)
                                                self.modificar_cartas(id_jugador, -1)
                                                break
                                    self.jugadas_por_jugador[id_donde_bajarse][2][-1].extend(cartas_expandir)
                        
                        # REEMPLAZAR
                        elif mensaje["type"] == "reemplazar":
                            print(mensaje)
                            print("sei llega el msj")
                            carta_a_remplazar = []
                            if mensaje["carta_descartada"] != None:
                                id_jugador_reemplazado = None
                                carta_a_remplazar.append(mensaje["carta_descartada"])
                                print("carta valida")
                                validaciones_extender = []
                                for id_j, jugadas_list in list(self.jugadas_por_jugador.items()):
                                    for idx, entry in enumerate(jugadas_list):
                                        # entry expected to be (tag, grupo)
                                        try:
                                            tag, grupo = entry
                                        except Exception:
                                            continue
                                        if tag == "Seguidilla":
                                            valor = self.validar_reemplazar_joker_seguidilla(mensaje["carta_descartada"], grupo)
                                            if valor is not None:
                                                # guardar validaciÃ³n y reemplazar la jugada en la estructura original
                                                validaciones_extender.append(valor)
                                                self.jugadas_por_jugador[id_j][idx] = (tag, valor)
                                                id_jugador_reemplazado = id_j
                                                break
                                if validaciones_extender != []:
                                    for carta in self.manos[id_jugador-1]:
                                        try:
                                            carta_serealizada = carta.to_dict()
                                        except:
                                            carta_serealizada = carta
                                        if carta_serealizada["numero"] == mensaje["carta_descartada"]["numero"] and carta_serealizada["figura"] == mensaje["carta_descartada"]["figura"]:
                                            self.manos[id_jugador-1].remove(carta)
                                            self.manos[id_jugador-1].append(Carta(un_juego=None, numero="Joker", figura="Especial"))
                                            break
                                    self.difundir_excepcion(id_jugador_reemplazado,{
                                        "type": "se_extendio",
                                        "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                                        "jugadas_jugadores": self.jugadas_por_jugador,
                                    })
                                    self.enviar_a_cliente(id_jugador,{
                                        "type": "reemplazar_valido",
                                        "nueva_mano": self.convertir_mano_dic(id_jugador),
                                        "jugadas_jugadores": self.jugadas_por_jugador,
                                        "jugada" :self.jugadas_por_jugador[id_jugador],
                                        })
                                    self.enviar_a_cliente(id_jugador_reemplazado,{
                                        "type": "reemplazaron_tu_jugada",
                                        "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                                        "jugadas_jugadores": self.jugadas_por_jugador,
                                        "jugadas_jugadores": self.jugadas_por_jugador,
                                        "jugada" :self.jugadas_por_jugador[id_jugador_reemplazado],
                                        })
                            
                        
                        # ACTUALIZAR MANO CHEAT
                        #elif mensaje.get("type") == "ActualizarManoCheat":
                         #   nuevas_cartas_dict = mensaje.get("mano", [])
                          #  try:
                           #     nueva_mano = []
                            #    for c in nuevas_cartas_dict:
                             #       nueva_mano.append(Carta(
                              #          un_juego=None,
                               #         numero=c.get("numero"),
                                #        figura=c.get("figura")
                                 #   ))
                                #self.manos[id_jugador - 1] = nueva_mano
                                #for jug_info in self.mesa_juego.elementos_mesa.get("cantidad_manos_jugadores", []):
                                #    if jug_info["id"] == id_jugador:
                                 #       jug_info["cantidad_mano"] = len(nueva_mano)
                                  #      break
                                #print(f"[CheatSync] Mano del servidor para jugador {id_jugador} actualizada")
                            #except Exception as e:
                             #   print(f"[CheatSync] Error actualizando mano cheat en servidor: {e}")

                    # FIX Bug 2: Sincronizar mano del servidor con el cheat del cliente
                    if mensaje.get("type") == "ActualizarManoCheat":
                        nuevas_cartas_dict = mensaje.get("mano", [])
                        try:
                            nueva_mano = []
                            for c in nuevas_cartas_dict:
                                nueva_mano.append(Carta(
                                    un_juego=None,
                                    numero=c.get("numero"),
                                    figura=c.get("figura")
                                ))
                            self.manos[id_jugador - 1] = nueva_mano

                            # NUEVO: Actualizar contador de cartas en cantidad_manos_jugadores
                            for jug_info in self.mesa_juego.elementos_mesa.get("cantidad_manos_jugadores", []):
                                if jug_info["id"] == id_jugador:
                                    jug_info["cantidad_mano"] = len(nueva_mano)
                                    break

                            # NUEVO: Notificar a todos los jugadores la cantidad actualizada
                            self.difundir_excepcion(id_jugador, {
                                "type": "se_bajo_alguien",  # Reutiliza mensaje existente para actualizar contadores
                                "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa.get("cantidad_manos_jugadores"),
                                "jugadas_jugadores": self.jugadas_por_jugador,
                            })

                            print(f"[CheatSync] Mano servidor jugador {id_jugador}: "
                                f"{[str(c) for c in nueva_mano]}")
                        except Exception as e:
                            print(f"[CheatSync] Error: {e}")
                    # FIN NUEVO CÓDIGO

        except Exception as e:
            print(f"[Redes] Excepción crítica en hilo de cliente {id_jugador}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print(f"[Redes] Cerrando conexión para jugador {id_jugador}")
            self._ejecutar_limpieza_jugador(id_jugador)
            try:
                socket_cliente.close()
            except:
                pass
                pass
