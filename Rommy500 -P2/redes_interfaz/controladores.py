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
        
        un_juego.lista_elementos = {
            "nombre_creador": nombre_creador_sala,
            "nombre_sala": nombre_sala,
            "cantidad_jugadores": max_jugadores,
            "ip_sala":"127.0.0.1",
            "lista_jugadores": [],
            "nombre_unirse": ""
        }
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

        # ── BOTÓN ORDENAR MANO (NUEVO) ────────────────────────────────────────
        # Se crea una sola vez, justo después de crear_mesa(), para que el
        # objeto Menu ya exista y se le pueda agregar el botón correctamente.
        try:
            clase_mesa_interfaz.crear_boton_ordenar(un_juego.mesa)
            print("DEBUG: Botón de ordenamiento de mano creado")
        except Exception as e:
            print(f"WARN: No se pudo crear el botón de ordenamiento: {e}")
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

    # Mostrar la sección de la mesa (ya sea nueva o actualizada)
    #==========Fin Jesua===========
    # Detener música de menú si la ventana tiene ese control
    try:
        if hasattr(un_juego, 'detener_musica'):
            un_juego.detener_musica()
    except Exception:
        pass

    Mostrar_seccion(un_juego, un_juego.mesa)
    # Reproducir música de partida al mostrar la mesa
    try:
        if hasattr(un_juego, 'reproducir_musica_partida'):
            un_juego.reproducir_musica_partida()
    except Exception:
        pass

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
    
"""Metodos para las actualizaciones en tiempo real"""
def modificacion_real_datos(un_juego, evento, constantes):
    global estado_espera_inicio
    
    if evento.type == constantes.EVENTO_NUEVO_JUGADOR:
        un_juego.lista_elementos["lista_jugadores"] = evento.nueva_lista
        print("Lista actualizada:", un_juego.lista_elementos["lista_jugadores"])
        un_juego.actualizar_mesa_espera()
    
    if evento.type == constantes.EVENTO_SALAS_ENCONTRADAS:
        un_juego.lista_elementos["salas_disponibles"] = evento.salas
    
    # Manejar evento de inicio de partida - versión no bloqueante
    if evento.type == constantes.EVENTO_INICIAR_PARTIDA:
        print("Evento para iniciar partida recibido")
        # Marcar que estamos esperando recursos
        estado_espera_inicio['esperando'] = True
        estado_espera_inicio['tiempo_inicio'] = pygame.time.get_ticks()
        estado_espera_inicio['evento_pendiente'] = evento
        estado_espera_inicio['ultimo_debug'] = None  # Resetear para empezar a contar desde el inicio
    
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
