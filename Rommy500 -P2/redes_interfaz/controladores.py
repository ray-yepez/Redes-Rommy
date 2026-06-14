import threading
import pygame
from redes_juego import client_main
from redes_juego import server_main
from redes_juego import conexion
conexion_Rummy = conexion.conexion_Rummy
"""Metodos de redes(interfaz-redes)"""

"""Agregar un jugador en lista de jugadores de redes, y actualizar la lista de usurios de la interfaz por esa nueva lista"""
server_rummy = None  # servidor, si se crea uno
cliente_rummy = None  # cliente, si se crea uno

# Estado para controlar la espera no bloqueante de recursos al iniciar partida
estado_espera_inicio = {
    'esperando': False,
    'tiempo_inicio': None,
    'timeout_ms': 2500,  # 2.5 segundos en milisegundos
    'evento_pendiente': None,
    'ultimo_debug': None  # Para controlar la frecuencia de mensajes de debug
}
def validar_campos_servidor(menu):
    """Valida todos los campos necesarios para crear un servidor"""
    campos_requeridos = {
        'nombre_creador': False,
        'nombre_sala': False
    }
    
    for boton in menu.botones:
        if hasattr(boton, 'valor') and hasattr(boton, 'texto_valido'):
            texto_boton = getattr(boton, 'texto', '').lower()
            
            if "nombre" in texto_boton and "sala" not in texto_boton and boton.texto_valido:
                campos_requeridos['nombre_creador'] = True
            elif "sala" in texto_boton and boton.texto_valido:
                campos_requeridos['nombre_sala'] = True
    
    return all(campos_requeridos.values())

def Crear_servidor(un_juego, menu):

    valor_nombre_creador = None
    valor_nombre_sala = None
    nombre_creador_sala = None
    nombre_sala = None
    max_jugadores = un_juego.lista_elementos.get("cantidad_jugadores")
    campos_validos = True

    campos_entrada = []
    for boton in menu.botones:
        if hasattr(boton, 'valor') and hasattr(boton, 'texto_valido'):
            campos_entrada.append(boton)

    # Asignar valores por posición
    if len(campos_entrada) >= 1:
        campo_nombre = campos_entrada[0]
        nombre_creador_sala = campo_nombre.valor.strip() if campo_nombre.valor else ""
        un_juego.lista_elementos["nombre_creador"] = nombre_creador_sala
        if not campo_nombre.texto_valido:
            campos_validos = False

    if len(campos_entrada) >= 2:
        campo_sala = campos_entrada[1]
        nombre_sala = campo_sala.valor.strip() if campo_sala.valor else ""
        un_juego.lista_elementos["nombre_sala"] = nombre_sala
        if not campo_sala.texto_valido:
            campos_validos = False

    # Validación
    if (campos_validos and 
        nombre_creador_sala and 
        nombre_sala and 
        max_jugadores > 0):
        
        un_juego.lista_elementos.update({
            "nombre_creador": nombre_creador_sala,
            "nombre_sala": nombre_sala,
            "cantidad_jugadores": max_jugadores,
            "ip_sala": "127.0.0.1",
            "lista_jugadores": [],
            "nombre_unirse": "",
            "salas_disponibles": un_juego.lista_elementos.get("salas_disponibles", []),
            "es_host": True,
            "origen_espera": "crear_sala"
        })
        print("holaaa")
        Agregar_jugador(un_juego)
        return True
    else:
        if not validar_campos_servidor(menu):
            print("Faltan campos requeridos o no son válidos")
            return False

    #A partir de aqui deberan crear la sala formalmente la sala puede utilizar sala_creada de la lista de elemento de ventana, los elementos del diccionario sala_creada son, sala_creada = {'nombre':'', 'ip':'','jugadores':0, 'max_jugadores': 0}, Como este metodo se llamara directamente despues de pedir los valores de creacion de la sala, pueden aplicar cualquier metodo para crear el servidor. la sala_creada es importante que tengan su variable interna donde tengan guardado esos datos del servidor.

def Crear_partida(un_juego):
    global server_rummy, cliente_rummy, conexion_salas
    nombre_creador_sala = un_juego.lista_elementos.get("nombre_creador")
    nombre_sala = un_juego.lista_elementos.get("nombre_sala")
    max_jugadores = un_juego.lista_elementos.get("cantidad_jugadores")
    server_rummy = conexion_Rummy()
    cliente_rummy = conexion_Rummy()
    hilo_server = threading.Thread(
        target=server_main.run_server,
        args=(server_rummy,cliente_rummy,max_jugadores,nombre_creador_sala,nombre_sala,un_juego)
    )
    hilo_server.daemon = True
    hilo_server.start()
    conexion_salas.buscador = False  # Detener la búsqueda de servidores al iniciar una partida

