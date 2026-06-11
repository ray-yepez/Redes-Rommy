"""Módulo interno para funcionalidad del cliente"""

import socket
import threading
import json
import time
import pygame
from redes_juego import archivo_de_importaciones

importar_desde_carpeta = archivo_de_importaciones.importar_desde_carpeta
constantes = importar_desde_carpeta(
    nombre_archivo="constantes.py",
    nombre_carpeta="recursos_graficos",
)
mesa_interfaz = importar_desde_carpeta(
    nombre_archivo="mesa_interfaz.py",
    nombre_carpeta="logica_interfaz",
)
Carta = importar_desde_carpeta(
    nombre_archivo="cartas_interfaz.py",
    nombre_clase="Cartas_interfaz",
    nombre_carpeta="logica_interfaz"
)
Boton = importar_desde_carpeta(
    nombre_archivo="elementos_de_interfaz_de_usuario.py",
    nombre_clase="Boton",
    nombre_carpeta="recursos_graficos",
)

class ClienteMixin:
    """Mixin con métodos para funcionalidad del cliente"""
    
    def conectar_a_servidor(self, ip_servidor, id_jugador_reconectar=None, nombre_jugador=None):
        try:
            print(f"Conectado al servidor en {ip_servidor}:{self.puerto}")
            self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_cliente.connect((ip_servidor, self.puerto))
            self.conectado = True
            print("Enviando mensaje de conexión...")
            if id_jugador_reconectar is not None:
                mensaje = {
                        'type': 'Reconectar',
                        'id_jugador': id_jugador_reconectar,
                        'nombre': nombre_jugador
                    }
            else:
                mensaje = {
                    'type': 'NuevoJugador',
                    'nombre': nombre_jugador
                }
            print(f"Mensaje enviado: {mensaje}")    
            self.socket_cliente.sendall((json.dumps(mensaje) + '\n').encode('utf-8'))
            self.hilo_recepcion = threading.Thread(target=self._recibir_mensajes)
            self.hilo_recepcion.daemon = True
            self.hilo_recepcion.start()
            self.hilo_ping = threading.Thread(target=self._enviar_pings)
            self.hilo_ping.daemon = True
            self.hilo_ping.start()
            return True
        except Exception as e:
            print(f"Error al conectar al servidor: {e}")
            return False
    def _enviar_pings(self):
        """Envía un heartbeat al servidor cada 5 segundos"""
        while self.conectado:
            time.sleep(5)
            if self.conectado:

                
                self.tiempo_ping_enviado = time.perf_counter()

                self.enviar_accion('Ping')

    def _recibir_mensajes(self):
        buffer = ""
        while self.conectado:
            try:
                data = self.socket_cliente.recv(65536)
                if not data:
                    print("[RED-CLIENTE] Servidor cerró la conexión.")
                    break
                buffer += data.decode('utf-8')
                while '\n' in buffer:
                    mensaje_str, buffer = buffer.split('\n', 1)
                    if mensaje_str.strip():
                        mensaje = json.loads(mensaje_str)
                        self._manejo_mensaje_red(mensaje)
                        
            except Exception as e:
                print(f"[RED-CLIENTE] Error al recibir mensaje del servidor: {e}")
                import traceback
                traceback.print_exc()
                # FIX C-05: Intentar reconexión automática (código movido a lugar alcanzable)
                if self.id_jugador is not None and self.socket_cliente is not None:
                    try:
                        ip_servidor = self.socket_cliente.getpeername()[0]
                        print(f"[RED-CLIENTE] Intentando reconexión automática a {ip_servidor}...")
                        self.intentar_reconexion(ip_servidor)
                    except Exception as re:
                        print(f"[RED-CLIENTE] No se pudo determinar IP para reconexión: {re}")
                break


    def _manejo_mensaje_red(self, mensaje):
        if not hasattr(self, '_message_handler'):
            from redes_juego.cliente.message_handler import MessageHandler
            self._message_handler = MessageHandler(self)
        self._message_handler.handle_message(mensaje)

    def encontrar_ip_servidor(self, un_juego):
        socket_busqueda = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_busqueda.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_busqueda.bind(('', 5556)) # Escuchar en el mismo puerto que el anuncio
        socket_busqueda.settimeout(2.0) # Esperar 2 segundos para mayor responsividad

        print("[RED-CLIENTE] Buscando servidor en la red...")
        try:
            while self.buscador:
                try:
                    data, direccion_servidor = socket_busqueda.recvfrom(1024)
                    mensaje = json.loads(data.decode('utf-8'))
                    ip_encontrada = direccion_servidor[0]
                    
                    if mensaje.get('type') != 'RummyServer':
                        continue
                        
                    nombre_partida = mensaje.get('partida', 'Desconocida')
                    nombre_host = mensaje.get('host', 'Host')
                    max_jugadores = mensaje.get('max_jugadores', 7)
                    jugadores = mensaje.get('jugadores', 0)
                    self.jugadores_desconectados = mensaje.get('id_jugadores_desconectados', {})
                    lista_jugadores = mensaje.get('lista_jugadores', [])
                    
                    info = {
                        "nombre": nombre_partida,
                        "jugadores": jugadores,
                        "max_jugadores": max_jugadores,
                        "ip": ip_encontrada,
                        "lista_jugadores": lista_jugadores,
                        "creador": nombre_host
                    }
                    
                    servidor_encontrado = None
                    for server in self.conexiones_disponibles:
                        if server['ip'] == ip_encontrada:
                            servidor_encontrado = server
                            break

                    if servidor_encontrado is None:
                        # FIX N-09: Si no está, lo agregamos
                        print(f"Servidor encontrado en la IP: {ip_encontrada} - Partida: {nombre_partida} - Host: {nombre_host}")
                        self.conexiones_disponibles.append(info)
                        evento_py = pygame.event.Event(constantes.EVENTO_SALAS_ENCONTRADAS, salas=self.conexiones_disponibles)
                        pygame.event.post(evento_py)
                    elif servidor_encontrado["jugadores"] != jugadores or servidor_encontrado["lista_jugadores"] != lista_jugadores:
                        # Si está y hay cambios, actualizamos
                        servidor_encontrado["jugadores"] = jugadores
                        servidor_encontrado["lista_jugadores"] = lista_jugadores
                        evento_py = pygame.event.Event(constantes.EVENTO_SALAS_ENCONTRADAS, salas=self.conexiones_disponibles)
                        pygame.event.post(evento_py)
                        
                except socket.timeout:
                    # FIX: No limpiar la lista en timeout, solo iterar para checar self.buscador
                    pass
                except Exception as e:
                    print(f"[RED-CLIENTE] Error buscando servidor: {e}")
                    time.sleep(1) # Pequeña pausa en caso de error continuo
        finally:
            socket_busqueda.close()
            print("[RED-CLIENTE] Búsqueda de servidores detenida.")


    def intentar_reconexion(self, ip_servidor, intentos=5, espera=3):
        """
        Delega el intento de reconexión al ReconnectionManager.
        """
        if not hasattr(self, '_reconnection_manager'):
            from redes_juego.cliente.reconnection import ReconnectionManager
            self._reconnection_manager = ReconnectionManager(self)
        return self._reconnection_manager.intentar_reconexion(ip_servidor, intentos, espera)
    
    def enviar_accion(self, accion, datos=None):
        if self.conectado and self.socket_cliente:
            mensaje = {'type': accion}
            if datos:
                mensaje.update(datos)
            try:
                self.socket_cliente.sendall((json.dumps(mensaje) + '\n').encode('utf-8'))
            except Exception as e:
                print(f"Error al enviar acción al servidor: {e}")
        else:
            print("No conectado al servidor, no se puede enviar la acción.")

    def verificar_conexion_nueva(self,ip_encontrada):
        for x in self.conexiones_disponibles:
            if ip_encontrada != self.conexiones_disponibles["ip"]:
                return True
            else:
                return False

    def desconectar_cliente(self):
        """Cierra la conexión del cliente"""
        self.conectado = False
        if self.socket_cliente and self.id_jugador is not None:
            try:
                mensaje_desconexion = {
                    'type': 'ClienteDesconectado',
                    'id_jugador': self.id_jugador
                }
                self.socket_cliente.send(json.dumps(mensaje_desconexion).encode('utf-8'))
                time.sleep(2)
            except Exception as e:
                print(f"Error al notificar al servidor sobre la desconexión: {e}")
            finally:
                try:
                    self.socket_cliente.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                self.socket_cliente.close()
                self.socket_cliente = None
                if hasattr(self, '_manejo_mensaje_red'):
                    self._manejo_mensaje_red({
                        'type': 'JugadorDesconectado',
                        'id_jugador': self.id_jugador,
                        'TotalJugadores': len(self.clientes) if hasattr(self, 'clientes') else 0
                    })
        else:
            print("Socket cliente no existe o ID de jugador no asignado")
            print(f"Socket cliente: {self.socket_cliente}, ID jugador: {self.id_jugador}")

        # Cerrar hilo de recepción del cliente
        if self.hilo_recepcion and threading.current_thread() != self.hilo_recepcion:
            self.hilo_recepcion.join()

    def desconectar_servidor(self):
        """Cierra el servidor y notifica a los clientes"""
        self.ejecutandose = False
        if self.socket_servidor:
            try:
                if hasattr(self, 'difundir'):
                    self.difundir({
                        'type': 'ServidorCerrado'
                    })
            except Exception as e:
                print(f"Error al notificar a cliente sobre el cierre del servidor: {e}")
            self.socket_servidor.close()
            self.socket_servidor = None

    def desconectar(self):
        """Cierra todas las conexiones (compatibilidad hacia atrás)"""
        self.ejecutandose = False
        self.conectado = False
        self.desconectar_servidor()
        self.desconectar_cliente()

