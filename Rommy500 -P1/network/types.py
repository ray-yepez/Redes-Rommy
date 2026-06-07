from dataclasses import dataclass
from typing import Optional
import socket
import time

@dataclass
class ConnectedPlayer:
    """Representa un jugador conectado al servidor."""
    conn: socket.socket
    addr: tuple  # (ip, puerto)
    name: str
    player_id: int
    is_host: bool = False
    last_activity: float = None  # timestamp
    
    def __post_init__(self):
        if self.last_activity is None:
            self.last_activity = time.time()

@dataclass
class ServerInfo:
    """Información de un servidor descubierto en el broadcast."""
    name: str
    player_name: str  # Nombre del creador
    ip: str
    port: int
    max_players: int
    current_players: int
    password: Optional[str] = None
    # (nota: password se excluye del broadcast por seguridad)

@dataclass
class NetworkMessage:
    """Mensaje de red con metadatos."""
    message_type: str
    data: dict
    sender_id: Optional[int] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
