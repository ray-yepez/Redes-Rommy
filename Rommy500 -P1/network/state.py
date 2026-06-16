import threading
from queue import Queue
from typing import Dict, List, Any
import logging
from .types import ConnectedPlayer

logger = logging.getLogger(__name__)

class NetworkState:
    """Contenedor thread-safe para el estado de conexión y juego."""
    
    def __init__(self):
        # Locks para sincronización
        self._lock_players = threading.Lock()
        self._lock_game = threading.Lock()
        self._lock_messages = threading.Lock()
        
        # Colas thread-safe (reemplazan a las listas tradicionales para prevenir colisiones)
        self.incoming_messages = Queue()  # Mensajes entrantes que procesará el cliente
        self.moves_game = Queue()         # Jugadas del cliente
        self.moves_gameServer = Queue()   # Jugadas procesadas en el Host
        
        # Diccionarios de estado de juego protegidos por Lock
        self.game_state = {}              # Estado general de las cartas y el juego
        self.msgStartGame = {}            # Mensaje y estado inicial de partida
        self.messagesServer = []          # Historial de mensajes (si se requiere)
        
        # Configuración y estado de la conexión en curso
        self.is_connected = False
        self.running = False
        self.running_broadcast = False
        self.is_host = False
        self.game_started = False
        self.host_disconnected = False
        # --- NUEVO: Estado de notificaciones de chat ---
        self.has_unread_chat = False
        
        # Datos del cliente / servidor local
        self.player_id = None
        self.player_name = None
        self.playerName = None  # Alias usado en algunas partes del Server/Host
        self.host = None
        self.port = None
        self.gameName = None
        self.password = None
        self.max_players = None
        
        # Socket principal y referencias
        self.player = None  # Socket del lado cliente para conexión al Host
        self.server_info_to_reconnect = None
        self.receivedData = None
        
        # Mensajes temporales para la UI (avisos de conexión/desconexión)
        self.mensaje = "" #LOS ATRIBUTOS DEL MENSAJE SE INICIALIZAN AQUÍ PARA QUE LUEGO EL MÁNAGER LOS HEREDE
        self.tiempoDelMensaje = 0
        
        # Estado de jugadores en partida
        self.connected_players: List[ConnectedPlayer] = []
        self.last_activity = {}  # {player_id: timestamp_float}
        
        self.current_player_count = None
        
        logger.info("NetworkState inicializado de forma segura.")
    
    def add_incoming_message(self, msg_type: str, data: dict = None):
        """Agrega mensaje entrante a la cola (thread-safe)."""
        # ui2.py espera tuplas (msg_type, data_dict)
        self.incoming_messages.put((msg_type, data or {}))
    
    def get_incoming_messages(self) -> List[dict]:
        """Extrae de golpe todos los mensajes pendientes de la cola."""
        msgs = []
        while not self.incoming_messages.empty():
            try:
                msgs.append(self.incoming_messages.get_nowait())
            except:
                break
        return msgs
    
    def add_move(self, move: dict, server=False):
        """Agrega una jugada a la cola correspondiente."""
        queue = self.moves_gameServer if server else self.moves_game
        queue.put(move)
    
    def get_moves(self, server=False) -> List[dict]:
        """Extrae todas las jugadas pendientes de la cola solicitada."""
        queue = self.moves_gameServer if server else self.moves_game
        moves = []
        while not queue.empty():
            try:
                moves.append(queue.get_nowait())
            except:
                break
        return moves
    
    def update_game_state(self, state_dict: dict):
        """Actualiza el diccionario de estado del juego bajo un Lock sincronizado."""
        with self._lock_game:
            self.game_state.update(state_dict)
            logger.debug(f"Game state actualizado con las claves: {list(state_dict.keys())}")
    
    def get_game_state(self) -> dict:
        """Lee el estado del juego actual y lo vacía para que no se lea dos veces."""
        with self._lock_game:
            state = self.game_state.copy()
            self.game_state.clear()
            return state
    
    def add_connected_player(self, player: ConnectedPlayer):
        """Registra un nuevo jugador a la lista del servidor."""
        with self._lock_players:
            self.connected_players.append(player)
            logger.info(f"Jugador agregado a la partida: {player.name} (ID: {player.player_id})")
    
    def remove_connected_player(self, player_id: int):
        """Elimina a un jugador por su ID (ej: cuando se desconecta)."""
        with self._lock_players:
            self.connected_players = [p for p in self.connected_players if p.player_id != player_id]
            logger.info(f"Jugador removido de la partida (ID: {player_id})")
    
    def get_connected_players(self) -> List[ConnectedPlayer]:
        """Obtiene una copia segura de la lista de jugadores conectados."""
        with self._lock_players:
            return self.connected_players.copy()
    
    def update_last_activity(self, player_id: int, timestamp: float):
        """Registra el último milisegundo en que un jugador respondió un ping."""
        with self._lock_players:
            self.last_activity[player_id] = timestamp
