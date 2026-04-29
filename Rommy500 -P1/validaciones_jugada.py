# NUEVO CODIGO - INSERTAR AQUI

VALORES_ORDEN = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
    "8": 8, "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14
}


def _es_joker(carta):
    if isinstance(carta, dict):
        return bool(carta.get("joker", False))
    return bool(getattr(carta, "joker", False))


def _obtener_valor(carta):
    if isinstance(carta, dict):
        return carta.get("valor", carta.get("value"))
    return getattr(carta, "value", getattr(carta, "valor", None))


def _obtener_palo(carta):
    if isinstance(carta, dict):
        return carta.get("palo", carta.get("type"))
    return getattr(carta, "type", getattr(carta, "palo", None))


def _valor_numerico(valor, as_alto=True):
    if valor == "A":
        return 14 if as_alto else 1
    return VALORES_ORDEN.get(valor)


def _valor_base_trio(cartas):
    for carta in cartas:
        if not _es_joker(carta):
            return _obtener_valor(carta)
    return None


def _normalizar_ronda(ronda_actual):
    if isinstance(ronda_actual, int):
        return ronda_actual

    mapa = {
        "roundone": 1,
        "roundtwo": 2,
        "roundthree": 3,
        "roundfour": 4,
        "ronda1": 1,
        "ronda2": 2,
        "ronda3": 3,
        "ronda4": 4,
    }
    return mapa.get(str(ronda_actual).lower())


def es_trio(cartas):
    """
    Valida un trio:
    - exactamente 3 cartas
    - maximo 1 joker
    - las cartas no-joker deben tener el mismo valor
    """
    if not cartas or len(cartas) != 3:
        return False

    jokers = [c for c in cartas if _es_joker(c)]
    naturales = [c for c in cartas if not _es_joker(c)]

    if len(jokers) > 1:
        return False

    if len(naturales) < 2:
        return False

    valor_base = _obtener_valor(naturales[0])
    return all(_obtener_valor(c) == valor_base for c in naturales)


def _es_seguidilla_con_modo(cartas, as_alto):
    jokers = [c for c in cartas if _es_joker(c)]
    naturales = [c for c in cartas if not _es_joker(c)]

    if not naturales:
        return False

    palos = [_obtener_palo(c) for c in naturales]
    if len(set(palos)) != 1:
        return False

    valores = [_valor_numerico(_obtener_valor(c), as_alto=as_alto) for c in naturales]
    if any(v is None for v in valores):
        return False

    valores.sort()

    if len(valores) != len(set(valores)):
        return False

    huecos = 0
    for i in range(len(valores) - 1):
        diferencia = valores[i + 1] - valores[i]
        if diferencia <= 0:
            return False
        huecos += diferencia - 1

    span_total = valores[-1] - valores[0] + 1

    if huecos > len(jokers):
        return False

    if span_total > 4:
        return False

    return len(naturales) + len(jokers) == 4


def es_seguidilla(cartas):
    """
    Valida una seguidilla:
    - exactamente 4 cartas
    - mismo palo en las cartas no-joker
    - consecutivas
    - permite jokers si el proyecto ya los usa
    """
    if not cartas or len(cartas) != 4:
        return False

    return _es_seguidilla_con_modo(cartas, as_alto=False) or _es_seguidilla_con_modo(cartas, as_alto=True)


def validar_jugada(cartas, tipo_esperado=None, ronda_actual=None):
    """
    Valida una sola jugada.
    Retorna:
    {
        "valida": bool,
        "tipo": "trio" | "seguidilla" | None,
        "mensaje": str
    }
    """
    if not cartas:
        return {
            "valida": False,
            "tipo": None,
            "mensaje": "La zona de juego esta vacia."
        }

    if tipo_esperado == "trio":
        es_valida = validar_jugada_avanzada_por_tipo(cartas, "trio")
        return {
            "valida": es_valida,
            "tipo": "trio",
            "mensaje": "" if es_valida else "La combinacion no cumple la regla de trio."
        }

    if tipo_esperado == "seguidilla":
        es_valida = validar_jugada_avanzada_por_tipo(cartas, "seguidilla")
        return {
            "valida": es_valida,
            "tipo": "seguidilla",
            "mensaje": "" if es_valida else "La combinacion no cumple la regla de seguidilla."
        }

    if validar_jugada_avanzada_por_tipo(cartas, "trio"):
        return {
            "valida": True,
            "tipo": "trio",
            "mensaje": ""
        }

    if validar_jugada_avanzada_por_tipo(cartas, "seguidilla"):
        return {
            "valida": True,
            "tipo": "seguidilla",
            "mensaje": ""
        }

    return {
        "valida": False,
        "tipo": None,
        "mensaje": "La combinacion no corresponde ni a un trio ni a una seguidilla valida."
    }


