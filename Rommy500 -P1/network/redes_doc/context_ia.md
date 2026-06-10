# CONTEXTO DE IA: REFACTORIZACIÓN DEL MÓDULO DE RED
## RUMMY 500 - Proyecto Gaming Multijugador

**Fecha**: 2026-05-08  
**Rol del asistente**: Ingeniero de Redes  
**Objetivo**: Refactorizar `network.py` de 840 líneas monolíticas en una arquitectura modular escalable  
**Restricción crítica**: Cero cambios en la interfaz pública — `main.py` y `ui2.py` deben funcionar sin modificación  

---

## 1. DIAGNÓSTICO ACTUAL

### 1.1 Problemas Identificados

El archivo `network.py` (840 líneas) viola el principio de responsabilidad única:

- **Todo en una clase**: `NetworkManager` es simultáneamente servidor TCP, cliente TCP, emisor UDP, receptor UDP, gestor de estado del juego y monitor de salud de conexiones.
- **Atributos desorganizados**: 30+ variables en `__init__()` sin estructura lógica, variables duplicadas (`received_data` vs `receivedData`), comentarios `# Nuevo...` indicando crecimiento sin plan.
- **Estado del juego mezclado**: `moves_game`, `game_state`, `msgStartGame` viven en el módulo de red cuando deberían ser orquestados externamente.
- **Manejo de errores inconsistente**: Algunos `except:` capturan todo sin logging. Otros muy específicos. Imposible reproducir bugs.
- **Variables comentadas**: `#self.ready_players`, `#self.ready_state`, `#self.game_started` sin explicación de por qué existen.
- **Locks duplicados**: `self.lock` y `self.socet_lock` sin claridad de cuál protege qué.
- **Print en lugar de logging**: Nada de `logging`, todo `print()` — imposible controlar verbosidad en producción.
- **Números mágicos**: Puerto 5555, 5554, timeout 30s, max_retries 5, buffer 8192 bytes hardcodeados en múltiples lugares.

### 1.2 Impacto en Equipo Multidisciplinario

Con 8 personas trabajando en red + 10 en otros departamentos:
- **Merge conflicts** serán frecuentes en cambios simultáneos.
- **Bugs silenciosos** por inconsistencias en manejo de estado.
- **Onboarding lento**: Nuevos desarrolladores no saben dónde tocar sin romper.
- **Testeo fragmentado**: No se puede probar un componente sin maquinar todo.

---

## 2. ARQUITECTURA PROPUESTA

### 2.1 Patrón: Facade + Inyección de Dependencias

```
network/
    __init__.py          ← Exporta NetworkManager (interfaz pública)
    manager.py           ← Fachada orquestadora (delegación)
    
    # Capas de funcionalidad (cada una ~100 líneas)
    constants.py         ← Enums y constantes centralizadas
    config.py            ← Configuración (puertos, timeouts, buffers)
    exceptions.py        ← Excepciones de red personalizadas
    types.py             ← Dataclasses para tipado fuerte (ConnectedPlayer, etc.)
    
    # Capas de implementación
    transport.py         ← Protocolo atómico (send_atomic, recv_atomic, _recv_exact)
    state.py             ← Gestión de estado compartido (colas, locks)
    
    server.py            ← Lógica HOST (acceptConnections, handlePlayer)
    client.py            ← Lógica CLIENTE (connectToServer, receiveData, sendData)
    discovery.py         ← UDP broadcast (broadcast_server, listenForServers)
    health.py            ← Monitoreo (ping-pong, health_check)
    
    # Testing
    tests/
        test_transport.py
        test_server.py
        test_client.py
        test_integration.py
```

### 2.2 Flujo de Dependencias

```
NetworkManager (fachada)
    ↓ delega en
Transport + State (infraestructura base)
    ↓ usados por
Server / Client / Discovery / Health
    ↓ acceden a
Constants / Config / Exceptions / Types
```

**Principio**: Las capas inferiores nunca importan de las superiores. Flujo de dependencias unidireccional.

### 2.3 Interfaz Pública (CERO Cambios)

El código existente (`main.py`, `ui2.py`) llamará exactamente igual:

```python
from network import NetworkManager

nm = NetworkManager()
nm.start_server("Sala1", "pass123", 7, "Mi Sala")
nm.connectToServer(server_dict)
nm.sendData({"type": "BAJARSE", ...})
nm.get_incoming_messages()  # etc.
```

Internamente, estos métodos delegarán a los módulos. Usuarios externos: sin cambios.

---

## 3. ESPECIFICACIÓN POR MÓDULO

### 3.1 `constants.py` — Enums Centralizados

**Propósito**: Eliminar strings mágicos como `"PING"`, `"BAJARSE"`, `"START_GAME"`.

