from random import shuffle
import math

class Mazo:
    """
    Clase Mazo para el juego Rummy 500.

    CORRECCIONES APLICADAS:
    ─────────────────────────────────────────────────────────────────
    1. repartir_cartas() garantiza EXACTAMENTE cartas_por_jugador (default=10)
       a cada jugador, sin importar el reordenamiento por jugador-mano.
    2. repartir_para_red() — método nuevo — devuelve un DICT {id_jugador: mano}
       en lugar de una lista posicional, eliminando el desfase entre posición
       e id que causaba manos de 15 y 9 cartas en el servidor.
    3. verificar_cartas_suficientes() para consultar sin lanzar excepción.
    4. validar_manos() detecta y loguea manos con cantidad incorrecta o
       cartas duplicadas entre jugadores.
    5. Callback opcional actualizar_visual para reposicionar cartas en Pygame.
    """

    def __init__(self):
        self.cartas = []

    # ── Mutadores básicos ─────────────────────────────────────────────────

    def agregar_cartas(self, carta):
        self.cartas.append(carta)

    def revolver_mazo(self):
        """Baraja las cartas del mazo en su lugar (Fisher-Yates via random.shuffle)."""
        shuffle(self.cartas)

    def calcular_nro_mazos(self, numero_de_jugadores):
        if numero_de_jugadores == 0:
            return 0
        resultado = math.ceil(numero_de_jugadores / 3) + 1
        return resultado
    
    # def calcular_nro_mazos(self, numero_de_jugadores):
    #     resultado = numero_de_jugadores // 3 
    #     if numero_de_jugadores % 3 != 0:
    #         resultado += 1
    #     return resultado

    # ── Diagnóstico ───────────────────────────────────────────────────────

    def mostrar_cartas(self, mensaje):
        print(mensaje)
        for carta in self.cartas:
            print(carta)

    def mostrar_numero_cartas(self, mensaje):
        print(str(mensaje) + str(len(self.cartas)))

    # ── Verificación previa ───────────────────────────────────────────────

    def verificar_cartas_suficientes(self, num_jugadores, cartas_por_jugador=10):
        """
        Verifica si el mazo tiene cartas suficientes SIN lanzar excepción.

        Returns:
            tuple[bool, int, int]: (suficientes, disponibles, necesarias)
        """
        necesarias  = cartas_por_jugador * num_jugadores
        disponibles = len(self.cartas)
        return disponibles >= necesarias, disponibles, necesarias

    # ── Validación post-repartición ───────────────────────────────────────

    @staticmethod
    def validar_manos(manos, cartas_por_jugador=10):
        """
        Verifica que todas las manos tengan exactamente cartas_por_jugador cartas
        y que no existan cartas duplicadas entre distintas manos.

        Args:
            manos: list[list] devuelta por repartir_cartas(), O
                   dict {id: list} devuelta por repartir_para_red().
            cartas_por_jugador (int): Cantidad esperada por jugador.

        Returns:
            bool: True si todo es correcto.
        """
        ok = True

        # Normalizar a lista de (etiqueta, mano)
        if isinstance(manos, dict):
            items = [(f"id={k}", v) for k, v in manos.items()]
        else:
            items = [(f"pos={i}", m) for i, m in enumerate(manos)]

        # 1. Cantidad exacta por jugador
        for etiqueta, mano in items:
            if len(mano) != cartas_por_jugador:
                print(
                    f"[Mazo.validar_manos] ✗ Jugador {etiqueta} tiene "
                    f"{len(mano)} cartas (se esperaban {cartas_por_jugador})."
                )
                ok = False
            else:
                print(f"[Mazo.validar_manos] ✓ Jugador {etiqueta}: {cartas_por_jugador} cartas.")

        # 2. Sin duplicados entre manos
        vistas = {}
        for etiqueta, mano in items:
            for carta in mano:
                clave = str(carta)
                if clave in vistas:
                    print(
                        f"[Mazo.validar_manos] ✗ Carta duplicada '{clave}' "
                        f"en jugador {etiqueta} y jugador {vistas[clave]}."
                    )
                    ok = False
                else:
                    vistas[clave] = etiqueta

        if ok:
            print("[Mazo.validar_manos] ✓ Todas las manos son correctas.")
        return ok

    # ── Repartición principal (modo local / lista) ────────────────────────

    def repartir_cartas(self, lista_de_jugadores, cartas_por_jugador=10,
                        actualizar_visual=None, un_juego=None):
        """
        Baraja y reparte EXACTAMENTE cartas_por_jugador a cada jugador.
        Devuelve una LISTA de manos indexada por posición en lista_de_jugadores.

        Úsalo para el modo local (mesa.py / principal.py).
        Para el servidor de red, usa repartir_para_red() que devuelve un dict
        {id_jugador: mano} y evita el desfase posición-id.

        Args:
            lista_de_jugadores (list): Jugadores activos en orden de turno.
            cartas_por_jugador (int): Cartas por jugador. Default 10.
            actualizar_visual (callable|None): Callback f(idx, mano, un_juego)
                para reposicionar cartas en Pygame tras repartir.
            un_juego: Referencia al juego para el callback visual.

        Returns:
            list[list]: manos[i] → cartas del jugador en la posición i.

        Raises:
            ValueError: Si no hay cartas suficientes.
        """
        num_jugadores = len(lista_de_jugadores)

        # 1. Barajar
        self.revolver_mazo()

        # 2. Verificar cartas suficientes
        suficientes, disponibles, necesarias = self.verificar_cartas_suficientes(
            num_jugadores, cartas_por_jugador
        )
        if not suficientes:
            raise ValueError(
                f"[Mazo] Cartas insuficientes: hay {disponibles}, "
                f"se necesitan {necesarias} para repartir {cartas_por_jugador} "
                f"a cada uno de los {num_jugadores} jugadores."
            )

        # 3. Manos vacías (cada jugador recibe su propia lista nueva)
        manos = [[] for _ in range(num_jugadores)]

        # 4. Repartir en ronda — UNA carta por jugador por vuelta
        #    Esto garantiza EXACTAMENTE cartas_por_jugador por jugador.
        for _ in range(cartas_por_jugador):
            for idx_jugador in range(num_jugadores):
                carta = self.cartas.pop(0)  # elimina la carta del tope
                manos[idx_jugador].append(carta)

        # 5. Validar resultado
        self.validar_manos(manos, cartas_por_jugador)

        # 6. Callback visual opcional
        if callable(actualizar_visual):
            for idx_jugador, mano in enumerate(manos):
                try:
                    actualizar_visual(idx_jugador, mano, un_juego)
                except Exception as e:
                    print(f"[Mazo] Error actualizando visual jugador {idx_jugador}: {e}")

        return manos

    # ── Repartición para red (modo servidor / dict) ───────────────────────

    def repartir_para_red(self, jugadores_reordenados, cartas_por_jugador=10):
        """
        Baraja y reparte EXACTAMENTE cartas_por_jugador a cada jugador.
        Devuelve un DICT {id_jugador (int): list[Carta]} en lugar de una lista
        posicional, eliminando el desfase entre posición e id_jugador que
        causaba manos de 15 y 9 cartas en el servidor.

        PROBLEMA QUE RESUELVE:
        ──────────────────────
        jugadores_reordenados empieza por el jugador-mano (elegido al azar),
        por lo que manos[0] corresponde al jugador-mano, NO necesariamente al
        jugador con id=1.  Al guardar las manos como dict {id: cartas} el
        servidor siempre puede recuperar la mano correcta con self.manos[id]
        sin importar el orden de turno.

        Args:
            jugadores_reordenados (list): Objetos Jugador en orden de turno
                (el jugador-mano va en la posición 0).
                Cada objeto debe tener el atributo nro_jugador (= id de red).
            cartas_por_jugador (int): Cartas por jugador. Default 10.

        Returns:
            dict[int, list]: {id_jugador: [Carta, ...]}

        Raises:
            ValueError: Si no hay cartas suficientes.
        """
        num_jugadores = len(jugadores_reordenados)

        # 1. Barajar
        self.revolver_mazo()

        # 2. Verificar cartas suficientes
        suficientes, disponibles, necesarias = self.verificar_cartas_suficientes(
            num_jugadores, cartas_por_jugador
        )
        if not suficientes:
            raise ValueError(
                f"[Mazo] Cartas insuficientes: hay {disponibles}, "
                f"se necesitan {necesarias} para repartir {cartas_por_jugador} "
                f"a cada uno de los {num_jugadores} jugadores."
            )

        # 3. Inicializar dict {id_jugador: []} usando nro_jugador como clave
        manos_dict = {j.nro_jugador: [] for j in jugadores_reordenados}

        # 4. Repartir en ronda — UNA carta por jugador por vuelta
        for _ in range(cartas_por_jugador):
            for jugador in jugadores_reordenados:
                carta = self.cartas.pop(0)
                manos_dict[jugador.nro_jugador].append(carta)

        # 5. Validar resultado
        self.validar_manos(manos_dict, cartas_por_jugador)

        return manos_dict