def validar_bajada_por_ronda(zonas, ronda_actual):
    """
    Valida todas las zonas necesarias para la ronda actual.
    Retorna:
    {
        "valida": bool,
        "mensaje": str,
        "detalle": list
    }
    """
    ronda = _normalizar_ronda(ronda_actual)

    reglas = {
        1: ["trio", "seguidilla"],
        2: ["seguidilla", "seguidilla"],
        3: ["trio", "trio", "trio"],
        4: ["trio", "trio", "seguidilla"],
    }

    if ronda not in reglas:
        return {
            "valida": False,
            "mensaje": "La ronda actual no es valida.",
            "detalle": []
        }

    patrones = reglas[ronda]
    detalle = []

    if len(zonas) < len(patrones):
        return {
            "valida": False,
            "mensaje": "No existen suficientes zonas para validar la bajada.",
            "detalle": []
        }

    for indice, tipo_esperado in enumerate(patrones):
        resultado = validar_jugada(zonas[indice], tipo_esperado=tipo_esperado, ronda_actual=ronda)
        detalle.append(resultado)

        if not resultado["valida"]:
            nombre = f"Zona {indice + 1}"
            return {
                "valida": False,
                "mensaje": f"{nombre}: {resultado['mensaje']}",
                "detalle": detalle
            }

    if ronda in (3, 4):
        valores_trio = []
        for indice, tipo_esperado in enumerate(patrones):
            if tipo_esperado == "trio":
                valores_trio.append(_valor_base_trio(zonas[indice]))

        valores_trio = [v for v in valores_trio if v is not None]
        if len(valores_trio) != len(set(valores_trio)):
            return {
                "valida": False,
                "mensaje": "No puedes bajar dos trios del mismo valor en esta ronda.",
                "detalle": detalle
            }

    return {
        "valida": True,
        "mensaje": "Jugada valida.",
        "detalle": detalle
    }


def resolver_campo_accion(zonas, ronda_actual):
    """
    Punto unico de entrada para el campo de accion.
    El jugador coloca cartas aqui y solo si pasa la validacion se autoriza la bajada.
    """
    return validar_bajada_por_ronda(zonas, ronda_actual)


# NUEVO CODIGO - INSERTAR AQUI
def validar_jugada_flexible(cartas):
    """
    Detecta automaticamente el tipo de jugada sin importar el campo visual.
    Retorna:
    - "trio" si las cartas forman un trio valido.
    - "seguidilla" si las cartas forman una seguidilla valida.
    - None si no forman ninguna jugada valida.
    """
    if es_trio(cartas):
        return "trio"

    if es_seguidilla(cartas):
        return "seguidilla"

    return None


# NUEVO CODIGO - INSERTAR AQUI
def adaptar_zonas_flexibles(zonas, ronda_actual):
    """
    Capa intermedia para convertir los campos en libres inteligentes.
    No elimina validaciones existentes: solo reordena internamente las zonas
    para que el flujo actual pueda seguir validando como ya lo hacia.
    """
    ronda = _normalizar_ronda(ronda_actual)

    reglas = {
        1: ["trio", "seguidilla"],
        2: ["seguidilla", "seguidilla"],
        3: ["trio", "trio", "trio"],
        4: ["trio", "trio", "seguidilla"],
    }

    if ronda not in reglas:
        return {
            "valida": False,
            "mensaje": "La ronda actual no es valida.",
            "zonas_adaptadas": zonas,
            "tipos_detectados": []
        }

    patrones_requeridos = reglas[ronda]

    if len(zonas) < len(patrones_requeridos):
        return {
            "valida": False,
            "mensaje": "No existen suficientes zonas para validar la bajada.",
            "zonas_adaptadas": zonas,
            "tipos_detectados": []
        }

    jugadas_detectadas = []
    for indice in range(len(patrones_requeridos)):
        tipo_detectado = validar_jugada_avanzada(zonas[indice])

        if tipo_detectado is None:
            return {
                "valida": False,
                "mensaje": f"Zona {indice + 1}: no es trio ni seguidilla valida.",
                "zonas_adaptadas": zonas,
                "tipos_detectados": []
            }

        jugadas_detectadas.append({
            "tipo": tipo_detectado,
            "cartas": zonas[indice]
        })

    zonas_ordenadas = []
    pendientes = jugadas_detectadas[:]

    for tipo_requerido in patrones_requeridos:
        indice_encontrado = next(
            (i for i, jugada in enumerate(pendientes) if jugada["tipo"] == tipo_requerido),
            None
        )

        if indice_encontrado is None:
            return {
                "valida": False,
                "mensaje": "Las jugadas son validas, pero no cumplen los requisitos de esta ronda.",
                "zonas_adaptadas": zonas,
                "tipos_detectados": [j["tipo"] for j in jugadas_detectadas]
            }

        zonas_ordenadas.append(pendientes.pop(indice_encontrado)["cartas"])

    zonas_adaptadas = list(zonas)
    for indice, cartas in enumerate(zonas_ordenadas):
        zonas_adaptadas[indice] = cartas

    return {
        "valida": True,
        "mensaje": "Jugada flexible valida.",
        "zonas_adaptadas": zonas_adaptadas,
        "tipos_detectados": [j["tipo"] for j in jugadas_detectadas]
    }