```python
# network/constants.py
from enum import Enum

class MessageType(Enum):
    """Tipos de mensaje en el protocolo de red."""
    PING = "PING"
    PONG = "PONG"
    START_GAME = "START_GAME"
    SELECTION_UPDATE = "SELECTION_UPDATE"
    ELECTION_CARDS = "ELECTION_CARDS"
    ESTADO_CARTAS = "ESTADO_CARTAS"
    ORDEN_COMPLETO = "ORDEN_COMPLETO"
    BAJARSE = "BAJARSE"
    TOMAR_DESCARTE = "TOMAR_DESCARTE"
    TOMAR_CARTA = "TOMAR_CARTA"
    DESCARTE = "DESCARTE"
    COMPRAR_CARTA = "COMPRAR_CARTA"
    # ... más tipos según juego.py

class ConnectionStatus(Enum):
    """Estados de conexión."""
    CONNECTED = "CONNECTED"
    WRONG_PASSWORD = "WRONG_PASSWORD"
    FULL = "FULL"
    DISCONNECTED = "DISCONNECTED"

class ErrorCode(Enum):
    """Códigos de error para excepciones."""
    TIMEOUT = "TIMEOUT"
    CONNECTION_RESET = "CONNECTION_RESET"
    SOCKET_ERROR = "SOCKET_ERROR"
    AUTH_FAILED = "AUTH_FAILED"
    SERVER_FULL = "SERVER_FULL"
    NETWORK_UNREACHABLE = "NETWORK_UNREACHABLE"
```

**Nota**: Cambiar todos los strings hardcodeados en otros módulos por `MessageType.PING.value`.

---

### 3.2 `config.py` — Configuración Centralizada

**Propósito**: Reemplazar números mágicos. Fácil ajuste sin buscar en todo el código.

```python
# network/config.py
from dataclasses import dataclass

@dataclass
class NetworkConfig:
    """Configuración de red del servidor y cliente."""
    
    # Puertos
    TCP_PORT: int = 5555
    BROADCAST_PORT: int = 5554
    
    # Timeouts (segundos)
    SOCKET_TIMEOUT: int = 30
    HEALTH_CHECK_INTERVAL: int = 60
    PING_TIMEOUT: int = 5
    CONNECTION_TIMEOUT: int = 10
    
    # Reintentos
    MAX_RECV_RETRIES: int = 5
    RECONNECT_MAX_ATTEMPTS: int = 3
    RECONNECT_BASE_DELAY: float = 1.0  # segundos (escalado exponencial)
    
    # Buffers y límites
    BUFFER_SIZE: int = 8192
    MAX_MESSAGE_SIZE: int = 1_000_000  # 1MB límite
    
    # Comportamiento
    BROADCAST_INTERVAL: float = 3.0  # broadcast UDP cada 3 segundos
    ENABLE_DEBUG: bool = False
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR

# Instancia global (puede ser sobrescrita en tests)
DEFAULT_CONFIG = NetworkConfig()
```

---

### 3.3 `exceptions.py` — Excepciones Personalizadas

**Propósito**: Handling estructurado, no `except: pass`.

```python
# network/exceptions.py
from .constants import ErrorCode

class NetworkException(Exception):
    """Base para todas las excepciones de red."""
    def __init__(self, code: ErrorCode, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"[{code.value}] {message}")

class TimeoutException(NetworkException):
    """Socket timeout o timeout de espera de respuesta."""
    def __init__(self, message: str, player_id: int = None):
        super().__init__(ErrorCode.TIMEOUT, message, {"player_id": player_id})

class ConnectionResetException(NetworkException):
    """Conexión cerrada por el otro extremo."""
    def __init__(self, message: str, addr: tuple = None):
        super().__init__(ErrorCode.CONNECTION_RESET, message, {"address": addr})

class AuthenticationException(NetworkException):
    """Fallo de autenticación (contraseña incorrecta)."""
    def __init__(self, message: str = "Contraseña incorrecta"):
        super().__init__(ErrorCode.AUTH_FAILED, message)

class ServerFullException(NetworkException):
    """Servidor ha alcanzado máximo de jugadores."""
    def __init__(self, max_players: int):
        super().__init__(ErrorCode.SERVER_FULL, 
                        f"Servidor lleno ({max_players} jugadores)", 
                        {"max_players": max_players})
```

---

### 3.4 `types.py` — Dataclasses para Tipado Fuerte

**Propósito**: Reemplazar tuplas como `(conn, addr, name, id)` por objetos con nombres.

```python
# network/types.py
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
```

---

### 3.5 `transport.py` — Protocolo Atómico

