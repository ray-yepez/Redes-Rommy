from Deck import Deck
def drawCard(player, roundPlayed, fromDiscards = False):
    print(f"drawCard called! Discards size: {len(roundPlayed.discards)}")
    print(f"CARTAS DEL DESCARTE: {[str(c) for c in roundPlayed.discards]}")
    if fromDiscards: #Si se indica que se quiere sacar una carta del montón de descartes y se proporciona un índice válido
        card = roundPlayed.discards.pop()  #Sacamos la carta del montón de descartes
        roundPlayed.hands[player.playerId].append(card)  #Añadimos la carta tomada a la mano del jugador
        player.cardDrawn = True
        return card
    else:
        if len(roundPlayed.pile) == 0:
            refillDeck(roundPlayed)
        card = roundPlayed.pile.pop()  #Sacamos la última carta del mazo
        roundPlayed.hands[player.playerId].append(card)  #Añadimos la carta a la mano del jugador
        player.playerPass = True
        player.cardDrawn = True
        return card

def discardCard(player, roundPlayed, card):
    roundPlayed.hands[player.playerId].remove(card)  #Quitamos la carta de la mano del jugador
    card.discarded_by = player.playerId #Marcamos quién descartó la carta
    roundPlayed.discards.append(card)  #Añadimos la carta al montón de descartes

def refillDeck(roundPlayed):
    print(f"---------------------------------------------------REFILL DECK CALLED! Pile size: {len(roundPlayed.pile)}, Discards size: {len(roundPlayed.discards)}")
    if len(roundPlayed.pile) == 0 and len(roundPlayed.discards) == 1:
        roundPlayed.deck = Deck()
        roundPlayed.deck.shuffleCards()
        roundPlayed.pile = roundPlayed.deck.cards[:]
        roundPlayed.deck.cards.clear()
        # roundPlayed.discards.append(roundPlayed.pile.pop())
        print("--------------------------------------------------SE CREO UN NUEVO MAZO EN ESTA VAINAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA!")
    elif len(roundPlayed.pile) == 0 and len(roundPlayed.discards) > 1:  #Si el mazo se queda sin cartas, sacamos las cartas del montón de descartes y las ponemos en el mazo
        roundPlayed.pile = roundPlayed.discards[:-1]
        lastCard = roundPlayed.discards[-1]  #Guardamos la última carta del montón de descartes
        roundPlayed.discards = [lastCard] #roundPlayed.discards[-1:]  #Dejamos la última carta del montón de descartes como la única carta en el montón de descartes
        print("SOLO SE CICLÓ EL MAZO CON LAS CARTAS QUE SE QUEMAROOOOOOOOOOOOOOOOOOOOOOOOON!")
        if roundPlayed.refillCounter % 3 == 0:
            newDeck = Deck()
            newDeck.shuffleCards()
            roundPlayed.pile.extend(newDeck.cards)
            print("SE AÑADIÓ UN NUEVO MAZO AL PILA PORQUE SE HABÍA CICLADO TRES VECEEEEEEEEEEEEEEEEEEEEEEEEEEEES!")
        roundPlayed.refillCounter += 1