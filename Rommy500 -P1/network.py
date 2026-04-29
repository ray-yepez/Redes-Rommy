import socket
import threading
import pickle
import time
import json
import struct

class NetworkManager:
    """clase para las conexiones de red local"""
    def __init__(self):
        self.server = None
        self.servers = []  # lista de servidores
        self.currentServer = None
        self.client = None
        self.connection = None
        self.is_connected = False
        self.receive_thread_running = False
        self.server_info_to_reconnect = None
        self.next_player_id = 2
        self.players_by_id = {}  # {player_id: {'conn':..., 'addr':..., 'name':..., 'spectator':..., 'active':...}}
        self.player_states = {}
        self.player_name_to_id = {}
        self.player_id = None
        self.last_activity = {}
        self.msgPong = {}
        self.host = " "
        self.port = 5555
        self.broadcast_port = 5554
        self.player = None
        self.max_players = None
        self.password = ""
        self.gameName = ""
        self.playerName = None
        self.is_host = False
        self.connected_players = []
        self.game_started = False
        self.running = False
        self.running_broadcast = False
        self.receivedData = None
        self.lock = threading.Lock()
        self.messagesServer = []
        self.msgPlayersCarSelection = None
        self.received_data = None
        self.msgStartGame = {}
        self.game_state = {}
        self.incoming_messages = []
        self.moves_game = []
        self.moves_gameServer = []
        self.exit_gameServer = []
        self.socet_lock = threading.Lock()

        # Nuevas variables para manejo de reconexión
        self.players_reconnect_data = {}  # {player_name: {'player_id':..., 'state':..., 'conn':...}}
    

    def _recv_exact(self, sock, n, max_retries=5):
        data = b''
        retries = 0
        while len(data) < n:
            try:
                chunk = sock.recv(n - len(data))
                if not chunk:
                    return None
                data += chunk
                retries = 0
            except socket.timeout:
                retries += 1
                if retries >= max_retries:
                    return None
        return data

    def send_atomic(self, sock, data):
        try:
            pickled = pickle.dumps(data)
            length = len(pickled)
            header = struct.pack('>I', length)
            sock.sendall(header)
            sock.sendall(pickled)
            return True
        except Exception:
            return False

    def recv_atomic(self, sock, timeout=None):
        original_timeout = sock.gettimeout()
        if timeout is not None:
            sock.settimeout(timeout)
        try:
            header = self._recv_exact(sock, 4)
            if header is None:
                return None
            length = struct.unpack('>I', header)[0]
            data = self._recv_exact(sock, length)
            if data is None:
                return None
            return pickle.loads(data)
        except:
             return None
        finally:
            if timeout is not None:
                sock.settimeout(original_timeout)
               
    def getLocalIP(self):
        """Obtiene la IP local de la computadora"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except (socket.error, OSError, ConnectionError):
            return "127.0.0.1" #Local IP
    def start_server(self, gameName, password, max_players, name_sala):
        self.host = self.getLocalIP()
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host, self.port))
            self.server.listen(max_players)
            self.gameName = gameName
            self.playerName = name_sala
            self.password = password
            self.max_players = max_players
            self.is_host = True
            self.running = True

            # Inicializar la lista de jugadores con el host (id=1)
            self.connected_players = [(self.server, (self.host, self.port), self.playerName, 1)]
            self.currentServer = {
                'name': self.gameName,
                'playerName': self.playerName,
                'ip': self.host,
                'port': self.port,
                'max_players': max_players,
                'password': self.password,
                'currentPlayers': len(self.connected_players)
            }
            print(f"Servidor iniciado en {self.host}:{self.port}")
            threading.Thread(target=self.acceptConnections, daemon=True).start()

            # Broadcast
            self.running_broadcast = True
            threading.Thread(target=self.broadcast_server, daemon=True).start()

            # Health check
            self.start_health_check(interval=60)

            return True
        except Exception as e:
            print(f"Error al iniciar servidor: {e}")
            return False

    def acceptConnections(self):
        while self.running:
            try:
                conn, addr = self.server.accept()
                print("Nueva conexión entrante... verificando clave...")

                received = self.recv_atomic(conn, timeout=30)
                if received is None:
                    print("No llegó la clave, cerrando conexión.")
                    conn.close()
                    continue

                client_password, client_name = received
                if client_password != self.currentServer['password']:
                    self.send_atomic(conn, "WRONG_PASSWORD")
                    conn.close()
                    continue

                # Verificar si hay espacio
                if len(self.connected_players) >= self.currentServer['max_players']:
                    self.send_atomic(conn, "FULL")
                    conn.close()
                    continue

                # Revisar si el jugador está en lista de reconexión
                existing_id = None
                existing_conn_info = None
                for pname, data in self.players_reconnect_data.items():
                    if pname == client_name:
                        existing_id = data['player_id']
                        existing_conn_info = data
                        break

                if existing_id:
                    # Reconexión exitosa
                    print(f"Reconexión del jugador {client_name} con ID {existing_id}")
                    # Cerrar conexión anterior
                    old_conn = self.players_by_id[existing_id]['conn']
                    try:
                        old_conn.close()
                    except:
                        pass
                    # Actualizar datos
                    self.players_by_id[existing_id]['conn'] = conn
                    self.players_by_id[existing_id]['active'] = True
                    # Restablecer estado si es necesario
                    if self.game_started:
                        self.players_by_id[existing_id]['spectator'] = True
                    # Enviar confirmación
                    response_data = {
                        "status": "CONNECTED",
                        "player_id": existing_id,
                        "player_name": client_name
                    }
                    self.send_atomic(conn, response_data)
                    # Actualizar lista de jugadores
                    for idx, p in enumerate(self.connected_players):
                        if p[3] == existing_id:
                            self.connected_players[idx] = (conn, addr, client_name, existing_id)
                            break
                else:
                    # Nuevo jugador
                    new_id = self.next_player_id
                    self.next_player_id += 1
                    self.players_by_id[new_id] = {'conn': conn, 'addr': addr, 'name': client_name, 'spectator': False, 'active': True}
                    self.player_name_to_id[client_name] = new_id
                    # Guardar en lista de reconexión por si vuelve a salir
                    self.players_reconnect_data[client_name] = {'player_id': new_id}

                    # Agregar a la lista de jugadores conectados
                    self.connected_players.append((conn, addr, client_name, new_id))
                    # Enviar confirmación
                    response_data = {
                        "status": "CONNECTED",
                        "player_id": new_id,
                        "player_name": client_name
                    }
                    self.send_atomic(conn, response_data)
                    print(f"Nuevo jugador {client_name} con ID {new_id}")

                # Iniciar hilo para manejar a este jugador
                threading.Thread(target=self.handlePlayer, args=(conn, addr, client_name, new_id), daemon=True).start()

            except Exception as e:
                print(f"Error en acceptConnections: {e}")

    def handlePlayer(self, conn, addr, namePlayer, player_id):
        try:
            while self.running:
                received_data = self.recv_atomic(conn, timeout=30)
                if received_data is None:
                    print(f"{namePlayer} desconectó o timeout.")
                    break
                with self.lock:
                    self.received_data = received_data
                
        finally:
            self.handle_disconnect(player_id, namePlayer)

    def handle_disconnect(self, player_id, name):
        with self.lock:
            if player_id in self.players_by_id:
                self.players_by_id[player_id]['active'] = False
                try:
                    self.players_by_id[player_id]['conn'].close()
                except:
                    pass
                # Mantener datos para reconexión
                if name not in self.players_reconnect_data:
                    self.players_reconnect_data[name] = {'player_id': player_id}
                print(f"{name} desconectado.")
                # Notificar a todos
                self.broadcast_message({
                    "type": "PLAYER_DISCONNECTED",
                    "id": player_id,
                    "name": name,
                    "msg": "Jugador desconectado"
                })
                # Actualizar lista de jugadores conectados
                self.connected_players = [p for p in self.connected_players if p[3] != player_id]
                self.currentServer['currentPlayers'] = len(self.connected_players)

    
    def stop(self):
        self.running = False
        self.receive_thread_running = False
        for p in self.connected_players:
            try:
                p[0].close()
            except:
                pass
        if self.server:
            try:
                self.server.close()
            except:
                pass
        if self.player:
            try:
                self.player.close()
            except:
                pass
    def canStartGame (self):
        """
        Verifica que haya minimo 2 jugadores
        """
        return len(self.connected_players)>=2

    def startGame(self):
        """Inicia el juego y notifica a todos"""
        self.game_started = True

        print(f"Iniciando el juego con {len(self.connected_players)} jugadores")

        # Notificar a todos los jugdores 
        msgStart = {"type": "START_GAME"}
        self.broadcast_message(msgStart)

    def send_selection_update(self, cartas_eleccion_serializada):
        """
        El Host usa este método para notificar a todos los clientes 
        la lista actualizada de cartas_eleccion.
        """
        if not self.is_host:
            print("ERROR: Solo el Host puede enviar actualizaciones de selección.")
            return

        # El mensaje contendrá la lista de cartas de elección actualizada
        message = {
            "type": "SELECTION_UPDATE",
            "cartas_eleccion": cartas_eleccion_serializada # Ya debe venir serializada (Pickle)
        }


        self.broadcast_message(message)
        print(f"Host: Enviando actualización de cartas de elección. Quedan {len(cartas_eleccion_serializada)} cartas.")

    def exit_game(self, playerId, playerName):
        msgSalir = {
            "type": "SALIR",
            "playerId": playerId,
            "playerName": playerName
            }
        if self.player:
            self.sendData(msgSalir)

    def get_game_info(self):
        """Obtiene información del juego"""
        return {
            "gameName": self.gameName,
            "host": self.host,
            "port": self.port,
            "max_players": self.max_players,
            "connected_players": self.connected_players,
            "is_host": self.is_host
        }

    def dprint(self, dic):
        """Para imprimir mas bonito un diccionario"""
        if isinstance(dic, dict):
            for clave, valor in dic.items():
                print(f"{str(clave).rjust(15)}: {valor}")
        else:
            return False
    def discoverServers(self, timeout=5):
        """Descubre servidores disponibles en la red local"""
        self.servers = []

        # Escuchar por servidores
        listenThread = threading.Thread(target=self.listenForServers, args=(timeout,), daemon=True)
        listenThread.start()

        print("asi va quedando la lista de servidores!", self.servers)
        return None
    def listenForServers(self, timeout=5):
        """Escucha anuncios de servidores en la red"""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('', self.broadcast_port))
            s.settimeout(1.0)

            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    data, _ = s.recvfrom(1024)
                    serverInfo = json.loads(data.decode('utf-8'))

                    # Actualizar si el servidor ya está en la lista
                    existing = next((s for s in self.servers if s['ip'] == serverInfo['ip']), None)
                    print(existing)
                    if existing:
                        existing.update(serverInfo)
                    else:
                        self.servers.append(serverInfo)
                        print(f"Después de anxear nuevo servidor {self.servers}")
                except socket.timeout:
                    print("Nadie me habló..... ")
                    continue
                except ImportError:
                    break
    def broadcast_server(self):
        """Envía broadcast anunciando el servidor"""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
         s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
         while self.running_broadcast and self.server:
            try:
                self.currentServer['currentPlayers'] = len(self.connected_players)
                tServer = self.currentServer.copy()
                if 'password' in tServer: del tServer['password']
                
                # Forzar que la IP enviada sea la correcta
                tServer['ip'] = self.host 
                
                data = json.dumps(tServer).encode('utf-8')
                s.sendto(data, ('<broadcast>', self.broadcast_port))
                time.sleep(3)
            except Exception as e:
                print(f"Error en broadcast: {e}")
                break
    def stop_broadcast(self):
        """Detiene solo el broadcast"""
        self.running_broadcast = False

    def broadcast_message(self, message):
        """Envía un mensaje a todos los clientes conectados excepto al remitente"""
        if not self.connected_players:
            print(" No hay jugadores conectados ")
            return

        disconnectedPlayer = []
        message1 = None  # Initialize to avoid undefined variable error
        try:
            # Bloqueando el lock antes de acceder a connected_players
            with self.lock:
                # No enviar al jugador remitente
                if isinstance(message, tuple):
                    connSend = message[1]
                    message1 = message[0]
                    self.messagesServer.append(message1)
                    # Agregando mensaje del jugador a Lista de mensaje del servidor... {self.messagesServer}
                else:
                    message1 = message
                    connSend = None
                # Iterando sobre (conn, addr, player_name, player_id)
                for conn, addr, player_name , player_id in self.connected_players:      # Nuevo...
                    # No enviar al servidor   El servidor tambien es jugador
                    if conn == self.server:
                        continue
                  
                    if conn!=connSend:
                        try:
                            ##conn.send(pickle.dumps(message1))
                            if message1 is not None and self.send_atomic(conn, message1):
                                print(f"Mensaje transmitido a {player_name}")  # Nuevo...
                                if message1 is not None and isinstance(message1, dict):
                                    print(f"TIPO: {message1.get('type')}")
                                elif message1 is not None and isinstance(message1, str):
                                    print("TIPO: CHAT")
                            else:
                                print(f"Error enviando mensaje a {player_name}: send_atomic falló")
                                disconnectedPlayer.append((conn, addr, player_name, player_id))
                        except (socket.error, ConnectionResetError, BrokenPipeError) as e:
                            print(f"Error enviando mensaje a {player_name}: {e}")
                            disconnectedPlayer.append((conn, addr, player_name, player_id)) # Nuevo...

                # Si hay un error con un cliente, cerrar su conexión
                #Remover jugadores desconectados
                if disconnectedPlayer:
                    disconnected_ids = [player[3] for player in disconnectedPlayer]
                    for player in disconnectedPlayer:
                        print(f"Jugador desconectado.... POR MENSAJERIA: {player[2]}")
                    self.connected_players = [p for p in self.connected_players if p[3] not in disconnected_ids]
                    self.currentServer['currentPlayers'] = len(self.connected_players)
        except (socket.error, OSError) as e:
            print(f"Error en broadcast: {e}")
    def start_health_check(self, interval = 60):
        """ Inicia la verificacion periodica de conexiones"""
        def health_check_loop():
            while self.running:
                time.sleep(interval)
                if len(self.connected_players) > 1: # un jugador ademas del host
                    print(" Ejecutando el Health check...")
                    self.check_connection_health()
        # Creamos un hilo para no detener el hilo principal
        health_thread = threading.Thread(target=health_check_loop,daemon=True)
        health_thread.start()
        print(f"Health check iniciado cada {interval} segundos")

    def check_connection_health(self):
        """Verifica que las conecciones esten activas"""
        if not self.running:
            return

        disconnected = []

        for conn, addr, player_name, player_id in self.connected_players:
            # No hacer el PING al host :D
            if conn == self.server:
                continue
            try:
                # Intentando enviar un ping
                conn.settimeout(5.0)
                msg_PING = {"type": "PING",
                            "timestamp": time.time(),
                            "msg": "¿Estas vivo? :) "}
                ##conn.send(pickle.dumps(msg_PING))
                if not self.send_atomic(conn, msg_PING):
                    raise Exception("No se pudo enviar PING atómico")
                print(f" Enviando PING a {player_name}")

                # Intentando recibir el PONG
                start_time = time.time()
                pong_received = False
                while time.time() - start_time < 5.0:
                    try:
                        data = self.last_activity
                        if data:
                            if time.time() - self.last_activity.get(player_id,0)< 30:
                                print(f" El jugador {player_name} respondio el PONG")
                                pong_received = True
                                break
                    except socket.timeout:
                        continue # Continua esperando en el tiempo limite
                    except BlockingIOError:
                        continue # No hay datos disponibles aun... :'( 
                if not pong_received:
                    # Timeout - Eljugador no resondio el PONG
                    raise Exception("El jugador no respondio PONG en el tiempo limite :'( No esta vivo ")
            except (socket.error, socket.timeout, ConnectionResetError) as e:
                print(f" El jugador {player_name} no respondio el PING: {e}")
                disconnected.append((conn, addr,player_name,player_id))
        
        # Eliminar desconectados
        if disconnected:
            disconnected_ids = [player[3] for player in disconnected]
            self.connected_players = [p for p in self.connected_players if p[3] not in disconnected_ids]
            for player in disconnected:
                print(f" El jugador {player[2]} fue eliminado por falta de respueta del PING")

            self.currentServer['currentPlayers'] = len(self.connected_players)
            print(f" Jugadores restantes {self.currentServer['currentPlayers']}")

    def connectToServer(self, server):
        """Conecta al servidor especificado"""
        try:
            self.player = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.player.connect((server['ip'], server['port']))
            print("Socket creado...")

            # Enviar contraseña
            ##self.player.send(pickle.dumps((server['password'],server['playerName'])))
            if not self.send_atomic(self.player, (server['password'], server['playerName'])):
                return False, "Error enviando credenciales"
            print("clave enviada...")

            # Recibir respuesta
            ##response = pickle.loads(self.player.recv(2048))
            response = self.recv_atomic(self.player, timeout=30)
            print(f" Respuesta recibida... {response}")
            if isinstance(response, dict) and response.get("status") == "CONNECTED":
                player_name = response["player_name"]   # Nuevo...
                player_id = response["player_id"]       # Nuevo...
                self.player_id = player_id              # Nuevo...
                self.host = server['ip']
                self.is_host = False
                self.running = True
                self.is_connected = True                # Nuevo... Jugador Conectado
                self.receive_thread_running = True      # Nuevo... Hilo iniciado
                self.server_info_to_reconnect = server.copy()  # Nuevo... Guardar para la reconexión

                # Hilo para que el jugador reciba datos
                receiveThread = threading.Thread(target=self.receiveData, daemon=True)
                receiveThread.start()
                print("Hilo para recepción de datos iniciado")
                print(f" Juagador conectado como {player_name} con (ID: {player_id})")  # Nuevo...
                return True, "Conectado exitosamente"
            elif response == "WRONG_PASSWORD":
                return False, "Contraseña incorrecta"
            elif response == "FULL":
                return False, "El servidor está lleno"
            else:
                return False, "Error desconocido al conectar"

        except (socket.error, ConnectionRefusedError, socket.timeout) as e:
            return False, f"Error conectando al servidor: {e}"

    def receiveData(self):
        """Recibe datos del servidor"""
        while self.running and self.player:
            try:
                # Timeout para detectar desconexiones
                #self.player.settimeout(5.0)
                ##data = self.player.recv(8192) #2048->4096
                received_data = self.recv_atomic(self.player, timeout=30)

                ##if not data:
                if received_data is None:
                    print("Conexion cerrada por el servidor")
                    break # Dejar de intentar leer la data

                ##received_data = pickle.loads(data)

                # Manejo del mensaje PING
                if isinstance(received_data, dict) and received_data.get("type")=="PING":
                    print(" Recibido el PING, enviando el PONG al servidor")
                    msg_PONG = {"type": "PONG",
                                "timestamp":received_data.get("timestamp"),
                                "response_to": received_data.get("msg","PING")}
                    # Envio del msg PONG
                    self.sendData(msg_PONG)
                    continue # No procesar mas este mensaje
                # Restaurar timeout para operar normal
                #self.player.settimeout(None)

                with self.lock:
                    self.receivedData = received_data
                    #print(f"Datos recibidos y almacenados en self.receivedData... :: {self.receivedData}")

                    if isinstance(received_data, dict) and received_data.get("type")=="START_GAME":
                        self.msgStartGame.update(received_data)
                        print(" Inicio del juego recibido: msg START_GAME")

                    # Si es un mensaje de ESTADO (como el que contiene cartas_disponibles, elecciones, etc.) en ui2
                    elif isinstance(received_data, dict) and received_data.get("type") in ["ELECTION_CARDS","SELECTION_UPDATE", "ESTADO_CARTAS", "ORDEN_COMPLETO"]:
                        self.game_state.update(received_data)
                        print(f"Estado del juego actualizado: {self.game_state}")

                    # Si es un mensaje entrante de CHAT o NOTIFICACIÓN simple
                    elif isinstance(received_data, str):
                        self.incoming_messages.append(("chat", received_data)) 
                        print(f"Mensaje de chat/notificación recibido: {received_data}")

                    elif isinstance(received_data, dict) and received_data.get("type") in ["BAJARSE","TOMAR_DESCARTE", "TOMAR_CARTA", "DESCARTE", "COMPRAR_CARTA", "PASAR_DESCARTE", "INICIAR_COMPRA","INSERTAR_CARTA","PASAR_COMPRA","REALIZAR_COMPRA","SWAP_JOKER","SALIR","DESCONEXION"]:
                        self.moves_game.append(received_data)
                        print(f" Jugada del jugador recibida:{received_data.get('type')}")

                    # Si es otro tipo de estructura/mensaje no clasificado
                    else:
                        self.incoming_messages.append(("raw", received_data)) # Opcional: para mensajes no clasificados
                        #print(f"Mensaje guardado en incoming_messages... raw {self.incoming_messages}")

            except socket.timeout:
                # Timeout normal, continua el bucle
                continue
            except ConnectionResetError:
                print("Conexión reseteada por el servidor")
                #self.handle_disconnection()
                break        
            except(socket.error, socket.timeout) as e:
                print(f"Error recibiendo datos: {e}")
                if "broken pipe" in str(e).lower() or "connection reset" in str(e).lower():
                    #self.handle_disconnection()
                    break
                continue
            finally:
                # Asegurando reestablecer el timeout
                try:
                    self.player.settimeout(None)
                except (OSError, socket.error):
                    pass

        print("Hilo de recepción terminado. ")
        self.receive_thread_running = False
        # Si se detuvo por desconexión (y no porque utilizamos a self.stop())
        if self.is_connected:
            self.is_connected = False # Desconectado. Avisar al bucle principal.

    def sendData(self, data):
        """Envía datos al servidor"""
        if self.player and self.running:
            try:
                ##self.player.send(pickle.dumps(data))
                success = self.send_atomic(self.player, data)
                print(f"Datos enviados al servidor: TIPO: {data.get('type')}")
                return success
            except (socket.error, ConnectionResetError, BrokenPipeError) as e:
                print(f"Error enviando datos.....: {e}")
                return False

        return False

    def get_msgStartGame(self):
        """Devuelve y borra la lista de mensajes entrantes de forma segura."""
    
        with self.lock:
            if self.msgStartGame:
                return "launch_ui2"

    def get_incoming_messages(self):
        """Devuelve y borra la lista de mensajes entrantes de forma segura."""
        #accede a variables compartidas
        with self.lock: 
            # 1. Crear una copia de los mensajes recibidos
            messages = list(self.incoming_messages).copy()
            # 2. Limpiar la cola de mensajes
            self.incoming_messages.clear()
    
            return messages

    def get_game_state(self):
        """Devuelve y borra la lista de mensajes de estado del juego de forma segura."""
        # self.lock es un threading.Lock que debe usarse para acceder a variables compartidas
        with self.lock:
            # 1. Crear una copia de los mensajes recibidos
            messages = (self.game_state).copy()
            # 2. Limpiar la cola de mensajes
            self.game_state.clear()
            # 3. Devolver los mensajes
            return messages

    def get_moves_game(self):
        """Devuelve y borra la lista de mensajes de jugadas del juego de forma segura."""
        # self.lock es un threading.Lock que debe usarse para acceder a variables compartidas
        with self.lock: 
            # 1. Crear una copia de los mensajes recibidos
            messages = self.moves_game.copy()
            # 2. Limpiar la cola de mensajes
            self.moves_game.clear()
            # 3. Devolver los mensajes
            return messages

    def get_moves_gameServer(self):
        """Devuelve y borra la lista de mensajes de jugadas del juego de forma segura."""
        # self.lock es un threading.Lock que debe usarse para acceder a variables compartidas
        with self.lock:
            # 1. Crear una copia de los mensajes recibidos
            messages = self.moves_gameServer.copy()
            # 2. Limpiar la cola de mensajes
            self.moves_gameServer.clear()
            # 3. Devolver los mensajes
            return messages

    def get_exit_gameServer(self):
        """Devuelve y borra la lista de mensajes de salir/desconexion del juego de forma segura."""
        with self.lock: 
            # 1. Crear una copia de los mensajes recibidos
            messages = self.exit_gameServer.copy()
            # 2. Limpiar la cola de mensajes
            self.exit_gameServer.clear()
            # 3. Devolver los mensajes
            return messages
