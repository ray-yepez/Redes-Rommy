from enum import Enum

class MessageType(Enum):
    """Tipos de mensaje en el protocolo de red."""
    PING = "PING"
    PONG = "PONG"
    START_GAME = "START_GAME"
    SELECTION_UPDATE = "SELECTION_UPDATE"
    ELECTION_CARDS = "ELECTION_CARDS"
    ESTADO_CARTAS = "ESTADO_CARTAS"
    ORDEN_COMPLETO = "ORDEN_COMPLETO"
    BAJARSE = "BAJARSE"
    TOMAR_DESCARTE = "TOMAR_DESCARTE"
    TOMAR_CARTA = "TOMAR_CARTA"
    DESCARTE = "DESCARTE"
    COMPRAR_CARTA = "COMPRAR_CARTA"
    PLAYER_ORDER = "PLAYER_ORDER"
    UPDATE_PLAYERS = "UPDATE_PLAYERS"
    PASAR_DESCARTE = "PASAR_DESCARTE"
    INICIAR_COMPRA = "INICIAR_COMPRA"
    PASAR_COMPRA = "PASAR_COMPRA"
    REALIZAR_COMPRA = "REALIZAR_COMPRA"
    SWAP_JOKER = "SWAP_JOKER"
    SALIR = "SALIR"
    DESCONEXION = "DESCONEXION"
    INSERTAR_CARTA = "INSERTAR_CARTA"
    REQUEST_RESYNC = "REQUEST_RESYNC"
    DEV_HAND_SYNC = "DEV_HAND_SYNC"

class ConnectionStatus(Enum):
    """Estados de conexión."""
    CONNECTED = "CONNECTED"
    WRONG_PASSWORD = "WRONG_PASSWORD"
    FULL = "FULL"
    DISCONNECTED = "DISCONNECTED"

class ErrorCode(Enum):
    """Códigos de error para excepciones."""
    TIMEOUT = "TIMEOUT"
    CONNECTION_RESET = "CONNECTION_RESET"
    SOCKET_ERROR = "SOCKET_ERROR"
    AUTH_FAILED = "AUTH_FAILED"
    SERVER_FULL = "SERVER_FULL"
    NETWORK_UNREACHABLE = "NETWORK_UNREACHABLE"


# ── Protocol constants ────────────────────────────────────────────────────
# Header: [4 bytes payload length][4 bytes type_hash][2 bytes version]
HEADER_SIZE = 10
PROTOCOL_VERSION = 0

MESSAGE_SCHEMA = {
    # ── Control messages (strict validation) ──
    "PING":                {"required": ["type", "timestamp"],        "optional": []},
    "PONG":                {"required": ["type", "timestamp"],        "optional": []},
    "UPDATE_PLAYERS":      {"required": ["type", "players"],          "optional": []},
    "SALIR":               {"required": ["type"],                     "optional": ["playerId", "playerName"]},
    "DESCONEXION":         {"required": ["type"],                     "optional": ["playerId", "playerName", "reason"]},
    "NOTICE":              {"required": ["type", "mensaje"],          "optional": ["timestamp"]},
    "CHAT":                {"required": ["type", "mensaje"],          "optional": ["playerName", "notificar"]},
    "PLAYER_DISCONNECTED": {"required": ["type", "player_id"],        "optional": []},

    # ── Game action messages (permissive — only `type` is required) ──
    "START_GAME":          {"required": ["type"], "optional": []},
    "SELECTION_UPDATE":    {"required": ["type"], "optional": []},
    "ELECTION_CARDS":      {"required": ["type"], "optional": []},
    "ESTADO_CARTAS":       {"required": ["type"], "optional": []},
    "ORDEN_COMPLETO":      {"required": ["type"], "optional": []},
    "BAJARSE":             {"required": ["type"], "optional": []},
    "TOMAR_DESCARTE":      {"required": ["type"], "optional": []},
    "TOMAR_CARTA":         {"required": ["type"], "optional": []},
    "DESCARTE":            {"required": ["type"], "optional": []},
    "COMPRAR_CARTA":       {"required": ["type"], "optional": []},
    "PLAYER_ORDER":        {"required": ["type"], "optional": []},
    "PASAR_DESCARTE":      {"required": ["type"], "optional": []},
    "INICIAR_COMPRA":      {"required": ["type"], "optional": []},
    "PASAR_COMPRA":        {"required": ["type"], "optional": []},
    "REALIZAR_COMPRA":     {"required": ["type"], "optional": []},
    "SWAP_JOKER":          {"required": ["type"], "optional": []},
    "INSERTAR_CARTA":      {"required": ["type"], "optional": []},
    "REQUEST_RESYNC":      {"required": ["type"], "optional": []},
    "DEV_HAND_SYNC":       {"required": ["type"], "optional": []},
    "REVELAR_FALLO":       {"required": ["type"], "optional": []},
}
