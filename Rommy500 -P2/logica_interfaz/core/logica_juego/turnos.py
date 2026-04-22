"""Módulo interno para gestión de turnos"""


class TurnosMixin:
    """Mixin con métodos para gestión de turnos"""
    
    def determinar_turno(self):
        """Determina si es el turno del jugador local"""
        if (not hasattr(self, 'elementos_mesa') or not self.elementos_mesa or "id_jugador" not in self.elementos_mesa or "jugador_mano" not in self.elementos_mesa):
            self.tu_turno = False
            return
            
        if self.elementos_mesa["id_jugador"] == self.elementos_mesa["jugador_mano"][0]:
            self.tu_turno = True
        else:
            self.tu_turno = False

    def determinar_turno_robar(self):
        """Determina si es turno de robar"""
        if self.elementos_mesa["turno_robar"] is not None:
            self.turno_robar = self.elementos_mesa["turno_robar"]

