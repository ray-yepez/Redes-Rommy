"""Módulo interno para sistema de alertas"""

from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta
from recursos_graficos import constantes

CartelAlerta = importar_desde_carpeta("elementos_de_interfaz_de_usuario.py","CartelAlerta","recursos_graficos")


class AlertasMixin:
    """Mixin con métodos para sistema de alertas"""
    def alerta_no_puede_descartar_joker(self, mesa):
        """Muestra alerta cuando un jugador intenta descartar un Joker"""
        # Primero limpiar cualquier alerta previa
        self.limpiar_alertas(mesa)
        
        # Crear nueva alerta
        mensaje = "No puedes descartar un Joker"
        self.crear_cartel_alerta(mesa, mensaje,ancho=800,mostrar_boton_cerrar=False,duracion_ms=2000).mostrar()
    def alerta_error_descartar(self, mesa):
        """Muestra alerta cuando un jugador intenta descartar una carta inválida"""
        # Primero limpiar cualquier alerta previa
        self.limpiar_alertas(mesa)
        
        # Crear nueva alerta
        mensaje = "Debes seleccionar una carta para descartar"
        self.crear_cartel_alerta(mesa, mensaje,ancho=800).mostrar()
    def alerta_carta_descartar_invalida(self, mesa):
        """Muestra alerta cuando un jugador intenta descartar una carta inválida"""
        # Primero limpiar cualquier alerta previa
        self.limpiar_alertas(mesa)
        
        # Crear nueva alerta
        mensaje = "No puedes descartar esa carta"
        self.crear_cartel_alerta(mesa, mensaje,ancho=800,mostrar_boton_cerrar=False,duracion_ms=2000).mostrar()
    
    def alerta_carta_tomada(self,mesa):
        """Muestra alerta cuando un jugador toma carta del descarte"""
        # Primero limpiar cualquier alerta previa
        self.limpiar_alertas(mesa)
        
        # Crear nueva alerta
        mensaje = "No puedes descartar la carta que acabas de tomar"
        self.crear_cartel_alerta(mesa, mensaje,ancho=800,mostrar_boton_cerrar=False,duracion_ms=2000).mostrar()
    
    def alerta_trio_invalido(self, mesa):
        """Muestra alerta para selección de trío inválido"""
        # Primero limpiar cualquier alerta previa
        self.limpiar_alertas(mesa)
        
        # Crear nueva alerta
        mensaje = "Seleccione un trío válido (3 cartas del mismo número)"
        self.crear_cartel_alerta(mesa, mensaje,ancho=800).mostrar()
    
    def alerta_seguidilla_invalida(self, mesa):
        # Primero limpiar cualquier alerta previa
        self.limpiar_alertas(mesa)
        
        # Crear nueva alerta
        mensaje = "Seleccione una seguidilla valida"
        self.crear_cartel_alerta(mesa, mensaje,ancho=800).mostrar()
    
    def alerta_descarte_invalido(self, mesa):
        # Primero limpiar cualquier alerta previa
        self.limpiar_alertas(mesa)
        
        # Crear nueva alerta
        mensaje = "Seleccione una carta"
        self.crear_cartel_alerta(mesa, mensaje,ancho=800).mostrar()

    def crear_cartel_alerta(self, mesa, mensaje, x=None, y=None, ancho=500, alto=300, mostrar_boton_cerrar=True, duracion_ms=None):
        """Crea y muestra un cartel de alerta centrado"""
    
        # Si no se especifican coordenadas, centrar en la pantalla
        if x is None or y is None:
            x = (constantes.ANCHO_VENTANA - ancho) // 2
            y = (constantes.ALTO_VENTANA - alto) // 2
        
        cartel = CartelAlerta(
            pantalla=self.un_juego.pantalla,
            mensaje=mensaje,
            x=x,
            y=y,
            ancho=ancho,
            alto=alto,
            mostrar_boton_cerrar=mostrar_boton_cerrar,
            duracion_ms=duracion_ms
        )
        
        # Guardar referencia
        clave = f"alerta_{mensaje.lower().replace(' ', '_')}"
        self.botones_accion[clave] = cartel
        
        # Agregar a la mesa en la capa de overlays para que se dibuje por encima de las cartas
        try:
            if hasattr(mesa, 'overlays'):
                mesa.overlays.append(cartel)
            else:
                mesa.botones.append(cartel)
        except Exception:
            mesa.botones.append(cartel)
        
        print(f"✅ Cartel de alerta creado: {mensaje}")
        return cartel
    
    def limpiar_alertas(self, mesa):
        """Elimina todas las alertas de la mesa"""
        # Identificar y remover alertas de mesa.botones
        alertas_a_remover = []
        for boton in list(getattr(mesa, 'botones', [])):
            if isinstance(boton, CartelAlerta):
                alertas_a_remover.append(boton)
        # Revisar overlays también
        for overlay in list(getattr(mesa, 'overlays', [])):
            if isinstance(overlay, CartelAlerta):
                alertas_a_remover.append(overlay)
        
        for alerta in alertas_a_remover:
            try:
                if alerta in getattr(mesa, 'botones', []):
                    mesa.botones.remove(alerta)
            except Exception:
                pass
            try:
                if alerta in getattr(mesa, 'overlays', []):
                    mesa.overlays.remove(alerta)
            except Exception:
                pass
        
        # Limpiar del diccionario
        claves_a_eliminar = []
        for clave, elemento in self.botones_accion.items():
            if isinstance(elemento, CartelAlerta):
                claves_a_eliminar.append(clave)
        
        for clave in claves_a_eliminar:
            del self.botones_accion[clave]

    def alerta_jugador_compro_carta_del_descarte(self, mesa, jugador_compro):
        """Muestra alerta cuando un jugador compra una carta del descarte"""
        # Primero limpiar cualquier alerta previa
        self.limpiar_alertas(mesa)
        
        # Crear nueva alerta con nombre del jugador y temporización de 3 segundos
        mensaje = f"{jugador_compro} compró la carta"
        self.crear_cartel_alerta(mesa, mensaje, ancho=800, mostrar_boton_cerrar=False, duracion_ms=2000).mostrar()