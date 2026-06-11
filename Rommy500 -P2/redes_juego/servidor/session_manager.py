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

        hilo_heartbeat = threading.Thread(target=self._verificar_conexiones_activas)
        hilo_heartbeat.daemon = True
        hilo_heartbeat.start()

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

    def _verificar_conexiones_activas(self):
        """Verifica los heartbeats de los clientes y los desconecta si no responden en 15 segundos"""
        while self.ejecutandose:
            tiempo_actual = time.time()
            with self.candado:
                for cliente in self.clientes:
                    # Inicializar si no existe
                    if 'last_activity' not in cliente:
                        cliente['last_activity'] = tiempo_actual
                    
                    if tiempo_actual - cliente['last_activity'] > 15:
                        print(f"Timeout (Heartbeat) detectado para cliente {cliente['id']} ({cliente['nombre']}). Desconectando...")
                        # Inyectar mensaje de desconexión artificial
                        self.cola_mensajes.append((cliente['id'], {'type': 'ClienteDesconectado'}, cliente['socket']))
                        # Evitar spam de desconexiones
                        cliente['last_activity'] = tiempo_actual + 99999
            time.sleep(5)
    
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
        from redes_juego.servidor.message_router import MessageRouter
        enrutador = MessageRouter(self)
        
        while self.ejecutandose:
            id_jugador = None
            mensaje = None
            socket_cliente = None
            with self.candado:
                if self.cola_mensajes:
                    id_jugador, mensaje, socket_cliente = self.cola_mensajes.pop(0)
            if mensaje is not None:
                # El enrutador central procesa TODA la lógica en este hilo seguro
                enrutador.route_message(id_jugador, mensaje, socket_cliente)
                
            else:
                import time
                time.sleep(0.01) # Evitar 100% CPU cuando la cola está vacía
    
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
        
    def verificar_jugadores_activos(self):
      """
      Verifica cuántos jugadores activos quedan en la partida.
      Retorna el número de jugadores activos y la lista de ellos.
      """
      with self.candado:
            jugadores_activos = [c for c in self.clientes if c.get('status') == 'activo']
            return len(jugadores_activos), jugadores_activos

    
    def reiniciar_partida_por_falta_jugadores(self):
     """
     Reinicia el estado de la partida cuando quedan menos de 2 jugadores activos.
     Notifica a todos los clientes y limpia las estructuras de juego.
     """
     print("[SERVIDOR] Menos de 2 jugadores activos. Reiniciando partida...")
    
     # Notificar a todos los clientes que la partida se reinicia
     mensaje_reinicio = { 
        'type': 'PartidaReiniciada',
        'reason': 'faltan_jugadores',
        'mensaje': 'No hay suficientes jugadores para continuar. Volviendo al lobby...'
    }
     self.difundir(mensaje_reinicio)
    
    # Limpiar estado de la partida
     self.estado_partida = False
     self.ronda = 1
     self.descarte = []
     self.quema = []
     self.jugadas_por_jugador = {}
     self.manos = {}
     self.mazo = None
     self.mesa_juego = None
    
    # Limpiar jugadores desconectados
     self.jugadores_desconectados = {}
    
    # Limpiar eventos de conexión
     self.eventos_conexion = []
    
    # Reiniciar contadores de turno
     self.contador_turno_compra = 0
     self.jugador_compra = None
     self.jugador_que_descarto = None
    
    # Marcar que se pueden aceptar nuevas conexiones
     self.aceptar_conexiones_estado = True
    
     print("[SERVIDOR] Estado de partida reiniciado. Esperando nuevos jugadores.")
    
    def eliminar_jugador_inactivo(self, id_jugador):
      """
      Elimina un jugador inactivo de la partida sin detener el juego.
      Si el jugador eliminado era el que tenía el turno, pasa el turno al siguiente.
      """
      with self.candado:
         # Buscar el cliente
         cliente = next((c for c in self.clientes if c.get('id') == id_jugador), None)
         if not cliente:
             return
        
        # Si estaba en partida, eliminarlo de las estructuras de juego
         if self.estado_partida:
            # Remover de la lista de jugadores en la mesa
            if self.mesa_juego and self.mesa_juego.elementos_mesa.get("datos_lista_jugadores"):
                jugadores_mesa = self.mesa_juego.elementos_mesa["datos_lista_jugadores"]
                self.mesa_juego.elementos_mesa["datos_lista_jugadores"] = [
                    j for j in jugadores_mesa if j[0] != id_jugador
                ]
            
            # Remover de cantidad_manos_jugadores
            if self.mesa_juego and self.mesa_juego.elementos_mesa.get("cantidad_manos_jugadores"):
                manos_jugadores = self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"]
                self.mesa_juego.elementos_mesa["cantidad_manos_jugadores"] = [
                    m for m in manos_jugadores if m.get("id") != id_jugador
                ]
            
            # Remover de jugadas_por_jugador
            if id_jugador in self.jugadas_por_jugador:
                del self.jugadas_por_jugador[id_jugador]
            
            # Remover de manos
            if (id_jugador - 1) in self.manos:
                del self.manos[id_jugador - 1]
            
            # Verificar si el jugador eliminado tenía el turno
            if self.mesa_juego and self.mesa_juego.elementos_mesa.get("jugador_mano"):
                jugador_mano_id = self.mesa_juego.elementos_mesa["jugador_mano"][0]
                if jugador_mano_id == id_jugador:
                    self.pasar_turno_al_siguiente_activo(id_jugador)
            
            # Verificar si quedan menos de 2 jugadores activos
            activos, _ = self.verificar_jugadores_activos()
            if activos < 2:
                self.reiniciar_partida_por_falta_jugadores()
            else:
                # Difundir la actualización a los jugadores restantes
                self.difundir_estado_partida_actualizado()
        
         # Marcar como inactivo
         cliente['status'] = 'inactivo'
        
         print(f"[SERVIDOR] Jugador {id_jugador} eliminado de la partida. Activos restantes: {self.verificar_jugadores_activos()[0]}")
    
    def pasar_turno_al_siguiente_activo(self, id_jugador_actual):
      """
      Pasa el turno al siguiente jugador activo cuando el actual se desconecta.
      """
      if not self.mesa_juego:
          return
    
      jugadores = self.mesa_juego.elementos_mesa.get("datos_lista_jugadores", [])
      if not jugadores:
          return
    
    # Encontrar índice del jugador actual
      idx_actual = next((i for i, j in enumerate(jugadores) if j[0] == id_jugador_actual), None)
      if idx_actual is None:
          return
    
    # Buscar siguiente jugador activo
      idx_siguiente = (idx_actual + 1) % len(jugadores)
      intentos = 0
      while intentos < len(jugadores):
        siguiente_id = jugadores[idx_siguiente][0]
        siguiente_nombre = jugadores[idx_siguiente][1]
        
        # Verificar si el jugador está activo
        cliente = next((c for c in self.clientes if c.get('id') == siguiente_id), None)
        if cliente and cliente.get('status') == 'activo':
            # Asignar turno
            self.mesa_juego.elementos_mesa["jugador_mano"] = (siguiente_id, siguiente_nombre)
            
            # Notificar cambio de turno
            self.finalizar_turno(id_jugador_actual, siguiente_id)
            return
        
        idx_siguiente = (idx_siguiente + 1) % len(jugadores)
        intentos += 1
    
      # Si no hay jugadores activos, reiniciar partida
      self.reiniciar_partida_por_falta_jugadores()

    def difundir_estado_partida_actualizado(self):
       """
      Difunde el estado actualizado de la partida a todos los clientes activos.
      """
       if not self.mesa_juego:
           return
      
      # Preparar datos de manos para difundir
       manos_dict = {}
       for idx, mano in self.manos.items():
          try:
             manos_dict[idx + 1] = [c.to_dict() for c in mano]
          except:
             manos_dict[idx + 1] = [c for c in mano]
    
       mensaje = {
          'type': 'ActualizacionEstadoPartida',
          'jugadores_activos': self.verificar_jugadores_activos()[0],
          'datos_lista_jugadores': self.mesa_juego.elementos_mesa.get("datos_lista_jugadores", []),
          'cantidad_manos_jugadores': self.mesa_juego.elementos_mesa.get("cantidad_manos_jugadores", []),
          'jugador_mano': self.mesa_juego.elementos_mesa.get("jugador_mano"),
          'jugadas_jugadores': self.jugadas_por_jugador,
          'manos': manos_dict
        }
    
       self.difundir(mensaje)

    def cerrar_sala_por_host_desconectado(self, id_host):
     """
     Cierra la sala y desconecta a todos los clientes cuando el host se desconecta.
     """
     print(f"[SERVIDOR] Host (ID {id_host}) desconectado. Cerrando sala...")
    
    # Notificar a todos los clientes que la sala se cierra
     mensaje_cierre = {
        'type': 'SalaCerrada',
        'reason': 'host_desconectado',
        'mensaje': 'El host de la sala se ha desconectado. La sala se cerrará.'
     }
     self.difundir(mensaje_cierre)
     
    # Desconectar a todos los clientes
     for cliente in self.clientes[:]:  # Copia para evitar modificación durante iteración
        try:
            if cliente.get('socket'):
                cliente['socket'].close()
        except Exception as e:
            print(f"Error cerrando conexión del cliente {cliente.get('id')}: {e}")
    
    # Limpiar listas
     self.clientes.clear()
     self.jugadores_desconectados.clear()
    
    # Detener el servidor
     self.ejecutandose = False
     self.estado_partida = False
     self.aceptar_conexiones_estado = False
     self.anunciar_servidor_estado = False
    
    # Cerrar socket del servidor
     if self.socket_servidor:
        try:
            self.socket_servidor.close()
        except:
            pass
        self.socket_servidor = None
    
     print("[SERVIDOR] Sala cerrada completamente.")

