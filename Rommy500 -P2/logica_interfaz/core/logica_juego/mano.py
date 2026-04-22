"""Módulo interno para comportamiento de mano del jugador local"""


class ManoMixin:
    """Mixin con métodos para comportamiento de mano del jugador local"""

    def modificar_comportamiento_mi_mano(self):
        mi_mano = self.referencia_elementos["elementos_mis_cartas"]
        prioridad = 1
        for carta in mi_mano:
            carta.seleccion_multiple = True
            carta.deseleccionar()
            carta.prioridad = prioridad
            prioridad += 1
        self.referencia_elementos["elementos_mis_cartas"] = mi_mano
    
    def restaurar_comportamiento_mi_mano(self):
        mi_mano = self.referencia_elementos["elementos_mis_cartas"]
        for carta in mi_mano:
            carta.seleccion_multiple = False
            carta.deseleccionar()
            carta.deshabilitado = False
        self.referencia_elementos["elementos_mis_cartas"] = mi_mano

