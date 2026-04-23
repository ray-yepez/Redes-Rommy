class Card:
    idCounter = 0 #Contador para asignar un ID único a cada Carta
    values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"] #Son los valores de cada Carta
    types = ["♠", "♥", "♦", "♣"] #Indica el palo de dicha Carta

    def __init__(self, value, type, joker=False): #Inicializamos el constructor con el valor, palo e indicamos si es Joker o no (por defecto se dice que no lo es)
        self.value = value
        self.type = type
        self.joker = joker
        self.id = Card.idCounter #Asignamos un ID único a la Carta, que es el valor del contador de ID
        Card.idCounter += 1 #Aumentamos el contador de ID cada vez que se crea una nueva Carta
        
    def __str__(self):        
        if self.joker:
            return f"Joker" #Si la Carta es un Joker, se imprime la cadena de texto "Joker" para identificarla en lugar de colocar su valor y palo
        else:
            return f"{self.value}{self.type}" #Si no es un Joker, se imprime el value y el palo de la Carta
        
    def __eq__(self, other):
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
    
    def __repr__(self):
        return self.__str__()

        
    def numValue(self): #Devuelve el valor numérico de la Carta, donde 2 es el más bajo y A es el más alto
        if self.joker:
            return None #Los Jokers no tienen value numérico
        return Card.values.index(self.value) + 2 #Los valores comienzan en 2, ya que el 2 es la Carta de menor valor
