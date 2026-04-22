"""Módulo interno para validación de jugadas (trio, seguidillas, extensiones)"""

import copy

class ValidadoresMixin:
    """Mixin con métodos para validar jugadas del juego Rummy"""
    
    def quema_del_mono(self, id_jugador, carta):
        """Verifica si se descartó un joker (quema del mono)
        
        Retorna: (bool, dict) - Tupla con (True si es joker, mensaje a enviar o None)
        """
        if carta["numero"] == "Joker":
            print("si se llego hasta aqui es que se descarto un joker")
            return (True, {"type": "quema_del_mono"})
        else:
            return (False, None)
    
    def salto_joker(self, rango, valores):
        """Cuenta cuántos saltos de 2 hay (para jokers)"""
        saltos = 0
        for i in range(rango, len(valores) - 1):
            if valores[i + 1] - valores[i] == 2:
                saltos += 1
        return saltos

    def salto(self, rango, valores):
        """Cuenta cuántos saltos hay en la secuencia"""
        saltos = 0
        for i in range(rango, len(valores) - 1):
            if valores[i + 1] - valores[i] != 1:
                saltos += 1
        return saltos

    def validar_trio(self, cartas):
        """Valida si un conjunto de cartas forma un trío válido"""
        cart = copy.deepcopy(cartas)
        if len(cart) < 3:
            return False                
        numero_de_jokers = 0
        for x, p in enumerate(cart):
            if p["numero"] == "Joker" and numero_de_jokers < 1 and x != 0:
                cart[x]["numero"] = cart[0]["numero"]
                numero_de_jokers += 1
            elif p["numero"] == "Joker" and numero_de_jokers < 1 and x == 0:
                cart[x]["numero"] = cart[1]["numero"]
                numero_de_jokers += 1
        
        if all(carta["numero"] == cart[0]["numero"] for carta in cart):
            print("El trio es valido")
            return True 
        else:
            print("El trio no es valido")
            return False
    
    def ordenar_seguidilla(self, cartas, valor_A):
        """Ordena una seguidilla según el valor del As (inicio=1 o final=14)"""
        cart = copy.deepcopy(cartas)
        if valor_A == "inicio":
            valores = {"A": 1, "J": 11, "Q": 12, "K": 13}
        elif valor_A == "final":
            valores = {"A": 14, "J": 11, "Q": 12, "K": 13}
        # Convertir a valores numéricos (Joker = None)
        reales, jokers = [], []
        for carta in cart:
            if carta["numero"] == "Joker":
                jokers.append({"numero": None, "figura": carta["figura"], "original": "Joker"})
            elif carta["numero"] in valores:
                reales.append({"numero": valores[carta["numero"]], "figura": carta["figura"], "original": carta["numero"]})
            else:
                reales.append({"numero": int(carta["numero"]), "figura": carta["figura"], "original": carta["numero"]})

        # Ordenar reales
        reales.sort(key=lambda c: c["numero"])

        resultado = []
        i = 0
        while i < len(reales)-1:
            resultado.append(reales[i])
            gap = reales[i+1]["numero"] - reales[i]["numero"] - 1
            # Si hay huecos y Jokers disponibles, los insertamos
            while gap > 0 and jokers:
                resultado.append(jokers.pop(0))  # Joker ocupa el hueco
                gap -= 1
            i += 1
        resultado.append(reales[-1])
        if len(jokers) == 1 and resultado[0]["numero"] != 1 and resultado[-1]["numero"] != 14:
            final = []
            for c in resultado:
                if c["original"] == "Joker":
                    final.append({"numero": "Joker", "figura": c["figura"]})
                elif isinstance(c["original"], int):
                    final.append({"numero": c["original"], "figura": c["figura"]})
                else:
                    final.append({"numero": c["original"], "figura": c["figura"]})
            final.append({"numero": "Joker", "figura": jokers[0]["figura"]})
            return ["ambos", final]

        # Si sobran Jokers, los ponemos al inicio o final
        if len(jokers) == 2 and resultado[0]["numero"] != 1 and resultado[-1]["numero"] != 14:
            resultado.append(jokers.pop(0))
            resultado.insert(0, jokers.pop(0))
        if resultado and jokers and resultado[0]["numero"] == 1:
            resultado = resultado + jokers if jokers else resultado
        elif resultado and jokers and resultado[-1]["numero"] == 14:
            resultado = jokers + resultado if jokers else resultado

        # Reconstruir con nombres originales
        final = []
        for c in resultado:
            if c["original"] == "Joker":
                final.append({"numero": "Joker", "figura": c["figura"]})
            elif isinstance(c["original"], int):
                final.append({"numero": c["original"], "figura": c["figura"]})
            else:
                final.append({"numero": c["original"], "figura": c["figura"]})
        return final

    def validar_segudilla(self, cartas):
        """Valida si un conjunto de cartas forma una seguidilla válida"""
        def validar(cartas2, valor):
            cart = copy.deepcopy(cartas2)
            print(cart)
            print(valor)
            if valor == "inicio":
                print("por el inicio")
                valores = {"Joker": 0, "A": 1, "J": 11, "Q": 12, "K": 13}
            if valor == "final":
                print("por el final")
                valores = {"Joker": 0, "A": 14, "J": 11, "Q": 12, "K": 13}
            for carta in cart:
                print(carta["numero"] )
                if carta["numero"] in valores:
                    carta["numero"] = valores[carta["numero"]]
                else:
                    carta["numero"] = int(carta["numero"])
            print(cart)
            cart_ordenada = sorted(cart, key=lambda carta: carta["numero"])

            numeros = [carta["numero"] for carta in cart_ordenada]
            if len(cart_ordenada) < 4:
                return False      
            numero_de_jokers = 0
            for x, p in enumerate(cart_ordenada):
                if p["numero"] == 0 and numero_de_jokers < 2:
                    cart_ordenada[x]["figura"] = cart_ordenada[2]["figura"]
                    numero_de_jokers += 1
            for x in cart_ordenada:
                print(f"Carta :{x}")
            if all(carta["figura"] == cart_ordenada[0]["figura"] for carta in cart_ordenada):              
                if numeros[0] != 0 and numeros[1] != 0:
                    num_saltos = self.salto(0, numeros)
                    if num_saltos == 0:
                        return True
                    else:
                        return False
                elif numeros[0] == 0 and numeros[1] != 0:
                    salto_joker1 = self.salto_joker(1, numeros)
                    if salto_joker1 == 1:
                        num_saltos = self.salto(1, numeros)
                        if num_saltos == 1:
                            return True                   
                        else:
                            return False
                    elif salto_joker1 == 0:
                        num_salto = self.salto(1, numeros)
                        if num_salto != 0:
                            return False
                        elif num_salto == 0 and numeros[-1] != 13 and numeros[1] != 1:
                            return True                                      
                        elif num_salto == 0 and numeros[-1] == 13 and numeros[1] != 1:
                            return True
                        elif num_salto == 0 and numeros[-1] != 13 and numeros[1] == 1:
                            return True
                        elif num_salto == 0 and numeros[-1] == 13 and numeros[1] == 1:
                            return False
                    else:
                        return False
                elif numeros[0] == 0 and numeros[1] == 0:
                    salto_joker1 = self.salto_joker(1, numeros)
                    if salto_joker1 == 2:
                        num_salto = self.salto(2, numeros)
                        if num_salto == 2:
                            return True
                        else:
                            return False
                    elif salto_joker1 == 1:
                        num_salto = self.salto(2, numeros)
                        if num_salto == 1 and numeros[-1] != 13 and numeros[2] != 1:                   
                            return True
                        elif num_salto == 1 and numeros[-1] == 13 and numeros[2] != 1:
                            return True
                        elif num_salto == 1 and numeros[-1] != 13 and numeros[2] == 1:
                            return True
                        elif num_salto == 1 and numeros[-1] == 13 and numeros[2] == 1:
                            return False
                        else:
                            return False
                    elif salto_joker1 == 0:
                        num_salto = self.salto(2, numeros)
                        if num_salto == 0 and numeros[-1] != 13 and numeros[2] != 1:
                            return True
                        else:
                            return False
                    else:
                        return False
            else:
                return False
        valor_a_14 = validar(cartas, valor="final")
        valor_a_1 = validar(cartas, valor="inicio")
        print(valor_a_1, valor_a_14)
        if valor_a_1 and valor_a_14:
            return self.ordenar_seguidilla(cartas, "inicio")
        elif valor_a_1 and not valor_a_14:
            return self.ordenar_seguidilla(cartas, "inicio")
        elif not valor_a_1 and valor_a_14:
            return self.ordenar_seguidilla(cartas, "final")
        else:
            return False
            
    def validar_extender_trio(self, carta_extender, trio):
        """Valida si una carta puede extender un trío"""
        valores = {"A": 1, "J": 11, "Q": 12, "K": 13}
        def valor_numerico(carta):
            if carta["numero"] == "Joker":
                return None
            if carta["numero"] in valores:
                return valores[carta["numero"]]
            return int(carta["numero"])
        trio_cartas = list(trio)
        if not trio_cartas:
            return False
        cartas_no_joker = [c for c in trio_cartas if c["numero"] != "Joker"]
        if not cartas_no_joker:
            return False
        numero_objetivo = cartas_no_joker[0]["numero"]
        valor_objetivo = valor_numerico(cartas_no_joker[0])
        if valor_objetivo is None:
            return False
        if not all(c["numero"] == numero_objetivo for c in cartas_no_joker):
            return False
        if not isinstance(carta_extender, dict):
            return False
        es_joker_ext = carta_extender.get("numero") == "Joker"
        total_en_trio = len(trio_cartas)
        jokers_en_trio = sum(1 for c in trio_cartas if c["numero"] == "Joker")
        figuras_presentes = {c["figura"] for c in trio_cartas if c["numero"] != "Joker"}
        if es_joker_ext:
            if jokers_en_trio == 0:
                return True
            else:
                return False
        # no es joker
        if carta_extender.get("numero") != numero_objetivo:
            return False

        figuras_presentes.add(carta_extender.get("figura"))
        return True

    def validar_extender_seguidilla(self, carta_extender, seguidilla):
        """Valida si una carta puede extender una seguidilla"""
        if (seguidilla[-1]["numero"] == "A" or seguidilla[-1]["numero"] == "K") and seguidilla[0]["numero"] != "A" and seguidilla[1]["numero"] != "2":
            valores = {"A": 14, "J": 11, "Q": 12, "K": 13}
        elif seguidilla[0]["numero"] == "A" or seguidilla[1]["numero"] == "2":
            valores = {"A": 1, "J": 11, "Q": 12, "K": 13}
        elif carta_extender["numero"] == "A" and seguidilla[0]["numero"] != "2" and seguidilla[-1]["numero"] != "K" and seguidilla[-2]["numero"] != "Q":
            valores = {"A": 1, "J": 11, "Q": 12, "K": 13}
        elif carta_extender["numero"] == "A" and (seguidilla[-1]["numero"] == "K" or seguidilla[-2]["numero"] == "Q") and seguidilla[0]["numero"] != "2":
            valores = {"A": 14, "J": 11, "Q": 12, "K": 13}
        elif carta_extender["numero"] == "A" and seguidilla[0]["numero"] == "2" and seguidilla[-1]["numero"] == "K":
            valores = {"A": 1, "J": 11, "Q": 12, "K": 13}
        elif seguidilla[0]["numero"] == "Joker" and seguidilla[1]["numero"] == "2" and seguidilla[-1]["numero"] != "K":
            valores = {"A": 1, "J": 11, "Q": 12, "K": 13}
        elif seguidilla[-1]["numero"] == "Joker" and seguidilla[-2]["numero"] == "K":
            valores = {"A": 1, "J": 11, "Q": 12, "K": 13}
        elif seguidilla[0]["numero"] == "Joker" and seguidilla[1]["numero"] == "2":
            valores = {"A": 14, "J": 11, "Q": 12, "K": 13}
        elif seguidilla[0]["numero"] == "Joker" and seguidilla[-1]["numero"] == "3":
            valores = {"A": 1, "J": 11, "Q": 12, "K": 13}
        elif seguidilla[-1]["numero"] == "Joker" and seguidilla[-2]["numero"] == "Q":
            valores = {"A": 14, "J": 11, "Q": 12, "K": 13}
        elif seguidilla[-1]["numero"] == "Joker" and seguidilla[0]["numero"] == "Joker" and len(seguidilla) == 14:
            return False
        else:
            valores = {"A": 1, "J": 11, "Q": 12, "K": 13}
        if carta_extender["numero"] != "Joker" and carta_extender in seguidilla:
            return False
        for carta in seguidilla:
            if carta["numero"] != "Joker":
                palo = carta["figura"]
                break

        def valor_numerico(carta):
            if carta["numero"] == "Joker":
                return None
            if carta["numero"] in valores:
                return valores[carta["numero"]]
            return int(carta["numero"])
        try:
            if seguidilla[0]["numero"] == "Joker" and carta_extender["figura"] == palo:
                print("aaaaaaaaaaaa")
                carta_siguiente = seguidilla[1]
                valor_joker = valor_numerico(carta_siguiente) - 1
                print(valor_joker)
                if carta_extender["numero"] != "Joker" and valor_numerico(carta_extender) == valor_joker-1:
                    print("Puede extenderse al inicio")
                    return "inicio"
            if seguidilla[-1]["numero"] == "Joker" and carta_extender["figura"] == palo:
                print("aaaaaaaaaeeeaaa")
                carta_anterior = seguidilla[-2]
                valor_joker = valor_numerico(carta_anterior) + 1
                print(valor_joker)
                if carta_extender["numero"] != "Joker" and valor_numerico(carta_extender) == valor_joker+1:
                    print("Puede extenderse al final")
                    return "final"
        except:
            pass
        seg = list(seguidilla)
        if not seg:
            return False

        for i in range(len(seg) - 1):
            if seg[i]["numero"] == "Joker" and seg[i + 1]["numero"] == "Joker":
                return False

        cartas_no_joker = [c for c in seg if c["numero"] != "Joker"]
        if not cartas_no_joker:
            return False

        palo_base = cartas_no_joker[0]["figura"]
        if not all(c["figura"] == palo_base for c in cartas_no_joker):
            return False

        valores_presentes = {valor_numerico(c) for c in cartas_no_joker}
        if any(v is None for v in valores_presentes):
            return False

        first_non_joker_idx = next(i for i, c in enumerate(seg) if c["numero"] != "Joker")
        last_non_joker_idx = len(seg) - 1 - next(i for i, c in enumerate(reversed(seg)) if c["numero"] != "Joker")

        seg_ = []
        copia_seg = copy.deepcopy(seguidilla)
        for c in copia_seg:
            if c["numero"] != "Joker":
                c["numero"] = valor_numerico(c)
                seg_.append(c)
            elif c["numero"] == "Joker":
                seg_.append(c)    
        print(seg_)
        valores_reales = self.valor_joker(seg_)
                

        first_val = valores_reales[0]["numero"]
        last_val = valores_reales[-1]["numero"]

        def siguiente(v): return v + 1
        def anterior(v): return v - 1

        if not isinstance(carta_extender, dict):
            return False

        es_joker_ext = carta_extender.get("numero") == "Joker"
        if not es_joker_ext and carta_extender.get("figura") != palo_base:
            return False

        if not es_joker_ext:
            v_ext = valor_numerico(carta_extender)
            if v_ext is None:
                return False
            if v_ext in valores_presentes:
                return False

            if first_val > 0 and v_ext == anterior(first_val):
                return "inicio"

            if last_val < 15 and v_ext == siguiente(last_val):
                return "final"

            return False
        if es_joker_ext:
            if seg[0]["numero"] == "Joker" and seg[-1]["numero"] == "Joker":
                return False
            elif seg[0]["numero"] == "Joker" and len(seg) < 14 and seguidilla[-1]["numero"] != "A":
                return "final"
            elif seg[-1]["numero"] == "Joker" and len(seg) < 14 and seguidilla[0]["numero"] != "A":
                return "inicio"

                
        puede_inicio = False
        puede_final = False

        if seguidilla[0]["numero"] != "Joker" and first_val > 1:
            intended_start_val = anterior(first_val)
            if intended_start_val not in valores_presentes:
                puede_inicio = True

        if seguidilla[-1]["numero"] != "Joker" and last_val < 14:
            intended_end_val = siguiente(last_val)
            if intended_end_val not in valores_presentes:
                print("puede final 1")
                puede_final = True
        print(seg_)
        if seguidilla[0]["numero"] == "Joker":
            seg_1 = self.valor_joker(seg_)
            if carta_extender["numero"] != "Joker" and carta_extender["numero"] == seg_1[0]["numero"] -1:
                puede_inicio = True
        if seguidilla[-1]["numero"] == "Joker":
            seg_1 = self.valor_joker(seg_)
            if carta_extender["numero"] != "Joker" and carta_extender["numero"] == seg_1[0]["numero"] -1:
                print("puede final 2")
                puede_final = True

        if puede_inicio and puede_final:
            return "ambos"
        if puede_inicio:
            return "inicio"
        if puede_final:
            return "final"
        return False
    
    def valor_joker2(self, seg):
        """Calcula el valor numérico de los jokers en una seguidilla"""
        cartas_no_joker = [c for c in seg if c["numero"] != "Joker"]
        palo = cartas_no_joker[0]["figura"]
        for c in seg:
            if c["numero"] == "Joker":
                indice = seg.index(c)
                if indice == 0:
                    siguiente_carta = seg[indice + 1]
                    valor_siguiente = siguiente_carta["numero"]
                    if valor_siguiente > 1:
                        c["numero"] = valor_siguiente - 1
                        c["figura"] = palo
                    else:
                        c["numero"] = 13
                        c["figura"] = palo
                elif indice == len(seg) - 1:
                    carta_anterior = seg[indice - 1]
                    valor_anterior = carta_anterior["numero"]
                    if valor_anterior < 13:
                        c["numero"] = valor_anterior + 1
                        c["figura"] = palo
                    else:
                        c["numero"] = 1
                        c["figura"] = palo
                else:
                    carta_anterior = seg[indice - 1]
                    siguiente_carta = seg[indice + 1]
                    valor_anterior = carta_anterior["numero"]
                    valor_siguiente = siguiente_carta["numero"]
                    if valor_anterior is not None and valor_siguiente is not None:
                        if valor_siguiente - valor_anterior == 2:
                            c["numero"] = valor_anterior + 1
                            c["figura"] = palo
                        else:
                            c["numero"] = None
                    else:
                        c["numero"] = None
        return seg

    def valor_joker(self, seg):
        """Calcula el valor numérico de los jokers en una seguidilla"""
        for c in seg:
            if c["numero"] == "Joker":
                indice = seg.index(c)
                if indice == 0:
                    siguiente_carta = seg[indice + 1]
                    valor_siguiente = siguiente_carta["numero"]
                    if valor_siguiente > 1:
                        c["numero"] = valor_siguiente - 1
                    else:
                        c["numero"] = 13
                elif indice == len(seg) - 1:
                    carta_anterior = seg[indice - 1]
                    valor_anterior = carta_anterior["numero"]
                    if valor_anterior < 13:
                        c["numero"] = valor_anterior + 1
                    else:
                        c["numero"] = 1
                else:
                    carta_anterior = seg[indice - 1]
                    siguiente_carta = seg[indice + 1]
                    valor_anterior = carta_anterior["numero"]
                    valor_siguiente = siguiente_carta["numero"]
                    if valor_anterior is not None and valor_siguiente is not None:
                        if valor_siguiente - valor_anterior == 2:
                            c["numero"] = valor_anterior + 1
                        else:
                            c["numero"] = None
                    else:
                        c["numero"] = None
        return seg
    
    def validar_reemplazar_joker_trio(self,carta_reemplazar, trio):
        """Valida si una carta puede reemplazar un joker en un trío (método estático)"""
        trio_cartas = []
        for carta in trio:
            trio_cartas.append(carta)
        
        valores = [c.numero for c in trio_cartas]
        if 'Joker' in valores:
            joker_index = valores.index('Joker')
            otros_valores = [val for i, val in enumerate(valores) if i != joker_index and val != 'Joker']
            if len(set(otros_valores)) == 1 and carta_reemplazar.numero == otros_valores[0]:
                return joker_index
        return -1

    def validar_reemplazar_joker_seguidilla(self,carta_reemplazar, seguidilla):
        """
        Intenta reemplazar un solo Joker en una seguidilla (lista de dicts).
        - carta_reemplazar: {"numero": "1"|"2"|...|"J"|"Q"|"K"|"A", "figura": "Pica"|...}
        - seguidilla: lista de dicts; un Joker tiene "numero": "joker" (cualquier mayúsc/minúsc).
        Retorna: nueva seguidilla (lista de dicts) con un solo Joker reemplazado si existe
                una posición válida, o None si no es posible.
        """

        def valor_numerico(carta):
            """Convierte el campo 'numero' a su valor numérico (A=1, J=11, Q=12, K=13)"""
            num = str(carta.get("numero", "")).strip().lower()
            if num == "joker":
                return None
            if seguidilla[0]["numero"] == "A" or seguidilla[1]["numero"] == "2":
                mapa = {"a": 1, "j": 11, "q": 12, "k": 13}
            else:
                mapa = {"a": 14, "j": 11, "q": 12, "k": 13}
            if num in mapa:
                return mapa[num]
            try:
                return int(num)
            except (ValueError, TypeError):
                return None

        # Detectar posiciones de todos los jokers
        joker_positions = [i for i, c in enumerate(seguidilla)
                        if str(c.get("numero", "")).strip().lower() == "joker"]
        if not joker_positions:
            return None

        # Extraer cartas no-joker para referencia de figura
        cartas_no_joker = [c for c in seguidilla
                        if str(c.get("numero", "")).strip().lower() != "joker"]
        if not cartas_no_joker:
            return None

        # La figura de la carta_reemplazar debe coincidir con la figura de las cartas no-joker
        figura_ref = cartas_no_joker[0].get("figura")
        if carta_reemplazar.get("figura") != figura_ref:
            return None

        # Intentar reemplazar cada joker, uno por uno
        seguidilla_numero = self.valor_joker2(self.jugada_numeros(seguidilla))
        carta_reemplazar_num = valor_numerico(carta_reemplazar)
        valores_jokers = []
        for pos in joker_positions:
            valores_jokers.append((pos,seguidilla_numero[pos]))
        for y,x in valores_jokers:
            
            if x["numero"] == carta_reemplazar_num:
                seguidilla[y] = carta_reemplazar
                return seguidilla
        return None

    
    def validar_seleccion(self, cartas_a_bajar, id_jugador):
        """Valida la selección de cartas para formar jugadas
        
        Retorna: (bool, list) - Tupla con (True si hay cambios, lista de mensajes a enviar)
        """
        validacion_seguidilla = self.validar_segudilla(cartas_a_bajar)
        validacion_trio = self.validar_trio(cartas_a_bajar)
        jugadas = self.jugadas_por_jugador[id_jugador]
        self.seleccionando = True
        mensajes_a_enviar = []
        
        if self.ronda == 1:
            val_trio = False
            val_seguidilla = False
            for x, y in jugadas:
                if x == "Trio":
                    val_trio = True
                if x == "Seguidilla":
                    val_seguidilla = True
            if validacion_seguidilla != False and validacion_trio != False:
                print("esto no puede pasasr xd")
                self.seleccionando = False
                mensajes_a_enviar.append({
                    "type": "Seleccion_cancelada",
                })

            elif validacion_seguidilla == False and validacion_trio == False:
                print("La jugada no es valida")
                self.seleccionando = False
                self.seguidilla = {}
                self.trio = {}
                mensajes_a_enviar.append({
                    "type": "Seleccion_cancelada",
                })
            elif validacion_seguidilla != False and val_seguidilla == False and self.seguidilla == {}:
                self.seguidilla = validacion_seguidilla
                print("Seguidilla valida")
                if len(self.seguidilla) == 2 and self.seguidilla[0] == "ambos":
                    print("elegir donde posicionar la carta")
                    self.seguidilla = self.seguidilla[1]
                    print(self.seguidilla)
                    mensajes_a_enviar.append({
                        "type": "elegir_posicion_seguidilla",
                    })
                else:
                    print("Seguidilla valida")
                    mensajes_a_enviar.append({
                        "type": "seleccion_valida",
                        "actualizar": False
                    })
            elif validacion_trio != False and val_trio == False and self.trio == {}:
                self.trio = cartas_a_bajar
                print("Trio valido")
                mensajes_a_enviar.append({
                    "type": "seleccion_valida",
                    "actualizar": False
                })
            else:
                self.seleccionando = False
                mensajes_a_enviar.append({
                    "type": "Seleccion_cancelada",
                })
                print("XDDD")
        if self.ronda == 2:
            if validacion_seguidilla != False:
                if len(self.seguidilla) == 0 and len(self.jugadas_por_jugador[id_jugador]) == 0:
                    self.seguidilla = []
                    if len(validacion_seguidilla) == 2 and validacion_seguidilla[0] == "ambos":
                        print("elegir donde posicionar la carta")
                        self.seguidilla.append(validacion_seguidilla[-1])
                        print(self.seguidilla)
                        mensajes_a_enviar.append({
                            "type": "elegir_posicion_seguidilla",
                        })
                    else:
                        print("Seguidilla valida")
                        mensajes_a_enviar.append({
                            "type": "seleccion_valida",
                            "actualizar": False
                        })
                        self.seguidilla.append(validacion_seguidilla)
                        print(self.seguidilla)
                elif len(self.jugadas_por_jugador[id_jugador]) == 1:
                    if len(validacion_seguidilla) == 2 and validacion_seguidilla[0] == "ambos":
                        print("elegir donde posicionar la carta")
                        self.seguidilla.append(validacion_seguidilla[-1])
                        print(self.seguidilla)
                        self.enviar_a_cliente(id_jugador, {
                            "type": "elegir_posicion_seguidilla",
                        })
                    
                    else:    
                        print("pinche codigo no sirve")
                        print(self.seguidilla)
                        print(validacion_seguidilla)
                        prueba_separacion_ = self.valor_joker2(self.jugada_numeros(self.jugadas_por_jugador[id_jugador][-1][-1])) + self.valor_joker2(self.jugada_numeros(validacion_seguidilla))
                        print(prueba_separacion_)
                        validacion = self.validar_segudilla(prueba_separacion_)
                        if validacion != False:
                            print("No se puede dividir dos seguidillas continuas")
                            self.seleccionando = False
                            self.seguidilla = []
                            mensajes_a_enviar.append({
                            "type": "Seleccion_cancelada",
                            })
                        else:
                            print("Seguidilla valida")
                            self.seguidilla.append(validacion_seguidilla)
                            mensajes_a_enviar.append({
                                "type": "seleccion_valida",
                                "actualizar": False
                            })
                elif len(self.jugadas_por_jugador[id_jugador]) == 0 and len(self.seguidilla)==1:
                    if len(validacion_seguidilla) == 2 and validacion_seguidilla[0] == "ambos":
                        print("elegir donde posicionar la carta")
                        self.seguidilla.append(validacion_seguidilla[-1])
                        print(self.seguidilla)
                        mensajes_a_enviar.append({
                            "type": "elegir_posicion_seguidilla",
                        })
                    else:
                        print(self.jugada_numeros(self.seguidilla[-1]))
                        print("pinche codigo no sirve")
                        print(self.seguidilla[0])
                        print(validacion_seguidilla)
                        prueba_separacion_ = self.valor_joker2(self.jugada_numeros(self.seguidilla[-1])) + self.valor_joker2(self.jugada_numeros(validacion_seguidilla))
                        print(prueba_separacion_)
                        prueba_separacion = prueba_separacion_
                        print(prueba_separacion)

                        validacion = self.validar_segudilla(prueba_separacion)
                        if validacion != False:
                            print("No se puede dividir dos seguidillas continuas")
                            self.seleccionando = False
                            self.seguidilla = []
                            mensajes_a_enviar.append({
                            "type": "Seleccion_cancelada",
                            })
                        else:
                            print("Seguidilla valida")
                            self.seguidilla.append(validacion_seguidilla)
                            mensajes_a_enviar.append({
                                "type": "seleccion_valida",
                                "actualizar": False
                            })
                else:
                    self.seleccionando = False
                    self.seguidilla = []
                    mensajes_a_enviar.append({
                    "type": "Seleccion_cancelada",
                    })
            else:
                self.seleccionando = False
                self.seguidilla = []
                mensajes_a_enviar.append({
                "type": "Seleccion_cancelada",
                })
        if self.ronda == 3: #3 trio, no seguidillas
            if validacion_trio != False:
                if len(self.trio) < 3:
                    if self.trio == {}:
                        self.trio = []
                    self.trio.append(cartas_a_bajar)
                    print("Trio valido")
                    mensajes_a_enviar.append({
                        "type": "seleccion_valida",
                        "actualizar": False
                    })
            else:
                self.seleccionando = False
                self.seguidilla = {}
                self.trio = {}
                mensajes_a_enviar.append({
                "type": "Seleccion_cancelada",
                })

        if self.ronda == 4:
            if validacion_seguidilla != False:
                if len(self.seguidilla) < 1:
                    self.seguidilla = []
                    if len(validacion_seguidilla) == 2 and validacion_seguidilla[0] == "ambos":
                        print("elegir donde posicionar la carta")
                        self.seguidilla.append(validacion_seguidilla[-1])
                        print(self.seguidilla)
                        mensajes_a_enviar.append({
                            "type": "elegir_posicion_seguidilla",
                        })
                    else:
                        print("Seguidilla valida")
                        mensajes_a_enviar.append({
                            "type": "seleccion_valida",
                            "actualizar": False
                        })
                        self.seguidilla.append(validacion_seguidilla)
                        print(self.seguidilla)
                else:
                    self.seleccionando = False
                    self.seguidilla = {}
                    self.trio = {}
                    mensajes_a_enviar.append({
                    "type": "Seleccion_cancelada",
                    })
            elif validacion_trio != False:
                if len(self.trio) < 2:
                    if self.trio == {}:
                        self.trio = []
                    self.trio.append(cartas_a_bajar)
                    print("Trio valido")
                    mensajes_a_enviar.append({
                        "type": "seleccion_valida",
                        "actualizar": False
                    })
                else:
                    self.seleccionando = False
                    self.seguidilla = {}
                    self.trio = {}
                    mensajes_a_enviar.append({
                    "type": "Seleccion_cancelada",
                    })
            else:
                self.seleccionando = False
                self.seguidilla = {}
                self.trio = {}
                mensajes_a_enviar.append({
                "type": "Seleccion_cancelada",
                })
        return (len(mensajes_a_enviar) > 0, mensajes_a_enviar)

    def jugada_numeros(self,jugada_):
        jugada = copy.deepcopy(jugada_)
        valores = {"A": 1, "J": 11, "Q": 12, "K": 13}
        if jugada[0]["numero"] == "Joker":
            if jugada[1]["numero"] in valores:
                jugada[0]["numero"] = valores[jugada[1]["numero"]]-1
            else:      
                jugada[0]["numero"] = int(jugada[1]["numero"])-1 
            contador = int(jugada[0]["numero"])-1
        else:
            if jugada[0]["numero"] in valores:
                jugada[0]["numero"] = valores[jugada[0]["numero"]]
            contador = int(jugada[0]["numero"])-1
        for i,cartas in enumerate(jugada):
            if cartas["numero"] != "Joker":
                cartas["numero"] = contador +1
                contador += 1
            if cartas["numero"] == "Joker" and cartas != jugada[0]:
                cartas["numero"] = int(jugada[i-1]["numero"])+1
                cartas["figura"] = jugada[i-1]["figura"]
                contador += 1
        return jugada

    def validar_jugada(self, id_jugador):
        """Valida y procesa la jugada completa del jugador (bajarse)
        
        Retorna: (bool, list, list) - Tupla con (exito, mensajes_a_cliente, mensajes_a_difundir)
        """
        mensajes_a_cliente = []
        mensajes_a_difundir = []
        if self.ronda == 1:
            if self.trio != {} and self.seguidilla != {}:
                self.ultima_jugada = []
                print("Jugada valida, te has bajado")
                carta_jug = []
                for tag, cart in self.jugadas_por_jugador[id_jugador]:
                    carta_jug.append(cart)
                if carta_jug:
                    carta_jug = carta_jug[0]
                print(carta_jug)
                jugada = []
                if self.trio[0] not in carta_jug:
                    jugada.append(("Trio", self.trio))
                    self.ultima_jugada.append(self.trio)
                    print(self.ultima_jugada)
                if self.seguidilla[0] not in carta_jug:
                    jugada.append(("Seguidilla", self.seguidilla))
                    self.ultima_jugada.append(self.seguidilla)
                    print(self.ultima_jugada)
                    print("Aaaaaaaaaaaaaaaaaaaa")
                    print(self.jugadas_por_jugador[id_jugador])
                for carta in self.trio:
                    for i, _carta in enumerate(self.manos[id_jugador-1]):
                        try:
                            _carta = _carta.to_dict()
                        except:
                            _carta = _carta
                        if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                            self.manos[id_jugador-1].pop(i)
                            break
                for carta in self.seguidilla:
                    for i, _carta in enumerate(self.manos[id_jugador-1]):
                        try:
                            _carta = _carta.to_dict()
                        except:
                            _carta = _carta
                        if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                            self.manos[id_jugador-1].pop(i)
                            break
                self.cancelar = False
                self.jugadas_por_jugador[id_jugador] = jugada
                mano_nueva = self.convertir_mano_dic(id_jugador)
                self.modificar_cartas(id_jugador, -(len(self.trio)+len(self.seguidilla)))
                mensajes_a_cliente.append({
                    "type": "validacion_bajarse",
                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "datos_mano_jugador": mano_nueva,
                    "jugada": self.jugadas_por_jugador[id_jugador],
                    "jugadas_jugadores": self.jugadas_por_jugador
                })
                mensajes_a_cliente.append({
                    "type": "mostrar_extender",
                })
                mensajes_a_difundir.append({
                    "type": "se_bajo_alguien",
                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "jugadas_jugadores": self.jugadas_por_jugador,
                })
                #=====Jesua: Verificar si la mano quedó vacía por esta acción y difundir puntuaciones
                self.trio = {}
                self.seguidilla = {}
                self.seleccionando = False
            elif self.trio != {} and self.seguidilla == {}:
                print("Bajando trio")
                jugada = []
                jugada.append(("Trio", self.trio))
                self.jugadas_por_jugador[id_jugador] = jugada + self.jugadas_por_jugador[id_jugador]
                self.ultima_jugada = []
                self.ultima_jugada.append(self.trio)
                for carta in self.trio:
                    for i, _carta in enumerate(self.manos[id_jugador-1]):
                        try:
                            _carta = _carta.to_dict()
                        except:
                            _carta = _carta
                        if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                            self.manos[id_jugador-1].pop(i)
                            break
                mano_nueva = self.convertir_mano_dic(id_jugador)
                self.modificar_cartas(id_jugador, -len(self.trio))
                mensajes_a_cliente.append({
                    "type": "validacion_bajarse",
                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "datos_mano_jugador": mano_nueva,
                    "jugada": self.jugadas_por_jugador[id_jugador],
                    "jugadas_jugadores": self.jugadas_por_jugador
                })
                mensajes_a_difundir.append({
                    "type": "se_bajo_alguien",
                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "jugadas_jugadores": self.jugadas_por_jugador,
                })
                #=====Jesua: Verificar si la mano quedó vacía por esta acción y difundir puntuaciones
                try:
                    self.verificar_mano_vacia_y_difundir(id_jugador)
                except Exception as _:
                    pass
                if len(self.jugadas_por_jugador[id_jugador]) == 2:
                    print("te has bajado completo")
                    mensajes_a_cliente.append({
                        "type": "mostrar_extender",
                    })
                self.cancelar = False   
                self.trio = {}
                self.seleccionando = False
            elif self.trio == {} and self.seguidilla != {}:
                print("Bajando seguidilla")
                jugada = []
                jugada.append(("Seguidilla", self.seguidilla))
                self.jugadas_por_jugador[id_jugador] = self.jugadas_por_jugador[id_jugador] + jugada 
                self.ultima_jugada = []
                self.ultima_jugada.append(self.seguidilla)
                for carta in self.seguidilla:
                    for i, _carta in enumerate(self.manos[id_jugador-1]):
                        try:
                            _carta = _carta.to_dict()
                        except:
                            _carta = _carta
                        if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                            self.manos[id_jugador-1].pop(i)
                            break
                self.modificar_cartas(id_jugador, -len(self.seguidilla))
                mano_nueva = self.convertir_mano_dic(id_jugador)
                self.enviar_a_cliente(id_jugador, {
                    "type": "validacion_bajarse",
                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "datos_mano_jugador": mano_nueva,
                    "jugada": self.jugadas_por_jugador[id_jugador],
                    "jugadas_jugadores": self.jugadas_por_jugador
                })
                self.difundir_excepcion(id_jugador, {
                    "type": "se_bajo_alguien",
                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "jugadas_jugadores": self.jugadas_por_jugador,
                })
                if len(self.jugadas_por_jugador[id_jugador]) == 2:
                    print("te has bajado completo")
                    self.enviar_a_cliente(id_jugador, {
                        "type": "mostrar_extender",
                    })
                print(jugada)
                self.seleccionando = False
                self.cancelar = False
                self.seguidilla = {}
            else:
                print("La jugada no es valida")
        if self.ronda == 2:
            if len(self.seguidilla) == 1 and len(self.jugadas_por_jugador[id_jugador]) == 0:
                print("Bajando seguidilla")
                jugada = []
                jugada.append(("Seguidilla", self.seguidilla[-1]))
                self.jugadas_por_jugador[id_jugador] = self.jugadas_por_jugador[id_jugador] + jugada 
                self.ultima_jugada = []
                self.ultima_jugada.append(self.seguidilla[-1])
                for carta in self.seguidilla[-1]:
                    for i, _carta in enumerate(self.manos[id_jugador-1]):
                        try:
                            _carta = _carta.to_dict()
                        except:
                            _carta = _carta
                        if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                            self.manos[id_jugador-1].pop(i)
                            break
                self.modificar_cartas(id_jugador, -len(self.seguidilla))
                mano_nueva = self.convertir_mano_dic(id_jugador)
                mensajes_a_cliente.append({
                    "type": "validacion_bajarse",
                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "datos_mano_jugador": mano_nueva,
                    "jugada": self.jugadas_por_jugador[id_jugador],
                    "jugadas_jugadores": self.jugadas_por_jugador
                })
                mensajes_a_difundir.append({
                    "type": "se_bajo_alguien",
                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "jugadas_jugadores": self.jugadas_por_jugador,
                })
                if len(self.jugadas_por_jugador[id_jugador]) == 2:
                    print("te has bajado completo")
                    mensajes_a_cliente.append({
                        "type": "mostrar_extender",
                    })
                print(jugada)
                self.seguidilla = []
                self.seleccionando = False
                self.cancelar = False
            elif len(self.seguidilla) == 2 and self.jugadas_por_jugador[id_jugador]==[]:
                print("Bajando jugada completa")
                jugada = []
                jugada.append(("Seguidilla", self.seguidilla[0]))
                if jugada in self.jugadas_por_jugador[id_jugador]:
                    print("en este caso se bajo antes una jugada")
                else:
                    self.jugadas_por_jugador[id_jugador] = self.jugadas_por_jugador[id_jugador] + jugada 
                jugada = []
                jugada.append(("Seguidilla", self.seguidilla[-1]))
                self.jugadas_por_jugador[id_jugador] = self.jugadas_por_jugador[id_jugador] + jugada 
                self.ultima_jugada = []
                self.ultima_jugada = self.seguidilla
                print(self.seguidilla)
                for jugada in self.seguidilla:
                    for carta in jugada:
                        for i, _carta in enumerate(self.manos[id_jugador-1]):
                            try:
                                _carta = _carta.to_dict()
                            except:
                                _carta = _carta
                            if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                self.manos[id_jugador-1].pop(i)
                                break
                self.modificar_cartas(id_jugador, -len(self.seguidilla[0]))
                self.modificar_cartas(id_jugador, -len(self.seguidilla[-1]))
                mano_nueva = self.convertir_mano_dic(id_jugador)
                mensajes_a_cliente.append({
                    "type": "validacion_bajarse",
                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "datos_mano_jugador": mano_nueva,
                    "jugada": self.jugadas_por_jugador[id_jugador],
                    "jugadas_jugadores": self.jugadas_por_jugador
                })
                mensajes_a_difundir.append({
                    "type": "se_bajo_alguien",
                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "jugadas_jugadores": self.jugadas_por_jugador,
                })
                if len(self.jugadas_por_jugador[id_jugador]) == 2:
                    print("te has bajado completo")
                    mensajes_a_cliente.append({
                        "type": "mostrar_extender",
                    })
                self.seguidilla = []
                self.seleccionando = False
                self.cancelar = False
            elif len(self.jugadas_por_jugador[id_jugador]) == 1 and len(self.seguidilla) == 1:
                print("Bajando jugada completa")
                jugada = []
                jugada.append(("Seguidilla", self.seguidilla[-1]))
                self.jugadas_por_jugador[id_jugador] = self.jugadas_por_jugador[id_jugador] + jugada 
                self.ultima_jugada = []
                self.ultima_jugada.append(self.seguidilla[-1])
                print(self.seguidilla)
                "aqui esta el error recuerdalo acomada el pinche bucle para que elimine las cartas que son"
                for jugada in self.seguidilla:
                    for carta in jugada:
                        for i, _carta in enumerate(self.manos[id_jugador-1]):
                            try:
                                _carta = _carta.to_dict()
                            except:
                                _carta = _carta
                            if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                self.manos[id_jugador-1].pop(i)
                                break
                    
                        
                self.modificar_cartas(id_jugador, -len(self.seguidilla[-1]))
                mano_nueva = self.convertir_mano_dic(id_jugador)
                mensajes_a_cliente.append({
                    "type": "validacion_bajarse",
                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "datos_mano_jugador": mano_nueva,
                    "jugada": self.jugadas_por_jugador[id_jugador],
                    "jugadas_jugadores": self.jugadas_por_jugador
                })
                mensajes_a_difundir.append({
                    "type": "se_bajo_alguien",
                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "jugadas_jugadores": self.jugadas_por_jugador,
                })
                if len(self.jugadas_por_jugador[id_jugador]) == 2:
                    print("te has bajado completo")
                    mensajes_a_cliente.append({
                        "type": "mostrar_extender",
                    })
                self.seguidilla = []
                self.seleccionando = False
                self.cancelar = False
            else:
                print("La jugada no es valida")
        if self.ronda == 3:  # 3 tríos, no seguidillas
            # Caso 1: bajar el primer trío si aún no hay jugadas
            if len(self.trio) == 1 and len(self.jugadas_por_jugador[id_jugador]) == 0:
                print("Bajando primer trío")
                jugada = [("Trio", self.trio[-1])]
                self.jugadas_por_jugador[id_jugador] += jugada
                self.ultima_jugada = [self.trio[-1]]

                # Eliminar cartas del trío de la mano
                for carta in self.trio[-1]:
                    for i, _carta in enumerate(self.manos[id_jugador-1]):
                        try:
                            _carta = _carta.to_dict()
                        except:
                            pass
                        if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                            self.manos[id_jugador-1].pop(i)
                            break

                self.modificar_cartas(id_jugador, -len(self.trio[-1]))
                mano_nueva = self.convertir_mano_dic(id_jugador)

                mensajes_a_cliente.append({
                    "type": "validacion_bajarse",
                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "datos_mano_jugador": mano_nueva,
                    "jugada": self.jugadas_por_jugador[id_jugador],
                    "jugadas_jugadores": self.jugadas_por_jugador
                })
                mensajes_a_difundir.append({
                    "type": "se_bajo_alguien",
                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "jugadas_jugadores": self.jugadas_por_jugador,
                })

                if len(self.jugadas_por_jugador[id_jugador]) == 3:
                    print("Te has bajado completo")
                    mensajes_a_cliente.append({"type": "mostrar_extender"})

                self.trio = []
                self.seleccionando = False
                self.cancelar = False

            # Caso 2: bajar los 3 tríos de golpe si aún no hay jugadas
            elif len(self.trio) == 3 and self.jugadas_por_jugador[id_jugador] == []:
                print("Bajando jugada completa (3 tríos)")
                for trio in self.trio:
                    jugada = [("Trio", trio)]
                    self.jugadas_por_jugador[id_jugador] += jugada

                    for carta in trio:
                        for i, _carta in enumerate(self.manos[id_jugador-1]):
                            try:
                                _carta = _carta.to_dict()
                            except:
                                pass
                            if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                self.manos[id_jugador-1].pop(i)
                                break

                    self.modificar_cartas(id_jugador, -len(trio))

                self.ultima_jugada = self.trio
                mano_nueva = self.convertir_mano_dic(id_jugador)

                mensajes_a_cliente.append({
                    "type": "validacion_bajarse",
                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "datos_mano_jugador": mano_nueva,
                    "jugada": self.jugadas_por_jugador[id_jugador],
                    "jugadas_jugadores": self.jugadas_por_jugador
                })
                mensajes_a_difundir.append({
                    "type": "se_bajo_alguien",
                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "jugadas_jugadores": self.jugadas_por_jugador,
                })

                if len(self.jugadas_por_jugador[id_jugador]) == 3:
                    print("Te has bajado completo")
                    mensajes_a_cliente.append({"type": "mostrar_extender"})

                self.trio = []
                self.seleccionando = False
                self.cancelar = False
            elif len(self.trio) == 2 and self.jugadas_por_jugador[id_jugador] == []:
                print("Bajando jugada completa (2 tríos)")
                for trio in self.trio:
                    jugada = [("Trio", trio)]
                    self.jugadas_por_jugador[id_jugador] += jugada

                    for carta in trio:
                        for i, _carta in enumerate(self.manos[id_jugador-1]):
                            try:
                                _carta = _carta.to_dict()
                            except:
                                pass
                            if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                self.manos[id_jugador-1].pop(i)
                                break

                    self.modificar_cartas(id_jugador, -len(trio))

                self.ultima_jugada = self.trio
                mano_nueva = self.convertir_mano_dic(id_jugador)

                mensajes_a_cliente.append({
                    "type": "validacion_bajarse",
                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "datos_mano_jugador": mano_nueva,
                    "jugada": self.jugadas_por_jugador[id_jugador],
                    "jugadas_jugadores": self.jugadas_por_jugador
                })
                mensajes_a_difundir.append({
                    "type": "se_bajo_alguien",
                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "jugadas_jugadores": self.jugadas_por_jugador,
                })

                if len(self.jugadas_por_jugador[id_jugador]) == 3:
                    print("Te has bajado completo")
                    mensajes_a_cliente.append({"type": "mostrar_extender"})

                self.trio = []
                self.seleccionando = False
                self.cancelar = False


            # Caso 3: ya bajó 1 o 2 tríos y ahora baja otro
            elif len(self.jugadas_por_jugador[id_jugador]) in [1, 2] and len(self.trio) == 1:
                print("Bajando otro trío")
                jugada = [("Trio", self.trio[-1])]
                self.jugadas_por_jugador[id_jugador] += jugada
                self.ultima_jugada = [self.trio[-1]]

                for carta in self.trio[-1]:
                    for i, _carta in enumerate(self.manos[id_jugador-1]):
                        try:
                            _carta = _carta.to_dict()
                        except:
                            pass
                        if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                            self.manos[id_jugador-1].pop(i)
                            break

                self.modificar_cartas(id_jugador, -len(self.trio[-1]))
                mano_nueva = self.convertir_mano_dic(id_jugador)

                mensajes_a_cliente.append({
                    "type": "validacion_bajarse",
                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "datos_mano_jugador": mano_nueva,
                    "jugada": self.jugadas_por_jugador[id_jugador],
                    "jugadas_jugadores": self.jugadas_por_jugador
                })
                mensajes_a_difundir.append({
                    "type": "se_bajo_alguien",
                    "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                    "jugadas_jugadores": self.jugadas_por_jugador,
                })

                if len(self.jugadas_por_jugador[id_jugador]) == 3:
                    print("Te has bajado completo")
                    mensajes_a_cliente.append({"type": "mostrar_extender"})

                self.trio = []
                self.seleccionando = False
                self.cancelar = False
            else:
                print("La jugada no es valida")

        if self.ronda == 4:
            print(self.trio)
            print(self.seguidilla)
            if len(self.trio) == 2 and len(self.seguidilla) == 1:
                cantidad_cartas = len(self.trio[0])+len(self.seguidilla[0])+len(self.trio[-1])
                print(cantidad_cartas)
                if cantidad_cartas == len(self.manos[id_jugador-1]):
                    self.ultima_jugada = []
                    print("Jugada valida, te has bajado")
                    carta_jug = []
                    for tag, cart in self.jugadas_por_jugador[id_jugador]:
                        carta_jug.append(cart)
                    if carta_jug:
                        carta_jug = carta_jug[0]
                    print(carta_jug)
                    jugada = []
                    if self.trio[0] not in carta_jug:
                        jugada.append(("Trio", self.trio[0]))
                        self.ultima_jugada.append(self.trio[0])
                        print(self.ultima_jugada)
                    if self.trio[-1] not in carta_jug:
                        jugada.append(("Trio", self.trio[-1]))
                        self.ultima_jugada.append(self.trio[-1])
                        print(self.ultima_jugada)
                    if self.seguidilla[0] not in carta_jug:
                        jugada.append(("Seguidilla", self.seguidilla[-1]))
                        self.ultima_jugada.append(self.seguidilla)
                        print(self.ultima_jugada)
                        print("Aaaaaaaaaaaaaaaaaaaa")
                        print(self.jugadas_por_jugador[id_jugador])
                    for carta in self.trio[0]:
                        for i, _carta in enumerate(self.manos[id_jugador-1]):
                            try:
                                _carta = _carta.to_dict()
                            except:
                                _carta = _carta
                            if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                self.manos[id_jugador-1].pop(i)
                                break
                    for carta in self.trio[-1]:
                        for i, _carta in enumerate(self.manos[id_jugador-1]):
                            try:
                                _carta = _carta.to_dict()
                            except:
                                _carta = _carta
                            if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                self.manos[id_jugador-1].pop(i)
                                break
                    for carta in self.seguidilla[-1]:
                        for i, _carta in enumerate(self.manos[id_jugador-1]):
                            try:
                                _carta = _carta.to_dict()
                            except:
                                _carta = _carta
                            if carta["numero"] == _carta["numero"] and carta["figura"] == _carta["figura"]:
                                self.manos[id_jugador-1].pop(i)
                                break
                    self.cancelar = False
                    self.jugadas_por_jugador[id_jugador] = jugada
                    mano_nueva = self.convertir_mano_dic(id_jugador)
                    self.modificar_cartas(id_jugador, -(len(self.trio)+len(self.seguidilla)))
                    mensajes_a_cliente.append({
                        "type": "validacion_bajarse",
                        "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                        "datos_mano_jugador": mano_nueva,
                        "jugada": self.jugadas_por_jugador[id_jugador],
                        "jugadas_jugadores": self.jugadas_por_jugador
                    })
                    mensajes_a_cliente.append({
                        "type": "mostrar_extender",
                    })
                    mensajes_a_difundir.append({
                        "type": "se_bajo_alguien",
                        "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                        "jugadas_jugadores": self.jugadas_por_jugador,
                    })
                    #=====Jesua: Verificar si la mano quedó vacía por esta acción y difundir puntuaciones
                    self.trio = {}
                    self.seguidilla = {}
                    self.seleccionando = False
            else:
                print("aqui estara una alerta de que no se pudo bajar la jugada completa")
                self.seleccionando = False
                self.seguidilla = {}
                self.trio = {}
                mensajes_a_cliente.append({
                "type": "jugada_invalida",
                })
        # Retornar tupla con (exito, mensajes_a_cliente, mensajes_a_difundir)
        exito = len(mensajes_a_cliente) > 0 or len(mensajes_a_difundir) > 0
        return (exito, mensajes_a_cliente, mensajes_a_difundir)
        
