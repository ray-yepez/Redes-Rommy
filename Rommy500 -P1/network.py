import socket
import threading
import pickle
import time
import json
import struct
import queue
import threading

class NetworkManager:
    def __init__(self):
        self.server = None
        self.servers = []  #lista de servidores
        self.currentServer = None # Información del servidor  CREADOR
        self.client = None
        self.connection = None
        self.is_connected = False            # Nuevo... Estado de conexion para los jugadores
        self.receive_thread_running = False  # Nuevo... Para el estado de los hilos de los jugadores 
        self.server_info_to_reconnect = None # Nuevo... Para guardar los datos del servidor
        self.next_player_id = 2              # Nuevo... Contador simple para asignar IDs
        self.players_by_id = {}              # Nuevo... {player_id: (conn,addr,player_name, ????)}
        self.player_name_to_id = {}          # Nuevo... Para evitar duplicados 
        self.player_id = None                # Nuevo... 
        self.last_activity = {}              # Nuevo... Para el Check Health {player_id: timestamp}
        self.msgPong = {}                    # Nuevo... Mensaje de Ping pong
        self.host = " "
        self.port = 5555                     # Puerto TCP principal para las conexiones de juego
        self.broadcast_port = 5554           # Puerto UDP dedicado para Discovery
        self.player = None
        self.max_players = None
        self.password = ""
        self.gameName = ""
        self.playerName = None 
        self.is_host = False
        self.connected_players = []   #Lista de jugadores
        #self.ready_players = []       #Lista de jugadores listos para iniciar partida
        #self.ready_state = {}       # {'ID_jugador': False, ...}
        #self.game_started = False
        self.running = False
        self.running_broadcast = False
        self.receivedData = None
        self.lock = threading.Lock()
        self.messagesServer = [] #Mensajes del servidor
        self.msgPlayersCarSelection = None
        self.received_data = None # Robando la info de los jugadores ara uso del Host    NUEVO
        #+++++++++++++++++++++++++++
        # Nuevas variables de estado para el juego (cliente)
        self.msgStartGame = {}      # Para iniciar la partida de los jugadores
        self.game_state = {}        # Para el estado persistente del juego
        self.incoming_messages = [] # Para mensajes transitorios (chat, notificaciones)
        self.moves_game = []        # Jugadas del jugador
        self.moves_gameServer = []  # Jugadas de los jugadores usadas para el Host 
        #self.exit_gameServer = []   # Para salir o desconexion de jugadores + Host
        # Diccionario auxiliar para la sincronización (ya asociado por ID)
        #self.ready_state = {} 
        self.game_started = False
        #self.player_ids = {}
        self.socet_lock = threading.Lock() # Lock para operaciones de socket (evita intercalación)
        # NUEVO: INICIALIZACIÓN DE COLA Y HILO DE SALIDA
        self.cola_mensajes_salida = queue.Queue()
        threading.Thread(target=self._procesar_cola_salida, daemon=True).start()
    
    def _procesar_cola_salida(self):
        """ Hilo dedicado a extraer mensajes de la cola y enviarlos por el socket de forma segura. """
        while True:
            mensaje, conn_destino = self.cola_mensajes_salida.get()
            try:
                # Bloqueamos solo al momento de enviar para evitar corrupción de bytes
                with self.socet_lock:
                    self.send_atomic(conn_destino, mensaje)
            except Exception as e:
                print(f"Error enviando mensaje desde la cola: {e}")
            self.cola_mensajes_salida.task_done()
            
    def _recv_exact(self, sock, n, max_retries=5):
        """ Recibe exactamente n bytes del socket """
        data = b''      # Transforma a bytes
        retries = 0     # Contador de timeouts
        print(f"\n               Longitud del mensaje _recv_exact n: {n}\n")

        while len(data) < n:
            try:
                chunk = sock.recv(n - len(data))    # Segmento de información
                if not chunk:
                    # Conexión cerrada
                    return None
                data += chunk
                retries = 0 # Reinicia el contador si recibimos datos con éxito
                
            except socket.timeout:
                # Timeout, continuar intentando
                retries += 1
                print(f"Timeout alcanzado ({retries}/{max_retries})...")
            
                if retries >= max_retries:
                    print("Límite de reintentos alcanzado. Abortando recepción de datos.")
                    return None
                continue
            except Exception as e:
                print(f"Error en _recv_exact: {e}")
                return None
        return data
                
    def send_atomic(self, sock, data):
        """ Envía datos como un solo bloque atómico. """
        try:
            pickled = pickle.dumps(data)
            length = len(pickled)
            header = struct.pack('>I', length)
            
            # SOLUCIÓN: Agregamos el lock aquí
            with self.socet_lock:
                sock.sendall(header)
                sock.sendall(pickled)

            print(f"\n               Longitud del mensaje send_atomic length: {length}\n")
            return True
        except Exception as e:
            print(f"Error en send_atomic: {e}")
            return False
    
    def recv_atomic(self, sock, timeout=None):
        """ Recibe un mensaje completo en formato atómico """
        original_timeout = sock.gettimeout() # timeout actual para no perder la configuracion original
        
        if timeout is not None:
            # Aplicar timeout especifico temporalmente
            sock.settimeout(timeout)
        
        try:
            # Recibiiendo los 4 bytes de longitud
            header = self._recv_exact(sock, 4)
            if header is None:
                return None
            length = struct.unpack('>I', header)[0] # 1er valor de la tupla, la longitud
            
            # Recibiendo exactamente 'length' bytes
            data = self._recv_exact(sock, length)
            if data is None:
                return None
            
            print(f"\n               Longitud del mensaje recv_atomic length: {length}\n")
            
            # Deserializando y enviando data
            return pickle.loads(data)
        except socket.timeout:
            print("Timeout en recv_atomic")
            return None
        except Exception as e:
            print(f"Error en recv_atomic: {e}")
            return None
        finally:
            # Devolvemos configuracion original del timeout
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
        except:
            return "127.0.0.1" #Local IP
        

    def start_server(self, gameName, password, max_players,name_sala):
        self.host = self.getLocalIP() #Obteniendo IP del Creador (SERVIDOR)
        """Inicia el servidor del juego"""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # NUEVO: Activar Keep-Alive en el servidor
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.server.bind((self.host, self.port))
            self.server.listen(max_players)
            
            self.gameName = name_sala
            self.playerName = gameName   
            host_id = 1
            self.password = password
            self.max_players = max_players
            self.is_host = True
            self.running = True
            self.connected_players.append((self.server,(self.host, self.port),self.playerName, host_id)) #Nuevo...
            print(f"Servidor iniciado en el puerto {self.port}")
            
            self.currentServer = {
                'name': self.gameName,
                'playerName': self.playerName,
                'ip': self.host,
                'port': self.port,
                'max_players': max_players,
                'password': self.password,
                'currentPlayers': len(self.connected_players)        
                }
            print(f" currentServer.... ")
            self.dprint(self.currentServer)
            # Hilo para aceptar conexiones
            threading.Thread(target=self.acceptConnections, daemon=True).start()

            # Iniciar hilo para broadcast
            self.running_broadcast = True
            self.broadcast_thread = threading.Thread(target=self.broadcast_server, daemon=True)
            self.broadcast_thread.start()
            print(F"HILO PARA EL BROASDCAST... ")

            # Inicio de health check con su respectivo hilo
            self.start_health_check(interval = 60)

            return True
        except Exception as e:
            print(f"Error al iniciar el servidor: {e}")
            return False

    def acceptConnections(self):
        """Acepta conexiones entrantes y verifica la contraseña"""
        while self.running:
            try:
                conn, addr = self.server.accept()
                print(f"Se conecto... estamos viendo la clave...")
                
                # Recibir la contraseña del cliente
                ##data = conn.recv(2048)
                received = self.recv_atomic(conn, timeout=30)  
                ##if not data:
                if received is None:
                    print("No llego la Clave...Cerrando esa conexion")
                    conn.close()
                    continue
                    
                client_password, client_name = received ##pickle.loads(data)

                # Verificar contraseña
                if client_password == self.currentServer['password']:  #self.password:
                    
                    if len(self.connected_players) <= self.currentServer['max_players']:
                        if len(self.connected_players) <= self.currentServer['max_players']:
                            # Nuevo...
                            # Verificando si es reconexion o jugador nuevo
                            player_id = None
                            found_index = -1    # Para guardar indice encontrado
                            is_reconnection = False
                            if len(self.connected_players) >= 2:
                                for i, (existing_conn, existing_addr, existing_name, existing_id) in enumerate(self.connected_players[1:],start=2):
                                    if existing_name == client_name:
                                        player_id = existing_id
                                        found_index = i     # Indice encontrado
                                        is_reconnection = True
                                        break

                            if is_reconnection:
                                # RECONEXION! Actulizar conexion
                                print(f" Reconexion del jugador {client_name} (ID: {player_id})") 
                                # Cerrar conexion anterior
                                old_conn, old_addr, old_name, old_id = self.connected_players[found_index]
                                try:
                                    old_conn.close()
                                except:
                                    pass

                                # Actualiza con nueva conexion
                                self.connected_players[found_index] = (conn, addr, client_name, player_id)
                                self.enviar_game_state_sync(conn, player_id) #logica de reconexion actualizada
                            else:
                                # Nuevo jugador
                                player_id = self.next_player_id
                                self.next_player_id += 1
                                self.connected_players.append((conn, addr, client_name, player_id))
                                print(f" Nuevo jugador: {client_name} (ID: {player_id})")

                            # Acualizando la cantidad de jugadores
                            self.currentServer['currentPlayers'] = len(self.connected_players)

                            # Enviar confirmacion con id al jugador
                            response_data = {
                                "status": "CONNECTED",
                                "player_id": player_id,
                                "player_name": client_name
                            }
                            ## conn.send(pickle.dumps(response_data))
                            if not self.send_atomic(conn, response_data):
                                print("Error enviando respuesta de conexión")
                                conn.close()
                                continue
                            print(f" Enviando ID:{player_id} al jugador {client_name}")
                    
                        # Hilo para manejar al jugador
                        threading.Thread(
                            target=self.handlePlayer,
                            args=(conn, addr, client_name, player_id),
                            daemon=True
                        ).start()
                        
                    else:
                        # Servidor lleno
                        ##conn.send(pickle.dumps("FULL"))
                        self.send_atomic(conn, "FULL")
                        conn.close()
                else:
                    # Contraseña incorrecta
                    ##conn.send(pickle.dumps("WRONG_PASSWORD"))
                    self.send_atomic(conn, "WRONG_PASSWORD")
                    conn.close()
                    
            except Exception as e:
                if "10038" in str(e): 
                    print("Cierre de servidor detectado. Terminando hilo de aceptación.")
                    break

                print(f"Error aceptando conexión: {e}")
                if self.running:
                    continue
                else:
                    break


    def handlePlayer(self, conn, addr, namePlayer, player_id):
        """Maneja la comunicación con un cliente conectado"""
        player_name = f"{namePlayer}" #Para identificar al juador por el nombre
        try:
            while self.running:
                try:
                    ##data = conn.recv(8192)
                    received_data = self.recv_atomic(conn, timeout=30)
                              
                    ##if not data:
                    if received_data is None:
                        print(f"Jugador {namePlayer} (ID: {player_id}) cerró conexión normalmente.")
                        break

                    with self.lock:
                        ##received_data = pickle.loads(data)
                        self.received_data = received_data  # Informacion del juego para el Host

                    #Procesar mensajes del lobby/Chat
                    if isinstance(received_data, tuple) and received_data[0]=="chat_messages":
                        message_content = received_data[1]
                        formattedMsg = f"{player_name}: {message_content}"
                        print(f"Transmitiendo mensaje: {formattedMsg}")
                        # Enviar el mensaje a todos los clientes conectados
                        self.broadcast_message((formattedMsg, conn))
                        
                    # mensajes que no son del chat...
                    else:
                        # Mensajes del juego de jugadores para los jugadores
                        if isinstance(received_data,dict) and received_data.get("type") == "PONG":
                            with self.lock:
                                self.last_activity[player_id] = time.time()
                            print(f" Respuesta al PING..., PONG: Sigo vivo :) ")
                            print(f" [Health] Actividad registrada para {player_name} (ID: {player_id})")
                            print(f"Tamaño del last_activity {len(self.last_activity)}")
                            continue # No procesar este mensaje como mensaje de juego
                            
                        elif isinstance(received_data, dict) and received_data.get("type") != "PONG": 
                            print(f"Transmitiendo mensaje de los jugadores---> TIPO:{received_data.get("type")}")
                            # Enviar el mensaje a todos los clientes conectados
                            self.broadcast_message((received_data, conn))
                        #pass
                except ConnectionResetError:
                    print(f"Conexión reseteada por el jugador: {namePlayer}")
                    break # Evita seguir intentando recibir datos de una conexion cerrada       # Nuevo... 
                except socket.timeout:
                    # El timeout es normal si el jugador no ha movido nada.
                    # Simplemente volvemos al inicio del while para seguir escuchando.
                    continue
                except Exception as e:
                    print(f"Error manejando jugador {player_name}: {e}")   # Se cambió addr por player_name
                    time.sleep(0.5) 
                    continue # Intenta continuar, recibir el siguiente dato
                        
        finally:
            conn.close()
            with self.lock:
                # Remover por ID del jugador
                self.connected_players = [p for p in self.connected_players if p[3] != player_id] # Nuevo...
                self.currentServer['currentPlayers'] = len(self.connected_players)   
            print(f"Conexión cerrada con {addr}, Cantidad de JUGADORES:{len(self.connected_players)}")

    def discoverServers(self, timeout=5):  
        """Descubre servidores disponibles en la red local"""
        self.servers = []
        
        # Escuchar por servidores
        listenThread = threading.Thread(target=self.listenForServers, args=(timeout,), daemon=True)
        listenThread.start()
        
        print(f"asi va quedando la lista de servidores!",self.servers)
        return None 
    
    
    def listenForServers(self, timeout=5):
        """Escucha anuncios de servidores en la red"""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', self.broadcast_port))
            s.settimeout(1)
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    data, addr = s.recvfrom(1024)
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
                    print(f"Nadie me habló..... ")
                    continue
                except:
                    break

    def broadcast_server(self):
        """Envía broadcast anunciando el servidor"""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            print(f"self.running_broadcast {self.running_broadcast}")
            print(f"self.server::  {self.server}")
                
            while self.running_broadcast and self.server:
                try:
                    # Actualizar datos del servidor para transmitir
                    # Actualizar número de jugadores
                    self.currentServer['currentPlayers'] = len(self.connected_players)  
                    tServer = self.currentServer.copy()
                    del tServer['password']
                    # Enviar datos del servidor
                    data = json.dumps(tServer).encode('utf-8')
                    s.sendto(data, ('<broadcast>', self.broadcast_port))
                    print(f"Datos Tansmitiendose ", data )
                    time.sleep(3)  #3 segundos
                except:
                    print("No se pudo hacer la transmisión...")
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
                           # NUEVO: Enviamos el mensaje a la cola para que el hilo lo despache
                            self.cola_mensajes_salida.put((message1, conn))
                            
                            print(f"Mensaje en cola para {player_name}")  
                            if type(message1)==dict:
                                print(f"TIPO: {message1.get("type")}")
                            elif type(message1)==str:
                                print(f"TIPO: CHAT")
                        except Exception as e:
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
        except Exception as e:
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
                msg_PING = {"type": "PING",
                            "timestamp": time.time(),
                            "msg": "¿Estas vivo? :) "}
                
                # NUEVO: Mandamos el latido a la cola
                self.cola_mensajes_salida.put((msg_PING, conn))
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
                    raise Exception( "El jugador no respondio PONG en el tiempo limite :'( No esta vivo ")
            except Exception as e:
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
            # NUEVO: Activar Keep-Alive en el cliente
            self.player.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
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
                
        except Exception as e:
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
                        print(f" Inicio del juego recibido: msg START_GAME")
                    
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
                        print(f" Jugada del jugador recibida:{received_data.get("type")}")

                    # Si es otro tipo de estructura/mensaje no clasificado
                    else:
                        self.incoming_messages.append(("raw", received_data)) # Opcional: para mensajes no clasificados
                        #print(f"Mensaje guardado en incoming_messages... raw {self.incoming_messages}")
            
            except socket.timeout:
                # Timeout normal, continua el bucle
                continue
            except (ConnectionResetError, BrokenPipeError):
                print("Conexión perdida. Iniciando protocolo de recuperación...")
                self.reconnect_client()
                break        
            except Exception as e:
                print(f"Error recibiendo datos: {e}")
                # Captura errores de socket comunes en Windows/Linux
                if "10054" in str(e) or "Broken pipe" in str(e):
                    self.reconnect_client()
                    break
                continue
            finally:
                # Asegurando reestablecer el timeout
                try:
                    self.player.settimeout(None)
                except:
                    pass 
            
        print("Hilo de recepción terminado. ")
        self.receive_thread_running = False 
        # Si se detuvo por desconexión (y no porque utilizamos a self.stop())
        if self.is_connected:
            self.is_connected = False # Desconectado. Avisar al bucle principal.
    
    def reconnect_client(self):
        """ Bucle que intenta volver al servidor sin cerrar el juego """
        self.is_connected = False
        print("Iniciando reconexión automática...")

        while self.running and not self.is_connected:
            time.sleep(3.0) # Espera para no saturar el procesador
            print("Intentando reconectar al Host...")
            try:
                if self.server_info_to_reconnect:
                    exito, msj = self.connectToServer(self.server_info_to_reconnect)
                    if exito:
                        print("¡Reconexión exitosa!")
                        return 
            except Exception as e:
                print(f"Falló el intento: {e}")

    def sendData(self, data):
        """Envía datos al servidor mediante la cola"""
        if self.player and self.running:
            try:
                # NUEVO: En lugar de enviar directo, metemos la tupla a la cola
                self.cola_mensajes_salida.put((data, self.player))
                print(f"Datos en cola para el servidor: TIPO: {data.get('type')}")
                return True
            except Exception as e:
                print(f"Error encolando datos.....: {e}")
                return False
        
        return False

    def get_msgStartGame(self):
        """Devuelve y borra la lista de mensajes entrantes de forma segura."""
        # self.lock es un threading.Lock que debe usarse para acceder a variables compartidas
        with self.lock: 
            if self.msgStartGame: 
                return "launch_ui2"

    def get_incoming_messages(self):
        """Devuelve y borra la lista de mensajes entrantes de forma segura."""
        # self.lock es un threading.Lock que debe usarse para acceder a variables compartidas
        with self.lock: 
            # 1. Crear una copia de los mensajes recibidos
            messages = list(self.incoming_messages).copy() 
            # 2. Limpiar la cola de mensajes
            self.incoming_messages.clear()
            # 3. Devolver los mensajes
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


    def stop(self):
        """Detiene el servidor o la conexión"""
        self.running = False
        self.receive_thread_running = False
        # Cerra todas las conecciones de jugadores
        for player in self.connected_players:
            try:
                if player[0] != self.server:
                    player[0].close()
            except:
                pass
        # Cerrar sokcet princial
        if self.server:
            try:
                self.server.close()
            except:
                pass

        # Cerrar socket del jugador
        if self.player:
            try:
                self.player.close()
            except:
                pass
        print("Conexión cerrada")

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
        
        # Envía el mensaje a todos los jugadores conectados.
        # Asumo que tienes un método 'broadcast_message' o similar, 
        # si no lo tienes, puedes implementar un bucle para enviar a todos los clientes.
        # Si 'broadcast_message' no existe, puedes usar tu lógica de envío.
        self.broadcast_message(message) 
        
        print(f"Host: Enviando actualización de cartas de elección. Quedan {len(cartas_eleccion_serializada)} cartas.")
        
    def enviar_game_state_sync(self, conn, id_recuperado):
       # """ Construye y envía el estado actual de la mesa al jugador reconectado """
        # NOTA: Debes asegurarte de que en Game.py, al iniciar la ronda, 
        # asignes el objeto Round a network_manager.ronda_actual
        if not hasattr(self, 'ronda_actual') or not self.ronda_actual:
            print("Aún no hay ronda activa para sincronizar.")
            return

        jugador_recuperado = None
        for p in self.ronda_actual.players:
            if p.playerId == id_recuperado:
                jugador_recuperado = p
                break

        if not jugador_recuperado:
            return

        msg_sync = {
            "type": "GAME_STATE_SYNC",
            "playerId": jugador_recuperado.playerId,
            "playerHand": jugador_recuperado.playerHand,       
            "isHand": jugador_recuperado.isHand,               
            "downHand": jugador_recuperado.downHand,           
            "playerPoints": jugador_recuperado.playerPoints,   
            "discards": self.ronda_actual.discards,                 
            "pile_count": len(self.ronda_actual.pile)               
        }

        # Enviamos a la cola para que el hilo lo despache de forma segura
        self.cola_mensajes_salida.put((msg_sync, conn))
        print(f"Sincronización enviada a {jugador_recuperado.playerName}")

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
        if type(dic) == dict:
            for clave, valor in dic.items():
                print(f"{str(clave).rjust(15)}: {valor}")
        else:
            return False
     

     