"""Mixin para el menú de cantidad de jugadores"""

import pygame
from recursos_graficos import constantes
from recursos_graficos.menu import Menu
from recursos_graficos.elementos_de_interfaz_de_usuario import Elemento_texto, BotonRadio, BotonRadioImagenes
from redes_interfaz import controladores
from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta


class MenuCantidadJugadoresMixin:
    """Mixin con métodos para el menú de selección de cantidad de jugadores"""
    
    def Menu_Cantidad_Jugadores(self):
        """Crea el menú para seleccionar cuántos jugadores jugarán (2-7)
        
        Returns:
            Menu: Instancia del menú de cantidad de jugadores
        """
        x_menu, y_menu = self.centrar(constantes.ANCHO_MENU_CNT_J, constantes.ALTO_MENU_CNT_J)
        
        menu_cantidad = Menu(
            self,
            constantes.ANCHO_MENU_CNT_J,
            constantes.ALTO_MENU_CNT_J,
            x_menu,
            y_menu,
            constantes.ELEMENTO_FONDO_SECUNDARO,
            constantes.ELEMENTO_BORDE_SECUNDARIO,
            constantes.BORDE_PRONUNCIADO,
            constantes.REDONDEO_PRONUNCIADO
        )
 
        posicion_y = self.crear_elementos_cantidad_jugadores(menu_cantidad)
        self.crear_elementos_control_cantidad_jugadores(menu_cantidad, posicion_y)
        
        self.elementos_creados.append(menu_cantidad)
        return menu_cantidad
    
    def crear_elementos_cantidad_jugadores(self, menu_cantidad):
        """Crea título y grid de radio buttons para seleccionar cantidad de jugadores
        
        Args:
            menu_cantidad: Instancia del menú
            
        Returns:
            float: Última posición Y usada (para posicionar botones de control debajo)
        """
        # Título
        ancho_seleccion = constantes.ELEMENTO_GRANDE_ANCHO * 2
        alto_seleccion = constantes.ELEMENTO_MEDIANO_ALTO * 0.95
        x_seleccion = (constantes.ANCHO_MENU_CNT_J - ancho_seleccion) * (0.5)
        y_seleccion = (constantes.ALTO_MENU_CNT_J - alto_seleccion) * (0.10)
 
        # subrayado
        x = 299
        y = 10
        ancho = 600
        
        menu_cantidad.crear_elemento(
            Clase=Elemento_texto,
            x=x_seleccion,
            y=y_seleccion,
            un_juego=self,
            texto="SELECCIONE EL NUMERO DE JUGADORES",
            ancho=ancho_seleccion,
            alto=alto_seleccion,
            tamaño_fuente=60,
            fuente=constantes.FUENTE_TITULO,
            # --- CAMBIOS AQUÍ ---
            color=None, # Cambiamos el color de fondo a None para que sea transparente
            radio_borde=0, # Quitamos el redondeo ya que no habrá fondo
            color_texto=(187, 165, 113), # Asegúrate que sea un color que resalte sobre el verde (como blanco o dorado)
            color_borde=None, # Quitamos el color del borde
            grosor_borde=0, # Ponemos el grosor del borde en 0
            # --------------------
        )
 
        # SUBRAYADO
        ruta_subrayado = importar_desde_carpeta(
            nombre_archivo="Imagenes/botones/subrayado_4.png",
            nombre_carpeta="assets"
        )
 
        img_subrayado = pygame.image.load(ruta_subrayado).convert_alpha()
 
        ancho_subrayado = 1100
        alto_subrayado = 290
 
        img_subrayado = pygame.transform.smoothscale(
            img_subrayado,
            (ancho_subrayado, alto_subrayado)
        )
 
        x_subrayado = x + (ancho - ancho_subrayado) // 2
        y_subrayado = y + 6
 
        menu_cantidad.agregar_imagen(
            img_subrayado,
            (x_subrayado, y_subrayado),
            1
        )
 
        # Radio buttons con imágenes de cartas en layout horizontal
        # Cartas que se usarán: 2 a 7 jugadores
        cartas_config = [
            ("Corazon (2).png", 2),
            ("Trebol (3).png", 3),
            ("Pica (4).png", 4),
            ("Corazon (5).png", 5),
            ("Trebol (6).png", 6),
            ("Pica (7).png", 7)
        ]
        
        grupo_radio = []
 
        # Calcular ancho total y posición inicial
        num_botones = len(cartas_config)
        ancho_boton = constantes.ELEMENTO_PEQUENO_ANCHO * 1.25   # Un poco más grandes
        alto_boton = constantes.ELEMENTO_PEQUENO_ALTO * 2.0     # Alto proporcional al nuevo ancho
        
        # Centrar horizontalmente los 6 botones
        for i, (nombre_carta, num_jugadores) in enumerate(cartas_config):
            # Posición horizontal: distribuir uniformemente entre ~0.04 y ~0.96
            posicion_x = 0.10 + (i * (1.2 / (num_botones - 1))) # el 1.2 es para separar las cartas 
            posicion_y = 0.50  # Posición vertical centrada
            
            # Cargar la imagen de la carta
            ruta_carta = importar_desde_carpeta(
                nombre_archivo=f"Imagenes/Cartas/{nombre_carta}",
                nombre_carpeta="assets"
            )
            imagen_carta = pygame.image.load(ruta_carta).convert_alpha()
            
            # Calcular escala para ajustar la carta al tamaño del botón
            scala = min(
                ancho_boton / imagen_carta.get_width(),
                alto_boton / imagen_carta.get_height()
            )
            
            x_pos = (constantes.ANCHO_MENU_CNT_J - ancho_boton) * posicion_x
            y_pos = (constantes.ALTO_MENU_CNT_J - alto_boton) * posicion_y
            
            menu_cantidad.crear_elemento(
                Clase=BotonRadioImagenes,
                un_juego=self,
                imagen=imagen_carta,
                scala=scala,
                x=x_pos,
                y=y_pos,
                radio_borde=constantes.REDONDEO_NORMAL,
                grupo=grupo_radio,
                valor=num_jugadores,
                deshabilitado=False,
                color_borde=constantes.ELEMENTO_BORDE_SECUNDARIO,
                color_borde_hover=constantes.ELEMENTO_HOVER_PRINCIPAL,
                color_borde_clicado=constantes.ELEMENTO_CLICADO_PRINCIPAL,
                arrastre_disponible=False
            )
        return posicion_y
    
    def crear_elementos_control_cantidad_jugadores(self, menu_cantidad, posicion_y):
        """Crea botones VOLVER y CONFIRMAR con imágenes personalizadas
        
        Args:
            menu_cantidad: Instancia del menú
            posicion_y: Posición Y de referencia
        """
        # 1. Definir alto fijo para que ambos botones sean iguales
        ALTO_FIJO_BOTONES = 80
        
        # Posición vertical base
        y_base = (constantes.ALTO_MENU_CNT_J - constantes.ELEMENTO_MEDIANO_ALTO) * (posicion_y + 0.43)
 
        datos_botones = [
            {
                "texto": "VOLVER",
                "archivo": "boton_volver.png",
                "accion": lambda: controladores.Mostrar_seccion(self, self.menu_inicio),
                "lado": 0.29
            },
            {
                "texto": "CONFIRMAR",
                "archivo": "boton_confirmar.png", 
                "accion": lambda: controladores.mostrar_menu_nombre_usuario(self, True),
                "lado": 0.72
            }
        ]
 
        for datos in datos_botones:
            # 2. Crear el botón base
            ancho_base = constantes.ELEMENTO_MEDIANO_ANCHO
            alto_base = constantes.ELEMENTO_MEDIANO_ALTO
            x_relativa = (constantes.ANCHO_MENU_CNT_J - ancho_base) * datos["lado"] 
            
            boton = menu_cantidad.crear_elemento(
                x=x_relativa,
                y=y_base,
                funcion=True,
                ancho=ancho_base,
                alto=alto_base,
                texto=datos["texto"],
                accion=datos["accion"],
                tp_color="s",
                tp_borde="n"
            )
 
            # 3. Cargar y aplicar la imagen
            try:
                ruta_img = importar_desde_carpeta(
                    nombre_archivo=f"Imagenes/botones/{datos['archivo']}",
                    nombre_carpeta="assets"
                )
                img = pygame.image.load(ruta_img).convert_alpha()
 
                # Escala proporcional basada en altura fija
                ancho_orig, alto_orig = img.get_size()
                factor_escala = ALTO_FIJO_BOTONES / alto_orig
                nuevo_ancho = int(ancho_orig * factor_escala)
                nuevo_alto = ALTO_FIJO_BOTONES
 
                img = pygame.transform.smoothscale(img, (nuevo_ancho, nuevo_alto))
 
                # Coordenadas absolutas para el área de clic
                x_absoluto = menu_cantidad.x + x_relativa
                y_absoluto = menu_cantidad.y + y_base
 
                # Ajustar el rect del botón (centrando el ancho si es necesario)
                boton.rect = pygame.Rect(
                    int(x_absoluto - (nuevo_ancho - ancho_base) // 2),
                    int(y_absoluto),
                    nuevo_ancho,
                    nuevo_alto
                )
 
                # Asignar la imagen al botón
                boton.superficie_texto = img
                boton.rect_texto = img.get_rect(center=boton.rect.center)
 
                # Limpiar el diseño genérico
                boton.color_actual = boton.color = boton.color_hover = boton.color_clicado = None
                boton.grosor_borde = 0
                boton.color_borde = None
                boton.color_borde_actual = None
 
            except Exception as e:
                print(f"Error cargando imagen para {datos['texto']}: {e}")