def Agregar_jugador(un_juego):
    """
    Agrega un jugador a la lista local del juego.
    """
    lista_elementos = un_juego.lista_elementos
    nombre_creador = lista_elementos["nombre_creador"]
    lista_jugadores = lista_elementos["lista_jugadores"]
    nombre_unirse = lista_elementos["nombre_unirse"]
    # Determinar qué nombre usar
    if lista_elementos:
        if nombre_creador and nombre_creador not in lista_jugadores:
            jugador = nombre_creador
            print(f"Agregando creador: {jugador}")
        elif nombre_unirse and nombre_unirse not in lista_jugadores:
            jugador = nombre_unirse
            print(f"Agregando jugador que se une: {jugador}")
        else:
            print("No se encontro nombre de jugador para agregar")
            return

    # Agregar jugador
    if jugador:
        lista_jugadores.append(jugador)
        print(f"Jugador agregado: {jugador}")
        print(f"Lista actual: {lista_jugadores}")
        
        # FORZAR ACTUALIZACIÓN INMEDIATA
        print("Forzando actualización de mesa de espera...")
        Notificar_cambio_jugadores(un_juego)
    else:
        print(f"Jugador ya existe o es inválido: {jugador}")

    #Actualizar las instancias de clase
    un_juego.lista_elementos = lista_elementos
    un_juego.lista_elementos["nombre_creador"] = nombre_creador
    un_juego.lista_elementos["lista_jugadores"] = lista_jugadores
    un_juego.lista_elementos["nombre_unirse"] = nombre_unirse
    
    # Notificar_cambio_jugadores(un_juego)  # Notifica los cambios y actualiza la mesa




"""Metodos netamete interfaz(uso de funciones de interfaz-redes)"""

"""Accion que se ejecuta al presionar un boton de la ventana"""
def Mostrar_seccion(un_juego, menu_destino,solo_ocultar=False):
    """
    Oculta todos los menús del juego y muestra solo el destino.
    """
    for elemento in un_juego.elementos_creados:
        elemento.ocultar()
    if solo_ocultar:
        return
    # Mostramos el que queremos
    menu_destino.mostrar()


"""Metodo que obtiene el valor de cantidad de jugadores, al darle confirmar en el menu_cantidad_jugadores en la interfaz"""
def Confirmar_cantidad_jugadores(un_juego,menu_destino,menu_ocultar):
    #Recorremos todos los botones del menu, y verificamos que el boton tenga el atributo "valor" y el "seleccionado" con hasattr, luego verificamos si efectivamente el boton esta seleccionado
    
    valor_seleccionado = None
    
    for boton in menu_ocultar.botones:
        if hasattr(boton, 'valor') and hasattr(boton, 'seleccionado'):
            if boton.seleccionado:
                un_juego.lista_elementos["cantidad_jugadores"] = boton.valor
                valor_seleccionado = boton.valor

    if valor_seleccionado != None:
        print("Cantidad de jugadores:",un_juego.lista_elementos["cantidad_jugadores"])
    else:
        print("No se ha seleccionado ninguna cantidad de jugadores")
        return
    Mostrar_seccion(un_juego,menu_destino)

"""Metodo que obtiene el valor de el nombre del creador de la sala y el nombre de su sala"""
def Valores_crear_sevidor(un_juego, menu):
    valor_nombre_creador = None
    valor_nombre_sala = None

    for boton in menu.botones:
        if hasattr(boton, "grupo") and boton.grupo:
            if len(boton.grupo) >= 1:
                un_juego.lista_elementos["nombre_creador"] = boton.grupo[0].valor
                valor_nombre_creador = boton.grupo[0].valor
            if len(boton.grupo) >= 2:
                un_juego.lista_elementos["nombre_sala"] = boton.grupo[1].valor
                valor_nombre_sala = boton.grupo[1].valor

    if valor_nombre_creador != "" and valor_nombre_sala != "":
        print("Creador:",un_juego.lista_elementos["nombre_creador"])
        print("Sala:",un_juego.lista_elementos["nombre_sala"])
    else:
        print("No se ha seleccionado un creador o un nombre de sala")
        return

"""Metodo que permite obtener el nombre del jugador a unirse, usado en el boton de menu_inicio (unirse sala)"""
def Nombre_jugador_unirse(un_juego,menu):
    for boton in menu.botones:
        if hasattr(boton,"grupo"):
            if len(boton.grupo) >= 1:
                un_juego.lista_elementos["nombre_unirse"] = boton.grupo[0].valor
    print("Buscando servidores disponibles... ")
    un_juego.actualizar_lista_salas()
def Notificar_cambio_jugadores(un_juego):
    """
    Llama a la actualización de la mesa de espera.
    """
    un_juego.actualizar_mesa_espera()

def Datos_unirse_sala(un_juego, menu):
    """Valida las entradas antes de unirse"""
    nombre_valido = True
    for boton in menu.botones:
        # Buscar elementos de entrada por sus atributos (sin importar clases)
        if hasattr(boton, 'valor') and hasattr(boton, 'texto_valido'):
            if not boton.texto_valido:
                nombre_valido = False
                print("Error: Nombre no válido")
                # Mostrar mensaje de error
                if hasattr(boton, 'mostrar_alerta'):
                    boton.mostrar_alerta("¡Nombre no válido! Recuerda no utilizar números o caracteres especiales.")  # Rojo para error
                break
            else:
                if hasattr(boton, 'obtener_texto_validado'):
                    un_juego.lista_elementos["nombre_unirse"] = boton.obtener_texto_validado()
                else:
                    un_juego.lista_elementos["nombre_unirse"] = boton.valor
    
    if nombre_valido:
        if hasattr(un_juego, 'cartel_alerta'):
            un_juego.cartel_alerta.ocultar()

        print("Uniendose al servidor... ")
        print(un_juego.lista_elementos.get("nombre_unirse"), "Te estas uniendo...")
        return True
    else:
        print("Por favor, corrige los errores en el formulario")
        return False
    
