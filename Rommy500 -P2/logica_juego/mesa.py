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
        """
        Muestra las manos en consola.
        Acepta tanto manos como lista (modo local) como dict {id: cartas} (modo red).
        """
        for i, jugador in enumerate(jugadores_reordenados):
            if isinstance(manos, dict):
                mano = manos.get(jugador.nro_jugador, [])
            else:
                mano = manos[i]
            print(f'\nCartas del jugador {jugador.nro_jugador} - {jugador.nombre_jugador}:')
            print([str(c) for c in mano])

    @classmethod
    def jugador_mano_orden(cls):
        # Elige aleatoriamente el índice y el objeto del jugador que será el jugador mano
        indice_del_jugador_mano, nom_jug_mano = choice(list(enumerate(cls.lista_jugadores)))
        print(f"El jugador mano es: {nom_jug_mano.nombre_jugador}")

        # Reordenar empezando por el jugador mano
        jugadores_reordenados = (cls.lista_jugadores[indice_del_jugador_mano:] +
                                 cls.lista_jugadores[:indice_del_jugador_mano])

        # Inicializar lista vacía de jugadas por jugador
        for _ in range(len(jugadores_reordenados)):
            cls.cartas_mesa.append([])

        return jugadores_reordenados

    # ── Quema ─────────────────────────────────────────────────────────────

    @classmethod
    def _revisar_y_barajar_quema(cls, mazo):
        """Revisa si el mazo está vacío y baraja la quema si es necesario."""
        if not mazo.cartas and cls.quema:
            print("\n¡El mazo se ha agotado! Barajando las cartas quemadas...")
            mazo.cartas.extend(cls.quema)
            cls.quema.clear()
            mazo.revolver_mazo()
            print("Nuevo mazo creado y barajado.")

    # ══════════════════════════════════════════════════════════════════════
    # NUEVO: iniciar_ronda_red
    # Reemplaza la lógica de repartición del servidor (_logica_partida.py)
    # usando repartir_para_red() que devuelve dict {id_jugador: mano},
    # eliminando el desfase entre posición en jugadores_reordenados e id
    # que causaba manos de 15 y 9 cartas.
    # ══════════════════════════════════════════════════════════════════════

    @classmethod
    def iniciar_ronda_red(cls, lista_jugadores_objetos, cantidad_de_jugadores):
        """
        Prepara y reparte las cartas para una partida en red.

        PROBLEMA QUE CORRIGE:
        ─────────────────────
        El servidor llamaba a repartir_cartas() (devuelve lista posicional) y
        luego mapeaba manos[i] → self.manos[id_jugador] usando el índice de
        posición. Como jugadores_reordenados empieza por el jugador-mano
        (elegido al azar), el índice 0 NO siempre corresponde al id=1,
        provocando que el jugador 1 recibiera 15 cartas y el jugador 2, 9.

        SOLUCIÓN:
        ─────────
        Usar repartir_para_red() que construye directamente el dict
        {id_jugador: [Carta, ...]} usando jugador.nro_jugador como clave,
        garantizando que cada cliente reciba exactamente 10 cartas correctas
        sin importar el orden de reordenamiento por jugador-mano.

        Args:
            lista_jugadores_objetos (list): Objetos Jugador/Jugador_interfaz
                con atributo nro_jugador (= id de red, 1-based).
            cantidad_de_jugadores (int): Número de jugadores activos.

        Returns:
            tuple:
                jugadores_reordenados (list): Jugadores en orden de turno
                    (jugador-mano en posición 0).
                manos_dict (dict): {id_jugador (int): [Carta, ...]}
                    Exactamente 10 cartas por jugador.
                mazo (Mazo): Mazo residual tras la repartición y el descarte.
                carta_descarte_inicial (Carta): Primera carta del descarte.
        """
        palos    = ('Pica', 'Corazon', 'Diamante', 'Trebol')
        nro_carta = ('A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K')

        # ── Construir mazo ────────────────────────────────────────────────
        mazo = Mazo()
        nro_mazos = mazo.calcular_nro_mazos(cantidad_de_jugadores)

        for _ in range(nro_mazos):
            for palo in palos:
                for carta in nro_carta:
                    mazo.agregar_cartas(Cartas(carta, palo))
            mazo.agregar_cartas(Cartas('Joker', 'Especial'))
            mazo.agregar_cartas(Cartas('Joker', 'Especial'))

        # ── Reordenar por jugador-mano ────────────────────────────────────
        # Guardamos una copia limpia de la lista original para no mutarla
        cls.lista_jugadores = list(lista_jugadores_objetos)
        jugadores_reordenados = cls.jugador_mano_orden()

        # ── Repartir con dict {id_jugador: mano} ─────────────────────────
        # CORRECCIÓN CLAVE: repartir_para_red() usa jugador.nro_jugador como
        # clave del dict, evitando el desfase entre posición e id de red.
        manos_dict = mazo.repartir_para_red(jugadores_reordenados, cartas_por_jugador=10)

        # ── Descarte inicial ──────────────────────────────────────────────
        carta_descarte_inicial = None
        if mazo.cartas:
            carta_descarte_inicial = mazo.cartas.pop(-1)
            cls.descarte.append(carta_descarte_inicial)

        # ── Debug ─────────────────────────────────────────────────────────
        print("\n[Mesa.iniciar_ronda_red] Manos repartidas:")
        cls.mostrar_manos(jugadores_reordenados, manos_dict)
        print(f"[Mesa.iniciar_ronda_red] Carta inicial en el descarte: {carta_descarte_inicial}")
        print(f"[Mesa.iniciar_ronda_red] Cartas restantes en el mazo: {len(mazo.cartas)}")

        return jugadores_reordenados, manos_dict, mazo, carta_descarte_inicial

    # ── Métodos de juego ──────────────────────────────────────────────────

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
            respuesta = input(
                f'{jugador_siguiente.nombre_jugador}, '
                f'¿quieres comprar la carta del descarte ({carta_descarte})? (si/no): '
            )

            if cls.normalizar(respuesta) == 'si':
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

            idx = (idx + 1) % cantidad_jugadores
            intentos += 1

        if not carta_comprada:
            carta_quemada = cls.descarte.pop(-1)
            cls.quema.append(carta_quemada)
            print(f"Nadie compró la carta. Se ha quemado: {carta_quemada}")

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
        jugador    = jugadores[jugador_actual]
        mano_actual = manos[jugador_actual]
        print(f"\n{jugador.nombre_jugador}, debes descartar una carta.")
        print("Tus cartas actuales:")

        for idx, carta in enumerate(mano_actual, 1):
            print(f"{idx}. {carta}")

        while True:
            try:
                indice = int(input("Ingresa el número de la carta que quieres descartar: "))
                if 1 <= indice <= len(mano_actual):
                    carta_a_descartar = mano_actual.pop(indice - 1)

                    if str(carta_a_descartar.numero).lower() == 'joker':
                        print(f"¡Has descartado un Joker! Debes descartar otra carta.")
                        cls.quema.append(carta_a_descartar)

                        if not mano_actual:
                            print("No te quedan más cartas para descartar.")
                            break

                        print("\nAhora, elige la segunda carta para descartar:")
                        for idx, carta in enumerate(mano_actual, 1):
                            print(f"{idx}. {carta}")

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
        """Devuelve un diccionario con todas las jugadas numeradas."""
        jugadas_numeradas = {}
        contador = 1

        for i, jugada in enumerate(cartas_mesa):
            if jugada and i < len(jugadores):
                jugador_obj = jugadores[i]
                subgrupos   = cls.dividir_en_grupos_validos(jugada)

                for subgrupo in subgrupos:
                    if len(subgrupo) >= 3:
                        es_trio      = all(c.numero == subgrupo[0].numero for c in subgrupo if c.numero != 'Joker')
                        es_seguidilla = all(c.figura == subgrupo[0].figura for c in subgrupo if c.numero != 'Joker')

                        if es_trio:
                            tipo = 'trio'
                        elif es_seguidilla:
                            tipo = 'seguidilla'
                        else:
                            tipo = 'grupo'

                        jugadas_numeradas[contador] = {
                            'jugador_idx':    i,
                            'jugador_nombre': jugador_obj.nombre_jugador,
                            'jugador_numero': jugador_obj.nro_jugador,
                            'subgrupo':       subgrupo,
                            'tipo':           tipo
                        }
                        contador += 1

        return jugadas_numeradas

    @classmethod
    def mostrar_menu_extension(cls, jugador_actual, jugadores, manos, mazo):
        jugador     = jugadores[jugador_actual]
        mano_actual = manos[jugador_actual]

        print(f"\n--- TURNO DE {jugador.nombre_jugador.upper()} ---")

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
            print("4. Reemplazar carta en jugada existente")

            opcion = input("Elige una opción: ")

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

            elif opcion == "4":
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

    # ── Partida local (sin red) ───────────────────────────────────────────

    @classmethod
    def iniciar_partida(cls):
        while not cls.cuantos_jugadores():
            pass

        cantidad_de_jugadores = len(cls.lista_jugadores)
        palos    = ('Pica', 'Corazon', 'Diamante', 'Trebol')
        nro_carta = ('A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K')

        mazo = Mazo()
        nro_mazos = mazo.calcular_nro_mazos(cantidad_de_jugadores)

        for _ in range(nro_mazos):
            for palo in palos:
                for carta in nro_carta:
                    mazo.agregar_cartas(Cartas(carta, palo))
            mazo.agregar_cartas(Cartas('Joker', 'Especial'))
            mazo.agregar_cartas(Cartas('Joker', 'Especial'))

        mazo.revolver_mazo()
        mazo.mostrar_cartas("Las cartas en el mazo son: ")
        mazo.mostrar_numero_cartas("El número de cartas en el mazo: ")

        jugadores_reordenados = cls.jugador_mano_orden()

        # Modo local: lista posicional es suficiente
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
                    mano_actual = cls.mostrar_menu_extension(i, jugadores, manos, mazo)
                    manos[i] = mano_actual
                else:
                    print(f"\nEs el turno de {jugador.nombre_jugador} (Jugador {jugador.nro_jugador})")
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
                            Jugada.validar_jugada(
                                mano_actual, jugador,
                                cls.cartas_mesa, cls.jugadores_primera_jugada, i
                            )
                            cls.mostrar_cartas_mesa()
                            if jugador not in cls.jugadores_primera_jugada:
                                continue
                            else:
                                break
                        else:
                            print("Opción inválida. Intenta de nuevo.")

                if not mano_actual:
                    print(f"\n¡{jugador.nombre_jugador} se ha quedado sin cartas y ha ganado la ronda!")
                    ronda_terminada = True
                    ganador = jugador
                    break

            if ronda_terminada:
                break

        if ganador:
            cls.calcular_y_mostrar_puntuaciones(ganador, jugadores, manos)