**Propósito**: Envío/recepción confiable de mensajes pickle.  
**Responsabilidades**: `send_atomic`, `recv_atomic`, `_recv_exact` + reintentos.

```python
# network/transport.py (aprox. 80 líneas)
import socket
import struct
import pickle
import logging
from typing import Optional, Any
from .config import DEFAULT_CONFIG
from .exceptions import TimeoutException, ConnectionResetException

logger = logging.getLogger(__name__)

class Transport:
    """Capa de transporte: envío/recepción confiable con pickle."""
    
    def __init__(self, config=None):
        self.config = config or DEFAULT_CONFIG
    
    def send_atomic(self, sock: socket.socket, data: Any) -> bool:
        """Envía datos como un bloque atómico.
        
        Formato: [4 bytes longitud big-endian][datos pickle]
        """
        try:
            pickled = pickle.dumps(data)
            length = len(pickled)
            
            if length > self.config.MAX_MESSAGE_SIZE:
                raise ValueError(f"Mensaje demasiado grande: {length} bytes")
            
            header = struct.pack('>I', length)
            sock.sendall(header)
            sock.sendall(pickled)
            
            logger.debug(f"Mensaje enviado: {length} bytes")
            return True
        except Exception as e:
            logger.error(f"Error en send_atomic: {e}")
            return False
    
    def recv_atomic(self, sock: socket.socket, timeout: Optional[int] = None) -> Optional[Any]:
        """Recibe un mensaje completo en formato atómico."""
        original_timeout = sock.gettimeout()
        
        try:
            if timeout is not None:
                sock.settimeout(timeout)
            
            # Recibir cabecera (4 bytes)
            header = self._recv_exact(sock, 4)
            if header is None:
                return None
            
            length = struct.unpack('>I', header)[0]
            
            # Recibir payload
            data = self._recv_exact(sock, length)
            if data is None:
                return None
            
            logger.debug(f"Mensaje recibido: {length} bytes")
            return pickle.loads(data)
            
        except socket.timeout:
            logger.warning("Timeout en recv_atomic")
            raise TimeoutException("Socket timeout en recepción")
        except Exception as e:
            logger.error(f"Error en recv_atomic: {e}")
            return None
        finally:
            if timeout is not None:
                sock.settimeout(original_timeout)
    
    def _recv_exact(self, sock: socket.socket, n: int) -> Optional[bytes]:
        """Recibe exactamente n bytes, reintentando en case de timeout."""
        data = b''
        retries = 0
        
        while len(data) < n:
            try:
                chunk = sock.recv(n - len(data))
                if not chunk:
                    logger.warning("Socket cerrado remotamente")
                    return None
                data += chunk
                retries = 0
            except socket.timeout:
                retries += 1
                logger.warning(f"Timeout en _recv_exact ({retries}/{self.config.MAX_RECV_RETRIES})")
                if retries >= self.config.MAX_RECV_RETRIES:
                    raise TimeoutException(f"Max retries ({self.config.MAX_RECV_RETRIES}) alcanzado")
                continue
            except Exception as e:
                logger.error(f"Error en _recv_exact: {e}")
                return None
        
        return data
```

**Nota**: Este módulo es el más crítico. Debe ser revisado exhaustivamente y testeado.

---

### 3.6 `state.py` — Gestión de Estado Compartido

**Propósito**: Colas thread-safe, locks organizados, acceso sincronizado a variables del juego.

