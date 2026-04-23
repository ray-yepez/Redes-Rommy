import random #nos permitirá mezclar las cartas
from Card import Card

class Deck:
    def __init__(self, decks = 1):
        self.cards = []
        for _ in range(decks):
            for type in Card.types:
                for value in Card.values:
                    self.cards.append(Card(value, type))
            #Agregamos 2 Joker
            self.cards.append(Card("Joker", "", joker=True))
            self.cards.append(Card("Joker", "", joker=True))
        
    def shuffleCards(self):
        random.shuffle(self.cards) #Barajamos las cartas del mazo

    def drawCard(self):
        if len(self.cards) == 0:
            raise ValueError("No hay cards en el Mazo") #Si no hay cartas en el mazo, lanzamos una excepción
        else:
            return self.cards.pop() #Sacamos la última carta del mazo y la devolvemos
        
        #NOTA: La última carta del mazo es la que estará al tope del mazo después de barajar, por lo que al sacar una carta se obtiene siempre la que esté en el tope del mazo

    def drawInElectionPhase(self, numOfPlayers): #Sacar cartas en la fase de elección
        selectedCards = []
        valueSelected = set()

        while len(selectedCards) < numOfPlayers and len(self.cards) > 0:
            card = self.drawCard()
            if not card.joker and card.value not in valueSelected: #Esto se traduce a: "Si la carta no es un Joker y su valor no ha sido seleccionado aún..."
                
                selectedCards.append(card) #Añadimos la carta a la lista de cartas seleccionadas
                
                valueSelected.add(card.value)  #Evita seleccionar cartas con el mismo valor, para así evitar empates en la fase de elección
        
        return selectedCards #Devolvemos las cartas seleccionadas, que serán las que se mostrarán a los jugadores en la fase de elección