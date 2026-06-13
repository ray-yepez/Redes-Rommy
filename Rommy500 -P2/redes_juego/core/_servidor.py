"""Módulo interno para funcionalidad del servidor"""

import socket
import threading
import json
import time
import copy
from redes_juego import archivo_de_importaciones

importar_desde_carpeta = archivo_de_importaciones.importar_desde_carpeta
mesa_interfaz = importar_desde_carpeta(
    nombre_archivo="mesa_interfaz.py",
    nombre_carpeta="logica_interfaz",
)
Carta = importar_desde_carpeta(
    nombre_archivo="cartas_interfaz.py",
    nombre_clase="Cartas_interfaz",
    nombre_carpeta="logica_interfaz"
)

class ServidorMixin:
    """Mixin con métodos para funcionalidad del servidor"""
    
    def iniciar_servidor(self, nombre_sala="Sala1"):
        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_servidor.bind(('0.0.0.0', self.puerto))
        self.socket_servidor.listen(self.max_jugadores)
        self.ejecutandose = True
        self.aceptar_conexiones_estado = True
        self.anunciar_servidor_estado = True
        hilo_servidor = threading.Thread(target=self.aceptar_conexiones)
        hilo_servidor.daemon = True
        hilo_servidor.start()
        
        hilo_anuncio = threading.Thread(target=self.anunciar_servidor)
        hilo_anuncio.daemon = True
        hilo_anuncio.start()

        hilo_procesar = threading.Thread(target=self._procesar_mensajes)
        hilo_procesar.daemon = True
        hilo_procesar.start()

        print(f"Servidor iniciado en el puerto {self.puerto}, esperando jugadores...")
    
    def aceptar_conexiones(self):
        while self.aceptar_conexiones_estado:
            try:
                #Limitar el número de clientes activos
                with self.candado:
                    jugadores_conectados = len(self.clientes)-len(self.jugadores_desconectados)
                if jugadores_conectados >= self.max_jugadores:
                    print("Sala llena, no se aceptan más conexiones.")
                    time.sleep(1)
                    continue
                socket_cliente, addr = self.socket_servidor.accept()
                with self.candado:
                    print(f"Cliente conectado desde {addr}")
                    id_jugador = len(self.clientes)+1
                    # Añadir el cliente a la lista
                    manejador_cliente = threading.Thread(target=self._procesar_cliente, args=(socket_cliente, id_jugador))
                    manejador_cliente.daemon = True
                    manejador_cliente.start()
                    print(f"Cliente asignado ID {id_jugador}")
            except Exception as e:
                if self.ejecutandose:
                    print(f"Error al aceptar conexiones: {e}")
    
    def _procesar_cliente(self, socket_cliente, id_jugador):
        """Wrapper que delega el procesamiento de mensajes al mixin correspondiente"""
        self._manejar_cliente_mensajes(socket_cliente, id_jugador)
    
    def desconectar_servidor(self):
        """Cierra el servidor y notifica a los clientes"""
        self.ejecutandose = False
        if self.socket_servidor:
            try:
                self.difundir({
                    'type': 'ServidorCerrado'
                })
            except Exception as e:
                print(f"Error al notificar a cliente sobre el cierre del servidor: {e}")
            self.socket_servidor.close()
            self.socket_servidor = None
    
    def _eliminar_cliente(self, id_jugador):
        with self.candado:
            clientes_a_eliminar = [c for c in self.clientes if c['id'] == id_jugador]
            for cliente in clientes_a_eliminar:
                try:
                    cliente['socket'].shutdown(socket.SHUT_RDWR)
                    cliente['socket'].close()
                except Exception as e:
                    print(f"Error cerrando socket de cliente {id_jugador}: {e}")
            # Elimina fuera del bucle
            self.clientes = [c for c in self.clientes if c['id'] != id_jugador]

    def anunciar_servidor(self):
        socket_anuncio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_anuncio.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        socket_anuncio.settimeout(1)

        try:
            while self.anunciar_servidor_estado:
                mensaje = json.dumps({
                'type': 'RummyServer',
                'port': self.puerto,
                'partida': self.nombre_partida,
                'host': getattr(self, 'nombre_host', 'Host'),
                'id_jugadores_desconectados': self.jugadores_desconectados,
                'jugadores': len(self.clientes),
                'max_jugadores': self.max_jugadores,
                "lista_jugadores" : [c['nombre'] for c in self.clientes],
                    }).encode('utf-8')
                socket_anuncio.sendto(mensaje, ('255.255.255.255', 5556)) # Puerto diferente al de conexión
                time.sleep(1) # Anunciarse cada segundo
        except Exception as e:
            print(f"Error en el anuncio del servidor: {e}")
        finally:
            socket_anuncio.close()      

    def _procesar_mensajes(self):
        while self.ejecutandose:
            id_jugador = None
            mensaje = None
            with self.candado:
                if self.cola_mensajes:
                    id_jugador, mensaje = self.cola_mensajes.pop(0)
            if mensaje is not None:
                if mensaje.get('type') == 'NuevoJugador1':
                    print(f"Nuevo jugador conectado: ID {mensaje['id_jugador']}, Total jugadores: {mensaje['TotalJugadores']}")
    
    def verificar_inicio_partida(self):
        if len(self.clientes) >= self.max_jugadores and self.estado_partida == False:
            print("Número máximo de jugadores alcanzado, iniciando partida...")
            self.estado_partida = True
            self.anunciar_servidor_estado = False
            self.aceptar_conexiones_estado = False
            self.iniciar_partida_servidor()
            
    def iniciar_partida_servidor(self):
        # Iniciar la partida
        #1. Se guardan los nombres de los jugadores
        lista_jugadores = []
        for cliente in self.clientes:
            id_jugador = cliente['id']
            nombre_jugador = cliente['nombre']
            tupla_jugador = (id_jugador, nombre_jugador)
            lista_jugadores.append(tupla_jugador)
        #2. Se inicia la mesa
        self.mesa_juego = mesa_interfaz.Mesa_interfaz(self.un_juego)
        #3. Se inicia la mesa
        print("Lista de jugadores para iniciar la partida:", lista_jugadores)
        self.iniciar_partida(lista_jugadores)
        #4. Prepara los datos a enviar
        elementos_mesa = self.mesa_juego.elementos_mesa
        print("Elementos de la mesa a enviar a los clientes:", elementos_mesa)