```python
# network/state.py (aprox. 100 líneas)
import threading
from queue import Queue
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class NetworkState:
    """Contenedor thread-safe para el estado de conexión y juego."""
    
    def __init__(self):
        # Locks (un lock por sección lógica, no un mega-lock)
        self._lock_players = threading.Lock()
        self._lock_game = threading.Lock()
        self._lock_messages = threading.Lock()
        
        # Colas thread-safe (mejor que listas simples)
        self.incoming_messages = Queue()  # Mensajes entrantes
        self.moves_game = Queue()         # Jugadas del cliente
        self.moves_gameServer = Queue()   # Jugadas para el HOST
        
        # Diccionarios protegidos
        self.game_state = {}              # Estado de juego
        self.msgStartGame = {}            # Señal de inicio
        self.messagesServer = []          # Registro de mensajes
        
        # Información de conexión
        self.is_connected = False
        self.receive_thread_running = False
        self.server_info_to_reconnect = None
        self.player_id = None
        self.host = None
        self.port = None
        self.player_name = None
        self.is_host = False
        self.running = False
        
        # Health check
        self.last_activity = {}           # {player_id: timestamp}
        self.connected_players = []
        
        logger.info("NetworkState inicializado")
    
    def add_incoming_message(self, msg_type: str, data: dict = None):
        """Agrega mensaje entrante (thread-safe)."""
        self.incoming_messages.put({"type": msg_type, "data": data or {}})
    
    def get_incoming_messages(self) -> List[dict]:
        """Extrae todos los mensajes pendientes."""
        msgs = []
        while not self.incoming_messages.empty():
            try:
                msgs.append(self.incoming_messages.get_nowait())
            except:
                break
        return msgs
    
    def add_move(self, move: dict, server=False):
        """Agrega una jugada (cliente o servidor)."""
        queue = self.moves_gameServer if server else self.moves_game
        queue.put(move)
    
    def get_moves(self, server=False) -> List[dict]:
        """Extrae todas las jugadas pendientes."""
        queue = self.moves_gameServer if server else self.moves_game
        moves = []
        while not queue.empty():
            try:
                moves.append(queue.get_nowait())
            except:
                break
        return moves
    
    def update_game_state(self, state_dict: dict):
        """Actualiza el estado del juego de forma sincronizada."""
        with self._lock_game:
            self.game_state.update(state_dict)
            logger.debug(f"Game state actualizado: {list(state_dict.keys())}")
    
    def get_game_state(self) -> dict:
        """Lee el estado del juego y lo vacía."""
        with self._lock_game:
            state = self.game_state.copy()
            self.game_state.clear()
            return state
    
    def add_connected_player(self, player):
        """Agrega jugador a lista (usando dataclass ConnectedPlayer)."""
        with self._lock_players:
            self.connected_players.append(player)
            logger.info(f"Jugador agregado: {player.name} (ID: {player.player_id})")
    
    def remove_connected_player(self, player_id: int):
        """Remueve jugador por ID."""
        with self._lock_players:
            self.connected_players = [p for p in self.connected_players if p.player_id != player_id]
            logger.info(f"Jugador removido (ID: {player_id})")
    
    def get_connected_players(self) -> List:
        """Lee lista de jugadores conectados."""
        with self._lock_players:
            return self.connected_players.copy()
    
    def update_last_activity(self, player_id: int, timestamp: float):
        """Registra actividad de un jugador (health check)."""
        with self._lock_players:
            self.last_activity[player_id] = timestamp
```

**Cambio importante**: Reemplazar `list.append()` y acceso directo por métodos sincronizados. Si otro código intenta `nm.state.incoming_messages.append(...)`, fallará (porque es un Queue, no una list). Esto es intencional y bueno: obliga el uso correcto.

---

### 3.7 `server.py` — Lógica del HOST

**Propósito**: `acceptConnections`, `handlePlayer`, reconexión.  
**Crítico**: Esta es la lógica más compleja. Requiere 2 desarrolladores.

```python
# network/server.py (aprox. 200 líneas)
import socket
import threading
import logging
from typing import Tuple
from .transport import Transport
from .state import NetworkState
from .config import NetworkConfig
from .types import ConnectedPlayer
from .exceptions import TimeoutException, ConnectionResetException
from .constants import MessageType

logger = logging.getLogger(__name__)

class GameServer:
    """Lógica del servidor (HOST)."""
    
    def __init__(self, state: NetworkState, transport: Transport, config: NetworkConfig = None):
        self.state = state
        self.transport = transport
        self.config = config
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
                    password, player_name = self.transport.recv_atomic(conn, timeout=self.config.CONNECTION_TIMEOUT)
                except TimeoutException:
                    logger.warning(f"Timeout esperando credenciales de {addr}")
                    conn.close()
                    continue
                
                # Validar contraseña
                if password != self.state.password:
                    logger.warning(f"Contraseña incorrecta de {addr}")
                    self.transport.send_atomic(conn, MessageType.WRONG_PASSWORD.value)
                    conn.close()
                    continue
                
                # Validar espacio
                if len(self.state.connected_players) >= self.state.max_players:
                    logger.warning(f"Servidor lleno, rechazando {addr}")
                    self.transport.send_atomic(conn, MessageType.FULL.value)
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
                
                # Enviar confirmación
                response = {
                    "status": MessageType.CONNECTED.value,
                    "player_id": player_id,
                    "player_name": player_name
                }
                self.transport.send_atomic(conn, response)
                
                # Hilo manejador para este jugador
                threading.Thread(
                    target=self._handle_player,
                    args=(player,),
                    daemon=True
                ).start()
                
            except OSError as e:
                if "10038" in str(e):
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
                        logger.info(f"Conexión cerrada por {player.name}")
                        break
                    
                    # Procesar mensaje
                    self._process_message(player, data)
                    
                except socket.timeout:
                    continue  # Timeout normal, seguir escuchando
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
            logger.info(f"Handler terminado para {player.name}")
    
    def _process_message(self, player: ConnectedPlayer, data: dict):
        """Procesa un mensaje recibido."""
        msg_type = data.get("type")
        
        if msg_type == MessageType.PONG.value:
            self.state.update_last_activity(player.player_id, __import__('time').time())
            logger.debug(f"PONG recibido de {player.name}")
        else:
            # Otros mensajes
            logger.debug(f"Mensaje de {player.name}: {msg_type}")
            self.state.add_move(data, server=True)
    
    def _find_player_by_name(self, name: str):
        """Busca jugador por nombre (para reconexión)."""
        for p in self.state.get_connected_players():
            if p.name == name:
                return p
        return None
```

