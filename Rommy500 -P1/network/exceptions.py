from .constants import ErrorCode

class NetworkException(Exception):
    """Base para todas las excepciones de red."""
    def __init__(self, code: ErrorCode, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"[{code.value}] {message}")

class TimeoutException(NetworkException):
    """Socket timeout o timeout de espera de respuesta."""
    def __init__(self, message: str, player_id: int = None):
        super().__init__(ErrorCode.TIMEOUT, message, {"player_id": player_id})

class ConnectionResetException(NetworkException):
    """Conexión cerrada por el otro extremo."""
    def __init__(self, message: str, addr: tuple = None):
        super().__init__(ErrorCode.CONNECTION_RESET, message, {"address": addr})

class AuthenticationException(NetworkException):
    """Fallo de autenticación (contraseña incorrecta)."""
    def __init__(self, message: str = "Contraseña incorrecta"):
        super().__init__(ErrorCode.AUTH_FAILED, message)

class ServerFullException(NetworkException):
    """Servidor ha alcanzado máximo de jugadores."""
    def __init__(self, max_players: int):
        super().__init__(ErrorCode.SERVER_FULL, 
                        f"Servidor lleno ({max_players} jugadores)", 
                        {"max_players": max_players})
