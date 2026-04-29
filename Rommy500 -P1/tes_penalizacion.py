import time
# Importamos tus funciones corregidas
from penalizaciones import ejecutar_penalizacion, esta_penalizado

# 1. SIMULAMOS UN JUGADOR (Mock)
class JugadorPrueba:
    def __init__(self):
        self.playerId = 1
        self.playerName = "Prototipo_UCLA"
        self.playerHand = ["4-Corazones", "J-Picas", "Joker"]
        self.penalizado_hasta = 0 # Atributo inicial

# 2. SIMULAMOS EL RESULTADO DEL VALIDADOR
resultado_falso = {
    "valida": False,
    "mensaje": "Intentaste bajar un trío con cartas de distinto valor."
}

# --- INICIO DE LA PRUEBA ---
def correr_test():
    mi_jugador = JugadorPrueba()

    print("--- INICIO DE PRUEBA DE PENALIZACIÓN ---")
    print(f"¿Está penalizado al inicio?: {esta_penalizado(mi_jugador)}")

    # Ejecutamos tu función y recibimos el paquete
    paquete = ejecutar_penalizacion(mi_jugador, resultado_falso)

    print("\n--- RESULTADOS ---")
    print(f"Paquete generado para red: {paquete}")
    print(f"¿Está penalizado ahora?: {esta_penalizado(mi_jugador)}")

    # Probamos el tiempo de espera
    print("\nEsperando 4 segundos para ver si el castigo expira...")
    time.sleep(4)

    if not esta_penalizado(mi_jugador):
        print("¿Sigue penalizado tras la espera?: False")
        print("\n¡TEST EXITOSO! La lógica funciona correctamente.")
    else:
        print("Error: El jugador sigue penalizado.")
    
    print("--- FIN DE LA PRUEBA ---")

if __name__ == "__main__":
    correr_test()