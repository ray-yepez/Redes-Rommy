"""Módulo interno para mostrar elementos en la mesa"""

import pygame
from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta
from recursos_graficos import constantes
from recursos_graficos.elementos_de_interfaz_de_usuario import Elemento_texto
from recursos_graficos.elementos_de_interfaz_de_usuario import BotonCarta
from recursos_graficos.elementos_de_interfaz_de_usuario import ScrollHorizontal

Mazo = importar_desde_carpeta(
    nombre_archivo="mazo_interfaz.py",
    nombre_clase="Mazo_interfaz",
    nombre_carpeta="logica_interfaz"
)


class MostrarMixin:
    """Mixin con métodos para mostrar elementos en la mesa"""
    
    def mostrar_jugador(self, mesa): 
        """Muestra todos los elementos de los jugadores"""
        alto_jugador = constantes.ELEMENTO_PEQUENO_ALTO * 0.50
        ancho_jugador = constantes.ELEMENTO_GRANDE_ANCHO * 0.40

        cantidad_jugadores = len(self.lista_jugadores_objetos)
        tipo_posiciones = "pocos_jugadores" if cantidad_jugadores < 5 else "muchos_jugadores"

        posiciones_base = self.posiciones_por_cantidad[cantidad_jugadores]
        indices = self.permutaciones_por_jugador[cantidad_jugadores][self.elementos_mesa["id_jugador"]]
        posiciones = [posiciones_base[i] for i in indices]

        self.cargar_elementos_jugadores(mesa, posiciones, ancho_jugador, alto_jugador)

    def mostrar_manos(self, mesa):
        """Muestra las manos de todos los jugadores"""
        for i, jugador_list in enumerate(self.elementos_mesa["cantidad_manos_jugadores"]):
            jugador = self.lista_jugadores_objetos[i]

            # Usar método reutilizable
            dx, dy = self.calcular_desplazamiento_mano(jugador)
            x, y, dx, dy = self.determinar_ubicacion_mano(jugador, dx, dy)

            es_local = (self.elementos_mesa["id_jugador"] == jugador.nro_jugador)
            escala = constantes.ESCALA_CARTAS if es_local else constantes.ESCALA_DEMAS_CARTAS

            mano_jugador_i = []
            if not es_local:
                self.agregar_manos_jugadores(mesa, jugador_list["cantidad_mano"], jugador, escala, dx, dy, x, y)
            else:
                self.agregar_mi_mano(mesa, mano_jugador_i, escala, dx, dy, x, y)
            self.mostrar_contador_de_cartas_manos(mesa)

    def agregar_manos_jugadores(self, mesa, cantidad_cartas, jugador, escala, dx, dy, x, y):
        """Agrega las cartas de otros jugadores (reverso)"""
        for _ in range(cantidad_cartas):
            cart_imagen = self._cartas_imagenes.get("Reverso") 

            if jugador.fila_cartas == "vertical":
                rotacion = -90 if jugador.direccion == "derecha" else 90
                cart_imagen = pygame.transform.rotate(cart_imagen, rotacion)
            mesa.agregar_imagen(cart_imagen, (x, y), escala)
            x += dx
            y += dy
            self.referencia_elementos["reversos_por_jugador"].append(mesa.imagenes[-1])

    def agregar_mi_mano(self, mesa, mano_jugador_i, escala, dx, dy, x, y):
        """Agrega las cartas de la mano local visualmente"""
        for carta in self.mano:
            cart_imagen = carta.imagen_asociada(False)
            self.determinar_turno()
            cartas_activas = not self.tu_turno
            carta_agregar = carta.Elemento_carta(mano_jugador_i, x, y, escala, cart_imagen, deshabilitado=cartas_activas,mesa=self)
            self.referencia_elementos["elementos_mis_cartas"].append(carta_agregar)
            mesa.botones.append(carta_agregar)
            x += dx
            y += dy
    #cambio lismar         
    def mostrar_contador_de_cartas_manos(self, *args, **kwargs):
        """Función desactivada: Las cartas ahora se muestran en el panel principal"""
        pass
    
    def mostrar_mi_contador_cartas_mano(self):
        return
    def mostrar_contadores_mano_jugadores(self, mesa, cantidad_cartas, x, y):
        """Agrega las cartas de otros jugadores (reverso)"""
        elemento_cantidad_carta = Elemento_texto(
            un_juego=self.un_juego,
            texto=str(int(cantidad_cartas)),
            ancho=constantes.ELEMENTO_PEQUENO_ANCHO*0.1,
            alto=constantes.ELEMENTO_PEQUENO_ALTO*0.37,
            x=x,
            y=y,
            tamaño_fuente=constantes.F_PEQUENA,
            fuente=constantes.FUENTE_LLAMATIVA,
            color=constantes.ELEMENTO_FONDO_PRINCIPAL,
            radio_borde=constantes.REDONDEO_NORMAL,
            color_texto=constantes.COLOR_TEXTO_PRINCIPAL,
            color_borde=constantes.ELEMENTO_BORDE_SECUNDARIO,
            grosor_borde=constantes.BORDE_INTERMEDIO
        )
        self.referencia_elementos["contadores_mano_por_jugador"].append(elemento_cantidad_carta)
        mesa.overlays.append(elemento_cantidad_carta)

    def mostrar_jugadas(self, mesa):
        self.cargar_dato_jugadas_jugadores()
        self.preparar_estructura_visual()  # Nuevo: post-procesar para fusión visual
        self.cargar_elementos_jugadas()
        self.cargar_dato_jugada_jugador()
        self.cargar_elemento_mi_jugada()
        
        # Iterar sobre IDs con jugadas VISUALES (post-fusionadas)
        print(f"DEBUG mostrar_jugadas: visual_jugadas_jugadores.keys() = {list(self.visual_jugadas_jugadores.keys())}")
        for id_jugador_str in self.visual_jugadas_jugadores.keys():
            id_jugador = int(id_jugador_str)  # Convertir string a int
            print(f"DEBUG: Buscando jugador con nro_jugador={id_jugador}")
            try:
                jugador = next(j for j in self.lista_jugadores_objetos if j.nro_jugador == id_jugador)
                print(f"DEBUG: Jugador encontrado: {jugador.nombre_jugador}")
            except StopIteration:
                print(f"DEBUG: Jugador {id_jugador} NO encontrado en lista_jugadores_objetos")
                continue
            
            # Usar método reutilizable
            dx, dy = self.calcular_desplazamiento_mano(jugador)
            x, y, dx, dy = self.determinar_ubicacion_jugada(jugador,dx,dy)

            es_local = (self.elementos_mesa["id_jugador"] == jugador.nro_jugador)
            escala = constantes.ESCALA_DMUCHAS_CARTAS if es_local else constantes.ESCALA_DMUCHAS_CARTAS*0.90
            
            grupos_visuales = self.visual_jugadas_jugadores[id_jugador_str]
            print(f"DEBUG: es_local={es_local}, grupos_visuales={len(grupos_visuales)} grupos")

            if es_local:
                print(f"DEBUG: Llamando agregar_mi_jugada con {len(grupos_visuales)} grupos")
                self.agregar_mi_jugada(mesa, escala, dx, dy, x, y, grupos_visuales)
            else:
                print(f"DEBUG: Llamando agregar_jugadas_jugadores con {len(grupos_visuales)} grupos")
                self.agregar_jugadas_jugadores(mesa, grupos_visuales, jugador, escala, dx, dy, x, y)
    
    
    def agregar_mi_jugada(self, mesa, escala, dx, dy, x, y, grupos_visuales):
        """Renderiza grupos visuales (post-fusión) para jugador local"""
        for grupo in grupos_visuales:
            # Detectar si es trío para spacing
            es_trio = False
            if len(grupo) >= 3:
                numeros = [str(c.numero) for c in grupo if str(c.numero).lower() != "joker"]
                if len(set(numeros)) <= 1:
                    es_trio = True
            
            spacing_factor = 0.1 if es_trio else 0.5
            
            # Renderizar cartas del grupo
            for i, carta in enumerate(grupo):
                cart_imagen = carta.imagen_asociada(False)
                mesa.agregar_imagen(cart_imagen, (x, y), escala)
                self.referencia_elementos["elementos_mi_jugada"].append(mesa.imagenes[-1])
                
                # Spacing interno del grupo
                if i < len(grupo) - 1:
                    # Espaciado especial después del primer Joker en tríos
                    if es_trio and i == 0 and str(carta.numero).lower() == "joker":
                        # Espacio grande después del primer Joker para ver la siguiente carta
                        x += dx * 0.5
                        y += dy * 0.5
                    else:
                        x += dx * spacing_factor
                        y += dy * spacing_factor
            
            # Spacing entre grupos
            x += dx * (2.5 - (spacing_factor+0.5))
            y += dy * (2.5 - (spacing_factor+0.5))
    
    def agregar_jugadas_jugadores(self, mesa, grupos_visuales, jugador, escala, dx, dy, x, y): #Actualize aqui
        """Renderiza grupos visuales (post-fusión) para otros jugadores"""
        for grupo in grupos_visuales:
            es_trio = False
            if len(grupo) >= 3:
                numeros = [str(c.numero) for c in grupo if str(c.numero).lower() != "joker"]
                if len(set(numeros)) <= 1:
                    es_trio = True

            spacing_factor = 0.1 if es_trio else 0.5
            grupo_capturado = list(grupo)

            for i, carta in enumerate(grupo):
                cart_imagen = carta.imagen_asociada(False)

                if jugador.fila_cartas == "vertical":
                    rotacion = -90 if jugador.direccion == "derecha" else 90
                    cart_imagen = pygame.transform.rotate(cart_imagen, rotacion)

                # Crear botón clickeable con BotonCarta
                accion = lambda g=grupo_capturado, j=jugador: self.mostrar_modal_jugada(mesa, g, j)
                boton_carta = BotonCarta(
                    un_juego=self.un_juego,
                    imagen_carta=cart_imagen,
                    x=x,
                    y=y,
                    escala=escala,
                    accion=accion,
                )
                mesa.botones.append(boton_carta)
                self.referencia_elementos["elementos_jugadas_jugadores"].append(boton_carta)

                if i < len(grupo) - 1:
                    if es_trio and i == 0 and str(carta.numero).lower() == "joker":
                        x += dx * 0.5
                        y += dy * 0.5
                    else:
                        x += dx * spacing_factor
                        y += dy * spacing_factor

            x += dx * (3.6 - (spacing_factor + 0.5))
            y += dy * (3.6 - (spacing_factor + 0.5))

    def mostrar_modal_jugada(self, mesa, grupo, jugador):# Añadi aqui
        """Muestra un overlay/modal con las cartas de la jugada en grande""" 
        from recursos_graficos.elementos_de_interfaz_de_usuario import Boton

        # Limpiar modal anterior si existe
        if hasattr(self, '_modal_jugada_activo') and self._modal_jugada_activo:
            for elem in self._modal_jugada_activo:
                if elem in mesa.overlays:
                    mesa.overlays.remove(elem)
            self._modal_jugada_activo = []

        # Dimensiones del modal centrado
        ancho_modal = int(constantes.ANCHO_VENTANA * 0.6)
        alto_modal = int(constantes.ALTO_VENTANA * 0.4)
        x_modal = (constantes.ANCHO_VENTANA - ancho_modal) // 2
        y_modal = (constantes.ALTO_VENTANA - alto_modal) // 2

        # Fondo del modal con imagen
        imagen_fondo_modal = pygame.image.load("assets/Imagenes/fondos/ver_cartas.png").convert_alpha()
        imagen_fondo_modal = pygame.transform.smoothscale(imagen_fondo_modal, (ancho_modal, alto_modal))
        superficie_modal = imagen_fondo_modal

        # Título con nombre del jugador (izquierda) y botón cerrar (derecha), misma fila
        ancho_titulo = int(ancho_modal * 0.65)
        alto_titulo_elem = int(constantes.ELEMENTO_PEQUENO_ALTO * 0.5)
        ancho_btn = int(constantes.ELEMENTO_PEQUENO_ANCHO * 0.25)
        alto_btn = alto_titulo_elem

        espacio_entre = 10
        ancho_total = ancho_titulo + espacio_entre + ancho_btn
        x_inicio = x_modal + (ancho_modal - ancho_total) // 2
        y_fila = y_modal + 35

        titulo = Boton(
            un_juego=self.un_juego,
            texto=f"Jugada de {jugador.nombre_jugador}",
            ancho=ancho_titulo,
            alto=alto_titulo_elem,
            x=x_inicio,
            y=y_fila,
            tamaño_fuente=constantes.F_PEQUENA,
            fuente=constantes.FUENTE_LLAMATIVA,
            color=constantes.ELEMENTO_FONDO_PRINCIPAL,
            radio_borde=constantes.REDONDEO_NORMAL,
            color_texto=constantes.COLOR_TEXTO_PRINCIPAL,
            color_borde=constantes.ELEMENTO_BORDE_PRINCIPAL,
            grosor_borde=2,
            accion=None,
        )

        escala_modal = constantes.ESCALA_CARTAS * 1.4
        padding = 20
        alto_fila_superior = alto_titulo_elem + 15

        scroll = ScrollHorizontal(
            un_juego=self.un_juego,
            x=x_modal + padding + 30,
            y=y_modal + alto_fila_superior,
            ancho_visible=ancho_modal - padding * 2 - 65,
            alto=alto_modal - alto_fila_superior - 15,
        )

        x_carta = 40  # posición LOCAL dentro del scroll
        for carta in grupo:
            cart_imagen = carta.imagen_asociada(False)
            w = int(cart_imagen.get_width() * escala_modal)
            h = int(cart_imagen.get_height() * escala_modal)
            imagen_escalada = pygame.transform.smoothscale(cart_imagen, (w, h))
            scroll.agregar_imagen(imagen_escalada, x_carta, 20)
            x_carta += w + 10
        x_btn = x_inicio + ancho_titulo + espacio_entre
        y_btn = y_fila

        def cerrar():
            for elem in self._modal_jugada_activo:
                if elem in mesa.overlays:
                    mesa.overlays.remove(elem)
            self._modal_jugada_activo = []

        boton_cerrar = Boton(
            un_juego=self.un_juego,
            texto="Cerrar",
            ancho=ancho_btn,
            alto=alto_btn,
            x=x_btn,
            y=y_btn,
            tamaño_fuente=constantes.F_PEQUENA,
            fuente=constantes.FUENTE_ESTANDAR,
            color=constantes.AZUL_PRINCIPAL,
            radio_borde=constantes.REDONDEO_NORMAL,
            color_texto=constantes.BLANCO,
            color_borde=constantes.NEGRO,
            grosor_borde=2,
            color_borde_hover=constantes.NARANJA,
            color_borde_clicado=constantes.VERDE_CLARO,
            accion=cerrar,
        )

        self._modal_jugada_activo = [
            (superficie_modal, (x_modal, y_modal)),
            titulo,
            scroll,
            boton_cerrar,
        ]
        for elem in self._modal_jugada_activo:
            mesa.overlays.append(elem)

    def mostrar_carta_descarte(self, mesa, x, y, escala):
        """Muestra la carta de descarte"""
        if self.carta_descarte is None:
            return
        mesa.agregar_imagen(self.carta_descarte.imagen_asociada(False), (x, y), escala)
        self.referencia_elementos["elemento_carta_descarte"] = mesa.imagenes[-1] #guardamos la referencia de la carta que acabamos de agregar
    
    def mostrar_carta_quema(self, mesa, x, y, escala):
        """Muestra la carta de quema"""
        
        self.cargar_dato_carta_quema()
        self.cargar_elemento_carta_quema()
        if self.carta_quema is None:
            return
        if self.referencia_elementos["elemento_carta_quema"] is not None:
            mesa.imagenes.remove(self.referencia_elementos["elemento_carta_quema"])
            self.referencia_elementos["elemento_carta_quema"] = None
        mesa.agregar_imagen(self.carta_quema.imagen_asociada(False), (x, y), escala)
        self.referencia_elementos["elemento_carta_quema"] = mesa.imagenes[-1] #guardamos la referencia de la carta que acabamos de agregar
    
    def mostrar_mazo(self, mesa, x, y, scala, accion):
        """Muestra el mazo de robar"""
        mazo = Mazo(self.elementos_mesa["cantidad_cartas_mazo"], x, y, scala, accion, un_juego=self.un_juego)
        mesa.botones.append(mazo.elemento_mazo)
        self.referencia_elementos["elemento_mazo"] = mesa.botones[-1]

    def mostrar_mazo_quema(self, mesa, x, y, scala, accion):
        """Muestra el mazo de descarte"""
        mazo = Mazo(self.elementos_mesa["cantidad_cartas_quema"], x, y, scala, accion, un_juego=self.un_juego)
        mesa.botones.append(mazo.elemento_mazo)
        self.mazo_quema = mazo
        self.referencia_elementos["elemento_mazo_quema"] = mesa.botones[-1]
 #cambio lismar
    def crear_indicador_turno(self, mesa):
        """Muestra el cartel de turno con fondo vinotinto y letras blancas"""
        self.determinar_turno()
        nombre_jugador_turno = self.elementos_mesa["jugador_mano"][1]
        
        #color_vinotinto = (128, 0, 32)
        color_blanco = (255, 255, 255)
        color_dorado = (218, 165, 32)
        
        # ─── CAMBIO: Definición de colores dinámicos para las letras ───
        if self.tu_turno:
            texto = f"¡TU TURNO! - {nombre_jugador_turno}"
            color_borde = constantes.NARANJA
            color_texto_actual = constantes.NARANJA  # Letras naranjas si es tu turno
        else:
            texto = f"Turno de: {nombre_jugador_turno}"
            color_borde = color_dorado
            color_texto_actual = color_dorado       # Letras doradas para los demás turnos
        # ──────────────────────────────────────────────────────────────
        
        ancho = constantes.ELEMENTO_PEQUENO_ANCHO * 0.70
        alto = constantes.ELEMENTO_PEQUENO_ALTO / 2
        x = (constantes.ANCHO_MENU_MESA - ancho) * 0.02
        y = (constantes.ALTO_MENU_MESA - alto) * 0.02

        # Imagen base del indicador de turno
        try:
            ruta_base = importar_desde_carpeta(
                nombre_archivo="Imagenes/botones/boton_base.png",
                nombre_carpeta="assets"
            )

            img_base = pygame.image.load(ruta_base).convert_alpha()
            img_base = pygame.transform.smoothscale(
                img_base,
                (int(ancho), int(alto))
            )

            mesa.agregar_imagen(img_base, (x, y), 1)

        except Exception as e:
            print(f"Error cargando boton_base.png para indicador de turno: {e}")

        x_texto = x + 14
        y_texto = y + 8
        
        indicador = Elemento_texto(
            un_juego=self.un_juego,
            texto=texto,
            ancho=ancho,
            alto=alto,
            x=x_texto,
            y=y_texto,
            tamaño_fuente=27,                  # Se mantiene tu tamaño de letra original
            fuente=constantes.FUENTE_ESTANDAR, 
            color=None,                        # sin fondo
            radio_borde=0,
            color_texto=color_texto_actual,    # CAMBIO: Ahora aplica el color dorado/naranja
            color_borde=color_borde,
            grosor_borde=0
        )
        self.referencia_elementos["indicador_turno"] = indicador
        mesa.botones.append(indicador)