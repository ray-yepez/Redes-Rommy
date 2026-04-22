"""Módulo interno para sistema de rondas"""


class RondasMixin:
    """Mixin con métodos para sistema de rondas"""
    
    def manejar_ronda(self, mesa, ronda):
        """Maneja la ronda actual y actualiza la interfaz de usuario para mostrar la ronda actual."""
        self.actualizar_ronda(mesa, ronda) 

    def actualizar_ronda(self, mesa, ronda):
        """Actualiza la interfaz de usuario para mostrar la ronda actual."""
        #alerta de ronda finalizada
        self.alerta_ronda(mesa, ronda)

        #actualizar ronda actual
        self.ronda_actual = ronda
    

    def alerta_ronda(self, mesa, ronda):
        # Primero limpiar cualquier alerta previa
        self.limpiar_alertas(mesa)
        
        # Crear nueva alerta con temporización de 3 segundos
        if ronda == 1:
            mensaje = f"La primera Ronda es una seguidilla y un trio"
        elif ronda == 2:
            mensaje = f"La segunda Ronda son dos seguidillas"
        elif ronda == 3:
            mensaje = f"La tercera Ronda son tres trios"
        elif ronda == 4:
            mensaje = f"La cuarta Ronda son una seguidilla y dos trio"
        self.crear_cartel_alerta(mesa, mensaje, ancho=800, mostrar_boton_cerrar=False, duracion_ms=3000).mostrar()