def Unirse_a_sala_seleccionada(un_juego, elemento_seleccion_sala):
    """Conecta a la sala seleccionada"""
    global conexion_salas

    if elemento_seleccion_sala:
        print(f"Conectando a {elemento_seleccion_sala['nombre']}...")
        print(f"IP: {elemento_seleccion_sala.get('ip', 'IP no disponible')}")
        print(f"Jugadores: {elemento_seleccion_sala['jugadores']}/{elemento_seleccion_sala['max_jugadores']}")
        print(f"Lista Jugadores: {elemento_seleccion_sala['lista_jugadores']}")
        print(f"Usuario: {un_juego.lista_elementos.get('nombre_unirse')}")
        
        # Guardar información de la sala seleccionada
        un_juego.lista_elementos["nombre_creador"] = elemento_seleccion_sala["creador"]
        un_juego.lista_elementos["nombre_sala"] = elemento_seleccion_sala["nombre"]
        un_juego.lista_elementos["cantidad_jugadores"] = elemento_seleccion_sala["max_jugadores"]
        un_juego.lista_elementos["ip_sala"] = elemento_seleccion_sala["ip"]
        un_juego.lista_elementos["lista_jugadores"] = elemento_seleccion_sala["lista_jugadores"]
        
        global cliente_rummy, hilo_cliente
        cliente_rummy = conexion_Rummy()
        nombre_jugador = un_juego.lista_elementos.get("nombre_unirse")
        ip_servidor = un_juego.lista_elementos.get("ip_sala")

        hilo_cliente = threading.Thread(
            target=client_main.run_client,
            args=(cliente_rummy,nombre_jugador,un_juego,ip_servidor))
        hilo_cliente.daemon = True
        hilo_cliente.start()
        # Detener música del menú principal (si existe) y reproducir música de sala de espera
        try:
            if hasattr(un_juego, 'detener_musica'):
                un_juego.detener_musica()
        except Exception:
            pass
        un_juego.lista_elementos["es_host"] = False
        un_juego.lista_elementos["origen_espera"] = "unirse_sala"
        Mostrar_seccion(un_juego, un_juego.menu_mesa_espera)
        try:
            if hasattr(un_juego, 'reproducir_musica_espera'):
                un_juego.reproducir_musica_espera()
        except Exception:
            pass
        conexion_salas.buscador = False  # Detener la búsqueda de servidores al iniciar una partida
        
        
    else:
        print("No se ha seleccionado ninguna sala")

"""Metodos meramente para el control de aparicion de menus"""
def mostrar_menu_nombre_usuario(un_juego, creador=False):
    if creador:
        if not hasattr(un_juego, "menu_nombre_creador"):
            un_juego.menu_nombre_creador = un_juego.Menu_nombre_usuario(True)
        Confirmar_cantidad_jugadores(un_juego,un_juego.menu_nombre_creador,un_juego.menu_Cantidad_Jugadores)
    else:
        if not hasattr(un_juego, "menu_nombre_usuario"):
            un_juego.menu_nombre_usuario = un_juego.Menu_nombre_usuario(False)
        Mostrar_seccion(un_juego, un_juego.menu_nombre_usuario)

def mostrar_menu_mesa_espera(un_juego):
    if hasattr(un_juego, "menu_nombre_creador"):
        Valores_crear_sevidor(un_juego, un_juego.menu_nombre_creador)

    if Crear_servidor(un_juego, un_juego.menu_nombre_creador):
        un_juego.lista_elementos["es_host"] = True
        un_juego.lista_elementos["origen_espera"] = "crear_sala"
    # (re)crear el menú ahora que lista_elementos ya está actualizada
        un_juego.menu_mesa_espera = un_juego.Menu_mesa_espera()
        # Detener música del menú principal si está sonando
        try:
            if hasattr(un_juego, 'detener_musica'):
                un_juego.detener_musica()
        except Exception:
            pass
        Mostrar_seccion(un_juego, un_juego.menu_mesa_espera)
        # Reproducir música de sala de espera
        try:
            if hasattr(un_juego, 'reproducir_musica_espera'):
                un_juego.reproducir_musica_espera()
        except Exception:
            pass

def mostrar_menu_seleccion_sala(un_juego):
    """Muestra el menú de selección de sala"""
    # Crear el menú si no existe
    if not hasattr(un_juego, "menu_seleccion_sala"):
        un_juego.menu_seleccion_sala = un_juego.Menu_seleccion_sala()

    # Mostrar el menú y guardar el nombre del jugador
    Nombre_jugador_unirse(un_juego,un_juego.menu_nombre_usuario)
    Mostrar_seccion(un_juego, un_juego.menu_seleccion_sala)

