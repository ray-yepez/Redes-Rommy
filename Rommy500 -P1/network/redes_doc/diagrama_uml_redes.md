# Diagrama UML del Módulo de Redes (Rummy 500)

Este diagrama representa la arquitectura refactorizada del sistema de redes, siguiendo el patrón **Facade** y asegurando la seguridad entre hilos (**Thread-Safety**).

# si no logras visualizar el siguiente diagrama, ver UML_redes_refactor.png adjunto

```mermaid
classDiagram
    class NetworkManager {
        +NetworkConfig config
        +NetworkState state
        +Transport transport
        +GameServer server
        +GameClient client
        +Discovery discovery
        +HealthMonitor health
        +start_server(nameHost, password, max_players, nameSala) bool
        +connectToServer(server_info) tuple
        +sendData(data) bool
        +discoverServers(timeout)
        +broadcast_message(message)
        +startGame()
        +stop()
    }

    class NetworkState {
        -Lock _lock_players
        -Lock _lock_game
        -Queue incoming_messages
        -Queue moves_game
        -Queue moves_gameServer
        +dict game_state
        +list connected_players
        +bool is_connected
        +bool is_host
        +bool game_started
        +add_incoming_message(msg_type, data)
        +get_incoming_messages() list
        +add_move(move, server)
        +get_moves(server) list
        +update_game_state(state_dict)
        +add_connected_player(player)
        +remove_connected_player(player_id)
    }

    class GameServer {
        -NetworkState state
        -Transport transport
        -NetworkConfig config
        +socket server_socket
        +int next_player_id
        +start(game_name, player_name, max_players, room_name) bool
        -_accept_loop()
        -_handle_player(player)
        -_process_message(player, data)
        -_broadcast_players()
    }

    class GameClient {
        -NetworkState state
        -Transport transport
        -NetworkConfig config
        +connect(server_info) tuple
        -_receive_loop()
        -_process_message(data)
        +send(data) bool
    }

    class Transport {
        +NetworkConfig config
        +send_atomic(sock, data) bool
        +recv_atomic(sock, timeout) Any
        -_recv_exact(sock, n) bytes
    }

    class Discovery {
        -NetworkState state
        -NetworkConfig config
        +list discovered_servers
        +start_broadcast()
        +discover_servers(timeout)
    }

    class HealthMonitor {
        -NetworkState state
        -Transport transport
        +start_health_check()
        -_check_players()
    }

    class ConnectedPlayer {
        <<dataclass>>
        +socket conn
        +tuple addr
        +str name
        +int player_id
        +bool is_host
        +float last_activity
    }

    class ServerInfo {
        <<dataclass>>
        +str name
        +str player_name
        +str ip
        +int port
        +int max_players
        +int current_players
        +str password
    }

    NetworkManager *-- NetworkState : posee
    NetworkManager *-- Transport : posee
    NetworkManager *-- GameServer : posee
    NetworkManager *-- GameClient : posee
    NetworkManager *-- Discovery : posee
    NetworkManager *-- HealthMonitor : posee

    GameServer ..> ConnectedPlayer : gestiona
    NetworkState "1" o-- "*" ConnectedPlayer : almacena
    GameServer --> Transport : usa
    GameClient --> Transport : usa
    HealthMonitor --> Transport : usa
    Discovery ..> ServerInfo : descubre
```

## Descripción de Componentes Clave

### 1. NetworkManager (Fachada)
Es el punto de entrada único para la interfaz de usuario (`ui.py`). Orquesta todos los sub-servicios y oculta la complejidad interna de sockets e hilos.

### 2. NetworkState (Estado Compartido)
Actúa como la "Fuente de la Verdad" del módulo. Utiliza **Locks** y **Queues** de Python para garantizar que múltiples hilos (recepción, envío, broadcast) no corrompan los datos.

### 3. Transport (Capa de Comunicación)
Encargada de la serialización con `pickle` y de asegurar que los mensajes lleguen completos mediante un encabezado de longitud (4 bytes). Previene el problema de "mensajes cortados" en TCP.

### 4. GameServer & GameClient
Contienen la lógica específica de cada rol. El servidor gestiona múltiples clientes en hilos separados, mientras que el cliente mantiene un único hilo de escucha constante.

### 5. Discovery & HealthMonitor
- **Discovery**: Usa UDP Broadcast para que los jugadores encuentren partidas en la misma red local sin saber la IP.
- **HealthMonitor**: Implementa un sistema de *Heartbeat* (Latido) para detectar y desconectar jugadores que pierden la conexión de forma abrupta.