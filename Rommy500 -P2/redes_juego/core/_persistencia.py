"""Módulo interno para persistencia de datos (guardar/cargar ID y nombre)"""

class PersistenciaMixin:
    """Mixin con métodos para guardar y cargar datos localmente"""
    
    def guardar_id_local(self):
        """Guarda el ID del jugador en un archivo local"""
        if self.id_jugador is not None:
            try:
                with open("id_jugador.txt", "w") as f:
                    f.write(str(self.id_jugador))
            except Exception as e:
                print(f"Error guardando el ID local: {e}")
    
    def cargar_id_local(self):
        """Carga el ID del jugador desde un archivo local"""
        try:
            with open("id_jugador.txt", "r") as f:
                self.id_jugador = int(f.read().strip())
                print(f"ID de jugador cargado localmente: {self.id_jugador}")
                return self.id_jugador
        except Exception:
            return None
    
    def guardar_nombre_local(self, nombre):
        """Guarda el nombre del jugador en un archivo local"""
        try:
            with open("nombre_jugador.txt", "w", encoding="utf-8") as f:
                f.write(nombre)
        except Exception as e:
            print(f"Error al guardar el nombre local: {e}")

    def cargar_nombre_local(self):
        """Carga el nombre del jugador desde un archivo local"""
        try:
            with open("nombre_jugador.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            return None

