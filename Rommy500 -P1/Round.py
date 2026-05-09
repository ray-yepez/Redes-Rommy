from Deck import Deck
class Round:
    #idCounter = 0

    def __init__(self, players):
        self.players = players
        self.hands = {player.playerId: [] for player in players} #Creamos un diccionario que contendrá las manos de cada jugador, donde la clave es el nombre del jugador y el valor es una lista vacía que contendrá las cartas de ese jugador
        self.deck = None #Inicializamos el mazo como None, ya que aún no lo hemos creado
        self.tableDeck = [] #Esto será el mazo que estará en la mesa, donde se colocarán las cartas boca abajo que los jugadores podrán tomar
        self.discards = [] #Es el montón de descartes
        self.pile = []  # NUEVO PARA PRUEBA
        self.refillCounter = 0 #Contador para llevar la cuenta de cuántas veces se ha rellenado el mazo
        #self.id = Round.idCounter
        #Round.idCounter += 1

    #def __eq__(self, other):
    #    return self.id == other.id

    #def __hash__(self):
    #    return hash(self.id)

    def initDeck(self):
        numOfPlayers = len(self.players) #Mostrará el número de jugadores
        numOfDecks = 2 #Por defecto, se usará 2 mazos
        if numOfPlayers >= 4 and numOfPlayers <= 6:
            numOfDecks = 3
        elif numOfPlayers > 6:  #Estos condicionales son para utilizar mazos de acuerdo a la cantidad de jugadores
            numOfDecks = 4
        self.deck = Deck(numOfDecks) #Creamos el mazo total con el número de mazos correspondiente
        self.deck.shuffleCards() #Barajamos las cartas del mazo (de nuevo, por si acaso)
    
    def dealCards(self):
        for _ in range(10):
            for player in self.players:
                if not player.isSpectator:  # Solo repartir si NO es espectador
                    card = self.deck.drawCard()
                    self.hands[player.playerId].append(card)
                    player.playerHand.append(card) #Añadimos la carta a la mano del jugador correspondiente
    
    def discardsAndTableDeck(self):
        self.pile = self.deck.cards[:] #Copiamos las cartas del mazo a la pila
        self.deck.cards.clear() #Limpiamos el mazo para que no tenga cartas
        if self.pile:
            self.discards.append(self.pile.pop()) #Sacamos la última carta de la pila y la añadimos al montón de descartes
    
    def showInitialState(self):
        print("ESTADO INICIAL DE LA RONDA")
        print(f"\nPrimer descarte: {self.discards[-1]}") #Mostramos la primera carta del montón de descartes
        print(f"Cartas restantes en el montón: {len(self.pile)}") #Se muestra la cantidad de cartas restantes en el montón, sin que estas sean reveladas (seguirán boca abajo)
    

