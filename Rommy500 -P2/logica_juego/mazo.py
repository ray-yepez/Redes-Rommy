from random import sample, shuffle
class Mazo:
    def __init__(self):
        self.cartas = []
    def agregar_cartas(self,carta):
        self.cartas.append(carta)
    def calcular_nro_mazos(self,numero_de_jugadores):
        resultado = numero_de_jugadores // 3  
        if numero_de_jugadores % 3 != 0:
            resultado += 1
        return resultado
    def revolver_mazo(self):
        shuffle(self.cartas)

    def mostrar_cartas(self,mensaje):
        print(mensaje)
        for carta in self.cartas:
            print(carta)
    def mostrar_numero_cartas(self,mensaje):
        print(str(mensaje) + str(len(self.cartas)))
    # def repartir_cartas(self, lista_de_jugadores):
    #     num_jugadores = len(lista_de_jugadores)
    #     jugadores = [[] for _ in range(num_jugadores)]
    #     cartas_especiales_por_id = {
    #         2: [  # Jugador con ID 2
    #             {'numero': '3', 'figura': 'Diamante'},
    #             {'numero': '2', 'figura': 'Corazon'},
    #             {'numero': '3', 'figura': 'Corazon'},
    #             {'numero': '4', 'figura': 'Corazon'},
    #             {'numero': '5', 'figura': 'Corazon'},
    #             {'numero': '6', 'figura': 'Corazon'},
    #             {'numero': '7', 'figura': 'Corazon'},
    #             {'numero': '8', 'figura': 'Trebol'},
    #             {'numero': '8', 'figura': 'Diamante'},
    #             {'numero': 'Joker', 'figura': 'Especial'}
    #             ],
    #         1: [  # Jugador con ID 1
    #             {'numero': '2', 'figura': 'Pica'},
    #             {'numero': '3', 'figura': 'Pica'},
    #             {'numero': '4', 'figura': 'Pica'},
    #             {'numero': '5', 'figura': 'Pica'},
    #             {'numero': '6', 'figura': 'Pica'},
    #             {'numero': '7', 'figura': 'Pica'},
    #             {'numero': '8', 'figura': 'Corazon'},
    #             {'numero': '8', 'figura': 'Pica'},
    #             {'numero': '2', 'figura': 'Corazon'},
    #             {'numero': 'Joker', 'figura': 'Especial'}
    #             ]}

    #     cartas_especiales_por_id = cartas_especiales_por_id or {}

    #     # 🔹 Paso 1: Asignar cartas especiales
    #     for idx, jugador in enumerate(lista_de_jugadores):
    #         id_jugador = jugador.nro_jugador
    #         especiales = cartas_especiales_por_id.get(id_jugador, [])
    #         for carta_especial in especiales:
    #             for carta in self.cartas:
    #                 if str(carta.numero) == str(carta_especial['numero']) and str(carta.figura) == str(carta_especial['figura']):
    #                     jugadores[idx].append(carta)
    #                     self.cartas.remove(carta)
    #                     break  # Evita duplicados si hay más de una carta igual

    #     # 🔹 Paso 2: Calcular cuántas cartas faltan para cada jugador
    #     cartas_faltantes_total = sum(10 - len(mano) for mano in jugadores)

    #     # 🔹 Paso 3: Seleccionar cartas aleatorias del mazo
    #     cartas_indice_repartidas = sample(list(enumerate(self.cartas)), cartas_faltantes_total)
    #     cartas_repartidas = [x[1] for x in cartas_indice_repartidas]
    #     indice_de_cartas_eliminar = [x[0] for x in cartas_indice_repartidas]

    #     # 🔹 Paso 4: Repartir cartas faltantes
    #     index = 0
    #     for i in range(num_jugadores):
    #         faltantes = 10 - len(jugadores[i])
    #         for _ in range(faltantes):
    #             if index < len(cartas_repartidas):
    #                 jugadores[i].append(cartas_repartidas[index])
    #                 index += 1

    #     # 🔹 Paso 5: Eliminar cartas del mazo
    #     for indice in sorted(indice_de_cartas_eliminar, reverse=True):
    #         if indice < len(self.cartas):
    #             self.cartas.pop(indice)

    #     return jugadores
    def repartir_cartas(self,lista_de_jugadores):
        num_jugadores = len(lista_de_jugadores)
        cartas_indice_repartidas = sample(list(enumerate(self.cartas)), 10*num_jugadores)
        cartas_repartidas = [] #Cartas a repartir
        indice_de_cartas_eliminar = [] #Indice de cartas a eliminar
        for x in cartas_indice_repartidas:
            cartas_repartidas.append(x[1])
            indice_de_cartas_eliminar.append(x[0])
        jugadores = [] #lista que guardara una lista con cartas para cada jugadores [[],[],..]
        for _ in range(num_jugadores):
            jugadores.append([])
        for index, carta in enumerate(cartas_repartidas):
            indice_de_jugador = index % num_jugadores
            jugadores[indice_de_jugador].append(carta)

        for indice in sorted(indice_de_cartas_eliminar,reverse=True):
            self.cartas.pop(indice)
        
        #El sorted(lista) -> Se encarga de ordenar en forma ascendente por defecto, sin embargo el reverse="True" hace que se ordene en forma descendente, ademas el sorted(lista) no modifica la lista, el literalmente crea otra lista. El ciclo de antes funciona asi: al aplicar el sorted al indice_de_cartas_eliminar, por ejemplo. indice_de_cartas_eliminar = [1,2,5,9,3] el sorted lo deja, [9,5,3,2,1] entonces el ciclo en su primer valor tomara 9, se borra de las cartas, la carta que estaba en la posicion 9. 
        
        return jugadores