def mostrar_mesa(un_juego,clase_mesa_interfaz,datos):
    global cliente_rummy
    """Muestra la mesa"""
    print(datos)
    clase_mesa_interfaz.elementos_mesa["id_jugador"] = datos.get("id_jugador")
    clase_mesa_interfaz.elementos_mesa["jugador_mano"] = datos.get("jugador_mano")
    clase_mesa_interfaz.elementos_mesa["cantidad_cartas_mazo"] = datos.get("mazo")
    clase_mesa_interfaz.elementos_mesa["cantidad_manos_jugadores"] = datos.get("cantidad_manos_jugadores")
    clase_mesa_interfaz.elementos_mesa["datos_mano_jugador"] = datos.get("mano")
    clase_mesa_interfaz.elementos_mesa["datos_lista_jugadores"] = datos.get("datos_lista_jugadores")
    clase_mesa_interfaz.elementos_mesa["dato_carta_descarte"] = datos.get("dato_carta_descarte")
    clase_mesa_interfaz.instacia_conexion = cliente_rummy

    # Crear el menú si no existe
    #==========Inicio Jesua===========
    

    # Si no existe la mesa, crearla; si ya existe, reconfigurarla para reflejar los nuevos datos
    if not hasattr(un_juego, "mesa") or not un_juego.mesa_juego:
        un_juego.mesa_juego = clase_mesa_interfaz
        mesa = clase_mesa_interfaz
        un_juego.mesa = mesa.crear_mesa()
        print("DEBUG: Mesa creada por primera vez")

        # ── BOTÓN ORDENAR MANO ────────────────────────────────────────────────
        try:
            clase_mesa_interfaz.crear_boton_ordenar(un_juego.mesa)
            print("DEBUG: Botón de ordenamiento de mano creado")
        except Exception as e:
            print(f"WARN: No se pudo crear el botón de ordenamiento: {e}")
        # ─────────────────────────────────────────────────────────────────────

        # ── BOTÓN CONCLUIR RONDA (Cheat/Admin) ───────────────────────────────
        # Solo se crea si el cliente es el Host (id_jugador == 1).
        # crear_boton_concluir_ronda() evalúa internamente si es host; si no
        # lo es, simplemente no hace nada → ningún riesgo en llamarlo siempre.
        try:
            clase_mesa_interfaz.crear_boton_concluir_ronda(un_juego.mesa)
            print("DEBUG: Botón 'Concluir Ronda' procesado (host check interno).")
        except Exception as e:
            print(f"WARN: No se pudo crear el botón 'Concluir Ronda': {e}")
        # ─────────────────────────────────────────────────────────────────────

    else:
        un_juego.mesa_juego = clase_mesa_interfaz
        # Hay una mesa existente: actualizar sus elementos usando manejar_partida
        try:
            print("DEBUG: Mesa existente - limpiando visual y reconstruyendo mesa")
            # Preservar puntuaciones acumuladas de los jugadores antes de reiniciar la mesa
            puntuaciones_previas = {}
            try:
                # un_juego.mesa_juego es la instancia actual mostrada en pantalla
                mesa_actual = un_juego.mesa_juego if hasattr(un_juego, 'mesa_juego') else clase_mesa_interfaz
                for jugador in getattr(mesa_actual, 'lista_jugadores_objetos', []):
                    try:
                        puntuaciones_previas[jugador.nro_jugador] = getattr(jugador, 'puntos_acumulados', 0)
                    except Exception:
                        continue
            except Exception:
                puntuaciones_previas = {}

            # Limpiar visual actual para evitar solapamientos y referencias obsoletas
            try:
                clase_mesa_interfaz.reiniciar_visual_mesa(un_juego.mesa)
            except Exception as e:
                print(f"WARN: reiniciar_visual_mesa falló: {e}")

            # Reconstruir el contenido de la mesa actual
            clase_mesa_interfaz.manejar_partida(un_juego.mesa)

            # Reaplicar las puntuaciones previas a los nuevos objetos Jugador creados
            try:
                for jugador in getattr(clase_mesa_interfaz, 'lista_jugadores_objetos', []):
                    puntos_prev = puntuaciones_previas.get(jugador.nro_jugador)
                    if puntos_prev is not None:
                        try:
                            setattr(jugador, 'puntos_acumulados', puntos_prev)
                        except Exception:
                            pass
                # Actualizar la tabla/contador visual si existe
                try:
                    if hasattr(clase_mesa_interfaz, 'referencia_elementos') and clase_mesa_interfaz.referencia_elementos.get('contador_puntos'):
                        contador = clase_mesa_interfaz.referencia_elementos.get('contador_puntos')
                        # Si el contador corresponde al jugador local, refrescar el texto
                        try:
                            if clase_mesa_interfaz.elementos_mesa.get('id_jugador'):
                                id_local = clase_mesa_interfaz.elementos_mesa.get('id_jugador')
                                # Buscar jugador local y actualizar puntos de ronda acumulados mostrados
                                for j in clase_mesa_interfaz.lista_jugadores_objetos:
                                    if getattr(j, 'nro_jugador', None) == id_local:
                                        # Preferir mostrar los puntos acumulados (como en la tabla de puntuación)
                                        try:
                                            puntos_local = getattr(j, 'puntos_acumulados', getattr(j, 'puntos_ronda_actual', 0))
                                            contador.texto = f"Tus Puntos: {puntos_local}"
                                            contador.prepar_texto()
                                        except Exception:
                                            pass
                                        break
                        except Exception:
                            pass
                except Exception:
                    pass
            except Exception:
                pass
        except Exception as e:
            print(f"ERROR actualizando mesa existente: {e}")

        # ── BOTÓN ORDENAR MANO (nueva ronda) ─────────────────────────────────
        try:
            clase_mesa_interfaz.crear_boton_ordenar(un_juego.mesa)
            print("DEBUG: Botón de ordenamiento de mano recreado para nueva ronda")
        except Exception as e:
            print(f"WARN: No se pudo recrear el botón de ordenamiento: {e}")

        # ── BOTÓN CONCLUIR RONDA (nueva ronda, solo Host) ────────────────────
        # Se recrea porque manejar_partida() limpia y reconstruye los botones
        # de la mesa, eliminando el botón anterior.
        try:
            clase_mesa_interfaz.crear_boton_concluir_ronda(un_juego.mesa)
            print("DEBUG: Botón 'Concluir Ronda' re-procesado para nueva ronda.")
        except Exception as e:
            print(f"WARN: No se pudo recrear el botón 'Concluir Ronda': {e}")
        # ─────────────────────────────────────────────────────────────────────

    # Mostrar la sección de la mesa (ya sea nueva o actualizada)
    #==========Fin Jesua===========
    # Detener música de menú si la ventana tiene ese control
    try:
        if hasattr(un_juego, 'detener_musica'):
            un_juego.detener_musica()
    except Exception:
        pass
