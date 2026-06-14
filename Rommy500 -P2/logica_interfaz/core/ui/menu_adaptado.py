"""Módulo interno para Menu_adaptado"""

import pygame
from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta
from recursos_graficos import constantes

Menu = importar_desde_carpeta("menu.py","Menu","recursos_graficos")


class Menu_adaptado(Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def dibujar_fondo(self):
        # 1. Dibujar la imagen de madera primero (Capa de abajo)
        """if hasattr(self.un_juego, 'imagen_fondo_juego') and self.un_juego.imagen_fondo_juego:
            self.pantalla.blit(self.un_juego.imagen_fondo_juego, (0, 0))
        p
        # 2. SOLO dibujar el rectángulo si hay un color definido (Capa de arriba)
        # Como ahora pasamos None desde crear_mesa, este código se saltará
        # y por fin verás la imagen de fondo limpia.
        if self.fondo_color is not None:
            pygame.draw.rect(self.pantalla, self.fondo_color, self.menu, border_radius=self.redondeo) """""   
        pass
    def dibujar_botones(self):
        # separar cartas (tienen atributo 'valor' o tipo) del resto
        cartas = [b for b in self.botones if hasattr(b, "valor")]
        otros = [b for b in self.botones if not hasattr(b, "valor")]

        # dibujar primero los no-cartas
        for boton in otros:
            boton.dibujar()

        # luego las cartas ordenadas por prioridad (seguro ante None)
        for carta in sorted(cartas, key=lambda c: getattr(c, "prioridad", 0) or 0):
            carta.dibujar()