# NUEVO CODIGO - INSERTAR AQUI
def hay_jokers_consecutivos(cartas):
    """
    Valida la regla avanzada de seguidillas:
    no puede haber dos jokers seguidos en el orden colocado por el jugador.
    """
    for indice in range(len(cartas) - 1):
        if _es_joker(cartas[indice]) and _es_joker(cartas[indice + 1]):
            return True
    return False


# NUEVO CODIGO - INSERTAR AQUI
def validar_trio_con_joker(cartas):
    """
    Extension segura para trios:
    mantiene la validacion base de es_trio y refuerza maximo 1 Joker.
    """
    if not cartas:
        return False

    if len([carta for carta in cartas if _es_joker(carta)]) > 1:
        return False

    return es_trio(cartas)


# NUEVO CODIGO - INSERTAR AQUI
def _validar_seguidilla_extendida_con_modo(cartas, as_alto):
    jokers = [carta for carta in cartas if _es_joker(carta)]
    naturales = [carta for carta in cartas if not _es_joker(carta)]

    if len(cartas) < 4:
        return False

    if hay_jokers_consecutivos(cartas):
        return False

    if not naturales:
        return False

    palos = [_obtener_palo(carta) for carta in naturales]
    if len(set(palos)) != 1:
        return False

    valores = [_valor_numerico(_obtener_valor(carta), as_alto=as_alto) for carta in naturales]
    if any(valor is None for valor in valores):
        return False

    valores.sort()

    if len(valores) != len(set(valores)):
        return False

    huecos_necesarios = 0
    for indice in range(len(valores) - 1):
        diferencia = valores[indice + 1] - valores[indice]

        if diferencia <= 0:
            return False

        huecos_necesarios += diferencia - 1

    return huecos_necesarios <= len(jokers)


# NUEVO CODIGO - INSERTAR AQUI
def validar_seguidilla_extendida(cartas):
    """
    Extension segura para seguidillas:
    - acepta 4 o mas cartas
    - mantiene mismo palo
    - permite multiples jokers
    - rechaza jokers consecutivos
    - usa es_seguidilla como base para conservar lo que ya funcionaba
    """
    if es_seguidilla(cartas):
        return not hay_jokers_consecutivos(cartas)

    return (
        _validar_seguidilla_extendida_con_modo(cartas, as_alto=False)
        or _validar_seguidilla_extendida_con_modo(cartas, as_alto=True)
    )


# NUEVO CODIGO - INSERTAR AQUI
def validar_jugada_avanzada(cartas):
    """
    Wrapper avanzado:
    primero intenta usar la deteccion flexible existente y luego aplica
    las nuevas reglas de Joker y seguidillas extendidas.
    """
    tipo_base = validar_jugada_flexible(cartas)

    if tipo_base == "trio" and validar_trio_con_joker(cartas):
        return "trio"

    if tipo_base == "seguidilla" and validar_seguidilla_extendida(cartas):
        return "seguidilla"

    if validar_trio_con_joker(cartas):
        return "trio"

    if validar_seguidilla_extendida(cartas):
        return "seguidilla"

    return None


# NUEVO CODIGO - INSERTAR AQUI
def validar_jugada_avanzada_por_tipo(cartas, tipo_esperado):
    """
    Complemento para integrarse con validaciones actuales sin eliminarlas.
    """
    tipo_detectado = validar_jugada_avanzada(cartas)
    return tipo_detectado == tipo_esperado


# NUEVO CODIGO - INSERTAR AQUI
def preparar_seguidilla_extendida(cartas):
    """
    Devuelve una copia segura de la seguidilla avanzada para guardar en mesa
    cuando el ordenador anterior no puede manejar mas de 2 Jokers.
    """
    if validar_seguidilla_extendida(cartas):
        return list(cartas)
    return False
