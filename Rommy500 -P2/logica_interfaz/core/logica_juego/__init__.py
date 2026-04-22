"""Módulo de lógica del juego"""

from logica_interfaz.core.logica_juego.turnos import TurnosMixin
from logica_interfaz.core.logica_juego.procesamiento import ProcesamientoMixin
from logica_interfaz.core.logica_juego.mano import ManoMixin
from logica_interfaz.core.logica_juego.puntos import PuntosMixin
from logica_interfaz.core.logica_juego.rondas import RondasMixin

__all__ = [
    'TurnosMixin',
    'ProcesamientoMixin',
    'ManoMixin',
    'PuntosMixin',
    'RondasMixin',
]

