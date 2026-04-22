"""Módulo interno para funcionalidad del cliente"""

import socket
import threading
import json
import time
import pygame
from redes_juego import archivo_de_importaciones

importar_desde_carpeta = archivo_de_importaciones.importar_desde_carpeta
constantes = importar_desde_carpeta(
    nombre_archivo="constantes.py",
    nombre_carpeta="recursos_graficos",
)
mesa_interfaz = importar_desde_carpeta(
    nombre_archivo="mesa_interfaz.py",
    nombre_carpeta="logica_interfaz",
)
Carta = importar_desde_carpeta(
    nombre_archivo="cartas_interfaz.py",
    nombre_clase="Cartas_interfaz",
    nombre_carpeta="logica_interfaz"
)
Boton = importar_desde_carpeta(
    nombre_archivo="elementos_de_interfaz_de_usuario.py",
    nombre_clase="Boton",
    nombre_carpeta="recursos_graficos",
)

class ClienteMixin:
    """Mixin con métodos para funcionalidad del cliente"""
    
    def conectar_a_servidor(self, ip_servidor, id_jugador_reconectar=None, nombre_jugador=None):
        try:
            print(f"Conectado al servidor en {ip_servidor}:{self.puerto}")
            self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_cliente.connect((ip_servidor, self.puerto))
            self.conectado = True
            print("Enviando mensaje de conexión...")
            if id_jugador_reconectar is not None:
                mensaje = {
                        'type': 'Reconectar',
                        'id_jugador': id_jugador_reconectar,
                        'nombre': nombre_jugador
                    }
            else:
                mensaje = {
                    'type': 'NuevoJugador',
                    'nombre': nombre_jugador
                }
            print(f"Mensaje enviado: {mensaje}")    
            self.socket_cliente.sendall((json.dumps(mensaje) + '\n').encode('utf-8'))
            self.hilo_recepcion = threading.Thread(target=self._recibir_mensajes)
            self.hilo_recepcion.daemon = True
            self.hilo_recepcion.start()
            return True
        except Exception as e:
            print(f"Error al conectar al servidor: {e}")
            return False
            
    def _recibir_mensajes(self):
        buffer = ""
        while self.conectado:
            try:
                data = self.socket_cliente.recv(4096)
                buffer += data.decode('utf-8')
                while '\n' in buffer:
                    mensaje_str, buffer = buffer.split('\n', 1)
                    if mensaje_str.strip():
                        mensaje = json.loads(mensaje_str)
                        self._manejo_mensaje_red(mensaje)
                        
            except Exception as e:
                print(f"Error al recibir mensaje del servidor: {e}")
                import traceback
                traceback.print_exc()
                break
                # Intentar reconexión automática
                if self.id_jugador is not None and self.socket_cliente is not None:
                    ip_servidor = self.socket_cliente.getpeername()[0]
                    ##self.intentar_reconexion(ip_servidor)

    def _manejo_mensaje_red(self, mensaje):
        # Método completo para procesar todos los mensajes del servidor
        # Este método es muy largo (360+ líneas) y se mantiene completo aquí
        
        # Inicializar variable si no existe
        if not hasattr(self, 'descarto_recientemente'):
            self.descarto_recientemente = False
        if mensaje['type'] == 'Bienvenido':
            self.id_jugador = mensaje['id_jugador']
            self.guardar_id_local()
            nombre = mensaje.get('nombre')
            print(f'ID:{self.id_jugador} - Nombre: {nombre}')
            self.estado_juego = mensaje.get('game_state', None)
        elif mensaje['type'] == 'Reconectado':
            self.id_jugador = mensaje['id_jugador']
            self.guardar_id_local()
            self.estado_juego = mensaje.get('estado_juego', None)
            print(f"Reconectado como {mensaje.get('nombre')}, estado restaurado.")
        elif mensaje['type'] == 'JugadorReconectado':
            nombre = mensaje.get('nombre')
            print(f"Jugador {mensaje['nombre']} (ID {mensaje['id_jugador']}) se ha reconectado.")
            if self.un_juego:
                nueva_lista = self.un_juego.lista_elementos["lista_jugadores"]
                if mensaje.get('lista_jugadores') != nueva_lista:
                    evento_py = pygame.event.Event(constantes.EVENTO_NUEVO_JUGADOR,nueva_lista =mensaje.get('lista_jugadores'))
                    pygame.event.post(evento_py)
        elif mensaje['type'] == 'game_update':
            self.estado_juego = mensaje.get('game_state', None)
        elif mensaje['type'] == 'NuevoJugador':
            nombre = mensaje.get('nombre')
            print(f"Nuevo jugador conectado: ID {mensaje['id_jugador']} - Nombre: {nombre}, Total jugadores: {mensaje['TotalJugadores']}")
            if self.un_juego:
                nueva_lista = self.un_juego.lista_elementos.get("lista_jugadores", [])
                if mensaje.get('lista_jugadores') != nueva_lista:
                    evento_py = pygame.event.Event(constantes.EVENTO_NUEVO_JUGADOR,nueva_lista =mensaje.get('lista_jugadores'))
                    pygame.event.post(evento_py)
        elif mensaje['type'] == 'JugadorDesconectado':
            print(f"Jugador desconectado: ID {mensaje['id_jugador']}, Total jugadores: {mensaje['TotalJugadores']}")
            print(mensaje.get('lista_jugadores'))
            nombre = mensaje.get('nombre')
            if self.un_juego:
                nueva_lista = self.un_juego.lista_elementos.get("lista_jugadores", [])
                if mensaje.get('lista_jugadores') != nueva_lista:
                    evento_py = pygame.event.Event(constantes.EVENTO_NUEVO_JUGADOR,nueva_lista =mensaje.get('lista_jugadores'))
                    pygame.event.post(evento_py)
        elif mensaje['type'] == 'ServidorCerrado':
            print("El servidor ha cerrado la conexión.")
        elif mensaje["type"] == "ManoInicial":
            if not self.mesa_juego:
                self.mesa_juego = mesa_interfaz.Mesa_interfaz(self.un_juego)
            evento_py = pygame.event.Event(constantes.EVENTO_INICIAR_PARTIDA,un_juego=self.un_juego,mesa=self.mesa_juego,datos=mensaje)
            pygame.event.post(evento_py)
            print(mensaje)
        elif mensaje["type"] == "Actualizacion_Carta_Descarte":
            print(mensaje)
            if self.mesa_juego:
                # Si dato_carta_descarte es None, significa que alguien compró o tomó la carta
                # Resetear la variable para que el jugador que descartó pueda tener botones nuevamente
                if mensaje.get("dato_carta_descarte") is None:
                    self.descarto_recientemente = False
                self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
                self.mesa_juego.elementos_mesa["dato_carta_descarte"] = None
                self.mesa_juego.carta_descarte = None
                self.mesa_juego.actualizar_carta_descarte(self.mesa_juego.mesa)
                self.mesa_juego.actualizar_manos_jugadores(self.mesa_juego.mesa)
        elif mensaje["type"] == "Actualizacion_Toma_Descarte":
            if self.mesa_juego:
                self.mesa_juego.procesar_tomar_descarte(self.mesa_juego.mesa)
        elif mensaje["type"] == "Descartar_Carta":
            self.mesa_juego.finalizar_turno(self.mesa_juego.mesa)
            # Desactivar cartas del jugador que descartó
            # Marcar que el jugador descartó recientemente (no puede comprar su propia carta)
            self.descarto_recientemente = True
        elif mensaje["type"] == "Reactivar_Botones_No_Turno":
            # Ya no es su carta, puede tener botones nuevamente
            self.descarto_recientemente = False
            # Recrear botones del jugador que descartó (ya no es su carta, y no es su turno)
            if self.mesa_juego:
                if not self.mesa_juego.tu_turno:
                    # Actualizar turno_robar antes de crear los botones
                    self.mesa_juego.determinar_turno_robar()
                    # Los botones se crearán desactivados si no tiene turno_robar
                    self.mesa_juego.crear_botones_no_turno(self.mesa_juego.mesa)
        elif mensaje["type"] == "Actualizacion_Decartar_Carta":
            print(mensaje)
            if self.mesa_juego:
                self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
                self.mesa_juego.elementos_mesa["dato_carta_descarte"] = mensaje.get("dato_carta_descarte")
                self.mesa_juego.cargar_dato_carta_descarte()
                self.mesa_juego.cargar_elemento_carta_descarte()
                self.mesa_juego.actualizar_carta_descarte(self.mesa_juego.mesa)
                self.mesa_juego.actualizar_manos_jugadores(self.mesa_juego.mesa)
        elif mensaje["type"] == "Rechazar_descarte":
            if self.mesa_juego:
                if mensaje.get("turno_robar") == False:
                    self.mesa_juego.actualizar_estado_mano(accion="esperar_robar")
        elif mensaje["type"] == "No_descartar":
            print(mensaje)
            if self.mesa_juego:
                self.mesa_juego.elementos_mesa["turno_robar"] = mensaje.get("turno_robar")
                self.mesa_juego.turno_robar = mensaje.get("turno_robar")
                if mensaje.get("turno_robar") == False:
                    self.mesa_juego.actualizar_estado_mano(accion="desactivar_boton")
                else:
                    self.mesa_juego.actualizar_estado_mano(accion="robar")
        elif mensaje["type"] == "comprar":
            print(mensaje)
            self.mesa_juego.procesar_comprar(self.mesa_juego.mesa,mensaje.get("carta_extra"))
            self.mesa_juego.actualizar_estado_mano(accion="desactivar_boton")                       
            print(mensaje.get("carta_extra"))
            print("XD")
        elif mensaje["type"] == "Compra_realizada":
            self.mesa_juego.actualizar_estado_mano(accion="activar_mano")
            self.mesa_juego.actualizar_estado_mano(accion="activar_boton")
            self.mesa_juego.accion_tomar_mazo()
        elif mensaje["type"] == "Actualizar_botones":
            print(mensaje)
            if self.mesa_juego:
                # Si se quema la carta (dato_carta_descarte es None), resetear la variable
                if mensaje.get("dato_carta_descarte") is None:
                    self.descarto_recientemente = False
                self.mesa_juego.elementos_mesa["turno_robar"] = mensaje.get("turno_robar")
                self.mesa_juego.elementos_mesa["cantidad_cartas_quema"] = mensaje.get("cantidad_cartas_quema")
                self.mesa_juego.elementos_mesa["dato_carta_descarte"] = None
                self.mesa_juego.elementos_mesa["dato_carta_quema"] = mensaje.get("dato_carta_quema")
                if self.mesa_juego.elementos_mesa["turno_robar"] == True:
                    self.mesa_juego.actualizar_estado_mano(accion="activar_mano")
                else:
                    self.mesa_juego.actualizar_estado_mano(accion="desactivar_boton")      
                self.mesa_juego.actualizar_botones()
                self.mesa_juego.actualizar_carta_quema(self.mesa_juego.mesa)
                self.mesa_juego.actualizar_mazo_quema()
                self.mesa_juego.cargar_dato_carta_descarte()
                self.mesa_juego.cargar_elemento_carta_descarte()
                self.mesa_juego.actualizar_carta_descarte(self.mesa_juego.mesa)
                self.mesa_juego.accion_tomar_mazo()
        elif mensaje["type"] == "Tomar_carta_mazo":
            print(mensaje)
            self.mesa_juego.procesar_tomar_mazo(self.mesa_juego.mesa,mensaje.get("carta_extra"))
            self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
            self.mesa_juego.actualizar_mazo(self.mesa_juego.mesa)
        elif mensaje["type"] == "Pasar_Turno":
            self.mesa_juego.elementos_mesa["jugador_mano"] = mensaje.get("jugador_mano")
            self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
            self.mesa_juego.elementos_mesa["turno_robar"] = mensaje.get("turno_robar")
            self.mesa_juego.actualizar_manos_jugadores(self.mesa_juego.mesa)
            self.mesa_juego.limpiar_botones(self.mesa_juego.mesa)
            # Solo crear botones si el jugador NO descartó recientemente
            if not self.descarto_recientemente:
                self.mesa_juego.crear_botones_no_turno(self.mesa_juego.mesa)
            self.mesa_juego.actualizar_estado_mano(accion="desactivar_boton")
        elif mensaje["type"] == "Tu_Turno":
            self.mesa_juego.elementos_mesa["jugador_mano"] = mensaje.get("jugador_mano")
            self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
            self.mesa_juego.actualizar_manos_jugadores(self.mesa_juego.mesa)
            self.mesa_juego.limpiar_botones(self.mesa_juego.mesa)
            self.mesa_juego.crear_botones_inicio_turno(self.mesa_juego.mesa)
            self.mesa_juego.actualizar_estado_mano(accion="activar_mano")
        elif mensaje["type"] == "Actualizar_Etiqueta_Turno":
            self.mesa_juego.elementos_mesa["jugador_mano"] = mensaje.get("jugador_mano")
            self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
            self.mesa_juego.elementos_mesa["turno_robar"] = mensaje.get("turno_robar")
            self.mesa_juego.actualizar_indicador_turno()
            self.mesa_juego.actualizar_elementos_jugadores()
            # Si no es el turno del jugador y no descartó recientemente, crear botones
            if self.mesa_juego:
                self.mesa_juego.determinar_turno()
                if not self.mesa_juego.tu_turno and not self.descarto_recientemente:
                    # Asegurarse de que los botones estén limpios antes de crear nuevos
                    self.mesa_juego.limpiar_botones(self.mesa_juego.mesa)
                    self.mesa_juego.crear_botones_no_turno(self.mesa_juego.mesa)
        elif mensaje["type"] == "quema_del_mono":
            print(mensaje)
            self.mesa_juego.crear_botones_quema_mono(self.mesa_juego.mesa)
            self.mesa_juego.actualizar_estado_mano(accion="activar_mano")
        elif mensaje["type"] == "Actualizar_quema_descarte":
            print(mensaje)
            self.mesa_juego.elementos_mesa["cantidad_cartas_quema"] = mensaje.get("cantidad_cartas_quema")
            self.mesa_juego.elementos_mesa["dato_carta_descarte"] = None
            self.mesa_juego.actualizar_mazo_quema()      
            self.mesa_juego.cargar_dato_carta_descarte()
            self.mesa_juego.cargar_elemento_carta_descarte()
            self.mesa_juego.actualizar_carta_descarte(self.mesa_juego.mesa)            
        elif mensaje["type"] == "descartar_mono":
            self.mesa_juego.elementos_mesa["dato_carta_quema"] = mensaje.get("dato_carta_quema")
            self.mesa_juego.actualizar_carta_quema(self.mesa_juego.mesa)
            self.mesa_juego.finalizar_turno(self.mesa_juego.mesa)
            

        elif mensaje["type"] == "actualizar_mono":
            self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
            self.mesa_juego.elementos_mesa["dato_carta_descarte"] = mensaje.get("dato_carta_descarte")
            self.mesa_juego.elementos_mesa["dato_carta_quema"] = mensaje.get("dato_carta_quema")
            self.mesa_juego.actualizar_carta_quema(self.mesa_juego.mesa)
            self.mesa_juego.cargar_dato_carta_descarte()
            self.mesa_juego.cargar_elemento_carta_descarte()
            self.mesa_juego.actualizar_carta_descarte(self.mesa_juego.mesa)
            self.mesa_juego.actualizar_manos_jugadores(self.mesa_juego.mesa)
        elif mensaje["type"] == "validacion_trio":
            self.mesa_juego.seleccionar_seguidilla(self.mesa_juego.mesa)
        elif mensaje["type"] == "validacion_trio_fallida":
            self.mesa_juego.alerta_trio_invalido(self.mesa_juego.mesa)
            self.mesa_juego.restaurar_comportamiento_mi_mano()
            self.mesa_juego.modificar_comportamiento_mi_mano()
        elif mensaje["type"] == "validacion_seguidilla":
            print(mensaje)
            print("validacion aceptada")
            self.mesa_juego.elementos_mesa["datos_mano_jugador"] = mensaje.get("datos_mano_jugador")
            self.mesa_juego.elementos_mesa["jugada"] = mensaje.get("jugada")
            self.mesa_juego.elementos_mesa["jugadas_jugadores"] = mensaje.get("jugadas_jugadores")
            self.mesa_juego.cargar_datos_mano_jugador()
            self.mesa_juego.cargar_elemento_mi_mano()
            self.mesa_juego.actualizar_mano_visual(self.mesa_juego.mesa,accion="reorganizar_todo")
            self.mesa_juego.actualizar_jugadas(self.mesa_juego.mesa)
            self.mesa_juego.crear_botones_jugar_descartar(self.mesa_juego.mesa)
        elif mensaje["type"] == "validacion_seguidilla_fallida":
            self.mesa_juego.alerta_seguidilla_invalida(self.mesa_juego.mesa)
            self.mesa_juego.restaurar_comportamiento_mi_mano()
            self.mesa_juego.modificar_comportamiento_mi_mano()
        elif mensaje["type"] == "seleccion_valida":
            print(mensaje)
            if mensaje["actualizar"] == True:
                self.mesa_juego.crear_botones_seleccionar_jugada(self.mesa_juego.mesa)
        elif mensaje["type"] == "validacion_bajarse":
            print("validacion aceptada")
            self.mesa_juego.elementos_mesa["datos_mano_jugador"] = mensaje.get("datos_mano_jugador")
            self.mesa_juego.elementos_mesa["jugada"] = mensaje.get("jugada")
            self.mesa_juego.elementos_mesa["jugadas_jugadores"] = mensaje.get("jugadas_jugadores")
            self.mesa_juego.cargar_datos_mano_jugador()
            self.mesa_juego.cargar_elemento_mi_mano()
            self.mesa_juego.actualizar_mano_visual(self.mesa_juego.mesa,accion="reorganizar_todo")
            self.mesa_juego.modificar_comportamiento_mi_mano()
            self.mesa_juego.actualizar_jugadas(self.mesa_juego.mesa)
        elif mensaje["type"] == "se_bajo_alguien":
            self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
            self.mesa_juego.elementos_mesa["jugadas_jugadores"] = mensaje.get("jugadas_jugadores")
            self.mesa_juego.actualizar_jugadas(self.mesa_juego.mesa)
            self.mesa_juego.actualizar_manos_jugadores(self.mesa_juego.mesa)
        elif mensaje["type"] == "Fin_Ronda_Puntuaciones":
            print("Fin_Ronda_Puntuaciones recibido:", mensaje)
            resultados = mensaje.get("resultados", [])
            if self.mesa_juego:
                for res in resultados:
                    nro = res.get("id")
                    mano = res.get("mano", [])
                    puntos_partida = res.get("puntos_partida")
                    puntos_acumulados = res.get("puntos_acumulados")
                    mano_objs = []
                    for c in mano:
                        try:
                            carta_obj = Carta(numero=c.get("numero"), figura=c.get("figura"))
                        except Exception:
                            continue
                        mano_objs.append(carta_obj)
                    if puntos_acumulados is not None:
                        try:
                            self.mesa_juego.aplicar_puntuacion_servidor(nro, puntos_partida, puntos_acumulados, mano_objs)
                        except Exception:
                            self.mesa_juego.actualizar_puntos_jugador(nro, mano_objs)
                    else:
                        self.mesa_juego.actualizar_puntos_jugador(nro, mano_objs)
                siguiente = mensaje.get("siguiente_ronda")
                try:
                    self.mesa_juego.elementos_mesa["jugada"] = []
                    self.mesa_juego.elementos_mesa["jugadas_jugadores"] = []
                    try:
                        self.mesa_juego.jugada = []
                    except Exception:
                        pass
                    try:
                        self.mesa_juego.jugadas_jugadores = {}
                    except Exception:
                        pass
                    try:
                        ref = self.mesa_juego.referencia_elementos
                        if isinstance(ref.get("elementos_jugadas_jugadores"), list):
                            ref["elementos_jugadas_jugadores"].clear()
                        if isinstance(ref.get("elementos_mi_jugada"), list):
                            ref["elementos_mi_jugada"].clear()
                    except Exception:
                        pass
                    try:
                        if hasattr(self.mesa_juego, 'actualizar_jugadas') and self.mesa_juego.mesa:
                            self.mesa_juego.actualizar_jugadas(self.mesa_juego.mesa)
                    except Exception:
                        pass
                except Exception as e:
                    print(f"Error limpiando jugadas locales tras fin de ronda: {e}")
                if siguiente is not None:
                    try:
                        self.mesa_juego.elementos_mesa["nro_ronda"] = siguiente
                        try:
                            ronda_finalizada = siguiente - 1 if siguiente > 1 else 4
                            texto = f"Ronda {ronda_finalizada} Finalizada"
                            if hasattr(self.mesa_juego, 'mesa') and self.mesa_juego.mesa:
                                try:
                                    cartel = self.mesa_juego.crear_cartel_alerta(self.mesa_juego.mesa, texto, ancho=500, mostrar_boton_cerrar=False)
                                    cartel.mostrar()
                                    try:
                                        threading.Timer(2.0, lambda: cartel.ocultar()).start()
                                    except Exception:
                                        pass
                                except Exception:
                                    print(texto)
                        except Exception as e:
                            print(f"Error mostrando cartel fin de ronda: {e}")
                    except Exception as e:
                        print(f"Error procesando cambio de ronda: {e}")
        elif mensaje.get("type") == "Fin_Partida_Ganador":
            print("Fin_Partida_Ganador recibido:", mensaje)
            nombre = mensaje.get("nombre_ganador", "")
            texto = f"PARTIDA FINALIZADA!\nEl ganador es {nombre}"
            if self.mesa_juego:
                try:
                    cartel = self.mesa_juego.crear_cartel_alerta(self.mesa_juego.mesa, texto, ancho=700, mostrar_boton_cerrar=False)
                    cartel.mostrar()

                    # Ocultar/Desactivar botones de juego y la mano del jugador
                    try:
                        self.mesa_juego.limpiar_botones(self.mesa_juego.mesa)
                    except Exception:
                        pass
                    try:
                        self.mesa_juego.actualizar_estado_mano(accion="desactivar_boton")
                    except Exception:
                        pass
                    try:
                        self.mesa_juego.actualizar_estado_mano(accion="desactivar_mano")
                    except Exception:
                        pass

                    try:
                        # Asegurar que overlays y botones existen
                        if not hasattr(self.mesa_juego, 'overlays'):
                            self.mesa_juego.overlays = []
                        if not hasattr(self.mesa_juego, 'botones'):
                            self.mesa_juego.botones = []

                        ancho_b = 300
                        alto_b = 60
                        # Asegurar que el cartel ya está centrado
                        cartel.centrar_en_pantalla()
                        x_b = int(cartel.x + (cartel.ancho - ancho_b) // 2)
                        y_b = int(cartel.y + cartel.alto - alto_b - 20)

                        def accion_volver():
                            try:
                                self.mesa_juego.salir_partida()
                            except Exception:
                                pass

                        boton = Boton(
                            un_juego=self.mesa_juego.un_juego,
                            texto="VOLVER AL MENÚ",
                            ancho=ancho_b,
                            alto=alto_b,
                            x=x_b,
                            y=y_b,
                            tamaño_fuente=constantes.F_PEQUENA,
                            fuente=constantes.FUENTE_ESTANDAR,
                            color=constantes.ELEMENTO_FONDO_PRINCIPAL,
                            radio_borde=constantes.REDONDEO_NORMAL,
                            color_texto=constantes.COLOR_TEXTO_PRINCIPAL,
                            color_borde=constantes.ELEMENTO_BORDE_SECUNDARIO,
                            grosor_borde=constantes.BORDE_INTERMEDIO,
                            color_borde_hover=constantes.ELEMENTO_HOVER_PRINCIPAL,
                            color_borde_clicado=constantes.ELEMENTO_CLICADO_PRINCIPAL,
                            grupo=[],
                            valor="volver_menu",
                            accion=accion_volver
                        )

                        # Asegurar visibilidad y agregar tanto a overlays como a botones
                        boton.visible = True
                        # Si hay menus activos en la mesa, anexar al último menu activo (se dibuja encima)
                        target_menu = None
                        try:
                            if hasattr(self.mesa_juego, 'menus_activos') and self.mesa_juego.menus_activos:
                                target_menu = self.mesa_juego.menus_activos[-1]
                        except Exception:
                            target_menu = None
                        if target_menu is None:
                            target_menu = self.mesa_juego.mesa if hasattr(self.mesa_juego, 'mesa') else None

                        if target_menu is not None:
                            if not hasattr(target_menu, 'overlays'):
                                target_menu.overlays = []
                            if not hasattr(target_menu, 'botones'):
                                target_menu.botones = []
                            if boton not in target_menu.overlays:
                                target_menu.overlays.append(boton)
                            if boton not in target_menu.botones:
                                target_menu.botones.append(boton)
                        else:
                            # Fallback: anexar a la mesa_juego directamente
                            if boton not in self.mesa_juego.overlays:
                                self.mesa_juego.overlays.append(boton)
                            if boton not in self.mesa_juego.botones:
                                self.mesa_juego.botones.append(boton)

                        # Guardar referencia al boton de volver sin ponerlo en botones_accion
                        try:
                            self.mesa_juego.boton_volver = boton
                        except Exception:
                            pass
                    except Exception as e:
                        print(f"Error creando boton volver al menu: {e}")
                    except Exception:
                        pass
                except Exception:
                    print(texto)
        elif mensaje["type"] == "Mazo_Nuevo":
            print("Mazo nuevo recibido")
            print(mensaje)
            self.mesa_juego.elementos_mesa["cantidad_cartas_mazo"] = mensaje.get("cantidad_cartas_mazo")
            self.mesa_juego.actualizar_mazo(self.mesa_juego.mesa)
            if mensaje["cantidad_cartas_quema"] == None and mensaje["direccion"] == None:
                self.mesa_juego.elementos_mesa["dato_carta_quema"] = None
                self.mesa_juego.carta_quema = None
                self.mesa_juego.elementos_mesa["cantidad_cartas_quema"] = 0
                self.mesa_juego.actualizar_carta_quema(self.mesa_juego.mesa)
                self.mesa_juego.borrar_mazo_quema()

            elif mensaje["cantidad_cartas_quema"] == None and mensaje["direccion"] != None:
                self.mesa_juego.elementos_mesa["dato_carta_quema"] = None
                self.mesa_juego.carta_quema = None
                self.mesa_juego.elementos_mesa["cantidad_cartas_quema"] = 0
                self.mesa_juego.actualizar_carta_quema(self.mesa_juego.mesa)
                self.mesa_juego.borrar_mazo_quema()
        elif mensaje["type"] == "validacion_extender":
            print(mensaje)
            self.mesa_juego.elementos_mesa["datos_mano_jugador"] = mensaje.get("datos_mano_jugador")
            self.mesa_juego.elementos_mesa["jugada"] = mensaje.get("jugada")
            self.mesa_juego.elementos_mesa["jugadas_jugadores"] = mensaje.get("jugadas_jugadores")
            self.mesa_juego.cargar_datos_mano_jugador()
            self.mesa_juego.cargar_elemento_mi_mano()
            self.mesa_juego.actualizar_mano_visual(self.mesa_juego.mesa,accion="reorganizar_todo")
            self.mesa_juego.actualizar_jugadas(self.mesa_juego.mesa)
            for boton in list(self.mesa_juego.botones_accion.values()):
                if boton in self.mesa_juego.mesa.botones:
                    boton.accion == self.mesa_juego.crear_botones_despues_de_bajarse(self.mesa_juego.mesa)
                    self.mesa_juego.crear_botones_extender_jug(self.mesa_juego.mesa,opc=True)
        elif mensaje["type"] == "se_extendio":
            self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
            self.mesa_juego.elementos_mesa["jugadas_jugadores"] = mensaje.get("jugadas_jugadores")
            self.mesa_juego.actualizar_jugadas(self.mesa_juego.mesa)
            self.mesa_juego.actualizar_manos_jugadores(self.mesa_juego.mesa)
        elif mensaje['type'] == 'elegir_posicion_seguidilla':
            print("El servidor solicita elegir posición para la seguidilla.")
            self.mesa_juego.crear_botones_elegir_posicion_seguidilla(self.mesa_juego.mesa)
        elif mensaje["type"] == "elejir_donde_extender":
            print("El servidor solicita elegir dónde extender la jugada.")
            if mensaje["trio_seguidilla"]:
                self.mesa_juego.crear_botones_elegir_donde_extender(self.mesa_juego.mesa,lug = mensaje["posicion_seguidilla"])
            elif mensaje["trio_seguidilla"] == False and mensaje["seguidilla_seguidilla"] == False:
                try:
                    if mensaje["ronda"] == 2:
                        ronda == mensaje["ronda"] 
                except:
                    ronda = None
                self.mesa_juego.crear_botones_elegir_pos_seguidilla(ronda, pos1 = mensaje["posicion_seguidilla"])    
            elif mensaje["seguidilla_seguidilla"] == True:
                self.mesa_juego.crear_botones_elegir_donde_extender(self.mesa_juego.mesa,lug = mensaje["posicion_seguidilla1"],lug2 = mensaje["posicion_seguidilla2"],ronda = mensaje["ronda"])
        elif mensaje['type'] == 'Seleccion_cancelada':
            self.mesa_juego.crear_botones_seleccionar_jugada(self.mesa_juego.mesa)
            self.mesa_juego.restaurar_comportamiento_mi_mano()
            self.mesa_juego.modificar_comportamiento_mi_mano()
        elif mensaje['type'] == 'jugada_invalida':
            self.mesa_juego.crear_botones_seleccionar_jugada(self.mesa_juego.mesa)
            self.mesa_juego.restaurar_comportamiento_mi_mano()
            self.mesa_juego.modificar_comportamiento_mi_mano()
        elif mensaje["type"] == "jugada_cancelada":
            print(mensaje)
            self.mesa_juego.elementos_mesa["datos_mano_jugador"] = mensaje.get("datos_mano_jugador")
            self.mesa_juego.elementos_mesa["jugada"] = mensaje.get("jugada")
            self.mesa_juego.elementos_mesa["jugadas_jugadores"] = mensaje.get("jugadas_jugadores")
            self.mesa_juego.cargar_datos_mano_jugador()
            self.mesa_juego.cargar_elemento_mi_mano()
            self.mesa_juego.actualizar_mano_visual(self.mesa_juego.mesa,accion="reorganizar_todo")
            self.mesa_juego.actualizar_jugadas(self.mesa_juego.mesa)
            self.mesa_juego.modificar_comportamiento_mi_mano()
            self.mesa_juego.crear_botones_seleccionar_jugada(self.mesa_juego.mesa)
            for boton in list(self.mesa_juego.botones_accion.values()):
                if boton in self.mesa_juego.mesa.botones:
                    boton.texto == "DESCARTAR"
                    self.mesa_juego.crear_botones_seleccionar_jugada(self.mesa_juego.mesa)
        elif mensaje["type"] == "regresando_menu":
            print("Regresando al menú principal.")
            self.mesa_juego.crear_botones_jugar_descartar(self.mesa_juego.mesa)
        elif mensaje["type"] == "mostrar_extender":
            self.mesa_juego.crear_botones_despues_de_bajarse(self.mesa_juego.mesa)
        elif mensaje["type"] == "mensaje_seguidillas_continuas":
            print(mensaje)
            self.mesa_juego.crear_botones_seleccionar_jugada(self.mesa_juego.mesa)
        elif mensaje["type"] == "No_Puede_Descartar_Misma_Carta":
            self.mesa_juego.alerta_carta_descartar_invalida(self.mesa_juego.mesa)
        elif mensaje["type"] == "Error_Descartar":
            self.mesa_juego.alerta_carta_descartar_invalida(self.mesa_juego.mesa)
        elif mensaje["type"] == "No_Puede_Descartar_Joker":
            self.mesa_juego.alerta_no_puede_descartar_joker(self.mesa_juego.mesa)
        elif mensaje["type"] == "reemplazar_valido":
            print(mensaje)
            self.mesa_juego.elementos_mesa["datos_mano_jugador"] = mensaje.get("nueva_mano")
            self.mesa_juego.elementos_mesa["jugada"] = mensaje.get("jugada")
            self.mesa_juego.elementos_mesa["jugadas_jugadores"] = mensaje.get("jugadas_jugadores")
            self.mesa_juego.cargar_datos_mano_jugador()
            self.mesa_juego.cargar_elemento_mi_mano()
            self.mesa_juego.actualizar_mano_visual(self.mesa_juego.mesa,accion="reorganizar_todo")
            self.mesa_juego.actualizar_jugadas(self.mesa_juego.mesa)
            self.mesa_juego.restaurar_comportamiento_mi_mano()
        elif mensaje["type"] == "Ciert_jugador_compro_carta_del_descarte":
            self.mesa_juego.alerta_jugador_compro_carta_del_descarte(self.mesa_juego.mesa, mensaje["jugador_compro"])
        elif mensaje["type"] == "reemplazaron_tu_jugada":
            self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
            self.mesa_juego.elementos_mesa["jugadas_jugadores"] = mensaje.get("jugadas_jugadores")
            self.mesa_juego.elementos_mesa["jugada"] = mensaje.get("jugada")
            self.mesa_juego.actualizar_jugadas(self.mesa_juego.mesa)
            self.mesa_juego.actualizar_manos_jugadores(self.mesa_juego.mesa)
        elif mensaje["type"] == "extendieron_tu_jugada":
            self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
            self.mesa_juego.elementos_mesa["jugadas_jugadores"] = mensaje.get("jugadas_jugadores")
            self.mesa_juego.elementos_mesa["jugada"] = mensaje.get("jugada")
            self.mesa_juego.actualizar_jugadas(self.mesa_juego.mesa)
            self.mesa_juego.actualizar_manos_jugadores(self.mesa_juego.mesa)
        elif mensaje["type"] == "Reconectar_partida":
            print(mensaje)
            if not self.mesa_juego:
                self.mesa_juego = mesa_interfaz.Mesa_interfaz(self.un_juego)
            self.mesa_juego.elementos_mesa["datos_mano_jugador"] = mensaje.get("mano")
            self.mesa_juego.elementos_mesa["jugada"] = mensaje.get("jugada")
            self.mesa_juego.elementos_mesa["jugadas_jugadores"] = mensaje.get("jugadas_jugadores")
            self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
            self.mesa_juego.elementos_mesa["cantidad_cartas_mazo"] = mensaje.get("mazo")
            self.mesa_juego.elementos_mesa["dato_carta_quema"] = mensaje.get("dato_carta_quema")
            self.mesa_juego.elementos_mesa["dato_carta_descarte"] = mensaje.get("dato_carta_descarte")
            evento_py = pygame.event.Event(constantes.EVENTO_INICIAR_PARTIDA,un_juego=self.un_juego,mesa=self.mesa_juego,datos=mensaje)
            pygame.event.post(evento_py)
            time.sleep(5)
            if mensaje.get("jugadas_jugadores") or mensaje.get("jugada"):
                self.mesa_juego.actualizar_jugadas(self.mesa_juego.mesa)

            
    def encontrar_ip_servidor(self,un_juego):
        socket_busqueda = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_busqueda.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_busqueda.bind(('', 5556)) # Escuchar en el mismo puerto que el anuncio
        socket_busqueda.settimeout(5) # Esperar 5 segundos

        print("Buscando servidor en la red...")
        while self.buscador:
            try:
                data, direccion_servidor = socket_busqueda.recvfrom(1024)
                mensaje = json.loads(data.decode('utf-8'))
                ip_encontrada = direccion_servidor[0]
                nombre_partida = mensaje.get('partida', 'Desconocida')
                nombre_host = mensaje.get('host', 'Host')
                max_jugadores = mensaje.get('max_jugadores', 7)
                jugadores = mensaje.get('jugadores', 0)
                self.jugadores_desconectados = mensaje.get('id_jugadores_desconectados', {})
                lista_jugadores = mensaje.get('lista_jugadores', [])
                info = {"nombre": nombre_partida,"jugadores":jugadores,"max_jugadores":max_jugadores,"ip": ip_encontrada,"lista_jugadores":lista_jugadores,"creador":nombre_host}
                servidor_encontrado = None
                for server in self.conexiones_disponibles:
                    if server['ip'] == ip_encontrada:
                        servidor_encontrado = server
                        break  # Se encontró, no es necesario seguir buscando
                if mensaje.get('type') == 'RummyServer' and servidor_encontrado == None:
                    print(f"Servidor encontrado en la IP: {ip_encontrada} - Partida: {nombre_partida} - Host: {nombre_host}")
                    self.conexiones_disponibles.append(info)
                    evento_py = pygame.event.Event(constantes.EVENTO_SALAS_ENCONTRADAS,salas=self.conexiones_disponibles)
                    pygame.event.post(evento_py)
                    print(f"Conexiones disponibles: {self.conexiones_disponibles}")
                elif servidor_encontrado["jugadores"] != jugadores:
                    print(f"Actualizando Partida {nombre_partida} ")
                    servidor_encontrado["jugadores"] = jugadores
                    servidor_encontrado["lista_jugadores"] = lista_jugadores
                    evento_py = pygame.event.Event(constantes.EVENTO_SALAS_ENCONTRADAS,salas=self.conexiones_disponibles)
                    pygame.event.post(evento_py)
                else:
                    print(f"Servidor ya listado: {ip_encontrada}")


            except socket.timeout:
                    print("Tiempo de búsqueda agotado. Servidor no encontrado.")
                    self.conexiones_disponibles = []
                    evento_py = pygame.event.Event(constantes.EVENTO_SALAS_ENCONTRADAS,salas=self.conexiones_disponibles)
                    pygame.event.post(evento_py)
            except Exception as e:
                print(f"Error buscando servidor: {e}")
            finally:
                time.sleep(5) # Esperar antes de la siguiente búsqueda
    

    def intentar_reconexion(self, ip_servidor, intentos=5, espera=3):
        """
        Intenta reconectar automáticamente al servidor usando el id_jugador anterior.
        """
        # Cargar el ID local antes de intentar reconectar
        id_local = self.cargar_id_local()
        if id_local:
            self.id_jugador = id_local
        for intento in range(intentos):
            print(f"Intentando reconectar... (Intento {intento + 1}/{intentos})")
            exito = self.conectar_a_servidor(ip_servidor, id_jugador_reconectar=self.id_jugador)
            if exito:
                print("Reconexión exitosa.")
                return True
            time.sleep(espera)
        print("No se pudo reconectar después de varios intentos.")
        return False
    
    def enviar_accion(self, accion, datos=None):
        if self.conectado and self.socket_cliente:
            mensaje = {'type': accion}
            if datos:
                mensaje.update(datos)
            try:
                self.socket_cliente.sendall((json.dumps(mensaje) + '\n').encode('utf-8'))
            except Exception as e:
                print(f"Error al enviar acción al servidor: {e}")
        else:
            print("No conectado al servidor, no se puede enviar la acción.")

    def verificar_conexion_nueva(self,ip_encontrada):
        for x in self.conexiones_disponibles:
            if ip_encontrada != self.conexiones_disponibles["ip"]:
                return True
            else:
                return False

    def desconectar_cliente(self):
        """Cierra la conexión del cliente"""
        self.conectado = False
        if self.socket_cliente and self.id_jugador is not None:
            try:
                mensaje_desconexion = {
                    'type': 'ClienteDesconectado',
                    'id_jugador': self.id_jugador
                }
                self.socket_cliente.send(json.dumps(mensaje_desconexion).encode('utf-8'))
                time.sleep(2)
            except Exception as e:
                print(f"Error al notificar al servidor sobre la desconexión: {e}")
            finally:
                try:
                    self.socket_cliente.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                self.socket_cliente.close()
                self.socket_cliente = None
                if hasattr(self, '_manejo_mensaje_red'):
                    self._manejo_mensaje_red({
                        'type': 'JugadorDesconectado',
                        'id_jugador': self.id_jugador,
                        'TotalJugadores': len(self.clientes) if hasattr(self, 'clientes') else 0
                    })
        else:
            print("Socket cliente no existe o ID de jugador no asignado")
            print(f"Socket cliente: {self.socket_cliente}, ID jugador: {self.id_jugador}")

        # Cerrar hilo de recepción del cliente
        if self.hilo_recepcion and threading.current_thread() != self.hilo_recepcion:
            self.hilo_recepcion.join()

    def desconectar_servidor(self):
        """Cierra el servidor y notifica a los clientes"""
        self.ejecutandose = False
        if self.socket_servidor:
            try:
                if hasattr(self, 'difundir'):
                    self.difundir({
                        'type': 'ServidorCerrado'
                    })
            except Exception as e:
                print(f"Error al notificar a cliente sobre el cierre del servidor: {e}")
            self.socket_servidor.close()
            self.socket_servidor = None

    def desconectar(self):
        """Cierra todas las conexiones (compatibilidad hacia atrás)"""
        self.ejecutandose = False
        self.conectado = False
        self.desconectar_servidor()
        self.desconectar_cliente()

