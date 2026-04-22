import socket
import threading
import pickle
import time
import json

class NetworkManager:
    def __init__(self):
        self.server = None
        self.servers = []  #lista de servidores
        self.currentServer = None # Información del servidor  CREADOR
        self.client = None
        self.connection = None
        self.host = " "
        self.port = 5555
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
        self.msgStartGame = {}     # Para iniciar la partida de los jugadores
        self.game_state = {}     # Para el estado persistente del juego
        self.incoming_messages = [] # Para mensajes transitorios (chat, notificaciones)
        self.moves_game = []       # Jugadas del jugador
        self.moves_gameServer = [] # Jugadas de los jugadores usadas para el Host 
        # Diccionario auxiliar para la sincronización (ya asociado por ID)
        #self.ready_state = {} 
        #self.next_player_id = 0 # Contador simple para asignar IDs
        self.game_started = False
        #self.player_ids = {}


    def getLocalIP(self):
        """Obtiene la IP local de la computadora"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80)) #PON LA IP DE TU ROUTER AQUI
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            print(f"Error: {e}")
            return "127.0.0.1" #Local IP
        

    def start_server(self, gameName, password, max_players,name_sala):
        self.host = self.getLocalIP() #Obteniendo IP del Creador (SERVIDOR)
        """Inicia el servidor del juego"""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host, self.port))
            self.server.listen(max_players)
            
            self.gameName = name_sala
            self.playerName = gameName   #Falta input_box 
            playerName = ""
            self.password = password
            self.max_players = max_players
            self.is_host = True
            self.running = True
            #self.connected_players.append((self.server,(self.host, self.port),self.playerName))
            self.connected_players.append((self.server,(self.host, self.port),self.playerName))
            print(f"connected_player al INICIO {self.connected_players}")
            print(f"Servidor iniciado en el puerto {self.port}")
            # Hilo para aceptar conexiones
            threading.Thread(target=self.acceptConnections, daemon=True).start()

            # Iniciar hilo para broadcast
            self.running_broadcast = True
            self.broadcast_thread = threading.Thread(target=self.broadcast_server, daemon=True)
            self.broadcast_thread.start()
            print(F"HILO PARA EL BROASDCAST... ")

            self.currentServer = {
            'name': self.gameName,
            'playerName': self.playerName,
            'ip': self.host,
            'port': self.port,
            'max_players': max_players,
            'password': self.password,
            'currentPlayers': len(self.connected_players)        
            }
            print(f" currentServer.... {self.currentServer}")
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
                
                data = conn.recv(2048)  
                if not data:
                    print("No llego la Clave...Cerrando esa conexion")
                    conn.close()
                    continue
                    
                client_password, client_name = pickle.loads(data)
                #print(f"Lo que esta en la clave... {client_password}")
                #print(f"Lo que esta en la clave sin pickle ... {data}")
                # Verificar contraseña
                if client_password == self.currentServer['password']:  #self.password:
                    
                    if len(self.connected_players) < self.currentServer['max_players']:
                        # Actualizar si el servidor ya está en la lista
                        existing = next((s for s in self.connected_players if s ==  (conn,addr,client_name)), None)
                        print(existing)
                        if existing:
                            # Actualizando conexión existente
                            index = self.connected_players.index(existing)
                            self.connected_players[index]=(conn, addr, client_name)
                        else:
                            #self.connected_players.append((conn,addr,self.currentServer['playerName']))
                            self.connected_players.append((conn,addr, client_name))
                            print(f"Anxeando nuevo JUGADOR {self.connected_players}")
                            print(f"Nuevo jugador conectado {addr,client_name}")
                        
                            conn.send(pickle.dumps("CONNECTED"))
                            print(f"Conexión aceptada de {addr}")
                        # Acualizando la cantidad de jugadores
                        self.currentServer['currentPlayers'] = len(self.connected_players)

                        # Hilo para manejar al jugador
                        threading.Thread(
                            target=self.handlePlayer,
                            args=(conn, addr, client_name),
                            daemon=True
                        ).start()
                        
                    else:
                        conn.send(pickle.dumps("FULL"))
                        conn.close()
                else:
                    conn.send(pickle.dumps("WRONG_PASSWORD"))
                    conn.close()
                    
            except Exception as e:
                print(f"Error aceptando conexión: {e}")
                if self.running:
                    continue
                else:
                    break


    def handlePlayer(self, conn, addr, namePlayer):
        """Maneja la comunicación con un cliente conectado"""
        player_name = f"{namePlayer}" #Para identificar al juador por el puerto
        try:
            while self.running:
                try:
                    data = conn.recv(8192)
                    if not data:
                        break
                        
                    with self.lock:
                        #print("Antes del pickle")
                        received_data = pickle.loads(data)
                        self.received_data = received_data  # Informacion del juego para el Host
                        #print(f"Mensaje recibido de {player_name}: {received_data}")

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
                        if isinstance(received_data, dict): # and received_data[0]=="chat_messages":
                            print(f"Transmitiendo mensaje de los jugadores: {received_data}")
                            # Enviar el mensaje a todos los clientes conectados
                            self.broadcast_message((received_data, conn))
                        #pass
                    
                except Exception as e:
                    print(f"Error manejando jugador {player_name}: {e}")   # Se cambió addr por player_name
                    break
                    
        finally:
            conn.close()
            with self.lock:
                self.connected_players = [p for p in self.connected_players if p[0] != conn]
                self.currentServer['currentPlayers'] = len(self.connected_players)   
            print(f"Conexión cerrada con {addr}, Cantidad de JUGADORES:{len(self.connected_players)}")

    def discoverServers(self, timeout=5):  
        """Descubre servidores disponibles en la red local"""
        self.servers = []
        
        # Escuchar por servidores
        listenThread = threading.Thread(target=self.listenForServers, args=(timeout,), daemon=True)
        listenThread.start()
        
        print(f"asi va quedando la lista de servidores!",self.servers)
        return None #self.servers
    
    
    def listenForServers(self, timeout=5):
        """Escucha anuncios de servidores en la red"""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', self.port))
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
                    s.sendto(data, ('<broadcast>', self.port))
                    print(f"Datos Tansmitiendose ", data )
                    time.sleep(3)  #3 segundos
                except Exception as e:
                    print(f"No se pudo hacer la transmisión...{e}")
                    break
    
    def stop_broadcast(self):
        """Detiene solo el broadcast"""
        self.running_broadcast = False

    def broadcast_message(self, message):
        """Envía un mensaje a todos los clientes conectados excepto al remitente"""
        if not self.connected_players:
            print(" No hay jugadores conectados ")
            return
        
        #print(f"Loqueestaenelmensajedelatransmisión... {message}")
        disconnectedPlayer = []
        try:
            # Bloqueando el lock antes de acceder a connected_players
            with self.lock:
                # No enviar al jugador remitente
                if isinstance(message, tuple):
                    connSend = message[1]
                    message1 = message[0]
                    self.messagesServer.append(message1)
                    #print(f"Agregando mensaje de jugador a Lista de mensaje del servidor... {self.messagesServer}")
                else:
                    message1 = message
                    connSend = None
                for conn, addr, _ in self.connected_players:
                    # No enviar al servidor   El servidor tambien es jugador
                    if conn == self.server:
                        continue
                  
                    if conn!=connSend:
                        try:
                            conn.send(pickle.dumps(message1))
                            print(f"Mensaje broadcast a {addr}: {message1}")
                        except Exception as e:
                            print(f"Error enviando mensaje a {addr}: {e}")
                            disconnectedPlayer.append((conn, addr))

                # Si hay un error con un cliente, cerrar su conexión
                #Remover jugadores desconectados    
                for player in disconnectedPlayer:
                    print(f"Jugadores desconectado.... POR MENSAJERIA: {player}")
                    self.connected_players.remove(player)
                self.currentServer['currentPlayers'] = len(self.connected_players)
                    #conn.close()
        except Exception as e:
            print(f"Error en broadcast: {e}")

    def connectToServer(self, server):
        """Conecta al servidor especificado"""
        try:
            self.player = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.player.connect((server['ip'], server['port']))
            print("Socket creado...")
            print(f"esto es el server {server}")
            
            # Enviar contraseña
            self.player.send(pickle.dumps((server['password'],server['playerName'])))
            print("clave enviada...")
            
            # Recibir respuesta
            response = pickle.loads(self.player.recv(2048))
            print(f"respuesta recibida... {response}")
            if response == "CONNECTED":
                self.host = server['ip']
                self.is_host = False
                self.running = True
                
                # Hilo para que el jugador reciba datos
                receiveThread = threading.Thread(target=self.receiveData, daemon=True)
                receiveThread.start()
                print("Hilo para recepción de datos iniciado")
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
                data = self.player.recv(8192) #2048->4096
                if not data:
                    print("Conexion cerrada por el servidor")
                    break

                received_data = pickle.loads(data)

                #print(f"Datos recibidos {received_data}")
                
                with self.lock:
                    self.receivedData = received_data
                    print(f"Datos recibidos y almacenados en self.receivedData... :: {self.receivedData}")
                    #if self.running:
                    #    time.sleep(0.1) #Pausa antesde reintentar
                    #break
                    print(f"Tipo dedatodelmenaje... {type(received_data)}")
                    if isinstance(received_data, dict) and received_data.get("type")=="START_GAME":
                        self.msgStartGame.update(received_data)
                        # self.msgPlayersCarSelection = received_data
                        print("Haciendo copia de .... ah joda")
                
                    # Si es un mensaje de ESTADO (como el que contiene cartas_disponibles, elecciones, etc.) en ui2
                    elif isinstance(received_data, dict) and received_data.get("type") in ["ELECTION_CARDS","SELECTION_UPDATE", "ESTADO_CARTAS", "ORDEN_COMPLETO"]:
                        self.game_state.update(received_data)
                        print(f"Estado del juego actualizado: {self.game_state}")
                        
                    # Si es un mensaje entrante de CHAT o NOTIFICACIÓN simple
                    elif isinstance(received_data, str):
                        self.incoming_messages.append(("chat", received_data)) 
                        print(f"Mensaje de chat/notificación recibido: {received_data}")
   
                    elif isinstance(received_data, dict) and received_data.get("type") in ["BAJARSE","TOMAR_DESCARTE", "TOMAR_CARTA", "DESCARTE", "COMPRAR_CARTA", "PASAR_DESCARTE", "INICIAR_COMPRA","INSERTAR_CARTA","PASAR_COMPRA","REALIZAR_COMPRA","SWAP_JOKER"]:
                        self.moves_game.append(received_data)
                        print(f" Jugada del jugador recibida:{received_data.get("type"),self.moves_game}")
                    # Si es otro tipo de estructura/mensaje no clasificado
                    else:
                        # Puedes mantener el antiguo self.receivedData para mensajes no tipificados,
                        # O agregar un sistema de colas/eventos si usas Pygame.event.
                        self.incoming_messages.append(("raw", received_data)) # Opcional: para mensajes no clasificados
                        print(f"Mensaje guardado en incoming_messages... raw {self.incoming_messages}")
            
            except socket.timeout:
                continue
            except ConnectionResetError:
                print("Conexión reseteada por el servidor")
                break        
            except Exception as e:
                print(f"Error recibiendo datos: {e}")
                #break
                continue
        print("Hilo de recepción terminado. ")

    def sendData(self, data):
        """Envía datos al servidor"""
        if self.player and self.running:
            try:
                self.player.send(pickle.dumps(data))
                print(f"Datos enviados al servidor: {data}")
                return True
            except Exception as e:
                print(f"Error enviando datos.....: {e}")
                return False
        
        return False

    def get_msgStartGame(self):
        """Devuelve y borra la lista de mensajes entrantes de forma segura."""
        # self.lock es un threading.Lock que debe usarse para acceder a variables compartidas
        with self.lock: 
            # 1. Crear una copia de los mensajes recibidos
            if self.msgStartGame: 
                # 2. Limpiar la cola de mensajes
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
            #print(f"ANTES {messages, self.player, self.server}")
            self.moves_game.clear()
            # 3. Devolver los mensajes
            #print(f" Pasé por aqui CABRON!!! get_moves_game {messages, self.player, self.server}")
            return messages
        
    def get_moves_gameServer(self):
        """Devuelve y borra la lista de mensajes de jugadas del juego de forma segura."""
        # self.lock es un threading.Lock que debe usarse para acceder a variables compartidas
        with self.lock: 
            # 1. Crear una copia de los mensajes recibidos
            messages = self.moves_gameServer.copy() 
            # 2. Limpiar la cola de mensajes
            #print(f"ANTES {messages, self.player, self.server}")
            self.moves_gameServer.clear()
            # 3. Devolver los mensajes
            #print(f" Pasé por aqui CABRON!!! get_moves_game {messages, self.player, self.server}")
            return messages

    def stop(self):
        """Detiene el servidor o la conexión"""
        self.running = False
        if self.server:
            try:
                self.server.close()
                self.connected_players.remove(self.server)
            except:
                pass
        if self.player:
            try:
                self.player.close()
                self.connected_players.remove(self.player)
                self.server.sendall() 
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
    
    """
    def send_start_game_to_all(self):
        mensaje = pickle.dumps(("START_GAME", None))
        for jugador in self.connected_players:
            if isinstance(jugador, tuple) and hasattr(jugador[0], "sendall"):
                try:
                    jugador[0].sendall(mensaje)
                    print(f"Enviando START_GAME a {jugador[1]}")
                except Exception as e:
                    print(f"Error enviando START_GAME a {jugador[1]}: {e}")
    """