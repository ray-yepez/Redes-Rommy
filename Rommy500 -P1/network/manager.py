import logging

from .transport import Transport
from .server import GameServer
from .client import GameClient
from .discovery import Discovery
from .health import HealthMonitor
from .state import NetworkState
from .config import NetworkConfig
from .constants import MessageType
from .game_manager import GameManager

logger = logging.getLogger(__name__)

class NetworkManager:
    """Fachada orquestadora de la red (interfaz pública)."""
    
    def __init__(self):
        self.config = NetworkConfig()
        self.state = NetworkState()
        self.transport = Transport(self.config)
        self._server = GameServer(self.state, self.transport, self.config)
        self.client = GameClient(self.state, self.transport, self.config)
        self.discovery = Discovery(self.state, self.config)
        self.health = HealthMonitor(self.state, self.transport, self.config)
        self.game_manager = GameManager(self)
        self._server.set_game_manager(self.game_manager)
    
    # === Métodos públicos (INTERFAZ COMPATIBLE) ===
    
    def start_server(self, nameHost, password, max_players, nameSala):
        """Inicia servidor.
        
        nameHost: nombre del jugador host (se muestra en el juego)
        nameSala: nombre de la sala/partida (se anuncia en LAN)
        """
        success = self._server.start(nameSala, nameHost, max_players, nameSala)
        if success:
            self.state.password = password
            self.state.playerName = nameHost   # Para que ui.py pueda leerlo
            self.state.running_broadcast = True
            self.discovery.start_broadcast()
            self.health.start_health_check()
        return success
    
    def connectToServer(self, server):
        """Conecta a un servidor."""
        result = self.client.connect(server)
        if result[0]:  # success
            self._current_server = server
        return result
    
    def sendData(self, data):
        """Envía datos al servidor."""
        return self.client.send(data)
    
    def discoverServers(self, timeout=5):
        """Descubre servidores en la red local asíncronamente."""
        self.discovery.discover_servers(timeout)
        return None
    
    @property
    def servers(self):
        """Lista asíncrona de servidores para compatibilidad con UI."""
        return self.discovery.discovered_servers
    
    def broadcast_message(self, message):
        """Broadcast a todos los clientes (solo HOST)."""
        if not self.state.is_host:
            logger.warning("Solo el HOST puede hacer broadcast")
            return
        
        disconnected = []
        for player in self.state.get_connected_players():
            if player.is_host:
                continue
            try:
                if not self.transport.send_atomic(player.conn, message):
                    disconnected.append(player.player_id)
            except Exception as e:
                logger.error(f"Error broadcast a {player.name}: {e}")
                disconnected.append(player.player_id)
        
        for pid in disconnected:
            self.state.remove_connected_player(pid)
    
    def stop(self):
        """Detiene servidor y cliente."""
        self.state.running = False
        self.state.running_broadcast = False
        
        # Si es host, desconectar a todos los jugadores antes de cerrar
        if self.state.is_host:
            logger.info("Host deteniendo el servidor, desconectando a todos los jugadores...")
            self._server._disconnect_all_players()
        
        # Cerrar sockets
        if self._server.server_socket:
            try:
                self._server.server_socket.close()
            except:
                pass
        
        if self.state.player:
            try:
                self.state.player.close()
            except:
                pass
        
        logger.info("NetworkManager detenido")
    
    # === Getters de estado (INTERFAZ COMPATIBLE) ===
    
    def get_incoming_messages(self):
        return self.state.get_incoming_messages()
    
    def get_game_state(self):
        return self.state.get_game_state()
    
    def get_moves_game(self):
        return self.state.get_moves()
    
    def get_moves_gameServer(self):
        return self.state.get_moves(server=True)
    
    def canStartGame(self):
        return len(self.state.get_connected_players()) >= 2
    
    def startGame(self):
        self.state.game_started = True
        player_ids = [p.player_id for p in self.state.get_connected_players()]
        self.game_manager.start_game(player_ids)
        msg = {"type": MessageType.START_GAME.value}
        self.broadcast_message(msg)
        self.state.msgStartGame.update(msg)
    
    # Propiedades para compatibilidad con llamadas viejas
    @property
    def is_host(self):
        return self.state.is_host
    
    @property
    def is_connected(self):
        return self.state.is_connected
    
    @property
    def connected_players(self):
        # Mapea ConnectedPlayer a tupla para la compatibilidad con ui.py (conn, addr, name, id)
        return [(p.conn, p.addr, p.name, p.player_id) for p in self.state.get_connected_players()]
    
    @property
    def gameName(self):
        return self.state.gameName
    
    @property
    def host(self):
        return self.state.host
    
    @property
    def port(self):
        return self.state.port
    
    @property
    def running(self):
        return self.state.running
    
    @running.setter
    def running(self, value):
        self.state.running = value

    @property
    def receive_thread_running(self):
        return self.state.running
    
    @property
    def player_id(self):
        return self.state.player_id
    
    @property
    def msgStartGame(self):
        return self.state.msgStartGame
    
    @msgStartGame.setter
    def msgStartGame(self, value):
         self.state.msgStartGame = value

    @property
    def game_started(self):
        return self.state.game_started
        
    @game_started.setter
    def game_started(self, value):
        self.state.game_started = value
         
    # --- Propiedades adiccionales para ui.py ---
    @property
    def lock(self):
        return self.state._lock_messages

    @property
    def receivedData(self):
        return self.state.receivedData
        
    @receivedData.setter
    def receivedData(self, value):
        self.state.receivedData = value

    @property
    def messagesServer(self):
        return self.state.messagesServer
        
    @property
    def server(self):
        # Exponemos el socket del Host para la validacion 'if self.network_manager.server:'
        return self._server.server_socket
        
    @property
    def player(self):
        # Exponemos el socket del Cliente
        return self.state.player
        
    @property
    def playerName(self):
        return self.state.playerName
        
    def stop_broadcast(self):
        self.state.running_broadcast = False
        
    @property
    def currentServer(self):
        """Devuelve info del server actual si es host, o el server seleccionado si es cliente."""
        if self.state.is_host:
            return {
                'name': self.state.gameName,
                'playerName': self.state.playerName,
                'ip': self.state.host,
                'port': self.state.port,
                'max_players': self.state.max_players,
                'password': self.state.password,
                'currentPlayers': len(self.state.get_connected_players())
            }
        return getattr(self, '_current_server', None)

    def get_exit_gameServer(self):
        """Devuelve y borra la lista de mensajes de salir/desconexion del juego."""
        # TODO: Implementar estado real si ui2.py lo demanda, por ahora lista vacía
        return []

    def send_selection_update(self, cartas_eleccion_serializada):
        """El Host usa este método para notificar a todos la lista actualizada de cartas_eleccion."""
        if not self.state.is_host:
            logger.error("Solo el Host puede enviar actualizaciones de selección.")
            return

        message = {
            "type": MessageType.SELECTION_UPDATE.value,
            "cartas_eleccion": cartas_eleccion_serializada 
        }
        self.broadcast_message(message)

    def exit_game(self, playerId, playerName):
        msgSalir = {
            "type": "SALIR",
            "playerId": playerId,
            "playerName": playerName
        }
        self.sendData(msgSalir)

    def get_game_info(self):
        """Obtiene información del juego."""
        return {
            "gameName": self.state.gameName,
            "host": self.state.host,
            "port": self.state.port,
            "max_players": self.state.max_players,
            "connected_players": self.connected_players,
            "is_host": self.state.is_host
        }

    def dprint(self, dic):
        """Para imprimir mas bonito un diccionario."""
        if type(dic) == dict:
            for clave, valor in dic.items():
                print(f"{str(clave).rjust(15)}: {valor}")
        else:
            return False