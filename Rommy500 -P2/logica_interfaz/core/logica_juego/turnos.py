"""Módulo interno para gestión de turnos"""


class TurnosMixin:
    """Mixin con métodos para gestión de turnos"""
    
    def determinar_turno(self):
        if not self.elementos_mesa:
            self.tu_turno = False
            return

        id_local = self.elementos_mesa.get("id_jugador")
        jugador_mano = self.elementos_mesa.get("jugador_mano")

        if not jugador_mano:
            self.tu_turno = False
            return

        id_turno = jugador_mano[0]

        self.tu_turno = int(id_local) == int(id_turno)

        print("ID LOCAL:", id_local, "ID TURNO:", id_turno, "TU TURNO:", self.tu_turno)

    def determinar_turno_robar(self):
        """Determina si es turno de robar"""
        if self.elementos_mesa["turno_robar"] is not None:
            self.turno_robar = self.elementos_mesa["turno_robar"]

