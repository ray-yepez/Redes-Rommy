"""Módulo interno para métodos auxiliares de posicionamiento"""

from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta
from recursos_graficos import constantes

Mazo = importar_desde_carpeta(
    nombre_archivo="mazo_interfaz.py",
    nombre_clase="Mazo_interfaz",
    nombre_carpeta="logica_interfaz"
)


class PosicionamientoMixin:
    """Mixin con métodos auxiliares de posicionamiento"""
    
    def _calcular_posicion_mazo(self):
        """Calcula la posición relativa del mazo en la mesa (método auxiliar reutilizable)"""
        # Crear mazo temporal para obtener dimensiones
        mazo_temp = Mazo(0, 0, 0, 0.05, None, self.un_juego)
        ancho_mazo = mazo_temp.elemento_mazo.ancho
        alto_mazo = mazo_temp.elemento_mazo.alto
        # Calcular posición CENTRADA restando ancho/alto
        x_relativo = (constantes.ANCHO_MENU_MESA * 0.40) - ancho_mazo
        y_relativo = (constantes.ALTO_MENU_MESA * 0.55) - alto_mazo
        return x_relativo, y_relativo, ancho_mazo, alto_mazo
    
    def determinar_alineacion_jugador(self, direccion, ancho_jugador, alto_jugador, alineacion):
        """Determina la posición y orientación de un jugador"""
        if direccion == "abajo":
            x, y = self.alinear_abajo(ancho_jugador, alto_jugador, alineacion)
            fila_cartas = "horizontal"
        elif direccion == "arriba":
            x, y = self.alinear_arriba(ancho_jugador, alto_jugador, alineacion)
            fila_cartas = "horizontal"
        elif direccion == "izquierda":
            x, y = self.alinear_izquierda(ancho_jugador, alto_jugador, alineacion)
            fila_cartas = "vertical"
        elif direccion == "derecha":
            x, y = self.alinear_derecha(ancho_jugador, alto_jugador, alineacion)
            fila_cartas = "vertical"
        return x, y, fila_cartas

    def determinar_ubicacion_mano(self, jugador, dx, dy):
        """Determina la posición inicial de la mano de un jugador"""
        if jugador.fila_cartas == "horizontal":
            if jugador.direccion == "abajo":
                x, y = jugador.x - (jugador.ancho/2), jugador.y + (jugador.alto + 10)
            elif jugador.direccion == "arriba":
                x, y = jugador.x + (jugador.ancho - 50), jugador.y - (jugador.alto + 75)
                dx = -jugador.offset_cartas
        elif jugador.fila_cartas == "vertical":
            if jugador.direccion == "derecha":
                x, y = jugador.x + (jugador.ancho - 50), jugador.y - (jugador.alto + 25)
                dy = -jugador.offset_cartas
            elif jugador.direccion == "izquierda":
                x, y = jugador.x - (jugador.ancho - 150), jugador.y - (jugador.alto + 205)
        return x, y, dx, dy

    def determinar_ubicacion_jugada(self,jugador,dx,dy):
        """Determina la ubicación de las jugadas de un jugador"""
        if jugador.fila_cartas == "horizontal":
            if jugador.direccion == "abajo":
                x, y = jugador.x - (jugador.ancho/2), jugador.y + (jugador.alto + 10)
                y = y-200
            elif jugador.direccion == "arriba":
                x, y = jugador.x + (jugador.ancho - 50), jugador.y - (jugador.alto + 75)
                y = y+180
                dx = -jugador.offset_cartas
        elif jugador.fila_cartas == "vertical":
            if jugador.direccion == "derecha":
                x, y = jugador.x + (jugador.ancho - 50), jugador.y - (jugador.alto + 25)
                x = x-100
                dy = -jugador.offset_cartas
            elif jugador.direccion == "izquierda":
                x, y = jugador.x - (jugador.ancho - 150), jugador.y - (jugador.alto + 205)
                x = x+100
        return x, y, dx, dy

    def alinear_abajo(self, ancho, alto, alineacion_x):
        """Alinea un elemento en la parte inferior de la mesa"""
        x = (constantes.ANCHO_MENU_MESA_ESPERA - ancho) * alineacion_x
        y = (constantes.ALTO_MENU_MESA_ESPERA - alto) * 0.87
        return (x, y)

    def alinear_arriba(self, ancho, alto, alineacion_x):
        """Alinea un elemento en la parte superior de la mesa"""
        x = (constantes.ANCHO_MENU_MESA_ESPERA - ancho) * alineacion_x
        y = (constantes.ALTO_MENU_MESA_ESPERA - alto) * 0.13
        return (x, y)

    def alinear_izquierda(self, ancho, alto, alineacion_y):
        """Alinea un elemento en el lado izquierdo de la mesa"""
        x = (constantes.ANCHO_MENU_MESA_ESPERA - ancho) * 0.02
        y = (constantes.ALTO_MENU_MESA_ESPERA - alto) * alineacion_y
        return (x, y)

    def alinear_derecha(self, ancho, alto, alineacion_y):
        """Alinea un elemento en el lado derecho de la mesa"""
        x = (constantes.ANCHO_MENU_MESA_ESPERA - ancho)
        y = (constantes.ALTO_MENU_MESA_ESPERA - alto) * alineacion_y
        return (x, y)

    def calcular_desplazamiento_mano(self, jugador):
        """Calcula dx, dy basado en la orientación del jugador"""
        if jugador.fila_cartas == "horizontal":
            return (jugador.offset_cartas, 0)
        else:
            return (0, jugador.offset_cartas)
    def determinar_ubicacion_contador_de_cartas(self,jugador):
        if jugador.fila_cartas == "horizontal":
            if jugador.direccion == "abajo":
                x, y = jugador.x - (jugador.ancho/2), jugador.y + (jugador.alto + 10)
            elif jugador.direccion == "arriba":
                x, y = jugador.x + (jugador.ancho - 50), jugador.y - (jugador.alto - 60)
        elif jugador.fila_cartas == "vertical":
            if jugador.direccion == "derecha":
                x, y = jugador.x + (jugador.ancho - 50), jugador.y - (jugador.alto -62)
            elif jugador.direccion == "izquierda":
                x, y = jugador.x + (jugador.ancho - 50), jugador.y - (jugador.alto - 62)
        return x, y

