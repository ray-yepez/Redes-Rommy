"""
Sistema de empaquetado de mensajes con header de 10 bytes
Estructura del Diccionario:
- Header (10 bytes): longitud del JSON en bytes (padding a 10 caracteres)
- Payload: mensaje JSON
"""
import json

HEADER_SIZE = 10

# ESQUEMAS DE MENSAJES
MESSAGE_SCHEMAS = {
    # Mensajes Cliente -> Servidor
    'NuevoJugador': {
        'required': ['type', 'nombre'],
        'optional': []
    },
    'Reconectar': {
        'required': ['type', 'nombre'],
        'optional': ['id_jugador']
    },
    'ClienteDesconectado': {
        'required': ['type', 'id_jugador'],
        'optional': []
    },
    'Tomar_Carta_Descarte': {
        'required': ['type'],
        'optional': []
    },
    'Descarte_Carta': {
        'required': ['type', 'carta_descartada'],
        'optional': []
    },
    'No_tomar_descarte': {
        'required': ['type'],
        'optional': []
    },
    'comprar': {
        'required': ['type'],
        'optional': []
    },
    'Tomar_carta_mazo': {
        'required': ['type'],
        'optional': []
    },
    'validar_seleccion': {
        'required': ['type', 'datos_cartas'],
        'optional': []
    },
    'bajarse': {
        'required': ['type'],
        'optional': []
    },
    'PING': {
        'required': ['type'],
        'optional': []
    },
    'PONG_HOST': {
        'required': ['type'],
        'optional': []
    },
    'ReporteLatencia': {
        'required': ['type', 'valor'],
        'optional': []
    },
    
    # Mensajes Servidor -> Cliente
    'Bienvenido': {
        'required': ['type', 'id_jugador', 'nombre'],
        'optional': ['game_state']
    },
    'Reconectado': {
        'required': ['type', 'nombre'],
        'optional': ['id_jugador']
    },

    'jugadorDesconectado': {
        'required': ['type', 'id_jugador'],
        'optional': []
    },
    'NuevoJugador': {
        'required': ['type', 'nombre'],     
        'optional': ['id_jugador']    
    },
    'JugadorDesconectado': {
        'required': ['type', 'id_jugador', 'TotalJugadores', 'nombre', 'lista_jugadores'],
        'optional': []
    },
    'ServidorCerrado': {
        'required': ['type'],
        'optional': []
    },
    'ManoInicial': {
        'required': ['type', 'mano', 'cantidad_manos_jugadores', 'mazo', 'id_jugador', 'jugador_mano', 'datos_lista_jugadores'],
        'optional': ['dato_carta_descarte']
    },
    'PING_HOST': {
        'required': ['type'],
        'optional': []
    },
    'PONG': {
        'required': ['type'],
        'optional': []
    },
    'Fin_Ronda_Puntuaciones': {
        'required': ['type', 'ganador', 'resultados', 'cantidad_manos_jugadores', 'siguiente_ronda'],
        'optional': []
    },
    'Fin_Partida_Ganador': {
        'required': ['type', 'id_ganador', 'nombre_ganador', 'mensaje'],
        'optional': []
    },
     'Regresando_menu': {
        'required': ['type'],
        'optional': []
    },
}

# FUNCIONES PRINCIPALES
def pack_message(mensaje: dict) -> bytes:
    """
    Empaqueta un mensaje con header de 10 bytes.
    
    Formato: [10 bytes: longitud del payload] + [payload JSON]
    """
    json_str = json.dumps(mensaje, ensure_ascii=False)
    json_bytes = json_str.encode('utf-8')
    payload_len = len(json_bytes)
    header = str(payload_len).zfill(HEADER_SIZE).encode('utf-8')
    return header + json_bytes


def unpack_message(buffer: bytes):
    """
    Desempaqueta un mensaje desde un buffer.
    
    Retorna: (mensaje_dict, error_msg)
    - Si el mensaje está completo: (mensaje, None)
    - Si falta data: (None, "Buffer insuficiente...")
    - Si hay error: (None, "Error...")
    """
    if len(buffer) < HEADER_SIZE:
        return None, "Buffer insuficiente para leer header"
    
    header = buffer[:HEADER_SIZE].decode('utf-8').strip()
    
    try:
        payload_len = int(header)
    except ValueError:
        return None, f"Header inválido: {header}"
    
    if len(buffer) < HEADER_SIZE + payload_len:
        return None, f"Payload incompleto: esperado {payload_len}, recibido {len(buffer) - HEADER_SIZE}"
    
    payload_bytes = buffer[HEADER_SIZE:HEADER_SIZE + payload_len]
    
    try:
        mensaje = json.loads(payload_bytes.decode('utf-8'))
        return mensaje, None
    except json.JSONDecodeError as e:
        return None, f"Error decodificando JSON: {e}"


def validate_message_schema(mensaje: dict) -> tuple:
    """
    Valida un mensaje contra su esquema definido.
    
    Retorna: (es_valido, mensaje_error)
    """
    if not isinstance(mensaje, dict):
        return False, "El mensaje no es un diccionario"
    
    msg_type = mensaje.get('type')
    
    if not msg_type:
        return False, "El mensaje no tiene campo 'type'"
    
    if msg_type not in MESSAGE_SCHEMAS:
        # Tipos desconocidos se permiten (para flexibilidad)
        return True, None
    
    schema = MESSAGE_SCHEMAS[msg_type]
    
    for field in schema['required']:
        if field not in mensaje:
            return False, f"Mensaje '{msg_type}' falta campo requerido: {field}"
    
    return True, None