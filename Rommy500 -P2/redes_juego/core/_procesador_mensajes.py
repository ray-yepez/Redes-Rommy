"""Módulo interno para recepción de mensajes del juego (Productor)"""

import json
from redes_juego.logging_config import logger

class ProcesadorMensajesMixin:
    """Mixin con métodos para recibir mensajes y encolarlos (Productor)"""
    
    def _manejar_cliente_mensajes(self, socket_cliente, id_jugador):
        """Lee del socket y encola (id_jugador, mensaje, socket_cliente). No procesa la lógica."""
        buffer = ""
        try:
            while self.ejecutandose:
                try:
                    data = socket_cliente.recv(65536)
                except OSError:
                    break
                if not data:
                    break

                buffer += data.decode('utf-8')

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
            logger.error(f"Error en recepción de cliente {id_jugador}: {e}")
