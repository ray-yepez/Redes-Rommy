"""Módulo interno para carga y preparación de datos"""

from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta

Carta = importar_desde_carpeta(
    nombre_archivo="cartas_interfaz.py",
    nombre_clase="Cartas_interfaz",
    nombre_carpeta="logica_interfaz"
)
Jugador = importar_desde_carpeta(
    nombre_archivo="jugador_interfaz.py",
    nombre_clase="Jugador_interfaz",
    nombre_carpeta="logica_interfaz"
)


class CargaDatosMixin:
    """Mixin con métodos para carga y preparación de datos"""
    
    def preparar_datos_objetos(self):
        """Prepara todos los objetos del juego a partir de los datos del servidor"""
        self.cargar_datos_listas_jugador()
        self.cargar_datos_mano_jugador()
        self.cargar_dato_carta_descarte()
        self.cargar_dato_carta_quema()
        self._cartas_imagenes = self.un_juego._cartas_imagenes

    def cargar_dato_carta_descarte(self):
        """Carga la carta de descarte desde los datos del servidor"""
        registro = self.elementos_mesa["dato_carta_descarte"]
        if registro is None:
            return
        if self.carta_descarte is not None:
            if self.carta_descarte.to_dict() == self.elementos_mesa["dato_carta_descarte"]:
                return
        carta = Carta(numero=registro["numero"], figura=registro["figura"])
        self.carta_descarte = carta

    def cargar_datos_listas_jugador(self):
        """Carga la lista de jugadores desde los datos del servidor"""
        registros_jugadores = self.elementos_mesa["datos_lista_jugadores"]
        for registro in registros_jugadores:
            jugador = Jugador(nro=registro[0], nombre=registro[1])
            self.lista_jugadores_objetos.append(jugador)
        # Invalidar cache de diccionario cuando se actualiza la lista
        self._jugadores_dict = None

    def cargar_datos_mano_jugador(self):
        """Carga la mano del jugador desde los datos del servidor"""
        registro_mano = self.elementos_mesa["datos_mano_jugador"]
        
        # Si es la primera vez, crear la mano completa
        if not self.mano:
            for registro in registro_mano:
                carta = Carta(numero=registro["numero"], figura=registro["figura"])
                self.mano.append(carta)
            return
        
        # Verificar si la mano actual coincide con la del servidor
        mano_coincide = True
        if len(registro_mano) != len(self.mano):
            mano_coincide = False
        else:
            for i, carta_obj in enumerate(self.mano):
                carta_dict = carta_obj.to_dict()
                if (carta_dict["numero"] != registro_mano[i]["numero"] or 
                    carta_dict["figura"] != registro_mano[i]["figura"]):
                    mano_coincide = False
                    break
        
        # Si no coincide, reemplazar toda la mano
        if not mano_coincide:
            self.mano.clear()
            for registro in registro_mano:
                carta = Carta(numero=registro["numero"], figura=registro["figura"])
                self.mano.append(carta)

    def cargar_dato_jugada_jugador(self):
        registro_jugada = self.elementos_mesa["jugada"]
        self.jugada.clear()
        for y,x in registro_jugada:
            for registro in x:
                print(registro)
                carta = Carta(numero=registro["numero"], figura=registro["figura"])
                self.jugada.append(carta)
    
    def cargar_dato_jugadas_jugadores(self):
        self.jugadas_jugadores = {}  # Reiniciar estructura
        for id_jugador, lista_jugada in self.elementos_mesa["jugadas_jugadores"].items():
            cartas = []
            print(lista_jugada)
            for y,x in lista_jugada:
                print(y)
                for registro in x:
                    print(registro)
                    carta = Carta(numero=registro["numero"], figura=registro["figura"])
                    cartas.append(carta)
            self.jugadas_jugadores[id_jugador] = cartas
    
    def preparar_estructura_visual(self):
        """
        Post-procesa self.jugadas_jugadores (que YA tiene objetos Carta con imágenes cargadas)
        para crear self.visual_jugadas_jugadores con tríos fusionados.
        
        NO modifica ningún dato original, solo crea una estructura visual.
        """
        print("DEBUG preparar_estructura_visual - INICIO")
        print(f"jugadas_jugadores keys: {list(self.jugadas_jugadores.keys())}")
        
        self.visual_jugadas_jugadores = {}
        trios_existentes = {}  # {numero_carta: (id_jugador_dueño, idx_grupo)}
        
        # Verificar si hay datos
        if not self.jugadas_jugadores:
            print("DEBUG: No hay jugadas_jugadores para procesar")
            return
        
        # Procesar cada jugador
        for id_jugador_str, lista_cartas_planas in self.jugadas_jugadores.items():
            self.visual_jugadas_jugadores[id_jugador_str] = []
            
            print(f"DEBUG: Procesando jugador {id_jugador_str}, total cartas: {len(lista_cartas_planas)}")
            
            # Necesitamos reconstruir los grupos desde elementos_mesa
            if id_jugador_str not in self.elementos_mesa["jugadas_jugadores"]:
                print(f"DEBUG: Jugador {id_jugador_str} no tiene jugadas en elementos_mesa")
                continue
                
            lista_jugada = self.elementos_mesa["jugadas_jugadores"][id_jugador_str]
            idx_carta_global = 0
            
            # Procesar cada grupo (tag, subjugada)
            for tag, subjugada in lista_jugada:
                num_cartas_grupo = len(subjugada)
                # Reutilizar las cartas correspondientes de self.jugadas_jugadores (CON imágenes cargadas)
                cartas_grupo = lista_cartas_planas[idx_carta_global:idx_carta_global + num_cartas_grupo]
                idx_carta_global += num_cartas_grupo
                
                print(f"DEBUG: tag={tag}, {len(cartas_grupo)} cartas")
                
                # Detectar si es trío
                es_trio = False
                numero_trio = None
                if len(cartas_grupo) >= 3:
                    numeros = [str(c.numero) for c in cartas_grupo if str(c.numero).lower() != "joker"]
                    if len(set(numeros)) <= 1:  # Todos del mismo número
                        es_trio = True
                        if numeros:
                            numero_trio = numeros[0]
                        elif len(cartas_grupo) > 0:
                            numero_trio = str(cartas_grupo[0].numero)
                
                # Lógica de fusión
                fusionado = False
                ronda = getattr(self, 'ronda_actual', 1)
                
                if ronda >= 0 and es_trio and numero_trio:
                    if numero_trio in trios_existentes:
                        # YA EXISTE: fusionar con el dueño original
                        id_dueño, idx_grupo_dueño = trios_existentes[numero_trio]
                        # Agregar cartas al trío existente (se ordenarán después)
                        self.visual_jugadas_jugadores[id_dueño][idx_grupo_dueño].extend(cartas_grupo)
                        fusionado = True
                        print(f"DEBUG: Trío fusionado! numero={numero_trio}, dueño={id_dueño}")
                    else:
                        # PRIMER trío de este número: registrar como dueño
                        idx_nuevo = len(self.visual_jugadas_jugadores[id_jugador_str])
                        trios_existentes[numero_trio] = (id_jugador_str, idx_nuevo)
                        print(f"DEBUG: Nuevo trío registrado, numero={numero_trio}, dueño={id_jugador_str}")
                
                #Si no se fusionó, agregar como grupo normal
                if not fusionado:
                    # Ordenar cartas del trío con Jokers primero si es un trío
                    if es_trio:
                        cartas_grupo = self._ordenar_cartas_trio_con_jokers(cartas_grupo)
                    self.visual_jugadas_jugadores[id_jugador_str].append(cartas_grupo)
                    print(f"DEBUG: Grupo agregado normalmente a jugador {id_jugador_str}")
        
        # Ordenar todos los tríos después de fusionarlos
        for id_jugador_str, grupos in self.visual_jugadas_jugadores.items():
            for i, grupo in enumerate(grupos):
                # Detectar si es trío
                if len(grupo) >= 3:
                    numeros = [str(c.numero) for c in grupo if str(c.numero).lower() != "joker"]
                    if len(set(numeros)) <= 1:  # Es un trío
                        self.visual_jugadas_jugadores[id_jugador_str][i] = self._ordenar_cartas_trio_con_jokers(grupo)
        
        print(f"DEBUG preparar_estructura_visual - FIN, visual_jugadas_jugadores: {list(self.visual_jugadas_jugadores.keys())}")
    
    def _ordenar_cartas_trio_con_jokers(self, cartas):
        """
        Ordena las cartas de un trío poniendo Jokers con prioridad:
        1. Primer Joker (si existe)
        2. Primera carta NO-Joker (para mostrar el número del trío)
        3. Resto de cartas intercaladas
        4. ÚLTIMA carta SIEMPRE debe ser NO-Joker (para claridad visual)
        """
        jokers = [c for c in cartas if str(c.numero).lower() == "joker"]
        no_jokers = [c for c in cartas if str(c.numero).lower() != "joker"]
        
        if not jokers:
            # No hay Jokers, devolver como está
            return cartas
        
        if not no_jokers:
            # Solo hay Jokers (caso extremadamente raro)
            return jokers
        
        if len(jokers) == 1:
            # Un solo Joker: Joker primero, luego el resto
            return [jokers[0]] + no_jokers
        
        # Más de un Joker: 
        # 1er Joker, 1era carta normal, Jokers intermedios, resto cartas normales (última debe ser normal)
        resultado = [jokers[0]]
        
        if len(no_jokers) == 1:
            # Solo hay 1 carta normal: Jokers primero, carta normal al final
            resultado.extend(jokers[1:])
            resultado.append(no_jokers[0])
        else:
            # Hay múltiples cartas normales
            # Formato: Joker → Número → Jokers_intermedios → Números_restantes
            resultado.append(no_jokers[0])
            # Jokers adicionales en medio
            resultado.extend(jokers[1:])
            # Resto de números (garantizando que el último sea número)
            resultado.extend(no_jokers[1:])
        
        return resultado
    
    def cargar_dato_carta_quema(self):
        registro = self.elementos_mesa["dato_carta_quema"]
        if registro is None:
            return
        if self.carta_quema is not None:
            if self.carta_quema.to_dict() == self.elementos_mesa["dato_carta_quema"]:
                return
        carta = Carta(numero=registro["numero"], figura=registro["figura"])
        self.carta_quema = carta

