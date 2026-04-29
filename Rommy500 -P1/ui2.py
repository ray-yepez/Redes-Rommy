import pygame
import os
from network import NetworkManager
from Game import startRound#,
from Turn import drawCard, refillDeck
import time 
from Round import Round
from Deck import Deck
from Card import Card
import threading
import sys
from penalizaciones import ejecutar_penalizacion, esta_penalizado
from volumen import ControlVolumen
from validaciones_jugada import (
    adaptar_zonas_flexibles,
    preparar_seguidilla_extendida,
    resolver_campo_accion,
    validar_jugada_avanzada_por_tipo,
)

network_manager = None   #NetworkManager()
jugadores = []           #network_manager.connected_players
print(f"Jugadore ... {jugadores}")

pygame.init()

icon = pygame.image.load("assets/icon.png")  # Reemplaza con la ruta correcta a tu imagen
pygame.display.set_icon(icon)
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("RUMMY 500")


mensaje_orden = ""
tiempo_inicio_orden = 0

# ── Ordenamiento de mano ──────────────────────────────────────────────────────
modo_orden = "Sets"   # Alterna entre 'Sets' (Tríos) y 'Runs' (Escaleras)

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Rummy 500 - Layout Base")

# Cargar fondo
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")
fondo_path = os.path.join(ASSETS_PATH, "fondo_juego.png")
fondo_img = pygame.image.load(fondo_path).convert()
fondo_img = pygame.transform.scale(fondo_img, (WIDTH, HEIGHT))
# --- Iniciar fuente centralizada del juego ---
FONT_FILE = os.path.join(ASSETS_PATH, "PressStart2P-Regular.ttf")
_fonts_cache = {}
def get_game_font(size):
    """Devuelve pygame.font.Font cargada desde assets o SysFont si falla; cachea por tamaño."""
    if size in _fonts_cache:
        return _fonts_cache[size]
    try:
        if os.path.exists(FONT_FILE):
            f = pygame.font.Font(FONT_FILE, size)
        else:
            f = pygame.font.SysFont("arial", size)
    except Exception:
        f = pygame.font.SysFont("arial", size)
    _fonts_cache[size] = f
    return f
# Colores (con alpha para transparencia)
CAJA_JUG = (70, 130, 180, 60)   # Más transparente
CAJA_BAJ = (100, 200, 100, 60)
CENTRAL = (50, 50, 80, 60)
TEXTO = (255, 255, 255)
BORDER = (0, 0, 0, 180)

MIN_OVERLAP = 30

font = pygame.font.SysFont("arial", 16, bold=True)

# Proporciones relativas
bajada_h_pct = 0.125
bajada_w_pct = 0.083
jug_w_pct = 0.092
jug_h_pct = 0.137

# Diccionario para identificar cada caja
boxes = {}

cartas_apartadas = set()
cartas_ocultas = set()

zona_cartas_snapshot = None

mazo_descarte = []  # Lista para el mazo de descarte
mostrar_boton_descartar = False
mostrar_boton_bajarse = False
mostrar_boton_comprar = False

# guarda la última carta tomada y por quién (para impedir descartarla en el mismo turno)
last_taken_card = None
last_taken_player = None
#Cambio Boton Menu / Salir




def show_menu_modal(screen, WIDTH, HEIGHT, ASSETS_PATH):
    import pygame
    import os
    clock = pygame.time.Clock()
    img_reanudar = pygame.image.load(os.path.join(ASSETS_PATH, "reanudar.png")).convert_alpha()
    img_ajustes = pygame.image.load(os.path.join(ASSETS_PATH, "ajustes.png")).convert_alpha()
    img_salir = pygame.image.load(os.path.join(ASSETS_PATH, "salir.png")).convert_alpha()
    btn_w, btn_h = 220, 70
    img_reanudar = pygame.transform.smoothscale(img_reanudar, (btn_w, btn_h))
    img_ajustes = pygame.transform.smoothscale(img_ajustes, (btn_w, btn_h))
    img_salir = pygame.transform.smoothscale(img_salir, (btn_w, btn_h))
    try:
        background_snapshot = screen.copy()
    except Exception:
        background_snapshot = pygame.Surface((WIDTH, HEIGHT))
        background_snapshot.blit(screen, (0, 0))

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))

    w, h = 330, 300
    x = (WIDTH - w) // 2
    y = (HEIGHT - h) // 2
    modal_rect = pygame.Rect(x, y, w, h)
    padding = 16

    btn_w, btn_h = 220, 44
    espacio_vertical = 35
    inicio_y = y + 40
    btn_resume = pygame.Rect(x + (w - btn_w) // 2, inicio_y, btn_w, btn_h)
    btn_config = pygame.Rect(x + (w - btn_w) // 2, inicio_y + btn_h + espacio_vertical, btn_w, btn_h)
    btn_exit   = pygame.Rect(x + (w - btn_w) // 2, inicio_y + 2 * (btn_h + espacio_vertical), btn_w, btn_h)
    font_path = os.path.join(ASSETS_PATH, "PressStart2P-Regular.ttf")
    title_font = pygame.font.Font(font_path, 16)

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return "exit"
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return "resume"
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                if btn_resume.collidepoint(mx, my):
                    return "resume"
                if btn_config.collidepoint(mx, my):
                    return "config"
                if btn_exit.collidepoint(mx, my):
                    pygame.quit()

        if pygame.display.get_init():
            screen.blit(background_snapshot, (0, 0))
            screen.blit(overlay, (0, 0))

            pygame.draw.rect(screen, (40, 40, 40), modal_rect, border_radius=12)
            pygame.draw.rect(screen, (150, 150, 150), modal_rect, 2, border_radius=12)

            title = title_font.render("Menú de Pausa", True, (230, 230, 230))
            screen.blit(title, (x + padding + 50, y + padding))

            screen.blit(img_reanudar, btn_resume.topleft)
            screen.blit(img_ajustes, btn_config.topleft)
            screen.blit(img_salir, btn_exit.topleft)
            pygame.display.flip()
            clock.tick(60)
        else:
            return "exit"
#Cambio Boton Menu / Salir

def register_taken_card(player, card):
    global last_taken_card, last_taken_player
    last_taken_card = card
    last_taken_player = player

def clear_taken_card_for_player(player):
    global last_taken_card, last_taken_player
    if last_taken_player is not player:
        last_taken_card = None
        last_taken_player = None

def can_discard(player, cards):
    # devuelve False si el jugador intentara descartar la carta que tomó este turno
    global last_taken_card, last_taken_player
    # si no es el mismo jugador o no hay carta registrada, permitir
    if last_taken_player is not player or last_taken_card is None:
        return True

    # normaliza a lista
    if isinstance(cards, (list, tuple, set)):
        items = list(cards)
    else:
        items = [cards]

    for c in items:
        # compara por identidad primero, luego por igualdad de string/valor
        try:
            if (c is last_taken_card or c == last_taken_card) and len(items) >= 1:
                return False
        except Exception:
            if str(c) == str(last_taken_card):
                return False
    return True

# ---------------------- Helpers robustos para UI ----------------------
from Card import Card

def string_to_card(card_string_or_object):
    """
    Si recibe string como 'A♥' o 'Joker', devuelve Card(...).
    Si recibe lista con strings, intenta convertir cada elemento.
    Si recibe ya un Card, lo devuelve.
    """
    if isinstance(card_string_or_object, Card):
        return card_string_or_object
    if isinstance(card_string_or_object, list):
        # retorna lista de Card o lista original si ya son Card
        return [string_to_card(c) for c in card_string_or_object]
    if not isinstance(card_string_or_object, str):
        return card_string_or_object

    # es str
    if card_string_or_object == "Joker":
        return Card("Joker", "", joker=True)
    # valor == todo menos último char, palo == último char
    value = card_string_or_object[:-1]
    suit = card_string_or_object[-1]
    
    return Card(value, suit)

def resolve_play(jugador, raw_play, play_index=None):
    """
    raw_play puede ser:
      - una lista de Card (ok) -> devuelve la misma lista
      - una lista de str -> si jugador tiene 'jugadas_bajadas' usa esa para resolver
      - un dict -> devolver dict convertida con Card objects
    Devuelve la estructura con cartas como objetos Card (no strings). Si no puede resolver,
    devuelve None.
    """
    # caso ya resuelto
    if isinstance(raw_play, dict):
        resolved = {}
        if "trio" in raw_play and raw_play["trio"]:
            resolved["trio"] = [string_to_card(c) for c in raw_play["trio"]]
        if "straight" in raw_play and raw_play["straight"]:
            resolved["straight"] = [string_to_card(c) for c in raw_play["straight"]]
        return resolved

    if isinstance(raw_play, list) and raw_play and isinstance(raw_play[0], str):
        # busca en jugadas_bajadas si existe
        if hasattr(jugador, "jugadas_bajadas") and play_index is not None and len(jugador.jugadas_bajadas) > play_index:
            return jugador.jugadas_bajadas[play_index]
        # no hay resolved, intentar convertir strings a Card
        try:
            return [string_to_card(s) for s in raw_play]
        except Exception:
            return None

    # si es lista de Card o mezcla:
    if isinstance(raw_play, list):
        return [string_to_card(c) for c in raw_play]

    # fallback
    return raw_play
# --------------------------------------------------------------------


# Nueva función: valida tipos y llama insertCard solo si todo está correcto
def safe_insert_card(jugador, target_player, idx_jugada, card_to_insert, position, target_subtype=None,joker_index=None):
    """
    Valida tipos y que la jugada objetivo tenga objetos Card.
    target_subtype: "trio" | "straight" | None (None -> intenta inferir)
    """
    from Card import Card
    objeto_carta = string_to_card(card_to_insert)
    print(f"Objeto de carta: {objeto_carta}")
    print(f"String de carta: {card_to_insert}")
    # normaliza carta
    if not isinstance(card_to_insert, Card):
        print("safe_insert_card: card_to_insert NO es Card:", type(card_to_insert), repr(card_to_insert))
        return False

    plays = getattr(target_player, "playMade", [])
    if idx_jugada < 0 or idx_jugada >= len(plays):
        print("safe_insert_card: idx_jugada fuera de rango:", idx_jugada, "len(playMade)=", len(plays))
        return False

    target_play = plays[idx_jugada]

    # si target_play es dict, elegimos la sublista correcta
    if isinstance(target_play, dict):
        if target_subtype == "trio":
            cartas_jugada = target_play.get("trio", [])
        elif target_subtype == "straight":
            cartas_jugada = target_play.get("straight", [])
        else:
            # intentar inferir: preferir straight si existe no vacío
            cartas_jugada = target_play.get("straight") or target_play.get("trio") or []
    else:
        cartas_jugada = target_play or []

    # Validar que cartas_jugada sean objetos Card
    for c in cartas_jugada:
        string_to_card(c)
        if not isinstance(c, Card):
            print("safe_insert_card: elemento en la jugada objetivo NO es Card:", type(c), repr(c))
            print("target_player.playMade[{}] = {}".format(idx_jugada, target_play))
            return False

    # Todo bien: llamar al método real. Importante: aquí llamamos con idx_jugada (índice en playMade).
    try:
        # Si tu Player.insertCard espera trabajar con dict y asume 'straight' por defecto,
        # esto funcionará. Si insertCard necesita un subtype explícito, habría que pasarlo.
        result  = jugador.insertCard(
            targetPlayer=target_player, 
            targetPlayIndex=idx_jugada, 
            cardToInsert=card_to_insert, 
            position=position, 
            jokerIndex=joker_index
        )
        if result:
            return True
        else:
            return False
    except Exception as e:
        print("safe_insert_card: excepción al llamar insertCard:", e)
        return False

def render_text_with_border(text, font, color, border_color, pos, surface):
    # Dibuja el texto en 8 posiciones alrededor (borde)
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
        border = font.render(text, True, border_color)
        surface.blit(border, (pos[0]+dx, pos[1]+dy))
    # Dibuja el texto principal encima
    txt = font.render(text, True, color)
    surface.blit(txt, pos)

def draw_transparent_rect(surface, color, rect, border=1):
    temp_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    temp_surface.fill(color)
    surface.blit(temp_surface, (rect.x, rect.y))
    pygame.draw.rect(surface, BORDER, rect, border)

def draw_label(rect, text):
    label = font.render(text, True, TEXTO)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)

def get_clicked_box(mouse_pos, cuadros):
    """
    Retorna el nombre del cuadro clickeado o None si no se clickeó ninguno.
    Si hay solapamiento (como en las cartas), prioriza la carta más a la derecha (la que está encima).
    """
    # Recorre los cuadros en orden inverso para que la última carta (más a la derecha) tenga prioridad
    for nombre, rect in reversed(list(cuadros.items())):
        if rect.collidepoint(mouse_pos):
            return nombre
                
    return None

def get_card_image(card):
    """
    Devuelve la imagen pygame de la carta según su string (por ejemplo, '2♣.png').
    Si es Joker, busca JokerV2.png.
    Si no existe, devuelve una imagen de carta genérica.
    """
    if hasattr(card, "joker") and card.joker:
        nombre = "JokerV2.png"
    else:
        nombre = str(card) + ".png"
    ruta = os.path.join(ASSETS_PATH, "cartas", nombre)
    if os.path.exists(ruta):
        return pygame.image.load(ruta).convert_alpha()
    else:
        # Imagen genérica si no existe la carta
        generic_path = os.path.join(ASSETS_PATH, "cartas", "back.png")
        if os.path.exists(generic_path):
            return pygame.image.load(generic_path).convert_alpha()
        else:
            # Si tampoco existe back.png, crea una carta vacía
            img = pygame.Surface((60, 90), pygame.SRCALPHA)
            pygame.draw.rect(img, (200, 200, 200), img.get_rect(), border_radius=8)
            return img

#CAMBIO 1
# --- Añadir en ui2.py (zona de utilidades/UI) ---
def draw_simple_button(surface, rect, text, font, bg=(70,70,70), fg=(255,255,255)):
    pygame.draw.rect(surface, bg, rect, border_radius=8)
    pygame.draw.rect(surface, (180,180,180), rect, 2, border_radius=8)
    txt = font.render(text, True, fg)
    tr = txt.get_rect(center=rect.center)
    surface.blit(txt, tr)


#COMPRAR CARTA

def confirm_buy_card(screen, card, WIDTH, HEIGHT, ASSETS_PATH, font):
    #def confirm_replace_joker(screen, WIDTH, HEIGHT, ASSETS_PATH):
    """
    Muestra una ventana modal que pregunta si el jugador quiere comprar la carta.
    - card: objeto Card (puede ser None para mostrar reverso).
    - Devuelve True si pulsa SI, False si pulsa NO o cierra.
    Bloqueante: procesa su propio loop hasta respuesta.
    """
    clock = pygame.time.Clock()
    # Captura del fondo actual para mostrarlo detrás del modal (asegura transparencia visual)
    try:
        background_snapshot = screen.copy()
    except Exception:
        background_snapshot = pygame.Surface((WIDTH, HEIGHT))
        background_snapshot.blit(screen, (0, 0))

    # Overlay semi-transparente (creado una vez)
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))  # ajuste alpha aquí (0=totalmente transparente, 255=opaco)


    #Cambio 3 (Tamaño del Rectángulo de 420,240 a 330,320)
    # Tamaños y rects
    w, h = 330, 320
    #Cambio 3

    x = (WIDTH - w)//2
    y = (HEIGHT - h)//2
    modal_rect = pygame.Rect(x, y, w, h)
    padding = 16


    #Cambio 4 (Centrar Carta)
    # Rect para imagen de carta
    card_w, card_h = 100, 150
    card_rect = pygame.Rect(x + (w - card_w)//2, y + (h - card_h)//2, card_w, card_h)
    #Cambio 4


    # Botones SI / NO
    btn_w, btn_h = 120, 44
    btn_yes = pygame.Rect(x + w - padding - btn_w, y + h - padding - btn_h, btn_w, btn_h)
    btn_no = pygame.Rect(x + w - padding - 2*btn_w - 12, y + h - padding - btn_h, btn_w, btn_h)

    # Preparar imagen de carta (usar get_card_image existente)
    try:
        if card is None:
            card_img = get_card_image("back")
        else:
            card_img = get_card_image(card)
    except Exception:
        card_img = pygame.Surface((card_w, card_h))
        card_img.fill((200,200,200))
    card_img = pygame.transform.smoothscale(card_img, (card_w, card_h))

    #Cambio 5 (Tipografía)
    #Descartamos: title_font = pygame.font.SysFont("arial", 20, bold=True)
    font_path = os.path.join(ASSETS_PATH, "PressStart2P-Regular.ttf")
    title_font = pygame.font.Font(font_path, 16)
    info_font = pygame.font.Font(font_path, 12)
    #Cambio 5


    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return False
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                if btn_yes.collidepoint(mx, my):
                    return True
                if btn_no.collidepoint(mx, my):
                    return False

        # Dibujo del modal: primero el fondo capturado, luego overlay semi-transparente
        screen.blit(background_snapshot, (0, 0))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, (40,40,40), modal_rect, border_radius=12)
        pygame.draw.rect(screen, (150,150,150), modal_rect, 2, border_radius=12)

        # Texto
        title = title_font.render("Comprar carta", True, (230,230,230))
        screen.blit(title, (x + padding, y + padding))

        
        #Cambio 6 (Separar Texto)
        info = info_font.render("¿Deseas comprar esta carta", True, (200,200,200))
        screen.blit(info, (x + padding, y + padding + 30))
        info2 = info_font.render("del descarte?", True, (200,200,200))
        screen.blit(info2, (x + padding, y + padding + 50))
        #Cambio 6


        # Dibuja la carta
        screen.blit(card_img, card_rect.topleft)
        # Mostrar nombre de carta debajo
        name_txt = info_font.render(str(card) if card is not None else "?", True, (230,230,230))
        nt = name_txt.get_rect(midtop=(card_rect.centerx, card_rect.bottom + 6))
        screen.blit(name_txt, nt)

        # Botones
        draw_simple_button(screen, btn_no, "No", info_font, bg=(120,40,40))
        draw_simple_button(screen, btn_yes, "Si", info_font, bg=(40,120,40))

        pygame.display.flip()
        clock.tick(60)
#COMPRAR CARTA'''




#CambioJoker #WhySoSerious

def confirm_joker(screen, card, WIDTH, HEIGHT, ASSETS_PATH, font):
    #def confirm_replace_joker(screen, WIDTH, HEIGHT, ASSETS_PATH):
    """
    Muestra una ventana modal que pregunta si el jugador quiere comprar la carta.
    - card: objeto Card (puede ser None para mostrar reverso).
    - font: pygame.font.Font ya creado para renderizar texto.
    Devuelve True si pulsa Si, False si pulsa No o cierra.
    Bloqueante: procesa su propio loop hasta respuesta.
    """
    clock = pygame.time.Clock()
    try:
        background_snapshot = screen.copy()
    except Exception:
        background_snapshot = pygame.Surface((WIDTH, HEIGHT))
        background_snapshot.blit(screen, (0, 0))

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))

    w, h = 330, 370
    x = (WIDTH - w)//2
    y = (HEIGHT - h)//2
    modal_rect = pygame.Rect(x, y, w, h)
    padding = 16

    card_w, card_h = 100, 150
    card_rect = pygame.Rect(x + (w - card_w)//2, y + (h - card_h)//2, card_w, card_h)

    btn_w, btn_h = 140, 44
    btn_replace = pygame.Rect(x + w - padding - btn_w, y + h - padding - btn_h, btn_w, btn_h)
    btn_continue = pygame.Rect(x + w - padding - 2*btn_w - 12, y + h - padding - btn_h, btn_w, btn_h)

    # Mostrar siempre la imagen del Joker
    try:
        card_img = get_card_image(Card("Joker", "", joker=True))
    except Exception:
        card_img = pygame.Surface((card_w, card_h))
        card_img.fill((200,200,200))
    card_img = pygame.transform.smoothscale(card_img, (card_w, card_h))
    font_path = os.path.join(ASSETS_PATH, "PressStart2P-Regular.ttf")
    title_font = pygame.font.Font(font_path, 16)
    info_font = pygame.font.Font(font_path, 12)

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return False
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                if btn_replace.collidepoint(mx, my):
                    return True
                if btn_continue.collidepoint(mx, my):
                    return False

        screen.blit(background_snapshot, (0, 0))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, (40,40,40), modal_rect, border_radius=12)
        pygame.draw.rect(screen, (150,150,150), modal_rect, 2, border_radius=12)

        title = title_font.render("Jugada con Joker", True, (230,230,230))
        screen.blit(title, (x + padding, y + padding))

        info1 = info_font.render("¿Deseas continuar la", True, (200,200,200))
        info2 = info_font.render("secuencia o reemplazar", True, (200,200,200))
        info3 = info_font.render("al Joker?", True, (200,200,200))
        screen.blit(info1, (x + padding, y + padding + 30))
        screen.blit(info2, (x + padding, y + padding + 50))
        screen.blit(info3, (x + padding, y + padding + 70))

        screen.blit(card_img, card_rect.topleft)
        name_txt = info_font.render("Joker", True, (230,230,230))
        nt = name_txt.get_rect(midtop=(card_rect.centerx, card_rect.bottom + 6))
        screen.blit(name_txt, nt)

        draw_simple_button(screen, btn_continue, "Seguir", info_font, bg=(120,40,40))
        draw_simple_button(screen, btn_replace, "Reemplazar", info_font, bg=(40,120,40))

        pygame.display.flip()
        clock.tick(60)
#CambioJoker #WhySoSerious
    
#CAMBIO 1 