# Mostrar la sección de la mesa
    try:
        clase_mesa_interfaz.determinar_turno()

        if clase_mesa_interfaz.tu_turno:
            print("ACTIVANDO MANO - es mi turno")
            clase_mesa_interfaz.actualizar_estado_mano("activar_mano")
        else:
            print("DESACTIVANDO MANO - no es mi turno")
            clase_mesa_interfaz.actualizar_estado_mano("desactivar_mano")

    except Exception as e:
        print(f"Error actualizando estado de mano por turno: {e}")

    Mostrar_seccion(un_juego, un_juego.mesa)
    # Reproducir música de partida al mostrar la mesa
    try:
        if hasattr(un_juego, 'reproducir_musica_partida'):
            un_juego.reproducir_musica_partida()
    except Exception:
        pass

#cambio lismar, cambio redes que paso maria valeria
"""Metodos para las actualizaciones en tiempo real"""

# Lista de carteles de notificación activos para apilarlos verticalmente
_notificaciones_activas = []
_lock_notificaciones = threading.Lock()

def _mostrar_notificacion_jugador(un_juego, nombre, accion):
    """Muestra un cartel temporal cuando un jugador se une o desconecta de la sala."""
    import threading
    try:
        from recursos_graficos.elementos_de_interfaz_de_usuario import CartelAlerta
        from recursos_graficos import constantes as _const

        nombre_mostrar = nombre if nombre else "Jugador"
        if accion == "unio":
            mensaje = f"{nombre_mostrar} se unió a la sala"
        else:
            mensaje = f"{nombre_mostrar} se desconectó"

        # Determinar en qué superficie mostrar el cartel
        # Prioridad: mesa de juego activa > sala de espera
        pantalla = un_juego.pantalla
        ancho_cartel = 600
        alto_cartel = 110
        margen = 10
        x = (_const.ANCHO_VENTANA - ancho_cartel) // 2
        y_base = int(_const.ALTO_VENTANA * 0.08)
       
        with _lock_notificaciones:
            slot = len(_notificaciones_activas)
            y = y_base + slot * (alto_cartel + margen)

        cartel = CartelAlerta(
            pantalla=pantalla,
            mensaje=mensaje,
            x=x,
            y=y,
            ancho=ancho_cartel,
            alto=alto_cartel,
            mostrar_boton_cerrar=False,
            duracion_ms=5000
        )

        # Añadir el cartel al menú activo para que se dibuje
        menu_activo = None
        # Preferir la mesa de juego si está activa
        if hasattr(un_juego, 'mesa') and un_juego.mesa and getattr(un_juego.mesa, 'visible', False):
            menu_activo = un_juego.mesa
        elif hasattr(un_juego, 'menu_mesa_espera') and un_juego.menu_mesa_espera and getattr(un_juego.menu_mesa_espera, 'visible', False):
            menu_activo = un_juego.menu_mesa_espera

        if menu_activo is not None:
            if not hasattr(menu_activo, 'overlays'):
                menu_activo.overlays = []
            menu_activo.overlays.append(cartel)
            cartel.mostrar()
            # Ocultar y limpiar automáticamente tras la duración
            def _quitar():
                try:
                    cartel.ocultar()
                    if cartel in menu_activo.overlays:
                        menu_activo.overlays.remove(cartel)
                    with _lock_notificaciones:
                        if cartel in _notificaciones_activas:
                            _notificaciones_activas.remove(cartel)
                        for i, c in enumerate(_notificaciones_activas):
                            c.rect.y = y_base + i * (alto_cartel + margen)
                except Exception:
                    pass
            threading.Timer(5.2, _quitar).start()
        else:
            print(f"[Notificación] {mensaje}")
    except Exception as e:
        print(f"Error mostrando notificación de jugador: {e}")

