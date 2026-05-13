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
        """Inicia el chequeo periódico en un hilo dedicado."""
        def health_check_loop():
            while self.state.running:
                time.sleep(self.config.HEALTH_CHECK_INTERVAL)
                
                # Solo tiene sentido el chequeo si hay alguien conectado (aparte del host)
                if len(self.state.get_connected_players()) > 1:
                    logger.debug("Ejecutando ciclo de health check (PING)...")
                    self._check_players()
        
        threading.Thread(target=health_check_loop, daemon=True).start()
    
    def _check_players(self):
        """Envía un PING a todos los clientes e invalida los inactivos."""
        disconnected = []
        
        for player in self.state.get_connected_players():
            if player.is_host:
                continue  # El Host no se pinguea a sí mismo
            
            try:
                # Enviamos el latido con el tiempo exacto actual para medir latencia si es necesario
                msg = {
                    "type": MessageType.PING.value,
                    "timestamp": time.time()
                }
                
                # Envío optimista
                if not self.transport.send_atomic(player.conn, msg):
                     logger.warning(f"Fallo al enviar PING a {player.name}, asumiendo desconectado.")
                     disconnected.append(player.player_id)
                     continue
                     
                logger.debug(f"PING enviado a {player.name}")
                
                # Si el juego ya inició, NO expulsar por timeout de inactividad.
                # El jugador puede estar simplemente pensando su turno.
                if self.state.game_started:
                    continue

                # Verificar tiempo desde última respuesta (solo en lobby)
                last_activity = self.state.last_activity.get(player.player_id, 0)
                
                # Si han pasado demasiados segundos sin saber de él
                if time.time() - last_activity > (self.config.HEALTH_CHECK_INTERVAL + self.config.PING_TIMEOUT):
                    logger.warning(f"Jugador {player.name} excedió el timeout de inactividad.")
                    disconnected.append(player.player_id)
            
            except Exception as e:
                logger.error(f"Error procesando health check para {player.name}: {e}")
                
