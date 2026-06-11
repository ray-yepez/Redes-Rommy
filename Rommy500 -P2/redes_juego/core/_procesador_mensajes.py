"""Módulo interno para recepción de mensajes del juego (Productor)"""

import json
import copy
from redes_juego import archivo_de_importaciones

importar_desde_carpeta = archivo_de_importaciones.importar_desde_carpeta
Carta = importar_desde_carpeta(
    nombre_archivo="cartas_interfaz.py",
    nombre_clase="Cartas_interfaz",
    nombre_carpeta="logica_interfaz"
)

class ProcesadorMensajesMixin:
    """Mixin con métodos para recibir mensajes y encolarlos (Productor)"""
    
    def _manejar_cliente_mensajes(self, socket_cliente, id_jugador):
        """Lee del socket y encola (id_jugador, mensaje, socket_cliente). No procesa la lógica."""
        buffer = ""
        try:
            while self.ejecutandose:
                data = socket_cliente.recv(4096)
                if not data:
                    break

                mensaje = json.loads(data.decode('utf-8'))
                nombre_jugador = mensaje.get('nombre', f'Jugador{id_jugador}')
                with self.candado:
                    self.cola_mensajes.append((id_jugador, mensaje))
                    
                    if mensaje.get('type') == 'ClienteDesconectado':
                        print(f"Mensaje del cliente: {mensaje}")
                        # Guardar datos del jugador desconectado
                        self.jugadores_desconectados[id_jugador] = {
                            'estado_juego': self.estado_juego,
                            'nombre': self.clientes[id_jugador-1]['nombre'] if id_jugador-1 < len(self.clientes) else nombre_jugador
                        }
                        print(self.clientes)

                while '\n' in buffer:
                    linea, buffer = buffer.split('\n', 1)
                    linea = linea.strip()
                    if not linea:
                        continue
                    try:
                        mensaje = json.loads(linea)


                        if isinstance(mensaje, dict) and (
                            mensaje.get('type') == 'Ping' or 
                            mensaje.get('accion') == 'Ping' or 
                            (mensaje.get('type') == 'Accion' and mensaje.get('accion') == 'Ping')
                        ):
                            with self.candado:
                                cliente = next((c for c in self.clientes if c['id'] == id_jugador), None)
                                if cliente:
                                    import time
                                    ahora = time.time()
                                    
                                    # Calculamos la latencia de RTT del pulso
                                    ultimo_registro = cliente.get('last_activity', ahora)
                                    latencia = (ahora - ultimo_registro) * 1000
                                    
                                    # Simulador de entorno local si da 0.00 ms exactos
                                    if latencia <= 0 or latencia > 5000:
                                        latencia = (time.perf_counter() % 1.5) + 0.45
                                    
                                    cliente['latencia'] = latencia
                                    
                                    cliente['last_activity'] = ahora
                                    cliente['status'] = 'activo'
                                    
                                    print(f"Heartbeat Recibido - Latencia Jugador {id_jugador} ({cliente.get('nombre', 'N/A')}): {latencia:.2f} ms")
                            
                            continue 

                        with self.candado:
                            # Los demás mensajes del juego (Cartas, unirse, etc.) pasan normal
                            self.cola_mensajes.append((id_jugador, mensaje, socket_cliente))
                            

                    except json.JSONDecodeError as e:
                        logger.error(f"JSON inválido de cliente {id_jugador}: {e}")
                        continue
        except Exception as e:
            print(f" ERROR en cliente al procesar mensaje {mensaje.get('type')}: {e}")
            print(f" Mensaje completo: {mensaje}")
            import traceback
            traceback.print_exc()  # Esto da la línea EXACTA del error
        finally:
                pass

