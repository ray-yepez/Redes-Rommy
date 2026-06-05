"""Puente de eventos de red para desacoplar la interfaz gráfica (Pygame) de la lógica de red."""

from typing import Callable, Dict, Any

class NetworkEventBridge:
    """
    Patrón Observador para mediar entre la capa de red y la UI.
    La capa de red emite eventos aquí, y la UI registra callbacks.
    """
    
    def __init__(self):
        self._handlers: Dict[str, list[Callable]] = {}
    
    def register(self, msg_type: str, handler: Callable):
        """Registra una función callback para un tipo de evento específico."""
        self._handlers.setdefault(msg_type, []).append(handler)
    
    def emit(self, msg_type: str, payload: dict):
        """Emite un evento a todos los callbacks registrados."""
        for handler in self._handlers.get(msg_type, []):
            handler(payload)

# Instancia global del puente para ser importada por UI y Red
event_bridge = NetworkEventBridge()