"""Metodos meramente para las validaciones"""
def validar_y_unirse_sala(un_juego, menu):
    resultado = Datos_unirse_sala(un_juego, menu)
    if resultado == False:
        print("Los datos ingresados no son validos")
    elif resultado == True:
        mostrar_menu_seleccion_sala(un_juego)

def validar_y_crear_servidor(un_juego, menu):
    """Valida y procede a crear servidor"""
    if Crear_servidor(un_juego, menu):
    # Solo crear servidor si la validación fue exitosa
        Crear_partida(un_juego)
        mostrar_menu_mesa_espera(un_juego)




def Salir():
    global cliente_rummy, server_rummy
    if cliente_rummy is not None:
        cliente_rummy.desconectar()
    if server_rummy is not None:
        server_rummy.desconectar()
    else:
        print("No hay cliente o servidor para desconectar.")

def Buscar_salas(un_juego,):
    global hilo_busqueda,conexion_salas
    conexion_salas = conexion_Rummy()
    hilo_busqueda = threading.Thread(
        target=conexion_salas.encontrar_ip_servidor,
        args=(un_juego,))
    hilo_busqueda.daemon = True
    hilo_busqueda.start()
    print(conexion_salas.conexiones_disponibles)
    
def _mostrar_notificacion_jugador(un_juego, nombre, accion):
    """Muestra un cartel temporal cuando un jugador se une o desconecta de la sala."""
    import threading
    try:
        from recursos_graficos.elementos_de_interfaz_de_usuario import CartelAlerta
        from recursos_graficos import constantes as _const

        nombre_mostrar = nombre if nombre else "Jugador"
        if accion == "unio":
            mensaje = f"{nombre_mostrar} se unió a la sala"
        else:
            mensaje = f"{nombre_mostrar} se desconectó"

        # Determinar en qué superficie mostrar el cartel
        # Prioridad: mesa de juego activa > sala de espera
        pantalla = un_juego.pantalla
        ancho_cartel = 600
        alto_cartel = 110
        x = (_const.ANCHO_VENTANA - ancho_cartel) // 2
        y = int(_const.ALTO_VENTANA * 0.08)

        cartel = CartelAlerta(
            pantalla=pantalla,
            mensaje=mensaje,
            x=x,
            y=y,
            ancho=ancho_cartel,
            alto=alto_cartel,
            mostrar_boton_cerrar=False,
            duracion_ms=3000
        )

        # Añadir el cartel al menú activo para que se dibuje
        menu_activo = None
        # Preferir la mesa de juego si está activa
        if hasattr(un_juego, 'mesa') and un_juego.mesa and getattr(un_juego.mesa, 'visible', False):
            menu_activo = un_juego.mesa
        elif hasattr(un_juego, 'menu_mesa_espera') and un_juego.menu_mesa_espera and getattr(un_juego.menu_mesa_espera, 'visible', False):
            menu_activo = un_juego.menu_mesa_espera

        if menu_activo is not None:
            if not hasattr(menu_activo, 'overlays'):
                menu_activo.overlays = []
            menu_activo.overlays.append(cartel)
            cartel.mostrar()
            # Ocultar y limpiar automáticamente tras la duración
            def _quitar():
                try:
                    cartel.ocultar()
                    if cartel in menu_activo.overlays:
                        menu_activo.overlays.remove(cartel)
                except Exception:
                    pass
            threading.Timer(15.1, _quitar).start()
        else:
            print(f"[Notificación] {mensaje}")
    except Exception as e:
        print(f"Error mostrando notificación de jugador: {e}")

