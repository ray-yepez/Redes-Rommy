from random import choice
from logica_juego.jugador import Jugador
from logica_juego.cartas import Cartas
from logica_juego.mazo import Mazo
from logica_juego.jugadas import Jugada

class Mesa:
    lista_jugadores = []
    descarte = []
    quema = []
    cartas_mesa = []
    jugadores_primera_jugada = []
    

    def __init__(self):
        pass

    @classmethod
    def normalizar(cls, texto):
        return texto.strip().lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')

    @classmethod
    def cuantos_jugadores(cls):
        while True:
            entrada = input('¿Cuántos jugadores van a jugar?: ')
            try:
                num_jugadores = int(entrada)
                if num_jugadores < 2:
                    print('Para jugar necesitas más de un jugador.')
                elif num_jugadores > 7:
                    print("Solo se puede jugar con un máximo de 7 jugadores.")
                else:
                    for x in range(num_jugadores):
                        nombre = input('Ingrese el nombre del jugador: ')
                        jugador = Jugador(x + 1, nombre)
                        cls.lista_jugadores.append(jugador)
                        print('Jugador añadido.')
                    return True
            except ValueError:
                print("Por favor ingrese un número válido.")



    @classmethod
    def mostrar_manos(cls, jugadores_reordenados, manos):
        for i, mano in enumerate(manos):
            jugador = jugadores_reordenados[i]
            print(f'\nCartas del jugador {jugador.nro_jugador} - {jugador.nombre_jugador}:')
            for carta in mano:
                print(carta)

    @classmethod
    def jugador_mano_orden(cls):
        #Elige aleatoriamente el índice y el objeto del jugador que será el jugador mano
        indice_del_jugador_mano, nom_jug_mano = choice(list(enumerate(cls.lista_jugadores)))
        print(f"El jugador mano es: {nom_jug_mano.nombre_jugador}")

        # Se crea la lista de jugadores reordenada usando slicing (rebanado). Esto toma la parte de la lista desde el jugador mano hasta el final, y le concatena la parte desde el inicio de la lista hasta el jugador mano.
        jugadores_reordenados = (cls.lista_jugadores[indice_del_jugador_mano:] + 
                                 cls.lista_jugadores[:indice_del_jugador_mano])

        # Se inicializa una lista vacía de jugadas para cada jugador en la mesa
        for _ in range(len(jugadores_reordenados)):
            cls.cartas_mesa.append([])

        return jugadores_reordenados
    
    #NUEVA FUNCION: Revisa si el mazo está vacío y baraja la quema si es necesario.
    @classmethod
    def _revisar_y_barajar_quema(cls, mazo):
        #Revisa si el mazo está vacío. Si lo está, baraja las cartas de la quema y las usa como nuevo mazo.
        if not mazo.cartas and cls.quema:
            print("\n¡El mazo se ha agotado! Barajando las cartas quemadas para crear un nuevo mazo...")
            mazo.cartas.extend(cls.quema)
            cls.quema.clear()
            mazo.revolver_mazo()
            print("Nuevo mazo creado y barajado.")
            
    @classmethod
    def compra(cls, jugador_actual, jugadores, manos, mazo):
        if not cls.descarte:
            print("No hay carta en el descarte para ofrecer.")
            return

        carta_descarte = cls.descarte[-1]
        print(f"\nSe ofrece la carta del descarte: {carta_descarte}")
        carta_comprada = False

        cantidad_jugadores = len(jugadores)
        intentos = 0
        idx = (jugador_actual + 1) % cantidad_jugadores

        while intentos < cantidad_jugadores - 1:
            jugador_siguiente = jugadores[idx]
            respuesta = input(f'{jugador_siguiente.nombre_jugador}, ¿quieres comprar la carta del descarte ({carta_descarte})? (si/no): ')

            if cls.normalizar(respuesta) == 'si':
                
                # ANTES DE ROBAR LA CARTA EXTRA, REVISAMOS EL MAZO
                cls._revisar_y_barajar_quema(mazo)
                
                if mazo.cartas:
                    carta_extra = mazo.cartas.pop(-1)
                    manos[idx].append(carta_descarte)
                    manos[idx].append(carta_extra)
                    cls.descarte.pop(-1)
                    print(f"{jugador_siguiente.nombre_jugador} ha comprado la carta del descarte y robado una carta extra.")
                    carta_comprada = True
                else:
                    print("No hay cartas en el mazo para completar la compra.")
                break

            # Avanzar al siguiente jugador
            idx = (idx + 1) % cantidad_jugadores
            intentos += 1

        if not carta_comprada:
            carta_quemada = cls.descarte.pop(-1)
            cls.quema.append(carta_quemada)
            print(f"Nadie compró la carta. Se ha quemado: {carta_quemada}")

    #nuevo metodo
    @classmethod
    def mostrar_cartas_mesa(cls):
        print("\n--- Cartas en la mesa ---")
        for i, jugadas_jugador in enumerate(cls.cartas_mesa):
            if not jugadas_jugador:
                print(f"Jugador {i + 1}: [Aún no ha bajado jugada]")
            else:
                print(f"Jugador {i + 1}:")
                for jugada in jugadas_jugador:
                    cartas_legibles = [str(carta) for carta in jugada]
                    print(f"  - {' - '.join(cartas_legibles)}")

    @classmethod
    def descartar_carta(cls, jugador_actual, jugadores, manos):
        jugador = jugadores[jugador_actual]
        mano_actual = manos[jugador_actual]
        print(f"\n{jugador.nombre_jugador}, debes descartar una carta.")
        print("Tus cartas actuales:")

        # Mostrar la mano numerada
        for idx, carta in enumerate(mano_actual, 1):
            print(f"{idx}. {carta}")

        while True:
            try:
                indice = int(input("Ingresa el número de la carta que quieres descartar: "))
                if 1 <= indice <= len(mano_actual):
                    carta_a_descartar = mano_actual.pop(indice - 1)
                    
                    # quemar el mono
                    if carta_a_descartar.numero.lower() == 'joker':
                        print(f"¡Has descartado un Joker! Debes descartar otra carta.")
                        cls.quema.append(carta_a_descartar)

                        # Verificar si al jugador le quedan cartas
                        if not mano_actual:
                            print("No te quedan más cartas para descartar.")
                            break 

                        print("\nAhora, elige la segunda carta para descartar:")
                        # Mostrar la mano restante
                        for idx, carta in enumerate(mano_actual, 1):
                            print(f"{idx}. {carta}")

                        # Bucle para el segundo descarte obligatorio
                        while True:
                            try:
                                indice_extra = int(input("Ingresa el número de la carta extra a descartar: "))
                                if 1 <= indice_extra <= len(mano_actual):
                                    carta_extra = mano_actual.pop(indice_extra - 1)
                                    cls.descarte.append(carta_extra)
                                    print(f"Has descartado: {carta_extra}")
                                    break 
                                else:
                                    print("Número fuera de rango. Intenta de nuevo.")
                            except ValueError:
                                print("Entrada inválida. Ingresa un número.")
                    else:
                        # Si no es un Joker, se descarta normalmente
                        cls.descarte.append(carta_a_descartar)
                        print(f"Has descartado: {carta_a_descartar}")
                    break 
                else:
                    print("Número fuera de rango. Intenta de nuevo.")
            except ValueError:
                print("Entrada inválida. Ingresa un número.")

        manos[jugador_actual] = mano_actual


    @classmethod
    def obtener_todas_jugadas_numeradas(cls, cartas_mesa, jugadores):
        """Devuelve un diccionario con todas las jugadas numeradas"""
        jugadas_numeradas = {}
        contador = 1
        
        for i, jugada in enumerate(cartas_mesa):
            if jugada and i < len(jugadores):
                jugador_obj = jugadores[i]
                subgrupos = cls.dividir_en_grupos_validos(jugada)
                
                for subgrupo in subgrupos:
                    if len(subgrupo) >= 3:
                        # Determinar si es trío o seguidilla
                        es_trio = all(c.numero == subgrupo[0].numero for c in subgrupo if c.numero != 'Joker')
                        es_seguidilla = all(c.figura == subgrupo[0].figura for c in subgrupo if c.numero != 'Joker')
                        
                        if es_trio:
                            tipo = 'trio'
                        elif es_seguidilla:
                            tipo = 'seguidilla'
                        else:
                            tipo = 'grupo'
                        
                        jugadas_numeradas[contador] = {
                            'jugador_idx': i,
                            'jugador_nombre': jugador_obj.nombre_jugador,
                            'jugador_numero': jugador_obj.nro_jugador,
                            'subgrupo': subgrupo,
                            'tipo': tipo
                        }
                        contador += 1
        
        return jugadas_numeradas

    # NUEVO MÉTODO: Mostrar menú de extensión
    @classmethod
    def mostrar_menu_extension(cls, jugador_actual, jugadores, manos, mazo):
        jugador = jugadores[jugador_actual]
        mano_actual = manos[jugador_actual]
        
        print(f"\n--- TURNO DE {jugador.nombre_jugador.upper()} ---")
        
        # Obtener jugadas numeradas
        jugadas_numeradas = Jugada.obtener_todas_jugadas_numeradas(cls.cartas_mesa, jugadores)
        
        if not jugadas_numeradas:
            print("No hay jugadas en la mesa para extender.")
        else:
            print("Jugadas en la mesa (numeradas):")
            for num, info in jugadas_numeradas.items():
                print(f"({num}) {info['jugador_nombre']} - {info['tipo']}: {[str(c) for c in info['subgrupo']]}")
        
        print(f"\nTus cartas: {[str(c) for c in mano_actual]}")
        
        if cls.descarte:
            print(f"Carta en el descarte: {cls.descarte[-1]}")
        else:
            print("No hay carta en el descarte.")
        
        Jugada.cartas_usadas_extension = []
        
        while True:
            print("\nOpciones:")
            print("1. Robar carta del mazo cerrado")
            print("2. Tomar carta del descarte")
            print("3. Extender jugadas existentes")
            print("4. Reemplazar carta en jugada existente")  # ← NUEVA OPCIÓN
            
            opcion = input("Elige una opción: ")
            
            # ANTES DE ROBAR, REVISAMOS EL MAZO
            cls._revisar_y_barajar_quema(mazo)
            
            if opcion == "1":
                if mazo.cartas:
                    carta_robada = mazo.cartas.pop(-1)
                    mano_actual.append(carta_robada)
                    print(f"Has robado: {carta_robada}")
                    cls.compra(jugador_actual, jugadores, manos, mazo)
                    cls.descartar_carta(jugador_actual, jugadores, manos)
                    break
                else:
                    print("No hay cartas en el mazo cerrado.")
            
            elif opcion == "2":
                if cls.descarte:
                    carta_descarte = cls.descarte.pop(-1)
                    mano_actual.append(carta_descarte)
                    print(f"Has tomado del descarte: {carta_descarte}")
                    cls.descartar_carta(jugador_actual, jugadores, manos)
                    break
                else:
                    print("No hay carta en el descarte. Debes robar del mazo.")
            
            elif opcion == "3":
                if not jugadas_numeradas:
                    print("No hay jugadas para extender.")
                    continue
                
                extension_exitosa = Jugada.extender_jugadas(mano_actual, jugador, cls.cartas_mesa, jugadores)
                cls.mostrar_cartas_mesa()
                
                if not extension_exitosa:
                    continue
            
            elif opcion == "4":  # ← NUEVA OPCIÓN DE REEMPLAZO
                if not jugadas_numeradas:
                    print("No hay jugadas para modificar.")
                    continue
                
                reemplazo_exitosa = Jugada.reemplazar_carta_jugada(mano_actual, jugador, cls.cartas_mesa, jugadores)
                cls.mostrar_cartas_mesa()
                
                
                if not reemplazo_exitosa:
                    continue
            
            
            else:
                print("Opción inválida. Intenta de nuevo.")
        
        return mano_actual
    
    #NUEVO METODO: Calcular y mostrar puntuaciones
    @classmethod
    def calcular_y_mostrar_puntuaciones(cls, ganador, jugadores, manos):
        print("\nFIN DE LA JUGADA")
        print(f"Ganador: {ganador.nombre_jugador}")
        print("\nPuntuaciones:")
        
        puntuaciones = []
        for i, jugador in enumerate(jugadores):
            if jugador == ganador:
                continue
            
            mano_final = manos[i]
            puntos = sum(carta.valor_puntaje() for carta in mano_final)
            puntuaciones.append((jugador.nombre_jugador, puntos, [str(c) for c in mano_final]))
            
        puntuaciones.sort(key=lambda x: x[1])
        
        for nombre, puntos, mano_str in puntuaciones:
            print(f"\nJugador: {nombre}")
            print(f"  Puntos acumulados: {puntos}")
            print(f"  Cartas en mano: {', '.join(mano_str)}")

    @classmethod
    def iniciar_partida(cls):
        while not cls.cuantos_jugadores():
            pass  

        cantidad_de_jugadores = len(cls.lista_jugadores)
        palos = ('Pica', 'Corazon', 'Diamante', 'Trebol')
        nro_carta = ('A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K')
        
        mazo = Mazo()
        nro_mazos = mazo.calcular_nro_mazos(cantidad_de_jugadores)
        
        for _ in range(nro_mazos):
            for palo in palos:
                for carta in nro_carta:
                    cart = Cartas(carta, palo)
                    mazo.agregar_cartas(cart)
            # se agregan los dos Jokers
            mazo.agregar_cartas(Cartas('Joker', 'Especial'))
            mazo.agregar_cartas(Cartas('Joker', 'Especial'))
        
        mazo.revolver_mazo()
        mazo.mostrar_cartas("Las cartas en el mazo son: ")
        mazo.mostrar_numero_cartas("El número de cartas en el mazo: ")
        
        jugadores_reordenados = cls.jugador_mano_orden()
        manos = mazo.repartir_cartas(jugadores_reordenados)
        
        if mazo.cartas:
            cls.descarte.append(mazo.cartas.pop(-1))
        
        print("Inicia el juego")
        print(f"Carta inicial en el descarte: {cls.descarte[-1]}")
        cls.mostrar_manos(jugadores_reordenados, manos)
        mazo.mostrar_cartas("Las cartas restantes en el mazo son: ")
        mazo.mostrar_numero_cartas("El número de cartas en el mazo: ")
        
        cls.jugar_partida(jugadores_reordenados, manos, mazo)

    @classmethod
    def jugar_partida(cls, jugadores, manos, mazo):
        ronda_terminada = False
        ganador = None
        
        while not ronda_terminada:
            for i, jugador in enumerate(jugadores):
                mano_actual = manos[i]
                
                if jugador in cls.jugadores_primera_jugada:
                    # Jugador ya hizo primera jugada, mostrar menú de extensión
                    mano_actual = cls.mostrar_menu_extension(i, jugadores, manos, mazo)
                    manos[i] = mano_actual
                else:
                    # Jugador aún no ha hecho primera jugada
                    print(f"\nEs el turno de {jugador.nombre_jugador} (Jugador {jugador.nro_jugador})")
                    print("\nEs la primera ronda. Solo puedes intentar la primera jugada.")
                    print(f"Tus cartas: {[str(c) for c in mano_actual]}")
                    Mesa.mostrar_cartas_mesa()
                    
                    if cls.descarte:
                        print(f"Carta en el descarte: {cls.descarte[-1]}")
                    else:
                        print("No hay carta en el descarte.")
                    
                    while True:
                        print("\nOpciones:")
                        print("1. Robar carta del mazo cerrado")
                        print("2. Tomar carta del descarte")
                        print("3. Selecciona tus cartas para bajarte")
                        
                        opcion_robar = input("Elige una opción: ")
                        
                         # ANTES DE ROBAR, REVISAMOS EL MAZO
                        cls._revisar_y_barajar_quema(mazo)
                        
                        if opcion_robar == "1":
                            if mazo.cartas:
                                carta_robada = mazo.cartas.pop(-1)
                                mano_actual.append(carta_robada)
                                print(f"Has robado: {carta_robada}")
                                cls.compra(i, jugadores, manos, mazo)
                                cls.descartar_carta(i, jugadores, manos)
                                break
                            else:
                                print("No hay cartas en el mazo cerrado.")
                                continue
                        elif opcion_robar == "2":
                            if cls.descarte:
                                carta_descarte = cls.descarte.pop(-1)
                                mano_actual.append(carta_descarte)
                                print(f"Has tomado del descarte: {carta_descarte}")
                                cls.descartar_carta(i, jugadores, manos)
                                break
                            else:
                                print("No hay carta en el descarte. Debes robar del mazo.")
                                continue
                        elif opcion_robar == "3":
                            Jugada.validar_jugada(mano_actual, jugador, cls.cartas_mesa, cls.jugadores_primera_jugada, i)
                            cls.mostrar_cartas_mesa()
                            if jugador not in cls.jugadores_primera_jugada:
                                continue
                            else:
                                break
                        else:
                            print("Opción inválida. Intenta de nuevo.")
                
                # Verificar si el jugador se quedó sin cartas
                if not mano_actual:
                    print(f"\n¡{jugador.nombre_jugador} se ha quedado sin cartas y ha ganado la ronda!")
                    ronda_terminada = True
                    ganador = jugador
                    break
            
            if ronda_terminada:
                break
            
        if ganador:
            cls.calcular_y_mostrar_puntuaciones(ganador, jugadores, manos)