def draw_player_hand(player, rect, cuadros_interactivos=None, cartas_ref=None, ocultas=None):
    """
    Dibuja la mano del jugador alineada horizontalmente, solapada, sin curva ni inclinación.
    """
    hand = getattr(player, "playerHand", [])
    n = len(hand)
    if n == 0:
        return

    card_height = rect.height - 6
    card_width = int(card_height * 0.68)

    # Solapamiento horizontal
    if n > 1:
        base_sep = int(card_width * 1.25)
        min_sep = int(card_width * 0.65)
        if n <= 6:
            solapamiento = base_sep
        elif n >= 12:
            solapamiento = min_sep
        else:
            solapamiento = int(base_sep - (base_sep - min_sep) * (n - 6) / 6)
        total_width = card_width + (n - 1) * solapamiento
        if total_width > rect.width:
            solapamiento = max(8, (rect.width - card_width) // (n - 1))
        start_x = rect.x + (rect.width - (card_width + (n - 1) * solapamiento)) // 2
    else:
        solapamiento = 0
        start_x = rect.x + (rect.width - card_width) // 2

    y_base = rect.y + 18  # Puedes ajustar este valor si quieres subir/bajar las cartas

    for i in range(n):
        if ocultas and i in ocultas:
            continue
        card = hand[i]
        string_to_card(card)
        img = get_card_image(card)
        img = pygame.transform.smoothscale(img, (card_width, card_height))
        # Sin curva ni inclinación
        img_rect = img.get_rect(topleft=(start_x + i * solapamiento, y_base))
        screen.blit(img, img_rect.topleft)

        if cuadros_interactivos is not None:
            cuadros_interactivos[f"Carta_{i}"] = img_rect
        if cartas_ref is not None:
            cartas_ref[f"Carta_{i}"] = card

def draw_vertical_back_hand(player, rect):
    """
    Dibuja cartas boca abajo en vertical, tipo lluvia, según la cantidad real de cartas del jugador.
    """
    n = len(getattr(player, "playerHand", []))
    if n == 0:
        return

    # Tamaño de carta
    card_width = rect.width - 8
    card_height = int(card_width / 0.68)
    if card_height > rect.height // 2:
        card_height = rect.height // 2
        card_width = int(card_height * 0.68)

    # Solapamiento vertical
    if n > 1:
        solapamiento = (rect.height - card_height) // (n - 1)
        if solapamiento > card_height * 0.7:
            solapamiento = int(card_height * 0.7)
    else:
        solapamiento = 0

    start_y = rect.y + rect.height - card_height - (n - 1) * solapamiento

    # Imagen de reverso
    back_img = get_card_image("back")

    for i in range(n):
        img = pygame.transform.smoothscale(back_img, (card_width, card_height))
        card_rect = pygame.Rect(rect.x + (rect.width - card_width) // 2,
                                start_y + i * solapamiento,
                                card_width, card_height)
        screen.blit(img, card_rect.topleft)

def draw_back_cards_by_count(count, rect):
    """
    Dibuja 'count' cartas boca abajo en vertical (tipo lluvia) en el rectángulo dado.
    """
    if count == 0:
        return

    # Tamaño de carta
    card_width = rect.width - 8
    card_height = int(card_width / 0.68)
    if card_height > rect.height // 2:
        card_height = rect.height // 2
        card_width = int(card_height * 0.68)

    # Solapamiento vertical
    if count > 1:
        solapamiento = (rect.height - card_height) // (count - 1)
        if solapamiento > card_height * 0.7:
            solapamiento = int(card_height * 0.7)
    else:
        solapamiento = 0

    start_y = rect.y + rect.height - card_height - (count - 1) * solapamiento

    # Imagen de reverso
    back_img = get_card_image("back")

    for i in range(count):
        img = pygame.transform.smoothscale(back_img, (card_width, card_height))
        card_rect = pygame.Rect(rect.x + (rect.width - card_width) // 2,
                                start_y + i * solapamiento,
                                card_width, card_height)
        screen.blit(img, card_rect.topleft)

def draw_horizontal_pt_hand(player, rect):
    """
    Dibuja cartas horizontales usando PT.png, según la cantidad real de cartas del jugador.
    """
    n = len(getattr(player, "playerHand", []))
    if n == 0:
        return

    # Tamaño de carta
    card_height = rect.height - 8
    card_width = int(card_height * 0.68)
    if n > 1:
        max_width = rect.width - 8
        solapamiento = (max_width - card_width) // (n - 1)
        if solapamiento > card_width * 0.7:
            solapamiento = int(card_width * 0.7)
    else:
        solapamiento = 0

    start_x = rect.x
    y = rect.y + (rect.height - card_height) // 2

    # Imagen PT.png
    pt_img_path = os.path.join(ASSETS_PATH, "cartas", "PT.png")
    if os.path.exists(pt_img_path):
        pt_img = pygame.image.load(pt_img_path).convert_alpha()
    else:
        pt_img = get_card_image("back")

    for i in range(n):
        img = pygame.transform.smoothscale(pt_img, (card_width, card_height))
        card_rect = pygame.Rect(start_x + i * solapamiento, y, card_width, card_height)
        screen.blit(img, card_rect.topleft)

def draw_vertical_pt_hand(player, rect):
    """
    Dibuja cartas verticales usando PT.png, según la cantidad real de cartas del jugador.
    """
    n = len(getattr(player, "playerHand", []))
    if n == 0:
        return

    # Tamaño de carta
    card_width = rect.width - 8
    card_height = int(card_width / 0.68)
    if n > 1:
        max_height = rect.height - 8
        solapamiento = (max_height - card_height) // (n - 1)
        if solapamiento > card_height * 0.7:
            solapamiento = int(card_height * 0.7)
    else:
        solapamiento = 0

    x = rect.x + (rect.width - card_width) // 2
    start_y = rect.y

    # Imagen PT.png
    pt_img_path = os.path.join(ASSETS_PATH, "cartas", "PT.png")
    if os.path.exists(pt_img_path):
        pt_img = pygame.image.load(pt_img_path).convert_alpha()
    else:
        pt_img = get_card_image("back")

    for i in range(n):
        img = pygame.transform.smoothscale(pt_img, (card_width, card_height))
        card_rect = pygame.Rect(x, start_y + i * solapamiento, card_width, card_height)
        screen.blit(img, card_rect.topleft)

def draw_horizontal_rain_hand_rotated(player, rect):
    """
    Dibuja cartas en modo 'lluvia horizontal' pero verticalmente (cartas apiladas horizontalmente, rotadas 90 grados).
    El ancho de la carta es igual al de las cartas superiores y el ALTO (largo real de la carta) es más fino.
    """
    n = len(getattr(player, "playerHand", []))
    if n == 0:
        return

    # MISMO ancho que las cartas superiores, pero más finas (menos alto)
    card_width = 120   # igual que cuadro_w_carta
    card_height = 120  # más fino que las superiores (antes era 188)

    if n > 1:
        max_height = rect.height - 8
        solapamiento = (max_height - card_height) // (n - 1)
        if solapamiento > card_height * 0.7:
            solapamiento = int(card_height * 0.7)
        if solapamiento < 0:
            solapamiento = 0
    else:
        solapamiento = 0

    x = rect.x + (rect.width - card_height) // 2
    start_y = rect.y

    pt_img_path = os.path.join(ASSETS_PATH, "cartas", "PT.png")
    if os.path.exists(pt_img_path):
        pt_img = pygame.image.load(pt_img_path).convert_alpha()
    else:
        pt_img = get_card_image("back")

    for i in range(n):
        img = pygame.transform.smoothscale(pt_img, (card_height, card_width))
        img = pygame.transform.rotate(img, 90)
        card_rect = pygame.Rect(x, start_y + i * solapamiento, card_width, card_height)
        # No dibujar si se sale del recuadro
        if card_rect.bottom <= rect.bottom:
            screen.blit(img, card_rect.topleft)

def update_descartar_visibility(zona_cartas, roundThree, roundFour):
    """
    Botón 'Descartar':
    - Rondas 1/2 → visible si zona_cartas[2] tiene al menos 1 carta.
    - Rondas 3/4 → visible si zona_cartas[3] tiene al menos 1 carta.
    """
    global mostrar_boton_descartar

    try:
        if zona_cartas is None:
            mostrar_boton_descartar = False
            return

        if roundThree or roundFour:
            # revisar zona 3
            mostrar_boton_descartar = len(zona_cartas) > 3 and len(zona_cartas[3]) > 0
        else:
            # revisar zona 2
            mostrar_boton_descartar = len(zona_cartas) > 2 and len(zona_cartas[2]) > 0

    except Exception:
        mostrar_boton_descartar = False
def update_bajarse_visibility(zona_cartas, roundThree, roundFour):
    """
    Reglas:
    - En rondas 1/2 → zonas 0 y 1 deben tener al menos 1 carta.
    - En rondas 3/4 → zonas 0, 1 y 2 deben tener al menos 1 carta.
    """
    global mostrar_boton_bajarse
    try:
        # Validar existencia de zona_cartas
        if 'zona_cartas' not in globals() or zona_cartas is None:
            mostrar_boton_bajarse = False
            return

        # Rondas 3 o 4 → revisar zonas 0,1,2
        if roundThree or roundFour:
            if len(zona_cartas) > 2:
                mostrar_boton_bajarse = (
                    len(zona_cartas[0]) > 0 and
                    len(zona_cartas[1]) > 0 and
                    len(zona_cartas[2]) > 0
                )
            else:
                mostrar_boton_bajarse = False
            return

        # Rondas 1 o 2 → solo revisar zonas 0 y 1
        if len(zona_cartas) > 1:
            mostrar_boton_bajarse = (
                len(zona_cartas[0]) > 0 and
                len(zona_cartas[1]) > 0
            )
        else:
            mostrar_boton_bajarse = False

    except Exception:
        mostrar_boton_bajarse = False
def update_comprar_visibility():
    """
    El botón 'Comprar carta' será visible solo mientras:
    1. La flag mostrar_boton_comprar sea True
    2. El jugador NO sea quien descartó la carta del tope
    3. El jugador NO sea la mano actual
    """
    global mostrar_boton_comprar, mazo_descarte, jugador_local
    
    # Si ya es False, no hacemos nada
    if not mostrar_boton_comprar:
        return
    
    # Aplicar restricciones: si no hay cartas, si es mano, o si es su propio descarte
    if not mazo_descarte:
        mostrar_boton_comprar = False
    elif jugador_local.isHand:
        mostrar_boton_comprar = False
    elif getattr(mazo_descarte[-1], "discarded_by", None) == jugador_local.playerId:
        mostrar_boton_comprar = False
    
    return True


def main(manager_de_red): # <-- Acepta el manager de red
    global mostrar_boton_comprar
    global screen, WIDTH, HEIGHT, fondo_img, organizar_habilitado, fase
    global network_manager, jugadores , players, cartas_eleccion
    global cuadros_interactivos, cartas_ref, zona_cartas, visual_hand
    global dragging, carta_arrastrada, drag_rect, drag_offset_x, cartas_congeladas
    global cartas_ocultas, organizar_habilitado, mensaje_temporal, mensaje_tiempo
    global fase_fin_tiempo, mazo_descarte, deckForRound, round
    global mostrar_joker_fondo, tiempo_joker_fondo
    global player1   #NUEVO PARA PRUEBA
    global jugador_local  #NUEVO PARA PRUEBA Reeplazo de player1 :'(
    global siguiente_jugador_local
    global modo_orden   # ── Modo de ordenamiento de la mano ('Sets' / 'Runs')

    global ronudOne, roundTwo   # Para prueba
    # En ui2.py dentro de main()
    dragging_board_joker = False
    board_joker_data = None # Guardará { 'player': p, 'play_index': i, 'card': c, 'original_rect': r }
    just_went_down_this_turn = False  # Indica si se bajó en este turno
    jokers_insertados_este_turno = [] # para saber donde insertamos cartas
    last_inserted_card_data = None    # Guarda info para deshacer inserción: {'target_id': id, 'play_index': int, 'card': Card}
    roundOne =True
    roundTwo = False
    roundThree = False
    roundFour = False

    pygame.mixer.init()
    inicio_sound_path = os.path.join(os.path.dirname(__file__), "assets", "sonido", "inicio.wav")
    inicio_sound = pygame.mixer.Sound(inicio_sound_path)
    inicio_sound.play()

    # Asignar toda la informacion del manager de red de ui.py
    network_manager = manager_de_red 
    
    # Obtener los datos compartidos
    # jugadores n -> conn, addr, name, id
    jugadores = network_manager.connected_players
    
    from Card import Card
    from Player import Player

    # NUEVA INICIALIZACIÓN PARA EL JUGADOR
    players = []         # Lista de jugadores (vacía hasta que la reciba del host)
    cartas_eleccion = [] # Lista de cartas de elección (vacía hasta que la reciba del host)
    player1 = None # NUEVO PARA PRUEBA
    
    if network_manager.is_host:
        players = []
        print(f" puerto del servidor {jugadores[0][1][1]}")
        print(f" id del servidor {jugadores[0][3]}")
        host_id = jugadores[0][3]
        host_port = jugadores[0][1][1]
        # --- Jugador 1 ---
        player1 = Player(host_id, network_manager.playerName)

        players.append(player1)
        jugador_local = player1  # NUEVO PARA PRUEBA

        for jugador_info in network_manager.connected_players[1:]:
            # Obtener la IP del jugador
            jugador_id = jugador_info[3]
            jugador_name = jugador_info[2]
            player_cliente = Player( jugador_id, str(jugador_name)) 
            # Asignando mano inicial a los jugadores... Preguntar a Louis por la función
            players.append(player_cliente)

        print(f"Jugadores creados: {len(players)}")
        for p in players:
            print(f"Id: {p.playerId} --> Nombre:{p.playerName} ") 
        fase = "eleccion"        
    else:
        # El Jugador va directo a la fase de eleccion
        jugador_local = None  # NUEVO PARA PRUEBA
        fase = "eleccion"
    
    #from test3 import players
    running = True

    cuadros_interactivos = {}
    cartas_ref = {}

    zona_cartas = [[], [], [], []]  # [0]=segunda casilla, [1]=primera casilla, [2]=tercera casilla o descarte  ///o cuando son 4 [0]=segunda casilla, [1]=primera casilla, [2]=tercera casilla, [3]=cuarta casilla o descarte

    # Crea un set para ids de cartas "congeladas"
    cartas_congeladas = set()

    # Variables para el arrastre visual
    dragging = False
    carta_arrastrada = None
    drag_rect = None
    drag_offset_x = 0

    cartas_ocultas = set()  # Al inicio de main()
    organizar_habilitado = True  # Inicializa la variable

    # Variables temporales:
    mensaje_temporal = ""
    mensaje_tiempo = 0

    fase_fin_tiempo = 0  # Para controlar cuánto tiempo mostrar la pantalla final
           
    # --- CARTAS DE ELECCIÓN ---
    if network_manager.is_host:
        # El host genera las cartas de elección
        deck = Deck()
        cartas_eleccion = deck.drawInElectionPhase(len(players))
        visual_hand = list(player1.playerHand)  # Copia inicial para el orden visual
        # Asigna un id único a cada carta de la mano visual
        for idx, carta in enumerate(visual_hand):
            if not hasattr(carta, "id_visual"):
                carta.id_visual = id(carta)  # O usa idx para algo más simple

        msgEleccion = {
                    "type": "ELECTION_CARDS",
                    "players": players,
                    "election_cards": cartas_eleccion
                    }
        print(f"Transmitiendo lista de jugadores.................")
        recalcular_posiciones_eleccion(cartas_eleccion, WIDTH, HEIGHT)
        network_manager.broadcast_message(msgEleccion) 
        fase = "eleccion"
    
    # Cargar sonido de carta
    carta_sound_path = os.path.join(ASSETS_PATH, "sonido", "carta.wav")
    carta_sound = pygame.mixer.Sound(carta_sound_path)

    # Cargar sonido de bajarse
    bajarse_sound_path = os.path.join(ASSETS_PATH, "sonido", "bajarse.wav")
    bajarse_sound = pygame.mixer.Sound(bajarse_sound_path)

    #contJugador = 0
    #contHost = 0

    # Variables para manejar el ciclo de compra. 
    noBuy = True                # Indica que no hay compras activas.
    bought = False              # Indica que ya hubo ciclo de compras en el turno actual.
    waiting = False             # Indica que el MANO esta esperando alguna decision de compra.
    time_waiting = None         # Variable para manejar el tiempo de espera.
    players_for_buy_ids = []    # Variable para guardar a todos los ID de los jugadores que pueden comprar, una vez activado el inicio de una compra.
    player_in_turn_id = None    # Variable para guardar el ID del jugador en turno de compra
    player_init_buy_id = None   # Variable que guarda el ID del jugador que inicio el ciclo de compra.
    buy_finished = False        # Var. para indicar que el ciclo de compra ha finalizado (con mas de 2 jugadores).
    time_confirm = None         # Variable para manejar el tiempo de espera por mensajes tardios en ciclo de compra.
    list_confirm_ids = []       # Lista para almacenar jugadores que ya tuvieron su turno de compra.

    ctrl_volumen = ControlVolumen(x=1025, y=80)

    # ── Botón de ordenamiento de mano ─────────────────────────────────────────
    # Posición: esquina inferior derecha, por encima de la zona de cartas.
    # Ajusta x, y, w, h según tu layout si es necesario.
    btn_ordenar = pygame.Rect(WIDTH - 190, HEIGHT - 160, 170, 40)

    while running:
        # --- SOLO FASE DE ELECCIÓN ---
        update_descartar_visibility(zona_cartas, roundThree, roundFour)
        update_comprar_visibility()
        update_bajarse_visibility(zona_cartas, roundThree, roundFour)
        if fase == "eleccion":
            screen.blit(fondo_img, (0, 0))  # Nuevo pero se puede quedar :)

            # Procesando mensaje con datos de seleccion de cartas y la lista de jugadores...
            if not network_manager.is_host:
                # Recuperar los mensajes recibidos del buffer de red
                if roundOne:
                    msg = network_manager.get_game_state() 
                    # Verificar si el mensaje contiene los datos esperados
                    if isinstance(msg, dict) and msg.get("type") == "ELECTION_CARDS":
                        print(f"Este es el mensaje recibido en fase eleccion  {type(msg)} {msg}{msg.get('type')}")
                        players[:] = msg.get("players")
                        cartas_eleccion = msg.get("election_cards")
                        player1 = players[0]  

                # Procesar mensajes entrantes para actualizaciones de elecciones o orden
                msgList = network_manager.get_incoming_messages()
                #print(f"Este es el mensaje recibido en fase eleccion ORDENNNN  {type(msgList)} {msgList}")
                for msg in msgList:
                    if isinstance(msg[1], dict):
                        if msg[1].get("type") == "PLAYER_ORDER":
                            just_went_down_this_turn = False
                            last_inserted_card_data = None
                            dragging_board_joker = False
                            board_joker_data = None
                            # --- INICIO CORRECCIÓN: RESETEAR VARIABLES DE ESTADO ---
                            bought = False
                            noBuy = True
                            waiting = False
                            time_waiting = None
                            players_for_buy_ids = []
                            player_in_turn_id = None
                            player_init_buy_id = None
                            buy_finished = False
                            list_confirm_ids = []
                            mostrar_boton_comprar = False
                            # --- FIN CORRECCIÓN ---
                            print("Jugador: Recibido orden de jugadores")
                            players[:] = msg[1].get("players", [])
                            deckForRound = msg[1].get("deckForRound")
                            mazo_descarte = msg[1].get("mazo_descarte")
                            hands = msg[1].get("hands")
                            round = msg[1].get("round")
                            received_round = msg[1].get("round")
                            
                            if received_round:
                                round = received_round
                                deckForRound = round.pile
                                mazo_descarte = round.discards
                            else:
                                # Crear una instancia mínima de Round y rellenar pilas si vienen en el mensaje
                                round = Round(players)
                                deck_for_round = msg[1].get("deckForRound")
                                mazo_descarte_msg = msg[1].get("mazo_descarte")
                                if deck_for_round is not None:
                                    round.pile = list(deck_for_round)
                                if mazo_descarte_msg is not None:
                                    round.discards = list(mazo_descarte_msg)
                                # asegurar que round.players apunte a la lista de objetos Player
                                round.players = players
                                print("Jugador: creado Round local con pile/discards recibidos.NO DEBERIA...")
                            # Buscar y actualizar jugador local
                            #puerto_local = network_manager.player.getsockname()[1]
                            id_local = network_manager.player_id
                            print(f"id_local: {id_local}")
                            for p in players:
                                if p.playerId == id_local: #puerto_local:
                                    jugador_local = p
                                    break

                            jugador_local.playerHand = hands[jugador_local.playerId] 
                            visual_hand = list(jugador_local.playerHand)  # Copia inicial para el orden visual
                            # Limpiar zonas de cartas para todas las rondas
                            zona_cartas[0] = []
                            zona_cartas[0].clear()
                            zona_cartas[1] = []
                            zona_cartas[1].clear()
                            if roundThree or roundFour:
                                zona_cartas[2] = []
                                zona_cartas[2].clear()
                            for idx, carta in enumerate(visual_hand):
                                if not hasattr(carta, "id_visual"):
                                    carta.id_visual = id(carta)  # O usa idx para algo más simple

                            # Cambiar fase
                            mensaje_orden = msg[1].get("orden_str", "")
                            tiempo_inicio_orden = time.time()
                            
                            if roundOne:
                                fase = "mostrar_orden"
                            elif roundTwo:
                                fase = "ronda2" 
                            elif roundThree:
                                fase = "ronda3"
                            elif roundFour:
                                fase = "ronda4"
                # Fin procesar Mensajes de INICIO----  Cargar Mazos, Mano, e isHand... PARA EL JUGADOR...       
            if network_manager.is_host:
                if roundOne:
                    from Game import electionPhase
                    playerOrder = electionPhase(players, deck)
                    # Lista de jugadores Ordenada
                    players[:] = playerOrder
                    players[0].isHand = True    # El primer jugador es mano
                    player1 = None
                elif roundTwo or roundThree or roundFour:
                    # sacando al desconcectado
                    for player in players:
                        if player.disconnected == True:
                            players.remove(player)
                    # Rotar la lista: el primero pasa al final
                    players.append(players.pop(0))

                    # Reiniciar la bandera de 'isHand' para todos
                    for player in players:
                        player.isHand = False
                    

                    # El nuevo primer jugador es la nueva mano
                    lista_activos = [p for p in players if not p.isSpectator]
                    idx_siguiente_Mano = players.index(lista_activos[0])
                    players[idx_siguiente_Mano].isHand = True

                #for p in players:
                if players[0].playerId == host_id:
                    jugador_local = players[0]
                    print(f"nombre del jugador_local   {jugador_local.playerName}")  

                # Construir mensaje de orden
                orden_str = "Orden de juego:\n"
                for idx, jugador in enumerate(players):
                    orden_str += f"{idx+1}. {jugador.playerName}\n"
                
                # Limpiar bajadas/parametros de los jagadores para cada ronda
                for p in players:
                    p.jugadas_bajadas = []
                    p.playMade = []
                    p.playerHand = []
                    p.downHand = False
                    p.cardDrawn = False
                    p.discarded = False       # ### NUEVO: Asegurar que discarded sea False
                    p.playerPass = False      # ### NUEVO: Asegurar que nadie haya "pasado"
                    p.playerBuy = False
                # Inicializacion del mazo...
                round = startRound(players, screen)[0]
                print(f"deck para la ronda: {[str(c) for c in round.pile]}")
                print(f"descartes de la ronda: {[str(c) for c in round.discards]}")
                for c in round.discards:
                    mazo_descarte.append(c)
                deckForRound = round.pile
                print(f"Las manos a repartir ...... ID: CARTAS")#{round.hands}")
                network_manager.dprint(round.hands)
                # Enviar orden a todos
                
                # PARA PRUEBA...
                print(f" Mano del jugador... {jugador_local.playerHand}")
                '''if roundOne:
                        players[0].playerHand = [Card("2","♥"), Card("3","♥"), Card("4","♥"), 
                                                    Card("5","♥"),Card("6","♥"),
                                                    Card("9","♦"),Card("9","♦"),Card("9","♦"),Card("9","♦")]
                        round.hands[players[0].playerId] = players[0].playerHand   # Solo una carta para prueba,
                        players[1].playerHand = [Card("2","♥"), Card("3","♥"), Card("4","♥"), 
                                                    Card("5","♥"),Card("6","♥"),Card("7","♥"),Card("8","♥"),Card("9","♥"),Card("10","♥"),
                                                    Card("9","♦"), Card("9","♦"), 
                                                    Card("9","♦"),Card("9","♦"),Card("Joker","", True), Card("9","♦"),Card("Joker","", True,)
                                                    ]
                        round.hands[players[1].playerId] = players[1].playerHand   # Solo una carta para prueba,
                if roundTwo:
                        jugador_local.playerHand = [Card("2","♥"), Card("3","♥"), Card("4","♥"), 
                                                Card("5","♥"),
                                                Card("2","♠"), Card("3","♠"), Card("4","♠"), 
                                                Card("5","♠")]  # Solo una carta para prueba
                        round.hands[jugador_local.playerId] = jugador_local.playerHand''' 
                # --------------
                '''if roundThree:
                    jugador_local.playerHand = [Card("9","♥"), Card("9","♠"), Card("9","♦"), Card("9","♦"),
                                                Card("8","♥"), Card("8","♠"), Card("8","♦"), 
                                                Card("7","♥"),Card("7","♦"),Card("7","♠")]  # Solo una carta para prueba
                    round.hands[jugador_local.playerId] = jugador_local.playerHand'''
                '''if roundFour:
                    jugador_local.playerHand = [Card("9","♥"), Card("9","♠"), Card("9","♦"), 
                                                Card("8","♥"), Card("8","♠"), Card("8","♦"), 
                                                Card("2","♥"), Card("3","♥"), Card("4","♥"), 
                                                Card("5","♥")]  # Solo una carta para prueba
                    round.hands[jugador_local.playerId] = jugador_local.playerHand'''
                # Limpiar zonas de cartas para todas las rondas
                zona_cartas[0] = []
                zona_cartas[0].clear()
                zona_cartas[1] = []
                zona_cartas[1].clear()
                if roundThree or roundFour:
                    zona_cartas[2] = []
                    zona_cartas[2].clear()
                # --- INICIO CORRECCIÓN: RESETEAR VARIABLES DE ESTADO EN EL HOST ---
                bought = False
                noBuy = True
                waiting = False
                time_waiting = None
                players_for_buy_ids = []
                player_in_turn_id = None
                player_init_buy_id = None
                buy_finished = False
                list_confirm_ids = []
                mostrar_boton_comprar = False
                # --- FIN CORRECCIÓN ---'''
                msgOrden = {
                    "type": "PLAYER_ORDER",
                    "players": players,
                    "orden_str": orden_str,
                    "round": round,
                    "hands":round.hands,
                    "deckForRound": deckForRound,
                    "mazo_descarte": mazo_descarte
                }
                network_manager.broadcast_message(msgOrden)
                # Cambiar fase
                mensaje_orden = orden_str.strip()
                tiempo_inicio_orden = time.time()
                if roundOne:
                    fase = "mostrar_orden"
                elif roundTwo:
                    fase = "ronda2"
                elif roundThree:
                    fase = "ronda3"
                elif roundFour:
                    fase = "ronda4"

                print(f" fase del juego>>> Ronda en realidad :)   {fase}")

            # Dibujar
            screen.blit(fondo_img, (0, 0))
            #mostrar_cartas_eleccion(screen, cartas_eleccion)
            pygame.display.flip()
            continue  # <-- Esto es CLAVE: salta el resto del ciclo si estás en la fase de elección
        # Fin de la fase "eleccion"   ---- Está alineado... Mejor ubicacion..

        
        # --- FASE DE JUEGO NORMAL ---
        # Procesando mensajes del juego
        if not network_manager.is_host:
            msgGame = network_manager.get_moves_game()
        else:
            msgGame = network_manager.get_moves_gameServer()
        if msgGame:
            print(f"TURNO DEL JUGADOR: {[p.playerName for p in players if p.isHand]}")
            print(f"llego esto de get_moves_game.. {type(msgGame)} len:{len(msgGame)} TIPO: {msgGame[0].get('type')}")
        
        for msg in msgGame:
            if isinstance(msg,dict) and msg.get("type")=="BAJARSE":
                player_id_que_se_bajo = msg.get("playerId")
                mano_restante = msg.get("playerHand")  # Lista de objetos Card
                jugadas_en_mesa = msg.get("jugadas_bajadas")  # Lista con las combinaciones (tríos/escaleras)
                Jugadas_en_mesa2 = msg.get("playMade")    ## Lista con las combinaciones (tríos/escaleras) en INGLES :D
                round = msg.get("round")

                print(f"Mensaje de BAJARSE recibido del Player ID: {player_id_que_se_bajo}")
                for p in players:
                    if p.playerId == player_id_que_se_bajo:
                        p.playerHand = mano_restante
                        p.jugadas_bajadas = jugadas_en_mesa
                        p.playMade = Jugadas_en_mesa2
                        try:
                            bajarse_sound.play()
                        except Exception as e:
                            print("Error al reproducir bajarse_sound:", e)
            
            elif isinstance(msg,dict) and msg.get("type")=="TOMAR_DESCARTE":
                player_id_que_tomoD = msg.get("playerId")
                mano_restante = msg.get("playerHand")  # Lista de objetos Card
                carta_tomada = msg.get("cardTakenD")  # Lista con las combinaciones (tríos/escaleras)
                mazo_de_descarte = msg.get("mazo_descarte")
                round = msg.get("round")
                
                bought = True

                print(f"Mensaje de TOMAR DESCARTE recibido del Player ID: {player_id_que_tomoD}")
                print(f" Probando.. Mazo de descarte {msg.get('mazo_descarte')}")
                print(f" Probando.. round.discart    {round.discards}")
                print(f" Probando.. mano_restante                    {msg.get('playerHand')}")
                print(f" Probando.. round.hands[player_id_que_tomoD] {round.hands[player_id_que_tomoD]}")
                for p in players:
                    if p.playerId == player_id_que_tomoD:
                        p.playerHand = mano_restante
                        #pass
                cardTakenD = carta_tomada
                mazo_descarte = mazo_de_descarte   #round.discards #mazo_de_descarte
                mazo_descarte = list(round.discards)#prueba

            elif isinstance(msg,dict) and msg.get("type")=="TOMAR_CARTA":
                player_id_que_tomoC = msg.get("playerId")
                mano_restante = msg.get("playerHand")  # Lista de objetos Card
                carta_tomada = msg.get("cardTaken")  # Lista con las combinaciones (tríos/escaleras)
                mazoBocaAbajo = msg.get("mazo")
                round = msg.get("round")

                mostrar_boton_comprar = False
                bought = True
                waiting = False
                time_waiting = None

                print(f"Mensaje de TOMAR CARTA recibido del Player ID: {player_id_que_tomoC}")
                for p in players:
                    if p.playerId == player_id_que_tomoC:
                        p.playerHand = mano_restante
                        p.playerPass = False
                        #pass
                cardTaken = carta_tomada
                deckForRound = mazoBocaAbajo #round.pile

                print(f"Waiting y time_waiting: ({waiting}, {time_waiting})")

                mensaje_temporal = "Tiempo de espera para compras finalizado."
                mensaje_tiempo = time.time()

            elif isinstance(msg,dict) and msg.get("type")=="PASAR_DESCARTE": 

                player_id_que_pasoD = msg.get("playerId")
                player_name_que_pasoD = msg.get("playerName")

                waiting = True
                time_waiting = time.time()
                print(f"Waiting y time_waiting: ({waiting}, {time_waiting})")

                
                print(f"Mensaje de PASAR DESCARTE recibido del Player ID: {player_id_que_pasoD}")
                for p in players:
                    if p.playerId == player_id_que_pasoD:
                        p.playerPass = True
                
                if getattr(mazo_descarte[-1], "discarded_by", None) == jugador_local.playerId:
                    mensaje_temporal = f"{player_name_que_pasoD} pasó del descarte. Ha iniciado un ciclo de compra."
                    mensaje_tiempo = time.time()
                elif not jugador_local.isHand:
                    mostrar_boton_comprar = True  
                    mensaje_temporal = f"{player_name_que_pasoD} pasó del descarte. Compra habilitada temporalmente. Presiona 'COMPRAR CARTA' si deseas comprar."
                    mensaje_tiempo = time.time()

            elif isinstance(msg,dict) and msg.get("type")=="INICIAR_COMPRA":
                player_id_que_compraC = msg.get("playerId")
                player_name_que_compraC = msg.get("playerName")
                players_for_buy_ids = msg.get("players_for_buy_ids")
                player_in_turn_id = msg.get("player_in_turn_id")
                player_init_buy_id = msg.get("player_init_buy_id") 
                print(f"Mensaje de INICIAR COMPRA recibido del Player ID: {player_id_que_compraC}")

                mostrar_boton_comprar = False ###############
                noBuy = False
                waiting = False
                time_waiting = None

                # players[player_in_turn_id].playerTurn = True
                for idx, p in enumerate(players):

                    if p.playerId == player_in_turn_id:
                        players[idx].playerTurn = True
                        if p.playerId == jugador_local.playerId:
                            jugador_local.playerTurn = True   #mmmmmmmmmmmmm
                    else:
                        players[idx].playerTurn = False

                print(f"Lista de jugadores para compra: {players_for_buy_ids}")
                print(f"Jugador en turno de compra: {[p for p in players if p.playerTurn]}")

                mensaje_temporal = f"{player_name_que_compraC} decide si compra la carta."
                mensaje_tiempo = time.time()
        
            elif isinstance(msg,dict) and msg.get("type")=="PASAR_COMPRA":
                player_id_que_pasarCompraC = msg.get("playerId")
                player_name_que_pasarCompraC = msg.get("playerName")
                current_buy_id = msg.get("current_buy_id")
                list_confirm_ids = msg.get("list_confirm_ids")
                mostrar_boton_comprar = False ###############
                print(f"Mensaje de PASAR COMPRA recibido del Player ID: {player_id_que_pasarCompraC}")

                current_buy_pos = players_for_buy_ids.index(current_buy_id)
                next_buy_id_pos = (current_buy_pos + 1) % len(players_for_buy_ids)
                next_buy_id = players_for_buy_ids[next_buy_id_pos]

                for idx, p in enumerate(players):

                    if p.playerId == next_buy_id:
                        players[idx].playerTurn = True
                        if p.playerId == jugador_local.playerId:
                            jugador_local.playerTurn = True
                    else:
                        players[idx].playerTurn = False
                        
                print(f"Lista de jugadores para compra: {players_for_buy_ids}")
                print(f"Jugador en turno de compra: {[p for p in players if p.playerTurn]}")

                mensaje_temporal = f"{player_name_que_pasarCompraC} paso de la compra."
                mensaje_tiempo = time.time()

            elif isinstance(msg,dict) and msg.get("type")=="REALIZAR_COMPRA":
                player_id_que_realizarCompraC = msg.get("playerId")
                player_name_que_realizarCompraC = msg.get("playerName")
                mostrar_boton_comprar = False ###############
                print(f"Mensaje de REALIZAR COMPRA recibido del Player ID: {player_id_que_realizarCompraC}")

                bought = False # Se cambio a False, estaba en True...
                player_in_turn_id = None
                player_init_buy_id = None
                buy_finished = True
                time_confirm = time.time()
                
                for idx, p in enumerate(players):
                    players[idx].playerTurn = False
                        
                print(f"Lista de jugadores para compra: {players_for_buy_ids}")
                print(f"Jugador en turno de compra: {[p for p in players if p.playerTurn]}")

                mensaje_temporal = f"{player_name_que_realizarCompraC} realiza la compra."
                mensaje_tiempo = time.time()

            elif isinstance(msg,dict) and msg.get("type")=="DESCARTE":
                #print(f"Prueba de isHand ANTES JUGADOR: {[p.isHand for p in players]}")
                just_went_down_this_turn = False
                last_inserted_card_data = None
                jokers_insertados_este_turno.clear()
                player_id_que_descarto = msg.get("playerId")
                mano_restante = msg.get("playerHand")  # Lista de objetos Card
                cartasDescartadas = msg.get("cartas_descartadas")
                mazo_de_descarte = msg.get("mazo_descarte")
                players[:] = msg.get("players")
                deck_for_round = msg.get("deckForRound")
                round = msg.get("round")
                
                received_round = msg.get("round")
                
                noBuy = True
                bought = False
                waiting = False
                time_waiting = None
                players_for_buy_ids = []
                player_in_turn_id = None
                player_init_buy_id = None
                buy_finished = False
                time_confirm = None
                list_confirm_ids = []
                mostrar_boton_comprar = False
                # print(f"Valor de bought: {bought}")

                for idx, p in enumerate(players):
                    players[idx].playerTurn = False
                    players[idx].playerPass = False
                    players[idx].cardDrawn = False

                if received_round:
                    round = received_round
                    deckForRound = round.pile
                    mazo_descarte = list(round.discards)
                else:
                    # Crear una instancia mínima de Round y rellenar pilas si vienen en el mensaje
                    round = Round(players)
                    deck_for_round = msg.get("deckForRound")
                    mazo_descarte_msg = msg.get("mazo_descarte")
                    if deck_for_round is not None:
                        round.pile = list(deck_for_round)
                    if mazo_descarte_msg is not None:
                        round.discards = list(mazo_descarte_msg)
                    round.players = players

                for p in players:
                    if network_manager.is_host:
                        if p.isHand and p.playerId == host_id: 
                            jugador_local = p
                            break
                    else:
                        #puerto_local = network_manager.player.getsockname()[1]
                        id_local = network_manager.player_id
                        if p.isHand and p.playerId == id_local: #puerto_local:
                            jugador_local = p
                            break

                cartas_descartadas = cartasDescartadas
                #mazo_descarte = mazo_de_descarte #prueba
                mazo_descarte = list(round.discards) #prueba
                
            elif isinstance(msg,dict) and msg.get("type")=="COMPRAR_CARTA":   # Revisar la lógica... No vi la función append>>> Por es lo digo
                mano_actualizada = msg.get("playerHand")
                player_id_que_compro = msg.get("playerId")
                player_name_que_compro = msg.get("playerName")
                mazo_de_descarte = msg.get("mazo_descarte")
                deck_for_round = msg.get("deckForRound")
                received_round = msg.get("round")

                # Datos nuevos para actualizar al MANO.
                player_id_MANO = msg.get("playerId_Hand")
                player_hand_MANO = msg.get("playerHand_Hand")

                mostrar_boton_comprar = False
                noBuy = True
                bought = True
                players_for_buy_ids = []
                player_in_turn_id = None
                player_init_buy_id = None
                buy_finished = False
                time_confirm = None
                list_confirm_ids = []
                waiting = False
                time_waiting = None

                for idx, p in enumerate(players):
                    players[idx].playerTurn = False

                print(f"Mensaje de COMPRAR CARTA recibido del Player ID: {player_id_que_compro}")
                for p in players:
                    if p.playerId == player_id_que_compro:
                        p.playerHand = mano_actualizada
                        
                    elif p.playerId == player_id_MANO:
                        p.playerHand = player_hand_MANO
                
                if received_round:
                    round = received_round
                    deckForRound = round.pile
                    mazo_descarte = round.discards
                else:
                    print("Algo salio mal con la transmision de la compra, Houston...")

                if jugador_local.playerId == player_id_MANO:
                    jugador_local.playerHand = player_hand_MANO
                    jugador_local.cardDrawn = True
                    jugador_local.playerPass = False
                    mensaje_temporal = f"{player_name_que_compro} compro la carta. Continua tu jugada."
                    mensaje_tiempo = time.time()
                else:
                    mensaje_temporal = f"{player_name_que_compro} compro la carta."
                    mensaje_tiempo = time.time()
            
            elif isinstance(msg, dict) and msg.get("type") == "INSERTAR_CARTA":
                mano_restante = msg.get("playerHand")
                jugadas_visuales = msg.get("jugadas_bajadas")
                jugadas_logicas = msg.get("playMade")
                id_target_player = msg.get("playerId")
                id_jugador_que_inserto = msg.get("playerId2")
                received_round = msg.get("round")

                for p in players:
                    if p.playerId == id_target_player:
                        p.jugadas_bajadas = jugadas_visuales
                        p.playMade = jugadas_logicas
                    if p.playerId == id_jugador_que_inserto:
                        p.playerHand = mano_restante
            elif isinstance(msg, dict) and msg.get("type") == "SWAP_JOKER":
                p_id = msg.get("playerId")
                new_playMade = msg.get("playMade")
                new_visuals = msg.get("jugadas_bajadas")
                
                # Actualizar al jugador correspondiente
                for p in players:
                    if p.playerId == p_id:
                        p.playMade = new_playMade
                        p.jugadas_bajadas = new_visuals
                        print(f"Jugador {p.playerName} movió un Joker en su mesa.")

            elif isinstance(msg, dict) and msg.get("type") == "SALIR":
                p_id = msg.get("playerId")
                p_name = msg.get("playerName")

                # Incluir cartas del jugador en el mazo de descarte
                for idx, p in enumerate(players):
                    if p.playerId == p_id:
                        while p.playerHand != []:
                            for c in p.playerHand:
                                round.discards.insert(0,c)
                                p.playerHand.remove(c)
                        p.isSpectator = True
                        p.disconnected = True

                        if p.isHand == True:
                            p.isHand = False
                            #for idx, p in enumerate(players):
                            #        if p.playerId == jugador_local.playerId:
                            next_idx = (idx + 1) % len(players)
                            players[next_idx].isHand = True
                                        # Si el siguiente es espectador, seguimos buscando
                            #            while players[next_idx].isSpectator:
                            #                next_idx = (next_idx + 1) % len(players)
                                            # Seguridad para evitar bucle infinito si todos son espectadores (no debería pasar si el juego termina antes)
                            #                if next_idx == idx: 
                            #                    break 
                            break

                        
                mensaje_temporal = f"El jugador {p_name} abandonó la partida"
                mensaje_tiempo = time.time()
                
                
        # Fin procesar mensajes del juego...
        ###### SIgo aqui...
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                fondo_img = pygame.transform.scale(pygame.image.load(fondo_path).convert(), (WIDTH, HEIGHT))
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if esta_penalizado(jugador_local): continue 
                idx_descarte = 3 if (roundThree or roundFour) else 2 #prueba
                # --- Detecta clic en inicio o final de cada jugada ---
                mouse_x, mouse_y = event.pos
                carta_levantada_de_zona = False

                # ── BOTÓN ORDENAR MANO ────────────────────────────────────────
                _btn_ordenar_rect = pygame.Rect(WIDTH - 190, HEIGHT - 160, 170, 40)
                if _btn_ordenar_rect.collidepoint(mouse_x, mouse_y) and jugador_local:
                    from Player import ordenar_mano
                    modo_orden = "Runs" if modo_orden == "Sets" else "Sets"
                    ordenar_mano(jugador_local, modo_orden, WIDTH=WIDTH)
                    # Sincronizar visual_hand con el nuevo orden de playerHand
                    orden_logico = list(jugador_local.playerHand)
                    visual_hand[:] = [c for c in orden_logico if c in visual_hand]
                    # Agregar cartas que estén en visual_hand pero no en playerHand (no debería haber)
                    for c in visual_hand:
                        if c not in jugador_local.playerHand:
                            visual_hand.remove(c)
                    # Reasignar índices visuales
                    for idx_v, carta_v in enumerate(visual_hand):
                        carta_v.id_visual = idx_v
                    etiqueta_modo = "Sets (Tríos)" if modo_orden == "Sets" else "Runs (Escaleras)"
                    mensaje_temporal = f"Mano ordenada: {etiqueta_modo}"
                    mensaje_tiempo   = time.time()
                    continue   # no procesar más clics en este frame
                # ─────────────────────────────────────────────────────────────

                # 1. Intentar levantar de las zonas de juego (Trios/Seguidillas)
                # Excluimos el índice de descarte definido arriba
                for idx_zona, stack in enumerate(zona_cartas):
                    #if idx_zona == idx_descarte: continue # No permitir sacar del descarte
                    if stack:
                        # Obtener el nombre de la casilla para colisión
                        nombres_fase = mapping_nombres.get(fase, ["Trio", "Seguidilla"])
                        if idx_zona < len(nombres_fase):
                            nombre_casilla = nombres_fase[idx_zona]
                        else:
                            # Si es el índice de descarte, usamos el nombre "Descarte"
                            nombre_casilla = "Descarte"

                        rect_zona = cuadros_interactivos.get(nombre_casilla)

                        if rect_zona and rect_zona.collidepoint(mouse_x, mouse_y):
                            # Calcular la posición de la carta específica (la de más arriba)
                            # Usando la misma lógica de dibujado para colisión exacta
                            n = len(stack)
                            card_h = int(rect_zona.height * 0.90)
                            card_w = int(card_h * 0.68)
                            overlap_y = max(28, min(53, (rect_zona.height - card_h - 20) // max(1, n - 1))) if n > 1 else 0
                            
                            # Comprobar de la última (arriba) a la primera (abajo)
                            for i in range(n - 1, -1, -1):
                                c_rect = pygame.Rect(rect_zona.x + (rect_zona.width - card_w)//2, 
                                                    rect_zona.y + 10 + i * overlap_y, card_w, card_h)
                                
                                if c_rect.collidepoint(mouse_x, mouse_y):
                                    carta_arrastrada = stack.pop(i) # Sacar de la zona
                                    dragging = True
                                    drag_rect = c_rect
                                    drag_offset_x = mouse_x - c_rect.x
                                    carta_levantada_de_zona = True
                                    try: carta_sound.play()
                                    except: pass
                                    break
                    if carta_levantada_de_zona: break

                if carta_levantada_de_zona:
                    continue # Saltar al siguiente ciclo para evitar levantar de la mano al mismo tiempo
                if (jugador_local and jugador_local.isHand and 
                    jugador_local.downHand and not jugador_local.discarded):
                    
                    for p_name, jugadas_del_jugador in rects_jugadas.items():
                        owner_player = next((p for p in players if p.playerName == p_name), None)
                        if not owner_player: continue

                        es_mi_mesa_fresca = (owner_player.playerId == jugador_local.playerId and just_went_down_this_turn)
                        puedo_mover_por_insercion = (owner_player.playerId in jokers_insertados_este_turno)
                        
                        # Iteramos primero las jugadas
                        for jugada_info in jugadas_del_jugador:
                            if jugada_info["tipo"] != "straight": continue
                            
                            cartas = jugada_info["cartas"]
                            
                            # AHORA evaluamos el permiso para esta jugada específica
                            tiene_permiso_logico = False
                            if es_mi_mesa_fresca or puedo_mover_por_insercion:
                                tiene_permiso_logico = True
                            elif owner_player.playerId != jugador_local.playerId:
                                # Solo llamamos a checkJokerSwap si es mesa ajena
                                tiene_permiso_logico = jugador_local.checkJokerSwap(cartas)

                            if tiene_permiso_logico:
                                card_h = jugada_info["inicio"].height
                                card_w = jugada_info["inicio"].width
                                start_x = jugada_info["inicio"].x
                                start_y = jugada_info["inicio"].y
                                solapamiento = int(card_w * 0.20) if len(cartas) > 1 else 0
                                
                                for idx_c, card in enumerate(cartas):
                                    c_rect = pygame.Rect(start_x + idx_c * solapamiento, start_y, card_w, card_h)
                                    
                                    if c_rect.collidepoint(mouse_x, mouse_y) and getattr(card, "joker", False):
                                        if (idx_c == 0 or idx_c == len(cartas)-1): # Solo extremos
                                            dragging_board_joker = True
                                            carta_arrastrada = card
                                            drag_offset_x = mouse_x - c_rect.x
                                            dragging = True
                                            # IMPORTANTE: Guardamos al dueño (sea local o ajeno)
                                            board_joker_data = {
                                            "owner": owner_player, 
                                            "play_index": jugada_info["play_index"],
                                            "straight_ref": list(cartas), # Copia para validación
                                            "original_idx": idx_c,        # ¡ESTA ES LA CLAVE QUE FALTABA!
                                            "original_rect": jugada_info["rect_total"]
                                            }
                                            try: carta_sound.play() 
                                            except: pass
                                            break
                        if dragging_board_joker: break
                    if dragging_board_joker:
                        continue
                for jugador, jugadas in rects_jugadas.items():
                    for idx, jugada in enumerate(jugadas):
                        if jugada["inicio"].collidepoint(mouse_x, mouse_y):
                            print(f"Clic en INICIO de la jugada {idx+1} de {jugador} ({jugada['tipo']})")
                        elif jugada["final"].collidepoint(mouse_x, mouse_y):
                            print(f"Clic en FINAL de la jugada {idx+1} de {jugador} ({jugada['tipo']})")
                nombre = get_clicked_box(event.pos, cuadros_interactivos)
                if nombre and nombre.startswith("Carta_"):
                    idx = int(nombre.split("_")[1])
                    if idx in cartas_ocultas:
                        mensaje_temporal = "No puedes organizar una carta mientras ejecutas una jugada."
                        mensaje_tiempo = time.time()
                    else:
                        carta_arrastrada = cartas_ref[nombre]
                        drag_rect = cuadros_interactivos[nombre]
                        drag_offset_x = event.pos[0] - drag_rect.x
                        dragging = True
                        # Reproducir sonido al iniciar el arrastre
                        try:
                            carta_sound.play()
                        except Exception as e:
                            # Si falla la reproducción, no interrumpe el juego; registra en consola.
                            print("Error al reproducir carta_sound:", e)



                #Cambio Menu
                elif nombre == "Menú":
                    resultado = show_menu_modal(screen, WIDTH, HEIGHT, ASSETS_PATH)
                    if resultado == "resume":
                        pass  # simplemente se cierra el modal
                    elif resultado == "config":
                        print("Abrir configuración (modal futuro)")
                    elif resultado == "exit":
                        running = False
                        print(f" Jugador antes de salir {jugador_local.playerName}")
                        #.exit_game(jugador_local.playerId, jugador_local.playerName)
                        msgSalir = {
                            "type": "SALIR",
                            "playerId": jugador_local.playerId,
                            "playerName": jugador_local.playerName
                            }
                        #if network_manager.is_host:
                        #    network_manager.broadcast_message(msgSalir)
                        #el
                        if network_manager.player:
                            network_manager.sendData(msgSalir)
                        time.sleep(2)
                        #pygame.quit()
                        return
                #Cambio Menu



                elif nombre:
                    if nombre == "Tomar carta":

                        if not bought and jugador_local.isHand and not jugador_local.cardDrawn:

                            msgPasarD = {
                                    "type": "PASAR_DESCARTE",
                                    "playerId": jugador_local.playerId,
                                    "playerName": jugador_local.playerName
                            }

                            bought = True
                            waiting = True
                            time_waiting = time.time()
                            jugador_local.playerPass = True

                            mensaje_temporal = "Esperando decision de compra de los otros jugadores."
                            mensaje_tiempo = time.time()

                            if network_manager.is_host:
                                network_manager.broadcast_message(msgPasarD)
                            elif network_manager.player:
                                network_manager.sendData(msgPasarD)

                            break
                        elif jugador_local.cardDrawn and noBuy:
                            mensaje_temporal = "Ya tomaste una carta en este turno."
                            mensaje_tiempo = time.time()
                        elif not jugador_local.isHand and noBuy:
                            mensaje_temporal = "No puedes tomar cartas porque no es tu turno."
                            mensaje_tiempo = time.time()
                        elif noBuy and not waiting:
                            print("Aquí ya no debe hacer nada el MANO.")
                            pass
                            """ if not deckForRound or len(deckForRound) == 0:
                                print(f"DECKFORROUND VACÍOOOOOO: {[c for c in deckForRound]}")
                                refillDeck(round)
                                deckForRound = round.pile
                                mazo_descarte = round.discards 

                                print(f"DECKFORROUND Recargado :)  ... : {[c for c in deckForRound]}")

                            #print(f"jugadors {[p for p in players]}")
                            #print(f"El jugador local {jugador_local}")
                            cardTaken = drawCard(jugador_local, round, False)
                            #jugador_local.playerHand.append(cardTaken)
                            jugador_local.playerHand = round.hands[jugador_local.playerId]
                            jugador_local.cardDrawn = True
                            #print(f"DEPURACION DECKFORROUND AL TOMAR CARTA: {[c for c in deckForRound]}")

                            if not deckForRound or len(deckForRound) == 0:
                                print(f"DECKFORROUND VACÍOOOOOO: {[c for c in deckForRound]}")
                                refillDeck(round)
                                deckForRound = round.pile
                                mazo_descarte = round.discards 

                                print(f"DECKFORROUND Recargado :)  ... : {[c for c in deckForRound]}")
                                

                            msgTomarC = {
                                "type": "TOMAR_CARTA",
                                "cardTaken": cardTaken,
                                "playerHand": jugador_local.playerHand,
                                "playerId": jugador_local.playerId,
                                "mazo": deckForRound, #  El mazo se debe actualizar
                                "round": round
                                }
                            
                            jugador_local.playerPass = False
                            bought = True

                            if network_manager.is_host:
                                network_manager.broadcast_message(msgTomarC)
                            elif network_manager.player:
                                network_manager.sendData(msgTomarC) """
                        else:
                            mensaje_temporal = "Hay una compra activa en este momento. Toma del mazo cuando culmine."
                            mensaje_tiempo = time.time()
                    elif nombre == "Tomar descarte":
                        if jugador_local.cardDrawn:
                            mensaje_temporal = "Ya tomaste una carta."
                            mensaje_tiempo = time.time()
                        elif not jugador_local.isHand:
                            mensaje_temporal = "No puedes tomar cartas porque no es tu turno."
                            mensaje_tiempo = time.time()
                        elif bought:
                            mensaje_temporal = "No puedes tomar del mazo de descarte porque la carta se ha quemado."
                            mensaje_tiempo = time.time()
                        elif not waiting and round.discards and noBuy:
                            #print(f"Mano del jugador ANTES DE tomar la carta: {[str(c) for c in jugador_local.playerHand]}")
                            # 1. Obtener la carta del tope
                            top_card = round.discards[-1]
                            
                            # 2. Verificar si es prohibida (propio descarte)
                            player_id_check = getattr(top_card, "discarded_by", None)
                            is_own_discard = (player_id_check == jugador_local.playerId)

                            if is_own_discard:
                                # CASO: ES PROPIO DESCARTE -> BLOQUEAR SILENCIOSAMENTE
                                pass
                            else:
                                # CASO: ES VALIDA -> PROCEDER COMPRA
                                cardTakenD = drawCard(jugador_local, round, True)

                                if mazo_descarte:
                                    mazo_descarte = list(round.discards) #prueba
                                #jugador_local.playerHand.append(cardTakenD)
                                jugador_local.playerHand = round.hands[jugador_local.playerId]
                                register_taken_card(jugador_local, cardTakenD)
                                mensaje_temporal = "Tomaste una carta: no puedes descartarla este turno."
                                mensaje_tiempo = time.time()
                                #cardTakenInDiscards.append(cardTakenD)
                                actualizar_indices_visual_hand(visual_hand)
                                #reiniciar_visual(jugador_local, visual_hand, cuadros_interactivos, cartas_ref)
                                print(f"Carta tomada: {str(cardTakenD)}")
                                print(f"Mano del jugador al tomar la carta: {[str(c) for c in jugador_local.playerHand]}")
                                print(f"Mano visual: {[str(c) for c in visual_hand]}")
                                jugador_local.cardDrawn = True
                                organizar_habilitado = True
                                #cartas_ocultas.clear()


                                msgTomarDescarte = {
                                    "type": "TOMAR_DESCARTE",
                                    "cardTakenD": cardTakenD,
                                    "playerHand": jugador_local.playerHand,
                                    "playerId": jugador_local.playerId,
                                    "mazo_descarte": mazo_descarte,
                                    "round": round
                                    }
                                
                                bought = True

                                if network_manager.is_host:
                                    network_manager.broadcast_message(msgTomarDescarte)
                                elif network_manager.player:
                                    network_manager.sendData(msgTomarDescarte)
                        else:
                            mensaje_temporal = "No puedes tomar el descarte mientras el ciclo de compra este activo."
                            mensaje_tiempo = time.time()

                    elif nombre == "Bajarse":
                        send = False # Para controlar el envío del mensaje de "BAJARSE"
                        resultado1 = []
                        resultado2 = []
                        resultado3 = []
                        if jugador_local.cardDrawn:
                            ronda_actual = 1 if roundOne else 2 if roundTwo else 3 if roundThree else 4

                            # NUEVO CODIGO - INSERTAR AQUI
                            validacion_flexible = adaptar_zonas_flexibles(zona_cartas, ronda_actual)

                            if not validacion_flexible["valida"]:
                                # --- INICIO PENALIZACIÓN ---
                                paquete_red = ejecutar_penalizacion(jugador_local, validacion_flexible)
                                print(f"\n[DEBUG RED] Paquete generado: {paquete_red}\n")
                                # --- FIN PENALIZACIÓN ---
                                mensaje_temporal = validacion_flexible["mensaje"]
                                mensaje_tiempo = time.time()
                                continue

                            zona_cartas[:] = validacion_flexible["zonas_adaptadas"]

                            validacion_campo = resolver_campo_accion(zona_cartas, ronda_actual)

                            if not validacion_campo["valida"]:
                                # --- INICIO PENALIZACIÓN ---
                                paquete_red = ejecutar_penalizacion(jugador_local, validacion_campo)
                                print(f"\n[DEBUG RED] Paquete generado: {paquete_red}\n")
                                # --- FIN PENALIZACIÓN ---
                                mensaje_temporal = validacion_campo["mensaje"]
                                mensaje_tiempo = time.time()
                                continue

                            if roundOne:
                                resultado1 = jugador_local.isValidTrioF(zona_cartas[0]) or validar_jugada_avanzada_por_tipo(zona_cartas[0], "trio")
                                resultado2 = jugador_local.isValidStraightF(zona_cartas[1]) or validar_jugada_avanzada_por_tipo(zona_cartas[1], "seguidilla")
                            elif roundTwo:
                                resultado1 = jugador_local.isValidStraightF(zona_cartas[0]) or validar_jugada_avanzada_por_tipo(zona_cartas[0], "seguidilla")
                                resultado2 = jugador_local.isValidStraightF(zona_cartas[1]) or validar_jugada_avanzada_por_tipo(zona_cartas[1], "seguidilla")
                                
                                if resultado1 and resultado2:
                                    combined_check = zona_cartas[0] + zona_cartas[1]
                                    
                                    # Si juntas forman una sola escalera válida, es ilegal en esta ronda
                                    if jugador_local.isValidStraightF(combined_check, max_jokers= 4):
                                        mensaje_temporal = "Error: Es una misma seguidilla partida en dos. Deben ser distintas."
                                        mensaje_tiempo = time.time()
                                        
                                        continue 
                            elif roundThree:
                                #resultado = jugador_local.getOff2(zona_cartas[0], zona_cartas[1])
                                resultado1 = jugador_local.isValidTrioF(zona_cartas[0]) or validar_jugada_avanzada_por_tipo(zona_cartas[0], "trio")
                                resultado2 = jugador_local.isValidTrioF(zona_cartas[1]) or validar_jugada_avanzada_por_tipo(zona_cartas[1], "trio")
                                resultado3 = jugador_local.isValidTrioF(zona_cartas[2]) or validar_jugada_avanzada_por_tipo(zona_cartas[2], "trio")

                                if resultado1 and resultado2 and resultado3:
                                    # Obtenemos el valor de la primera carta que NO sea joker en cada zona
                                    # next() busca el primer elemento que cumpla la condición, devuelve None si no encuentra
                                    v1 = next((c.value for c in zona_cartas[0] if not getattr(c, "joker", False)), None)
                                    v2 = next((c.value for c in zona_cartas[1] if not getattr(c, "joker", False)), None)
                                    v3 = next((c.value for c in zona_cartas[2] if not getattr(c, "joker", False)), None)
                                    
                                    # Comparamos si hay duplicados
                                    if v1 == v2 or v1 == v3 or v2 == v3:
                                        mensaje_temporal = "Error: No puedes bajar dos o más tríos del mismo valor."
                                        mensaje_tiempo = time.time()
                                        
                                        continue
                            elif roundFour:
                                resultado1 = jugador_local.isValidTrioF(zona_cartas[0]) or validar_jugada_avanzada_por_tipo(zona_cartas[0], "trio")
                                resultado2 = jugador_local.isValidTrioF(zona_cartas[1]) or validar_jugada_avanzada_por_tipo(zona_cartas[1], "trio")
                                resultado3 = jugador_local.isValidStraightF(zona_cartas[2]) or validar_jugada_avanzada_por_tipo(zona_cartas[2], "seguidilla")

                                if resultado1 and resultado2 and resultado3:
                                    # En Ronda 4, zona 0 y zona 1 son los tríos
                                    v1 = next((c.value for c in zona_cartas[0] if not getattr(c, "joker", False)), None)
                                    v2 = next((c.value for c in zona_cartas[1] if not getattr(c, "joker", False)), None)
                                    
                                    if v1 == v2:
                                        mensaje_temporal = "Error: Los dos tríos deben ser de valores distintos."
                                        mensaje_tiempo = time.time()
                                        continue
                            if resultado1 and resultado2 and roundOne:  #Para la primera ronda 
                                send = True
                                sortedStraights = None
                                #trios_bajados, seguidillas_bajadas = resultado
                                # Guarda las jugadas bajadas en jugador_local.jugadas_bajadas
                                if not hasattr(jugador_local, "jugadas_bajadas"):
                                    jugador_local.jugadas_bajadas = []
                                if jugador_local.sortedStraight(zona_cartas[1]) == True:
                                    sortedStraights = zona_cartas[1]
                                else:
                                    sortedStraights = jugador_local.sortedStraight(zona_cartas[1])
                                    # NUEVO CODIGO - INSERTAR AQUI
                                    if sortedStraights is False:
                                        sortedStraights = preparar_seguidilla_extendida(zona_cartas[1])
                                jugador_local.jugadas_bajadas.append(sortedStraights)
                                jugador_local.jugadas_bajadas.append(zona_cartas[1])
                                for carta in zona_cartas[0] + zona_cartas[1]:
                                    if carta in visual_hand:
                                        visual_hand.remove(carta)
                                        jugador_local.playerHand.remove(carta)
                                jugador_local.playMade.append(zona_cartas[0])
                                jugador_local.playMade.append(sortedStraights)
                                
                                jugador_local.downHand =True
                                organizar_habilitado = True
                                just_went_down_this_turn = True
                                last_inserted_card_data = None
                                cartas_ocultas.clear()
                                zona_cartas[0] = []
                                zona_cartas[0].clear()
                                zona_cartas[1] = []
                                zona_cartas[1].clear()
                                reiniciar_visual(jugador_local, visual_hand, cuadros_interactivos, cartas_ref)
                                #Eliminamos las cartas de los espacios visuales, para que desaparezcan al pulsar el botón de bajarse
                            
                            elif resultado1 and resultado2 and roundTwo:
                            #elif resultado1 and resultado2 and roundTwo:  #Para la segunda ronda 
                                send = True
                                sortedStraights1 = None
                                sortedStraights2 = None
                                #seguidillas_bajadas, seguidillas2_bajadas = resultado
                                #NoUsar , seguidillas_bajadas = resultado1
                                #NoUsar , seguidillas2_bajadas = resultado2 
                                # Guarda las jugadas bajadas en jugador_local.jugadas_bajadas
                                if not hasattr(jugador_local, "jugadas_bajadas"):
                                    jugador_local.jugadas_bajadas = []
                                if jugador_local.sortedStraight(zona_cartas[0]) == True and jugador_local.sortedStraight(zona_cartas[1]) == True:
                                    sortedStraights1 = zona_cartas[0]
                                    sortedStraights2 = zona_cartas[1]
                                elif jugador_local.sortedStraight(zona_cartas[0]) == True and jugador_local.sortedStraight(zona_cartas[1]) != True:
                                    sortedStraights1 = zona_cartas[0]
                                    sortedStraights2 = jugador_local.sortedStraight(zona_cartas[1])
                                elif jugador_local.sortedStraight(zona_cartas[0]) != True and jugador_local.sortedStraight(zona_cartas[1]) == True:
                                    sortedStraights1 = jugador_local.sortedStraight(zona_cartas[0])
                                    sortedStraights2 = zona_cartas[1]
                                else:
                                    sortedStraights1 = jugador_local.sortedStraight(zona_cartas[0])
                                    sortedStraights2 = jugador_local.sortedStraight(zona_cartas[1])
                                # NUEVO CODIGO - INSERTAR AQUI
                                if sortedStraights1 is False:
                                    sortedStraights1 = preparar_seguidilla_extendida(zona_cartas[0])
                                if sortedStraights2 is False:
                                    sortedStraights2 = preparar_seguidilla_extendida(zona_cartas[1])
                                jugador_local.jugadas_bajadas.append(sortedStraights1)
                                jugador_local.jugadas_bajadas.append(sortedStraights2)
                                for carta in zona_cartas[0]+ zona_cartas[1]:
                                    if carta in visual_hand:
                                        visual_hand.remove(carta)
                                        jugador_local.playerHand.remove(carta)
                                jugador_local.playMade.append(sortedStraights1)
                                jugador_local.playMade.append(sortedStraights2)
                                jugador_local.downHand =True
                                organizar_habilitado = True
                                just_went_down_this_turn = True
                                last_inserted_card_data = None
                                cartas_ocultas.clear()
                                zona_cartas[0] = []
                                zona_cartas[0].clear()
                                zona_cartas[1] = []
                                zona_cartas[1].clear()
                                reiniciar_visual(jugador_local, visual_hand, cuadros_interactivos, cartas_ref)
                            elif resultado1 and resultado2 and resultado3 and roundThree:  #Para la tercera ronda 
                                send = True
                                if not hasattr(jugador_local, "jugadas_bajadas"):
                                    jugador_local.jugadas_bajadas = []
                                jugador_local.jugadas_bajadas.append(zona_cartas[0])
                                jugador_local.jugadas_bajadas.append(zona_cartas[1])
                                jugador_local.jugadas_bajadas.append(zona_cartas[2])
                                for carta in zona_cartas[0]+ zona_cartas[1] + zona_cartas[2]:
                                    if carta in visual_hand:
                                        visual_hand.remove(carta)
                                        jugador_local.playerHand.remove(carta)
                                jugador_local.playMade.append(zona_cartas[0])
                                jugador_local.playMade.append(zona_cartas[1])
                                jugador_local.playMade.append(zona_cartas[2])
                                jugador_local.downHand =True
                                organizar_habilitado = True
                                just_went_down_this_turn = True
                                last_inserted_card_data = None
                                cartas_ocultas.clear()
                                zona_cartas[0] = []
                                zona_cartas[0].clear()
                                zona_cartas[1] = []
                                zona_cartas[1].clear()
                                zona_cartas[2] = []
                                zona_cartas[2].clear()
                                reiniciar_visual(jugador_local, visual_hand, cuadros_interactivos, cartas_ref)
                                
                            elif resultado1 and resultado2 and resultado3 and roundFour and (len(zona_cartas[0])+len(zona_cartas[1])+len(zona_cartas[2]))==len(jugador_local.playerHand): 
                                send = True
                                sortedStraights = None
                                if not hasattr(jugador_local, "jugadas_bajadas"):
                                    jugador_local.jugadas_bajadas = []
                                if jugador_local.sortedStraight(zona_cartas[2]) == True:
                                    sortedStraights = zona_cartas[2]
                                else:
                                    sortedStraights = jugador_local.sortedStraight(zona_cartas[2])
                                    # NUEVO CODIGO - INSERTAR AQUI
                                    if sortedStraights is False:
                                        sortedStraights = preparar_seguidilla_extendida(zona_cartas[2])
                                jugador_local.jugadas_bajadas.append(zona_cartas[0])
                                jugador_local.jugadas_bajadas.append(zona_cartas[1])
                                jugador_local.jugadas_bajadas.append(sortedStraights)
                                for carta in zona_cartas[0]+ zona_cartas[1] + zona_cartas[2]:
                                    if carta in visual_hand:
                                        visual_hand.remove(carta)
                                        jugador_local.playerHand.remove(carta)
                                jugador_local.playMade.append(zona_cartas[0])
                                jugador_local.playMade.append(zona_cartas[1])
                                jugador_local.playMade.append(sortedStraights)
                                jugador_local.downHand =True
                                organizar_habilitado = True
                                just_went_down_this_turn = True
                                last_inserted_card_data = None
                                cartas_ocultas.clear()
                                zona_cartas[0] = []
                                zona_cartas[0].clear()
                                zona_cartas[1] = []
                                zona_cartas[1].clear()
                                zona_cartas[2] = []
                                zona_cartas[2].clear()
                                reiniciar_visual(jugador_local, visual_hand, cuadros_interactivos, cartas_ref)
                            else:
                                if roundOne:
                                    nombres = ["el trío", "la seguidilla"]
                                    resultados = [resultado1, resultado2]
                                elif roundTwo:
                                    nombres = ["la primera seguidilla", "la segunda seguidilla"]
                                    resultados = [resultado1, resultado2]
                                elif roundThree:
                                    nombres = ["el primer trío", "el segundo trío", "el tercer trío"]
                                    resultados = [resultado1, resultado2, resultado3]
                                elif roundFour:
                                    nombres = ["el primer trío", "el segundo trío", "la seguidilla"]
                                    resultados = [resultado1, resultado2, resultado3]

                                # 2. Filtramos solo los nombres de los que fallaron (donde resultado es False)
                                fallas = [nombres[i] for i, res in enumerate(resultados) if not res]

                                # 3. Construcción del mensaje
                                if not fallas:
                                    mensaje_temporal = "¡Todos los movimientos son válidos!"
                                else:
                                    if len(fallas) == 1:
                                        # Ejemplo: "El segundo trío no es válido."
                                        mensaje_temporal = f"{fallas[0].capitalize()} no es válido."
                                    else:
                                        # Une los elementos con comas y el último con "y"
                                        # Ejemplo: "el primer trío y el tercer trío"
                                        conector_y = " y "
                                        texto_unido = conector_y.join([", ".join(fallas[:-1]), fallas[-1]] if len(fallas) > 2 else fallas)
                                        
                                        mensaje_temporal = f"{texto_unido.capitalize()} no son válidos."

                                mensaje_tiempo = time.time()
                                '''cartas_ocultas.clear()
                                zona_cartas[0] = []
                                zona_cartas[0].clear()
                                zona_cartas[1] = []
                                zona_cartas[1].clear()
                                if roundThree or roundFour:
                                    zona_cartas[2] = []
                                    zona_cartas[2].clear()'''
                            if not send and roundFour and jugador_local.cardDrawn:
                                mensaje_temporal = "En la Ronda 4 No te puedes bajar y quedar con cartas en la mano"
                                mensaje_tiempo = time.time()


                            #reiniciar_visual(jugador_local, visual_hand, cuadros_interactivos, cartas_ref)
                            #organizar_habilitado = True
                            #cartas_ocultas.clear()

                            msgBajarse = {
                                "type":"BAJARSE",
                                "playerHand": jugador_local.playerHand,
                                "jugadas_bajadas": jugador_local.jugadas_bajadas,
                                "playMade": jugador_local.playMade,
                                "playerId": jugador_local.playerId,
                                "round": round
                                }
                            if network_manager.is_host:
                                if msgBajarse and send:
                                    network_manager.broadcast_message(msgBajarse)
                                else: 
                                    print("Mensaje vacio... No enviado")
                            else:
                                if msgBajarse and send:
                                    network_manager.sendData(msgBajarse)
                                else: 
                                    print("Mensaje vacio... No enviado")
                        else:
                            mensaje_temporal = "Debes tomar una carta antes de bajarte."
                            mensaje_tiempo = time.time()
                            #cartas_ocultas.clear()
                            '''zona_cartas[0] = []
                            zona_cartas[0].clear()
                            zona_cartas[1] = []
                            zona_cartas[1].clear()
                            if roundThree or roundFour:
                                    zona_cartas[2] = []
                                    zona_cartas[2].clear()'''
                    elif nombre == "Descartar":
                            # Determinar la carta seleccionada (click sobre Carta_x) o usar la zona de arrastre (zona_cartas[2])
                            selected_card = None
                            for key, rect in cuadros_interactivos.items():
                                if key.startswith("Carta_") and rect.collidepoint(event.pos):
                                    selected_card = cartas_ref.get(key)
                                    break
                            numero = 0
                            if roundOne or roundTwo:
                                numero = 2
                            elif roundThree or roundFour:
                                numero = 3
                            if len(zona_cartas[numero]) >= 1:
                                # si hay cartas arrastradas al área de descarte, úsalas
                                selected_cards = list(zona_cartas[numero])
                            elif selected_card is not None:
                                selected_cards = [selected_card]
                            else:
                                mensaje_temporal = "Selecciona una carta para descartar o arrástrala al área de Descarte."
                                mensaje_tiempo = time.time()
                                continue
                            # Llama al método del jugador para descartar (se espera que devuelva lista de Card o None)
                            if not can_discard(jugador_local, selected_cards):
                                
                                if last_inserted_card_data is not None and len(jugador_local.playerHand) <= 1:
                                    mensaje_temporal = "¡Inserción devuelta! No puedes cerrar con esa carta."
                                    mensaje_tiempo = time.time()
                                    
                                    target_p = last_inserted_card_data['target_player']
                                    idx_play = last_inserted_card_data['play_index']
                                    card_to_remove = last_inserted_card_data['card']
                                    
                                    # 1. Buscar y remover la carta de la jugada lógica (playMade)
                                    removed_successfully = False
                                    if idx_play < len(target_p.playMade):
                                        play_target = target_p.playMade[idx_play]
                                        
                                        # Determinar la lista real de cartas (maneja listas o diccionarios)
                                        target_list = None
                                        if isinstance(play_target, list):
                                            target_list = play_target
                                        elif isinstance(play_target, dict):
                                            target_list = play_target.get("straight") or play_target.get("trio")
                                            
                                        if target_list is not None:
                                            # Remover por valor/identidad
                                            for i, c in enumerate(target_list):
                                                if str(c) == str(card_to_remove):
                                                    target_list.pop(i)
                                                    removed_successfully = True
                                                    break

                                    if removed_successfully:
                                        # 2. Devolver a la mano del jugador local
                                        jugador_local.playerHand.append(card_to_remove)
                                        
                                        # 3. Limpiar visuales de la mesa del objetivo
                                        # Forzamos que el objeto del jugador objetivo actualice sus strings visuales
                                        if hasattr(target_p, "jugadas_bajadas"):
                                            target_p.jugadas_bajadas[idx_play] = [str(c) for c in target_list]

                                        # 4. Resetear estado de inserción
                                        last_inserted_card_data = None
                                        
                                        # 5. Actualizar interfaz local
                                        cartas_ocultas.clear()
                                        zona_cartas[numero] = []
                                        reiniciar_visual(jugador_local, visual_hand, cuadros_interactivos, cartas_ref)

                                        # 6. SINCRONIZAR RED: Avisar a todos que la inserción se canceló
                                        msgRevertirInsert = {
                                            "type": "INSERTAR_CARTA",
                                            "playerHand": jugador_local.playerHand,
                                            "jugadas_bajadas": target_p.jugadas_bajadas,
                                            "playMade": target_p.playMade,
                                            "playerId": target_p.playerId, # El dueño de la mesa
                                            "playerId2": jugador_local.playerId, # El que recupera la carta
                                            "round": round
                                        }
                                        if network_manager.is_host:
                                            network_manager.broadcast_message(msgRevertirInsert)
                                        else:
                                            network_manager.sendData(msgRevertirInsert)
                                            
                                    continue # Salta el resto del proceso de descarte
                                # Si se bajó en este turno y le queda 1 carta (la prohibida) o menos en mano
                                elif just_went_down_this_turn and len(jugador_local.playerHand) <= 1:
                                    mensaje_temporal = "¡Jugada devuelta! No puedes cerrar con la carta que tomaste."
                                    mensaje_tiempo = time.time()
                                    
                                    # 1. Recuperar cartas de la mesa a la mano
                                    cartas_recuperadas = []
                                    for jugada in jugador_local.playMade:
                                        # playMade tiene las listas de cartas (objetos Card)
                                        if isinstance(jugada, list):
                                            cartas_recuperadas.extend(jugada)
                                        elif isinstance(jugada, dict): # Por si acaso estructura dict
                                            if "trio" in jugada: cartas_recuperadas.extend(jugada["trio"])
                                            if "straight" in jugada: cartas_recuperadas.extend(jugada["straight"])
                                    
                                    jugador_local.playerHand.extend(cartas_recuperadas)
                                    
                                    # 2. Resetear estado del jugador
                                    jugador_local.jugadas_bajadas = []
                                    jugador_local.playMade = []
                                    jugador_local.downHand = False
                                    just_went_down_this_turn = False
                                    
                                    # 3. Actualizar visuales
                                    cartas_ocultas.clear()
                                    zona_cartas[numero] = []
                                    actualizar_indices_visual_hand(visual_hand)
                                    reiniciar_visual(jugador_local, visual_hand, cuadros_interactivos, cartas_ref)
                                    
                                    # SINCRONIZAR RED (Avisar a otros que "me levanté")
                                    # Reutilizamos el mensaje BAJARSE pero con las listas vacías, 
                                    # esto actualizará a los pares dejándome con las cartas en mano y nada en mesa.
                                    msgRevertir = {
                                        "type": "BAJARSE",
                                        "playerHand": jugador_local.playerHand,
                                        "jugadas_bajadas": [], # Vacío
                                        "playMade": [],        # Vacío
                                        "playerId": jugador_local.playerId,
                                        "round": round
                                    }
                                    if network_manager.is_host:
                                        network_manager.broadcast_message(msgRevertir)
                                    else:
                                        network_manager.sendData(msgRevertir)
                                    
                                    continue # Detener proceso de descarte

                                # CASO B: REVERTIR "INSERTAR CARTA"
                                # Si insertó carta este turno y se quedó solo con la prohibida
                                # CASO C: Solo notificación (tiene más cartas)
                                else:
                                    mensaje_temporal = "No puedes descartar la carta que acabas de tomar."
                                    mensaje_tiempo = time.time()
                                    for c in selected_cards:
                                        if c in visual_hand:
                                            idx_c = visual_hand.index(c)
                                            if idx_c in cartas_ocultas:
                                                cartas_ocultas.remove(idx_c)
                                    zona_cartas[numero] = []
                                    continue

                            cartas_descartadas = jugador_local.discardCard(selected_cards, round) #discardCard(selected_cards, round, [p for p in players if p != jugador_local]) asi funciona para lo de ana
                            if cartas_descartadas == '001':
                                mensaje_temporal = "Solo puedes bajar 2 cartas si una de ellas es un Joker"
                                mensaje_tiempo = time.time()
                                for c in selected_cards:
                                        if c in visual_hand:
                                            idx_c = visual_hand.index(c)
                                            if idx_c in cartas_ocultas:
                                                cartas_ocultas.remove(idx_c)
                                zona_cartas[numero] = []
                                continue
                            elif cartas_descartadas == '002':
                                mensaje_temporal = "Para poder descartar un joker, debes descartar también otra carta normal"
                                mensaje_tiempo = time.time()
                                for c in selected_cards:
                                        if c in visual_hand:
                                            idx_c = visual_hand.index(c)
                                            if idx_c in cartas_ocultas:
                                                cartas_ocultas.remove(idx_c)
                                zona_cartas[numero] = []
                                continue
                            elif cartas_descartadas == '003':
                                mensaje_temporal = "No puedes quemar el mono si no te has bajado."
                                mensaje_tiempo = time.time()
                                for c in selected_cards:
                                        if c in visual_hand:
                                            idx_c = visual_hand.index(c)
                                            if idx_c in cartas_ocultas:
                                                cartas_ocultas.remove(idx_c)
                                zona_cartas[numero] = []
                                continue
                            elif cartas_descartadas =="004":
                                mensaje_temporal = "Debes tomar una carta antes de descartar"
                                mensaje_tiempo = time.time()
                                for c in selected_cards:
                                        if c in visual_hand:
                                            idx_c = visual_hand.index(c)
                                            if idx_c in cartas_ocultas:
                                                cartas_ocultas.remove(idx_c)
                                zona_cartas[numero] = []
                                continue
                            elif not cartas_descartadas:
                                # No se descartó: devolver visuales si hacía falta
                                mensaje_temporal = "No se pudo descartar esa(s) carta(s)."
                                mensaje_tiempo = time.time()
                                for c in selected_cards:
                                        if c in visual_hand:
                                            idx_c = visual_hand.index(c)
                                            if idx_c in cartas_ocultas:
                                                cartas_ocultas.remove(idx_c)
                                zona_cartas[numero] = []
                                continue
                            else:
                                pass
                            # Validaciones de turno y regla "no descartar carta tomada este turno"
                            if not jugador_local.isHand:
                                mensaje_temporal = "No puedes descartar si no es tu turno."
                                mensaje_tiempo = time.time()
                                # devolver cartas a la mano si el método las removió
                                for c in selected_cards:
                                    if c not in jugador_local.playerHand:
                                        jugador_local.playerHand.append(c)
                                for c in selected_cards:
                                        if c in visual_hand:
                                            idx_c = visual_hand.index(c)
                                            if idx_c in cartas_ocultas:
                                                cartas_ocultas.remove(idx_c)
                                zona_cartas[numero] = []
                                continue
                            elif (jugador_local.isHand and jugador_local.canDiscard) or not can_discard(jugador_local, cartas_descartadas):
                                
                                cartas_en_zonas_visuales = []
                                for zona in zona_cartas:
                                    cartas_en_zonas_visuales.extend(zona)
                                actualizar_indices_visual_hand(visual_hand)
                                last_taken_card = None
                                last_taken_player = None
                                jugador_local.isHand = False
                                
                                reiniciar_visual(jugador_local, visual_hand, cuadros_interactivos, cartas_ref)
                                
                                visual_hand[:] = [c for c in visual_hand if c not in cartas_en_zonas_visuales]
                                cartas_ocultas.clear()
                                actualizar_indices_visual_hand(visual_hand)
                                organizar_habilitado = True
                                jugador_local.cardDrawn = False
                                #cartas_ocultas.clear() lo comente ya que si hacia un descarte y habia cartas en la zona de descarte se duplicaban
                                if len(cartas_descartadas) == 2:
                                    mazo_descarte = list(round.discards)
                                else:
                                    #mazo_descarte.append(carta)
                                    mazo_descarte = round.discards  #Luego de reiniciado el mazo, se duplicaron las cartas
                                zona_cartas[numero] = []
                                #print(f"Mano del jugador: {[str(c) for c in jugador_local.playerHand]}")
                                #print(f"Prueba de isHand ANTES: {[p.isHand for p in players]}")
                                # Ciclo para encontrar el siguiente jugador NO ESPECTADOR
                                for idx, p in enumerate(players):
                                    if p.playerId == jugador_local.playerId:
                                        next_idx = (idx + 1) % len(players)
                                        # Si el siguiente es espectador, seguimos buscando
                                        while players[next_idx].isSpectator:
                                            next_idx = (next_idx + 1) % len(players)
                                            # Seguridad para evitar bucle infinito si todos son espectadores (no debería pasar si el juego termina antes)
                                            if next_idx == idx: 
                                                break 
                                        break
                                
                                players[next_idx].isHand = True
                                #print(f"Prueba de isHand DESPUES: {[p.isHand for p in players]}")
                                # NUEVA LÓGICA: El turno terminó, el Joker ya no se puede mover
                                jokers_insertados_este_turno.clear()
                                noBuy = True
                                bought = False
                                waiting = False
                                time_waiting = None
                                players_for_buy_ids = []
                                player_in_turn_id = None
                                player_init_buy_id = None
                                buy_finished = False
                                time_confirm = None
                                list_confirm_ids = []

                                for idx, p in enumerate(players):
                                    players[idx].playerTurn = False
                                    players[idx].playerPass = False
                                    players[idx].cardDrawn = False
                                    players[idx].discarded = False

                                msgDescarte = {
                                    "type": "DESCARTE",
                                    "cartas_descartadas": cartas_descartadas,
                                    "playerHand": jugador_local.playerHand,
                                    "playerId": jugador_local.playerId,
                                    "mazo_descarte": mazo_descarte,#  El mazo se debe actualizar
                                    "players": players,   # La lista deberia Mantener el orden, pero con la MANO actualizada
                                    "deckForRound":deckForRound,
                                    "round": round
                                }
                                if network_manager.is_host:
                                    network_manager.broadcast_message(msgDescarte)
                                else:
                                    network_manager.sendData(msgDescarte)
                    elif nombre == "Comprar carta":
                        print(f" Click en COMPRAR CARTA... Boton comprar carta")
                        #CAMBIO 2
                        if not jugador_local.isHand: # El jugador MANO no puede comprar cartas...

                            if not bought:

                                jugador_mano_actual = [p for p in players if p.isHand][0] # Encontramos al jugador MANO actualmente
                            
                                print(f"MANO actual: {jugador_mano_actual}")
                                print(f"Valor de playerPass del MANO: {jugador_mano_actual.playerPass}")
                                if jugador_mano_actual.playerPass: # Verificamos el valor de "playerPass", para saber si la compra esta permitida.

                                    print(f"Valor de jugador_local: {jugador_local}")
                                    # Encontramos la posicion del jugador local en la lista de jugadores (el que activo la compra de cartas)
                                    indice_jugador_local = None
                                    for idx, player in enumerate(players):
                                        if player.playerId == jugador_local.playerId:
                                            indice_jugador_local = idx
                                            break
                                    
                                    # Buscamos la posicion del jugador MANO en la lista de jugadores y calculamos el indice que le sigue.
                                    indice_mano_actual = None
                                    siguiente_idx = None
                                    for idx, player in enumerate(players):
                                        if player.playerId == jugador_mano_actual.playerId:
                                            indice_mano_actual = idx
                                            siguiente_idx = (idx + 1) % len(players)
                                            break

                                    # noBuy = False

                                    for i in range(1, len(players)):
                                        
                                        idx_jugador_en_compra = (siguiente_idx + (i - 1)) % len(players)
                                        players_for_buy_ids.append(players[idx_jugador_en_compra].playerId)

                                        if idx_jugador_en_compra == indice_jugador_local:
                                            break
                                    
                                    # Si no hay cartas en la pila de descartes, no se puede comprar nada.
                                    if not round.discards:
                                        mensaje_temporal = "No hay cartas para comprar en este momento."
                                        mensaje_tiempo = time.time()
                                        continue
                                    elif not noBuy:
                                        mensaje_temporal = "Ya hay un ciclo de compra activo en este momento."
                                        mensaje_tiempo = time.time()
                                    # Si el indice del jugador que viene luego del MANO coincide con el indice del jugador local, 
                                    # se sigue el proceso de compra sin mostrar la pantalla de confirmacion (tiene la maxima prioridad).
                                    elif siguiente_idx == indice_jugador_local:
                                        
                                        # Indicamos que el jugador compra la carta.
                                        jugador_local.playerBuy = True
                                        print(f"Pila antes de compra: {[c for c in round.pile]}")

                                        # Validamos que el mazo tenga cartas antes de la compra.
                                        if not deckForRound or len(deckForRound) == 0:
                                            print(f"DECKFORROUND VACÍOOOOOO: {[c for c in deckForRound]}")
                                            refillDeck(round)
                                            deckForRound = round.pile
                                            mazo_descarte = round.discards 

                                            print(f"\nDECKFORROUND Recargado :)\nAntes de realizar la compra efectiva (compra iniciada por el proximo MANO)...:\n {[c for c in deckForRound]}\n")

                                        # Se ejecuta la compra.
                                        cards_bought = jugador_local.buyCard(round)
                                        print(f"Pila despues de compra: {[c for c in round.pile]}")

                                        # Recargamos el mazo, si se termina luego de la compra.
                                        if not deckForRound or len(deckForRound) == 0:
                                            print(f"DECKFORROUND VACÍOOOOOO: {[c for c in deckForRound]}")
                                            refillDeck(round)
                                            deckForRound = round.pile
                                            mazo_descarte = round.discards 

                                            print(f"DECKFORROUND Recargado :)\nDespues de realizar la compra efectiva (compra iniciada por el proximo MANO)...:\n {[c for c in deckForRound]}")

                                        jugador_local.playerBuy = False
                                        if cards_bought is not None:
                                            cartas_ocultas.clear()
                                            numero = 0
                                            if roundOne or roundTwo:
                                                numero = 2
                                            elif roundThree or roundFour:
                                                numero = 3
                                            zona_cartas[numero] = [] # Limpiamos la zona de descartes.
                                            print(f"Mano del jugador que compro: {jugador_local.playerHand}")
                                            
                                            # Asignamos una carta del mazo al MANO actual.
                                            cardTaken = drawCard(jugador_mano_actual, round, False)
                                            
                                            jugador_mano_actual.playerHand = round.hands[jugador_mano_actual.playerId]
                                            jugador_mano_actual.cardDrawn = True
                                            jugador_mano_actual.playerPass = False

                                            # Recargamos el mazo, si se termina luego de que el MANO tome del mazo.
                                            if not deckForRound or len(deckForRound) == 0:
                                                print(f"DECKFORROUND VACÍOOOOOO: {[c for c in deckForRound]}")
                                                refillDeck(round)
                                                deckForRound = round.pile
                                                mazo_descarte = round.discards 

                                                print(f"DECKFORROUND Recargado :)\nDespues de asignar una carta al MANO luego de la compra efectiva (compra iniciada por el proximo MANO)...:\n {[c for c in deckForRound]}")
                                            
                                            # players[indice_mano_actual].playerPass = False
                                            players[indice_mano_actual].isHand = True
                                            players[indice_jugador_local].isHand = False
                                            print("Se reseteo el valor de playerPass del MANO a False.")

                                            for idx, carta in enumerate(jugador_local.playerHand):
                                                carta.id_visual = idx
                                                visual_hand.append(carta)

                                            reiniciar_visual(jugador_local, visual_hand, cuadros_interactivos, cartas_ref)
                                            mazo_descarte = round.discards
                                            deckForRound = round.pile

                                            msgComprarC = {
                                                    "type": "COMPRAR_CARTA",
                                                    "playerHand": jugador_local.playerHand,
                                                    "playerId": jugador_local.playerId,
                                                    "playerName": jugador_local.playerName,
                                                    "mazo_descarte": mazo_descarte,#  El mazo se debe actualizar
                                                    "deckForRound": deckForRound,
                                                    "zona_cartas": zona_cartas,
                                                    "round": round,
                                                    "playerId_Hand": jugador_mano_actual.playerId,    # Dato extra
                                                    "playerHand_Hand": jugador_mano_actual.playerHand # Dato extra
                                            }

                                            mostrar_boton_comprar = False
                                            noBuy = True
                                            bought = True
                                            waiting = False
                                            time_waiting = None

                                            if network_manager.is_host:
                                                network_manager.broadcast_message(msgComprarC)
                                            else:
                                                network_manager.sendData(msgComprarC)

                                            mensaje_temporal = "Has comprado la carta."
                                            mensaje_tiempo = time.time()
                                        else:
                                            # CASO: COMPRA FALLIDA (ej. propio descarte)
                                            # Resetear variables del ciclo de compra para no quedar atascado
                                            noBuy = True
                                            bought = True
                                            players_for_buy_ids = []
                                            player_in_turn_id = None
                                            player_init_buy_id = None
                                            # Compra bloqueada silenciosamente (propio descarte)

                                    elif jugador_local.playerId in players_for_buy_ids:
                                        print(f" NO SE QUE ES ESTO... elif de comprar carta...")
                                        noBuy = False
                                        waiting = False
                                        time_waiting = None
                                        # player_in_turn = players.index(players[siguiente_idx])
                                        player_in_turn_id = players[siguiente_idx].playerId
                                        # players[player_in_turn_id].playerTurn = True
                                        for idx, p in enumerate(players):
                                            
                                            players[idx].playerTurn = False

                                            if p.playerId == player_in_turn_id:
                                                players[idx].playerTurn = True
                                                if p.playerId == jugador_local.playerId:
                                                    jugador_local.playerTurn = True
                                            else:
                                                players[idx].playerTurn = False
                                                #jugador_local.playerTurn = False
                                            
                                        player_init_buy_id = jugador_local.playerId

                                        # players_for_buy[player_in_turn].playerTurn = True

                                        msgIniciarCompra = {
                                            "type": "INICIAR_COMPRA",
                                            "playerId": jugador_local.playerId,
                                            "playerName": jugador_local.playerName,
                                            "players_for_buy_ids": players_for_buy_ids,
                                            "player_in_turn_id": player_in_turn_id,
                                            "player_init_buy_id": player_init_buy_id
                                        }

                                        mostrar_boton_comprar = False

                                        print(f"Lista de jugadores para compra: {players_for_buy_ids}")
                                        print(f"Jugador en turno de compra: {[p for p in players if p.playerTurn]}")

                                        if network_manager.is_host:
                                            network_manager.broadcast_message(msgIniciarCompra)
                                        else:
                                            network_manager.sendData(msgIniciarCompra)
                                        
                                        mensaje_temporal = "Has iniciado el ciclo de compra. Esperando decision de los otros jugadores."
                                        mensaje_tiempo = time.time()
                                        print(f"Mensje temporal... {mensaje_temporal}")
                                        print(f"Mensje tiempo... {mensaje_tiempo}")
                                    else:
                                        mensaje_temporal = "Un jugador mas cercano al MANO quiere comprar."
                                        mensaje_tiempo = time.time()
                                        print(f"Mensje temporal... {mensaje_temporal}")
                                        print(f"Mensje tiempo... {mensaje_tiempo}")
                                        continue
                                else:

                                    mensaje_temporal = "El jugador MANO aún no ha elegido una carta."
                                    mensaje_tiempo = time.time()
                                    print(f"Mensje temporal... {mensaje_temporal}")
                                    print(f"Mensje tiempo... {mensaje_tiempo}")
                                    continue
                            else:
                                mensaje_temporal = "El ciclo de compra ha finalizado."
                                mensaje_tiempo = time.time()
                                print(f"Mensje temporal... {mensaje_temporal}")
                                print(f"Mensje tiempo... {mensaje_tiempo}")
                                continue
                        else:
                            mensaje_temporal = "Botón inhabilitado: eres el jugador MANO."
                            mensaje_tiempo = time.time()
                            continue

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging_board_joker and board_joker_data:
                    mouse_x, mouse_y = event.pos
                    owner_p = board_joker_data["owner"]
                    
                    # 1. Simular la jugada resultante
                    temp_cards = list(board_joker_data["straight_ref"])
                    joker_card = temp_cards.pop(board_joker_data["original_idx"])
                    
                    # Si estaba en el índice 0, se mueve al final, y viceversa
                    if board_joker_data["original_idx"] == 0:
                        temp_cards.append(joker_card)
                    else:
                        temp_cards.insert(0, joker_card)
                    
                    # 2. VALIDACIÓN CRÍTICA: ¿La jugada resultante en la mesa AJENA es válida?
                    if jugador_local.isValidStraightFJoker(temp_cards):
                        # Si es válida, procedemos con el cambio real y la sincronización
                        owner_p.executeJokerSwap(board_joker_data["play_index"], temp_cards)
                        
                        msgSwap = {
                        "type": "SWAP_JOKER",
                        "playerId": owner_p.playerId,
                        "playIndex": board_joker_data["play_index"],
                        "playMade": owner_p.playMade, 
                        "jugadas_bajadas": owner_p.jugadas_bajadas
                        }
                                    
                        if network_manager.is_host:
                            network_manager.broadcast_message(msgSwap)
                        else:
                            network_manager.sendData(msgSwap)
                            
                        mensaje_temporal = f"Joker movido legalmente en la mesa de {owner_p.playerName}."
                    else:
                        # Si no es válida, cancelamos el movimiento
                        mensaje_temporal = "Movimiento inválido: El Joker no puede representar ese valor."
                        mensaje_tiempo = time.time()

                    # Reset de estados
                    dragging_board_joker = False
                    dragging = False
                    board_joker_data = None
                    carta_arrastrada = None

                # aca lo que cambia es que antes todo lo que estaba aca se paso dentro de If
                if dragging:
                    if carta_arrastrada is not None:
                        mouse_x, mouse_y = event.pos
                        nueva_pos = None
                        drop_handled = False 
                        for nombre, rect in cuadros_interactivos.items():
                            if nombre.startswith("Carta_") and rect.collidepoint(mouse_x, mouse_y):
                                idx = int(nombre.split("_")[1])
                                nueva_pos = idx
                                string_to_card(nombre)
                                break

                        # Detectar si se soltó sobre una caja de "bajada" (baj1..baj7)
                        drop_bajada = None
                        for nombre_box, rect_box in boxes.items():
                            if nombre_box.startswith("baj") and rect_box.collidepoint(mouse_x, mouse_y):
                                drop_bajada = nombre_box
                                break
                        # Detectar si se soltó sobre una caja de "bajada" (baj1..baj7)

                        # Resolver jugador objetivo consultando el mapeo baj_box_to_player (construido arriba)
                        def player_for_bajada(baj_name):
                            if not baj_name:
                                return None, None
                            target_player = baj_box_to_player.get(baj_name)
                            if target_player:
                                try:
                                    idx = players.index(target_player)
                                    return target_player, idx
                                except ValueError:
                                    return target_player, None
                            # fallback por índice si no está en el mapa
                            try:
                                idx = int(baj_name[3:]) - 1
                                if 0 <= idx < len(players):
                                    return players[idx], idx
                            except Exception:
                                pass
                            return None, None


                        # Normalizar carta a objeto Card
                        carta_obj = string_to_card(carta_arrastrada)
                        send = False
                        insertado_en_jugada = False
                        if drop_bajada:
                            insertado_en_jugada = False
                            target_player, target_idx = player_for_bajada(drop_bajada)
                            
                            if target_player:
                                mouse_pos = pygame.Vector2(mouse_x, mouse_y)
                                plays_del_objetivo = rects_jugadas.get(target_player.playerName, [])
                                
                                jugada_detectada = None
                                distancia_minima = float('inf')

                                for info in plays_del_objetivo:
                                    # 1. Aumentamos el "imán" (margen) para que sea más fácil acertar al soltar rápido
                                    margen_extra_ancho = info["rect_total"].width * 0.3 + 80
                                    margen_extra_alto = info["rect_total"].height * 0.3 + 80
                                    area_sensible = info["rect_total"].inflate(margen_extra_ancho, margen_extra_alto)
                                    
                                    # 2. CREAMOS EL RECTÁNGULO ACTUAL DE LA CARTA QUE LLEVAS EN LA MANO
                                    # Usamos las dimensiones de drag_rect para tener una superficie de contacto real
                                    rect_carta_actual = pygame.Rect(
                                        mouse_x - drag_offset_x, 
                                        mouse_y - (drag_rect.height // 2), 
                                        drag_rect.width, 
                                        drag_rect.height
                                    )
                                    
                                    # 3. CAMBIO CLAVE: Usamos colliderect (choque de áreas) en lugar de collidepoint (punto)
                                    if area_sensible.colliderect(rect_carta_actual):
                                        # Calculamos distancia al centro para elegir la mejor jugada si están cerca
                                        centro_jugada = pygame.Vector2(info["rect_total"].center)
                                        centro_carta = pygame.Vector2(rect_carta_actual.center)
                                        distancia = centro_jugada.distance_to(centro_carta)
                                        
                                        if distancia < distancia_minima:
                                            distancia_minima = distancia
                                            jugada_detectada = info
                                            play_index_real = info["play_index"]
                                # --- 1. DETECCIÓN DE JUGADA ---
                                if jugada_detectada:
                                    play_index_real = jugada_detectada["play_index"]
                                    target_player_fresh = target_player # El objeto jugador ya tiene los datos actualizados
                                    
                                    # Extraer la lista de cartas real del backend para evitar el lag de la UI
                                    cartas_en_mesa_frescas = []
                                    raw_play = target_player_fresh.playMade[play_index_real]
                                    if isinstance(raw_play, dict):
                                        cartas_en_mesa_frescas = raw_play.get("straight") or raw_play.get("trio") or []
                                    else:
                                        cartas_en_mesa_frescas = raw_play

                                    tipo = jugada_detectada["tipo"]
                                    intentado = False
                                    # Solo si NO pudo entrar en los extremos, intentamos la sustitución.
                                    if not intentado and tipo == "straight":
                                        if not getattr(carta_obj, "joker", False):
                                            for idx_c, c_mesa in enumerate(cartas_en_mesa_frescas):
                                                if getattr(c_mesa, "joker", False):
                                                    # Probamos si la carta actual sirve para reemplazar ese Joker específico
                                                    temp_test = list(cartas_en_mesa_frescas)
                                                    temp_test[idx_c] = carta_obj
                                                    
                                                    if jugador_local.isValidStraightFJoker(temp_test):
                                                        # Solo sustituimos si el usuario soltó la carta cerca de la posición del Joker
                                                        # (Opcional: puedes quitar esta condición de colisión si quieres que sea automático)
                                                        ok = safe_insert_card(jugador_local, target_player, play_index_real, carta_obj, None, tipo,joker_index=idx_c)
                                                        if ok:
                                                            mensaje_temporal = "¡Joker sustituido y devuelto a la mano!"
                                                            intentado = True
                                                            break

                                    # --- 2. PRIORIDAD 1: EXPANDIR LA SECUENCIA (Poner a los lados) ---
                                    # Esto evita que el Joker sea sustituido si la carta puede ir al principio o al final.
                                    temp_inicio = [carta_obj] + list(cartas_en_mesa_frescas)
                                    temp_final = list(cartas_en_mesa_frescas) + [carta_obj]
                                    
                                    valido_inicio = False
                                    valido_final = False

                                    if tipo == "straight":
                                        valido_inicio = jugador_local.isValidStraightFJoker(temp_inicio)
                                        valido_final = jugador_local.isValidStraightFJoker(temp_final)
                                    else: # Es un Trio
                                        valido_final = jugador_local.isValidTrioF(temp_final)

                                    if valido_inicio:
                                        ok = safe_insert_card(jugador_local, target_player, play_index_real, carta_obj, "start", tipo)
                                        if ok: 
                                            mensaje_temporal = "Insertada exitosamente"
                                            intentado = True
                                    elif valido_final:
                                        ok = safe_insert_card(jugador_local, target_player, play_index_real, carta_obj, "end", tipo)
                                        if ok: 
                                            mensaje_temporal = "Insertada exitosamente"
                                            intentado = True

            

                                    # --- 4. FINALIZACIÓN Y RED ---
                                    if intentado:
                                        mensaje_tiempo = time.time()
                                        insertado_en_jugada = True

                                        last_inserted_card_data = {
                                            'target_player': target_player,
                                            'play_index': play_index_real,
                                            'card': carta_obj,
                                            'tipo': tipo # 'trio' o 'straight'
                                        }
                                        
                                        if getattr(carta_obj, "joker", False):
                                            if target_player.playerId not in jokers_insertados_este_turno:
                                                jokers_insertados_este_turno.append(target_player.playerId)
                                        if carta_arrastrada in visual_hand:
                                            visual_hand.remove(carta_arrastrada)
                                        reiniciar_visual(jugador_local, visual_hand, cuadros_interactivos, cartas_ref)
                                        
                                        # Enviar actualización de red (Asegúrate de que este mensaje incluya el nuevo estado)
                                        msgInsertar = {
                                            "type": "INSERTAR_CARTA",
                                            "playerHand": jugador_local.playerHand,
                                            "jugadas_bajadas": target_player.jugadas_bajadas,
                                            "playMade": target_player.playMade,
                                            "playerId": target_player.playerId,
                                            "playerId2": jugador_local.playerId,
                                            "round": round
                                        }
                                        if network_manager.is_host:
                                            network_manager.broadcast_message(msgInsertar)
                                        else:
                                            network_manager.sendData(msgInsertar)
                                    else:
                                        if not jugador_local.isHand:
                                            mensaje_temporal = "No puedes insertar sino es tu turno"
                                            mensaje_tiempo = time.time()
                                        elif not jugador_local.downHand:
                                            mensaje_temporal = "Para poder insertar, debes haberte bajado"
                                            mensaje_tiempo = time.time()  
                                        elif not jugador_local.cardDrawn:
                                            mensaje_temporal = "Debes tomar una carta antes de insertar"
                                            mensaje_tiempo = time.time()
                                        else:   
                                            mensaje_temporal = "La carta no encaja en esta jugada."
                                            mensaje_tiempo = time.time()
                        # 3) Si no se insertó en jugada, chequear zonas Trio/Seguidilla/Descarte centrales
                        if not insertado_en_jugada:
                            # --- DIBUJO DINÁMICO DE CARTAS EN LA MESA (REEMPLAZO) ---
                            zona_detectada = False
                            nombres_fase = mapping_nombres.get(fase, ["Trio", "Seguidilla"])
                            
                            for nombre_zona, rect_zona in cuadros_interactivos.items():
                                if rect_zona.collidepoint(mouse_x, mouse_y):
                                    
                                    # Si el cuadro en el que soltamos está en los permitidos para esta ronda
                                    if nombre_zona in nombres_fase:
                                        idx_zona = nombres_fase.index(nombre_zona)
                                        zona_cartas[idx_zona].append(carta_arrastrada)
                                        zona_detectada = True
                                        drop_handled = True # <--- MARCAR COMO MANEJADO#carlos
                                    # --- Lógica especial para el DESCARTE ---
                                    elif "Descarte" in nombre_zona:
                                        # El descarte siempre es el último índice habilitado
                                        idx_desc = 3 if (roundThree or roundFour) else 2
                                        while len(zona_cartas) <= idx_desc:
                                            zona_cartas.append([])
                                        zona_cartas[idx_desc].append(carta_arrastrada)
                                        zona_detectada = True
                                        drop_handled = True # <--- MARCAR COMO MANEJADO#carlos
                                    elif nueva_pos is not None and organizar_habilitado:
                                        if carta_arrastrada in visual_hand:
                                            visual_hand.remove(carta_arrastrada)
                                        if mouse_x < cuadros_interactivos[f"Carta_{nueva_pos}"].centerx:
                                            visual_hand.insert(nueva_pos, carta_arrastrada)
                                        else:
                                            visual_hand.insert(nueva_pos + 1, carta_arrastrada)
                                        # --- AQUÍ SÍ LA MOSTRAMOS ---#carlos
                                        # Como la soltamos en la mano, hay que quitarla de cartas_ocultas
                                        actualizar_indices_visual_hand(visual_hand) # Reasignar IDs visuales
                                        if carta_arrastrada in visual_hand:
                                            new_idx = visual_hand.index(carta_arrastrada)
                                            if new_idx in cartas_ocultas:
                                                cartas_ocultas.remove(new_idx)
                                        
                                        drop_handled = True #carlos
                                    
                                    elif nueva_pos is not None and not organizar_habilitado:
                                        mensaje_temporal = "No puedes organizar una carta mientras ejecutas una jugada."
                                        mensaje_tiempo = time.time()

                                    if zona_detectada:
                                        if carta_arrastrada in visual_hand:
                                            cartas_ocultas.add(visual_hand.index(carta_arrastrada))
                                        organizar_habilitado = False
                                        break
                    # --- FALLBACK FINAL (Soltó en la nada) ---
                    # Si no se soltó en zona válida ni se reorganizó en la mano,
                    # la devolvemos a su estado visible en la mano.
                    #carlos
                    if not drop_handled and carta_arrastrada is not None:
                        if carta_arrastrada in visual_hand:
                            idx_return = visual_hand.index(carta_arrastrada)
                            if idx_return in cartas_ocultas:
                                cartas_ocultas.remove(idx_return)
                    #carlos
                    # siempre limpiar arrastre
                    dragging = False
                    carta_arrastrada = None
                    drag_rect = None
                '''try:
                    # Intercambiar la sublista que contiene '2' con la que contiene '4', si ambas existen
                    try:
                        idx2 = next((i for i, z in enumerate(zona_cartas) if any(str(c).startswith('2') for c in z)), None)
                        idx4 = next((i for i, z in enumerate(zona_cartas) if any(str(c).startswith('4') for c in z)), None)
                        if idx2 is not None and idx4 is not None and idx2 != idx4:
                            zona_cartas[idx2], zona_cartas[idx4] = zona_cartas[idx4], zona_cartas[idx2]
                    except Exception:
                        pass

                    print("DEBUG drag end -> zona_cartas:", [[str(c) for c in z] for z in zona_cartas])
                except Exception:
                    print("DEBUG drag end -> zona_cartas (raw):", zona_cartas)'''
            elif event.type == pygame.MOUSEMOTION and dragging:
                pass  # El dibujo se maneja abajo
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Click derecho
                for zona in zona_cartas:
                    for carta in zona:
                        if carta not in visual_hand:
                            visual_hand.append(carta)
                zona_cartas = [[], [], [],[]]
                cartas_ocultas.clear()
                organizar_habilitado = True  # Vuelve a habilitar organización
        # Fin evento de pygame...

        if jugador_local.playerTurn and jugador_local.playerId == player_init_buy_id:
            print(f" Fuera del evento PYGAME...")
            bought = False
            # noBuy = True
            jugador_local.playerTurn = False
            jugador_local.playerBuy = True
            player_in_turn_id = None
            player_init_buy_id = None
            buy_finished = True
            time_confirm = time.time()

            msgRealizarCompraC = {
                "type": "REALIZAR_COMPRA",
                "playerId": jugador_local.playerId,
                "playerName": jugador_local.playerName,
            }

            for idx, p in enumerate(players):
                players[idx].playerTurn = False
                #jugador_local.playerTurn = False

            if network_manager.is_host:
                network_manager.broadcast_message(msgRealizarCompraC)
            else:
                network_manager.sendData(msgRealizarCompraC)

            mensaje_temporal = "Procesando compra..."
            mensaje_tiempo = time.time()
            print(f"Mensje temporal... {mensaje_temporal}")
            print(f"Mensje tiempo... {mensaje_tiempo}")
                                

        elif jugador_local.playerTurn:
            print(f" AQUI SALIO LA PANTALLITA.... wiiiiiiiii \o/..")
            
            card_to_show = mazo_descarte[-1] if mazo_descarte else None
            
            # VALIDAR: No mostrar modal si la carta es del propio jugador
            if card_to_show and getattr(card_to_show, "discarded_by", None) == jugador_local.playerId:
                print(f"[VALIDACION] Carta descartada por {jugador_local.playerName}, auto-pasando compra")
                # Auto-pasar sin mostrar modal
                wants = False
            else:
                wants = confirm_buy_card(screen, card_to_show, WIDTH, HEIGHT, ASSETS_PATH, font)
            
            print(f"wants:  {wants}")
            if wants:
                print(" ADENTRO DE wants... ")
            
                bought = False
                # noBuy = True
                jugador_local.playerTurn = False
                jugador_local.playerBuy = True
                player_in_turn_id = None
                player_init_buy_id = None
                buy_finished = True
                time_confirm = time.time()

                msgRealizarCompraC = {
                    "type": "REALIZAR_COMPRA",
                    "playerId": jugador_local.playerId,
                    "playerName": jugador_local.playerName,
                }

                for idx, p in enumerate(players):
                    players[idx].playerTurn = False
                    #jugador_local.playerTurn = False

                if network_manager.is_host:
                    network_manager.broadcast_message(msgRealizarCompraC)
                else:
                    network_manager.sendData(msgRealizarCompraC)

                mensaje_temporal = "Procesando compra..."
                mensaje_tiempo = time.time()
                print(f"Mensje temporal... {mensaje_temporal}")
                print(f"Mensje tiempo... {mensaje_tiempo}")
            else:
                print(f"NO SE QUE PASA AQUI.... Ahhhh!")
            
                jugador_local.playerTurn = False
                # player_init_buy = None
                list_confirm_ids.append(jugador_local.playerId)

                current_buy_pos = players_for_buy_ids.index(jugador_local.playerId)
                next_buy_id_pos = (current_buy_pos + 1) % len(players_for_buy_ids)
                next_buy_id = players_for_buy_ids[next_buy_id_pos] #.playerId

                for idx, p in enumerate(players):

                    players[idx].playerTurn = False

                    if p.playerId == next_buy_id:
                        players[idx].playerTurn = True

                msgPasarCompraC = {
                    "type": "PASAR_COMPRA",
                    "playerId": jugador_local.playerId,
                    "playerName": jugador_local.playerName,
                    "current_buy_id": jugador_local.playerId,
                    "list_confirm_ids": list_confirm_ids
                }

                if network_manager.is_host:
                    network_manager.broadcast_message(msgPasarCompraC)
                else:
                    network_manager.sendData(msgPasarCompraC)

                mensaje_temporal = "Has pasado de la compra."
                mensaje_tiempo = time.time()
                print(f"Mensje temporal... {mensaje_temporal}")
                print(f"Mensje tiempo... {mensaje_tiempo}")
                
            

        if buy_finished and (time.time() - time_confirm) > (3 * (len(list_confirm_ids) + 0)):
            print("Ciclo de compra finalizado con mas de 2 jugadores.")
            print(f"(buy_finished, {buy_finished}), (time_confirm, {time_confirm}), (list_confirm_ids, {list_confirm_ids})")
            print(f"playerBuy del jugador_local: {jugador_local.playerBuy}")
            if jugador_local.playerBuy:
                jugador_mano_actual = [p for p in players if p.isHand][0] # Encontramos al jugador MANO actualmente

                # Encontramos la posicion del jugador local en la lista de jugadores (el que activo la compra de cartas)
                indice_jugador_local = None
                for idx, player in enumerate(players):
                    if player.playerId == jugador_local.playerId:
                        indice_jugador_local = idx
                        break
                                        
                # Buscamos la posicion del jugador MANO en la lista de jugadores y calculamos el indice que le sigue.
                indice_mano_actual = None
                siguiente_idx = None
                for idx, player in enumerate(players):
                    if player.playerId == jugador_mano_actual.playerId:
                        indice_mano_actual = idx
                        siguiente_idx = (idx + 1) % len(players)
                        break

                # Indicamos que el jugador compra la carta.
                #jugador_local.playerBuy = True
                print(f"Pila antes de compra: {[c for c in round.pile]}")

                # Validamos que el mazo tenga cartas antes de la compra.
                if not deckForRound or len(deckForRound) == 0:
                    print(f"DECKFORROUND VACÍOOOOOO: {[c for c in deckForRound]}")
                    refillDeck(round)
                    deckForRound = round.pile
                    mazo_descarte = round.discards 

                    print(f"DECKFORROUND Recargado :)\nAntes de realizar la compra efectiva (compra iniciada por un jugador lejano)...:\n {[c for c in deckForRound]}")

                cards_bought = jugador_local.buyCard(round)
                print(f"Pila despues de compra: {[c for c in round.pile]}")

                # Recargamos el mazo, si se termina luego de la compra.
                if not deckForRound or len(deckForRound) == 0:
                    print(f"DECKFORROUND VACÍOOOOOO: {[c for c in deckForRound]}")
                    refillDeck(round)
                    deckForRound = round.pile
                    mazo_descarte = round.discards 

                    print(f"DECKFORROUND Recargado :)\nDespues de realizar la compra efectiva (compra iniciada por un jugador lejano)...:\n {[c for c in deckForRound]}")

                jugador_local.playerBuy = False
                if cards_bought is not None:
                    # CASO: COMPRA EXITOSA
                    cartas_ocultas.clear()
                    numero = 0
                    if roundOne or roundTwo:
                        numero = 2
                    elif roundThree or roundFour:
                        numero = 3
                    zona_cartas[numero] = [] # Limpiamos la zona de descartes.
                    print(f"Mano del jugador que compro: {jugador_local.playerHand}")

                    # Asignamos una carta del mazo al MANO actual.
                    cardTaken = drawCard(jugador_mano_actual, round, False)
                                            
                    jugador_mano_actual.playerHand = round.hands[jugador_mano_actual.playerId]
                    jugador_mano_actual.cardDrawn = True
                    jugador_mano_actual.playerPass = False

                    # Recargamos el mazo, si se termina luego de que el MANO tome del mazo.
                    if not deckForRound or len(deckForRound) == 0:
                        print(f"DECKFORROUND VACÍOOOOOO: {[c for c in deckForRound]}")
                        refillDeck(round)
                        deckForRound = round.pile
                        mazo_descarte = round.discards 

                        print(f"DECKFORROUND Recargado :)\nDespues de asignar una carta al MANO luego de la compra efectiva (compra iniciada por un jugador lejano)...:\n {[c for c in deckForRound]}")

                    players[indice_mano_actual].isHand = True
                    players[indice_jugador_local].isHand = False

                    for idx, carta in enumerate(jugador_local.playerHand):
                        carta.id_visual = idx
                        visual_hand.append(carta)

                    reiniciar_visual(jugador_local, visual_hand, cuadros_interactivos, cartas_ref)
                    mazo_descarte = round.discards
                    deckForRound = round.pile

                    msgComprarC = {
                        "type": "COMPRAR_CARTA",
                        "playerHand": jugador_local.playerHand,
                        "playerId": jugador_local.playerId,
                        "playerName": jugador_local.playerName,
                        "mazo_descarte": mazo_descarte,#  El mazo se debe actualizar
                        "deckForRound": deckForRound,
                        "zona_cartas": zona_cartas,
                        "round": round,
                        "playerId_Hand": jugador_mano_actual.playerId,    # Dato extra
                        "playerHand_Hand": jugador_mano_actual.playerHand # Dato extra
                    }

                    for idx, p in enumerate(players):
                        players[idx].playerTurn = False

                    noBuy = True
                    bought = True
                    players_for_buy_ids = []
                    player_in_turn_id = None
                    player_init_buy_id = None
                    buy_finished = False
                    time_confirm = None
                    list_confirm_ids =[]

                    if network_manager.is_host:
                        network_manager.broadcast_message(msgComprarC)
                    else:
                        network_manager.sendData(msgComprarC)

                    mensaje_temporal = "Has comprado la carta."
                    mensaje_tiempo = time.time()
                    print(f"Mensje temporal... {mensaje_temporal}")
                    print(f"Mensje tiempo... {mensaje_tiempo}")
                else:
                    # CASO: COMPRA FALLIDA (ej. propio descarte)
                    # Resetear variables del ciclo de compra para no quedar atascado
                    noBuy = True
                    bought = True
                    players_for_buy_ids = []
                    player_in_turn_id = None
                    player_init_buy_id = None
                    buy_finished = False
                    time_confirm = None
                    list_confirm_ids = []
                    
                    # Resetear turnos de compra
                    for idx, p in enumerate(players):
                        players[idx].playerTurn = False
        if waiting and (time.time() - time_waiting) > 8 and noBuy:
            print(f"Temporizador, waiting, time_waiting, noBuy: ({waiting}, {time_waiting}, {noBuy})")

            if jugador_local.isHand:

                print("FINALIZO EL TIEMPO, VALEEEEE!")

                bought = True
                waiting = False
                time_waiting = None
                jugador_local.playerPass = False

                if not deckForRound or len(deckForRound) == 0:
                    print(f"DECKFORROUND VACÍOOOOOO: {[c for c in deckForRound]}")
                    refillDeck(round)
                    deckForRound = round.pile
                    mazo_descarte = round.discards 

                    print(f"DECKFORROUND Recargado :)\nAntes de que el MANO tome una carta (no hubo compras)...:\n {[c for c in deckForRound]}")

                #print(f"jugadors {[p for p in players]}")
                #print(f"El jugador local {jugador_local}")
                cardTaken = drawCard(jugador_local, round, False)
                #jugador_local.playerHand.append(cardTaken)
                jugador_local.playerHand = round.hands[jugador_local.playerId]
                jugador_local.cardDrawn = True
                #print(f"DEPURACION DECKFORROUND AL TOMAR CARTA: {[c for c in deckForRound]}")

                if not deckForRound or len(deckForRound) == 0:
                    print(f"DECKFORROUND VACÍOOOOOO: {[c for c in deckForRound]}")
                    refillDeck(round)
                    deckForRound = round.pile
                    mazo_descarte = round.discards 

                    print(f"DECKFORROUND Recargado :)\nDespues de que el MANO tome una carta (no hubo compras)...:\n {[c for c in deckForRound]}")
                                

                msgTomarC = {
                    "type": "TOMAR_CARTA",
                    "cardTaken": cardTaken,
                    "playerHand": jugador_local.playerHand,
                    "playerId": jugador_local.playerId,
                    "mazo": deckForRound, #  El mazo se debe actualizar
                    "round": round
                    }
                            
                jugador_local.playerPass = False
                bought = True

                if network_manager.is_host:
                    network_manager.broadcast_message(msgTomarC)
                elif network_manager.player:
                    network_manager.sendData(msgTomarC)

        process_received_messagesUi2()  
        #------ Hasta aqui el bucle de event de PYGAME ------------
        if not running:
            break
        # Sincroniza visual_hand con el backend si hay nuevas cartas
        if len(visual_hand) != len(jugador_local.playerHand) or any(c not in visual_hand for c in jugador_local.playerHand):
            # Añade nuevas cartas al final de visual_hand
            for c in jugador_local.playerHand:
                if c not in visual_hand and c not in cartas_apartadas:
                    visual_hand.append(c)
            # Elimina cartas que ya no están
            visual_hand = [c for c in visual_hand if c in jugador_local.playerHand and c not in cartas_apartadas]

        # Dibujar fondo
        #screen.blit(fondo_img, (0, 0))

        # Fondo Joker temporal
        if mostrar_joker_fondo and pygame.time.get_ticks() - tiempo_joker_fondo < 3000:
            pass
            screen.blit(joker_fondo_img, (0, 0))
        else:
            pass
            mostrar_joker_fondo = False
            screen.blit(fondo_img, (0, 0))

        def draw_player_turn_highlights():
            """Dibuja un resaltado muy sutil (debajo de todo) sobre la caja del jugador que tenga el turno."""
            try:
                alpha = 80  # casi invisible pero perceptible
                color = (255, 0, 0, alpha)
                for p in players:
                    if not getattr(p, "isHand", False):
                        continue
                    hl_rect = None
                    # jugador local -> jug1
                    if p is jugador_local:
                        hl_rect = boxes.get("jug1")
                    # buscar en listas laterales/superiores
                    if hl_rect is None:
                        found = next((r for pp, r in jugadores_laterales if getattr(pp, "playerName", None) == getattr(p, "playerName", None)), None)
                        if found:
                            hl_rect = found
                    if hl_rect is None:
                        found = next((r for pp, r in jugadores_superiores if getattr(pp, "playerName", None) == getattr(p, "playerName", None)), None)
                        if found:
                            hl_rect = found
                    # fallback por índice
                    if hl_rect is None:
                        try:
                            idx = players.index(p)
                            hl_rect = boxes.get(f"jug{idx+1}")
                        except Exception:
                            hl_rect = None
                    if not hl_rect:
                        continue
                    # Ajuste: para jug1 queremos que el resaltado sea menos ancho; para otros, sobresalga un poco
                    if p is jugador_local and hl_rect == boxes.get("jug1"):
                        # menos ancho => inflar negativamente en X
                        rect_to_draw = hl_rect.inflate(-110, 6).clip(pygame.Rect(0, 0, WIDTH, HEIGHT))
                    else:
                        rect_to_draw = hl_rect.inflate(6, 6).clip(pygame.Rect(0, 0, WIDTH, HEIGHT))
                    if rect_to_draw.width <= 0 or rect_to_draw.height <= 0:
                        continue
                    s = pygame.Surface((rect_to_draw.width, rect_to_draw.height), pygame.SRCALPHA)
                    s.fill((0, 0, 0, 0))  # transparente de fondo
                    # radio de esquina: proporcional al tamaño (aprox 1/6 de la menor dimensión)
                    border_radius = max(2, int(min(rect_to_draw.width, rect_to_draw.height) / 6))
                    pygame.draw.rect(s, color, s.get_rect(), border_radius=border_radius)
                    # NOTA: esta llamada se realiza antes de dibujar cartas para quedar debajo de todo
                    screen.blit(s, rect_to_draw.topleft)
            except Exception:
                pass

        # Cálculo de tamaños relativos
        bajada_h = int(HEIGHT * bajada_h_pct)
        bajada_w = int(WIDTH * bajada_w_pct)
        jug_w = int(WIDTH * jug_w_pct)
        jug_h = int(HEIGHT * jug_h_pct)
        
        # --- Inferior (Jugador 1) ---
        # Hacemos J1 más ancho (horizontalmente) y más alto (verticalmente)
        extra_ancho_j1 = int(WIDTH * 0.18)  # Más ancho horizontalmente
        extra_alto_j1 = int(HEIGHT * 0.06)  # Más alto verticalmente
        jug1 = pygame.Rect(
            jug_w + bajada_w - extra_ancho_j1 // 2,
            HEIGHT - jug_h - extra_alto_j1 // 2,
            WIDTH - 2 * (jug_w + bajada_w) + extra_ancho_j1,
            jug_h + extra_alto_j1
        )
        boxes["jug1"] = jug1
        # draw_transparent_rect(screen, CAJA_JUG, jug1)
        # draw_label(jug1, "J1")
        # cuadros_interactivos["J1"] = jug1
        #bajada_h = int(HEIGHT * (bajada_h_pct + 0.05))  # ahora será 17.5% de la altura total
        # B1 igual de ancho que antes, para no chocar con las cajas laterales
        baj1 = pygame.Rect(
            jug_w + bajada_w,
            HEIGHT - jug_h - bajada_h,
            WIDTH - 2 * (jug_w + bajada_w),
            bajada_h
        )
        boxes["baj1"] = baj1
        # draw_transparent_rect(screen, CAJA_BAJ, baj1)
        # draw_label(baj1, "B1")
        cuadros_interactivos["B1"] = baj1

        # --- Izquierda (Jugadores 2 y 3) --- (INVERTIDO: J2 más cerca del centro, J3 arriba)
        lado_total_h = HEIGHT - jug_h - bajada_h
        lado_h = lado_total_h // 2

        # J3 ARRIBA
        jug3 = pygame.Rect(0, jug_h, jug_w, lado_h)
        boxes["jug3"] = jug3
        # draw_transparent_rect(screen, CAJA_JUG, jug3)
        # draw_label(jug3, "J3")
        cuadros_interactivos["J3"] = jug3

        baj3 = pygame.Rect(jug_w, jug_h, bajada_w, lado_h)
        boxes["baj3"] = baj3
        # draw_transparent_rect(screen, CAJA_BAJ, baj3)
        # draw_label(baj3, "B3")
        cuadros_interactivos["B3"] = baj3

        # J2 ABAJO (más cerca del centro)
        jug2 = pygame.Rect(0, jug_h + lado_h, jug_w, lado_h)
        boxes["jug2"] = jug2
        # draw_transparent_rect(screen, CAJA_JUG, jug2)
        # draw_label(jug2, "J2")
        cuadros_interactivos["J2"] = jug2

        baj2 = pygame.Rect(jug_w, jug_h + lado_h, bajada_w, lado_h)
        boxes["baj2"] = baj2
        # draw_transparent_rect(screen, CAJA_BAJ, baj2)
        # draw_label(baj2, "B2")
        cuadros_interactivos["B2"] = baj2

        # --- Derecha (Jugadores 6 y 7) ---
        jug6 = pygame.Rect(WIDTH - jug_w, jug_h, jug_w, lado_h)
        boxes["jug6"] = jug6
        # draw_transparent_rect(screen, CAJA_JUG, jug6)
        # draw_label(jug6, "J6")
        cuadros_interactivos["B6"] = jug6

        baj6 = pygame.Rect(WIDTH - jug_w - bajada_w, jug_h, bajada_w, lado_h)
        boxes["baj6"] = baj6
        # draw_transparent_rect(screen, CAJA_BAJ, baj6)
        # draw_label(baj6, "B6")
        cuadros_interactivos["B6"] = baj6

        jug7 = pygame.Rect(WIDTH - jug_w, jug_h + lado_h, jug_w, lado_h)
        boxes["jug7"] = jug7
        # draw_transparent_rect(screen, CAJA_JUG, jug7)
        # draw_label(jug7, "J7")
        cuadros_interactivos["B7"] = jug7

        baj7 = pygame.Rect(WIDTH - jug_w - bajada_w, jug_h + lado_h, bajada_w, lado_h)
        boxes["baj7"] = baj7

        # Dibujar resaltados sutiles de turno sobre cajas de jugador (debajo de cartas/nombres)
        draw_player_turn_highlights()
        # draw_transparent_rect(screen, CAJA_BAJ, baj7)
        # draw_label(baj7, "B7")
        cuadros_interactivos["B7"] = baj7

        # --- Arriba (Jugadores 4 y 5) ---
        arriba_total_w = WIDTH - 2 * (jug_w + bajada_w)
        arriba_w = arriba_total_w // 2

        jug4 = pygame.Rect(jug_w + bajada_w, 0, arriba_w, jug_h)
        boxes["jug4"] = jug4
        # draw_transparent_rect(screen, CAJA_JUG, jug4)
        # draw_label(jug4, "J4")
        cuadros_interactivos["J4"] = jug4

        baj4 = pygame.Rect(jug_w + bajada_w, jug_h, arriba_w, bajada_h)
        boxes["baj4"] = baj4
        # draw_transparent_rect(screen, CAJA_BAJ, baj4)
        # draw_label(baj4, "B4")
        cuadros_interactivos["B4"] = baj4

        jug5 = pygame.Rect(jug_w + bajada_w + arriba_w, 0, arriba_w, jug_h)
        boxes["jug5"] = jug5
        # draw_transparent_rect(screen, CAJA_JUG, jug5)
        # draw_label(jug5, "J5")
        cuadros_interactivos["J5"] = jug5

        baj5 = pygame.Rect(jug_w + bajada_w + arriba_w, jug_h, arriba_w, bajada_h)
        boxes["baj5"] = baj5
        # draw_transparent_rect(screen, CAJA_BAJ, baj5)
        # draw_label(baj5, "B5")
        cuadros_interactivos["B5"] = baj5

        # --- Área central (mesa) ---
        mesa_x = jug_w + bajada_w
        mesa_y = jug_h + bajada_h
        mesa_w = WIDTH - 2 * (jug_w + bajada_w)
        mesa_h = HEIGHT - 2 * (jug_h + bajada_h)
        mesa = pygame.Rect(mesa_x, mesa_y, mesa_w, mesa_h)
        boxes["mesa"] = mesa
        # draw_transparent_rect(screen, CENTRAL, mesa)
        # draw_label(mesa, "Mesa")  # Quitado para que no aparezca la palabra "Mesa"

        # --- RECUADROS EN LA MESA (UNO AL LADO DEL OTRO) ---
        margin = min(24, max(8, int(mesa_w * 0.01)))
        cuadro_w_fino = max(110, int(mesa_w * 0.16))
        cuadro_h = max(120, int(mesa_h * 0.45))
        cuadro_y = mesa_y + (mesa_h - cuadro_h) // 2
        cuadro_w_carta = min(220, max(120, int(mesa_w * 0.12)))
        cuadro_h_carta = int(cuadro_w_carta / 0.68)

        # Definimos el orden lógico de las casillas para esta ronda
        # Esto evita que el descarte "baile" o se mueva mal
        if fase == "ronda1":
            orden_casillas = ["Trio", "Seguidilla"]
        elif fase == "ronda2":
            orden_casillas = ["Seguidilla_0", "Seguidilla_1"]
        elif fase == "ronda3":
            orden_casillas = ["Trio_0", "Trio_1", "Trio_2"]
        elif fase == "ronda4":
            orden_casillas = ["Trio_0", "Trio_1", "Seguidilla"]
        else:
            orden_casillas = ["Trio", "Seguidilla"]

        # Añadimos siempre las fijas al final
        orden_casillas += ["Descarte", "Tomar descarte", "Tomar carta"]

        # Calculamos el ancho total para centrar todo el bloque
        total_width = 0
        for nombre in orden_casillas:
            total_width += (cuadro_w_fino if "Tomar" not in nombre else cuadro_w_carta)
        total_width += margin * (len(orden_casillas) - 1)

        start_x = mesa_x + (mesa_w - total_width) // 2
        current_x = start_x

        # Dibujamos y guardamos en el diccionario en UN SOLO PASO
        for nombre in orden_casillas:
            # Determinar tamaño
            w_uso = cuadro_w_fino if "Tomar" not in nombre else cuadro_w_carta
            h_uso = cuadro_h if "Tomar" not in nombre else cuadro_h_carta
            y_uso = mesa_y + (mesa_h - h_uso) // 2
            
            rect = pygame.Rect(current_x, y_uso, w_uso, h_uso)
            cuadros_interactivos[nombre] = rect # Aquí guardamos la zona para clic
            img_key = nombre.split('_')[0].lower() # trio, seguidilla, descarte...
            if "tomar" not in img_key:
                png_path = os.path.join(ASSETS_PATH, f"{img_key}.png")
                if os.path.exists(png_path):
                    img = pygame.image.load(png_path).convert_alpha()
                    img_scaled = pygame.transform.smoothscale(img, (w_uso - 8, h_uso - 8))
                    screen.blit(img_scaled, (current_x + 4, y_uso + 4))
            elif img_key == "tomar carta":
                # Lógica especial para el mazo boca abajo
                back_path = os.path.join(ASSETS_PATH, "cartas", "PT2.png")
                if os.path.exists(back_path):
                    img = pygame.transform.smoothscale(pygame.image.load(back_path).convert_alpha(), (w_uso-8, h_uso-8))
                    screen.blit(img, (current_x + 4, y_uso + 4))

            current_x += w_uso + margin
        boton_h = int(cuadro_h * 0.22)
        boton_y = cuadro_y - boton_h - 10 # 10 píxeles arriba de las casillas

        # 1. Botón "BAJARSE" (Se centra entre las dos primeras casillas)
        rect_1 = cuadros_interactivos.get(orden_casillas[0])
        rect_2 = cuadros_interactivos.get(orden_casillas[1])
        if rect_1 and rect_2 and mostrar_boton_bajarse:
            # Calculamos el centro entre las dos primeras cajas
            centro_x = (rect_1.x + rect_2.right) // 2
            bajarse_rect = pygame.Rect(centro_x - (cuadro_w_fino // 2), boton_y, cuadro_w_fino, boton_h)
            
            # Dibujar imagen
            path_b = os.path.join(ASSETS_PATH, "bajarse.png")
            if os.path.exists(path_b):
                img = pygame.transform.smoothscale(pygame.image.load(path_b).convert_alpha(), (bajarse_rect.width, bajarse_rect.height))
                screen.blit(img, bajarse_rect.topleft)
            cuadros_interactivos["Bajarse"] = bajarse_rect

        # 2. Botón "DESCARTAR" (Siempre encima de la casilla "Descarte")
        rect_desc = cuadros_interactivos.get("Descarte")
        if rect_desc and mostrar_boton_descartar:
            descartar_rect = pygame.Rect(rect_desc.x, boton_y, rect_desc.width, boton_h)
            
            # Dibujar imagen
            path_d = os.path.join(ASSETS_PATH, "descartar.png")
            if os.path.exists(path_d):
                img = pygame.transform.smoothscale(pygame.image.load(path_d).convert_alpha(), (descartar_rect.width, descartar_rect.height))
                screen.blit(img, descartar_rect.topleft)
            cuadros_interactivos["Descartar"] = descartar_rect

        # 3. Botón "COMPRAR CARTA" (Encima de los mazos de tomar carta)
        rect_t1 = cuadros_interactivos.get("Tomar descarte")
        rect_t2 = cuadros_interactivos.get("Tomar carta")
        if rect_t1 and rect_t2 and mostrar_boton_comprar:
            # Centrado sobre ambos mazos
            centro_compra = (rect_t1.x + rect_t2.right) // 2
            comprar_rect = pygame.Rect(centro_compra - (cuadro_w_carta // 2), boton_y, cuadro_w_carta, boton_h)
            
            path_c = os.path.join(ASSETS_PATH, "comprar_carta.png")
            if os.path.exists(path_c):
                img = pygame.transform.smoothscale(pygame.image.load(path_c).convert_alpha(), (comprar_rect.width, comprar_rect.height))
                screen.blit(img, comprar_rect.topleft)
            cuadros_interactivos["Comprar carta"] = comprar_rect

        # 4. Botón "ORDENAR MANO" — siempre visible para el jugador local
        if jugador_local:
            etiqueta_btn = f"Ordenar: {modo_orden}"
            btn_ordenar = pygame.Rect(WIDTH - 190, HEIGHT - 160, 170, 40)
            draw_simple_button(
                screen, btn_ordenar, etiqueta_btn,
                get_game_font(10),
                bg=(40, 80, 130),
                fg=(255, 255, 255)
            )

        # Intercambiar SÓLO las zonas interactivas: "Descarte" <-> "ZonaCentralInteractiva".
        # Esto cambia solo el mapeo interactivo (donde se debe soltar una carta), no afecta el dibujo.
        '''try:
            if "Descarte" in cuadros_interactivos and "ZonaCentralInteractiva" in cuadros_interactivos:
                # Hacer swap de referencias
                d_rect = cuadros_interactivos["Descarte"]
                z_rect = cuadros_interactivos["ZonaCentralInteractiva"]
                cuadros_interactivos["Descarte"], cuadros_interactivos["ZonaCentralInteractiva"] = z_rect, d_rect

                # Detectar maximizado (comparando con resolución de escritorio)
                is_max = False
                try:
                    window_w, window_h = screen.get_size()
                    info = pygame.display.Info()
                    desktop_w, desktop_h = info.current_w, info.current_h
                    # margen ligero para evitar falsos negativos en multi-monitor
                    is_max = (window_w >= desktop_w - 20 and window_h >= desktop_h - 40)
                except Exception:
                    is_max = False

                # Si está maximizada, ajustar la posición X (hacia la derecha) + escalar ancho, tomando
                # en cuenta la Y y las medidas del primer 'Trio' (x_trio, cuadro_y, cuadro_w_fino, cuadro_h)
                if is_max:
                    try:
                        base_x = x_trio
                        base_y = cuadro_y
                        base_w = cuadro_w_fino
                        base_h = cuadro_h
                    except Exception:
                        base_x = None
                        base_y = None
                        base_w = None
                        base_h = None

                    # Desplazamiento pequeño a la derecha y aumento de ancho proporcional
                    delta = max(8, int((base_w or 100) * 0.08))

                    for key in ("Descarte", "ZonaCentralInteractiva"):
                        r = cuadros_interactivos.get(key)
                        if isinstance(r, pygame.Rect):
                            # mover X a la derecha y usar Y/alto del primer Trio
                            new_x = min(window_w - 10, r.x + delta)
                            new_y = base_y if base_y is not None else r.y
                            new_w = max(40, r.width + delta)
                            new_h = base_h if base_h is not None else r.height
                            cuadros_interactivos[key] = pygame.Rect(new_x, new_y, new_w, new_h)
        except Exception:
            pass'''

        # --- Caja superior izquierda: Ronda y Turno (pegada arriba a la izquierda) ---
        ronda_turno_x = 0
        ronda_turno_y = 0
        # Hacer la caja Ronda/Turno un poco más ancha para acomodar nombres largos
        ronda_turno_w = int(jug_w * 2.2)
        ronda_turno_h = jug_h

        ronda_turno_rect = pygame.Rect(ronda_turno_x, ronda_turno_y, ronda_turno_w, ronda_turno_h)
        # draw_transparent_rect(screen, (200, 200, 200, 80), ronda_turno_rect, border=1)
        cuadros_interactivos["Ronda/Turno"] = ronda_turno_rect

        ronda_rect = pygame.Rect(ronda_turno_x, ronda_turno_y, ronda_turno_w, ronda_turno_h // 2)
        # draw_transparent_rect(screen, (180, 180, 180, 80), ronda_rect, border=1)
        # draw_label(ronda_rect, "Ronda")
        cuadros_interactivos["Ronda"] = ronda_rect

        turno_rect = pygame.Rect(ronda_turno_x, ronda_turno_y + ronda_turno_h // 2, ronda_turno_w, ronda_turno_h // 2)
        # draw_transparent_rect(screen, (180, 180, 180, 80), turno_rect, border=1)
        # draw_label(turno_rect, "Turno")
        cuadros_interactivos["Turno"] = turno_rect

        # --- Caja superior derecha: Solo Menú (centrado en la esquina superior derecha, sin cuadro de sonido) ---
        menu_w = int(jug_w * 1.1)
        menu_h = int(jug_h * 0.5)
        margin_menu = 10

        menu_x = WIDTH - menu_w - margin_menu
        menu_y = margin_menu

        menu_rect = pygame.Rect(menu_x, menu_y, menu_w, menu_h)

        menu_img_path = os.path.join(ASSETS_PATH, "menu.png")
        if os.path.exists(menu_img_path):
            menu_img = pygame.image.load(menu_img_path).convert_alpha()
            img = pygame.transform.smoothscale(menu_img, (menu_rect.width, menu_rect.height))
            screen.blit(img, menu_rect.topleft)
        cuadros_interactivos["Menú"] = menu_rect

        # Elimina o comenta cualquier bloque relacionado con sonido_rect, draw_label(sonido_rect, "Sonido") y draw_transparent_rect para sonido.

        # --- Caja inferior izquierda: Tablero y posiciones (más pequeña y más abajo) ---
        tablero_w = ronda_turno_w
        tablero_h = int(jug_h * 0.6)
        tablero_x = 0
        tablero_y = HEIGHT - tablero_h
        tablero_rect = pygame.Rect(tablero_x, tablero_y, tablero_w, tablero_h)
        # draw_transparent_rect(screen, (200, 200, 200, 80), tablero_rect, border=1)
        # draw_label(tablero_rect, "Tablero y posiciones")
        cuadros_interactivos["Tablero y posiciones"] = tablero_rect



        # --- Mostrar cartas del jugador 1 en J1 (interactivas y auto-organizadas) ---
        # Usar visual_hand en vez de jugador_local.playerHand
        class VisualPlayer:
            pass
        visual_player = VisualPlayer()
        visual_player.playerHand = visual_hand
        draw_player_hand(visual_player, jug1, cuadros_interactivos, cartas_ref, ocultas=cartas_ocultas)

        # Dibuja la carta arrastrada como copia transparente, si corresponde (arrastre visual independiente)
        if dragging and carta_arrastrada is not None:
            # Mostrar la carta arrastrada más grande que las del hand
            base_hand_h = max(40, jug1.height - 6)
            # Ampliar un 25% como valor por defecto
            card_height = int(min(base_hand_h * 1.25, HEIGHT * 0.7))
            card_width = int(card_height * 0.68)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            img = get_card_image(carta_arrastrada).copy()
            img = pygame.transform.smoothscale(img, (card_width, card_height))
            img.set_alpha(120)  # Transparente
            x = mouse_x - drag_offset_x
            y = mouse_y - card_height // 2
            screen.blit(img, (x, y))

        # Lado izquierdo
        #from test3 import players

        # Ejemplo para 2 a 7 jugadores (ajusta según tu layout)
        jugadores_laterales = []
        jugadores_superiores = []
        player_baj_rect = {}      
        baj_box_to_player = {}
        # 2. ENCONTRAR INDICE LOCAL
        # Buscamos en qué posición de la lista 'players' estás tú.
        n_players = len(players)
        idx_local = 0
        if jugador_local:
            for i, p in enumerate(players):
                if p.playerId == jugador_local.playerId:
                    idx_local = i
                    break

        # Mapeo del jugador local (Siempre abajo / baj1)
        if jugador_local:
            player_baj_rect[jugador_local.playerName] = boxes.get("baj1")
            baj_box_to_player["baj1"] = jugador_local

        # 3. DEFINIR LOS ASIENTOS DISPONIBLES EN ORDEN (SENTIDO HORARIO)
        # Esto define qué cajas se usan visualmente según cuántos jugadores hay.
        # Formato: (NombreCajaAvatar, TipoDibujado) -> 0=Lateral, 1=Superior/Horizontal
        seat_map = {
            2: [("jug4", 1)],                                           # 1 vs 1: Frente
            3: [("jug2", 0), ("jug7", 0)],                              # Triángulo: Izq, Der
            4: [("jug2", 0), ("jug4", 1), ("jug7", 0)],                 # Cuadrado: Izq, Arr, Der
            5: [("jug2", 0), ("jug4", 1), ("jug5", 1), ("jug7", 0)],    # Pentágono
            6: [("jug2", 0), ("jug3", 0), ("jug4", 1), ("jug6", 0), ("jug7", 0)],
            7: [("jug2", 0), ("jug3", 0), ("jug4", 1), ("jug5", 1), ("jug6", 0), ("jug7", 0)]
        }

        # Obtenemos la configuración para la cantidad actual de jugadores
        config_actual = seat_map.get(n_players, [])

        # 4. ASIGNACIÓN MATEMÁTICA
        # Recorremos SOLO a los oponentes en orden
        for i in range(len(config_actual)):
            # Cálculo del índice relativo:
            # (MiIndice + 1 + i) % Total -> Nos da el jugador siguiente en la lista circularmente
            opponent_idx = (idx_local + 1 + i) % n_players
            
            # Protección por si la lista cambió repentinamente
            if opponent_idx < len(players):
                opponent = players[opponent_idx]
                box_name, draw_type = config_actual[i]
                
                rect_asiento = boxes.get(box_name)
                # Deducimos el nombre de la bajada (ej: jug2 -> baj2)
                baj_name = box_name.replace("jug", "baj")
                rect_bajada = boxes.get(baj_name)

                if rect_asiento:
                    # A. Asignar Avatar/Mano
                    if draw_type == 0: # Lateral
                        jugadores_laterales.append((opponent, rect_asiento))
                    else: # Superior
                        jugadores_superiores.append((opponent, rect_asiento))
                    
                    # B. Asignar Zona de Cartas Bajadas (Mesa)
                    if rect_bajada:
                        # 1. Para saber DÓNDE dibujar las cartas de este jugador
                        nombre_op = getattr(opponent, "playerName", "Desconocido")
                        player_baj_rect[nombre_op] = rect_bajada
                        
                        # 2. Para saber QUIÉN es el dueño de esa zona (para clicks/drops)
                        baj_box_to_player[baj_name] = opponent

        # Dibuja solo los jugadores activos en los recuadros correspondientes
        # Dibuja solo los jugadores activos en los recuadros correspondientes
        for jugador, recuadro in jugadores_laterales:
            draw_horizontal_rain_hand_rotated(jugador, recuadro)

        for jugador, recuadro in jugadores_superiores:
            draw_horizontal_pt_hand(jugador, recuadro)
        # ===== Construir mapeo caja_de_bajada -> jugador (CORREGIDO) =======
        BASE_NOMBRE_SIZE = 14
        BASE_PUNTOS_SIZE = 11

        def get_fitting_font(text, max_width, base_size, min_size=8):
            """
            Devuelve una pygame.font.Font cuyo tamaño se va reduciendo desde base_size
            hasta que el ancho del texto cabe en max_width (o llega a min_size).
            """
            size = base_size
            font = get_game_font(size)
            # medir con render (color cualquiera)
            width = font.render(text, True, (0,0,0)).get_width()
            while width > max_width and size > min_size:
                size -= 1
                font = get_game_font(size)
                width = font.render(text, True, (0,0,0)).get_width()
            return font

        # font por defecto para casos donde no se aplique ajuste directo
        # --- Después de dibujar manos, cartas y elementos (justo antes de dibujar nombres) ---
        # Tomar snapshot del screen tal y como están las cartas / UI detrás de los nombres
        try:
            pre_names_snapshot = screen.copy()
        except Exception:
            pre_names_snapshot = None

        BASE_NOMBRE_SIZE = 14
        BASE_PUNTOS_SIZE = 11

        def get_fitting_font(text, max_width, base_size, min_size=8):
            """Devuelve pygame.font.Font cuyo tamaño se reduce pixel a pixel hasta caber."""
            size = base_size
            font = get_game_font(size)
            width = font.render(text, True, (0,0,0)).get_width()
            while width > max_width and size > min_size:
                size -= 1
                font = get_game_font(size)
                width = font.render(text, True, (0,0,0)).get_width()
            return font

        # font por defecto
        font_nombre = get_game_font(BASE_NOMBRE_SIZE)
        font_puntos = get_game_font(BASE_PUNTOS_SIZE)

        def draw_text_with_border(surface, text, font, pos, color=(255,255,255), border_color=(0,0,0)):
            """Dibuja texto con borde (8 direcciones)."""
            x, y = pos
            # render de borde una sola vez por dirección para ahorrar
            for ox, oy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
                surface.blit(font.render(text, True, border_color), (x+ox, y+oy))
            surface.blit(font.render(text, True, color), (x, y))

        def restore_region(rect, inflate_x=12, inflate_y=10):
            """
            Restaura la región desde la instantánea pre_names_snapshot (que contiene
            las cartas ya dibujadas). Si no existe snapshot, usa fondo_img como fallback.
            Esto evita borrar las cartas debajo de los nombres al actualizar texto.
            """
            try:
                bg_rect = rect.inflate(inflate_x, inflate_y).clip(pygame.Rect(0,0,WIDTH,HEIGHT))
                if bg_rect.width <= 0 or bg_rect.height <= 0:
                    return
                if pre_names_snapshot:
                    # copiar desde la snapshot que contiene cartas y UI previas
                    screen.blit(pre_names_snapshot, bg_rect.topleft, bg_rect)
                else:
                    # fallback: reponer desde fondo estático (pierde cartas)
                    screen.blit(fondo_img, bg_rect.topleft, bg_rect)
            except Exception:
                pygame.draw.rect(screen, (0,0,0), rect.inflate(inflate_x, inflate_y))

        def draw_turn_highlight(jugador, nombre_rect, recuadro=None, position='bottom'):
            """Dibuja un rectángulo rojo semi-transparente justo debajo del nombre del jugador si tiene el turno."""
            try:
                if not getattr(jugador, "isHand", False):
                    return
                # Tamaño y posición del rectángulo basado en el rect del nombre
                width = max(40, nombre_rect.width + 12)
                height = 8
                x = nombre_rect.centerx - width // 2
                y = nombre_rect.bottom + 6
                rect = pygame.Rect(int(x), int(y), int(width), int(height))
                s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                s.fill((255, 0, 0, 140))  # rojo semi-transparente
                screen.blit(s, rect.topleft)
            except Exception:
                pass

        # --- Jugador local (parte inferior) ---
        if jugador_local:
            jug_rect = boxes.get("jug1")
            if jug_rect:
                borde_color = (255,0,0) if getattr(jugador_local, "isHand", False) else (0,0,0)
                nombre_txt = str(getattr(jugador_local, "playerName", "Jugador"))
                max_w_nombre = max(40, jug_rect.width - 8)
                font_nombre_used = get_fitting_font(nombre_txt, max_w_nombre, BASE_NOMBRE_SIZE)
                
                # MODIFICACIÓN AQUÍ: Cambiamos el centro por la derecha (right) con un margen de 100px
                nombre_rect = font_nombre_used.render(nombre_txt, True, (255,255,255)).get_rect(
                    center=(jug_rect.right - 200, jug_rect.top - 12) 
                )
                
                restore_region(nombre_rect, 14, 12)
                draw_text_with_border(screen, nombre_txt, font_nombre_used, nombre_rect.topleft,
                                    (255,255,255), borde_color)

                # Puntos inmediatamente debajo del nombre (alineados al nuevo centro a la derecha)
                puntos_txt = f"{getattr(jugador_local, 'playerPoints', 0)} pts"
                max_w_puntos = max(30, jug_rect.width - 8)
                font_puntos_used = get_fitting_font(puntos_txt, max_w_puntos, BASE_PUNTOS_SIZE)
                
                puntos_rect = font_puntos_used.render(puntos_txt, True, (220,220,120)).get_rect(
                    center=(nombre_rect.centerx, nombre_rect.bottom + 8)
                )
                
                restore_region(puntos_rect, 12, 10)
                draw_text_with_border(screen, puntos_txt, font_puntos_used, puntos_rect.topleft,
                                    (220,220,120), (0,0,0))

        # --- Jugadores laterales ---
        for jugador, recuadro in jugadores_laterales:
            borde_color = (255,0,0) if getattr(jugador, "isHand", False) else (0,0,0)
            nombre_txt = str(getattr(jugador, "playerName", "Jugador"))
            max_w_nombre = max(30, recuadro.width - 8)
            font_nombre_used = get_fitting_font(nombre_txt, max_w_nombre, BASE_NOMBRE_SIZE)
            temp_rect = font_nombre_used.render(nombre_txt, True, (255,255,255)).get_rect()
            baj_rect = player_baj_rect.get(getattr(jugador, "playerName", None))
            if baj_rect:
                desired_centery = max(temp_rect.height//2 + 6, baj_rect.top - 8 - temp_rect.height//2)
            else:
                desired_centery = recuadro.top - 12
            temp_rect.center = (recuadro.centerx, desired_centery)
            nombre_rect = temp_rect
            restore_region(nombre_rect, 12, 10)
            # el resaltado de turno ahora se dibuja debajo de todo (draw_player_turn_highlights).
            draw_text_with_border(screen, nombre_txt, font_nombre_used, nombre_rect.topleft,
                                 (255,255,255), borde_color)

            puntos_txt = f"{getattr(jugador, 'playerPoints', 0)} pts"
            max_w_puntos = max(30, recuadro.width - 8)
            font_puntos_used = get_fitting_font(puntos_txt, max_w_puntos, BASE_PUNTOS_SIZE)
            puntos_rect = font_puntos_used.render(puntos_txt, True, (220,220,120)).get_rect(
                center=(recuadro.centerx, nombre_rect.bottom + 10)
            )
            restore_region(puntos_rect, 10, 8)
            draw_text_with_border(screen, puntos_txt, font_puntos_used, puntos_rect.topleft,
                                 (220,220,120), (0,0,0))

        # --- Jugadores superiores ---
        for jugador, recuadro in jugadores_superiores:
            borde_color = (255,0,0) if getattr(jugador, "isHand", False) else (0,0,0)
            nombre_txt = str(getattr(jugador, "playerName", "Jugador"))
            max_w_nombre = max(30, recuadro.width - 8)
            font_nombre_used = get_fitting_font(nombre_txt, max_w_nombre, BASE_NOMBRE_SIZE)
            # Prefer colocar el nombre por encima de la bajada si existe
            SUPERIOR_NAME_OFFSET = 25
            temp_rect = font_nombre_used.render(nombre_txt, True, (255,255,255)).get_rect()
            baj_rect = player_baj_rect.get(getattr(jugador, "playerName", None))
            if baj_rect:
                desired_centery = max(temp_rect.height//2 + 6, baj_rect.top - 8 - temp_rect.height//2)
            else:
                desired_centery = recuadro.bottom + SUPERIOR_NAME_OFFSET
            temp_rect.center = (recuadro.centerx, desired_centery)
            nombre_rect = temp_rect
            restore_region(nombre_rect, 12, 10)
            # el resaltado de turno ahora se dibuja debajo de todo (draw_player_turn_highlights).
            draw_text_with_border(screen, nombre_txt, font_nombre_used, nombre_rect.topleft,
                                 (255,255,255), borde_color)

            puntos_txt = f"{getattr(jugador, 'playerPoints', 0)} pts"
            max_w_puntos = max(30, recuadro.width - 8)
            font_puntos_used = get_fitting_font(puntos_txt, max_w_puntos, BASE_PUNTOS_SIZE)
            puntos_rect = font_puntos_used.render(puntos_txt, True, (220,220,120)).get_rect(
                center=(recuadro.centerx, nombre_rect.bottom + 12)
            )
            restore_region(puntos_rect, 10, 8)
            draw_text_with_border(screen, puntos_txt, font_puntos_used, puntos_rect.topleft,
                                 (220,220,120), (0,0,0))
        # Dibuja cartas en Seguidilla (zona_cartas[0])
        '''if zona_cartas[0]:
            rect = cuadros_interactivos.get("Seguidilla")
            if rect:
                n = len(zona_cartas[0])
                pad = 0
                # Queremos la carta lo más grande posible: priorizamos altura
                card_height = rect.height - pad
                card_width = int(card_height * 0.68)
                # Si la carta resulta más ancha que el rect, ajustar por ancho
                if card_width > rect.width - pad:
                    card_width = rect.width - pad
                    card_height = int(card_width / 0.68)
                # Capamos la altura de la carta para que no ocupe demasiado del rect
                max_card_h = max(40, int(rect.height * 0.90))
                if card_height > max_card_h:
                    card_height = max_card_h
                    card_width = max(40, int(card_height * 0.68))
                # Rediseño de solapamiento: repartir espacio vertical para que ninguna carta quede totalmente oculta
                if n > 1:
                    available = max(0, rect.height - card_height)
                    if available >= (n - 1) * card_height:
                        overlap_y = card_height  # totalmente separadas
                    else:
                        # reducir margen cuando n aumenta; mínimo visible definido por MIN_OVERLAP
                        overlap_y = max(MIN_OVERLAP, available // max(1, n - 1))
                    overlap_y = min(overlap_y, card_height)
                else:
                    overlap_y = 0
                x = rect.x + (rect.width - card_width) // 2
                # Centrar la pila verticalmente dentro del rect
                total_stack_h = card_height + (n - 1) * overlap_y
                start_y = rect.y + max(4, (rect.height - total_stack_h) // 2)
                # Dibujar todas las cartas (desde la primera abajo a la última encima)
                for i in range(n):
                    card = zona_cartas[0][i]
                    img = get_card_image(card)
                    img = pygame.transform.smoothscale(img, (card_width, card_height))
                    card_rect = pygame.Rect(x, start_y + i * overlap_y, card_width, card_height)
                    screen.blit(img, card_rect.topleft)'''

        # Dibuja cartas en Trio (zona_cartas[1]) ##### Prueba no se para ver que pasa 
        '''if zona_cartas[1] and roundOne:
            rect = cuadros_interactivos.get("Trio")
            if rect:
                n = len(zona_cartas[1])
                card_width, card_height = calc_card_size_for_rect(rect)
                if n > 1:
                    max_height = rect.height - 8
                    solapamiento = (max_height - card_height) // (n - 1)
                    if solapamiento > card_height * 0.7:
                        solapamiento = int(card_height * 0.7)
                else:
                    solapamiento = 0
                x = rect.x + (rect.width - card_width) // 2
                start_y = rect.y + max(6, int(rect.height * 0.08))
                for i, card in enumerate(zona_cartas[1]):
                    img = get_card_image(card)
                    img = pygame.transform.smoothscale(img, (card_width, card_height))
                    card_rect = pygame.Rect(x, start_y + i * solapamiento, card_width, card_height)
                    screen.blit(img, card_rect.topleft)'''

        # --- DIBUJO DINÁMICO DE CARTAS EN LA MESA (REEMPLAZO) ---
        
        # 1. Definimos qué nombre de cuadro corresponde a cada índice de zona_cartas por ronda
        mapping_nombres = {
            "ronda1": ["Trio", "Seguidilla"],
            "ronda2": ["Seguidilla_0", "Seguidilla_1"],
            "ronda3": ["Trio_0", "Trio_1", "Trio_2"],
            "ronda4": ["Trio_0", "Trio_1", "Seguidilla"]
        }
        
        # --- DIBUJO DINÁMICO DE CARTAS EN LA MESA (MÁS ESPACIADO) ---
        nombres_ronda = mapping_nombres.get(fase, ["Trio","Seguidilla"])

        for i in range(len(nombres_ronda)):
            stack = zona_cartas[i]
            if stack:
                nombre_casilla = nombres_ronda[i]
                rect = cuadros_interactivos.get(nombre_casilla)
                
                if rect:
                    n = len(stack)
                    # Reducimos a 0.75 (75%) para que la carta no sea tan alta 
                    # y deje "pista" para que las demás bajen.
                    card_h = int(rect.height * 0.90) 
                    card_w = int(card_h * 0.68)
                    
                    if card_w > rect.width:
                        card_w = rect.width - 10
                        card_h = int(card_w / 0.68)

                    # Cálculo de solapamiento aumentado:
                    if n > 1:
                        espacio_disponible = rect.height - card_h - 20
                        # Aumentamos el tope a 50px (antes 35px) para más separación
                        overlap_y = min(53, espacio_disponible // (n - 1))
                        # El mínimo ahora es 25px para que siempre se vea el número
                        overlap_y = max(28, overlap_y) 
                    else:
                        overlap_y = 0
                    
                    start_y = rect.y + 10 
                    x = rect.x + (rect.width - card_w) // 2

                    for j, carta in enumerate(stack):
                        img = get_card_image(carta)
                        img_scaled = pygame.transform.smoothscale(img, (card_w, card_h))
                        # Dibujamos con el nuevo overlap_y más amplio
                        screen.blit(img_scaled, (x, start_y + j * overlap_y))
        # --- DIBUJO DEL DESCARTE (MÁS ESPACIADO) ---
        # --- DIBUJO DEL DESCARTE (MÁS ESPACIADO) ---
        idx_desc = 3 if (roundThree or roundFour) else 2
        rect_desc = cuadros_interactivos.get("Descarte")

        if rect_desc and len(zona_cartas) > idx_desc and zona_cartas[idx_desc]:
            stack_desc = zona_cartas[idx_desc]
            n_desc = len(stack_desc)
            
            # Tamaño al 75% para dar aire
            card_h = int(rect_desc.height * 0.90)
            card_w = int(card_h * 0.68)
            
            if n_desc > 1:
                espacio_libre = rect_desc.height - card_h - 20
                # Permitimos hasta 50px de separación entre cartas
                overlap_y = min(53, espacio_libre // (n_desc - 1))
                overlap_y = max(28, overlap_y)
            else:
                overlap_y = 0
                
            start_y = rect_desc.y + 10 
            x = rect_desc.x + (rect_desc.width - card_w) // 2
            
            for j, carta in enumerate(stack_desc):
                img = get_card_image(carta)
                img_scaled = pygame.transform.smoothscale(img, (card_w, card_h))
                screen.blit(img_scaled, (x, start_y + j * overlap_y))
                        
        if zona_cartas[3] and roundTwo:
            rect = cuadros_interactivos.get("Trio") 
            if rect:
                n = len(zona_cartas[3])
                card_width = rect.width - 8
                card_height = int(card_width / 0.68)
        if zona_cartas[3] and roundFour:
            rect = cuadros_interactivos.get("Seguidilla") 
            if rect:
                n = len(zona_cartas[3])
                card_width = rect.width - 8
                card_height = int(card_width / 0.68)

        rect = cuadros_interactivos.get("Tomar descarte")
        if rect:
            plantilla_img_path = os.path.join(ASSETS_PATH, "plantilla.png")
            if os.path.exists(plantilla_img_path):
                plantilla_img = pygame.image.load(plantilla_img_path).convert_alpha()
                img = pygame.transform.smoothscale(plantilla_img, (rect.width - 8, rect.height - 8))
                img_rect = img.get_rect(center=rect.center)
                screen.blit(img, img_rect.topleft)

            # Dibuja la última carta descartada encima
            if mazo_descarte:
                card = mazo_descarte[-1]
                # Queremos la carta lo más grande posible: priorizamos altura
                card_height = rect.height - 8
                card_width = int(card_height * 0.68)
                if card_width > rect.width - 8:
                    card_width = rect.width - 8
                    card_height = int(card_width / 0.68)
                # permitir que la carta ocupe mayor parte de la caja
                max_card_h_local = max(40, int(rect.height * 0.85))
                if card_height > max_card_h_local:
                    card_height = max_card_h_local
                    card_width = max(40, int(card_height * 0.68))
                x = rect.x + (rect.width - card_width) // 2
                y = rect.y + (rect.height - card_height) // 2
                img = get_card_image(card)
                img = pygame.transform.smoothscale(img, (card_width, card_height))
                card_rect = pygame.Rect(x, y, card_width, card_height)
                screen.blit(img, card_rect.topleft)

            # DIBUJA OVERLAY SEMI‑INVISIBLE (solo visual, la detección de click usa cuadros_interactivos)
            ov = cuadros_interactivos.get("DescarteOverlay")
            if ov:
                surf = pygame.Surface((ov.width, ov.height), pygame.SRCALPHA)
                surf.fill((255, 255, 255, 20))  # muy translúcido
                screen.blit(surf, ov.topleft)

        # for idx, nombre in enumerate(["Seguidilla", "Trio", "Descarte"]):
        #     if zona_cartas[idx]:
        #         rect = cuadros_interactivos.get(nombre)
        #         if rect:
                img = get_card_image(card)
                img = pygame.transform.smoothscale(img, (card_width, card_height))
                card_rect = pygame.Rect(x, y, card_width, card_height)
                screen.blit(img, card_rect.topleft)
        if zona_cartas[3] and roundTwo:
            rect = cuadros_interactivos.get("Trio") 
            if rect:
                n = len(zona_cartas[3])
                card_width = rect.width - 8
                card_height = int(card_width / 0.68)
        if zona_cartas[3] and roundFour:
            rect = cuadros_interactivos.get("Seguidilla") 
            if rect:
                n = len(zona_cartas[3])
                card_width = rect.width - 8
                card_height = int(card_width / 0.68)

        rect = cuadros_interactivos.get("Tomar descarte")
        if rect:
            plantilla_img_path = os.path.join(ASSETS_PATH, "plantilla.png")
            if os.path.exists(plantilla_img_path):
                plantilla_img = pygame.image.load(plantilla_img_path).convert_alpha()
                img = pygame.transform.smoothscale(plantilla_img, (rect.width - 8, rect.height - 8))
                img_rect = img.get_rect(center=rect.center)
                screen.blit(img, img_rect.topleft)

            # Dibuja la última carta descartada encima
            if mazo_descarte:
                card = mazo_descarte[-1]
                card_width = rect.width - 8
                card_height = int(card_width / 0.68)
                x = rect.x + (rect.width - card_width) // 2
                y = rect.y + (rect.height - card_height) // 2
                img = get_card_image(card)
                img = pygame.transform.smoothscale(img, (card_width, card_height))
                card_rect = pygame.Rect(x, y, card_width, card_height)
                screen.blit(img, card_rect.topleft)

        # for idx, nombre in enumerate(["Seguidilla", "Trio", "Descarte"]):
        #     if zona_cartas[idx]:
        #         rect = cuadros_interactivos.get(nombre)
        #         if rect:
        #             n = len(zona_cartas[idx])
        #             card_width = rect.width - 8
        #             card_height = int(card_width / 0.68)
        #             if n > 1:
        #                 solapamiento = (rect.height - card_height) // (n - 1)
        #                 if solapamiento > card_height * 0.7:
        #                     solapamiento = int(card_height * 0.7)
        #             else:
        #                 solapamiento = 0
        #             x = rect.x + (rect.width - card_width) // 2
        #             start_y = rect.y
        #             for i in range(n):
        #                 card = zona_cartas[idx][i]
        #                 img = get_card_image(card)
        #                 img = pygame.transform.smoothscale(img, (card_width, card_height))
        #                 card_rect = pygame.Rect(x, start_y + i * solapamiento, card_width, card_height)
        #                 screen.blit(img, card_rect.topleft)

        # Al final del while running, antes de pygame.display.flip(), agrega:
        # Mensaje temporal: blanco, más grande, wrap por palabra cada 35 caracteres y un poco más abajo
        
        # Dibujar siempre los textos "Ronda: X" y "Turno: N" dentro de sus cajas (sin PNGs)
        ronda_rect = cuadros_interactivos.get("Ronda")
        turno_rect = cuadros_interactivos.get("Turno")
        menu_rect = cuadros_interactivos.get("Menú") or cuadros_interactivos.get("Menu")

        font_path = os.path.join(ASSETS_PATH, "PressStart2P-Regular.ttf")

        # --- Ronda: calcula número según fase ---
        if fase == "ronda1":
            ronda_num = "Trio y Seguidilla"
        elif fase == "ronda2":
            ronda_num = "2 Seguidillas"
        elif fase == "ronda3":
            ronda_num = "3 Trios"
        elif fase == "ronda4":
            ronda_num = "1 Seguidilla y 2 Trios"
        else:
            ronda_num = "-"

        if ronda_rect:
            # Mostrar en dos líneas: etiqueta "Ronda:" arriba y número abajo
            label_text = "Ronda:"
            # Reducimos la base para que la etiqueta quede más pequeña en pantalla
            label_base = max(8, int(ronda_rect.height * 0.38))
            font_label = get_fitting_font(label_text, max(8, ronda_rect.width - 8), label_base)
            label_surf = font_label.render(label_text, True, (255, 255, 255))

            num_text = str(ronda_num)
            # Texto numérico más pequeño por defecto (evita que cadenas largas ocupen demasiado)
            num_base = max(10, int(ronda_rect.height * 0.48))
            font_num = get_fitting_font(num_text, max(8, ronda_rect.width - 8), num_base)
            num_surf = font_num.render(num_text, True, (255, 255, 255))

            spacing = max(2, int(ronda_rect.height * 0.06))
            total_h = label_surf.get_height() + spacing + num_surf.get_height()
            start_y = ronda_rect.centery - total_h // 2

            label_rect = label_surf.get_rect(centerx=ronda_rect.centerx, top=start_y)
            num_rect = num_surf.get_rect(centerx=ronda_rect.centerx, top=label_rect.bottom + spacing)

            render_text_with_border(label_text, font_label, (255, 255, 255), (100, 0, 0), (label_rect.x, label_rect.y), screen)
            render_text_with_border(num_text, font_num, (255, 255, 255), (100, 0, 0), (num_rect.x, num_rect.y), screen)
            cuadros_interactivos["Ronda"] = ronda_rect

        # --- Turno: mostrar el nombre del jugador en turno ---
        try:
            current_player = next((p for p in players if getattr(p, "isHand", False)))
            turno_name = getattr(current_player, "playerName", "-")
        except Exception:
            turno_name = "-"

        if turno_rect:
            # Mostrar en dos líneas: etiqueta "Turno" arriba y nombre del jugador abajo
            label_text = "Turno"
            label_base = max(10, int(turno_rect.height * 0.42))
            font_label = get_fitting_font(label_text, max(10, turno_rect.width - 8), label_base)
            label_surf = font_label.render(label_text, True, (255, 255, 255))

            name_text = turno_name
            name_base = max(12, int(turno_rect.height * 0.58))
            font_name = get_fitting_font(name_text, max(10, turno_rect.width - 8), name_base)
            name_surf = font_name.render(name_text, True, (255, 255, 255))

            # Espacio pequeño entre etiqueta y nombre (menos margen como pediste)
            spacing = max(2, int(turno_rect.height * 0.04))
            total_h = label_surf.get_height() + spacing + name_surf.get_height()
            start_y = turno_rect.centery - total_h // 2

            label_rect = label_surf.get_rect(centerx=turno_rect.centerx, top=start_y)
            name_rect = name_surf.get_rect(centerx=turno_rect.centerx, top=label_rect.bottom + spacing)

            render_text_with_border(label_text, font_label, (255, 255, 255), (0, 0, 0), (label_rect.x, label_rect.y), screen)
            render_text_with_border(name_text, font_name, (255, 255, 255), (0, 0, 0), (name_rect.x, name_rect.y), screen)
            cuadros_interactivos["Turno"] = turno_rect

        # --- Mantener Menú con imagen si existe ---
        if menu_rect:
            menu_img_path = os.path.join(ASSETS_PATH, "menu.png")
            if os.path.exists(menu_img_path):
                menu_img = pygame.image.load(menu_img_path).convert_alpha()
                img = pygame.transform.smoothscale(menu_img, (menu_rect.width, menu_rect.height))
                screen.blit(img, menu_rect.topleft)
            cuadros_interactivos["Menú"] = menu_rect
        # --- Botón "Menú" ---
            menu_img_path = os.path.join(ASSETS_PATH, "menu.png")
            if os.path.exists(menu_img_path):
                menu_img = pygame.image.load(menu_img_path).convert_alpha()
                img = pygame.transform.smoothscale(menu_img, (menu_rect.width, menu_rect.height))
                screen.blit(img, menu_rect.topleft)
            cuadros_interactivos["Menú"] = menu_rect

        # Mostrar jugadas bajadas en los bloques de bajada de todos los jugadores

        # Mostrar jugadas bajadas: ubicar cada bajada junto a la caja del jugador (misma lógica que nombres/manos)
        rects_jugadas = {}

        # Construir mapping playerName -> rect de "bajada" usando la misma perspectiva que ya usamos
        player_baj_rect = {}

        # jugador local -> baj1
        if jugador_local:
            player_baj_rect[getattr(jugador_local, "playerName", None)] = boxes.get("baj1")

        # Para laterales/superiores ya tenemos listas (jugadores_laterales, jugadores_superiores)
        all_side_players = jugadores_laterales + jugadores_superiores
        for p, jug_rect in all_side_players:
            # buscar la clave de 'jugX' dentro de boxes que coincida con el rect actual
            jug_key = next((k for k, v in boxes.items() if v == jug_rect and k.startswith("jug")), None)
            if jug_key:
                baj_key = jug_key.replace("jug", "baj")
                player_baj_rect[getattr(p, "playerName", None)] = boxes.get(baj_key)

        # También cubrir casos si hay players no listados (por si layout cambió)
        for p in players:
            if p.playerName not in player_baj_rect:
                # intentar mapear por índice relativo (0->baj1,1->baj2,...)
                try:
                    idx = players.index(p)
                    key = f"baj{idx+1}"
                    if key in boxes:
                        player_baj_rect[p.playerName] = boxes.get(key)
                except Exception:
                    pass

        # helper: devuelve rect aproximado del nombre del jugador (usado para evitar solapamientos con bajadas)
        def get_player_name_rect(jugador):
            try:
                name = getattr(jugador, "playerName", None)
                # Si hay una bajada asociada y NO es el jugador local, posicionar el nombre por encima de la bajada
                if jugador is not jugador_local and name and name in player_baj_rect:
                    baj = player_baj_rect[name]
                    # intentar obtener el recuadro (laterales/superiores/local) para centrar horizontalmente
                    rec = None
                    if jugador is jugador_local:
                        rec = boxes.get("jug1")
                    else:
                        for p, r in jugadores_laterales + jugadores_superiores:
                            if getattr(p, "playerName", None) == name:
                                rec = r
                                break
                    centerx = rec.centerx if rec else baj.centerx
                    width = max(30, (rec.width - 8) if rec else baj.width)
                    height = BASE_NOMBRE_SIZE + 4
                    centery = max(height//2 + 6, baj.top - 8 - height//2)
                    return pygame.Rect(centerx - width//2, centery - height//2, width, height)
                # fallback: comportamiento original
                if jugador is jugador_local:
                    jug_rect_local = boxes.get("jug1")
                    if jug_rect_local:
                        centerx = jug_rect_local.centerx
                        centery = jug_rect_local.bottom + 15
                        width = max(40, jug_rect_local.width - 8)
                        height = BASE_NOMBRE_SIZE + 6
                        return pygame.Rect(centerx - width//2, centery - height//2, width, height)
                # laterales
                for p, rec in jugadores_laterales:
                    if getattr(p, "playerName", None) == getattr(jugador, "playerName", None):
                        centerx = rec.centerx
                        centery = rec.top - 12
                        width = max(30, rec.width - 8)
                        height = BASE_NOMBRE_SIZE + 4
                        return pygame.Rect(centerx - width//2, centery - height//2, width, height)
                # superiores
                for p, rec in jugadores_superiores:
                    if getattr(p, "playerName", None) == getattr(jugador, "playerName", None):
                        centerx = rec.centerx
                        center_offset_super = 25
                        centery = rec.bottom + center_offset_super
                        width = max(30, rec.width - 8)
                        height = BASE_NOMBRE_SIZE + 4
                        return pygame.Rect(centerx - width//2, centery - height//2, width, height)
                # fallback por índice
                try:
                    idx = players.index(jugador)
                    key = f"jug{idx+1}"
                    rec = boxes.get(key)
                    if rec:
                        centerx = rec.centerx
                        centery = rec.bottom + 15
                        width = max(30, rec.width - 8)
                        height = BASE_NOMBRE_SIZE + 4
                        return pygame.Rect(centerx - width//2, centery - height//2, width, height)
                except Exception:
                    pass
            except Exception:
                pass
            return None

        # función helper que dibuja jugadas dentro de un rect (vertical u horizontal según caja)
        # función helper que dibuja jugadas dentro de un rect (vertical u horizontal según caja)
        def draw_plays_in_bajada(jugador, bloque_rect):
            """
            Dibuja las jugadas alineadas al inicio (Izquierda->Derecha o Arriba->Abajo).
            Si las jugadas exceden el tamaño de la caja, comprime el solapamiento dinámicamente
            Y ESCALA el tamaño de la carta si es necesario (Fix Rondas 3 y 4).
            """
            if not bloque_rect:
                return
            
            # Obtener jugadas crudas
            plays_source = getattr(jugador, "playMade", []) or getattr(jugador, "jugadas_bajadas", [])
            if not plays_source:
                return

            # --- PASO 1: Procesar y validar jugadas ---
            jugadas_validas = []
            total_cartas_count = 0
            
            for play_index, jugada in enumerate(plays_source):
                # Resolver si es lista de strings o punteros
                if isinstance(jugada, list) and jugada and isinstance(jugada[0], str):
                    resolved = None
                    if hasattr(jugador, "jugadas_bajadas") and len(jugador.jugadas_bajadas) > play_index:
                        resolved = jugador.jugadas_bajadas[play_index]
                    if resolved is None: continue
                    jugada = resolved

                resolved_jugada = resolve_play(jugador, jugada, play_index)
                if not resolved_jugada: continue

                # Identificar subtipos (trio/straight) para poder separar diccionarios mixtos
                sub_list = []
                if isinstance(resolved_jugada, dict):
                    if "trio" in resolved_jugada and resolved_jugada["trio"]:
                        sub_list.append(("trio", resolved_jugada["trio"]))
                    if "straight" in resolved_jugada and resolved_jugada["straight"]:
                        sub_list.append(("straight", resolved_jugada["straight"]))
                elif isinstance(resolved_jugada, list):
                    # Inferencia simple
                    naturals = [c for c in resolved_jugada if not getattr(c, "joker", False)]
                    if len(naturals) >= 2 and all(c.value == naturals[0].value for c in naturals):
                        inferred = "trio"
                    else:
                        inferred = "straight"
                    sub_list.append((inferred, resolved_jugada))
                
                for subtype, cartas in sub_list:
                    if len(cartas) > 0:
                        jugadas_validas.append({
                            "subtype": subtype, 
                            "cartas": cartas, 
                            "play_index": play_index
                        })
                        total_cartas_count += len(cartas)

            if not jugadas_validas: return

            rects_jugadas[jugador.playerName] = []
            
            # --- Configuración de Orientación ---
            vertical_boxes = {"baj2", "baj3", "baj6", "baj7"}
            box_name = next((k for k, v in boxes.items() if v == bloque_rect), None)
            is_vertical = box_name in vertical_boxes

            # Margen entre una jugada y la siguiente (ej. entre el trio y la escalera)
            GAP_ENTRE_JUGADAS = 15 
            PAD = 8 # Margen interno de la caja

            # --- Lógica VERTICAL (Jugadores Laterales) ---
            if is_vertical:
                # 1. Definir tamaño de carta (rotada)
                card_long = int(min(bloque_rect.width * 0.90, 110)) # Ancho visual (Alto real)
                card_short = int(card_long * 0.68)                  # Alto visual (Ancho real)
                
                # --- AUTO-ESCALADO VERTICAL ---
                # Si tenemos 3 jugadas, necesitamos altura para (3 * card_short) + 2 Gaps.
                # Si no cabe, reducimos el tamaño de la carta.
                min_height_needed = (len(jugadas_validas) * card_short) + ((len(jugadas_validas) - 1) * GAP_ENTRE_JUGADAS)
                avail_h = bloque_rect.height - (PAD * 2)
                
                if min_height_needed > avail_h:
                    ratio = avail_h / min_height_needed
                    # Reducimos tamaño (factor 0.95 para seguridad)
                    card_short = int(card_short * ratio * 0.95)
                    card_long = int(card_short / 0.68)
                # ------------------------------

                x_centrado = bloque_rect.x + (bloque_rect.width - card_long) // 2
                
                # 2. Calcular espacio necesario vs disponible
                overlap_ideal = int(card_short * 0.35) 
                
                altura_base_fija = (len(jugadas_validas) * card_short) + ((len(jugadas_validas) - 1) * GAP_ENTRE_JUGADAS)
                espacio_disponible_overlap = avail_h - altura_base_fija
                
                cartas_que_solapan = total_cartas_count - len(jugadas_validas)
                
                if cartas_que_solapan > 0:
                    overlap_calculado = espacio_disponible_overlap // cartas_que_solapan
                    solapamiento = min(overlap_ideal, overlap_calculado)
                    solapamiento = max(8, solapamiento) # Permitimos solapamiento más apretado si es necesario
                else:
                    solapamiento = 0

                # 3. Dibujar secuencialmente de Arriba hacia Abajo
                cursor_y = bloque_rect.y + PAD
                
                for info in jugadas_validas:
                    cartas = info["cartas"]
                    n = len(cartas)
                    
                    altura_jugada = card_short + (n - 1) * solapamiento
                    
                    inicio_rect = pygame.Rect(x_centrado, cursor_y, card_long, card_short)
                    final_rect = pygame.Rect(x_centrado, cursor_y + (n-1)*solapamiento, card_long, card_short)
                    
                    rects_jugadas[jugador.playerName].append({
                        "inicio": inicio_rect,
                        "final": final_rect,
                        "rect_total": inicio_rect.union(final_rect),
                        "tipo": info["subtype"],
                        "play_index": info["play_index"],
                        "cartas": cartas
                    })

                    for i, carta in enumerate(cartas):
                        pos_y = cursor_y + (i * solapamiento)
                        try:
                            img = get_card_image(carta)
                            img = pygame.transform.smoothscale(img, (card_short, card_long))
                            img = pygame.transform.rotate(img, 90)
                        except:
                            img = pygame.Surface((card_long, card_short))
                            img.fill((200,200,200))
                        
                        # Dibujar siempre, el escalado previo asegura que cabe
                        screen.blit(img, (x_centrado, pos_y))

                    cursor_y += altura_jugada + GAP_ENTRE_JUGADAS


            # --- Lógica HORIZONTAL (Jugador Local / Superiores) ---
            else:
                # 1. Definir tamaño de carta inicial
                card_h = int(min(bloque_rect.height * 0.95, 160)) 
                card_w = int(card_h * 0.68)
                
                # --- AUTO-ESCALADO HORIZONTAL (FIX PARA RONDA 3/4) ---
                # Calculamos si las CABECERAS de las 3 jugadas (o las que sean) caben a lo ancho
                min_width_needed = (len(jugadas_validas) * card_w) + ((len(jugadas_validas) - 1) * GAP_ENTRE_JUGADAS)
                avail_w = bloque_rect.width - (PAD * 2)

                if min_width_needed > avail_w:
                    # Si no caben, calculamos el ratio de reducción
                    ratio = avail_w / min_width_needed
                    # Aplicamos reducción con un pequeño margen de seguridad
                    card_w = int(card_w * ratio * 0.95)
                    card_h = int(card_w / 0.68)
                # -----------------------------------------------------

                # Corrección de perspectiva (arriba/abajo)
                offset_distancia = 15  
                base_y = bloque_rect.y + (bloque_rect.height - card_h) // 2
                
                if jugador == jugador_local:
                    y_centrado = base_y - offset_distancia
                else:
                    y_centrado = base_y + offset_distancia

                # 2. Calcular espacio diferenciado
                overlap_trio_target = int(card_w * 0.28)      
                overlap_straight_max = int(card_w * 0.50)     
                
                trios = [j for j in jugadas_validas if j["subtype"] == "trio"]
                straights = [j for j in jugadas_validas if j["subtype"] == "straight"]
                
                total_gaps = (len(jugadas_validas) - 1) * GAP_ENTRE_JUGADAS
                w_avail = avail_w - total_gaps # Usamos avail_w calculado arriba
                
                w_heads = len(jugadas_validas) * card_w 
                w_for_overlaps = max(0, w_avail - w_heads) # Evitamos negativos
                
                steps_trios = sum(len(t["cartas"]) - 1 for t in trios)
                steps_straights = sum(len(s["cartas"]) - 1 for s in straights)
                
                w_needed_trios = steps_trios * overlap_trio_target
                
                overlap_trio = overlap_trio_target
                overlap_straight = 0
                use_differentiated = True
                
                if w_needed_trios > w_for_overlaps:
                    use_differentiated = False 
                else:
                    if steps_straights > 0:
                        w_remaining = w_for_overlaps - w_needed_trios
                        overlap_straight = w_remaining // steps_straights
                        overlap_straight = min(overlap_straight, overlap_straight_max)
                        if overlap_straight < 10: # Umbral mínimo reducido
                            use_differentiated = False 

                if not use_differentiated:
                    total_steps = steps_trios + steps_straights
                    if total_steps > 0:
                        global_overlap = w_for_overlaps // total_steps
                        global_overlap = max(10, global_overlap) # Mínimo visible de seguridad
                    else:
                        global_overlap = 0
                    overlap_trio = global_overlap
                    overlap_straight = global_overlap

                # 3. Dibujar secuencialmente de Izquierda a Derecha
                cursor_x = bloque_rect.x + PAD
                
                for info in jugadas_validas:
                    cartas = info["cartas"]
                    n = len(cartas)
                    subtype = info["subtype"]
                    
                    if subtype == "trio":
                        current_overlap = overlap_trio
                    else:
                        current_overlap = overlap_straight
                        
                    ancho_jugada = card_w + (n - 1) * current_overlap
                    
                    inicio_rect = pygame.Rect(cursor_x, y_centrado, card_w, card_h)
                    final_rect = pygame.Rect(cursor_x + (n-1)*current_overlap, y_centrado, card_w, card_h)
                    
                    rects_jugadas[jugador.playerName].append({
                        "inicio": inicio_rect,
                        "final": final_rect,
                        "rect_total": inicio_rect.union(final_rect),
                        "tipo": info["subtype"],
                        "play_index": info["play_index"],
                        "cartas": cartas
                    })

                    for i, carta in enumerate(cartas):
                        pos_x = cursor_x + (i * current_overlap)
                        try:
                            img = get_card_image(carta)
                            img = pygame.transform.smoothscale(img, (card_w, card_h))
                        except:
                            img = pygame.Surface((card_w, card_h))
                            img.fill((200,200,200))
                        
                        # Ya no necesitamos clipping estricto porque el auto-escalado garantiza que cabe
                        screen.blit(img, (pos_x, y_centrado))
                    
                    cursor_x += ancho_jugada + GAP_ENTRE_JUGADAS
        # Dibujar todas las jugadas usando el mapping construido
            #esta es una prueba para ver los punto de collion
            '''for p_name, jugadas in rects_jugadas.items():
                for j in jugadas:
                    # Dibujamos el área sensible que definimos en el evento
                    debug_rect = j["rect_total"].inflate(60, 60) 
                    s = pygame.Surface((debug_rect.width, debug_rect.height), pygame.SRCALPHA)
                    s.fill((255, 255, 0, 50)) # Amarillo transparente
                    screen.blit(s, debug_rect.topleft)
                    pygame.draw.rect(screen, (255, 255, 0), debug_rect, 1)'''
        for p in players:
            p_name = getattr(p, "playerName", None)
            baj_rect = player_baj_rect.get(p_name)
            if baj_rect:
                draw_plays_in_bajada(p, baj_rect)

        # El nombre del jugador local se dibuja arriba de su caja (ver sección de jugador local) — no es necesario dibujarlo otra vez aquí

        # --- FASE DE MOSTRAR ORDEN ---
        if fase == "mostrar_orden":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.blit(fondo_img, (0, 0))

            # --- RECTÁNGULO DE FONDO GRIS ---
            ancho_rect = 420
            alto_rect = 60 + 40 * len(mensaje_orden.split("\n"))
            x_rect = (WIDTH - ancho_rect) // 2
            y_rect = HEIGHT // 2 - 180  # Más arriba

            # --- Usa la fuente personalizada desde assets ---
            font_path = os.path.join(ASSETS_PATH, "PressStart2P-Regular.ttf")
            font_orden = pygame.font.Font(font_path, 25)  # Fuente de videojuego

            rect_fondo = pygame.Rect(x_rect, y_rect, ancho_rect, alto_rect)
            pygame.draw.rect(screen, (60, 60, 60), rect_fondo, border_radius=18)
            pygame.draw.rect(screen, (180, 180, 180), rect_fondo, 2, border_radius=18)

            lineas = mensaje_orden.split("\n")
            for i, linea in enumerate(lineas):
                texto = font_orden.render(linea, True, (255, 255, 255))  # Color blanco
                rect = texto.get_rect(center=(WIDTH // 2, y_rect + 36 + i * 40))
                screen.blit(texto, rect)
            pygame.display.flip()
            # Espera 5 segundos y pasa a la fase de juego
            if time.time() - tiempo_inicio_orden >= 5:
                
                #Cambiar aqui juego1 para ronda 1 y juego2 para ronda 2 para hacer test
                fase = "ronda1"
                #-------------------------


                #Aquí voy a inicializar la ronda
                #round = startRound(players, screen)[0]
                #for c in round.discards:
                #    mazo_descarte.append(c)
                #deckForRound = [c for c in round.deck.cards if c!= round.discards]
                #print(str(round.discards))

                #mainGameLoop(screen, players, deck, mazo_descarte, nombre, zona_cartas)
                pass
            continue

        # --- DETECTAR FIN DE RONDA ---
        if fase == "ronda1":    # Puede quedarse "juego"  :)
            for jugador in players:
                if not getattr(jugador, "isSpectator", False): 
                    if hasattr(jugador, "playerHand") and len(jugador.playerHand) == 0:
                        # Calcular puntos de todos los jugadores
                        for p in players:
                            p.calculatePoints()
                        aplausos_sound_path = os.path.join(ASSETS_PATH, "sonido", "aplauso.wav")
                        aplausos_sound = pygame.mixer.Sound(aplausos_sound_path)
                        aplausos_sound.play()
                        fase = "fin1"
                        fase_fin_tiempo = time.time()
                        break

        # --- FASE DE FIN ---
        if fase == "fin1":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.blit(fondo_img, (0, 0))
            mostrar_puntuaciones_final(screen, fondo_img, players, WIDTH, HEIGHT, ASSETS_PATH, round_number=1)
            pygame.display.flip()
            # Espera 7 segundos y termina el juego (puedes cambiar el tiempo)
            if time.time() - fase_fin_tiempo >= 7:
                # Comprobar si terminó el juego
                active_players = [p for p in players if not getattr(p, "isSpectator", False)]
                if len(active_players) <= 1:
                    fase = "game_over"
                else:
                    fase = "eleccion"
                    roundOne = False
                    roundTwo = True   # Para Prueba
            continue
        
        if fase == "ronda2":
            for jugador in players:
                if not getattr(jugador, "isSpectator", False):
                    if hasattr(jugador, "playerHand") and len(jugador.playerHand) == 0:
                        for p in players:
                            p.calculatePoints()
                        aplausos_sound_path = os.path.join(ASSETS_PATH, "sonido", "aplauso.wav")
                        aplausos_sound = pygame.mixer.Sound(aplausos_sound_path)
                        aplausos_sound.play()
                        fase = "fin2"
                        fase_fin_tiempo = time.time()
                        break
        
        if fase == "fin2":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                screen.blit(fondo_img, (0, 0))
                mostrar_puntuaciones_final(screen, fondo_img, players, WIDTH, HEIGHT, ASSETS_PATH, round_number=2)
                pygame.display.flip()
                # Espera 7 segundos y termina el juego (puedes cambiar el tiempo)
                if time.time() - fase_fin_tiempo >= 7:
                    active_players = [p for p in players if not getattr(p, "isSpectator", False)]
                    if len(active_players) <= 1:
                        fase = "game_over"
                    else:
                        fase = "eleccion"
                        roundTwo = False
                        roundThree = True
                continue

        if fase == "ronda3":
            for jugador in players:
                if not getattr(jugador, "isSpectator", False):
                    if hasattr(jugador, "playerHand") and len(jugador.playerHand) == 0:
                        for p in players:
                            p.calculatePoints()
                        aplausos_sound_path = os.path.join(ASSETS_PATH, "sonido", "aplauso.wav")
                        aplausos_sound = pygame.mixer.Sound(aplausos_sound_path)
                        aplausos_sound.play()                    
                        fase = "fin3"
                        fase_fin_tiempo = time.time()
                        break

        if fase == "fin3":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                screen.blit(fondo_img, (0, 0))
                mostrar_puntuaciones_final(screen, fondo_img, players, WIDTH, HEIGHT, ASSETS_PATH, round_number=3)
                pygame.display.flip()
                # Espera 7 segundos y termina el juego (puedes cambiar el tiempo)
                if time.time() - fase_fin_tiempo >= 7:
                    active_players = [p for p in players if not getattr(p, "isSpectator", False)]
                    if len(active_players) <= 1:
                        fase = "game_over"
                    else:
                        fase = "eleccion"
                        roundThree = False
                        roundFour = True
                continue

        if fase == "ronda4":
            for jugador in players:
                if not getattr(jugador, "isSpectator", False):
                    if hasattr(jugador, "playerHand") and len(jugador.playerHand) == 0:
                        for p in players:
                            p.calculatePoints()
                        aplausos_sound_path = os.path.join(ASSETS_PATH, "sonido", "aplauso.wav")
                        aplausos_sound = pygame.mixer.Sound(aplausos_sound_path)
                        aplausos_sound.play()
                        fase = "fin4"
                        fase_fin_tiempo = time.time()
                        break
        if fase == "fin4":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                screen.blit(fondo_img, (0, 0))
                mostrar_puntuacion_final_detallada(screen, fondo_img, players, WIDTH, HEIGHT, ASSETS_PATH, round_number=4)
                pygame.display.flip()
                # Espera 7 segundos y termina el juego (puedes cambiar el tiempo)
                if time.time() - fase_fin_tiempo >= 7:
                    active_players = [p for p in players if not getattr(p, "isSpectator", False)]
                    if len(active_players) <= 1:
                        fase = "game_over"
                    else:
                        fase = "eleccion"
                        roundFour = False
                        roundOne = True
                continue

        if fase == "game_over":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                screen.blit(fondo_img, (0, 0))
                mostrar_ganador_final(screen, fondo_img, players, WIDTH, HEIGHT, ASSETS_PATH)
                pygame.display.flip()
                continue
        
        
        if mensaje_temporal and time.time() - mensaje_tiempo < 5:
            def wrap_preserve_words(text, max_chars=35):
                words = text.split()
                if not words:
                    return []
                lines = []
                cur = words[0]
                for w in words[1:]:
                    if len(cur) + 1 + len(w) <= max_chars:
                        cur += " " + w
                    else:
                        lines.append(cur)
                        cur = w
                lines.append(cur)
                return lines

            font_msg = get_game_font(18) 
            lines = wrap_preserve_words(mensaje_temporal, 35)
            line_h = font_msg.get_linesize()
            base_x = WIDTH // 2
            base_y = HEIGHT // 2 + 160  
            total_h = line_h * len(lines)
            start_y = base_y - total_h // 2

            for i, line in enumerate(lines):
                surf = font_msg.render(line, True, (255, 255, 255))
                rect = surf.get_rect(center=(base_x, start_y + i * line_h))
                # borde negro alrededor (8 direcciones)
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
                    screen.blit(font_msg.render(line, True, ( (165, 42, 42))), (rect.x + dx, rect.y + dy))
                screen.blit(surf, rect)
        elif mensaje_temporal and time.time() - mensaje_tiempo >= 5:
            mensaje_temporal = ""
        
        ctrl_volumen.actualizar_y_dibujar()
        
        pygame.display.flip()
        pygame.time.Clock().tick(60) # Esto mantiene el juego estable a 60 FPS
    return


def mostrar_puntuaciones_final(screen, fondo_img, players, WIDTH, HEIGHT, ASSETS_PATH, round_number=None):
    """
    Muestra un panel centrado que diga:
    PUNTUACIONES FINALES
    Ronda: <n>        (si round_number no es None)
    y debajo, la lista de jugadores en el orden dado.
    Ajustes: mayor espaciado y mejor centrado para que no se corte abajo.
    """
    jugadores = list(players)  # respetar orden de juego

    filas = max(1, len(jugadores))
    espacio_entre = 52        # un poco más de separación entre filas
    top_padding = 36
    bottom_padding = 40
    header_h = 120            # más espacio para título + subtítulo

    alto_rect = header_h + filas * espacio_entre + top_padding + bottom_padding
    ancho_rect = min(WIDTH - 140, 820)

    # evitar que el rect se salga de la pantalla; reducir si es necesario
    if alto_rect + 80 > HEIGHT:
        alto_rect = HEIGHT - 80
        espacio_entre = max(36, (alto_rect - header_h - top_padding - bottom_padding) // max(1, filas))

    x_rect = (WIDTH - ancho_rect) // 2
    y_rect = max(40, (HEIGHT - alto_rect) // 2)

    rect_fondo = pygame.Rect(x_rect, y_rect, ancho_rect, alto_rect)

    # Fondo semitransparente + borde
    overlay = pygame.Surface((rect_fondo.width, rect_fondo.height), pygame.SRCALPHA)
    overlay.fill((18, 18, 18, 200))
    screen.blit(overlay, rect_fondo.topleft)
    pygame.draw.rect(screen, (180, 180, 180), rect_fondo, 2, border_radius=12)

    # Fuentes (usar la fuente del juego si existe)
    title_font = get_game_font(34)
    subtitle_font = get_game_font(18)
    player_font = get_game_font(22)
    info_font = get_game_font(12)
    center_x = x_rect + ancho_rect // 2

    # Título grande centrado (con borde para legibilidad)
    title_txt = "Puntuaciones Finales"
    title_surf = title_font.render(title_txt, True, (255, 255, 255))
    title_pos = (center_x - title_surf.get_width() // 2, y_rect + 18)
    # borde simple
    for ox, oy in [(-1,0),(1,0),(0,-1),(0,1)]:
        screen.blit(title_font.render(title_txt, True, (0,0,0)), (title_pos[0] + ox, title_pos[1] + oy))
    screen.blit(title_surf, title_pos)

    # Subtítulo Ronda (si aplica) — centrado, con margen extra debajo
    players_start_y = title_pos[1] + title_surf.get_height() + 12
    if round_number is not None:
        sub_txt = f"Ronda: {round_number}"
        sub_surf = subtitle_font.render(sub_txt, True, (220, 220, 220))
        sub_pos = (center_x - sub_surf.get_width() // 2, players_start_y)
        screen.blit(sub_surf, sub_pos)
        players_start_y = sub_pos[1] + sub_surf.get_height() + 18
    else:
        players_start_y += 8

    # Lista de jugadores (centrada horizontalmente, más abajo)
    max_players_display = (alto_rect - (players_start_y - y_rect) - bottom_padding) // espacio_entre
    # si hay demasiados jugadores, ajustar espacio para que entren
    if filas > max_players_display and max_players_display > 0:
        espacio_entre = max(32, (alto_rect - (players_start_y - y_rect) - bottom_padding) // filas)

    for i, jugador in enumerate(jugadores):
        is_spec = getattr(jugador, "isSpectator", False)
        nombre = getattr(jugador, "playerName", f"Jugador {i+1}")
        puntos = getattr(jugador, "playerPoints", 0)
        
        status_text = " (ESPECTADOR)" if is_spec else ""
        color_texto = (200, 200, 200) if is_spec else (240, 240, 220)
        
        linea = f"{i+1}. {nombre}{status_text}  —  {puntos} pts"
        y_line = players_start_y + i * espacio_entre
        # centrar la línea
        surf = player_font.render(linea, True, color_texto)
        x_line = center_x - surf.get_width() // 2
        # borde ligero para contraste sin tapar fondo
        for ox, oy in [(-1,0),(1,0),(0,-1),(0,1)]:
            screen.blit(player_font.render(linea, True, (0,0,0)), (x_line + ox, y_line + oy))
        screen.blit(surf, (x_line, y_line))

    # Mensaje de instrucción al final (más abajo con margen)
    info_txt = "Iniciando Siguiente Ronda..."
    info_surf = info_font.render(info_txt, True, (190,190,190))
    info_rect = info_surf.get_rect(center=(center_x, y_rect + alto_rect - 22))
    screen.blit(info_surf, info_rect.topleft)


def mostrar_puntuacion_final_detallada(screen, fondo_img, players, WIDTH, HEIGHT, ASSETS_PATH, round_number=None):
    """
    Muestra pantalla de 'Puntuación final' con:
      1er Lugar, 2do Lugar, ...
    Ahora el 1er lugar será el jugador con MENOS puntos (orden ascendente).
    round_number: opcional, muestra "Ronda: <n>" debajo del título si se pasa.
    """
    if not players:
        return

    # ordenar por puntos ASCENDENTE => primero = menor puntaje
    jugadores_ordenados = sorted(players, key=lambda j: getattr(j, "playerPoints", 0))

    # Helper para ordinales simples en español
    def ordinal_es(n):
        if n == 1:
            return "1er"
        if n == 2:
            return "2do"
        if n == 3:
            return "3er"
        return f"{n}º"

    filas = len(jugadores_ordenados)
    padding_y = 28
    espacio_linea = 44
    header_h = 84
    alto_rect = header_h + filas * espacio_linea + padding_y * 2
    ancho_rect = min(WIDTH - 120, 720 + max(0, (filas - 4) * 24))

    x_rect = (WIDTH - ancho_rect) // 2
    y_rect = max(40, (HEIGHT - alto_rect) // 2)

    rect_fondo = pygame.Rect(x_rect, y_rect, ancho_rect, alto_rect)

    # Fondo semitransparente + borde
    overlay = pygame.Surface((rect_fondo.width, rect_fondo.height), pygame.SRCALPHA)
    overlay.fill((16, 16, 16, 220))
    screen.blit(overlay, rect_fondo.topleft)
    pygame.draw.rect(screen, (200, 200, 200), rect_fondo, 2, border_radius=10)

    # Fuentes (usar la fuente del juego)
    title_font = get_game_font(28)
    place_font = get_game_font(20)
    info_font = get_game_font(12)

    # Dibuja título con borde simple
    title_txt = "Puntuación final"
    title_surf = title_font.render(title_txt, True, (255, 255, 255))
    tx, ty = x_rect + ancho_rect // 2, y_rect + 20
    # borde
    for ox, oy in [(-1,0),(1,0),(0,-1),(0,1)]:
        screen.blit(title_font.render(title_txt, True, (0,0,0)), (tx - title_surf.get_width()//2 + ox, ty + oy))
    screen.blit(title_surf, (tx - title_surf.get_width()//2, ty))

    # Subtítulo: Ronda si se pasó
    players_start_y = ty + title_surf.get_height() + 10
    if round_number is not None:
        sub_txt = f"Ronda: {round_number}"
        sub_surf = info_font.render(sub_txt, True, (220, 220, 220))
        sub_x = x_rect + ancho_rect // 2 - sub_surf.get_width() // 2
        sub_y = players_start_y
        screen.blit(sub_surf, (sub_x, sub_y))
        players_start_y = sub_y + sub_surf.get_height() + 12

    # Listado de lugares (primero = menor puntaje)
    for i, jugador in enumerate(jugadores_ordenados):
        lugar = i + 1
        is_spec = getattr(jugador, "isSpectator", False)
        nombre = getattr(jugador, "playerName", f"Jugador {lugar}")
        puntos = getattr(jugador, "playerPoints", 0)
        
        status_text = " (ESPECTADOR)" if is_spec else ""
        color_texto = (180, 180, 180) if is_spec else (240, 240, 200)
        
        linea = f"{ordinal_es(lugar)} Lugar: {nombre}{status_text} — {puntos} pts"
        y_line = players_start_y + i * espacio_linea

        surf = place_font.render(linea, True, color_texto)
        rx = x_rect + ancho_rect // 2 - surf.get_width() // 2
        ry = y_line
        # borde ligero
        for ox, oy in [(-1,0),(1,0),(0,-1),(0,1)]:
            screen.blit(place_font.render(linea, True, (0,0,0)), (rx+ox, ry+oy))
        screen.blit(surf, (rx, ry))

    # Info para continuar (vacío o personalizado)
    info_txt = ""
    info_surf = info_font.render(info_txt, True, (200,200,200))
    info_rect = info_surf.get_rect(center=(x_rect + ancho_rect//2, y_rect + alto_rect - 18))
    screen.blit(info_surf, info_rect.topleft)

def mostrar_ganador_final(screen, fondo_img, players, WIDTH, HEIGHT, ASSETS_PATH):
    """
    Muestra una pantalla especial de 'Fin de Partida' declarando al ganador absoluto.
    """
    if not players:
        return

    # Clasificar jugadores
    activos = [p for p in players if not getattr(p, "isSpectator", False)]
    jugadores_ordenados = sorted(players, key=lambda j: getattr(j, "playerPoints", 0))

    if activos:
        ganador = sorted(activos, key=lambda j: getattr(j, "playerPoints", 0))[0]
    else:
        ganador = jugadores_ordenados[0]

    ancho_rect = min(WIDTH - 100, 850)
    alto_rect = min(HEIGHT - 100, 500)
    x_rect = (WIDTH - ancho_rect) // 2
    y_rect = (HEIGHT - alto_rect) // 2

    rect_fondo = pygame.Rect(x_rect, y_rect, ancho_rect, alto_rect)
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0,0))

    panel = pygame.Surface((ancho_rect, alto_rect), pygame.SRCALPHA)
    panel.fill((20, 20, 30, 230))
    screen.blit(panel, (x_rect, y_rect))
    pygame.draw.rect(screen, (255, 215, 0), rect_fondo, 4, border_radius=15)

    winner_font = get_game_font(40)
    name_font = get_game_font(30)
    ranking_font = get_game_font(18)
    info_font = get_game_font(12)
    center_x = WIDTH // 2

    title_txt = "¡GANADOR ABSOLUTO!"
    title_surf = winner_font.render(title_txt, True, (255, 255, 0))
    screen.blit(title_surf, (center_x - title_surf.get_width()//2, y_rect + 40))

    winner_name = getattr(ganador, "playerName", "Desconocido")
    name_surf = name_font.render(winner_name, True, (255, 255, 255))
    screen.blit(name_surf, (center_x - name_surf.get_width()//2, y_rect + 110))

    start_y_ranking = y_rect + 230
    for i, p in enumerate(jugadores_ordenados[:4]):
        p_name = getattr(p, "playerName", "???")
        p_pts = getattr(p, "playerPoints", 0)
        is_spec = getattr(p, "isSpectator", False)
        linea = f"{i+1}o {p_name}: {p_pts} pts"
        if is_spec: linea += " (Expulsado)"
        
        color = (255, 255, 255) if p == ganador else (180, 180, 180)
        r_surf = ranking_font.render(linea, True, color)
        screen.blit(r_surf, (center_x - r_surf.get_width()//2, start_y_ranking + i * 35))

    msg_final = "Gracias por jugar Rummy 500"
    msg_surf = info_font.render(msg_final, True, (150, 150, 150))
    screen.blit(msg_surf, (center_x - msg_surf.get_width()//2, y_rect + alto_rect - 30))

def actualizar_indices_visual_hand(visual_hand):
    """
    Reasigna el índice visual (id_visual) a cada carta en visual_hand.
    """
    for idx, carta in enumerate(visual_hand):
        carta.id_visual = idx

def compactar_visual_hand(visual_hand):
    """
    Si falta una carta (None o eliminada), mueve las cartas hacia la izquierda
    y reasigna los índices visuales para que no queden huecos.
    """
    # Elimina cualquier carta None o inexistente
    visual_hand = [c for c in visual_hand if c is not None]

    # Reasigna los índices visuales
    for idx, carta in enumerate(visual_hand):
        carta.id_visual = idx

    return visual_hand

def reiniciar_visual(jugador_local, visual_hand, cuadros_interactivos, cartas_ref):
    global dragging, carta_arrastrada, drag_rect, drag_offset_x, organizar_habilitado

    # ========== 1. GUARDAR COPIA DEL ORDEN VISUAL ANTES ==========
    orden_anterior = [carta for carta in visual_hand]   # copia exacta del orden visual previo

    # ========== 2. LIMPIAR ESTRUCTURAS ==========
    visual_hand.clear()
    cuadros_interactivos.clear()
    cartas_ref.clear()

    # ======= 3. CREAR NUEVO visual_hand DESDE playerHand ========
    # Pero SIN perder el orden anterior si la carta aún existe
    mano_actual = jugador_local.playerHand[:]  # copia

    # Primero agregamos en el mismo orden que estaban antes
    for carta_prev in orden_anterior:
        if carta_prev in mano_actual:
            visual_hand.append(carta_prev)
            mano_actual.remove(carta_prev)  # evitar duplicados

    # Después agregamos cualquier carta nueva (como la tomada)
    for carta in mano_actual:
        visual_hand.append(carta)

    # Reseteamos índices visuales
    for idx, carta in enumerate(visual_hand):
        carta.id_visual = idx

    # ======= 4. Reset de arrastre ========
    dragging = False
    carta_arrastrada = None
    drag_rect = None
    drag_offset_x = 0

    # ======= 5. Organizar habilitado ========
    organizar_habilitado = True


def ocultar_elementos_visual(screen, fondo_img):
    """
    Oculta todo lo visual del juego excepto el fondo.
    """
    screen.blit(fondo_img, (0, 0))
    pygame.display.flip()

def mostrar_cartas_eleccion(screen, cartas_eleccion):
    for carta in cartas_eleccion:
        # Siempre muestra la carta de reverso
        img = get_card_image("PT")
        img = pygame.transform.smoothscale(img, (60, 90))
        screen.blit(img, carta.rect.topleft)
        
        # NUEVO PARA PRUEBAS
        # Dibuja el rectángulo de colisión para diagnóstico (QUITAR DESPUÉS)
        pygame.draw.rect(screen, (255, 0, 0), carta.rect, 2) # Rojo, 2px de grosor
        
        screen.blit(img, carta.rect.topleft)

def process_received_messagesUi2():
        """Procesa los mensajes recividos de la red"""
        if hasattr(network_manager,'received_data') and network_manager.received_data:
            with network_manager.lock:
                data = network_manager.received_data
                network_manager.received_data = None  # Limpiar despues de procesar

            #print(f"Procesando mensaje recibido en Ui2.py: {data.get("type")}")
            
            if network_manager.is_host:
                #with threading.Lock:
                # Si es un mensaje de ESTADO (como el que contiene cartas_disponibles, elecciones, etc.) en ui2
                if isinstance(data, dict) and data.get("type") in ["ELECTION_CARDS","SELECTION_UPDATE", "ESTADO_CARTAS", "ORDEN_COMPLETO"]:
                    network_manager.game_state.update(data)
                    print(f"Estado del juego actualizado: {network_manager.game_state}")
                elif isinstance(data, dict) and data.get("type") in ["BAJARSE","TOMAR_DESCARTE", "TOMAR_CARTA", "DESCARTE", "COMPRAR_CARTA", "PASAR_DESCARTE", "INICIAR_COMPRA","INSERTAR_CARTA","PASAR_COMPRA","REALIZAR_COMPRA","SWAP_JOKER","SALIR","DESCONEXION"]:
                    network_manager.moves_gameServer.append(data)
                # Si es la respuesta del PING...
                elif isinstance(data, dict) and data.get("type")=="PONG":
                    pass
                # Si es otro tipo de estructura/mensaje no clasificado
                else:
                    network_manager.incoming_messages.append(("raw", data)) # Opcional: para mensajes no clasificados
                    #print(f"Mensaje guardado en incoming_messages... raw {network_manager.incoming_messages}")

def recalcular_posiciones_eleccion(cartas_eleccion, WIDTH, HEIGHT):
    """Calcula y asigna el atributo .rect a todas las cartas de elección."""
    if not cartas_eleccion:
        return

    # Parámetros de diseño (ajustar según tu UI)
    CARD_WIDTH = 60
    CARD_HEIGHT = 90
    espacio = 120 # separación horizontal entre cartas

    centro_x = WIDTH // 2
    centro_y = HEIGHT // 2
    
    total_cartas = len(cartas_eleccion)
    total_ancho = espacio * (total_cartas - 1)
    inicio_x = centro_x - total_ancho // 2 # Punto de inicio para centrar

    for i, carta in enumerate(cartas_eleccion):
        # La línea clave: asigna el rect a la carta
        carta.rect = pygame.Rect(
            inicio_x + i * espacio, 
            centro_y - CARD_HEIGHT // 2, 
            CARD_WIDTH, 
            CARD_HEIGHT
        )


def play_risa_if_joker(cartas):
    global mostrar_joker_fondo, tiempo_joker_fondo
    risa_sound_path = os.path.join(ASSETS_PATH, "sonido", "risa.wav")
    risa_sound = pygame.mixer.Sound(risa_sound_path)
    for carta in cartas:
        if hasattr(carta, "joker") and carta.joker:
            risa_sound.play()
            mostrar_joker_fondo = True
            tiempo_joker_fondo = pygame.time.get_ticks()
            break

joker_fondo_img = pygame.image.load(os.path.join(ASSETS_PATH, "joker_fondo.png")).convert()
joker_fondo_img = pygame.transform.scale(joker_fondo_img, (WIDTH, HEIGHT))
mostrar_joker_fondo = False
tiempo_joker_fondo = 0

if __name__ == "__main__":
    #ocultar_elementos_visual(screen, fondo_img)  # Solo muestra el fondo al inicio
    main()
