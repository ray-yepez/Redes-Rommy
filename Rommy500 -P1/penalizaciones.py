import time

def ejecutar_penalizacion(jugador, resultado_validador):
    """
    Solo marca el castigo en el objeto jugador y genera el paquete.
    NO envía nada por red, NO toca la mano del jugador.
    """
    mensaje_error = resultado_validador.get("mensaje", "Jugada ilegal detectada.")
    
    # Extraemos las cartas como texto respetando los símbolos (J♣, Q♦, etc.)
    mano_texto = [str(c) for c in jugador.playerHand]
    duracion = 10 
    
    # 1. Marcamos el bloqueo temporal en el objeto
    jugador.penalizado_hasta = time.time() + duracion
    
    # 2. Construimos el "chisme" (paquete) para que el que llamó a la función decida qué hacer
    paquete_red = {
        "type": "REVELAR_FALLO",
        "infractor_id": jugador.playerId,
        "nombre": jugador.playerName,
        "cards": mano_texto,
        "duration": duracion,
        "mensaje": mensaje_error
    }
    
    print(f">>> [SISTEMA] Penalización generada para {jugador.playerName}.")
    return paquete_red

def esta_penalizado(jugador):
    """
    Consulta si el jugador está bajo los efectos del castigo.
    """
    if not hasattr(jugador, 'penalizado_hasta'):
        return False
    return time.time() < jugador.penalizado_hasta