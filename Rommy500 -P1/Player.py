import pygame
from Round import Round
from Turn import drawCard
from Card import Card
from itertools import combinations
class Player:

    def __init__(self, id, name):
        self.playerId = id
        self.playerName = name
        self.playerPoints = 0 #Nos contiene los puntos del jugador a lo largo de la partida
        self.isHand = False #Esto nos indica si el jugador es mano o no, o en otras palabras, si está en turno
        self.playerTurn = False #Este turno se utilizará para determinar si el jugador está en su turno para comprar la carta
        self.playerHand = [] #Lista que contendrá las cartas del jugador.
        self.playerCardsPos = {} #Atributo experimental, para conocer la posición de cada carta lógica.
        self.playerCardsSelect = [] #Atributo experimental, para guardar las cartas selecc. para un movimiento.
        self.playerCardsToEx = []   # Atrib. exp., para guardar cartas para intercambiar posiciones.
        self.playMade = [] #Este array nos guarda la jugada hecha al momento de bajarse. Esta se actualiza en getOff()
        self.jugadas_bajadas = []
        #self.cardTakend = []
        self.downHand = False #Este atributo nos indica si el jugador ya se bajó o no, mostrando True o False respectivamente
        self.playerBuy = False #Este atributo nos indica si el jugador decidió comprar la carta o no
        self.playerPass = False #Atrib. experimental, para saber si el jugador en turno pasó de la carta descartada.
        self.winner = False #Nos permitirá saber si el jugador fue el ganador
        self.cardDrawn = False #Nos permitirá saber si el jugador tomó una carta en su turno (definido por isHand)
        self.connected = False #Nos permitirá saber si el jugador está conectado al servidor o no
        self.carta_elegida = False  #NUEVO PARA PRUEBA
        self.discarded = False
        self.canDiscard = True # Atrib. que permite bloquear o desbloquear el descarte (para compra de cartas)

    def __str__(self):
        return f"({self.playerId}, {self.playerName})"
    
    def __repr__(self):
        return self.__str__()

    # Mét. para permitir que el jugador seleccione cartas para jugar.
    def chooseCard(self, clickPos):
        
        # Para cada carta en la mano del jugador, verificamos si se hace click en el rectángulo asociado
        # a una carta específica y si dicha carta ha sido previamente seleccionada.
        # Si la carta no está en la lista de seleccionadas, la incluimos; si resulta que está entre las
        # seleccionadas y se vuelve a hacer click en ella, la eliminamos de la lista.
        # NOTA: Con la inclusión de un ID a cada carta este proceso se simplifica, ya que las coincidencias
        #       sólo pueden darse entre cartas con un mismo valor para todos sus atributos.
        for card in self.playerHand:
            if self.playerCardsPos[card].collidepoint(clickPos) and card not in self.playerCardsSelect:
                print(f"Carta marcada: {card}{card.id}")
                self.playerCardsSelect.append(card)
            elif self.playerCardsPos[card].collidepoint(clickPos) and card in self.playerCardsSelect:
                print(f"Carta desmarcada: {card}{card.id}")
                self.playerCardsSelect.remove(card)

    # Mét. para permitir al jugador intercambiar el lugar de sus cartas para que pueda ordenarlas.
    # Trabaja casi igual que chooseCard(), pero almacena dos cartas a lo mucho.
    def exchangeCard(self, clickPos):
        for card in self.playerHand:
            if self.playerCardsPos[card].collidepoint(clickPos) and card not in self.playerCardsToEx:
                print(f"Carta marcada para intercambiar: {card}{card.id}")
                self.playerCardsToEx.append(card)
            elif self.playerCardsPos[card].collidepoint(clickPos) and card in self.playerCardsToEx:
                print(f"Carta desmarcada para intercambiar: {card}{card.id}")
                self.playerCardsToEx.remove(card)

        # Si el jugador marca dos cartas para intercambiar (con el click derecho)...
        if len(self.playerCardsToEx) == 2:
                
                # Tomamos la posición de cada carta en la mano del jugador.
                IndexFirstCard = self.playerHand.index(self.playerCardsToEx[0])
                IndexSecondCard = self.playerHand.index(self.playerCardsToEx[1])

                # Tomamos las cartas asociadas a cada posición.
                firstCard = self.playerHand[IndexFirstCard]
                secondCard = self.playerHand[IndexSecondCard]

                # Intercambiamos posiciones en la mano del jugador.
                self.playerHand[IndexFirstCard] = secondCard
                self.playerHand[IndexSecondCard] = firstCard

                # Limpiamos la lista de intercambio para reiniciar el proceso.
                self.playerCardsToEx.clear()    
                
    #empiezan cambios por aqui
    '''def canExtendTrio(self, card, plays):
        """
        Verifica si la carta puede extender algún trío en la lista de jugadas 'plays'.
        Incluye validación interna de si cada jugada es un trío válido.
        similar a la logica de ins
        """
        for play in plays:
            # Validación interna: verificar si 'play' es un trío válido
            if len(play) < 3:
                continue
            noJokers = [c.value for c in play if not c.joker]
            if len(set(noJokers)) != 1:  # No todos los valores no-Joker son iguales
                continue
            
            # Verificar si la carta puede extender este trío
            common_value = noJokers[0]
            if card.joker:
                jokersInTrio = sum(1 for c in play if c.joker)
                if jokersInTrio < 1:
                    return True
            else:
                if card.value == common_value:
                    return True
        return False
        
    def canExtendStraight(self, card, plays):
        """
        Verifica si la carta puede extender alguna seguidilla en la lista de jugadas 'plays'.
        Incluye validación interna de si cada jugada es una seguidilla válida.
        """
        valueToRank = {"A": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
                       "8": 8, "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13}
        
        def rank(c, highAs=False):
            if getattr(c, "joker", False):
                return -1
            if c.value == "A" and highAs:
                return 14
            return valueToRank.get(c.value, -1)
        
        for play in plays:
            # Validación interna: verificar si 'play' es una seguidilla válida
            if len(play) < 4:
                continue
            noJokerSuit = [c.type for c in play if not c.joker]
            if len(set(noJokerSuit)) != 1:  # Todos los palos no-Joker deben ser iguales
                continue
            
            # Verificar secuencia con ranks
            common_suit = noJokerSuit[0]
            isValidStraight = False
            for highAs in (False, True):
                ranks = [rank(c, highAs) for c in play if rank(c, highAs) != -1]
                if len(ranks) < len(play) - 1:  # Demasiados Jokers
                    continue
                ranks.sort()
                if all(ranks[i] + 1 == ranks[i+1] for i in range(len(ranks)-1)):
                    isValidStraight = True
                    break
            if not isValidStraight:
                continue
            
            # Verificar si la carta puede extender esta seguidilla
            if card.joker:
                suit = common_suit
            else:
                if card.type != common_suit:
                    continue
            
            for highAs in (False, True):
                sorted_straight = sorted([c for c in play if rank(c, highAs) != -1], key=lambda c: rank(c, highAs))
                if not sorted_straight:
                    continue
                firstRank = rank(sorted_straight[0], highAs)
                lastRank = rank(sorted_straight[-1], highAs)
                cardRank = rank(card, highAs)
                
                if cardRank == firstRank - 1 or cardRank == lastRank + 1:
                    return True
        return False'''
        
    #Mét. para descartar una carta de la playerHand del jugador. Sólo se ejecuta si el jugador tiene una única
    #carta seleccionada previamente.
    def discardCard(self, selectedDiscards, round):#def discardCard(self, selectedDiscards, round, otherPlayers): asi para lo de ana
        """
        Modificado para verificar si alguna carta seleccionada puede extender una jugada en la mesa.
        - otherPlayers: Lista de otros jugadores (excluyendo al actual) para acceder a sus jugadas bajadas.
        """
        # Verificar si alguna carta puede extender jugadas propias
        '''for card in selectedDiscards:
            if self.downHand and self.playMade and not card.joker:  # Solo si el jugador se ha bajado
                if self.canExtendTrio(card, self.playMade):
                    print(f"No se puede descartar {card}: puede extender tu trio.")
                    return None
                if self.canExtendStraight(card, self.playMade) and not card.joker:
                    print(f"No se puede descartar {card}: puede extender tu seguidilla.")
                    return None
        # Verificar si alguna carta puede extender una jugada bajada de otros jugadores
        for card in selectedDiscards:
            for player in otherPlayers:
                
                if player.downHand and player.playMade and not card.joker:  # Solo si se ha bajado y tiene jugadas
                    if self.canExtendTrio(card, player.playMade):
                        print(f"No se puede descartar {card}: puede extender un trío en la jugada de {player.playerName}.")
                        return None
                    elif self.canExtendStraight(card, player.playMade) and not card.joker:
                        print(f"No se puede descartar {card}: puede extender una seguidilla en la jugada de {player.playerName}.")
                        return None'''
        # hasta aqui los cambios :))))
        if len(selectedDiscards) == 2 and self.isHand and self.cardDrawn and self.downHand:

            #Si seleccionaron dos y la primera es un Joker, se retorna una lista con ambas cartas.
            if selectedDiscards[0].joker:

                cardDiscarded = selectedDiscards[1]
                jokerDiscarded = selectedDiscards[0]
                self.playerHand.remove(cardDiscarded)
                self.playerHand.remove(jokerDiscarded)
                selectedDiscards.remove(cardDiscarded)
                selectedDiscards.remove(jokerDiscarded)
                selectedDiscards = []
                round.discards.append(jokerDiscarded)
                round.discards.append(cardDiscarded)
                self.discarded = True
                # self.isHand = False

                return [jokerDiscarded, cardDiscarded]
            #Si seleccionó dos y la segunda es un Joker, volvemos a retornar ambas cartas.
            elif selectedDiscards[1].joker:

                jokerDiscarded = selectedDiscards[1]
                cardDiscarded = selectedDiscards[0]
                self.playerHand.remove(jokerDiscarded)
                self.playerHand.remove(cardDiscarded)
                selectedDiscards.remove(cardDiscarded)
                selectedDiscards.remove(jokerDiscarded)
                selectedDiscards = []
                round.discards.append(jokerDiscarded)
                round.discards.append(cardDiscarded)
                self.discarded = True
                # self.isHand = False

                return [cardDiscarded, jokerDiscarded]
        #Si el jugador sólo seleccionó una carta para descartar, retornamos dicha carta.
        elif len(selectedDiscards) == 1 and not selectedDiscards[0].joker and self.isHand and self.cardDrawn:

            cardDiscarded = selectedDiscards[0]
            try:
                self.playerHand.remove(cardDiscarded)
                round.discards.append(cardDiscarded)
                selectedDiscards.remove(cardDiscarded)
                selectedDiscards = []
                self.discarded = True
                # self.isHand = False

                return [cardDiscarded]
            except ValueError:
                print("La carta que intenta descartar no pertenece a la mano del jugador")
                return []
        #Si el jugador no seleccionó ninguna carta, retornamos None.
        else:
            if len(selectedDiscards) == 2 and (not any(c.joker for c in selectedDiscards) or all(c.joker for c in selectedDiscards)) and self.downHand:
                return '001'#print("Solo puedes bajar 2 cartas si *una* de ellas es un Joker")
            elif len(selectedDiscards) == 1 and selectedDiscards[0].joker:
                return '002'#print("Para poder descartar un joker, debes descartar también otra carta normal")
            elif len(selectedDiscards)==2 and ( any(c.joker for c in selectedDiscards) or all(c.joker for c in selectedDiscards)) and not self.downHand:
                return '003' #print("No puedes quemar el mono sino te has bajado")
            elif not self.cardDrawn:
                return '004' #print("Debes tomar una carta antes de descartar")
            else:
                return []
    def isValidTrioF(self,lista):
        """
        Valida si una lista específica de cartas (propuesta) es un grupo válido.
        Un grupo válido (trío, cuarteto, etc.) debe:
        1. Tener 3 o más cartas.
        2. Tener un máximo de 1 joker.
        3. Todas las cartas normales deben tener el mismo valor.
        """
        
        # 1. Verificar el tamaño (mínimo 3 cartas)
        # Tu código original buscaba de 3 en adelante.
        if not lista or len(lista) < 3:
            print(f"Error: La propuesta debe tener al menos 3 cartas. (Tiene {len(lista)})")
            return False

        # 2. Separar jokers y cartas normales de la propuesta
        jokers_en_propuesta = []
        cartas_normales = []
        for card in lista:
            # Asumiendo que tu objeto Card tiene un booleano 'joker'
            if card.joker:
                jokers_en_propuesta.append(card)
            else:
                cartas_normales.append(card)

        # 3. Verificar la regla del Joker (máximo 1)
        if len(jokers_en_propuesta) > 1:
            print(f"Error: La propuesta tiene más de 1 joker. (Tiene {len(jokers_en_propuesta)})")
            return False

        # 4. Verificar los valores de las cartas normales
        # Si hay 0 o 1 carta normal, es válido (ej: [Joker, 5, 5])
        # Si hay 2 o más cartas normales, TODAS deben ser iguales.
        if len(cartas_normales) >= 2:
            # Tomamos el valor de la primera carta normal como referencia
            # Asumiendo que tu objeto Card tiene un atributo 'value'
            valor_referencia = cartas_normales[0].value
            
            # Iteramos sobre el RESTO de cartas normales
            for i in range(1, len(cartas_normales)):
                if cartas_normales[i].value != valor_referencia:
                    print(f"Error: Las cartas normales no tienen el mismo valor.")
                    print(f"Se esperaba '{valor_referencia}', pero se encontró '{cartas_normales[i].value}'")
                    return False
                    
        # 5. Caso especial: ¿Propuesta de solo Jokers?
        # Ej: [Joker, Joker, Joker]. Esto fallaría en el paso 3 (len > 1).
        if not cartas_normales and len(jokers_en_propuesta) >= 3:
             # Esto solo puede pasar si la regla de jokers es > 1, pero
             # nuestro paso 3 ya lo habría bloqueado. Es una doble seguridad.
             print("Error: No se pueden formar grupos solo de Jokers (o la regla de max 1 joker lo impide).")
             return False

        # Si llegamos hasta aquí, la propuesta es válida.
        print(f"¡Propuesta válida!: {[str(c) for c in lista]}")
        return True
    
    def isValidStraightF(self, cards):
        """
        Verifica si una lista de objetos Card forma una seguidilla válida (Rummy).
        NO requiere que las cartas vengan ordenadas.
        Retorna True o False.
        """
        if not cards or len(cards) < 4:
            return False

        # 1. Separar Jokers y Cartas normales
        jokers = [c for c in cards if c.joker]
        non_jokers = [c for c in cards if not c.joker]
        
        num_jokers = len(jokers)

        # Regla: Máximo 2 Jokers
        if num_jokers > 2:
            return False

        # Si todo son jokers no es válido sin referencia de palo
        if not non_jokers:
            return False 

        # 2. Verificar Palo (Suit)
        first_suit = non_jokers[0].type
        if any(c.type != first_suit for c in non_jokers):
            return False

        # Función auxiliar interna para verificar la secuencia numérica
        def check_sequence(values_list):
            # Ordenamos los valores numéricos de menor a mayor
            sorted_values = sorted(values_list)
            
            # Verificamos duplicados numéricos exactos
            if len(sorted_values) != len(set(sorted_values)):
                return False
            
            gaps_needed = 0
            
            # Recorremos la lista ordenada comparando pares
            for i in range(len(sorted_values) - 1):
                current_val = sorted_values[i]
                next_val = sorted_values[i+1]
                
                diff = next_val - current_val
                
                # Si diff es 1, son consecutivas (perfecto)
                # Si diff es 2, falta 1 carta (necesita 1 joker)
                # Si diff es > 2, faltan 2+ cartas (necesita 2+ jokers seguidos -> invalido)
                
                missing_cards = diff - 1
                
                if missing_cards > 1: 
                    return False 
                
                gaps_needed += missing_cards

            # Si la cantidad de jokers que tenemos cubre los huecos
            return gaps_needed <= num_jokers

        # 3. Construcción de listas de valores (Low, High, Mixed)
        
        values_low = []   # Todos los Ases valen 1
        values_high = []  # Todos los Ases valen 14
        values_mixed = [] # Un As vale 1, el otro 14 (Solo si hay 2+ Ases)
        
        # Contamos cuantos Ases hay para saber si activar el modo mixto
        ace_count = sum(1 for c in non_jokers if c.value == "A")
        aces_processed = 0

        for c in non_jokers:
            val = c.numValue() # Asumimos 2-13. Si tu numValue da 1 para As, no importa, lo sobreescribimos abajo.
            
            if c.value == "A":
                # Llenamos listas básicas
                values_low.append(1)
                values_high.append(14)
                
                # Llenamos lista mixta (si aplica)
                if ace_count >= 2:
                    aces_processed += 1
                    # El primer As que procesamos será el 1, el segundo será el 14
                    if aces_processed == 1:
                        values_mixed.append(1)
                    else:
                        values_mixed.append(14)
            else:
                values_low.append(val)
                values_high.append(val)
                if ace_count >= 2:
                    values_mixed.append(val)

        # 4. Verificaciones
        
        # Caso 1: As Bajo (A, 2, 3...)
        if check_sequence(values_low):
            return True
        
        # Caso 2: As Alto (...Q, K, A)
        if check_sequence(values_high):
            return True
            
        # Caso 3: As Mixto / Vuelta al mundo (A, 2 ... K, A)
        if ace_count >= 2:
            if check_sequence(values_mixed):
                return True              
        return False
    def isValidStraightFJoker(self, cards):
        """
        Verifica si una lista de objetos Card forma una seguidilla válida (Rummy).
        REQUIERE que las cartas vengan en el orden correcto.
        Retorna True o False.
        """
        if not cards or len(cards) < 4:
            return False

        # 1. Separar Jokers y Cartas normales (manteniendo el índice)
        non_jokers_info = [(i, c) for i, c in enumerate(cards) if not c.joker]
        num_jokers = len(cards) - len(non_jokers_info)

        # Regla: Máximo 2 Jokers y debe haber al menos una carta normal
        if num_jokers > 2 or not non_jokers_info:
            return False
        # --- NUEVA VALIDACIÓN: No permitir Jokers consecutivos ---
        for i in range(len(cards) - 1):
            if cards[i].joker and cards[i+1].joker:
                return False
        # 2. Verificar que todas las cartas normales sean del mismo palo (Suit)
        first_suit = non_jokers_info[0][1].type
        if any(c.type != first_suit for i, c in non_jokers_info):
            return False

        # 3. Función auxiliar para validar linealidad según el valor asignado al As
        def check_ordered_sequence(ace_mode):
            """
            ace_mode: 
            'low' (todos los A=1), 
            'high' (todos los A=14), 
            'mixed' (primer A=1, segundo A=14)
            """
            temp_values = []
            aces_seen = 0
            
            for i, card in enumerate(cards):
                if card.joker:
                    temp_values.append(None)
                elif card.value == "A":
                    aces_seen += 1
                    if ace_mode == 'low': temp_values.append(1)
                    elif ace_mode == 'high': temp_values.append(14)
                    elif ace_mode == 'mixed':
                        temp_values.append(1 if aces_seen == 1 else 14)
                else:
                    temp_values.append(card.numValue())

            # Buscamos la primera carta que no sea Joker para usarla como pivote
            pivot_idx = -1
            pivot_val = -1
            for i, val in enumerate(temp_values):
                if val is not None:
                    pivot_idx, pivot_val = i, val
                    break
            
            # Validar la secuencia
            for i, val in enumerate(temp_values):
                # El valor que "debería" tener la carta en esta posición
                expected_val = pivot_val + (i - pivot_idx)
                
                # 1. Si el valor esperado se sale del rango de una baraja (1-14)
                if expected_val < 1 or expected_val > 14:
                    return False
                
                # 2. Si es una carta normal, debe coincidir exactamente con el esperado
                if val is not None and val != expected_val:
                    return False
                    
            return True

        # 4. Probar los 3 escenarios posibles de interpretación de los Ases
        # Caso A: Ases como 1 (A-2-3-4)
        if check_ordered_sequence('low'): return True
        
        # Caso B: Ases como 14 (J-Q-K-A)
        if check_ordered_sequence('high'): return True
        
        # Caso C: Mixto (A-2...K-A) - Solo si hay al menos 2 Ases
        ace_count = sum(1 for _, c in non_jokers_info if c.value == "A")
        if ace_count >= 2 and check_ordered_sequence('mixed'):
            return True

        return False
    def sortedStraight(self, cards):
        """
        Valida y ordena una seguidilla (Straight).
        Soporta:
        - As Bajo (A, 2, 3...)
        - As Alto (...Q, K, A)
        - As Mixto/Vuelta al mundo (A, 2, ... K, A) si hay 2 Ases.
        """
        if not cards or len(cards) < 4:
            return False

        jokers = [c for c in cards if c.joker]
        naturals = [c for c in cards if not c.joker]

        if len(jokers) > 2: return False
        if not naturals: return False 

        # 1. Validar Palo
        first_suit = naturals[0].type
        if any(c.type != first_suit for c in naturals):
            return False

        # --- Función para construir la secuencia ---
        def try_build(mode):
            # modes: "LOW" (A=1), "HIGH" (A=14), "MIXED" (Un A=1, otro A=14)
            
            temp_naturals = []
            aces_seen = 0
            
            for c in naturals:
                val = c.numValue()
                if c.value == "A":
                    aces_seen += 1
                    if mode == "LOW":
                        val = 1
                    elif mode == "HIGH":
                        val = 14
                    elif mode == "MIXED":
                        # El primer As que veamos será 1, el segundo será 14
                        # Si hay más de 2 Ases, serán duplicados y fallará luego (correcto)
                        val = 1 if aces_seen == 1 else 14
                
                temp_naturals.append((val, c))
            
            # Ordenamos por valor numérico
            temp_naturals.sort(key=lambda x: x[0])
            
            # Verificar duplicados numéricos
            # Esto evita tener dos "5" o dos Ases asignados al mismo valor
            for i in range(len(temp_naturals) - 1):
                if temp_naturals[i][0] == temp_naturals[i+1][0]: 
                    return None

            built_sequence = []
            available_jokers = list(jokers)
            
            # Construcción de huecos internos
            curr_rank, curr_card = temp_naturals[0]
            built_sequence.append(curr_card)
            
            for i in range(len(temp_naturals) - 1):
                next_rank, next_card = temp_naturals[i+1]
                diff = next_rank - curr_rank
                
                if diff == 1:
                    built_sequence.append(next_card)
                elif diff == 2:
                    if not available_jokers: return None
                    built_sequence.append(available_jokers.pop(0))
                    built_sequence.append(next_card)
                else:
                    return None # Hueco > 1 carta requiere > 1 joker consecutivo
                
                curr_rank = next_rank

            # Gestión de extremos (Punta y Cola) para jokers sobrantes
            
            # Helper para obtener rango lógico ya asignado en la lista
            def get_rank(c, index_in_seq):
                if c.joker: return None
                if c.value == "A":
                    # Si estamos en modo MIXED, deducimos por posición
                    if mode == "MIXED":
                         # Si el As está al principio es 1, si está al final es 14
                         # Pero cuidado con el sort. Mejor miramos el vecino.
                         pass
                    return 14 if mode == "HIGH" else 1
                return c.numValue()
            
            # Nota: En modo MIXED con el sort hecho, el As(1) está al principio 
            # y el As(14) al final. Los numValue() simples funcionan para los límites.

           # 1. Rellenar COLA (Derecha)
            while available_jokers:
                if not built_sequence: break
                last_card = built_sequence[-1]
                
                # REGLA: No poner Joker si el último ya es Joker
                if last_card.joker: break 
                
                last_val = 14 if (last_card.value == "A" and (mode == "HIGH" or mode == "MIXED")) else last_card.numValue()
                
                if last_val < 14:
                    built_sequence.append(available_jokers.pop(0))
                else:
                    break

            # 2. Rellenar PUNTA (Izquierda)
            while available_jokers:
                if not built_sequence: break
                first_card = built_sequence[0]
                
                # REGLA: No poner Joker si el primero ya es Joker
                if first_card.joker: break
                
                first_val = 1 if (first_card.value == "A" and (mode == "LOW" or mode == "MIXED")) else first_card.numValue()
                
                if first_val > 1:
                    # Seguridad adicional para el IndexError
                    if available_jokers:
                        built_sequence.insert(0, available_jokers.pop(0))
                    else:
                        break
                else:
                    return None # Bloqueado por As
                    
            return built_sequence

        # --- Ejecución de Modos ---
        candidates = []

        # 1. Probar As Bajo
        s1 = try_build("LOW")
        if s1: candidates.append(s1)

        # 2. Probar As Alto
        s2 = try_build("HIGH")
        if s2: candidates.append(s2)
        
        # 3. Probar Mixto (Solo si hay más de 1 As)
        ace_count = sum(1 for c in naturals if c.value == "A")
        if ace_count >= 2:
            s3 = try_build("MIXED")
            if s3: candidates.append(s3)

        if not candidates:
            return False

        # --- Selección del Mejor Candidato ---
        best = candidates[0]
        for seq in candidates:
            if seq == cards: return True # Orden original perfecto
            
            # Preferencia: Joker al final
            if seq[-1].joker and not best[-1].joker:
                best = seq
            # Preferencia secundaria: Secuencia más larga (en caso de logicas raras)
            elif len(seq) > len(best):
                best = seq
                
        return best

    # --- EN Player.py ---

    def checkJokerSwap(self, straight):
        """
        Verifica si un Joker en el extremo de una seguidilla puede moverse al otro extremo
        manteniendo la validez visual y lógica.
        IMPIDE: Poner Joker antes de As bajo (ej: [Joker, A, 2]) o después de As alto.
        """
        if not straight or len(straight) < 3:
            return False
        
        # 1. Identificar si hay Joker en los extremos
        start_is_joker = getattr(straight[0], "joker", False)
        end_is_joker = getattr(straight[-1], "joker", False)
        # NUEVA REGLA: Si ambos extremos son Joker, el movimiento resultaría en
        # Jokers consecutivos (ej: [J, 5, 6, J] -> [5, 6, J, J]). 
        # Retornamos False para impedirlo.
        if start_is_joker and end_is_joker:
            return False
        
        if not start_is_joker and not end_is_joker:
            return False
            
        # 2. Simular el cambio en una lista temporal
        temp_straight = straight.copy()
        
        if start_is_joker:
            # Mover de INICIO -> FINAL (ej: [Joker, 2, 3] -> [2, 3, Joker])
            joker = temp_straight.pop(0)
            temp_straight.append(joker)
            
            # VALIDACIÓN FRONTERA SUPERIOR:
            # La carta anterior al nuevo joker (penúltima)
            prev_card = temp_straight[-2] 
            # Si termina en As (ej: Q, K, A), no podemos poner Joker después (no existe 15)
            if not getattr(prev_card, "joker", False) and prev_card.value == "A":
                return False

        elif end_is_joker:
            # Mover de FINAL -> INICIO (ej: [As, 2, Joker] -> [Joker, As, 2])
            joker = temp_straight.pop(-1)
            temp_straight.insert(0, joker)
            
            # VALIDACIÓN FRONTERA INFERIOR:
            # La carta siguiente al nuevo joker (segunda posición)
            neighbor = temp_straight[1]
            # Si empieza en As (ej: A, 2, 3), no podemos poner Joker antes (no existe 0)
            if not getattr(neighbor, "joker", False) and neighbor.value == "A":
                return False
            
        # 3. Validación matemática estándar
        return self.isValidStraightF(temp_straight)

    def executeJokerSwap(self, playIndex, straight_ref):
        """
        Realiza el movimiento físico del Joker de un extremo al otro en la memoria del jugador.
        """
        if playIndex < 0 or playIndex >= len(self.playMade):
            return

        # Obtener la referencia a la lista real dentro de playMade
        target_play = self.playMade[playIndex]
        
        # Si la jugada es un diccionario (ej: {'straight': [...]}), extraemos la lista
        if isinstance(target_play, dict):
            if "straight" in target_play:
                cards = target_play["straight"]
            else:
                return # No es una seguidilla
        else:
            cards = target_play # Es una lista directa

        # Verificar extremos y mover
        if not cards: return
        
        start_is_joker = getattr(cards[0], "joker", False)
        end_is_joker = getattr(cards[-1], "joker", False)

        if start_is_joker:
            joker = cards.pop(0)
            cards.append(joker)
        elif end_is_joker:
            joker = cards.pop(-1)
            cards.insert(0, joker)
        
        # Actualizar también jugadas_bajadas para que se refleje visualmente de inmediato
        if hasattr(self, "jugadas_bajadas") and playIndex < len(self.jugadas_bajadas):
            # Forzamos una copia visual actualizada
            self.jugadas_bajadas[playIndex] = list(cards)

    def insertCard(self, targetPlayer, targetPlayIndex, cardToInsert, position=None, jokerIndex = None):
        # 1) Validaciones básicas
        if not self.downHand:
            return False
        
        if not self.isHand:
            print(f"No es el turno de {self.playerName}")
            # Opcional: retornar False o permitirlo si es compra
        if not self.cardDrawn:
            return False
        if cardToInsert not in self.playerHand:
            return False

        if targetPlayIndex < 0 or targetPlayIndex >= len(targetPlayer.playMade):
            return False

        targetPlay = targetPlayer.playMade[targetPlayIndex]
        
        # Helper para extraer la lista de cartas (sea dict o list)
        def _extract_list(play):
            if isinstance(play, dict):
                return play.get("straight") or play.get("trio") or [], "straight" if "straight" in play else "trio"
            # Lógica robusta: Si las dos primeras cartas normales tienen mismo valor, es trío
            naturals = [c for c in play if not getattr(c, "joker", False)]
            if len(naturals) >= 2:
                # Si todas las cartas naturales tienen el mismo valor, es un trío
                if all(c.value == naturals[0].value for c in naturals):
                    return play, "trio"
            return play, "straight"
        
        cartas_lista, tipo_jugada = _extract_list(targetPlay)
        temporal_list = cartas_lista.copy()

        # 2) Simular la operación
        if position is None: # Sustitución de Joker
            # CAMBIO AQUÍ: Si recibimos un índice específico, lo usamos. 
            # Si no, buscamos el primero como respaldo (fallback).
            if jokerIndex is not None:
                joker_idx = jokerIndex
            else:
                joker_idx = next((i for i, c in enumerate(temporal_list) if getattr(c, "joker", False)), None)
                
            if joker_idx is None: return False
            temporal_list[joker_idx] = cardToInsert
        elif position == "start":
            temporal_list.insert(0, cardToInsert)
        elif position == "end":
            temporal_list.append(cardToInsert)

        # 3) VALIDACIÓN UNIFICADA
        # Usamos las funciones robustas de la clase
        if tipo_jugada == "trio":
            valido = self.isValidTrioF(temporal_list)
        else:
            valido = self.isValidStraightF(temporal_list)

        if not valido:
            print(f"Movimiento inválido lógicamente para {tipo_jugada}")
            return False

        # 4) Aplicar cambios reales y devolver Joker si fue sustitución
        if position is None:
            replaced_joker = cartas_lista[joker_idx]
            cartas_lista[joker_idx] = cardToInsert
            self.playerHand.remove(cardToInsert)
            self.playerHand.append(replaced_joker)
        else:
            if position == "start":
                cartas_lista.insert(0, cardToInsert)
            else:
                cartas_lista.append(cardToInsert)
            self.playerHand.remove(cardToInsert)
        
        # IMPORTANTE: Re-ordenar visualmente si es una escalera
        '''if tipo_jugada == "straight":
            nueva_ordenada = self.sortedStraight(cartas_lista)
            if nueva_ordenada and isinstance(nueva_ordenada, list):
                cartas_lista[:] = nueva_ordenada'''

        return True

    # Mét. para cambiar el valor de "playerPass" para saber si, en un turno dado, pasó de la carta del
    # descarte y agarró del mazo de disponibles. Servirá para la compra de cartas de los siguientes
    # jugadores.
    def passCard(self):
        self.playerPass = not self.playerPass

    def buyCard(self, round):
        """Este método debe recibir como parámetro el objeto de la ronda actual.
        Eso se hará desde el ciclo principal del juego.
        Este método se utilizará en el botón de comprar carta, que solo se mostrará
        cuando isHand es False"""
        discardedCard = round.discards.pop()
        #Si el jugador decidió comprar la carta del descarte, se le entrega dicha carta y además se le da una del mazo como castigo
        if self.playerBuy and not self.isHand:
            extraCard = round.pile.pop()  #Sacamos la última carta del mazo
            round.hands[self.playerId].append(extraCard)  #Añadimos la carta a la mano del jugador
            # self.playerHand.append(discardedCard)
            round.hands[self.playerId].append(discardedCard)
            self.playerHand = round.hands[self.playerId]
            print(f"El jugador {self.playerName} compró la carta {discardedCard} y recibió una carta: {extraCard}, del mazo como castigo")
            return [discardedCard, extraCard]
            # return round
        else:
            print(f"El jugador {self.playerName} no compró la carta del descarte")
            return None
        
    def calculatePoints(self):
        """Esto añade los puntos al jugador. Se debe llamar este método al finalizar cada ronda.
        Los puntos van de la siguiente manera:
        -Cartas del 2 al 9: 5 puntos cada una
        -Cartas 10, J, Q, K: 10 puntos cada una
        -Cartas de Ases: 20 puntos
        -Cartas Joker: 25 puntos"""
        totalPoints = 0
        for card in self.playerHand:
            if card.joker:
                totalPoints += 25
            elif card.value in ["K", "Q", "J", "10"]:
                totalPoints += 10
            elif card.value == "A":
                totalPoints += 20
            else:
                totalPoints += 5
        self.playerPoints += totalPoints
        return totalPoints