---

### 3.8 `client.py` — Lógica del CLIENTE

**Propósito**: `connectToServer`, `receiveData`, `sendData`.

```python
# network/client.py (aprox. 120 líneas)
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
from .constants import MessageType

logger = logging.getLogger(__name__)

class GameClient:
    """Lógica del cliente."""
    
    def __init__(self, state: NetworkState, transport: Transport, config: NetworkConfig = None):
        self.state = state
        self.transport = transport
        self.config = config or NetworkConfig()
    
    def connect(self, server_info: ServerInfo) -> Tuple[bool, str]:
        """Conecta a un servidor."""
        try:
            self.state.player = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.state.player.connect((server_info.ip, server_info.port))
            
            logger.info(f"Socket creado, conectando a {server_info.ip}:{server_info.port}")
            
            # Enviar credenciales
            credentials = (server_info.password or "", server_info.player_name)
            if not self.transport.send_atomic(self.state.player, credentials):
                return False, "Error enviando credenciales"
            
            # Recibir respuesta
            response = self.transport.recv_atomic(self.state.player, timeout=self.config.CONNECTION_TIMEOUT)
            
            if isinstance(response, dict) and response.get("status") == MessageType.CONNECTED.value:
                self.state.player_id = response["player_id"]
                self.state.player_name = response["player_name"]
                self.state.host = server_info.ip
                self.state.port = server_info.port
                self.state.is_host = False
                self.state.is_connected = True
                self.state.running = True
                self.state.server_info_to_reconnect = server_info
                
                # Hilo receptor
                threading.Thread(target=self._receive_loop, daemon=True).start()
                
                logger.info(f"Conectado como {self.state.player_name} (ID: {self.state.player_id})")
                return True, "Conectado exitosamente"
            
            elif response == MessageType.WRONG_PASSWORD.value:
                return False, "Contraseña incorrecta"
            elif response == MessageType.FULL.value:
                return False, "Servidor está lleno"
            else:
                return False, f"Error desconocido: {response}"
        
        except Exception as e:
            logger.error(f"Error conectando: {e}")
            return False, str(e)
    
    def _receive_loop(self):
        """Loop de recepción (CORRE EN HILO)."""
        while self.state.running and self.state.player:
            try:
                self.state.player.settimeout(self.config.SOCKET_TIMEOUT)
                data = self.transport.recv_atomic(self.state.player)
                
                if data is None:
                    logger.info("Servidor cerró conexión")
                    break
                
                # Procesar mensaje
                self._process_message(data)
                
            except socket.timeout:
                continue
            except ConnectionResetError:
                logger.warning("Conexión reseteada")
                break
            except Exception as e:
                logger.error(f"Error recibiendo: {e}")
                continue
        
        self.state.is_connected = False
        logger.info("Receive loop terminado")
    
    def _process_message(self, data: dict):
        """Procesa mensaje recibido del servidor."""
        msg_type = data.get("type")
        
        if msg_type == MessageType.PING.value:
            logger.debug("PING recibido, enviando PONG")
            pong = {
                "type": MessageType.PONG.value,
                "timestamp": data.get("timestamp")
            }
            self.send(pong)
        elif msg_type == MessageType.START_GAME.value:
            self.state.msgStartGame.update(data)
        elif msg_type in [MessageType.ELECTION_CARDS.value, MessageType.SELECTION_UPDATE.value]:
            self.state.update_game_state(data)
        elif msg_type in [MessageType.BAJARSE.value, MessageType.TOMAR_CARTA.value]:
            self.state.add_move(data)
        else:
            self.state.add_incoming_message(msg_type, data)
    
    def send(self, data: dict) -> bool:
        """Envía datos al servidor."""
        if not self.state.player or not self.state.running:
            logger.warning("No conectado o no running")
            return False
        
        try:
            return self.transport.send_atomic(self.state.player, data)
        except Exception as e:
            logger.error(f"Error enviando: {e}")
            return False
```

---

### 3.9 `discovery.py` — UDP Broadcast

**Propósito**: `broadcast_server`, `listenForServers`, `discoverServers`.

