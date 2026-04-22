"""Módulo interno para sistema de puntos"""

from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta
import pygame
from recursos_graficos import constantes
from recursos_graficos.elementos_de_interfaz_de_usuario import Elemento_texto, CartelAlerta

Menu = importar_desde_carpeta("menu.py","Menu","recursos_graficos")


class PuntosMixin:
    """Mixin con métodos para sistema de puntos"""
    
    def calcular_puntos_carta(self, carta):
        """Calcula los puntos de una carta según las reglas del Rummy 500"""
        try:
            num = carta.numero 
        except Exception:
            try:
                # En caso de que carta no tenga atributo numero, tratar como dict-like
                num = carta.get("numero")
            except Exception:
                return 0
        #Normalizar a string para comparaciones simples
        if isinstance(num, int):
            num_str = str(num)
        elif isinstance(num, str):
            num_str = num
        else:
            num_str = str(num)

        #Joker
        if num_str.lower() == 'joker':
            return 25
        
        #As
        if num_str == 'A':
            return 15
        
        #10-K
        if num_str in ['10', 'J', 'Q', 'K']:
            return 10
        #2-9
        if num_str in ['2', '3', '4', '5', '6', '7', '8', '9']:
            return 5

        # Si no coincide con ninguna, devolver 0
        return 0

        
    def calcular_puntos_mano(self, mano):
        """Calcula los puntos totales de una mano"""
        puntos = 0
        for carta in mano:
            puntos += self.calcular_puntos_carta(carta)
        return puntos
    
    def crear_contador_puntos(self, mesa):
        """Muestra el contador de puntos en la interfaz"""
        ancho = constantes.ELEMENTO_PEQUENO_ANCHO * 0.35
        alto = constantes.ELEMENTO_PEQUENO_ALTO * 0.4
        
        # Posición en esquina superior izquierda
        x = (constantes.ANCHO_MENU_MESA - ancho) - 100
        y = 10
        
        # Mostrar puntos acumulados si están disponibles (como en la tabla de puntuación)
        try:
            id_local = self.elementos_mesa.get("id_jugador")
            if id_local is not None:
                puntos_mostrar = self.obtener_puntos_jugador(id_local)
            else:
                puntos_mostrar = getattr(self, 'puntos_acumulados', getattr(self, 'puntos_ronda_actual', 0))
        except Exception:
            puntos_mostrar = getattr(self, 'puntos_acumulados', getattr(self, 'puntos_ronda_actual', 0))

        texto_puntos = f"Tus Puntos: {puntos_mostrar}"
        
        contador = Elemento_texto(
            un_juego=self.un_juego,
            texto=texto_puntos,
            ancho=ancho,
            alto=alto,
            x=x,
            y=y,
            tamaño_fuente=constantes.F_PEQUENA,
            fuente=constantes.FUENTE_ESTANDAR,
            color=constantes.ELEMENTO_FONDO_PRINCIPAL,
            radio_borde=constantes.REDONDEO_NORMAL,
            color_texto=constantes.COLOR_TEXTO_PRINCIPAL,
            color_borde=constantes.ELEMENTO_BORDE_SECUNDARIO,
            grosor_borde=constantes.BORDE_INTERMEDIO
        )
        
        mesa.botones.append(contador)
        # Guardar referencia para poder actualizarlo posteriormente
        self.referencia_elementos["contador_puntos"] = contador
        # Reutilizar `CartelAlerta` existente para mensaje temporal (3s)
        try:
            # Calcular tamaño y posición razonables para que no salga de pantalla
            ancho_msg = min(int(constantes.ANCHO_VENTANA * 0.35), max(300, int(ancho * 3)))
            alto_msg = max(50, int(alto * 1.65))

            # Posicionar en esquina superior derecha (margen 10px)
            y_msg = 10
            x_msg = int(constantes.ANCHO_VENTANA) - ancho_msg - 10
            if x_msg < 10:
                x_msg = 10

            # Crear cartel reutilizando la clase existente
            cartel = CartelAlerta(
                self.un_juego.pantalla,
                "Mantén TAB para ver la tabla de puntuaciones",
                x_msg,
                y_msg,
                ancho=ancho_msg,
                alto=alto_msg,
                mostrar_boton_cerrar=False,
                duracion_ms=3000
            )
            # Ajustar fuente a tamaño más pequeño para que el texto quepa
            try:
                cartel.fuente = pygame.font.SysFont(constantes.FUENTE_LLAMATIVA, max(25, int(constantes.F_PEQUENA * 0.7)))
                cartel.preparar_texto()
            except Exception:
                pass

            cartel.tiempo_mostrado = pygame.time.get_ticks()
            cartel.visible = True
            if not hasattr(mesa, 'overlays'):
                mesa.overlays = []
            mesa.overlays.append(cartel)
        except Exception:
            pass

        return contador

    def crear_menu_puntuacion(self):
        """Crea el menú de puntuación usando la clase Menu"""
        try:
            # Calcular dimensiones basadas en número de jugadores
            jugadores_datos = self.elementos_mesa.get("datos_lista_jugadores") or []
            if jugadores_datos:
                num = len(jugadores_datos)
            else:
                num = len(self.lista_jugadores_objetos) or 1

            ancho_menu = int(constantes.ANCHO_VENTANA * 0.36)
            alto_fila = max(28, int(constantes.F_MEDIANA * 0.6))
            alto_menu = int(120 + num * alto_fila)

            x, y = self.un_juego.centrar(ancho_menu, alto_menu)

            # Crear el menú
            self.menu_puntuacion = Menu(
                self.un_juego,
                ancho_menu,
                alto_menu,
                x,
                y,
                constantes.ELEMENTO_FONDO_PRINCIPAL,
                constantes.ELEMENTO_BORDE_PRINCIPAL,
                constantes.BORDE_PRONUNCIADO,
                constantes.REDONDEO_INTERMEDIO
            )

            # Crear elementos de texto
            self.crear_elementos_menu_puntuacion()

        except Exception as e:
            print(f"Error al crear menú de puntuación: {e}")

    def crear_elementos_menu_puntuacion(self):
        """Crea los elementos de texto del menú de puntuación"""
        try:
            menu = self.menu_puntuacion
            if menu is None:
                return

            # Limpiar elementos anteriores si existen
            menu.botones.clear()
            # Título
            menu.crear_elemento(
                Clase=Elemento_texto,
                x=(menu.ancho // 2) - 100,
                y=15,
                un_juego=self.un_juego,
                texto="TABLA DE PUNTOS",
                ancho=200,
                alto=30,
                tamaño_fuente=max(16, int(constantes.F_GRANDE * 0.38)),
                fuente=constantes.FUENTE_ESTANDAR,
                color=constantes.ELEMENTO_FONDO_PRINCIPAL,
                radio_borde=0,
                color_texto=constantes.COLOR_TEXTO_PRINCIPAL,
                color_borde=constantes.ELEMENTO_BORDE_PRINCIPAL,
                grosor_borde=0
            )

            # Encabezados
            alto_fila = max(28, int(constantes.F_MEDIANA * 0.6))
            tamaño_fuente_fila = max(14, int(constantes.F_MEDIANA * 0.32))
            ubicaciones = [(24,56),(menu.ancho - 100,56)]
            textos = ["Jugador","Puntos"]
            for i, texto in enumerate(textos):
                if texto == textos[0]:
                    ancho = 150
                else:
                    ancho = 70
                menu.crear_elemento(
                    Clase=Elemento_texto,
                    x=ubicaciones[i][0],
                    y=ubicaciones[i][1],
                    un_juego=self.un_juego,
                    texto=texto,
                    ancho=ancho,
                    alto=alto_fila,
                    tamaño_fuente=tamaño_fuente_fila,
                    fuente=constantes.FUENTE_ESTANDAR,
                    color=constantes.ELEMENTO_FONDO_PRINCIPAL,
                    radio_borde=0,
                    color_texto=constantes.COLOR_TEXTO_PRINCIPAL,
                    color_borde=constantes.ELEMENTO_BORDE_PRINCIPAL,
                    grosor_borde=0
                )

            # Filas de jugadores
            jugadores_datos = self.elementos_mesa.get("datos_lista_jugadores") or []
            y_pos = 80

            # Construir lista de (nombre, puntos) según la fuente de datos disponible
            filas_jugadores = []
            if jugadores_datos:
                # jugadores_datos: lista de tuplas (nro, nombre) en orden de turno
                for nro, nombre in jugadores_datos:
                    puntos = self.obtener_puntos_jugador(nro)
                    filas_jugadores.append((nombre, puntos))
            else:
                # Fallback: usar objetos
                for j in self.lista_jugadores_objetos:
                    nombre = getattr(j, 'nombre_jugador', f'Jugador {getattr(j, "nro_jugador", "?")}')
                    puntos = getattr(j, 'puntos_acumulados', 0)
                    filas_jugadores.append((nombre, puntos))

            # Crear elementos de texto para cada jugador (nombre y puntos)
            for nombre, puntos in filas_jugadores:
                # Configuración común para ambos elementos
                config_comun = {
                    "Clase": Elemento_texto,
                    "un_juego": self.un_juego,
                    "alto": alto_fila,
                    "tamaño_fuente": tamaño_fuente_fila,
                    "fuente": constantes.FUENTE_ESTANDAR,
                    "color": constantes.ELEMENTO_FONDO_PRINCIPAL,
                    "radio_borde": 0,
                    "color_texto": constantes.COLOR_TEXTO_PRINCIPAL,
                    "color_borde": constantes.ELEMENTO_BORDE_PRINCIPAL,
                    "grosor_borde": 0
                }
                
                # Nombre del jugador
                menu.crear_elemento(
                    x=24,
                    y=y_pos,
                    texto=str(nombre),
                    ancho=150,
                    **config_comun
                )
                
                # Puntos del jugador
                menu.crear_elemento(
                    x=menu.ancho - 100,
                    y=y_pos,
                    texto=str(puntos),
                    ancho=80,
                    **config_comun
                )
                y_pos += alto_fila

        except Exception as e:
            print(f"Error al crear elementos del menú de puntuación: {e}")

    def mostrar_menu_puntuacion(self):
        """Muestra el menú de puntuación"""
        try:
            if not hasattr(self, 'menu_puntuacion') or self.menu_puntuacion is None:
                self.crear_menu_puntuacion()
            else:
                # Actualizar elementos si ya existe
                self.crear_elementos_menu_puntuacion()
            
            if self.menu_puntuacion:
                self.menu_puntuacion.mostrar()
        except Exception as e:
            print(f"Error al mostrar menú de puntuación: {e}")

    def ocultar_menu_puntuacion(self):
        """Oculta el menú de puntuación"""
        try:
            if hasattr(self, 'menu_puntuacion') and self.menu_puntuacion:
                self.menu_puntuacion.ocultar()
        except Exception as e:
            print(f"Error al ocultar menú de puntuación: {e}")
    
    def actualizar_puntos_jugador(self, nro_jugador, mano):
        """Actualiza los puntos de un jugador específico al final de la ronda"""
        puntos_mano = self.calcular_puntos_mano(mano)

        # Buscar el jugador y actualizar sus puntos
        for jugador in self.lista_jugadores_objetos:
            if getattr(jugador, 'nro_jugador', None) == nro_jugador:
                # asegurar atributos existentes
                setattr(jugador, 'puntos_ronda_actual', puntos_mano)
                puntos_prev = getattr(jugador, 'puntos_acumulados', 0)
                setattr(jugador, 'puntos_acumulados', puntos_prev + puntos_mano)
                # Si el jugador actualizado es el local, actualizar el contador visual
                try:
                    if self.elementos_mesa.get("id_jugador") == nro_jugador:
                        # actualizar estado interno
                        self.puntos_ronda_actual = puntos_mano
                        # actualizar elemento UI si existe
                        contador = self.referencia_elementos.get("contador_puntos")
                        if contador is not None:
                            # Mostrar puntos acumulados para el jugador local
                            puntos_local = getattr(jugador, 'puntos_acumulados', puntos_mano)
                            contador.texto = f"Tus Puntos: {puntos_local}"
                            # Algunos elementos usan prepar_texto para recalcular superficies
                            try:
                                contador.prepar_texto()
                            except Exception:
                                pass
                except Exception:
                    pass
                nombre = getattr(jugador, 'nombre', getattr(jugador, 'nombre_jugador', str(nro_jugador)))
                print(f"DEBUG: Jugador {nombre} - Puntos partida: {puntos_mano}, Acumulados: {jugador.puntos_acumulados}")
                return puntos_mano

        print(f"DEBUG: No se encontró jugador {nro_jugador} para actualizar puntos")
        return 0

    def aplicar_puntuacion_servidor(self, nro_jugador, puntos_partida, puntos_acumulados, mano):
        # Buscar el jugador y actualizar sus puntos con los valores del servidor
        for jugador in self.lista_jugadores_objetos:
            if getattr(jugador, 'nro_jugador', None) == nro_jugador:
                try:
                    setattr(jugador, 'puntos_ronda_actual', puntos_partida if puntos_partida is not None else 0)
                    setattr(jugador, 'puntos_acumulados', puntos_acumulados if puntos_acumulados is not None else getattr(jugador, 'puntos_acumulados', 0))
                    # Si es el jugador local, actualizar contador visual
                    if self.elementos_mesa.get("id_jugador") == nro_jugador:
                        self.puntos_ronda_actual = puntos_partida if puntos_partida is not None else 0
                        contador = self.referencia_elementos.get("contador_puntos")
                        if contador is not None:
                            # Mostrar puntos acumulados recibidos desde servidor
                            puntos_local = getattr(jugador, 'puntos_acumulados', getattr(self, 'puntos_ronda_actual', 0))
                            contador.texto = f"Tus Puntos: {puntos_local}"
                            try:
                                contador.prepar_texto()
                            except Exception:
                                pass
                except Exception as e:
                    print(f"Error aplicando puntuacion servidor para {nro_jugador}: {e}")
                return


    def obtener_puntos_jugador(self, nro_jugador):
        for jugador in self.lista_jugadores_objetos:
            if getattr(jugador, 'nro_jugador', None) == nro_jugador:
                return getattr(jugador, 'puntos_acumulados', 0)
        return 0

    def reiniciar_puntos_ronda_jugadores(self):
        """Reinicia los puntos de ronda actual para todos los jugadores"""
        for jugador in self.lista_jugadores_objetos:
            jugador.puntos_ronda_actual = 0
        print("DEBUG: Puntos de partida reiniciados para todos los jugadores")

