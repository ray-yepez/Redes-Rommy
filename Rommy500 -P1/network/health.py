import threading
import time
import logging

from .transport import Transport
from .state import NetworkState
from .config import NetworkConfig
from .constants import MessageType

logger = logging.getLogger(__name__)

class HealthMonitor:
    """Sistema de monitoreo de conexión (Ping-Pong)."""
    
    def __init__(self, state: NetworkState, transport: Transport, config: NetworkConfig = None):
        self.state = state
        self.transport = transport
        self.config = config or NetworkConfig()
    
    def start_health_check(self):
        """Inicia el chequeo periódico en un hilo dedicado / proteccion contra duplicados"""
        if getattr(self.state, "monitor_activo", False):
            logger.debug("El hilo de health check ya se encuentra activo. Evitando duplicarlo.")
            return
        self.state.monitor_activo = True
        
        def health_check_loop():

            time.sleep(2)  # Esperar un poco antes de iniciar el primer chequeo

            while self.state.running:
                
                # Solo tiene sentido el chequeo si hay alguien conectado (aparte del host)
                if len(self.state.get_connected_players()) > 1:
                    logger.debug("Ejecutando ciclo de health check (PING)...")
                    
                    self.send_pings()

                time.sleep(self.config.HEALTH_CHECK_INTERVAL)

                if len(self.state.get_connected_players()) > 1:
                    self._check_players_timeout()
        
        threading.Thread(target=health_check_loop, daemon=True).start()

    def send_pings(self):
        # Enviar un ping a cada jugador conectado (aparte del host)
        current_time = time.time()
        for player in self.state.get_connected_players():
            if player.is_host:
                continue
            
            ping_msg = {
                "type": MessageType.PING.value,
                "timestamp": current_time
            }
            
            try:
                self.transport.send_atomic(player.conn, ping_msg)
                logger.debug(f"PING enviado a {player.name} (ID: {player.player_id})")
            except Exception as e:
                logger.warning(f"No se pudo enviar el PING a {player.name}: {e}")
    
    def _check_players_timeout(self):
        current_time = time.time()
        max_allowed_diff = self.config.CONNECTION_TIMEOUT
    
        for player in self.state.get_connected_players():
            if player.is_host:
                continue
                
            last_activity = self.state.last_activity.get(player.player_id, current_time)
            diff = current_time - last_activity
            
            logger.info(f"HEALTH CHECK -> Jugador: {player.name} (ID: {player.player_id}), Diff: {diff:.2f}s")
            
            if diff > max_allowed_diff:
                logger.warning(f"Jugador {player.player_id} ({player.name}) excedió el timeout de inactividad. Diff: {diff:.2f}s")

                try:
                    player.conn.close()
                    logger.info(f"Conexión cerrada para {player.name} (ID: {player.player_id}) debido a timeout.")
                except Exception as e:
                    logger.error(f"Error al cerrar la conexión para {player.name} (ID: {player.player_id}): {e}")
                
                self.state.remove_connected_player(player.player_id)
                logger.info(f"Jugador {player.name} (ID: {player.player_id}) removido de la lista de conectados por timeout.")