```python
# network/discovery.py (aprox. 80 líneas)
import socket
import threading
import json
import logging
import time

from .state import NetworkState
from .config import NetworkConfig
from .types import ServerInfo

logger = logging.getLogger(__name__)

class Discovery:
    """Servicio de descubrimiento UDP broadcast."""
    
    def __init__(self, state: NetworkState, config: NetworkConfig = None):
        self.state = state
        self.config = config or NetworkConfig()
    
    def start_broadcast(self):
        """Inicia broadcast periódico del servidor (CORRE EN HILO)."""
        def broadcast_loop():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            while self.state.running_broadcast:
                try:
                    server_data = {
                        "name": self.state.gameName,
                        "player_name": self.state.playerName,
                        "ip": self.state.host,
                        "port": self.state.port,
                        "max_players": self.state.max_players,
                        "current_players": len(self.state.connected_players),
                        # Nota: password NO se incluye en broadcast
                    }
                    
                    packet = json.dumps(server_data).encode('utf-8')
                    sock.sendto(packet, ('<broadcast>', self.config.BROADCAST_PORT))
                    logger.debug(f"Broadcast enviado: {self.state.gameName}")
                    
                    time.sleep(self.config.BROADCAST_INTERVAL)
                except Exception as e:
                    logger.error(f"Error en broadcast: {e}")
                    break
            
            sock.close()
        
        self.state.running_broadcast = True
        threading.Thread(target=broadcast_loop, daemon=True).start()
    
    def discover_servers(self, timeout: int = 5) -> list:
        """Escucha broadcasts y devuelve lista de servidores."""
        servers = []
        
        def listen_loop():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('0.0.0.0', self.config.BROADCAST_PORT))
            sock.settimeout(1)
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    data, addr = sock.recvfrom(1024)
                    server_dict = json.loads(data.decode('utf-8'))
                    
                    # Evitar duplicados
                    if not any(s["ip"] == server_dict["ip"] for s in servers):
                        servers.append(server_dict)
                        logger.info(f"Servidor descubierto: {server_dict['name']}")
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f"Error escuchando: {e}")
                    break
            
            sock.close()
        
        listen_thread = threading.Thread(target=listen_loop, daemon=True)
        listen_thread.start()
        listen_thread.join(timeout + 1)
        
        return servers
```

---

### 3.10 `health.py` — Monitoreo de Conexiones

**Propósito**: Ping-pong, detección de jugadores desconectados.

```python
# network/health.py (aprox. 80 líneas)
import threading
import time
import logging

from .transport import Transport
from .state import NetworkState
from .config import NetworkConfig
from .constants import MessageType

logger = logging.getLogger(__name__)

class HealthMonitor:
    """Monitoreo de salud de conexiones (ping-pong)."""
    
    def __init__(self, state: NetworkState, transport: Transport, config: NetworkConfig = None):
        self.state = state
        self.transport = transport
        self.config = config or NetworkConfig()
    
    def start_health_check(self):
        """Inicia health check periódico (CORRE EN HILO)."""
        def health_check_loop():
            while self.state.running:
                time.sleep(self.config.HEALTH_CHECK_INTERVAL)
                
                if len(self.state.connected_players) > 1:
                    logger.info("Ejecutando health check...")
                    self._check_players()
        
        threading.Thread(target=health_check_loop, daemon=True).start()
    
    def _check_players(self):
        """Envía PING a todos los jugadores y detecta no-responders."""
        disconnected = []
        
        for player in self.state.get_connected_players():
            if player.is_host:
                continue  # No hacer PING al HOST
            
            try:
                player.conn.settimeout(self.config.PING_TIMEOUT)
                
                # Enviar PING
                msg = {
                    "type": MessageType.PING.value,
                    "timestamp": time.time()
                }
                self.transport.send_atomic(player.conn, msg)
                logger.info(f"PING enviado a {player.name}")
                
                # Verificar actividad reciente (PONG se registra automáticamente)
                last_activity = self.state.last_activity.get(player.player_id, 0)
                if time.time() - last_activity > self.config.PING_TIMEOUT:
                    logger.warning(f"Jugador {player.name} no respondió")
                    disconnected.append(player.player_id)
            
            except Exception as e:
                logger.error(f"Error con {player.name}: {e}")
                disconnected.append(player.player_id)
        
        # Remover desconectados
        for player_id in disconnected:
            self.state.remove_connected_player(player_id)
```

---

### 3.11 `manager.py` — Fachada Orquestadora

**Propósito**: Mantiene interfaz pública, delega internamente.

