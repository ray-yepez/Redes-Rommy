from enum import Enum

class MessageType(str, Enum):
    """
    Catálogo de todos los tipos de mensajes posibles en el sistema de redes.
    Centraliza las cadenas para evitar typos o hardcodes en distintas partes del código.
    """
    
    # ── Conexión y Sesión ──
    NUEVO_JUGADOR = "NuevoJugador"
    NUEVO_JUGADOR_1 = "NuevoJugador1"  # Legado
    CLIENTE_DESCONECTADO = "ClienteDesconectado"
    JUGADOR_DESCONECTADO = "JugadorDesconectado"
    RECONECTAR = "Reconectar"
    RECONECTADO = "Reconectado"
    BIENVENIDO = "Bienvenido"
    NUEVA_CONEXION = "Nueva_Conexion"
    PARTIDA_INICIADA_ERROR = "PartidaIniciada"
    SALA_LLENA = "SalaLlena"
    
    # ── Discovery UDP ──
    RUMMY_SERVER = "RummyServer"
    
    # ── Estado de Partida ──
    MANO_INICIAL = "ManoInicial"
    TU_TURNO = "Tu_Turno"
    PASAR_TURNO = "Pasar_Turno"
    ACTUALIZAR_ETIQUETA_TURNO = "Actualizar_Etiqueta_Turno"
    MAZO_NUEVO = "Mazo_Nuevo"
    
    # ── Acciones de Juego ──
    DESCARTAR = "bajarse"
    DESCARTE_CARTA = "Descarte_Carta"
    TOMAR_CARTA_DESCARTE = "Tomar_Carta_Descarte"
    TOMAR_CARTA_MAZO = "Tomar_carta_mazo"
    MONO_QUEMADO = "mono_quemado"
    ACTUALIZAR_QUEMA_DESCARTE = "Actualizar_quema_descarte"
    ACTUALIZAR_MONO = "actualizar_mono"
    DESCARTAR_MONO = "descartar_mono"
    
    # ── Jugadas y Extensiones ──
    VALIDAR_SELECCION = "validar_seleccion"
    SELECCION_VALIDA = "seleccion_valida"
    SELECCION_CANCELADA = "Seleccion_cancelada"
    JUGADA_INVALIDA = "jugada_invalida"
    JUGADA_CANCELADA = "jugada_cancelada"
    CANCELAR_JUGADA = "cancelar_jugada"
    
    ELEGIR_POSICION_SEGUIDILLA = "elegir_posicion_seguidilla"
    ELEGIR_DONDE_EXTENDER = "elejir_donde_extender"  # Preservando typo original temporalmente
    EXTENDER_EN = "extender_en"
    ELECION_DONDE_EXTENDER = "elecion_donde_extender" # Preservando typo original
    SE_EXTENDIO = "se_extendio"
    MOSTRAR_EXTENDER = "mostrar_extender"
    
    REEMPLAZAR = "reemplazar"
    REEMPLAZAR_VALIDO = "reemplazar_valido"
    REEMPLAZARON_TU_JUGADA = "reemplazaron_tu_jugada"
    
    # ── Puntuaciones y Final ──
    PUNTUACIONES_JUGADORES = "puntuaciones_jugadores"
    NUEVA_RONDA = "nueva_ronda"
    FIN_PARTIDA = "fin_partida"
    REGRESANDO_MENU = "regresando_menu"
    
    # ── Misceláneos ──
    MENSAJE_SEGUIDILLAS_CONTINUAS = "mensaje_seguidillas_continuas"
