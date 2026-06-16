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


pass

MESSAGE_SCHEMA = {
    "START_GAME": {
        "required": ["type"],
        "fields": {"type": str}
    },
    "BAJARSE": {
        "required": ["type", "playerId", "playerHand", "jugadas_bajadas", "playMade", "round"],
        "fields": {
            "type": str,
            "playerId": int,
            "playerHand": list,
            "jugadas_bajadas": list,
            "playMade": list,
            "round": object
        }
    },
    "TOMAR_CARTA": {
        "required": ["type", "playerId", "playerHand", "cardTaken", "mazo", "round"],
        "fields": {
            "type": str,
            "playerId": int,
            "playerHand": list,
            "cardTaken": object,
            "mazo": list,
            "round": object
        }
    },
    "TOMAR_DESCARTE": {
        "required": ["type", "playerId", "playerHand", "cardTakenD", "mazo_descarte", "round"],
        "fields": {
            "type": str,
            "playerId": int,
            "playerHand": list,
            "cardTakenD": object,
            "mazo_descarte": list,
            "round": object
        }
    },
    "DESCARTE": {
        "required": ["type", "playerId", "playerHand", "cartas_descartadas", "mazo_descarte", "players", "deckForRound", "round"],
        "fields": {
            "type": str,
            "playerId": int,
            "playerHand": list,
            "cartas_descartadas": list,
            "mazo_descarte": list,
            "players": list,
            "deckForRound": list,
            "round": object
        }
    },
    "COMPRAR_CARTA": {
        "required": ["type", "playerId", "playerHand", "playerName", "mazo_descarte", "deckForRound", "round"],
        "fields": {
            "type": str,
            "playerId": int,
            "playerHand": list,
            "playerName": str,
            "mazo_descarte": list,
            "deckForRound": list,
            "round": object
        }
    },
    "INSERTAR_CARTA": {
        "required": ["type", "playerHand", "jugadas_bajadas", "playMade", "playerId", "playerId2", "round"],
        "fields": {
            "type": str,
            "playerHand": list,
            "jugadas_bajadas": list,
            "playMade": list,
            "playerId": int,
            "playerId2": int,
            "round": object
        }
    },
    "SWAP_JOKER": {
        "required": ["type", "playerId", "playMade", "jugadas_bajadas"],
        "fields": {
            "type": str,
            "playerId": int,
            "playMade": list,
            "jugadas_bajadas": list
        }
    },
    "PASAR_DESCARTE": {
        "required": ["type", "playerId", "playerName"],
        "fields": {"type": str, "playerId": int, "playerName": str}
    },
    "INICIAR_COMPRA": {
        "required": ["type", "playerId", "playerName", "players_for_buy_ids", "player_in_turn_id", "player_init_buy_id"],
        "fields": {
            "type": str,
            "playerId": int,
            "playerName": str,
            "players_for_buy_ids": list,
            "player_in_turn_id": int,
            "player_init_buy_id": int
        }
    },
    "PASAR_COMPRA": {
        "required": ["type", "playerId", "playerName", "current_buy_id", "list_confirm_ids"],
        "fields": {
            "type": str,
            "playerId": int,
            "playerName": str,
            "current_buy_id": int,
            "list_confirm_ids": list
        }
    },
    "REALIZAR_COMPRA": {
        "required": ["type", "playerId", "playerName"],
        "fields": {"type": str, "playerId": int, "playerName": str}
    },
    "PING": {
        "required": ["type", "timestamp"],
        "fields": {"type": str, "timestamp": float}
    },
    "PONG": {
        "required": ["type", "timestamp"],
        "fields": {"type": str, "timestamp": float}
    },
    "SALIR": {
        "required": ["type", "playerId", "playerName"],
        "fields": {"type": str, "playerId": int, "playerName": str}
    },
    "SELECTION_UPDATE": {
        "required": ["type", "cartas_eleccion"],
        "fields": {"type": str, "cartas_eleccion": list}
    },
    "PLAYER_ORDER": {
        "required": ["type", "players", "orden_str", "hands", "deckForRound", "mazo_descarte"],
        "fields": {
            "type": str,
            "players": list,
            "orden_str": str,
            "hands": dict,
            "deckForRound": list,
            "mazo_descarte": list
        }
    },
    "ELECTION_CARDS": {
        "required": ["type", "players", "election_cards"],
        "fields": {"type": str, "players": list, "election_cards": list}
    }
}

HEADER_SIZE = 10
PROTOCOL_VERSION = 1

