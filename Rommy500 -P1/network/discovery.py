import socket
import threading
import json
import logging
import time

# pyrefly: ignore [missing-import]
from .state import NetworkState
# pyrefly: ignore [missing-import]
from .config import NetworkConfig

logger = logging.getLogger(__name__)

class Discovery:
    """Servicio de descubrimiento UDP (Broadcast) para redes locales."""
    
    def __init__(self, state: NetworkState, config: NetworkConfig = None):
        self.state = state
        self.config = config or NetworkConfig()
        self.discovered_servers = []
    
    def start_broadcast(self):
        """Inicia el broadcast periódico de la sala (SOLO HOST, CORRE EN HILO)."""
        def broadcast_loop():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            while self.state.running_broadcast:
                try:
                    # Determinar IP local del HOST para publicarla
                    local_ip = "127.0.0.1"
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        s.connect(('10.255.255.255', 1))
                        local_ip = s.getsockname()[0]
                        s.close()
                    except Exception:
                        pass
                    
                    server_data = {
                        "name": self.state.gameName or "Sala de Rummy 500",
                        "playerName": self.state.playerName or "Host",
                        "ip": local_ip,
                        "port": self.config.TCP_PORT,
                        "max_players": self.state.max_players or 4,
                        "currentPlayers": len(self.state.get_connected_players()),
                    }
                    
                    packet = json.dumps(server_data).encode('utf-8')
                    # Broadcastear al puerto definido
                    sock.sendto(packet, ('<broadcast>', self.config.BROADCAST_PORT))
                    logger.debug(f"Broadcast enviado UDP: Sala '{server_data['name']}' IP {server_data['ip']}")
                    
                    time.sleep(self.config.BROADCAST_INTERVAL)
                except Exception as e:
                    logger.error(f"Error en broadcast UDP: {e}")
                    time.sleep(1) # Prevenir bucle de alto consumo en caso de error
            
            sock.close()
        
        self.state.running_broadcast = True
        threading.Thread(target=broadcast_loop, daemon=True).start()
    
    def discover_servers(self, timeout: int = 5):
        """Escucha paquetes UDP broadcast y actualiza discovered_servers asincronamente."""
        self.discovered_servers = []
        
        def listen_loop():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Escuchar en cualquier interfaz sobre el puerto de broadcast
            try:
                sock.bind(('', self.config.BROADCAST_PORT))
            except Exception as e:
                logger.error(f"Error bindeando socket UDP de escucha: {e}")
                return
                
            sock.settimeout(1)
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    data, addr = sock.recvfrom(1024)
                    server_dict = json.loads(data.decode('utf-8'))
                    
                    # Evitar duplicados revisando IPs
                    if not any(s["ip"] == server_dict["ip"] for s in self.discovered_servers):
                        self.discovered_servers.append(server_dict)
                        logger.info(f"Sala descubierta en LAN: {server_dict['name']} en {server_dict['ip']}")
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f"Error al decodificar paquete de descubrimiento: {e}")
            
            sock.close()
        
        listen_thread = threading.Thread(target=listen_loop, daemon=True)
        listen_thread.start()
        # No hacemos join() para no bloquear la interfaz.
