"""Módulo interno para creación y manejo de la mesa"""

from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta
from recursos_graficos import constantes
from logica_interfaz.core.ui.menu_adaptado import Menu_adaptado


class CreacionMesaMixin:
    """Mixin con métodos para creación y manejo de la mesa"""
    
    def crear_mesa(self):
        """Crea y configura la mesa de juego"""
        x_menu, y_menu = self.un_juego.centrar(constantes.ANCHO_MENU_MESA, constantes.ALTO_MENU_MESA)
        mesa = Menu_adaptado(
            self.un_juego,
            constantes.ANCHO_MENU_MESA,
            constantes.ALTO_MENU_MESA,
            x_menu,
            y_menu,
            constantes.ELEMENTO_FONDO_TERCIARIO,
            constantes.ELEMENTO_BORDE_TERCIARIO,
            constantes.BORDE_PRONUNCIADO,
            constantes.REDONDEO_NORMAL
        )
        self.mesa = mesa
        self.manejar_partida(mesa)
        return mesa

    def manejar_partida(self, mesa):
        """Configura todos los elementos de la partida"""
        self.preparar_datos_objetos()
        self.mostrar_jugador(mesa)
        self.cargar_elemento_mi_mano()
        self.cargar_elemento_carta_descarte()
        self.mostrar_manos(mesa)
        
        # Calcular posición del mazo usando método auxiliar
        x_relativo, y_relativo, _, _ = self._calcular_posicion_mazo()
        scala = constantes.ESCALA_CARTAS
        accion = lambda: print(f'las cantidad de cartas en el mazo son: {self.elementos_mesa["cantidad_cartas_mazo"]}')
        self.mostrar_mazo(mesa, x_relativo, y_relativo, scala, accion)
        self.mostrar_carta_descarte(mesa, x_relativo + 180, y_relativo, scala)
        self.mostrar_mazo_quema(mesa, x_relativo + 310, y_relativo, scala, accion)

        self.crear_contador_puntos(mesa)
        
        self.crear_indicador_turno(mesa)
        self.cargar_elemento_botones(mesa)

    def reiniciar_visual_mesa(self, mesa):
        """Limpia completamente los elementos visuales de la mesa para iniciar una nueva ronda.

        No modifica puntuaciones acumuladas. Reinicia listas visuales y datos temporales
        para que la siguiente llamada a `manejar_partida` construya desde cero.
        """
        try:
            print("DEBUG: Reiniciando visual de la mesa (limpieza completa)")

            # Limpiar superficies e imágenes agregadas
            if hasattr(mesa, 'imagenes'):
                mesa.imagenes.clear()

            # Limpiar botones (botones interactivos y mazos)
            if hasattr(mesa, 'botones'):
                mesa.botones.clear()

            # Limpiar overlays si existen (carteles, tooltips, etc.)
            if hasattr(mesa, 'overlays'):
                mesa.overlays.clear()

            # Resetear referencias internas que apuntan a elementos visuales
            self.referencia_elementos = {
                "elementos_mis_cartas":[],
                "elemento_carta_descarte":None,
                "elemento_mazo_quema":None,
                "elemento_jugadores":[],
                "reversos_por_jugador":[],
                "jugadas_por_jugador":[],
                "elementos_jugadas_jugadores":[],
                "elementos_mi_jugada":[],
                "elemento_mazo":None,
                "elemento_carta_quema":None,
                "indicador_turno":None,
                "contador_puntos":None,
                "contadores_mano_por_jugador":[]
            }

            # Resetear objetos temporales de la partida (no tocar puntos acumulados)
            self.carta_descarte = None
            self.carta_quema = None
            self.mazo_quema = None
            self.lista_jugadores_objetos = []
            self.jugadores = []
            self.jugada = []
            self.jugadas_jugadores = {}
            self.mano = []
            self.botones_accion.clear()
            self.boton_menu_opciones = None

        except Exception as e:
            print(f"ERROR al reiniciar visual de la mesa: {e}")

