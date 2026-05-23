from logica_juego.cartas import Cartas


# ══════════════════════════════════════════════════════════════════════════════
# NUEVA CLASE: GrupoJugada
# Representa una combinación de cartas (trío o seguidilla) que el jugador
# construye libremente antes de bajarla a la mesa.
# ══════════════════════════════════════════════════════════════════════════════

class GrupoJugada:
    """
    Estructura que agrupa cartas formando una combinación válida (trío/seguidilla).

    • No impone restricciones de orden previo — el jugador puede crear cualquier
      combinación válida sin necesidad de haber "bajado" antes.
    • Proporciona métodos para validar, añadir, quitar y consultar el tipo.
    """

    TIPO_TRIO       = "trio"
    TIPO_SEGUIDILLA = "seguidilla"
    TIPO_INVALIDO   = "invalido"

    def __init__(self):
        self.cartas: list = []          # objetos Cartas que forman el grupo
        self._tipo_cache = None         # cache del tipo para evitar recalcular

    # ── Mutadores ────────────────────────────────────────────────────────────

    def agregar(self, carta) -> bool:
        """
        Añade una carta al grupo si sigue siendo coherente con el tipo actual.
        Retorna True si se añadió, False si fue rechazada.
        """
        if isinstance(carta, str):
            carta = GrupoJugada._str_a_carta(carta)

        self.cartas.append(carta)
        self._tipo_cache = None          # invalidar cache

        tipo = self.tipo()
        if tipo == self.TIPO_INVALIDO and len(self.cartas) >= 2:
            # La carta rompe la combinación → devolverla
            self.cartas.pop()
            self._tipo_cache = None
            return False
        return True

    def quitar(self, carta) -> "Cartas | None":
        """
        Quita y retorna la carta del grupo.  Acepta string o Cartas.
        Retorna None si no se encontró.
        """
        if isinstance(carta, str):
            carta = GrupoJugada._str_a_carta(carta)
        for i, c in enumerate(self.cartas):
            if str(c).strip().lower() == str(carta).strip().lower():
                self._tipo_cache = None
                return self.cartas.pop(i)
        return None

    def limpiar(self):
        """Vacía el grupo y devuelve las cartas que contenía."""
        devueltas = list(self.cartas)
        self.cartas.clear()
        self._tipo_cache = None
        return devueltas

    # ── Consultas ────────────────────────────────────────────────────────────

    def tipo(self) -> str:
        """
        Determina y cachea el tipo actual del grupo.
        Con 0 o 1 carta siempre es indefinido (no inválido) para permitir
        que el jugador siga añadiendo.
        """
        if self._tipo_cache is not None:
            return self._tipo_cache

        n = len(self.cartas)
        if n <= 1:
            self._tipo_cache = self.TIPO_TRIO       # indeterminado → tratamos como trio
            return self._tipo_cache

        self._tipo_cache = self._clasificar()
        return self._tipo_cache

    def es_valida(self, minimo=3) -> bool:
        """True si el grupo tiene al menos `minimo` cartas y es trío o seguidilla."""
        return (len(self.cartas) >= minimo and
                self.tipo() in (self.TIPO_TRIO, self.TIPO_SEGUIDILLA))

    def __len__(self):
        return len(self.cartas)

    def __iter__(self):
        return iter(self.cartas)

    def __repr__(self):
        return f"GrupoJugada({self.tipo()}, {[str(c) for c in self.cartas]})"

    # ── Helpers internos ─────────────────────────────────────────────────────

    def _clasificar(self) -> str:
        """Clasifica el contenido actual como trio, seguidilla o invalido."""
        no_joker = [c for c in self.cartas if str(c.numero).lower() != "joker"]

        if not no_joker:
            return self.TIPO_TRIO   # solo jokers → aceptamos como trío implícito

        # ¿Trío? → todos los no-joker comparten el mismo número
        if len(set(str(c.numero) for c in no_joker)) == 1:
            return self.TIPO_TRIO

        # ¿Seguidilla? → mismo palo y valores consecutivos (con jokers como comodín)
        palos = set(c.figura for c in no_joker)
        if len(palos) == 1:
            valores = sorted(c.valor_numerico() for c in no_joker)
            jokers_disp = len(self.cartas) - len(no_joker)
            # contar "saltos" entre valores consecutivos
            saltos = sum(
                (valores[i + 1] - valores[i] - 1)
                for i in range(len(valores) - 1)
            )
            if saltos <= jokers_disp:
                return self.TIPO_SEGUIDILLA

        return self.TIPO_INVALIDO

    @staticmethod
    def _str_a_carta(texto: str) -> "Cartas":
        valor, _, palo = texto.partition(" de ")
        return Cartas(valor.strip(), palo.strip())


