import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class GameManager:
    """Controla la partida: turnos, puntajes, y responde a desconexiones."""
    
    def __init__(self, networkManager):
        """
        network_manager: referencia al NetworkManager (para broadcast y obtener jugadores)
        """
        self.nm = networkManager
        self.players_order: List[int] = []     # IDs en orden de turno
        self.current_turn_index: int = 0
        self.game_active: bool = False
        self.scores: Dict[int, int] = {}       # player_id -> puntaje

    def start_game(self, player_ids: List[int]):
        """Inicia la partida con la lista de IDs de jugadores."""
        self.players_order = player_ids.copy()
        self.current_turn_index = 0
        self.game_active = True
        self.scores = {pid: 0 for pid in player_ids}
        logger.info(f"Partida iniciada con jugadores: {player_ids}")
        self._broadcast_game_state()

    def on_player_disconnect(self, player_id: int):
        """LLAMADO DESDE EL SERVIDOR cuando un cliente se va."""
        if not self.game_active:
            return
        if player_id not in self.players_order:
            return

        # 1. Eliminar jugador de la partida
        self.players_order.remove(player_id)
        if player_id in self.scores:
            del self.scores[player_id]

        # 2. Si quedan menos de 2 jugadores, terminar la partida
        if len(self.players_order) < 2:
            self.end_game("Juego terminado: muy pocos jugadores")
            return

        # 3. Ajustar el turno actual
        if self.current_turn_index >= len(self.players_order):
            self.current_turn_index = 0

        # falta mejorar para que el turno siga siendo el mismo en la reconxion de un jugador
        if self.players_order:
            self.current_turn_index = 0
            current_id = self.players_order[0]
            self._broadcast({"type": "TURN_CHANGE", "player_id": current_id})
        
        self._broadcast_game_state()
        logger.info(f"Jugador {player_id} desconectado. Quedan {len(self.players_order)} jugadores.")

    def next_turn(self):
        """Cambia al siguiente jugador en el orden (llamado desde la lógica del juego)."""
        if not self.game_active or len(self.players_order) == 0:
            return
        self.current_turn_index = (self.current_turn_index + 1) % len(self.players_order)
        current_id = self.players_order[self.current_turn_index]
        self._broadcast({"type": "TURN_CHANGE", "player_id": current_id})
        logger.debug(f"Nuevo turno: jugador {current_id}")

    def end_game(self, reason: str):
        """Finaliza la partida y notifica a todos."""
        self.game_active = False
        self._broadcast({"type": "GAME_OVER", "reason": reason})
        logger.info(f"Partida terminada: {reason}")

    def _broadcast(self, message: dict):
        """Envía un mensaje a todos los clientes usando el NetworkManager."""
        if self.nm:
            self.nm.broadcast_message(message)

    def _broadcast_game_state(self):
        """Envía el estado completo del juego (turno, puntajes, orden)."""
        state_info = {
            "type": "GAME_STATE",
            "players_order": self.players_order,
            "current_turn": self.players_order[self.current_turn_index] if self.players_order else None,
            "scores": self.scores,
            "game_active": self.game_active
        }
        self._broadcast(state_info)