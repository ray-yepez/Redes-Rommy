from dataclasses import dataclass

@dataclass
class NetworkConfig:
    """Configuración de red del servidor y cliente."""
    
    # Puertos
    TCP_PORT: int = 5555
    BROADCAST_PORT: int = 5554
    
    # Timeouts (segundos)
    SOCKET_TIMEOUT: int = 30
    HEALTH_CHECK_INTERVAL: int = 60
    PING_TIMEOUT: int = 5
    CONNECTION_TIMEOUT: int = 10
    
    # Reintentos
    MAX_RECV_RETRIES: int = 5
    RECONNECT_MAX_ATTEMPTS: int = 3
    RECONNECT_BASE_DELAY: float = 1.0  # segundos (escalado exponencial)
    
    # Buffers y límites
    BUFFER_SIZE: int = 8192
    MAX_MESSAGE_SIZE: int = 1_000_000  # 1MB límite
    
    # Comportamiento
    BROADCAST_INTERVAL: float = 3.0  # broadcast UDP cada 3 segundos
    ENABLE_DEBUG: bool = False
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR

# Instancia global (puede ser sobrescrita en tests)
DEFAULT_CONFIG = NetworkConfig()