"""Metodos para las actualizaciones en tiempo real"""
def modificacion_real_datos(un_juego, evento, constantes):
    global estado_espera_inicio
    
    if evento.type == constantes.EVENTO_NUEVO_JUGADOR:
        un_juego.lista_elementos["lista_jugadores"] = evento.nueva_lista
        print("Lista actualizada:", un_juego.lista_elementos["lista_jugadores"])
        un_juego.actualizar_mesa_espera()
    
    if evento.type == constantes.EVENTO_SALAS_ENCONTRADAS:
        un_juego.lista_elementos["salas_disponibles"] = evento.salas
    # Si estamos en el menú de selección de sala, reconstruirlo con la lista nueva
        try:
            if hasattr(un_juego, "menu_seleccion_sala") and un_juego.menu_seleccion_sala.visible:
                if un_juego.menu_seleccion_sala in un_juego.elementos_creados:
                    un_juego.elementos_creados.remove(un_juego.menu_seleccion_sala)

                un_juego.menu_seleccion_sala = un_juego.Menu_seleccion_sala()
                Mostrar_seccion(un_juego, un_juego.menu_seleccion_sala)

                print("Menú de salas actualizado con salas nuevas")
        except Exception as e:
            print(f"No se pudo refrescar menú de salas: {e}")

    if evento.type == constantes.EVENTO_NOTIFICACION_JUGADOR:
        _mostrar_notificacion_jugador(un_juego, evento.nombre, evento.accion)
    
    # Manejar evento de inicio de partida - versión no bloqueante
    if evento.type == constantes.EVENTO_INICIAR_PARTIDA:
        print("Evento para iniciar partida recibido")
        # Marcar que estamos esperando recursos
        estado_espera_inicio['esperando'] = True
        estado_espera_inicio['tiempo_inicio'] = pygame.time.get_ticks()
        estado_espera_inicio['evento_pendiente'] = evento
        estado_espera_inicio['ultimo_debug'] = None  # Resetear para empezar a contar desde el inicio

    # ── Evento Cheat/Admin: concluir ronda inmediatamente ─────────────────────
    # Este evento puede llegar de dos fuentes:
    #   a) Disparado localmente por CheatAdminMixin._aplicar_mano_cheat_local()
    #      cuando no hay servidor activo (modo prueba).
    #   b) Disparado por el procesador de mensajes de red cuando el servidor
    #      reenvía la notificación "concluir_ronda" a todos los clientes.
    #
    # El evento debe tener los atributos:
    #   evento.ronda        → número de ronda concluida
    #   evento.cartas_cheat → lista de dicts {"numero":..,"figura":..}
    #   evento.id_jugador   → id del jugador host que concluyó la ronda
    if evento.type == constantes.EVENTO_CONCLUIR_RONDA:
        _manejar_evento_concluir_ronda(un_juego, evento)
    # ─────────────────────────────────────────────────────────────────────────
def verificar_espera_inicio_partida(un_juego):
    global estado_espera_inicio
    # Verificar en cada frame si debemos mostrar la mesa (no bloqueante)
    if estado_espera_inicio['esperando']:
        tiempo_actual = pygame.time.get_ticks()
        tiempo_transcurrido = tiempo_actual - estado_espera_inicio['tiempo_inicio']
        
        # Verificar si los recursos están listos
        img_c = un_juego._cartas_imagenes
        img_m = un_juego._mazo_imagenes
        
        try:
            texto_espera = un_juego.menu_mesa_espera.elemento_texto_espera.texto
        except Exception:
            texto_espera = ''
        
        recursos_listos = (
            len(texto_espera) != 0 and 
            img_c and img_m and 
            len(img_c) == 54 and 
            len(img_m) == 5
        )
        
        # Debug cada 500ms para no saturar la consola
        if estado_espera_inicio['ultimo_debug'] is None or (tiempo_actual - estado_espera_inicio['ultimo_debug']) >= 500:
            print(f"DEBUG: espera inicio partida - tiempo={tiempo_transcurrido}ms, texto_espera_len={len(texto_espera)}, img_c={len(img_c) if img_c else 0}, img_m={len(img_m) if img_m else 0}")
            estado_espera_inicio['ultimo_debug'] = tiempo_actual
        
        # Verificar timeout o recursos listos
        if recursos_listos or tiempo_transcurrido >= estado_espera_inicio['timeout_ms']:
            evento = estado_espera_inicio['evento_pendiente']
            if recursos_listos:
                print("DEBUG: Recursos cargados, mostrando mesa")
            else:
                print(f"WARN: Timeout esperando recursos ({tiempo_transcurrido}ms). Forzando mostrar_mesa")
            
            mostrar_mesa(evento.un_juego, clase_mesa_interfaz=evento.mesa, datos=evento.datos)
            
            # Resetear estado
            estado_espera_inicio['esperando'] = False
            estado_espera_inicio['tiempo_inicio'] = None
            estado_espera_inicio['evento_pendiente'] = None
            estado_espera_inicio['ultimo_debug'] = None
            print("Mesa mostrada")

##metodo de desconexion para el host y jugadores, este metodo se llama al darle salir a la mesa de espera, si es el host se desconecta el cliente y el servidor, si es un jugador que se unio solo se desconecta el cliente, luego se regresa al menu de inicio o al menu de seleccion de sala dependiendo del origen del jugador (si era un jugador que se unio o el host)

