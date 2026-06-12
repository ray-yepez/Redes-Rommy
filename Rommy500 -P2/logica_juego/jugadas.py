from logica_juego.cartas import Cartas

class Jugada:
    trio = []
    seguidilla = []
    cartas_usadas_extension = []

    def __init__(self):
        pass

    @classmethod
    def agregar_cartas_primera_jugada(cls, i, lista, cartas_mesa):
        """
        Agrega cartas a la mesa MANTENIENDO SEPARADAS las jugadas
        """
        # CORRECCIÓN: Cada jugada debe ser una lista separada
        if not cartas_mesa[i]:
            cartas_mesa[i] = []  # Inicializar como lista vacía si no existe
        
        # Crear una NUEVA lista para esta jugada específica
        nueva_jugada = []
        for x in lista:
            nueva_jugada.append(x)
        
        # Agregar la nueva jugada a las cartas del jugador
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
        Divide una jugada en grupos válidos (tríos y seguidillas)
        """
        grupos = []
        actual = []
        
        for carta in jugada:
            # Convertir a objeto Cartas si es string
            if isinstance(carta, str):
                valor, _, palo = carta.partition(" de ")
                carta_obj = Cartas(valor.strip(), palo.strip())
            else:
                carta_obj = carta
                
            if not actual:
                actual.append(carta_obj)
                continue
                
            primera = actual[0]
            
            # Verificar si es un trío (mismo número)
            if (str(carta_obj.numero) == str(primera.numero) or 
                str(carta_obj.numero).lower() == 'joker' or 
                str(primera.numero).lower() == 'joker'):
                actual.append(carta_obj)
            
            # Verificar si es una seguidilla (mismo palo y valores consecutivos)
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
            return False  # Ya está en la jugada

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
        Verifica si una carta puede reemplazar un joker en una seguidilla
        """
        seguidilla_cartas = []
        
        # Convertir todas las cartas a objetos Cartas
        for c in seguidilla:
            if isinstance(c, str):
                valor, _, palo = c.partition(" de ")
                seguidilla_cartas.append(Cartas(valor.strip(), palo.strip()))
            else:
                seguidilla_cartas.append(c)
        
        # Encontrar la posición del joker
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
        
        # Crear una copia reemplazando el joker
        seguidilla_reemplazada = seguidilla_cartas.copy()
        seguidilla_reemplazada[joker_pos] = carta
        
        # Obtener valores numéricos de las cartas no joker
        valores = []
        for c in seguidilla_reemplazada:
            if str(c.numero).lower() != 'joker':
                valores.append(c.valor_numerico())
        
        if len(valores) < 2:
            return False
        
        valores.sort()
        
        # Verificar si la secuencia es válida
        for i in range(len(valores) - 1):
            if valores[i + 1] - valores[i] != 1:
                return False
        
        return joker_pos

    @classmethod
    def obtener_todas_jugadas_numeradas(cls, cartas_mesa, jugadores):
        """Devuelve un diccionario con todas las jugadas numeradas"""
        jugadas_numeradas = {}
        contador = 1
        
        for i, jugadas_jugador in enumerate(cartas_mesa):
            if i < len(jugadores) and jugadas_jugador:
                jugador_obj = jugadores[i]
                
                # Iterar sobre CADA JUGADA del jugador
                for jugada_index, jugada in enumerate(jugadas_jugador):
                    if jugada:  # Solo si la jugada no está vacía
                        subgrupos = cls.dividir_en_grupos_validos(jugada)
                        
                        for subgrupo in subgrupos:
                            if len(subgrupo) >= 3:
                                # Determinar tipo
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
                                    continue  # Saltar si no es válida
                                
                                jugadas_numeradas[contador] = {
                                    'jugador_idx': i,
                                    'jugada_index': jugada_index,
                                    'jugador_nombre': jugador_obj.nombre_jugador,
                                    'jugador_numero': jugador_obj.nro_jugador,
                                    'subgrupo': subgrupo,
                                    'tipo': tipo,
                                    'jugada_original': jugada  # Guardar referencia a la jugada original
                                }
                                contador += 1
        
        return jugadas_numeradas

    @classmethod
    def extender_jugadas(cls, mano_actual, jugador, cartas_mesa, jugadores):
        """
        Permite extender jugadas existentes en la mesa de forma simplificada
        """

        print("\n--- EXTENDER JUGADAS ---")
        # Obtener todas las jugadas numeradas
        jugadas_numeradas = cls.obtener_todas_jugadas_numeradas(cartas_mesa, jugadores)
        
        if not jugadas_numeradas:
            print("No hay jugadas en la mesa para extender.")
            return False
        
        # Mostrar jugadas numeradas
        print("Jugadas en la mesa:")
        for num, info in jugadas_numeradas.items():
            print(f"({num}) {info['jugador_nombre']} - {info['tipo']}: {[str(c) for c in info['subgrupo']]}")
        
        # Mostrar cartas del jugador
        print(f"\nTus cartas:")
        for i, carta in enumerate(mano_actual, 1):
            print(f"{i}. {carta}")
        
        # Paso 1: Seleccionar jugada a extender
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
        
        # Paso 2: Mostrar cartas válidas para esta jugada
        cartas_validas = []
        
        for i, carta in enumerate(mano_actual):
            if isinstance(carta, str):
                valor, _, palo = carta.partition(" de ")
                carta_obj = Cartas(valor.strip(), palo.strip())
                mano_actual[i] = carta_obj  # Actualiza la carta en la mano
                carta = carta_obj

            if tipo_jugada == "trio":
                # Para tríos: misma número
                if str(carta.numero).lower() == str(jugada_seleccionada[0].numero).lower():
                    cartas_validas.append((i, carta, "agregar"))
                
                # Reemplazar joker en trío
                joker_pos = cls.puede_reemplazar_joker_trio(carta, jugada_seleccionada)
                if joker_pos != -1:
                    cartas_validas.append((i, carta, "reemplazar_joker", joker_pos))
            
            elif tipo_jugada == "seguidilla":
                # Para seguidillas: extender
                extension = cls.puede_extender_seguidilla(carta, jugada_seleccionada)
                if extension:
                    cartas_validas.append((i, carta, "extender", extension))
                
                # Reemplazar joker en seguidilla
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
            else:  # reemplazar_joker
                joker_pos = extra[0]
                print(f"{idx}. {carta} (reemplazar joker en posición {joker_pos+1})")
        
        # Paso 3: Seleccionar carta a usar
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
        
        # Paso 4: Realizar la acción
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
        
        else:  # reemplazar_joker
            joker_pos = extra[0]
            joker = jugada_modificada[joker_pos]
            jugada_modificada[joker_pos] = carta
            mano_actual.remove(carta)
            mano_actual.append(joker)
            print(f"Has reemplazado el joker con {carta}. El joker ha sido devuelto a tu mano.")
        
        # Paso 5: Actualizar la jugada en la mesa
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
        """
        Permite reemplazar una carta existente en una jugada
        """
        print("\n--- REEMPLAZAR CARTA EN JUGADA ---")
        
        # Obtener todas las jugadas numeradas
        jugadas_numeradas = cls.obtener_todas_jugadas_numeradas(cartas_mesa, jugadores)
        
        if not jugadas_numeradas:
            print("No hay jugadas en la mesa para modificar.")
            return False
        
        # Mostrar jugadas numeradas
        print("Jugadas en la mesa:")
        for num, info in jugadas_numeradas.items():
            print(f"({num}) {info['jugador_nombre']} - {info['tipo']}: {[str(c) for c in info['subgrupo']]}")
        
        # Paso 1: Seleccionar jugada a modificar
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
        
        # Paso 2: Seleccionar carta a reemplazar
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
        
        # Paso 3: Seleccionar carta nueva de la mano
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
        
        # Paso 4: Validar que el reemplazo mantenga la jugada válida
        jugada_modificada = jugada_seleccionada.copy()
        jugada_modificada[seleccion_carta_vieja - 1] = carta_nueva
        
        # Validar si la jugada modificada sigue siendo válida
        if not cls.es_jugada_valida(jugada_modificada, jugada_info['tipo']):
            print("El reemplazo haría que la jugada sea inválida.")
            return False
        
        # Paso 5: Realizar el reemplazo
        mano_actual.remove(carta_nueva)
        mano_actual.append(carta_vieja)  # La carta vieja vuelve a la mano
        
        # Actualizar la jugada en la mesa
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
        """
        Verifica si una jugada sigue siendo válida después de un reemplazo
        """
        if tipo == "trio":
            # Todos deben tener el mismo número (ignorando jokers)
            numeros = [str(c.numero).strip().lower() for c in jugada if str(c.numero).strip().lower() != 'joker']
            return len(set(numeros)) == 1 if numeros else True
        
        elif tipo == "seguidilla":
            # Mismo palo y valores consecutivos
            cartas_no_joker = [c for c in jugada if str(c.numero).lower() != 'joker']
            if not cartas_no_joker:
                return True
            
            # Mismo palo
            if not all(c.figura == cartas_no_joker[0].figura for c in cartas_no_joker):
                return False
            
            # Valores consecutivos
            valores = [c.valor_numerico() for c in cartas_no_joker]
            valores.sort()
            
            for i in range(len(valores) - 1):
                if valores[i + 1] - valores[i] != 1:
                    return False
            
            return True
        
        return False

    @classmethod
    def validar_jugada(cls, mano_actual, jugador, cartas_mesa, jugadores_primera_jugada, i):
        cls.trio.clear()
        cls.seguidilla.clear()
        
        if jugador not in jugadores_primera_jugada:
            print("primero seleccione las cartas para su trio")
            print("agregue las cartas que quiera, presione 1 para confirmar su trio, 2 para limpiar y 3 para salir")
            num_saltos = 0
            carta = None
            trio_valido = False
            seguidilla_valida = False
            
            # FASE 1: SELECCIÓN DEL TRÍO
            while carta != "1":
                mano_actual_a = [str(c) for c in mano_actual]
                mano_actual_a = [m.lower() for m in mano_actual_a]
                carta = input("seleccione su carta para el trio(recuerde presionar 1 para confirmar su trio): ").lower()
                
                if carta in mano_actual_a:
                    cls.trio.append(carta)
                    mano_actual_a.remove(carta)
                    cls.eliminar_carta(carta, mano_actual)
                elif carta == "1":
                    trioV = []
                    for x in cls.trio:
                        valor, _, palo = x.partition(" de ")
                        carta_obj = Cartas(valor, palo)
                        trioV.append(carta_obj)
                    
                    if len(trioV) < 3:
                        print("Debes seleccionar al menos tres cartas para formar un trío.")
                        cls.regresar_cartas(cls.trio, mano_actual)
                        cls.trio.clear()
                        continue
                    
                    numero_de_jokers = 0
                    for x, p in enumerate(trioV):
                        if p.numero == "joker" and numero_de_jokers < 1 and x != 0:
                            trioV[x].numero = trioV[0].numero
                            numero_de_jokers += 1
                        elif p.numero == "joker" and numero_de_jokers < 1 and x == 0:
                            trioV[x].numero = trioV[1].numero
                            numero_de_jokers += 1
                    
                    valores = [c.valor_numerico() for c in trioV]
                    if all(v == valores[0] for v in valores):
                        trioV_str = [str(c) for c in trioV]
                        print(f"Trío válido: {' - '.join(trioV_str)}")
                        trio_valido = True
                    else:
                        print("trío inválido")
                        cls.regresar_cartas(cls.trio, mano_actual)
                        cls.trio.clear()
                        continue
                elif carta == "2":
                    cls.regresar_cartas(cls.trio, mano_actual)
                    cls.trio.clear()
                    continue
                elif carta == "3":
                    cls.regresar_cartas(cls.trio, mano_actual)
                    cls.trio.clear()
                    return
                else:
                    print("la carta no esta :v")

            # FASE 2: SELECCIÓN DE LA SEGUIDILLA (SOLO SI EL TRÍO ES VÁLIDO)
            if trio_valido:
                print("ahora seleccione las cartas para su seguidilla")
                print("agregue las cartas que quiera, presione 1 para confirmar su seguidilla, 2 para limpiar y 3 para salir")
                
                carta = None
                while carta != "1":
                    mano_actual_a = [str(c) for c in mano_actual]
                    mano_actual_a = [m.lower() for m in mano_actual_a]
                    carta = input("seleccione su carta para la seguidilla(recuerde presionar 1 para confirmar): ").lower()
                    
                    if carta in mano_actual_a:
                        cls.seguidilla.append(carta)
                        mano_actual_a.remove(carta)
                        cls.eliminar_carta(carta, mano_actual)
                    elif carta == "1":
                        seguidillaV = []
                        for x in cls.seguidilla:
                            valor, _, palo = x.partition(" de ")
                            c = Cartas(valor, palo)
                            seguidillaV.append(c)
                        
                        if len(seguidillaV) < 4:
                            print("Debes seleccionar al menos cuatro cartas para formar una seguidilla.")
                            cls.regresar_cartas(cls.seguidilla, mano_actual)
                            cls.seguidilla.clear()
                            # También regresar el trío si la seguidilla falla
                            cls.regresar_cartas(cls.trio, mano_actual)
                            cls.trio.clear()
                            return
                        
                        valores = [c.valor_numerico() for c in seguidillaV]
                        valores = sorted(valores)
                        seguidilla_ordenada = sorted(seguidillaV, key=lambda c: c.valor_numerico())
                        
                        numero_de_jokers = 0
                        for x, p in enumerate(seguidilla_ordenada):
                            if p.numero == "joker" and numero_de_jokers < 2:
                                seguidilla_ordenada[x].figura = seguidilla_ordenada[2].figura
                                numero_de_jokers += 1
                        
                        if all(c.figura == seguidilla_ordenada[0].figura for c in seguidilla_ordenada):
                            seguidillaV_str = [str(c) for c in seguidillaV]
                            
                            if valores[0] != 0 and valores[1] != 0:
                                num_saltos = cls.salto(0, valores)
                                if num_saltos == 0:
                                    print(f"Seguidilla válida: {' - '.join(seguidillaV_str)}")
                                    seguidilla_valida = True
                                else:
                                    print("seguidilla invalida, tus cartas tienen que seguir una escalera como (1,2,3,4) sin saltos como (1,2,4,5)")
                                    cls.regresar_cartas(cls.seguidilla, mano_actual)
                                    cls.seguidilla.clear()
                                    cls.regresar_cartas(cls.trio, mano_actual)
                                    cls.trio.clear()
                                    return
                            elif valores[0] == 0 and valores[1] != 0:
                                salto_joker1 = cls.salto_joker(1, valores)
                                if salto_joker1 == 1:
                                    cls.jokers(seguidilla_ordenada, valores, 1)
                                    num_saltos = cls.salto(1, valores)
                                    if num_saltos == 1:
                                        print(f"Seguidilla válida: {' - '.join(seguidillaV_str)}")
                                        seguidilla_valida = True
                                    else:
                                        print("seguidilla invaliada, hay mas de un salto que tu joker no puede cubrir")
                                        cls.regresar_cartas(cls.seguidilla, mano_actual)
                                        cls.seguidilla.clear()
                                        cls.regresar_cartas(cls.trio, mano_actual)
                                        cls.trio.clear()
                                        return
                                elif salto_joker1 == 0:
                                    num_salto = cls.salto(1, valores)
                                    if num_salto != 0:
                                        print("seguidilla ivalida, hay mas de un salto que tu joker no puede cubrir")
                                        cls.regresar_cartas(cls.seguidilla, mano_actual)
                                        cls.seguidilla.clear()
                                        cls.regresar_cartas(cls.trio, mano_actual)
                                        cls.trio.clear()
                                        return
                                    elif num_salto == 0 and valores[-1] != 13 and valores[1] != 1:
                                        seguidilla_ordenada_str = [str(c) for c in seguidilla_ordenada]
                                        cls.opciones_joker(seguidilla_ordenada_str, "deseas colocar tu joker al principio o final de tu seguidilla?")
                                        print(f"Seguidilla válida: {' - '.join(seguidillaV_str)}")
                                        seguidilla_valida = True
                                    elif num_salto == 0 and valores[-1] == 13 and valores[1] != 1:
                                        print(f"Seguidilla válida: {' - '.join(seguidillaV_str)}")
                                        seguidilla_valida = True
                                    elif num_salto == 0 and valores[-1] != 13 and valores[1] == 1:
                                        seguidilla_ordenada_str = [str(c) for c in seguidilla_ordenada]
                                        cls.mover_joker(seguidilla_ordenada_str)
                                        print(f"Seguidilla válida: {' - '.join(seguidillaV_str)}")
                                        seguidilla_valida = True
                                    elif num_salto == 0 and valores[-1] == 13 and valores[1] == 1:
                                        print("seguidilla invalida, tienes mas de 13 cartas")
                                        cls.regresar_cartas(cls.seguidilla, mano_actual)
                                        cls.seguidilla.clear()
                                        cls.regresar_cartas(cls.trio, mano_actual)
                                        cls.trio.clear()
                                        return
                                else:
                                    print("seguidilla invalida, hay mas de un salto que tu joker no puede cubrir")
                                    cls.regresar_cartas(cls.seguidilla, mano_actual)
                                    cls.seguidilla.clear()
                                    cls.regresar_cartas(cls.trio, mano_actual)
                                    cls.trio.clear()
                                    return
                            elif valores[0] == 0 and valores[1] == 0:
                                salto_joker1 = cls.salto_joker(2, valores)
                                if salto_joker1 == 2:
                                    cls.jokers(seguidilla_ordenada, valores, 2)
                                    num_salto = cls.salto(2, valores)
                                    if num_salto == 2:
                                        print(f"Seguidilla válida: {' - '.join(seguidillaV_str)}")
                                        seguidilla_valida = True
                                    else:
                                        print("seguidilla invalida, hay mas de un salto que tu joker no puede cubrir")
                                        cls.regresar_cartas(cls.seguidilla, mano_actual)
                                        cls.seguidilla.clear()
                                        cls.regresar_cartas(cls.trio, mano_actual)
                                        cls.trio.clear()
                                        return
                                elif salto_joker1 == 1:
                                    cls.jokers(seguidilla_ordenada, valores, 1)
                                    num_salto = cls.salto(2, valores)
                                    if num_salto == 1 and valores[-1] != 13 and valores[2] != 1:
                                        seguidilla_ordenada_str = [str(c) for c in seguidilla_ordenada]
                                        cls.opciones_joker(seguidilla_ordenada_str, "deseas colocar tu joker restante al principio o final de tu seguidilla?")
                                        print(f"Seguidilla válida: {' - '.join(seguidillaV_str)}")
                                        seguidilla_valida = True
                                    elif num_salto == 1 and valores[-1] == 13 and valores[2] != 1:
                                        print(f"Seguidilla válida: {' - '.join(seguidillaV_str)}")
                                        seguidilla_valida = True
                                    elif num_salto == 1 and valores[-1] != 13 and valores[2] == 1:
                                        seguidilla_ordenada_str = [str(c) for c in seguidilla_ordenada]
                                        cls.mover_joker(seguidilla_ordenada_str)
                                        print(f"Seguidilla válida: {' - '.join(seguidillaV_str)}")
                                        seguidilla_valida = True
                                    elif num_salto == 1 and valores[-1] == 13 and valores[2] == 1:
                                        print("seguidilla invalida, tienes mas 13 cartas")
                                        cls.regresar_cartas(cls.seguidilla, mano_actual)
                                        cls.seguidilla.clear()
                                        cls.regresar_cartas(cls.trio, mano_actual)
                                        cls.trio.clear()
                                        return
                                    else:
                                        print("seguidilla invalida, hay mas de un salto que tu joker no puede cubrir")
                                        cls.regresar_cartas(cls.seguidilla, mano_actual)
                                        cls.seguidilla.clear()
                                        cls.regresar_cartas(cls.trio, mano_actual)
                                        cls.trio.clear()
                                        return
                                elif salto_joker1 == 0:
                                    num_salto = cls.salto(2, valores)
                                    if num_salto == 0 and valores[-1] != 13 and valores[2] != 1:
                                        seguidilla_ordenada_str = [str(c) for c in seguidilla_ordenada]
                                        cls.mover_joker(seguidilla_ordenada_str)
                                        print(f"Seguidilla válida: {' - '.join(seguidillaV_str)}")
                                        seguidilla_valida = True
                                    else:
                                        print("segudilla invalida, no puedes tener dos joker seguidos")
                                        cls.regresar_cartas(cls.seguidilla, mano_actual)
                                        cls.seguidilla.clear()
                                        cls.regresar_cartas(cls.trio, mano_actual)
                                        cls.trio.clear()
                                        return
                                else:
                                    print("seguidilla invalida, hay mas de un salto que tu joker no puede cubrir")
                                    cls.regresar_cartas(cls.seguidilla, mano_actual)
                                    cls.seguidilla.clear()
                                    cls.regresar_cartas(cls.trio, mano_actual)
                                    cls.trio.clear()
                                    return
                        else:
                            print("seguidilla invalida, todas tus cartas tienen que ser del mismo palo")
                            cls.regresar_cartas(cls.seguidilla, mano_actual)
                            cls.seguidilla.clear()
                            cls.regresar_cartas(cls.trio, mano_actual)
                            cls.trio.clear()
                            return
                    elif carta == "2":
                        cls.regresar_cartas(cls.seguidilla, mano_actual)
                        cls.seguidilla.clear()
                        continue
                    elif carta == "3":
                        cls.regresar_cartas(cls.trio, mano_actual)
                        cls.trio.clear()
                        cls.regresar_cartas(cls.seguidilla, mano_actual)
                        cls.seguidilla.clear()
                        return
                    else:
                        print("la carta no esta :v")

            # FASE 3: CONFIRMACIÓN FINAL (SOLO SI AMBAS SON VÁLIDAS)
            if trio_valido and seguidilla_valida:
                cls.agregar_cartas_primera_jugada(i, trioV, cartas_mesa)
                cls.agregar_cartas_primera_jugada(i, seguidilla_ordenada, cartas_mesa)
                cls.seguidilla.clear()
                cls.trio.clear()
                jugadores_primera_jugada.append(jugador)
                print("¡Primera jugada válida completada!")
                print(f"Trío: {[str(c) for c in trioV]}")
                print(f"Seguidilla: {[str(c) for c in seguidilla_ordenada]}")
            else:
                print("La primera jugada debe incluir un trío válido Y una seguidilla válida.")
                if trio_valido:
                    cls.regresar_cartas(cls.trio, mano_actual)
                    cls.trio.clear()
                if seguidilla_valida:
                    cls.regresar_cartas(cls.seguidilla, mano_actual)
                    cls.seguidilla.clear()
        else:
            print("ya hiciste la primera jugada")


    # conquiste este codigo :vvvvv