```python
# network/manager.py (aprox. 100 líneas)
import logging

from .transport import Transport
from .server import GameServer
from .client import GameClient
from .discovery import Discovery
from .health import HealthMonitor
from .state import NetworkState
from .config import NetworkConfig

logger = logging.getLogger(__name__)

class NetworkManager:
    """Fachada orquestadora de la red (interfaz pública)."""
    
    def __init__(self):
        self.config = NetworkConfig()
        self.state = NetworkState()
        self.transport = Transport(self.config)
        self.server = GameServer(self.state, self.transport, self.config)
        self.client = GameClient(self.state, self.transport, self.config)
        self.discovery = Discovery(self.state, self.config)
        self.health = HealthMonitor(self.state, self.transport, self.config)
    
    # === Métodos públicos (INTERFAZ COMPATIBLE) ===
    
    def start_server(self, gameName, password, max_players, name_sala):
        """Inicia servidor."""
        success = self.server.start(gameName, gameName, max_players, name_sala)
        if success:
            self.state.password = password
            self.state.running_broadcast = True
            self.discovery.start_broadcast()
            self.health.start_health_check()
        return success
    
    def connectToServer(self, server):
        """Conecta a un servidor."""
        return self.client.connect(server)
    
    def sendData(self, data):
        """Envía datos al servidor."""
        return self.client.send(data)
    
    def discoverServers(self, timeout=5):
        """Descubre servidores en la red local."""
        return self.discovery.discover_servers(timeout)
    
    def broadcast_message(self, message):
        """Broadcast a todos los clientes (solo HOST)."""
        if not self.state.is_host:
            logger.warning("Solo el HOST puede hacer broadcast")
            return
        
        # Implementar envío a todos los jugadores
        disconnected = []
        for player in self.state.get_connected_players():
            if player.is_host:
                continue
            try:
                self.transport.send_atomic(player.conn, message)
            except Exception as e:
                logger.error(f"Error broadcast a {player.name}: {e}")
                disconnected.append(player.player_id)
        
        for pid in disconnected:
            self.state.remove_connected_player(pid)
    
    def stop(self):
        """Detiene servidor y cliente."""
        self.state.running = False
        self.state.running_broadcast = False
        
        # Cerrar sockets
        if self.server.server_socket:
            try:
                self.server.server_socket.close()
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
        return len(self.state.connected_players) >= 2
    
    def startGame(self):
        self.state.game_started = True
        msg = {"type": "START_GAME"}
        self.broadcast_message(msg)
        self.state.msgStartGame.update(msg)
    
    # Propiedades para compatibilidad
    @property
    def is_host(self):
        return self.state.is_host
    
    @property
    def is_connected(self):
        return self.state.is_connected
    
    @property
    def connected_players(self):
        return self.state.connected_players
    
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
    
    # ... más propiedades según necesidad
```

---

### 3.12 `__init__.py` — Punto de Entrada

**Propósito**: Exportar `NetworkManager` manteniendo compatibilidad.

```python
# network/__init__.py
from .manager import NetworkManager

__version__ = "2.0.0"
__all__ = ["NetworkManager"]
```

Con esto, todo el código existente sigue funcionando:
```python
from network import NetworkManager
```

---

## 4. LOGGING CENTRALIZADO

Reemplazar todos los `print()` con logging. En `main.py`:

```python
import logging

# Configuración global (una sola vez)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('game.log'),
        logging.StreamHandler()
    ]
)

# En desarrollo, para más detalle:
# logging.getLogger('network').setLevel(logging.DEBUG)
```

---

## 5. DIVISIÓN DE TRABAJO (8 PERSONAS)

| Persona | Módulo | Responsabilidad | Estimado | Dependencias |
|---------|--------|---|---|---|
| **Dev 1** | `constants.py` + `config.py` | Enums y configuración | 2-3h | Ninguna |
| **Dev 2** | `exceptions.py` + `types.py` | Excepciones y dataclasses | 2-3h | constants.py |
| **Dev 3** | `transport.py` | Protocolo atómico (crítico) | 4-5h | config.py, exceptions.py |
| **Dev 4** | `state.py` | Gestión de estado | 3-4h | types.py |
| **Dev 5** | `server.py` (Parte A) | Iniciación y aceptación | 4-6h | transport.py, state.py |
| **Dev 6** | `server.py` (Parte B) | Manejo de jugadores | 4-6h | dev 5 (revisar juntos) |
| **Dev 7** | `client.py` | Lógica cliente | 3-4h | transport.py, state.py |
| **Dev 8** | `discovery.py` + `health.py` + `manager.py` | Integración final | 4-5h | Todos los anteriores |

**Hitos**:
1. Dev 1-2 entregan en paralelo (2 días)
2. Dev 3-4 empiezan inmediatamente (día 2)
3. Dev 5-6 y Dev 7 en paralelo (día 3-4)
4. Dev 8 hace integración final y tests (día 5-6)

---

## 6. TESTING