# ══════════════════════════════════════════════════════════════════════════════
# CLASE PRINCIPAL: Jugada
# ══════════════════════════════════════════════════════════════════════════════

class Jugada:
    # ── Estado de clase (compartido, igual que antes) ─────────────────────
    trio = []
    seguidilla = []
    cartas_usadas_extension = []

    def __init__(self):
        pass

    # ── Métodos originales preservados ────────────────────────────────────

    @classmethod
    def agregar_cartas_primera_jugada(cls, i, lista, cartas_mesa):
        """
        Agrega cartas a la mesa MANTENIENDO SEPARADAS las jugadas.
        """
        if not cartas_mesa[i]:
            cartas_mesa[i] = []
        nueva_jugada = list(lista)
        cartas_mesa[i].append(nueva_jugada)
        lista.clear()

    @classmethod
    def regresar_cartas(cls, lista, mano_actual):
        for x in lista:
            valor, _, palo = x.partition(" de ")
            c = Cartas(valor.strip(), palo.strip())
            mano_actual.append(c)

    @classmethod
    def eliminar_carta(cls, carta, mano_actual):
        carta_eliminada = None
        for x in mano_actual:
            if str(x).strip().lower() == carta:
                carta_eliminada = x
        if carta_eliminada:
            mano_actual.remove(carta_eliminada)

    @classmethod
    def salto_joker(cls, rango, valores):
        saltos = 0
        for i in range(rango, len(valores) - 1):
            if valores[i + 1] - valores[i] == 2:
                saltos += 1
        return saltos

    @classmethod
    def salto(cls, rango, valores):
        saltos = 0
        for i in range(rango, len(valores) - 1):
            if valores[i + 1] - valores[i] != 1:
                saltos += 1
        return saltos

    @classmethod
    def mover_joker(cls, seguidilla_ordenada):
        elemento = seguidilla_ordenada.pop(0)
        seguidilla_ordenada.append(elemento)

    @classmethod
    def jokers(cls, seguidilla_ordenada, valores, rango):
        c = 0
        for x in range(rango):
            elemento = seguidilla_ordenada.pop(0)
            insertado = 0
            for i in range(len(valores) - 1):
                actual = valores[i]
                siguiente = valores[i + 1]
                if siguiente - actual == 2 and actual != 0 and siguiente != 0 and c == 0:
                    seguidilla_ordenada.insert(i, elemento)
                    insertado = 1
                    c = 1
                    break
                elif siguiente - actual == 2 and actual != 0 and siguiente != 0 and c == 1:
                    seguidilla_ordenada.insert(i + 1, elemento)
                    insertado = 1
                    break
            if insertado == 0:
                seguidilla_ordenada.insert(0, elemento)

    @classmethod
    def opciones_joker(cls, seguidilla_ordenada, mensaje):
        print(mensaje)
        c = input("1 para colocarlo en el principio y 2 para colocarlo en el final: ")
        if c == "1":
            print("seguidilla válida")
        elif c == "2":
            cls.mover_joker(seguidilla_ordenada)
            print("seguidilla válida")

    @classmethod
    def dividir_en_grupos_validos(cls, jugada):
        """
        Divide una jugada en grupos válidos (tríos y seguidillas).
        """
        grupos = []
        actual = []

        for carta in jugada:
            if isinstance(carta, str):
                valor, _, palo = carta.partition(" de ")
                carta_obj = Cartas(valor.strip(), palo.strip())
            else:
                carta_obj = carta

            if not actual:
                actual.append(carta_obj)
                continue

            primera = actual[0]

            if (str(carta_obj.numero) == str(primera.numero) or
                    str(carta_obj.numero).lower() == 'joker' or
                    str(primera.numero).lower() == 'joker'):
                actual.append(carta_obj)

            elif (carta_obj.figura == primera.figura and
                  (str(carta_obj.numero).lower() == 'joker' or
                   str(primera.numero).lower() == 'joker' or
                   abs(carta_obj.valor_numerico() - actual[-1].valor_numerico()) == 1)):
                actual.append(carta_obj)

            else:
                grupos.append(actual)
                actual = [carta_obj]

        if actual:
            grupos.append(actual)

        return grupos

    @classmethod
    def puede_extender_seguidilla(cls, carta, seguidilla):
        seguidilla_cartas = []

        for c in seguidilla:
            if isinstance(c, str):
                valor, _, palo = c.partition(" de ")
                seguidilla_cartas.append(Cartas(valor.strip(), palo.strip()))
            else:
                seguidilla_cartas.append(c)

        cartas_no_joker = [c for c in seguidilla_cartas if str(c.numero).strip().lower() != 'joker']
        if not cartas_no_joker:
            return False

        palo_base = cartas_no_joker[0].figura.strip().lower()
        if carta.figura.strip().lower() != palo_base:
            return False

        if not all(c.figura.strip().lower() == palo_base for c in cartas_no_joker):
            return False

        valores = sorted(set(c.valor_numerico() for c in cartas_no_joker))

        if carta.valor_numerico() in valores:
            return False

        if carta.valor_numerico() == valores[0] - 1:
            return "inicio"
        if carta.valor_numerico() == valores[-1] + 1:
            return "final"

        return False

    @classmethod
    def puede_reemplazar_joker_trio(cls, carta, trio):
        trio_cartas = []
        for c in trio:
            if isinstance(c, str):
                valor, _, palo = c.partition(" de ")
                trio_cartas.append(Cartas(valor.strip(), palo.strip()))
            else:
                trio_cartas.append(c)

        valores = [c.numero for c in trio_cartas]
        if 'Joker' in valores:
            joker_index = valores.index('Joker')
            otros_valores = [val for i, val in enumerate(valores) if i != joker_index and val != 'Joker']
            if len(set(otros_valores)) == 1 and carta.numero == otros_valores[0]:
                return joker_index
        return -1

    @classmethod
    def puede_reemplazar_joker_seguidilla(cls, carta, seguidilla):
        """
        Verifica si una carta puede reemplazar un joker en una seguidilla.
        """
        seguidilla_cartas = []

        for c in seguidilla:
            if isinstance(c, str):
                valor, _, palo = c.partition(" de ")
                seguidilla_cartas.append(Cartas(valor.strip(), palo.strip()))
            else:
                seguidilla_cartas.append(c)

        joker_pos = -1
        for i, c in enumerate(seguidilla_cartas):
            if str(c.numero).lower() == 'joker':
                joker_pos = i
                break

        if joker_pos == -1:
            return False

        cartas_no_joker = [c for c in seguidilla_cartas if str(c.numero).lower() != 'joker']

        if not cartas_no_joker:
            return False

        if carta.figura != cartas_no_joker[0].figura:
            return False

        seguidilla_reemplazada = seguidilla_cartas.copy()
        seguidilla_reemplazada[joker_pos] = carta

        valores = []
        for c in seguidilla_reemplazada:
            if str(c.numero).lower() != 'joker':
                valores.append(c.valor_numerico())

        if len(valores) < 2:
            return False

        valores.sort()

        for i in range(len(valores) - 1):
            if valores[i + 1] - valores[i] != 1:
                return False

        return joker_pos

    @classmethod
    def obtener_todas_jugadas_numeradas(cls, cartas_mesa, jugadores):
        """Devuelve un diccionario con todas las jugadas numeradas."""
        jugadas_numeradas = {}
        contador = 1

        for i, jugadas_jugador in enumerate(cartas_mesa):
            if i < len(jugadores) and jugadas_jugador:
                jugador_obj = jugadores[i]

                for jugada_index, jugada in enumerate(jugadas_jugador):
                    if jugada:
                        subgrupos = cls.dividir_en_grupos_validos(jugada)

                        for subgrupo in subgrupos:
                            if len(subgrupo) >= 3:
                                es_trio = all(
                                    str(c.numero) == str(subgrupo[0].numero)
                                    for c in subgrupo
                                    if str(c.numero).lower() != 'joker'
                                )

                                es_seguidilla = all(
                                    c.figura == subgrupo[0].figura
                                    for c in subgrupo
                                    if str(c.numero).lower() != 'joker'
                                )

                                if es_trio:
                                    tipo = 'trio'
                                elif es_seguidilla:
                                    tipo = 'seguidilla'
                                else:
                                    continue

                                jugadas_numeradas[contador] = {
                                    'jugador_idx': i,
                                    'jugada_index': jugada_index,
                                    'jugador_nombre': jugador_obj.nombre_jugador,
                                    'jugador_numero': jugador_obj.nro_jugador,
                                    'subgrupo': subgrupo,
                                    'tipo': tipo,
                                    'jugada_original': jugada
                                }
                                contador += 1

        return jugadas_numeradas

    @classmethod
    def extender_jugadas(cls, mano_actual, jugador, cartas_mesa, jugadores):
        """Permite extender jugadas existentes en la mesa."""
        print("\n--- EXTENDER JUGADAS ---")
        jugadas_numeradas = cls.obtener_todas_jugadas_numeradas(cartas_mesa, jugadores)

        if not jugadas_numeradas:
            print("No hay jugadas en la mesa para extender.")
            return False

        print("Jugadas en la mesa:")
        for num, info in jugadas_numeradas.items():
            print(f"({num}) {info['jugador_nombre']} - {info['tipo']}: {[str(c) for c in info['subgrupo']]}")

        print(f"\nTus cartas:")
        for i, carta in enumerate(mano_actual, 1):
            print(f"{i}. {carta}")

        while True:
            try:
                seleccion_jugada = int(input("\nSelecciona el número de la jugada que deseas extender (0 para cancelar): "))
                if seleccion_jugada == 0:
                    return False
                if seleccion_jugada in jugadas_numeradas:
                    break
                else:
                    print("Número de jugada inválido. Intenta de nuevo.")
            except ValueError:
                print("Por favor ingresa un número válido.")

        jugada_info = jugadas_numeradas[seleccion_jugada]
        jugada_seleccionada = jugada_info['subgrupo']
        tipo_jugada = jugada_info['tipo']
        mesa_idx = jugada_info['jugador_idx']
        jugada_index = jugada_info['jugada_index']
        jugada_original = jugada_info['jugada_original']

        print(f"\nHas seleccionado: {tipo_jugada} - {[str(c) for c in jugada_seleccionada]}")

        cartas_validas = []

        for i, carta in enumerate(mano_actual):
            if isinstance(carta, str):
                valor, _, palo = carta.partition(" de ")
                carta_obj = Cartas(valor.strip(), palo.strip())
                mano_actual[i] = carta_obj
                carta = carta_obj

            if tipo_jugada == "trio":
                if str(carta.numero).lower() == str(jugada_seleccionada[0].numero).lower():
                    cartas_validas.append((i, carta, "agregar"))
                joker_pos = cls.puede_reemplazar_joker_trio(carta, jugada_seleccionada)
                if joker_pos != -1:
                    cartas_validas.append((i, carta, "reemplazar_joker", joker_pos))

            elif tipo_jugada == "seguidilla":
                extension = cls.puede_extender_seguidilla(carta, jugada_seleccionada)
                if extension:
                    cartas_validas.append((i, carta, "extender", extension))
                joker_pos = cls.puede_reemplazar_joker_seguidilla(carta, jugada_seleccionada)
                if joker_pos is not False:
                    cartas_validas.append((i, carta, "reemplazar_joker", joker_pos))

        if not cartas_validas:
            print("No tienes cartas válidas para extender esta jugada.")
            return False

        print("\nCartas válidas para esta jugada:")
        for idx, (carta_idx, carta, accion, *extra) in enumerate(cartas_validas, 1):
            if accion == "agregar":
                print(f"{idx}. {carta} (agregar al trío)")
            elif accion == "extender":
                pos = extra[0]
                print(f"{idx}. {carta} (agregar al {pos} de la seguidilla)")
            else:
                joker_pos = extra[0]
                print(f"{idx}. {carta} (reemplazar joker en posición {joker_pos+1})")

        while True:
            try:
                seleccion_carta = int(input("\nSelecciona el número de la carta a usar (0 para cancelar): "))
                if seleccion_carta == 0:
                    return False
                if 1 <= seleccion_carta <= len(cartas_validas):
                    break
                else:
                    print("Número de carta inválido. Intenta de nuevo.")
            except ValueError:
                print("Por favor ingresa un número válido.")

        carta_idx, carta, accion, *extra = cartas_validas[seleccion_carta - 1]
        jugada_modificada = jugada_seleccionada.copy()

        if accion == "agregar":
            jugada_modificada.append(carta)
            mano_actual.remove(carta)
            print(f"Has agregado {carta} al trío.")

        elif accion == "extender":
            pos = extra[0]
            if pos == "inicio":
                jugada_modificada.insert(0, carta)
            else:
                jugada_modificada.append(carta)
            mano_actual.remove(carta)
            print(f"Has agregado {carta} al {pos} de la seguidilla.")

        else:
            joker_pos = extra[0]
            joker = jugada_modificada[joker_pos]
            jugada_modificada[joker_pos] = carta
            mano_actual.remove(carta)
            mano_actual.append(joker)
            print(f"Has reemplazado el joker con {carta}. El joker ha sido devuelto a tu mano.")

        nueva_jugada_completa = []
        subgrupos_originales = cls.dividir_en_grupos_validos(jugada_original)

        for grupo in subgrupos_originales:
            if [str(c) for c in grupo] == [str(c) for c in jugada_seleccionada]:
                nueva_jugada_completa.extend(jugada_modificada)
            else:
                nueva_jugada_completa.extend(grupo)

        cartas_mesa[mesa_idx][jugada_index] = nueva_jugada_completa
        print("¡Jugada actualizada exitosamente!")
        return True

    @classmethod
    def reemplazar_carta_jugada(cls, mano_actual, jugador, cartas_mesa, jugadores):
        """Permite reemplazar una carta existente en una jugada."""
        print("\n--- REEMPLAZAR CARTA EN JUGADA ---")

        jugadas_numeradas = cls.obtener_todas_jugadas_numeradas(cartas_mesa, jugadores)

        if not jugadas_numeradas:
            print("No hay jugadas en la mesa para modificar.")
            return False

        print("Jugadas en la mesa:")
        for num, info in jugadas_numeradas.items():
            print(f"({num}) {info['jugador_nombre']} - {info['tipo']}: {[str(c) for c in info['subgrupo']]}")

        while True:
            try:
                seleccion_jugada = int(input("\nSelecciona el número de la jugada donde quieres reemplazar una carta (0 para cancelar): "))
                if seleccion_jugada == 0:
                    return False
                if seleccion_jugada in jugadas_numeradas:
                    break
                else:
                    print("Número de jugada inválido. Intenta de nuevo.")
            except ValueError:
                print("Por favor ingresa un número válido.")

        jugada_info = jugadas_numeradas[seleccion_jugada]
        jugada_seleccionada = jugada_info['subgrupo']
        mesa_idx = jugada_info['jugador_idx']
        jugada_index = jugada_info['jugada_index']
        jugada_original = jugada_info['jugada_original']

        print(f"\nJugada seleccionada: {[str(c) for c in jugada_seleccionada]}")

        print("\nCartas en la jugada:")
        for i, carta in enumerate(jugada_seleccionada, 1):
            print(f"{i}. {carta}")

        while True:
            try:
                seleccion_carta_vieja = int(input("\nSelecciona el número de la carta a reemplazar (0 para cancelar): "))
                if seleccion_carta_vieja == 0:
                    return False
                if 1 <= seleccion_carta_vieja <= len(jugada_seleccionada):
                    break
                else:
                    print("Número de carta inválido. Intenta de nuevo.")
            except ValueError:
                print("Por favor ingresa un número válido.")

        carta_vieja = jugada_seleccionada[seleccion_carta_vieja - 1]

        print(f"\nTus cartas:")
        for i, carta in enumerate(mano_actual, 1):
            print(f"{i}. {carta}")

        while True:
            try:
                seleccion_carta_nueva = int(input(f"\nSelecciona el número de la carta para reemplazar {carta_vieja} (0 para cancelar): "))
                if seleccion_carta_nueva == 0:
                    return False
                if 1 <= seleccion_carta_nueva <= len(mano_actual):
                    break
                else:
                    print("Número de carta inválido. Intenta de nuevo.")
            except ValueError:
                print("Por favor ingresa un número válido.")

        carta_nueva = mano_actual[seleccion_carta_nueva - 1]

        jugada_modificada = jugada_seleccionada.copy()
        jugada_modificada[seleccion_carta_vieja - 1] = carta_nueva

        if not cls.es_jugada_valida(jugada_modificada, jugada_info['tipo']):
            print("El reemplazo haría que la jugada sea inválida.")
            return False

        mano_actual.remove(carta_nueva)
        mano_actual.append(carta_vieja)

        nueva_jugada_completa = []
        subgrupos_originales = cls.dividir_en_grupos_validos(jugada_original)

        for grupo in subgrupos_originales:
            if [str(c) for c in grupo] == [str(c) for c in jugada_seleccionada]:
                nueva_jugada_completa.extend(jugada_modificada)
            else:
                nueva_jugada_completa.extend(grupo)

        cartas_mesa[mesa_idx][jugada_index] = nueva_jugada_completa
        print(f"¡Has reemplazado {carta_vieja} con {carta_nueva} exitosamente!")
        return True

    @classmethod
    def es_jugada_valida(cls, jugada, tipo):
        """Verifica si una jugada sigue siendo válida después de un reemplazo."""
        if tipo == "trio":
            numeros = [str(c.numero).strip().lower() for c in jugada if str(c.numero).strip().lower() != 'joker']
            return len(set(numeros)) == 1 if numeros else True

        elif tipo == "seguidilla":
            cartas_no_joker = [c for c in jugada if str(c.numero).lower() != 'joker']
            if not cartas_no_joker:
                return True
            if not all(c.figura == cartas_no_joker[0].figura for c in cartas_no_joker):
                return False
            valores = [c.valor_numerico() for c in cartas_no_joker]
            valores.sort()
            for i in range(len(valores) - 1):
                if valores[i + 1] - valores[i] != 1:
                    return False
            return True

        return False

    # ══════════════════════════════════════════════════════════════════════════
    # NUEVO: validar_jugada LIBRE — sin restricción de "primera jugada"
    #
    # El jugador puede bajar a la mesa CUALQUIER combinación válida desde
    # su mano, sin necesidad de haber bajado antes un trío + seguidilla.
    # Si existía alguna "jugada determinada" guardada en cls.trio /
    # cls.seguidilla, se limpia automáticamente al entrar a este método.
    # ══════════════════════════════════════════════════════════════════════════

    @classmethod
    def validar_jugada(cls, mano_actual, jugador, cartas_mesa, jugadores_primera_jugada, i):
        """
        Permite al jugador crear y bajar a la mesa cualquier jugada válida
        (trío o seguidilla) desde su mano, sin restricciones previas.

        • Si el jugador ya hizo su primera jugada, sigue pudiéndolas bajar.
        • Cualquier "jugada determinada" previa (cls.trio / cls.seguidilla)
          se descarta automáticamente al inicio para no bloquear al jugador.
        • La primera vez que el jugador baja una jugada, se le marca como
          habiéndola hecho (jugadores_primera_jugada).

        Opciones durante la selección:
            1  → confirmar el grupo de cartas seleccionadas
            2  → limpiar la selección y empezar de nuevo
            3  → salir sin bajar ninguna jugada
        """
        # ── Limpiar cualquier estado previo "determinado" ─────────────────
        cls.trio.clear()
        cls.seguidilla.clear()

        print("\n--- BAJAR JUGADA ---")
        print("Selecciona cartas para formar un trío (mín. 3) o seguidilla (mín. 3).")
        print("Comandos: [1] Confirmar  [2] Limpiar  [3] Salir")

        grupo = GrupoJugada()
        carta_cmd = None

        while True:
            mano_str = [str(c).lower() for c in mano_actual]

            # Mostrar mano y selección actual
            print(f"\nTu mano: {[str(c) for c in mano_actual]}")
            if grupo.cartas:
                print(f"Selección actual ({grupo.tipo()}): {[str(c) for c in grupo.cartas]}")

            carta_cmd = input("Carta (o 1/2/3): ").strip().lower()

            # ── Confirmar ─────────────────────────────────────────────────
            if carta_cmd == "1":
                if not grupo.es_valida(minimo=3):
                    print(f"Jugada inválida o incompleta (necesitas al menos 3 cartas válidas). "
                          f"Tipo detectado: {grupo.tipo()}, cartas: {len(grupo)}.")
                    continue

                # Registrar jugada en la mesa
                cls.agregar_cartas_primera_jugada(i, grupo.cartas, cartas_mesa)

                # Marcar primera jugada si aún no la hizo
                if jugador not in jugadores_primera_jugada:
                    jugadores_primera_jugada.append(jugador)
                    print("¡Primera jugada registrada!")

                print(f"✔ Jugada bajada a la mesa: {grupo.tipo().upper()} "
                      f"— {[str(c) for c in cartas_mesa[i][-1]]}")
                return True

            # ── Limpiar selección ─────────────────────────────────────────
            elif carta_cmd == "2":
                devueltas = grupo.limpiar()
                mano_actual.extend(devueltas)
                print("Selección limpiada. Cartas devueltas a tu mano.")
                continue

            # ── Salir sin bajar ───────────────────────────────────────────
            elif carta_cmd == "3":
                devueltas = grupo.limpiar()
                mano_actual.extend(devueltas)
                print("Saliste sin bajar ninguna jugada.")
                return False

            # ── Seleccionar carta ─────────────────────────────────────────
            elif carta_cmd in mano_str:
                # Encontrar el objeto Cartas correspondiente
                carta_obj = None
                for c in mano_actual:
                    if str(c).lower() == carta_cmd:
                        carta_obj = c
                        break

                if carta_obj is None:
                    print("No se encontró la carta.")
                    continue

                mano_actual.remove(carta_obj)

                if not grupo.agregar(carta_obj):
                    # La carta no es compatible → devolverla a la mano
                    mano_actual.append(carta_obj)
                    print(f"'{carta_obj}' no es compatible con la combinación actual "
                          f"({grupo.tipo()}). Carta devuelta.")
                else:
                    print(f"'{carta_obj}' añadida. Selección: {[str(c) for c in grupo.cartas]}")

            else:
                print("Carta no encontrada en tu mano. Escribe exactamente como se muestra.")

    # conquiste este codigo :vvvvv
