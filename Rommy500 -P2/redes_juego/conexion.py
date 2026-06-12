import socket
import threading
import json
import time
import pygame
import copy
from random import choice
from redes_juego import archivo_de_importaciones

# Importar mixins modulares
from redes_juego.core._persistencia import PersistenciaMixin
from redes_juego.core._mensajeria import MensajeriaMixin
from redes_juego.core._validadores import ValidadoresMixin
from redes_juego.core._servidor import ServidorMixin
from redes_juego.core._cliente import ClienteMixin
from redes_juego.core._logica_partida import LogicaPartidaMixin
from redes_juego.core._procesador_mensajes import ProcesadorMensajesMixin

importar_desde_carpeta = archivo_de_importaciones.importar_desde_carpeta
constantes = importar_desde_carpeta(
    nombre_archivo="constantes.py",
    nombre_carpeta="recursos_graficos",
)

mesa = importar_desde_carpeta(
    nombre_archivo="mesa.py",
    nombre_carpeta="logica_juego",
)

mesa_interfaz = importar_desde_carpeta(
    nombre_archivo="mesa_interfaz.py",
    nombre_carpeta="logica_interfaz",
)
mazo_logica = importar_desde_carpeta(
    nombre_archivo="mazo.py",
    nombre_clase="Mazo",
    nombre_carpeta="logica_juego",
)

#Importaciones de clases de interfaz
Mazo_interfaz = importar_desde_carpeta(
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

class conexion_Rummy(
    PersistenciaMixin,
    MensajeriaMixin,
    ValidadoresMixin,
    ServidorMixin,
    ClienteMixin,
    LogicaPartidaMixin,
    ProcesadorMensajesMixin
):
    def __init__(self,max_jugadores=7):
        self.puerto = 5555
        self.ejecutandose = False
        self.candado = threading.RLock()
        self.un_juego = None
        # Host
        self.max_jugadores = max_jugadores
        self.socket_servidor = None
        self.clientes = []
        self.cola_mensajes = []
        self.estado_juego = None
        self.nombre_partida = None
        self.id_jugador_enviador = None  # Atributo para el ID del jugador que envía mensajes
        self.buscador = True
        # Cliente
        self.socket_cliente = None
        self.conectado = False
        self.id_jugador = None
        self.hilo_recepcion = None
        self.conexiones_disponibles = []
        self.jugadores_desconectados = {}  # Nuevo: almacena datos de jugadores desconectados

        # eventos 
        self.eventos_conexion = []

        # Partida
        self.lista_jugadores_objetos = []
        self.lista_jugadores_objetos_reordenados = []
        self.descarte = []
        self.ultimo_descarte = []
        self.quema = []
        self.cartas_mesa = []
        self.jugadores_primera_jugada = []
        self.mesa_juego = None
        self.jugadas_por_jugador = {}
        self.mazo = None
        self.jugador_compra = None
        self.contador_turno_compra = 0
        self.jugador_que_descarto = None  # Guarda el ID del jugador que descartó la carta actual
        self.trio = {}
        self.seguidilla = {}
        self.ultima_jugada = []
        self.seleccionando = False
        self.cancelar = False
        self.informacion_extender = None  # Variable para almacenar información de extensión
        #Partida Server
        self.manos = {} #Este atributo solo se va a usar en el servidor
        self.estado_partida = False #Indica si la partida ha comenzado o noa
        self.aceptar_conexiones_estado = False #Indica si se esta aceptando conexiones o no
        self.anunciar_servidor_estado = False #Indica si se esta anunciando el servidor o no
        self.ronda = 1 #Indica la ronda actual de la partida

