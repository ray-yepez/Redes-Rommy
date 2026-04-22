"""Módulo interno para Menu_adaptado"""

import pygame
from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta
from recursos_graficos import constantes

Menu = importar_desde_carpeta("menu.py","Menu","recursos_graficos")


class Menu_adaptado(Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def dibujar_fondo(self):
        """Dibuja un rectángulo de fondo más grande que el menú, sin borde, y luego el menú centrado."""
        rect_fondo = pygame.Rect(
            0, 0, constantes.ANCHO_VENTANA, constantes.ALTO_VENTANA
        )
        pygame.draw.rect(self.pantalla, self.borde_color, rect_fondo, border_radius=0)
        pygame.draw.rect(self.pantalla, self.fondo_color, self.menu, border_radius=self.redondeo)

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

