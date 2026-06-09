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
        try:
            self._manejar_cliente_mensajes(socket_cliente, id_jugador)
        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            # Socket roto - el cliente se desconectó abruptamente
           print(f"[INFO] Cliente {id_jugador} se desconectó abruptamente: {e}")
           self._manejar_desconexion_cliente(id_jugador)
        except Exception as e:
           print(f"[ERROR] Error inesperado con cliente {id_jugador}: {e}")
           self._manejar_desconexion_cliente(id_jugador)
        finally:
        # Limpiar recursos del cliente
            try:
              socket_cliente.close()
            except:
               pass
    
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
        
        # En _servidor.py, agregar este método:

    def _manejar_desconexion_cliente(self, id_jugador):
         """Maneja la desconexión de un cliente (pregunta si quiere salir)"""
          # Buscar el nombre del jugador
         nombre_jugador = f"Jugador {id_jugador}"
         for cliente in self.clientes:
              if cliente.get('id') == id_jugador:
                nombre_jugador = cliente.get('nombre', nombre_jugador)
                break
    
         print(f"\n[DESCONEXIÓN] El jugador '{nombre_jugador}' (ID: {id_jugador}) se ha desconectado.")
    
         # Verificar si el que se desconectó es el HOST (id=1)
         if id_jugador == 1:
           print("[SERVIDOR] El HOST se ha desconectado. Cerrando la sala para todos...")
           self._cerrar_sala_por_host_desconectado()
           return
    
         # Si no es el host, continuar la partida
         with self.candado:
           # Marcar cliente como desconectado
            for cliente in self.clientes:
                if cliente.get('id') == id_jugador:
                   cliente["status"] = "desconectado"
                   break
        
         # Guardar en jugadores_desconectados
            self.jugadores_desconectados[id_jugador] = {
                'estado_juego': self.estado_juego,
                'nombre': nombre_jugador
            }
    
          # Notificar a los demás jugadores
         try:
            self.difundir({
            'type': 'JugadorDesconectado',
            'id_jugador': id_jugador,
            'TotalJugadores': len(self.clientes),
            "nombre": nombre_jugador,
            "lista_jugadores": [c.get('nombre', '') for c in self.clientes if c.get('status') == 'activo']
         })
         except Exception as e:
           print(f"Error notificando desconexión: {e}")
    
    # Si la partida está en curso, continuar con la lógica de juego
         if self.estado_partida:
          self._continuar_partida_despues_desconexion(id_jugador)
    
         print(f"[INFO] Partida continúa con {len(self.contar_jugadores_activos())} jugadores activos.")

    def _cerrar_sala_por_host_desconectado(self):
      """Cierra la sala y notifica a todos que el host se fue"""
      try:
           # Enviar mensaje especial a todos los clientes
            self.difundir({
            'type': 'HostDesconectado',
            'mensaje': 'El creador de la sala ha cerrado la partida.\nSerás enviado al menú principal.'
        })
      except Exception as e:
             print(f"Error notificando cierre por host: {e}")
    
    # Esperar un momento para que los mensajes se envíen
      import time
      time.sleep(0.5)
    
    # Cerrar todos los sockets de clientes
      for cliente in self.clientes:
             try:
                 cliente['socket'].close()
             except:
               pass
    
    # Cerrar socket del servidor
      self.ejecutandose = False
      self.aceptar_conexiones_estado = False
      self.anunciar_servidor_estado = False
    
      if self.socket_servidor:
            try:
               self.socket_servidor.close()
            except:
               pass
    
    print("[SERVIDOR] Sala cerrada por desconexión del host.")

    def _continuar_partida_despues_desconexion(self, id_jugador):
      """Continúa la partida después de que un jugador no-host se desconecta"""
      print(f"[PARTIDA] Procesando continuación después de desconexión de {id_jugador}")
    
      # Verificar si el jugador desconectado era el que tenía el turno
      if hasattr(self, 'mesa_juego') and self.mesa_juego:
         jugador_mano = self.mesa_juego.elementos_mesa.get("jugador_mano", (None,))
         if jugador_mano[0] == id_jugador:
            # El jugador que se fue tenía el turno - cambiar al siguiente
            jugadores = self.mesa_juego.elementos_mesa.get("datos_lista_jugadores", [])
            idx_actual = next((i for i, j in enumerate(jugadores) if j[0] == id_jugador), None)
            
            if idx_actual is not None:
                # Buscar siguiente jugador activo
                num = 1
                encontrado = False
                for _ in range(len(jugadores)):
                    idx_siguiente = (idx_actual + num) % len(jugadores)
                    id_siguiente = jugadores[idx_siguiente][0]
                    # Verificar si el jugador está activo
                    for cliente in self.clientes:
                        if cliente.get('id') == id_siguiente and cliente.get('status') == 'activo':
                            nombre = jugadores[idx_siguiente][1]
                            self.mesa_juego.elementos_mesa.update({"jugador_mano": (id_siguiente, nombre)})
                            encontrado = True
                            break
                    if encontrado:
                        break
                    num += 1
                
                # Notificar cambio de turno
                if encontrado:
                    self.difundir({
                        "type": "Actualizar_Etiqueta_Turno",
                        "jugador_mano": self.mesa_juego.elementos_mesa["jugador_mano"],
                        "cantidad_manos_jugadores": self.mesa_juego.elementos_mesa.get("cantidad_manos_jugadores", []),
                        "turno_robar": False
                    })

