import socket
import threading
import logging
from typing import Tuple
import time

from .transport import Transport
from .state import NetworkState
from .config import NetworkConfig
from .types import ServerInfo
from .exceptions import TimeoutException, AuthenticationException, ServerFullException
from .constants import MessageType, ConnectionStatus

logger = logging.getLogger(__name__)

class GameClient:
    """Lógica del cliente."""
    
    def __init__(self, state: NetworkState, transport: Transport, config: NetworkConfig = None):
        self.state = state
        self.transport = transport
        self.config = config or NetworkConfig()
    
    def connect(self, server_info: dict) -> Tuple[bool, str]:
        """Conecta a un servidor."""
        try:
            self.state.player = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Extraer info
            ip = server_info.get("ip")
            port = server_info.get("port", self.config.TCP_PORT)
            password = server_info.get("password", "")
            # Priorizar el nombre que la UI guardó en server_info, luego state, luego defecto
            player_name = (server_info.get("playerName") or
                           self.state.playerName or "Player")
            
            self.state.player.connect((ip, port))
            logger.info(f"Conectando a {ip}:{port}")
            
            # Enviar credenciales (contraseña, nombre)
            credentials = (password, player_name)
            if not self.transport.send_atomic(self.state.player, credentials):
                return False, "Error enviando credenciales"
            
            # Recibir confirmación
            response = self.transport.recv_atomic(self.state.player, timeout=self.config.CONNECTION_TIMEOUT)
            
            if isinstance(response, dict) and response.get("status") == ConnectionStatus.CONNECTED.value:
                self.state.player_id = response["player_id"]
                self.state.player_name = response["player_name"]
                self.state.host = ip
                self.state.port = port
                self.state.is_host = False
                self.state.is_connected = True
                self.state.running = True
                self.state.server_info_to_reconnect = server_info
                
                # Iniciar el hilo receptor del cliente
                threading.Thread(target=self._receive_loop, daemon=True).start()
                
                logger.info(f"Conectado como {self.state.player_name} (ID: {self.state.player_id})")
                return True, "Conectado exitosamente"
            
            elif response == ConnectionStatus.WRONG_PASSWORD.value:
                return False, "Contraseña incorrecta"
            elif response == ConnectionStatus.FULL.value:
                return False, "Servidor está lleno"
            else:
                return False, f"Error desconocido: {response}"
        
        except Exception as e:
            logger.error(f"Error conectando al Host: {e}")
            return False, str(e)
    
    def _receive_loop(self):
        """Loop de recepción infinita (CORRE EN HILO)."""
        while self.state.running and self.state.player:
            try:
                self.state.player.settimeout(self.config.SOCKET_TIMEOUT)
                data = self.transport.recv_atomic(self.state.player)
                
                if data is None:
                    logger.info("El servidor cerró la conexión")
                    break
                
                self._process_message(data)
                
            except socket.timeout:
                continue
            except ConnectionResetError:
                logger.warning("Conexión reseteada por el servidor")
                break
            except Exception as e:
                logger.error(f"Error recibiendo paquete: {e}")
                continue
        
        self.state.is_connected = False
        logger.info("Hilo de recepción del cliente finalizado")
    
    def _process_message(self, data: dict):
        """Procesa y rutéa el mensaje recibido del Host."""
        if not isinstance(data, dict):
            return
            
        msg_type = data.get("type")
        
        if msg_type == MessageType.PING.value:
            logger.debug("PING recibido, devolviendo PONG automáticamente")
            pong = {
                "type": MessageType.PONG.value,
                "timestamp": data.get("timestamp")
            }
            if not self.transport.send_atomic(self.state.player, pong):
                logger.warning("Fallo al enviar PONG de respuesta al PING del Host.")
            return

        elif msg_type == MessageType.START_GAME.value:
            self.state.msgStartGame.update(data)
            self.state.receivedData = data
            self.state.add_incoming_message(msg_type, data)
        elif msg_type == "CHAT":
            msgFormat = f"{data.get('playerName', 'Alguien')}: {data.get('mensaje', '')}"
            with self.state._lock_messages:
                self.state.messagesServer.append(msgFormat)
                if len(self.state.messagesServer) > 20:
                    self.state.messagesServer.pop(0)
                    # CAMBIO CLAVE: Lo añadimos a la cola de movimientos para que la UI lo detecte
            self.state.add_move(data, server=False)
        elif msg_type in [
            MessageType.ELECTION_CARDS.value,
            MessageType.SELECTION_UPDATE.value,
        ]:
            self.state.update_game_state(data)
        elif msg_type in [
            MessageType.BAJARSE.value,
            MessageType.TOMAR_CARTA.value,
            MessageType.DESCARTE.value,
            MessageType.TOMAR_DESCARTE.value,
            MessageType.COMPRAR_CARTA.value,
            MessageType.ESTADO_CARTAS.value,
            MessageType.ORDEN_COMPLETO.value,
            MessageType.PASAR_DESCARTE.value,
            MessageType.INICIAR_COMPRA.value,
            MessageType.PASAR_COMPRA.value,
            MessageType.REALIZAR_COMPRA.value,
            MessageType.SWAP_JOKER.value,
            MessageType.SALIR.value,
            MessageType.DESCONEXION.value,
            MessageType.INSERTAR_CARTA.value,
        ]:
            # Jugadas que el Cliente recibe (retransmitidas por el servidor)
            self.state.add_move(data, server=False)
        elif msg_type == MessageType.PLAYER_ORDER.value:
            # PLAYER_ORDER es especial: va a incoming_messages para que ui2.py lo lea
            self.state.receivedData = data
            self.state.add_incoming_message(msg_type, data)
        elif msg_type == MessageType.UPDATE_PLAYERS.value:
            self.state.receivedData = data
            self.state.add_incoming_message(msg_type, data)
        else:
            self.state.receivedData = data
            self.state.add_incoming_message(msg_type, data)
    
    def send(self, data: dict) -> bool:
        """Envía datos arbitrarios al Host."""
        if not self.state.player or not self.state.running:
            logger.warning("Intento de envío fallido: No conectado o no corriendo")
            return False
        
        try:
            return self.transport.send_atomic(self.state.player, data)
        except Exception as e:
            logger.error(f"Error durante el envío: {e}")
            return False
