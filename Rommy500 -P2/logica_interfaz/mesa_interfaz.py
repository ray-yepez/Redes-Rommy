import pygame
from recursos_graficos import constantes
from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta

# ===== IMPORTACIONES =====
# Importaciones de clases de interfaz
Mazo = importar_desde_carpeta(
    nombre_archivo="mazo_interfaz.py",
    nombre_clase="Mazo_interfaz",
    nombre_carpeta="logica_interfaz"
)
Jugador = importar_desde_carpeta(
    nombre_archivo="jugador_interfaz.py",
    nombre_clase="Jugador_interfaz",
    nombre_carpeta="logica_interfaz"
)
Carta = importar_desde_carpeta(
    nombre_archivo="cartas_interfaz.py",
    nombre_clase="Cartas_interfaz",
    nombre_carpeta="logica_interfaz"
)
BotonLogoMenu = importar_desde_carpeta("elementos_de_interfaz_de_usuario.py","BotonLogoMenu","recursos_graficos")

# Importar recursos graficos
Menu = importar_desde_carpeta("menu.py","Menu","recursos_graficos")
Boton = importar_desde_carpeta("elementos_de_interfaz_de_usuario.py","Boton","recursos_graficos")
CartelAlerta = importar_desde_carpeta("elementos_de_interfaz_de_usuario.py","CartelAlerta","recursos_graficos")

# ===== IMPORTACIONES DE MIXINS =====
from logica_interfaz.core.layout.posicionamiento import PosicionamientoMixin
from logica_interfaz.core.configuracion.utilidades import UtilidadesMixin
from logica_interfaz.core.datos.carga_datos import CargaDatosMixin
from logica_interfaz.core.datos.carga_visuales import CargaVisualesMixin
from logica_interfaz.core.logica_juego.turnos import TurnosMixin
from logica_interfaz.core.controles_ui.botones import BotonesMixin
from logica_interfaz.core.renderizado.mostrar import MostrarMixin
from logica_interfaz.core.configuracion.creacion import CreacionMesaMixin
from logica_interfaz.core.renderizado.actualizacion import ActualizacionMixin
from logica_interfaz.core.logica_juego.procesamiento import ProcesamientoMixin
from logica_interfaz.core.logica_juego.mano import ManoMixin
from logica_interfaz.core.red.acciones_red import AccionesRedMixin
from logica_interfaz.core.logica_juego.puntos import PuntosMixin
from logica_interfaz.core.controles_ui.menu_opciones import MenuOpcionesMixin
from logica_interfaz.core.controles_ui.alertas import AlertasMixin
from logica_interfaz.core.logica_juego.rondas import RondasMixin
from logica_interfaz.core.ui.menu_adaptado import Menu_adaptado


class Mesa_interfaz(
    PosicionamientoMixin,
    UtilidadesMixin,
    CargaDatosMixin,
    CargaVisualesMixin,
    TurnosMixin,
    BotonesMixin,
    MostrarMixin,
    CreacionMesaMixin,
    ActualizacionMixin,
    ProcesamientoMixin,
    ManoMixin,
    AccionesRedMixin,
    PuntosMixin,
    MenuOpcionesMixin,
    AlertasMixin,
    RondasMixin
):
    _cartas_imagenes = None  # cache estático
    
    def __init__(self, un_juego):
        # Inicialización de datos del juego interfaz-redes
        self.elementos_mesa = {
            "id_jugador": None,
            "jugador_mano": None,
            "cantidad_cartas_mazo": 0,
            "cantidad_cartas_quema": 0,
            "dato_carta_quema":None,
            "dato_carta_descarte": None,
            "datos_mano_jugador": [],
            "cantidad_manos_jugadores": [],
            "datos_lista_jugadores": [],
            "turno_robar": False,
            "jugada":[],
            "jugadas_jugadores":[],
            "nro_jugada":1,
        }
        
        # Objetos del juego
        self.carta_descarte = None
        self.lista_jugadores_objetos = []
        self._jugadores_dict = None  # Cache para búsqueda optimizada de jugadores
        self.mano = []
        self.mazo_quema = None
        self.carta_quema = None
        self.un_juego = un_juego
        self.instacia_conexion = None
        self.mesa = None
        self.jugadores = []
        self.jugadas_jugadores = {}
        self.jugada = []
        self.trio = []
        self.seguidilla = []

        # Estados del juego
        self.tu_turno = False
        self.turno_robar = False

        # Contador de puntos
        self.puntos_acumulados = 0
        self.puntos_ronda_actual = 0 

        self.menu_opciones = None
        self.menu_puntuacion = None
        self.menus_activos = []  # Lista para menus activos de la mesa
        self.boton_menu_opciones = None
        
        # Elementos de interfaz
        self.botones_accion = {}
        self.accion_seleccionada = None
        
        # Referencia de elementos surface mesa-ventana
        self.referencia_elementos = {
                    "elementos_mis_cartas":[],
                    "elemento_carta_descarte":None,
                    "elemento_mazo_quema":None,
                    "elemento_jugadores":[],
                    "reversos_por_jugador":[],
                    "contadores_mano_por_jugador":[],
                    "jugadas_por_jugador":[],
                    "elementos_jugadas_jugadores":[],
                    "elementos_mi_jugada":[],
                    "elemento_mazo":None,
                    "elemento_carta_quema":None,
                    "indicador_turno":None,
                    "contador_puntos":None
        }
        
        # Configuración de posiciones
        self._inicializar_configuracion_posiciones()

    # ===== INICIALIZACIÓN Y CONFIGURACIÓN =====
    def _inicializar_configuracion_posiciones(self):
        """Configura las posiciones y permutaciones para los jugadores"""
        self.posiciones_por_cantidad = {
            "pocos_jugadores": [
                ("abajo", 0.5), ("derecha", 0.6), ("arriba", 0.5), ("izquierda", 0.6)
            ],
            "muchos_jugadores": [
                ("abajo", 0.5),      # 0: abajo-enmedio
                ("abajo", 0.25),     # 1: abajo-izquierda
                ("abajo", 0.85),     # 2: abajo-derecha
                ("derecha", 0.9),    # 3: derecha-abajo
                ("derecha", 0.4),    # 4: derecha-enmedio
                ("arriba", 0.65),    # 5: arriba-derecha
                ("arriba", 0.5),     # 6: arriba-enmedio
                ("arriba", 0.25),    # 7: arriba-izquierda
                ("izquierda", 0.4),  # 8: izquierda-enmedio
                ("izquierda", 0.9)   # 9: izquierda-abajo
            ]
        }

        self.permutaciones_por_jugador = {
            2: {1: [0, 2], 2: [2, 0]},
            3: {1: [0, 1, 2], 2: [3, 0, 1], 3: [2, 3, 0]},
            4: {1: [0, 1, 2, 3], 2: [3, 0, 1, 2], 3: [2, 3, 0, 1], 4: [1, 2, 3, 0]},
            5: {
                1: [0, 4, 5, 7, 8],
                2: [8, 0, 3, 4, 6],
                3: [6, 8, 1, 2, 4],
                4: [6, 8, 1, 2, 4],
                5: [4, 6, 8, 9, 0]
            }
        }