def regresar_desde_mesa_espera(un_juego):
    global cliente_rummy, server_rummy, conexion_salas

    es_host = un_juego.lista_elementos.get("es_host", False)
    origen = un_juego.lista_elementos.get("origen_espera", "")

    if es_host:
        print("El host salió. Cerrando servidor...")

        try:
            if cliente_rummy is not None:
                cliente_rummy.activo = False

                if hasattr(cliente_rummy, "buscador"):
                    cliente_rummy.buscador = False

                cliente_rummy.desconectar()
                cliente_rummy = None

        except Exception as e:
            print(f"Error desconectando cliente host: {e}")

        try:
            if server_rummy is not None:
                server_rummy.activo = False

                if hasattr(server_rummy, "buscador"):
                    server_rummy.buscador = False

                server_rummy.desconectar()
                server_rummy = None

        except Exception as e:
            print(f"Error cerrando servidor: {e}")

        try:
            un_juego.lista_elementos["salas_disponibles"] = []
            un_juego.lista_elementos["lista_jugadores"] = []
            un_juego.lista_elementos["nombre_sala"] = ""
            un_juego.lista_elementos["nombre_creador"] = ""
            un_juego.lista_elementos["es_host"] = False
            un_juego.lista_elementos["origen_espera"] = ""

        except Exception as e:
            print(f"Error limpiando datos de sala local: {e}")

        try:
            conexion_salas.buscador = True
        except Exception:
            pass

        Mostrar_seccion(un_juego, un_juego.menu_Cantidad_Jugadores)

    else:
        print("Jugador externo salió de la sala de espera.")

        try:
            if cliente_rummy is not None:
                cliente_rummy.activo = False

                if hasattr(cliente_rummy, "buscador"):
                    cliente_rummy.buscador = False

                cliente_rummy.desconectar()
                cliente_rummy = None

        except Exception as e:
            print(f"Error desconectando jugador: {e}")

        try:
            conexion_salas.buscador = True
        except Exception:
            pass

        if origen == "unirse_sala":
            Mostrar_seccion(un_juego, un_juego.menu_nombre_usuario)
        else:
            Mostrar_seccion(un_juego, un_juego.menu_seleccion_sala)

    try:
        if hasattr(un_juego, "detener_musica"):
            un_juego.detener_musica()

        if hasattr(un_juego, "reproducir_musica_menu"):
            un_juego.reproducir_musica_menu()

    except Exception as e:
        print(f"Error cambiando música al regresar: {e}")
# =============================================================================
# ── HANDLER: EVENTO_CONCLUIR_RONDA ───────────────────────────────────────────
# =============================================================================

def _manejar_evento_concluir_ronda(un_juego, evento):
    """
    Procesa EVENTO_CONCLUIR_RONDA en el hilo principal de Pygame.

    Flujo:
      1. Extrae los datos del evento (ronda, cartas_cheat, id_jugador).
      2. Actualiza elementos_mesa["datos_mano_jugador"] con las cartas cheat
         solo para el jugador local cuyo id coincida con evento.id_jugador.
      3. Fuerza una reconstrucción visual de la mesa (llama a manejar_partida
         si existe, o recrea la mesa si es necesario).
      4. Muestra un cartel informativo al jugador local.

    NOTA: El servidor ya habrá aplicado el cambio en su estado interno y
    notificado a los demás clientes a través del mensaje de red.  Este handler
    solo actualiza la capa visual del cliente que recibe el evento.
    """
    try:
        ronda        = getattr(evento, "ronda",        None)
        cartas_cheat = getattr(evento, "cartas_cheat", [])
        id_host      = getattr(evento, "id_jugador",   1)

        print(f"[ConcluirRonda] Evento recibido — ronda={ronda}, "
              f"id_host={id_host}, cartas={cartas_cheat}")

        # ── 1. Necesitamos una mesa activa ────────────────────────────────────
        if not hasattr(un_juego, "mesa_juego") or not un_juego.mesa_juego:
            print("[ConcluirRonda] No hay mesa_juego activa; ignorando evento.")
            return

        mesa_interfaz_obj = un_juego.mesa_juego
        id_local = mesa_interfaz_obj.elementos_mesa.get("id_jugador")

        # ── 2. Actualizar mano del jugador local si es el host ────────────────
        # Si este cliente ES el host (id_local == id_host), actualizamos su
        # mano visual con las cartas cheat.
        if id_local is not None and int(id_local) == int(id_host):
            mesa_interfaz_obj.elementos_mesa["datos_mano_jugador"] = cartas_cheat
            print(f"[ConcluirRonda] Mano del Host actualizada con {len(cartas_cheat)} cartas cheat.")
        else:
            # Los demás clientes solo reciben el aviso visual; sus manos no cambian.
            print(f"[ConcluirRonda] Cliente {id_local} ≠ host {id_host}; "
                  "mano local sin cambios.")

        # ── 3. Actualizar número de ronda en la instancia mesa_interfaz ───────
        if ronda is not None:
            try:
                mesa_interfaz_obj._ronda_actual = int(ronda)
            except Exception:
                pass

        # ── 4. Forzar reconstrucción visual ───────────────────────────────────
        try:
            if hasattr(mesa_interfaz_obj, "manejar_partida") and un_juego.mesa:
                mesa_interfaz_obj.manejar_partida(un_juego.mesa)
                print("[ConcluirRonda] manejar_partida() ejecutado.")
        except Exception as e:
            print(f"[ConcluirRonda] Error en manejar_partida: {e}")

        # ── 5. Mostrar cartel informativo ──────────────────────────────────────
        try:
            if hasattr(un_juego, "cartel_alerta"):
                if id_local is not None and int(id_local) == int(id_host):
                    mensaje = (
                        f"[HOST] Ronda {ronda} concluida.\n"
                        "Tu mano fue reemplazada con las cartas cheat.\n"
                        "¡Baja tus cartas para ganar!"
                    )
                else:
                    mensaje = (
                        f"El Host ha concluido la ronda {ronda}.\n"
                        "Espera el resultado..."
                    )
                un_juego.cartel_alerta.mostrar(mensaje)
        except Exception as e:
            print(f"[ConcluirRonda] Error mostrando cartel: {e}")

    except Exception as e:
        print(f"[ConcluirRonda] Error general en handler: {e}")