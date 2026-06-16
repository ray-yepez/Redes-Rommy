import socket
import threading
import logging
import time
from typing import Tuple
from .transport import Transport
from .state import NetworkState
from .config import NetworkConfig
from .types import ConnectedPlayer
from .exceptions import TimeoutException, ConnectionResetException
from .constants import MessageType, ConnectionStatus

logger = logging.getLogger(__name__)

class GameServer:
    """Lógica del servidor (HOST)."""
    
    def __init__(self, state: NetworkState, transport: Transport, config: NetworkConfig = None):
        self.state = state
        self.transport = transport
        self.config = config or NetworkConfig()
        self.server_socket = None
        self.next_player_id = 2  # 1 es el HOST
    
    def start(self, game_name: str, player_name: str, max_players: int, room_name: str) -> bool:
        """Inicia el servidor TCP."""
        try:
            self.state.gameName = game_name
            self.state.playerName = player_name
            self.state.max_players = max_players
            self.state.is_host = True
            self.state.running = True
            
            # Limpiar estado anterior para evitar cuentas fantasmas
            with self.state._lock_players:
                self.state.connected_players.clear()
            
            # Socket TCP
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(("0.0.0.0", self.config.TCP_PORT))
            self.server_socket.listen(max_players)
            
            logger.info(f"Servidor iniciado en puerto {self.config.TCP_PORT}")
            
            # Agregar HOST a lista de jugadores
            host_player = ConnectedPlayer(
                conn=self.server_socket,
                addr=("localhost", self.config.TCP_PORT),
                name=player_name,
                player_id=1,
                is_host=True
            )
            self.state.add_connected_player(host_player)
            
            # Hilo aceptador
            threading.Thread(target=self._accept_loop, daemon=True).start()
            return True
        except Exception as e:
            logger.error(f"Error iniciando servidor: {e}")
            return False
    
    def _accept_loop(self):
        """Loop infinito aceptando conexiones (CORRE EN HILO)."""
        while self.state.running:
            try:
                conn, addr = self.server_socket.accept()
                logger.info(f"Nueva conexión desde {addr}")
                
                # Recibir credenciales
                try:
                    credentials = self.transport.recv_atomic(conn, timeout=self.config.CONNECTION_TIMEOUT)
                    if credentials is None:
                        conn.close()
                        continue
                    password, player_name = credentials
                except TimeoutException:
                    logger.warning(f"Timeout esperando credenciales de {addr}")
                    conn.close()
                    continue
                except ValueError:
                    logger.warning(f"Credenciales inválidas de {addr}")
                    conn.close()
                    continue
                
                # Validar contraseña
                if password != self.state.password:
                    logger.warning(f"Contraseña incorrecta de {addr}")
                    self.transport.send_atomic(conn, ConnectionStatus.WRONG_PASSWORD.value)
                    conn.close()
                    continue
                
                # Validar espacio
                if len(self.state.get_connected_players()) >= self.state.max_players:
                    logger.warning(f"Servidor lleno, rechazando {addr}")
                    self.transport.send_atomic(conn, ConnectionStatus.FULL.value)
                    conn.close()
                    continue
                
                # Verificar reconexión
                existing_player = self._find_player_by_name(player_name)
                if existing_player:
                    logger.info(f"Reconexión: {player_name} (ID: {existing_player.player_id})")
                    player_id = existing_player.player_id
                    self.state.remove_connected_player(player_id)
                else:
                    player_id = self.next_player_id
                    self.next_player_id += 1
                
                # Crear objeto jugador
                player = ConnectedPlayer(
                    conn=conn,
                    addr=addr,
                    name=player_name,
                    player_id=player_id
                )
                self.state.add_connected_player(player)
                
                # Registrar actividad inicial para que el health monitor
                # no lo expulse antes de recibir su primer PONG
                self.state.update_last_activity(player_id, time.time())
                
                # Enviar confirmación
                response = {
                    "status": ConnectionStatus.CONNECTED.value,
                    "player_id": player_id,
                    "player_name": player_name
                }
                self.transport.send_atomic(conn, response)
                
                #######CAMBIOS PARA EL MENSAJE DE LA SALA################### 
                #(si. También era necesario colocar esas variables aquí para que el mensaje se actualice al entrar un nuevo jugador, y no solo al host)
                try:
                    self.state.mensaje = f"{player_name} se ha unido a la sala"
                    self.state.tiempoDelMensaje = time.time()
                except Exception:
                    pass
                
                self._broadcast_players()
                self._broadcast_notice(f"{player_name} se ha unido a la sala")
                # Hilo manejador para este jugador
                threading.Thread(
                    target=self._handle_player,
                    args=(player,),
                    daemon=True
                ).start()
                
            except OSError as e:
                # Ignorar error de socket cerrado intencionalmente
                if "10038" in str(e) or "10004" in str(e):
                    logger.info("Servidor cerrado, terminando accept_loop")
                    break
                logger.error(f"Error aceptando: {e}")
                continue
    
    def _handle_player(self, player: ConnectedPlayer):
        """Maneja comunicación con un jugador individual (CORRE EN HILO)."""
        logger.info(f"Iniciando handler para {player.name}")
        
        try:
            while self.state.running:
                try:
                    player.conn.settimeout(self.config.SOCKET_TIMEOUT)
                    data = self.transport.recv_atomic(player.conn)
                    
                    if data is None:
                        logger.info(f"Conexión cerrada remotamente por {player.name}")
                        break
                    
                    # Procesar mensaje
                    self._process_message(player, data)
                    
                except socket.timeout:
                    continue  # Timeout normal por inactividad, seguir escuchando
                except ConnectionResetException:
                    logger.warning(f"Conexión reseteada por {player.name}")
                    break
                except Exception as e:
                    logger.error(f"Error manejando {player.name}: {e}")
                    continue
        finally:
            try:
                player.conn.close()
            except:
                pass
            self.state.remove_connected_player(player.player_id)
            self._broadcast_players()
            logger.info(f"Handler terminado para {player.name}")
    
    def _broadcast_players(self):
        """Notifica a todos los clientes la nueva lista de jugadores."""
        serializable_players = [(p.addr, p.name, p.player_id) for p in self.state.get_connected_players()]
        message = {"type": "UPDATE_PLAYERS", "players": serializable_players}
        for p in self.state.get_connected_players():
            if not p.is_host:
                try:
                    self.transport.send_atomic(p.conn, message)
                except:
                    pass
    
    def _broadcast_notice(self, mensaje: str):
        """Envia un aviso a todos los clientes conectados, poara que también les aparezca el popup del aviso de conexión (No solo al HOST)"""
        message = {"type": "NOTICE", "mensaje": mensaje, "timestamp": time.time()}
        for p in self.state.get_connected_players():
            if not p.is_host:
                try:
                    self.transport.send_atomic(p.conn, message)
                except:
                    pass
    
    def _process_message(self, player: ConnectedPlayer, data: dict):
        """Procesa un mensaje recibido en el Host y lo retransmite al resto."""
        if not isinstance(data, dict):
            return
            
        msg_type = data.get("type")

        is_pong = (msg_type == "PONG" or 
                   (hasattr(MessageType.PONG, 'value') and msg_type == MessageType.PONG.value))

        if is_pong:
            try:
                ping_time = data.get("timestamp")
                
                if ping_time is not None:
                    latencia = (time.time() - float(ping_time)) * 1000
                else:
                    latencia = 0.50
                
                if latencia <= 0 or latencia > 2000:
                    latencia = 0.45
                
                if not hasattr(self, 'ultimo_print_latencia'):
                    self.ultimo_print_latencia = {}
                
                ahora_print = time.time()
                ultimo_print = self.ultimo_print_latencia.get(player.player_id, 0)

                if ahora_print - ultimo_print > 5:   
                    print(f"Monitor Heartbeat - Latencia Jugador {player.player_id} ({player.name}): {latencia:.2f} ms")
                    self.ultimo_print_latencia[player.player_id] = ahora_print

                self.state.update_last_activity(player.player_id, time.time())
            
            except Exception as e:

                self.state.update_last_activity(player.player_id, time.time())
                print(f"[Sistema Red] Error calculando latencia pero jugador reportado vivo: {e}")

            return
        
            
        elif msg_type == "CHAT":
            logger.debug(f"CHAT de {player.name}: {data.get('mensaje')}")
            
            # Formateamos el mensaje y lo metemos a la lista para Pygame
            msgFormat = f"{player.name}: {data.get('mensaje', '')}"
            
            # CORRECCIÓN 2: Imprimir en la terminal del Servidor cuando un cliente escribe
            print(f"\n[CHAT - RECIBIDO EN SERVIDOR] {player.name}: {data.get('mensaje', '')}")
            
            with self.state._lock_messages:
                self.state.messagesServer.append(msgFormat)
                if len(self.state.messagesServer) > 20:
                    self.state.messagesServer.pop(0)
            
            # --- NUEVO: Encender notificación para el HOST ---
            self.state.has_unread_chat = True
            
            # Preparar datos para retransmitir
            data["playerName"] = player.name
            data["notificar"] = True # --- NUEVO: Flag para los clientes ---
            
            for p in self.state.get_connected_players():
                if not p.is_host and p.player_id != player.player_id:
                    try:
                        self.transport.send_atomic(p.conn, data)
                    except:
                        pass
            return

        else:
            # ── Todas las jugadas del juego ──────────────────────────────────
            # 1. Anotar el sender para que el Host sepa de quién viene
            data["sender_id"] = player.player_id
            
            # 2. Guardar en la cola del Host (get_moves_gameServer)
            self.state.add_move(data, server=True)
            
            # 3. RETRANSMITIR a todos los demás clientes (excepto al que envió)
            #    Así el otro jugador recibe la jugada en su get_moves_game()
            for p in self.state.get_connected_players():
                if not p.is_host and p.player_id != player.player_id:
                    try:
                        self.transport.send_atomic(p.conn, data)
                        logger.debug(f"Retransmitiendo {msg_type} de {player.name} a {p.name}")
                    except Exception as e:
                        logger.warning(f"Error retransmitiendo a {p.name}: {e}")
    
    def _find_player_by_name(self, name: str):
        """Busca jugador por nombre (usado para reconexiones)."""
        for p in self.state.get_connected_players():
            if p.name == name:
                return p
        return None
