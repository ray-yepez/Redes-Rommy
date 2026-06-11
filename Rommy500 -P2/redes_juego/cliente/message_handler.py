"""Manejador de mensajes de red del cliente"""

import pygame
import time
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

class MessageHandler:
    def __init__(self, client_instance):
        self.client = client_instance

    def handle_message(self, mensaje):
        # Método completo para procesar todos los mensajes del servidor
        # Este método es muy largo (360+ líneas) y se mantiene completo aquí

        # Inicializar variable si no existe
        if not hasattr(self, 'descarto_recientemente'):
            self.client.descarto_recientemente = False
        if mensaje['type'] == 'Bienvenido':
            self.client.id_jugador = mensaje['id_jugador']
            self.client.guardar_id_local()
            nombre = mensaje.get('nombre')
            print(f'ID:{self.client.id_jugador} - Nombre: {nombre}')
            self.client.estado_juego = mensaje.get('game_state', None)
        elif mensaje['type'] == 'Reconectado':
            self.client.id_jugador = mensaje['id_jugador']
            self.client.guardar_id_local()
            self.client.estado_juego = mensaje.get('estado_juego', None)
            print(f"Reconectado como {mensaje.get('nombre')}, estado restaurado.")
        elif mensaje['type'] == 'JugadorReconectado':
            nombre = mensaje.get('nombre')
            print(f"Jugador {mensaje['nombre']} (ID {mensaje['id_jugador']}) se ha reconectado.")
            if self.client.un_juego:
                nueva_lista = self.client.un_juego.lista_elementos["lista_jugadores"]
                if mensaje.get('lista_jugadores') != nueva_lista:
                    evento_py = pygame.event.Event(constantes.EVENTO_NUEVO_JUGADOR,nueva_lista =mensaje.get('lista_jugadores'))
                    pygame.event.post(evento_py)
        elif mensaje['type'] == 'game_update':
            self.client.estado_juego = mensaje.get('game_state', None)
        elif mensaje['type'] == 'NuevoJugador':
            nombre = mensaje.get('nombre')
            print(f"Nuevo jugador conectado: ID {mensaje['id_jugador']} - Nombre: {nombre}, Total jugadores: {mensaje['TotalJugadores']}")
            if self.client.un_juego:
                nueva_lista = self.client.un_juego.lista_elementos.get("lista_jugadores", [])
                if mensaje.get('lista_jugadores') != nueva_lista:
                    evento_py = pygame.event.Event(constantes.EVENTO_NUEVO_JUGADOR,nueva_lista =mensaje.get('lista_jugadores'))
                    pygame.event.post(evento_py)
        elif mensaje['type'] == 'JugadorDesconectado':
            print(f"Jugador desconectado: ID {mensaje['id_jugador']}, Total jugadores: {mensaje['TotalJugadores']}")
            print(mensaje.get('lista_jugadores'))
            nombre = mensaje.get('nombre')
            if self.client.un_juego:
                nueva_lista = self.client.un_juego.lista_elementos.get("lista_jugadores", [])
                if mensaje.get('lista_jugadores') != nueva_lista:
                    evento_py = pygame.event.Event(constantes.EVENTO_NUEVO_JUGADOR,nueva_lista =mensaje.get('lista_jugadores'))
                    pygame.event.post(evento_py)
        elif mensaje['type'] == 'ServidorCerrado':
            print("El servidor ha cerrado la conexión.")
        elif mensaje["type"] == "ManoInicial":
            if not self.client.mesa_juego:
                self.client.mesa_juego = mesa_interfaz.Mesa_interfaz(self.client.un_juego)
            evento_py = pygame.event.Event(constantes.EVENTO_INICIAR_PARTIDA,un_juego=self.client.un_juego,mesa=self.client.mesa_juego,datos=mensaje)
            pygame.event.post(evento_py)
            print(mensaje)
        elif mensaje["type"] == "Actualizacion_Carta_Descarte":
            print(mensaje)
            if self.client.mesa_juego:
                # Si dato_carta_descarte es None, significa que alguien compró o tomó la carta
                # Resetear la variable para que el jugador que descartó pueda tener botones nuevamente
                if mensaje.get("dato_carta_descarte") is None:
                    self.client.descarto_recientemente = False
                self.client.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
                self.client.mesa_juego.elementos_mesa["dato_carta_descarte"] = None
                self.client.mesa_juego.carta_descarte = None
                self.client.mesa_juego.actualizar_carta_descarte(self.client.mesa_juego.mesa)
                self.client.mesa_juego.actualizar_manos_jugadores(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "Actualizacion_Toma_Descarte":
            if self.client.mesa_juego:
                self.client.mesa_juego.procesar_tomar_descarte(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "Descartar_Carta":
            self.client.mesa_juego.finalizar_turno(self.client.mesa_juego.mesa)
            # Desactivar cartas del jugador que descartó
            # Marcar que el jugador descartó recientemente (no puede comprar su propia carta)
            self.client.descarto_recientemente = True
        elif mensaje["type"] == "Reactivar_Botones_No_Turno":
            # Ya no es su carta, puede tener botones nuevamente
            self.client.descarto_recientemente = False
            # Recrear botones del jugador que descartó (ya no es su carta, y no es su turno)
            if self.client.mesa_juego:
                if not self.client.mesa_juego.tu_turno:
                    # Actualizar turno_robar antes de crear los botones
                    self.client.mesa_juego.determinar_turno_robar()
                    # Los botones se crearán desactivados si no tiene turno_robar
                    self.client.mesa_juego.crear_botones_no_turno(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "Actualizacion_Decartar_Carta":
            print(mensaje)
            if self.client.mesa_juego:
                self.client.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
                self.client.mesa_juego.elementos_mesa["dato_carta_descarte"] = mensaje.get("dato_carta_descarte")
                self.client.mesa_juego.cargar_dato_carta_descarte()
                self.client.mesa_juego.cargar_elemento_carta_descarte()
                self.client.mesa_juego.actualizar_carta_descarte(self.client.mesa_juego.mesa)
                self.client.mesa_juego.actualizar_manos_jugadores(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "Rechazar_descarte":
            if self.client.mesa_juego:
                if mensaje.get("turno_robar") == False:
                    self.client.mesa_juego.actualizar_estado_mano(accion="esperar_robar")
        elif mensaje["type"] == "No_descartar":
            print(mensaje)
            if self.client.mesa_juego:
                self.client.mesa_juego.elementos_mesa["turno_robar"] = mensaje.get("turno_robar")
                self.client.mesa_juego.turno_robar = mensaje.get("turno_robar")
                if mensaje.get("turno_robar") == False:
                    self.client.mesa_juego.actualizar_estado_mano(accion="desactivar_boton")
                else:
                    self.client.mesa_juego.actualizar_estado_mano(accion="robar")
        elif mensaje["type"] == "comprar":
            print(mensaje)
            self.client.mesa_juego.procesar_comprar(self.client.mesa_juego.mesa,mensaje.get("carta_extra"))
            self.client.mesa_juego.actualizar_estado_mano(accion="desactivar_boton")                       
            print(mensaje.get("carta_extra"))
            print("XD")
        elif mensaje["type"] == "Compra_realizada":
            self.client.mesa_juego.actualizar_estado_mano(accion="activar_mano")
            self.client.mesa_juego.actualizar_estado_mano(accion="activar_boton")
            self.client.mesa_juego.accion_tomar_mazo()
        elif mensaje["type"] == "Actualizar_botones":
            print(mensaje)
            if self.client.mesa_juego:
                # Si se quema la carta (dato_carta_descarte es None), resetear la variable
                if mensaje.get("dato_carta_descarte") is None:
                    self.client.descarto_recientemente = False
                self.client.mesa_juego.elementos_mesa["turno_robar"] = mensaje.get("turno_robar")
                self.client.mesa_juego.elementos_mesa["cantidad_cartas_quema"] = mensaje.get("cantidad_cartas_quema")
                self.client.mesa_juego.elementos_mesa["dato_carta_descarte"] = None
                self.client.mesa_juego.elementos_mesa["dato_carta_quema"] = mensaje.get("dato_carta_quema")
                if self.client.mesa_juego.elementos_mesa["turno_robar"] == True:
                    self.client.mesa_juego.actualizar_estado_mano(accion="activar_mano")
                else:
                    self.client.mesa_juego.actualizar_estado_mano(accion="desactivar_boton")      
                self.client.mesa_juego.actualizar_botones()
                self.client.mesa_juego.actualizar_carta_quema(self.client.mesa_juego.mesa)
                self.client.mesa_juego.actualizar_mazo_quema()
                self.client.mesa_juego.cargar_dato_carta_descarte()
                self.client.mesa_juego.cargar_elemento_carta_descarte()
                self.client.mesa_juego.actualizar_carta_descarte(self.client.mesa_juego.mesa)
                self.client.mesa_juego.accion_tomar_mazo()
        elif mensaje["type"] == "Tomar_carta_mazo":
            print(mensaje)
            self.client.mesa_juego.procesar_tomar_mazo(self.client.mesa_juego.mesa,mensaje.get("carta_extra"))
            self.client.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
            self.client.mesa_juego.actualizar_mazo(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "Pasar_Turno":
            self.client.mesa_juego.elementos_mesa["jugador_mano"] = mensaje.get("jugador_mano")
            self.client.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
            self.client.mesa_juego.elementos_mesa["turno_robar"] = mensaje.get("turno_robar")
            self.client.mesa_juego.actualizar_manos_jugadores(self.client.mesa_juego.mesa)
            self.client.mesa_juego.limpiar_botones(self.client.mesa_juego.mesa)
            # Solo crear botones si el jugador NO descartó recientemente
            if not self.client.descarto_recientemente:
                self.client.mesa_juego.crear_botones_no_turno(self.client.mesa_juego.mesa)
            self.client.mesa_juego.actualizar_estado_mano(accion="desactivar_boton")
        elif mensaje["type"] == "Tu_Turno":
            self.client.mesa_juego.elementos_mesa["jugador_mano"] = mensaje.get("jugador_mano")
            self.client.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
            self.client.mesa_juego.actualizar_manos_jugadores(self.client.mesa_juego.mesa)
            self.client.mesa_juego.limpiar_botones(self.client.mesa_juego.mesa)
            self.client.mesa_juego.crear_botones_inicio_turno(self.client.mesa_juego.mesa)
            self.client.mesa_juego.actualizar_estado_mano(accion="activar_mano")
        elif mensaje["type"] == "Actualizar_Etiqueta_Turno":
            self.client.mesa_juego.elementos_mesa["jugador_mano"] = mensaje.get("jugador_mano")
            self.client.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
            self.client.mesa_juego.elementos_mesa["turno_robar"] = mensaje.get("turno_robar")
            self.client.mesa_juego.actualizar_indicador_turno()
            self.client.mesa_juego.actualizar_elementos_jugadores()
            # Si no es el turno del jugador y no descartó recientemente, crear botones
            if self.client.mesa_juego:
                self.client.mesa_juego.determinar_turno()
                if not self.client.mesa_juego.tu_turno and not self.client.descarto_recientemente:
                    # Asegurarse de que los botones estén limpios antes de crear nuevos
                    self.client.mesa_juego.limpiar_botones(self.client.mesa_juego.mesa)
                    self.client.mesa_juego.crear_botones_no_turno(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "quema_del_mono":
            print(mensaje)
            self.client.mesa_juego.crear_botones_quema_mono(self.client.mesa_juego.mesa)
            self.client.mesa_juego.actualizar_estado_mano(accion="activar_mano")
        elif mensaje["type"] == "Actualizar_quema_descarte":
            print(mensaje)
            self.client.mesa_juego.elementos_mesa["cantidad_cartas_quema"] = mensaje.get("cantidad_cartas_quema")
            self.client.mesa_juego.elementos_mesa["dato_carta_descarte"] = None
            self.client.mesa_juego.actualizar_mazo_quema()      
            self.client.mesa_juego.cargar_dato_carta_descarte()
            self.client.mesa_juego.cargar_elemento_carta_descarte()
            self.client.mesa_juego.actualizar_carta_descarte(self.client.mesa_juego.mesa)            
        elif mensaje["type"] == "descartar_mono":
            self.client.mesa_juego.elementos_mesa["dato_carta_quema"] = mensaje.get("dato_carta_quema")
            self.client.mesa_juego.actualizar_carta_quema(self.client.mesa_juego.mesa)
            self.client.mesa_juego.finalizar_turno(self.client.mesa_juego.mesa)


        elif mensaje["type"] == "actualizar_mono":
            self.client.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
            self.client.mesa_juego.elementos_mesa["dato_carta_descarte"] = mensaje.get("dato_carta_descarte")
            self.client.mesa_juego.elementos_mesa["dato_carta_quema"] = mensaje.get("dato_carta_quema")
            self.client.mesa_juego.actualizar_carta_quema(self.client.mesa_juego.mesa)
            self.client.mesa_juego.cargar_dato_carta_descarte()
            self.client.mesa_juego.cargar_elemento_carta_descarte()
            self.client.mesa_juego.actualizar_carta_descarte(self.client.mesa_juego.mesa)
            self.client.mesa_juego.actualizar_manos_jugadores(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "validacion_trio":
            self.client.mesa_juego.seleccionar_seguidilla(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "validacion_trio_fallida":
            self.client.mesa_juego.alerta_trio_invalido(self.client.mesa_juego.mesa)
            self.client.mesa_juego.restaurar_comportamiento_mi_mano()
            self.client.mesa_juego.modificar_comportamiento_mi_mano()
        elif mensaje["type"] == "validacion_seguidilla":
            print(mensaje)
            print("validacion aceptada")
            self.client.mesa_juego.elementos_mesa["datos_mano_jugador"] = mensaje.get("datos_mano_jugador")
            self.client.mesa_juego.elementos_mesa["jugada"] = mensaje.get("jugada")
            self.client.mesa_juego.elementos_mesa["jugadas_jugadores"] = mensaje.get("jugadas_jugadores")
            self.client.mesa_juego.cargar_datos_mano_jugador()
            self.client.mesa_juego.cargar_elemento_mi_mano()
            self.client.mesa_juego.actualizar_mano_visual(self.client.mesa_juego.mesa,accion="reorganizar_todo")
            self.client.mesa_juego.actualizar_jugadas(self.client.mesa_juego.mesa)
            self.client.mesa_juego.crear_botones_jugar_descartar(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "validacion_seguidilla_fallida":
            self.client.mesa_juego.alerta_seguidilla_invalida(self.client.mesa_juego.mesa)
            self.client.mesa_juego.restaurar_comportamiento_mi_mano()
            self.client.mesa_juego.modificar_comportamiento_mi_mano()
        elif mensaje["type"] == "seleccion_valida":
            print(mensaje)
            if mensaje["actualizar"] == True:
                self.client.mesa_juego.crear_botones_seleccionar_jugada(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "validacion_bajarse":
            print("validacion aceptada")
            self.client.mesa_juego.elementos_mesa["datos_mano_jugador"] = mensaje.get("datos_mano_jugador")
            self.client.mesa_juego.elementos_mesa["jugada"] = mensaje.get("jugada")
            self.client.mesa_juego.elementos_mesa["jugadas_jugadores"] = mensaje.get("jugadas_jugadores")
            self.client.mesa_juego.cargar_datos_mano_jugador()
            self.client.mesa_juego.cargar_elemento_mi_mano()
            self.client.mesa_juego.actualizar_mano_visual(self.client.mesa_juego.mesa,accion="reorganizar_todo")
            self.client.mesa_juego.modificar_comportamiento_mi_mano()
            self.client.mesa_juego.actualizar_jugadas(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "se_bajo_alguien":
            self.client.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
            self.client.mesa_juego.elementos_mesa["jugadas_jugadores"] = mensaje.get("jugadas_jugadores")
            self.client.mesa_juego.actualizar_jugadas(self.client.mesa_juego.mesa)
            self.client.mesa_juego.actualizar_manos_jugadores(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "Fin_Ronda_Puntuaciones":
            print("Fin_Ronda_Puntuaciones recibido:", mensaje)
            resultados = mensaje.get("resultados", [])
            if self.client.mesa_juego:
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
                            self.client.mesa_juego.aplicar_puntuacion_servidor(nro, puntos_partida, puntos_acumulados, mano_objs)
                        except Exception:
                            self.client.mesa_juego.actualizar_puntos_jugador(nro, mano_objs)
                    else:
                        self.client.mesa_juego.actualizar_puntos_jugador(nro, mano_objs)
                siguiente = mensaje.get("siguiente_ronda")
                try:
                    self.client.mesa_juego.elementos_mesa["jugada"] = []
                    self.client.mesa_juego.elementos_mesa["jugadas_jugadores"] = []
                    try:
                        self.client.mesa_juego.jugada = []
                    except Exception:
                        pass
                    try:
                        self.client.mesa_juego.jugadas_jugadores = {}
                    except Exception:
                        pass
                    try:
                        ref = self.client.mesa_juego.referencia_elementos
                        if isinstance(ref.get("elementos_jugadas_jugadores"), list):
                            ref["elementos_jugadas_jugadores"].clear()
                        if isinstance(ref.get("elementos_mi_jugada"), list):
                            ref["elementos_mi_jugada"].clear()
                    except Exception:
                        pass
                    try:
                        if hasattr(self.client.mesa_juego, 'actualizar_jugadas') and self.client.mesa_juego.mesa:
                            self.client.mesa_juego.actualizar_jugadas(self.client.mesa_juego.mesa)
                    except Exception:
                        pass
                except Exception as e:
                    print(f"Error limpiando jugadas locales tras fin de ronda: {e}")
                if siguiente is not None:
                    try:
                        self.client.mesa_juego.elementos_mesa["nro_ronda"] = siguiente
                        try:
                            ronda_finalizada = siguiente - 1 if siguiente > 1 else 4
                            texto = f"Ronda {ronda_finalizada} Finalizada"
                            if hasattr(self.client.mesa_juego, 'mesa') and self.client.mesa_juego.mesa:
                                try:
                                    cartel = self.client.mesa_juego.crear_cartel_alerta(self.client.mesa_juego.mesa, texto, ancho=500, mostrar_boton_cerrar=False)
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
            if self.client.mesa_juego:
                try:
                    cartel = self.client.mesa_juego.crear_cartel_alerta(self.client.mesa_juego.mesa, texto, ancho=700, mostrar_boton_cerrar=False)
                    cartel.mostrar()

                    # Ocultar/Desactivar botones de juego y la mano del jugador
                    try:
                        self.client.mesa_juego.limpiar_botones(self.client.mesa_juego.mesa)
                    except Exception:
                        pass
                    try:
                        self.client.mesa_juego.actualizar_estado_mano(accion="desactivar_boton")
                    except Exception:
                        pass
                    try:
                        self.client.mesa_juego.actualizar_estado_mano(accion="desactivar_mano")
                    except Exception:
                        pass

                    try:
                        # Asegurar que overlays y botones existen
                        if not hasattr(self.client.mesa_juego, 'overlays'):
                            self.client.mesa_juego.overlays = []
                        if not hasattr(self.client.mesa_juego, 'botones'):
                            self.client.mesa_juego.botones = []

                        ancho_b = 300
                        alto_b = 60
                        # Asegurar que el cartel ya está centrado
                        cartel.centrar_en_pantalla()
                        x_b = int(cartel.x + (cartel.ancho - ancho_b) // 2)
                        y_b = int(cartel.y + cartel.alto - alto_b - 20)

                        def accion_volver():
                            try:
                                self.client.mesa_juego.salir_partida()
                            except Exception:
                                pass

                        boton = Boton(
                            un_juego=self.client.mesa_juego.un_juego,
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
                            if hasattr(self.client.mesa_juego, 'menus_activos') and self.client.mesa_juego.menus_activos:
                                target_menu = self.client.mesa_juego.menus_activos[-1]
                        except Exception:
                            target_menu = None
                        if target_menu is None:
                            target_menu = self.client.mesa_juego.mesa if hasattr(self.client.mesa_juego, 'mesa') else None

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
                            if boton not in self.client.mesa_juego.overlays:
                                self.client.mesa_juego.overlays.append(boton)
                            if boton not in self.client.mesa_juego.botones:
                                self.client.mesa_juego.botones.append(boton)

                        # Guardar referencia al boton de volver sin ponerlo en botones_accion
                        try:
                            self.client.mesa_juego.boton_volver = boton
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
            self.client.mesa_juego.elementos_mesa["cantidad_cartas_mazo"] = mensaje.get("cantidad_cartas_mazo")
            self.client.mesa_juego.actualizar_mazo(self.client.mesa_juego.mesa)
            if mensaje["cantidad_cartas_quema"] == None and mensaje["direccion"] == None:
                self.client.mesa_juego.elementos_mesa["dato_carta_quema"] = None
                self.client.mesa_juego.carta_quema = None
                self.client.mesa_juego.elementos_mesa["cantidad_cartas_quema"] = 0
                self.client.mesa_juego.actualizar_carta_quema(self.client.mesa_juego.mesa)
                self.client.mesa_juego.borrar_mazo_quema()

            elif mensaje["cantidad_cartas_quema"] == None and mensaje["direccion"] != None:
                self.client.mesa_juego.elementos_mesa["dato_carta_quema"] = None
                self.client.mesa_juego.carta_quema = None
                self.client.mesa_juego.elementos_mesa["cantidad_cartas_quema"] = 0
                self.client.mesa_juego.actualizar_carta_quema(self.client.mesa_juego.mesa)
                self.client.mesa_juego.borrar_mazo_quema()
        elif mensaje["type"] == "validacion_extender":
            print(mensaje)
            self.client.mesa_juego.elementos_mesa["datos_mano_jugador"] = mensaje.get("datos_mano_jugador")
            self.client.mesa_juego.elementos_mesa["jugada"] = mensaje.get("jugada")
            self.client.mesa_juego.elementos_mesa["jugadas_jugadores"] = mensaje.get("jugadas_jugadores")
            self.client.mesa_juego.cargar_datos_mano_jugador()
            self.client.mesa_juego.cargar_elemento_mi_mano()
            self.client.mesa_juego.actualizar_mano_visual(self.client.mesa_juego.mesa,accion="reorganizar_todo")
            self.client.mesa_juego.actualizar_jugadas(self.client.mesa_juego.mesa)
            for boton in list(self.client.mesa_juego.botones_accion.values()):
                if boton in self.client.mesa_juego.mesa.botones:
                    boton.accion = lambda: self.client.mesa_juego.crear_botones_despues_de_bajarse(self.client.mesa_juego.mesa)
                    self.client.mesa_juego.crear_botones_extender_jug(self.client.mesa_juego.mesa,opc=True)
        elif mensaje["type"] == "se_extendio":
            self.client.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
            self.client.mesa_juego.elementos_mesa["jugadas_jugadores"] = mensaje.get("jugadas_jugadores")
            self.client.mesa_juego.actualizar_jugadas(self.client.mesa_juego.mesa)
            self.client.mesa_juego.actualizar_manos_jugadores(self.client.mesa_juego.mesa)
        elif mensaje['type'] == 'elegir_posicion_seguidilla':
            print("El servidor solicita elegir posición para la seguidilla.")
            self.client.mesa_juego.crear_botones_elegir_posicion_seguidilla(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "elejir_donde_extender":
            print("El servidor solicita elegir dónde extender la jugada.")
            if mensaje["trio_seguidilla"]:
                self.client.mesa_juego.crear_botones_elegir_donde_extender(self.client.mesa_juego.mesa,lug = mensaje["posicion_seguidilla"])
            elif mensaje["trio_seguidilla"] == False and mensaje["seguidilla_seguidilla"] == False:
                try:
                    if mensaje["ronda"] == 2:
                        ronda = mensaje["ronda"] 
                except:
                    ronda = None
                self.client.mesa_juego.crear_botones_elegir_pos_seguidilla(ronda, pos1 = mensaje["posicion_seguidilla"])    
            elif mensaje["seguidilla_seguidilla"] == True:
                self.client.mesa_juego.crear_botones_elegir_donde_extender(self.client.mesa_juego.mesa,lug = mensaje["posicion_seguidilla1"],lug2 = mensaje["posicion_seguidilla2"],ronda = mensaje["ronda"])
        elif mensaje['type'] == 'Seleccion_cancelada':
            self.client.mesa_juego.crear_botones_seleccionar_jugada(self.client.mesa_juego.mesa)
            self.client.mesa_juego.restaurar_comportamiento_mi_mano()
            self.client.mesa_juego.modificar_comportamiento_mi_mano()
        elif mensaje['type'] == 'jugada_invalida':
            self.client.mesa_juego.crear_botones_seleccionar_jugada(self.client.mesa_juego.mesa)
            self.client.mesa_juego.restaurar_comportamiento_mi_mano()
            self.client.mesa_juego.modificar_comportamiento_mi_mano()
        elif mensaje["type"] == "jugada_cancelada":
            print(mensaje)
            self.client.mesa_juego.elementos_mesa["datos_mano_jugador"] = mensaje.get("datos_mano_jugador")
            self.client.mesa_juego.elementos_mesa["jugada"] = mensaje.get("jugada")
            self.client.mesa_juego.elementos_mesa["jugadas_jugadores"] = mensaje.get("jugadas_jugadores")
            self.client.mesa_juego.cargar_datos_mano_jugador()
            self.client.mesa_juego.cargar_elemento_mi_mano()
            self.client.mesa_juego.actualizar_mano_visual(self.client.mesa_juego.mesa,accion="reorganizar_todo")
            self.client.mesa_juego.actualizar_jugadas(self.client.mesa_juego.mesa)
            self.client.mesa_juego.modificar_comportamiento_mi_mano()
            self.client.mesa_juego.crear_botones_seleccionar_jugada(self.client.mesa_juego.mesa)
            for boton in list(self.client.mesa_juego.botones_accion.values()):
                if boton in self.client.mesa_juego.mesa.botones:
                    boton.texto = "DESCARTAR"
                    self.client.mesa_juego.crear_botones_seleccionar_jugada(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "regresando_menu":
            print("Regresando al menú principal.")
            self.client.mesa_juego.crear_botones_jugar_descartar(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "mostrar_extender":
            self.client.mesa_juego.crear_botones_despues_de_bajarse(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "mensaje_seguidillas_continuas":
            print(mensaje)
            self.client.mesa_juego.crear_botones_seleccionar_jugada(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "No_Puede_Descartar_Misma_Carta":
            self.client.mesa_juego.alerta_carta_descartar_invalida(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "Error_Descartar":
            self.client.mesa_juego.alerta_carta_descartar_invalida(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "No_Puede_Descartar_Joker":
            self.client.mesa_juego.alerta_no_puede_descartar_joker(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "reemplazar_valido":
            print(mensaje)
            self.client.mesa_juego.elementos_mesa["datos_mano_jugador"] = mensaje.get("nueva_mano")
            self.client.mesa_juego.elementos_mesa["jugada"] = mensaje.get("jugada")
            self.client.mesa_juego.elementos_mesa["jugadas_jugadores"] = mensaje.get("jugadas_jugadores")
            self.client.mesa_juego.cargar_datos_mano_jugador()
            self.client.mesa_juego.cargar_elemento_mi_mano()
            self.client.mesa_juego.actualizar_mano_visual(self.client.mesa_juego.mesa,accion="reorganizar_todo")
            self.client.mesa_juego.actualizar_jugadas(self.client.mesa_juego.mesa)
            self.client.mesa_juego.restaurar_comportamiento_mi_mano()
        elif mensaje["type"] == "Ciert_jugador_compro_carta_del_descarte":
            self.client.mesa_juego.alerta_jugador_compro_carta_del_descarte(self.client.mesa_juego.mesa, mensaje["jugador_compro"])
        elif mensaje["type"] == "reemplazaron_tu_jugada":
            self.client.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
            self.client.mesa_juego.elementos_mesa["jugadas_jugadores"] = mensaje.get("jugadas_jugadores")
            self.client.mesa_juego.elementos_mesa["jugada"] = mensaje.get("jugada")
            self.client.mesa_juego.actualizar_jugadas(self.client.mesa_juego.mesa)
            self.client.mesa_juego.actualizar_manos_jugadores(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "extendieron_tu_jugada":
            self.client.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
            self.client.mesa_juego.elementos_mesa["jugadas_jugadores"] = mensaje.get("jugadas_jugadores")
            self.client.mesa_juego.elementos_mesa["jugada"] = mensaje.get("jugada")
            self.client.mesa_juego.actualizar_jugadas(self.client.mesa_juego.mesa)
            self.client.mesa_juego.actualizar_manos_jugadores(self.client.mesa_juego.mesa)
        elif mensaje["type"] == "Reconectar_partida":
            print(mensaje)
            if not self.client.mesa_juego:
                self.client.mesa_juego = mesa_interfaz.Mesa_interfaz(self.client.un_juego)
            self.client.mesa_juego.elementos_mesa["datos_mano_jugador"] = mensaje.get("mano")
            self.client.mesa_juego.elementos_mesa["jugada"] = mensaje.get("jugada")
            self.client.mesa_juego.elementos_mesa["jugadas_jugadores"] = mensaje.get("jugadas_jugadores")
            self.client.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores")
            self.client.mesa_juego.elementos_mesa["cantidad_cartas_mazo"] = mensaje.get("mazo")
            self.client.mesa_juego.elementos_mesa["dato_carta_quema"] = mensaje.get("dato_carta_quema")
            self.client.mesa_juego.elementos_mesa["dato_carta_descarte"] = mensaje.get("dato_carta_descarte")
            evento_py = pygame.event.Event(constantes.EVENTO_INICIAR_PARTIDA,un_juego=self.client.un_juego,mesa=self.client.mesa_juego,datos=mensaje)
            pygame.event.post(evento_py)
            time.sleep(5)
            if mensaje.get("jugadas_jugadores") or mensaje.get("jugada"):
                self.client.mesa_juego.actualizar_jugadas(self.client.mesa_juego.mesa)
        elif mensaje['type'] == 'PartidaReiniciada':
          print(f"[CLIENTE] Partida reiniciada: {mensaje.get('mensaje', '')}")
          if self.client.mesa_juego:
             self.client.mesa_juego.salir_partida()
          # Mostrar mensaje al usuario
             self.client.mesa_juego.mostrar_alerta(mensaje.get('mensaje', 'No hay suficientes jugadores.'))

        elif mensaje['type'] == 'SalaCerrada':
          print(f"[CLIENTE] Sala cerrada: {mensaje.get('mensaje', '')}")
          if self.client.mesa_juego:
            self.client.mesa_juego.salir_partida()
            self.client.mesa_juego.mostrar_alerta(mensaje.get('mensaje', 'El host cerró la sala.'))

        elif mensaje['type'] == 'ActualizacionEstadoPartida':
           print(f"[CLIENTE] Estado de partida actualizado. Jugadores activos: {mensaje.get('jugadores_activos')}")
           if self.client.mesa_juego:
           # Actualizar estructuras locales si es necesario
              self.client.mesa_juego.elementos_mesa["datos_lista_jugadores"] = mensaje.get("datos_lista_jugadores", [])
              self.client.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = mensaje.get("cantidad_manos_jugadores", [])
              self.client.mesa_juego.elementos_mesa["jugador_mano"] = mensaje.get("jugador_mano")
              self.client.mesa_juego.actualizar_manos_jugadores(self.client.mesa_juego.mesa)

