import random
from Turn import refillDeck, drawCard
def electionPhase(players, deck):
    print("Fase de Elección")
    availableCards = deck.drawInElectionPhase(len(players))  #Sacamos las Cartas para la fase de elección
    random.shuffle(availableCards)  #Mezclamos las Cartas que se van a elegir para que no estén en el mismo orden

    elections = {}  #Creamos un diccionario para almacenar las elecciones de los jugadores antes de la ronda
    for player, Card in zip(players, availableCards):
        elections[player] = Card  #Asignamos la Carta elegida a cada jugador
        print(f"{player} ha elegido la Carta: {Card}") #Indicamos qué Carta fue elegida

    #Con lo siguiente, se determinará el turno de la ronda para los jugadores dependiendo del valor numérico de la Carta que eligió cada uno
    order = sorted(
        elections.items(),
        key = lambda item: Card.values.index(item[1].value),
        reverse = True
    )
    playerOrder = [player for player, _ in order]  #Obtenemos el orden de los jugadores según sus elecciones
    print("Orden de los jugadores:", playerOrder)
    return playerOrder
    #Devolvemos el orden de los jugadores para la ronda


def startRound(playersInOrder, screen): # Incluimos el atributo "screen" para la interfaz gráfica
    from Round import Round  #Importamos la clase Round aquí para evitar importaciones circulares
    roundInstance = Round(playersInOrder)  #Creamos una instancia de la clase Round
    roundInstance.initDeck()  #Inicializamos el mazo
    roundInstance.dealCards()  #Repartimos las cartas a los jugadores
    roundInstance.discardsAndTableDeck()  #Colocamos la primera carta en el montón de descartes
    roundInstance.showInitialState()  #Mostramos el estado inicial de la ronda

    #playerOrder = electionPhase(players, roundInstance.deck, screen, clockObj)  #Obtenemos el orden de los jugadores para la ronda

    return roundInstance, playersInOrder  #Devolvemos la instancia de la ronda y el orden de los jugadores

def mainGameLoop(screen, playersInOrder, deck, discard_pile, nombre="", zona_cartas=None):
    """
    Lógica principal del juego:
      - Gestiona turnos.
      - Ofrece la carta del descarte a otros jugadores.
      - Controla compra, bajada, inserción y descarte.
    Devuelve el estado completo para depuración.
    players es un parámetro que va a recibir el array de los jugadores en orden después de la
    ronda de elección.
    """
    sourceAction = nombre
    roundObject = startRound(playersInOrder, screen)[0]
    # Orden de jugadores fijo
    turn_order = playersInOrder[:]
    #Aquí debería de leerse el orden de los jugadores según la fase de elección
    #turn_order.sort(key=lambda p: 0 if p.name == "Louis" else 1)

    current_index = 0
    game_running = True

    # Estado inicial
    state = {
        "players": [],
        "deck_remaining": len(deck),
        "discard_top": discard_pile[-1] if discard_pile else None,
        "turn_order": [p.playerName for p in turn_order],
    }

    while game_running:
        current_player = turn_order[current_index]
        current_player.isHand = True
        print(f"\nTurno de {current_player.playerName}")

        # --- 1. Tomar carta ---
        # El jugador decide si tomar del descarte o del mazo.
        if sourceAction == "discard" and discard_pile:
            drawCard(current_player, roundObject, fromDiscards=True, indexDiscards=roundObject.discards.index(discard_pile[-1]))
        elif sourceAction == "deck" and deck:
            drawCard(current_player, roundObject)

        # --- 2. Bajarse ---
        # El jugador decide si se baja o no.
        #la decision vendrá desde la interfaz. Cambiaré el input para que sea un parámetro del método
        #y reciba la acción del botón de bajarse si se pulsa. Sino, queda como None
        if sourceAction == "Bajarse":
            current_player.getOff(zona_cartas[0], zona_cartas[1])

        # --- 3. Insertar carta ---
        #decision = input("¿Desea insertar una carta en una jugada existente? (s/n): ").strip().lower()
        #if sourceAction == "Insertar":
        #Aquí el método me debería recibir el nombre del jugador al que se le va a insertar la carta
            #target_player_name = input("¿A qué jugador desea insertarle la carta?: ")
            #target_player = next((p for p in playersInOrder if p.playerName == target_player_name), None)
            #if target_player and target_player.playMade:
                # Suponiendo que la interfaz selecciona la carta
                #card_index = int(input("Índice de la carta en mano: "))
                #card = current_player.playerHand.pop(card_index)
                #target_play_index = int(input("Índice de la jugada del jugador objetivo: "))
                #current_player.insertCard(target_player, target_play_index, card)

        # --- 4. Descartar carta ---
        #card_index = int(input("Índice de la carta a descartar: "))
        #card_descartada = current_player.playerHand.pop(card_index)
        #discard_pile.append(card_descartada)
        #print(f"{current_player.playerName} descarta {card_descartada}.")
        #current_player.isHand = False

        # --- 5. Ofrecer carta a los demás jugadores ---
        for p in turn_order:
            if not p.isHand and p != current_player:
                respuesta = p.playerBuy
                if respuesta:
                    p.buyCard(roundObject)
                    break

        # --- Estado de depuración ---
        state["players"] = [{
            "name": p.playerName,
            "hand": [str(c) for c in p.playerHand],
            "down": getattr(p, "downHand", []),
            "isHand": p.isHand
        } for p in playersInOrder]
        state["deck_remaining"] = len(deck)
        state["discard_top"] = discard_pile[-1] if discard_pile else None

        # --- Siguiente jugador ---
        current_index = (current_index + 1) % len(turn_order)

        # Condición de salida temporal
        if len(deck) == 0:
            refillDeck(roundObject)

    return state