Cada módulo debe incluir tests unitarios básicos. Template:

```python
# network/tests/test_transport.py
import pytest
from network.transport import Transport
from network.config import NetworkConfig

def test_send_atomic_small_message():
    """Test envío de mensaje pequeño."""
    config = NetworkConfig(MAX_MESSAGE_SIZE=1_000_000)
    transport = Transport(config)
    # Crear mock socket y verificar
    ...

def test_recv_exact_timeout():
    """Test retry en timeout."""
    ...

def test_message_size_limit():
    """Test rechazo de mensaje > MAX_MESSAGE_SIZE."""
    ...
```

Archivo `tests/conftest.py` para fixtures compartidas.

---

## 7. INTEGRACIÓN CON CÓDIGO EXISTENTE

**Cambios CERO en otros módulos**. Ejemplo:

```python
# main.py - SIN CAMBIOS
from network import NetworkManager

nm = NetworkManager()
nm.start_server("Sala", "pass", 7, "Mi Sala")
```

Internamente, `NetworkManager` delega a los nuevos módulos, pero el exterior no lo ve.

---

## 8. CHECKLIST DE REFACTORIZACIÓN

- [ ] Crear carpeta `network/` en raíz del proyecto
- [ ] Crear `__init__.py` vacío
- [ ] Implementar `constants.py` (Dev 1)
- [ ] Implementar `config.py` (Dev 1)
- [ ] Implementar `exceptions.py` (Dev 2)
- [ ] Implementar `types.py` (Dev 2)
- [ ] Implementar `transport.py` (Dev 3) - **PRUEBAS EXHAUSTIVAS**
- [ ] Implementar `state.py` (Dev 4)
- [ ] Implementar `server.py` (Dev 5-6)
- [ ] Implementar `client.py` (Dev 7)
- [ ] Implementar `discovery.py` (Dev 8)
- [ ] Implementar `health.py` (Dev 8)
- [ ] Implementar `manager.py` (Dev 8)
- [ ] Tests unitarios por módulo
- [ ] Test de integración completo
- [ ] Verificar `main.py` sin cambios
- [ ] Verificar `ui2.py` sin cambios
- [ ] Documentación de API (docstrings)
- [ ] Logging correcto en todos los módulos
- [ ] Remover `network.py` antiguo y mover a `network_old.py.bak`

---

## 9. NOTAS IMPORTANTES

1. **El archivo `network.py` antiguo NO se elimina hasta que todo esté testeado**. Solo se mueve a `network_old.py.bak` para referencia.

2. **Los primeros tests deben ser manuales**: ejecutar `main.py`, crear una sala, conectarse, enviar mensajes. Verificar que funciona idéntico al original.

3. **Logging debe ser el primer cambio**: No esperes a implementar módulos para añadir logging. Desde Dev 1 hay que usar `logging.getLogger(__name__)`.

4. **Para deshacer rápido**: Si algo falla, es fácil volver a `import network_old as network` y cambiar un `__init__.py`.

5. **Thread-safety es crítica**: Todos los accesos a `state.connected_players`, `state.game_state`, etc. deben usar los métodos sincronizados, no acceso directo.

6. **Los strings de mensaje deben ir a `constants.MessageType`**: Buscar y reemplazar todos los `"PING"`, `"BAJARSE"`, etc. con `MessageType.PING.value`.

---

## 10. REFERENCIAS RÁPIDAS PARA DESARROLLADORES

- **¿Cómo envío un mensaje atómico?**  
  ```python
  self.transport.send_atomic(socket, {"type": "PING", "data": ...})
  ```

- **¿Cómo accedo al estado compartido de forma segura?**  
  ```python
  self.state.update_game_state({"key": "value"})
  ```

- **¿Cómo registro un evento?**  
  ```python
  logger.info(f"Jugador {name} conectado")
  ```

- **¿Cómo creo una excepción de red?**  
  ```python
  raise TimeoutException("Socket timeout en recepción", player_id=123)
  ```

- **¿Cómo hago que mi código sea testeable?**  
  Inyectar dependencias en `__init__`, no hardcodear.

---

## CONCLUSIÓN

Esta refactorización:
- ✅ Cero cambios en interfaz pública
- ✅ Código organizado en 11 módulos pequeños
- ✅ Divisible entre 8 desarrolladores sin conflictos
- ✅ Logging profesional
- ✅ Thread-safe por diseño
- ✅ Fácil de testear
- ✅ Escalable y mantenible

**Tiempo total estimado**: 5-7 días de trabajo en paralelo.

---

**Documento creado por**: Ingeniero de Redes (especializado en arquitectura de sistemas multijugador)  
**Versión**: 1.0  
**Última actualización**: 2026-05-08
