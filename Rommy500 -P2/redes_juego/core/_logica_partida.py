"""Módulo interno para lógica de partida (inicialización, turnos, rondas)"""

import threading
import copy
from random import choice
from redes_juego import archivo_de_importaciones

importar_desde_carpeta = archivo_de_importaciones.importar_desde_carpeta
mazo_logica = importar_desde_carpeta(
    nombre_archivo="mazo.py",
    nombre_clase="Mazo",
    nombre_carpeta="logica_juego",
)
Jugador = importar_desde_carpeta(
    nombre_archivo="jugador_interfaz.py",
    nombre_clase="Jugador_interfaz",
    nombre_carpeta="logica_interfaz"
)
Carta = importar_desde_carpeta(
    nombre_archivo="cartas_interfaz.py",
    nombre_clase="Cartas_interfaz",
    nombre_carpeta="logica_interfaz"
)

class LogicaPartidaMixin:
    """Mixin con métodos para lógica de partida"""
    
    def cargar_jugadores(self,lista_jugadores):
        for i, nombre in lista_jugadores:  # mantener orden de entrada a partida
            jugador = Jugador(
                un_juego=None,
                x=0, y=0,
                ancho=0,
                alto=0,
                nro=(i),      # orden de entrada a partida
                nombre=nombre     # es string, no objeto
            )
            self.lista_jugadores_objetos.append(jugador)
            
    def jugador_mano_orden(self,lista_jugadores):
        act = True
        while act:
            indice_del_jugador_mano, nom_jug_mano = choice(list(enumerate(lista_jugadores)))
            print("indice")
            print(indice_del_jugador_mano)
            if self.clientes[indice_del_jugador_mano-1]["status"] == "activo":
                print("jugador mano elegiod")
                act = False
                print(f"El jugador mano es: {nom_jug_mano}")
                indc = indice_del_jugador_mano
                nom_jug = nom_jug_mano
        jugadores_reordenados = []
        provisional = []

        for x in range(0, indc):
            jugadores_reordenados.insert(0, lista_jugadores[x])

        for x in range(indc, len(lista_jugadores)):
            provisional.insert(0, lista_jugadores[x])

        for p in provisional:
            jugadores_reordenados.append(p)
        self.lista_jugadores_objetos_reordenados = jugadores_reordenados
        #Es una lista ordenada de acuerdo al jugador mano, ejemplo(4jugadores) j2 es mano [j2,j1,j3,j4]
        
    def inicializar_mazo(self,cantidad_de_jugadores):
        mazo = mazo_logica()
        palos = ('Pica', 'Corazon', 'Diamante', 'Trebol')
        nro_carta = ('A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K')
        nro_mazos = mazo.calcular_nro_mazos(numero_de_jugadores=cantidad_de_jugadores)
        for _ in range(nro_mazos):
            for palo in palos:
                for carta in nro_carta:
                    cart = Carta(
                        un_juego=None,
                        numero=carta,
                        figura=palo
                    )
                    mazo.agregar_cartas(cart)
            # Joker
            cart1 = Carta(
                un_juego=None,
                numero='Joker',
                figura='Especial'
            )
            mazo.agregar_cartas(cart1)
            cart2 = Carta(
                un_juego=None,
                numero='Joker',
                figura='Especial'
            )
            mazo.agregar_cartas(cart2)
        mazo.revolver_mazo()
        return mazo
        
    def iniciar_partida(self, lista_jugadores):
        # 1. Crear objetos Jugador
        #====Jesua: Resetear listas de objetos para evitar duplicados al reiniciar rondas
        self.lista_jugadores_objetos = []
        self.lista_jugadores_objetos_reordenados = []
        #==========================
        self.cargar_jugadores(lista_jugadores)
        cantidad_de_jugadores = len(self.lista_jugadores_objetos)

        # 2. Inicializar mazo
        mazo = self.inicializar_mazo(cantidad_de_jugadores)

        # 3. Revolver el mazo
        mazo.revolver_mazo()

        # 4. Decidir jugador mano
        self.jugador_mano_orden(self.lista_jugadores_objetos)
        self.jugador_mano = self.lista_jugadores_objetos_reordenados[0]

        # 5. Sacar carta de descarte
        self.descarte.append(mazo.cartas.pop(-1))
        # 6. Repartir cartas
        cantidad_jug_activos = []
        for jug in self.lista_jugadores_objetos_reordenados:
            print("jugador añadido")
            print(self.clientes[jug.nro_jugador-1])
            if self.clientes[jug.nro_jugador-1]["status"] == "activo":
                cantidad_jug_activos.append(jug)
        manos = mazo.repartir_cartas(self.lista_jugadores_objetos_reordenados)

        for jugador in self.lista_jugadores_objetos_reordenados:
            self.jugadas_por_jugador[jugador.nro_jugador] = []
        # Jesua: Inicializar acumulador de puntos por jugador (servidor como fuente de verdad).
        # Jesua: No reiniciar el acumulador entre rondas: sólo inicializar la primera vez.
        try:
            if not hasattr(self, 'puntos_acumulados') or not self.puntos_acumulados:
                self.puntos_acumulados = {jugador.nro_jugador: 0 for jugador in self.lista_jugadores_objetos_reordenados}
        except Exception:
            self.puntos_acumulados = {}
        #==========================
        # 7. Ahora sí, que mano_por_usuario configure elementos_mesa y mande a clientes
        self.mano_por_usuario(self.lista_jugadores_objetos_reordenados, manos, mazo)

    def mano_por_usuario(self, jugadores, manos, mazo):
        # ── CORRECCIÓN 1: usar índice directo en lugar de manos.pop()
        # manos.pop() sacaba del final → las manos quedaban invertidas.
        # Ahora usamos manos[idx] para que jugadores[0] reciba manos[0], etc.
        #
        # ── CORRECCIÓN 2: eliminar cartas hardcodeadas de prueba
        # El bloque anterior sobreescribía self.manos con datos fijos
        # (15 cartas al jugador 1, 9 al jugador 2), ignorando la repartición real.
        # Ahora se usa exclusivamente el resultado de repartir_cartas().
        cantidad_cartas_usuario = []
        manos_por_jugador = {}

        for idx, jugador in enumerate(jugadores):
            if self.clientes[jugador.nro_jugador - 1]["status"] != "activo":
                manos_por_jugador[jugador.nro_jugador - 1] = []
            else:
                # CORRECCIÓN 1: índice directo, no pop()
                manos_por_jugador[jugador.nro_jugador - 1] = manos[idx]
            mano_id = {
                "cantidad_mano": len(manos_por_jugador[jugador.nro_jugador - 1]),
                "id": jugador.nro_jugador,
                "nombre": jugador.nombre_jugador
            }
            cantidad_cartas_usuario.append(mano_id)
            print(
                f'\nCartas del jugador {jugador.nro_jugador} - '
                f'{jugador.nombre_jugador}: '
                f'{[str(c) for c in manos_por_jugador[jugador.nro_jugador - 1]]}'
            )

        # CORRECCIÓN 2: asignar las manos reales (sin hardcodear ni sobreescribir)
        self.manos = manos_por_jugador
        self.mazo = mazo
        jugardor_mano = ()
        for jugador in self.lista_jugadores_objetos_reordenados:
            if self.clientes[jugador.nro_jugador-1]["status"] == "activo":
                jugardor_mano = (jugador.nro_jugador, jugador.nombre_jugador)
                break
        "self.mazo.cartas = []"
        # Ahora elementos_mesa se llena completo en un solo lugar
        self.mesa_juego.elementos_mesa.update({
            "cantidad_manos_jugadores": cantidad_cartas_usuario,
            "dato_carta_descarte": [c.to_dict() for c in self.descarte],
            "jugador_mano": jugardor_mano,
            "datos_lista_jugadores": [(j.nro_jugador, j.nombre_jugador) for j in self.lista_jugadores_objetos_reordenados],
            "cantidad_cartas_mazo": len(mazo.cartas)
        })
        print(f"\nElemento mesa actualizado: {self.mesa_juego.elementos_mesa}\n")
        # Enviar a cada cliente su mano inicial
        for cliente in self.clientes:
            mano = self.manos[cliente['id'] - 1]
            try:
                datos_serializables_mano = [c.to_dict() for c in mano]
            except:
                datos_serializables_mano = [c for c in mano]
            mano_inicial = {
                "type": "ManoInicial",
                "mano": datos_serializables_mano,
                "cantidad_manos_jugadores": cantidad_cartas_usuario,
                "mazo": len(mazo.cartas),
                "id_jugador": cliente['id'],
                "jugador_mano": self.mesa_juego.elementos_mesa["jugador_mano"],
                "datos_lista_jugadores": self.mesa_juego.elementos_mesa["datos_lista_jugadores"],
                "dato_carta_descarte": self.mesa_juego.elementos_mesa["dato_carta_descarte"][0],
            }
            self.enviar_a_cliente(cliente['id'], mano_inicial)

    def mazo_nuevo(self,dir = None):
        print(self.quema)
        if (self.mazo.cartas == [] or self.mazo.cartas is None) and self.quema == []:
            print("mazo nuevo creado")
            cantidad_jugadores = len(self.lista_jugadores_objetos)
            mazo = self.inicializar_mazo(cantidad_jugadores)
            mazo.revolver_mazo()
            self.mazo = mazo
            self.difundir({
                "type": "Mazo_Nuevo",
                "cantidad_cartas_mazo": len(self.mazo.cartas),
                "cantidad_cartas_quema": None,
                "direccion" : dir
            })
            self.mesa_juego.elementos_mesa["cantidad_cartas_quema"] = 0
            self.quema = []
            return mazo
        elif (self.mazo.cartas == [] or self.mazo.cartas is None) and self.quema != []:
            print("se pone la quema como mazo")
            self.mazo.cartas = self.quema
            self.difundir({
                "type": "Mazo_Nuevo",
                "cantidad_cartas_mazo": len(self.mazo.cartas),
                "cantidad_cartas_quema": None,
                "direccion" : dir
            })
            self.mesa_juego.elementos_mesa["cantidad_cartas_quema"] = 0
            self.quema = []
            return self.mazo.cartas
        else:
            print("El mazo no está vacío, no se crea uno nuevo.")

    def finalizar_turno(self,id_jugador,id_siguiente):
        self.enviar_a_cliente(id_jugador,{
            "type": "Pasar_Turno",
            "jugador_mano":self.mesa_juego.elementos_mesa["jugador_mano"],
            "cantidad_manos_jugadores":self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
            "turno_robar" : False
        })

        self.enviar_a_cliente(id_siguiente,{
            "type": "Tu_Turno",
            "jugador_mano":self.mesa_juego.elementos_mesa["jugador_mano"],
            "cantidad_manos_jugadores":self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
            "turno_robar" : False
        })

        self.difundir({
            "type": "Actualizar_Etiqueta_Turno",
            "jugador_mano":self.mesa_juego.elementos_mesa["jugador_mano"],
            "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
            "turno_robar" : False
        })
        
    def modificar_cartas(self,id_buscado, cantidad):
        for jugador in self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"]:
            if jugador["id"] == id_buscado:
                jugador["cantidad_mano"] += cantidad
                return True
        return False  # si no se encontró el jugador
        
    def convertir_mano_dic(self,id_jugador):
        cartas_mano = []
        for carta in self.manos[id_jugador-1]:
            try:
                cartas_mano.append(carta.to_dict())
            except:
                cartas_mano.append(carta)
        return cartas_mano
    
    def actualizar_mano_y_notificar(self, id_jugador, cantidad_cartas, 
                                    mensaje_cliente, mensaje_difundir=None):
        """Helper para actualizar mano y notificar cambios
        
        Args:
            id_jugador: ID del jugador
            cantidad_cartas: Cantidad de cartas a modificar (positivo o negativo)
            mensaje_cliente: Dict con mensaje a enviar al cliente (se actualizará con datos_mano_jugador)
            mensaje_difundir: Dict opcional con mensaje a difundir a otros jugadores
        
        Returns:
            mano_nueva: Lista de cartas serializadas de la nueva mano
        """
        mano_nueva = self.convertir_mano_dic(id_jugador)
        self.modificar_cartas(id_jugador, cantidad_cartas)
        # Actualizar mensaje con la mano nueva si tiene la clave
        if "datos_mano_jugador" in mensaje_cliente:
            mensaje_cliente["datos_mano_jugador"] = mano_nueva
        self.enviar_a_cliente(id_jugador, mensaje_cliente)
        if mensaje_difundir:
            self.difundir(mensaje_difundir)
        return mano_nueva
        
    def extender_confirmado(self,id_jugador,id_jugador_extendido):
        self.enviar_a_cliente(id_jugador,
            {
                "type" : "validacion_extender",
                "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                "datos_mano_jugador": self.convertir_mano_dic(id_jugador),  # Se actualizará automáticamente en el helper
                "jugada" : self.jugadas_por_jugador[id_jugador],
                "jugadas_jugadores":self.jugadas_por_jugador
            })
        self.difundir_excepcion(id_jugador_extendido,{
                "type" : "se_extendio",
                "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                "jugadas_jugadores":self.jugadas_por_jugador,
            }
        )
        self.enviar_a_cliente(id_jugador_extendido,{
                "type" : "extendieron_tu_jugada",
                "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"],
                "jugadas_jugadores":self.jugadas_por_jugador,
                "jugada" : self.jugadas_por_jugador[id_jugador_extendido],
            }
        )
        try:
            self.verificar_mano_vacia_y_difundir(id_jugador)
        except Exception:
            pass
            
    def verificar_mano_vacia_y_difundir(self, id_jugador):
        # Verificar si la mano quedó vacía
        try:
            mano = self.manos.get(id_jugador - 1, [])
            if isinstance(mano, list) and len(mano) == 0 and self.clientes[id_jugador-1]["status"] == "activo":
                self.difundir_puntuaciones_finales(id_jugador)
                return True
            else:
                return None
        except Exception as e:
            print(f"Error al verificar mano vacía para el jugador {id_jugador}: {e}")
            return None
    def difundir_puntuaciones_finales(self, id_ganador):
        try:
            resultados = []
            # self.manos: dict con clave = índice (id-1) y valor = lista de Cartas
            for idx in range(len(self.mesa_juego.elementos_mesa.get("datos_lista_jugadores", []))):
                mano = self.manos.get(idx, [])
                puntos_partida = 0
                mano_serializable = []
                for carta in mano:
                    try:
                        puntos_partida += carta.valor_puntaje()
                    except Exception:
                        # Si no es objeto Carta, intentar leer como dict
                        try:
                            num = carta.get("numero")
                            if num == 'A': puntos_partida += 15
                            elif str(num) in ['10', 'J', 'Q', 'K']: puntos_partida += 10
                            elif str(num) in ['2','3','4','5','6','7','8','9']: puntos_partida += 5
                        except Exception:
                            pass
                    try:
                        mano_serializable.append(carta.to_dict())
                    except Exception:
                        # si ya es dict
                        mano_serializable.append(carta)

                # Actualizar acumulado en servidor (inicializar si hace falta)
                try:
                    if not hasattr(self, 'puntos_acumulados') or self.puntos_acumulados is None:
                        self.puntos_acumulados = {}
                    # usar id de jugador (1-based)
                    id_j = idx + 1
                    prev = self.puntos_acumulados.get(id_j, 0)
                    self.puntos_acumulados[id_j] = prev + puntos_partida
                    puntos_acum = self.puntos_acumulados[id_j]
                except Exception:
                    puntos_acum = None

                resultados.append({
                    "id": idx + 1,
                    "puntos_partida": puntos_partida,
                    "puntos_acumulados": puntos_acum,
                    "mano": mano_serializable
                })
                if puntos_acum >= 500:
                    print("jugador paso los 500 puntos")
                    print(self.clientes[id_j-1])
                    self.clientes[id_j-1]["status"] = "inactivo"
                    print(self.clientes[id_j-1])
            # Calcular siguiente ronda (ciclo 1..4)
            try:
                ronda_actual = int(self.mesa_juego.elementos_mesa.get("nro_ronda", 1))
            except Exception:
                ronda_actual = 1
            siguiente_ronda = (ronda_actual % 4) + 1
            # Actualizar estado de la mesa en el servidor
            try:
                self.mesa_juego.elementos_mesa["nro_ronda"] = siguiente_ronda
            except Exception:
                pass

            mensaje = {
                "type": "Fin_Ronda_Puntuaciones",
                "ganador": id_ganador,
                "resultados": resultados,
                "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa.get("cantidad_manos_jugadores"),
                "siguiente_ronda": siguiente_ronda
            }

            print(f"Difundiendo puntuaciones finales: {mensaje}")
            self.difundir(mensaje)
            # Si tras actualizar puntuaciones solo queda 1 jugador activo, finalizar partida
            try:
                activo = [c for c in getattr(self, 'clientes', []) if c.get('status') == 'activo']
                if len(activo) == 1:
                    ganador = activo[0]
                    nombre_ganador = ganador.get('nombre')
                    id_ganador_final = ganador.get('id')
                    try:
                        self.difundir({
                            "type": "Fin_Partida_Ganador",
                            "id_ganador": id_ganador_final,
                            "nombre_ganador": nombre_ganador,
                            "mensaje": f"PARTIDA FINALIZADA\nGANADOR ({nombre_ganador})"
                        })
                    except Exception:
                        pass
                    # Programar limpieza/retorno de partida
                    try:
                        threading.Timer(5.0, lambda: self.finalizar_partida(id_ganador_final)).start()
                    except Exception:
                        pass
                    return
            except Exception:
                pass
            # Programar inicio de la siguiente ronda poco después de notificar a los clientes.
            try:
                threading.Timer(2.1, lambda: self.iniciar_siguiente_ronda()).start()
                print("Scheduled iniciar_siguiente_ronda in 2.1s")
            except Exception as e:
                print(f"Error scheduling iniciar_siguiente_ronda: {e}")
        except Exception as e:
            print(f"Error calculando/difundiendo puntuaciones finales: {e}")

    def iniciar_siguiente_ronda(self):
        try:
            print("iniciar_siguiente_ronda fired")
            if not self.mesa_juego:
                print("No hay mesa activa para iniciar la siguiente ronda")
                return
            datos = self.mesa_juego.elementos_mesa.get("datos_lista_jugadores", [])
            if not datos:
                print("No hay lista de jugadores en la mesa para reordenar")
                return
            prev_mano_id = None
            try:
                prev_mano_id = self.mesa_juego.elementos_mesa.get("jugador_mano", (None,))[0]
            except Exception:
                prev_mano_id = None
            ronda = [1,2,3,4]
            try:
                self.ronda = ronda[self.ronda]
            except Exception:
                self.ronda = 1
            # Encontrar índice del jugador mano actual en la lista (si no se encuentra, empezar desde 0)
            idx_prev = 0
            for i, t in enumerate(datos):
                try:
                    if t[0] == prev_mano_id:
                        idx_prev = i
                        break
                except Exception:
                    continue

            idx_next = (idx_prev + 1) % len(datos)
            # Nueva orden empezando por el siguiente jugador
            nueva_orden = datos[idx_next:] + datos[:idx_next]
            print(f"Iniciando nueva ronda. Nuevo orden de jugadores (comenzando por el nuevo mano): {nueva_orden}")
            # Reusar la rutina de inicio de partida con la nueva orden (esto enviará ManoInicial a clientes)
            self.descarte = []
            self.quema = []
            self.jugador_que_descarto = None
            self.iniciar_partida(nueva_orden)
            print("iniciar_siguiente_ronda completed")
        except Exception as e:
            print(f"Error iniciando siguiente ronda: {e}")

    def contar_jugadores_activos(self):
        """Retorna lista de clientes activos (status == 'activo')."""
        try:
            return [c for c in getattr(self, 'clientes', []) if c.get('status') == 'activo']
        except Exception:
            return []

    def finalizar_partida(self, id_ganador=None):
        """Acciones de limpieza al finalizar la partida.

        Actualmente: marca `estado_partida` como False, actualiza elementos_mesa
        y notifica a los clientes que regresen al menú.
        """
        try:
            self.estado_partida = False
        except Exception:
            pass
        try:
            if hasattr(self, 'mesa_juego') and self.mesa_juego:
                self.mesa_juego.elementos_mesa["partida_finalizada"] = True
        except Exception:
            pass
        try:
            # Notificar a clientes para que vuelvan al menú (el cliente maneja 'Regresando_menu')
            self.difundir({
                "type": "Regresando_menu"
            })
        except Exception:
            pass

