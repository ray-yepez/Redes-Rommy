import pygame
# BT significara boton

#Colores
AZUL_PRINCIPAL = (25,64,147)
VERDE = (0,97,48)
NEGRO = (0,0,0)
AZUL_SECUNDARIO = (9,14,52)
MARRON = (75,42,5)
VERDE_CLARO = (143,191,33)
NARANJA = (241,132,28)
BLANCO = (255,255,255)
GRIS = (128,128,128)
SIN_COLOR = None
#fin de los colores

#FPS
FPS = 60
#Fin fps

#Fuentes
FUENTE_ARCO = "assets/fuentes/ARCO.ttf"
FUENTE_ACUIM_BOLD = "assets/fuentes/Acuim-Bold.otf"
FUENTE_GAME_OVER = "assets/fuentes/game_over.ttf"
FUENTE_GOMAWO = "assets/fuentes/Gomawo.ttf"
FUENTE_PRESS_START = "assets/fuentes/PressStart2P-Regular.ttf"
FUENTE_PIXEL_RAND = "assets/fuentes/Pixel-Rand.otf"
FUENTE_ARIAL = 'arial'
FUENTE_SANS_SERIF = 'sansserif'
#Fin de la fuentes

#Fuentes mas usadas
FUENTE_LLAMATIVA = FUENTE_ARCO
FUENTE_ESTANDAR = FUENTE_ACUIM_BOLD
#Fin de fuentes mas usadas


#tamaño de fuentes
F_PEQUENA = 14
F_MEDIANA = 34
F_GRANDE = 44
#fin de tamaño de fuentes

#colores de texto
COLOR_TEXTO_PRINCIPAL = NEGRO
COLOR_TEXTO_SECUNDARIO = BLANCO
#fin de colores de texto


#Ventana
pygame.init()
info = pygame.display.Info()
ANCHO_VENTANA = info.current_w
ALTO_VENTANA = info.current_h  # Ajuste para la barra de tareas

FONDO_VENTANA = VERDE
#Fin de la ventana


#Bordes de elementos
SIN_BORDE = 0
BORDE_LIGERO = 3
BORDE_INTERMEDIO = 8
BORDE_PRONUNCIADO = 15
#Fin de bordes de elementos


#Redondeo de elementos "borde radio"
REDONDEO_NORMAL = 28
REDONDEO_INTERMEDIO = 45
REDONDEO_PRONUNCIADO = 60
#Fin de redondeo de elementos

#Colores principales usados en botones y menus
ELEMENTO_FONDO_PRINCIPAL = BLANCO
ELEMENTO_FONDO_SECUNDARO = AZUL_PRINCIPAL
ELEMENTO_FONDO_TERCIARIO = VERDE
ELEMENTO_BORDE_PRINCIPAL = AZUL_PRINCIPAL
ELEMENTO_BORDE_SECUNDARIO = AZUL_SECUNDARIO
ELEMENTO_BORDE_TERCIARIO = MARRON
ELEMENTO_BORDE_CUATERNARIO = NARANJA
ELEMENTO_BORDE_QUINARIO = VERDE
ELEMENTO_HOVER_PRINCIPAL = NARANJA
ELEMENTO_CLICADO_PRINCIPAL = VERDE_CLARO
#fin de colores principales usados en botones y menus

#Dimensiones de elementos(botones por ejemplo)
ELEMENTO_PEQUENO_ANCHO = ANCHO_VENTANA*0.28
ELEMENTO_PEQUENO_ALTO = ANCHO_VENTANA*0.08

ELEMENTO_MEDIANO_ANCHO = ANCHO_VENTANA*0.32
ELEMENTO_MEDIANO_ALTO = ALTO_VENTANA*0.15

ELEMENTO_GRANDE_ANCHO = ANCHO_VENTANA*0.42
ELEMENTO_GRANDE_ALTO = ALTO_VENTANA*0.18

#Fin de dimensiones de botones


#Escala de elementos insertado (ej: imagenes)
SCALA = 0.17
#fin de Escala de elementos

#Menu de instrucciones,dimensiones
ANCHO_MENU_INSTRUCCIONES = ANCHO_VENTANA*0.95 
ALTO_MENU_INSTRUCCIONES = ALTO_VENTANA*0.95
TEXTO_DE_INSTRUCCIONES = "1. El último jugador en acumular menos de 500 puntos al acabar todos los juegos de la partida, gana la partida. \n2. El primer jugador en alcanzar o superar los 500 puntos es eliminado. \n3. En cada turno, cada jugador en su turno puede robar una carta del mazo o del descarte.\n4. Puedes robar una carta fuera de tu turno (Compra) pero de penalización debes robar otra carta.\n5. El objetivo es formar tríos o seguidillas de cartas para bajarse.\n6. Los tríos debe tener mínimo 3 cartas del mismo valor y no más de un Joker.\n7. Las seguidillas deben de ser de mínimo 4 cartas del mismo palo y valor ascendente, sin tener dos Jokers juntos.\n8. Cada juego consta de 4 rondas, cada ronda termina cuando un jugador consigue bajar todas sus cartas.\n9. Al finalizar cada ronda, los jugadores que no consiguieron bajarse suman las cartas en sus manos según su valor."
#fin de menu de instrucciones



#Menu Inicio, dimensiones
ANCHO_MENU_I = ANCHO_VENTANA
ALTO_MENU_I = ALTO_VENTANA
#fin del menu inicio



#Menu Cantidad de jugadores(CntJ) dimensiones
ANCHO_MENU_CNT_J = ANCHO_VENTANA*0.95
ALTO_MENU_CNT_J = ALTO_VENTANA*0.95
#Fin de menu Cantidad de Jugadores

#Menu Mesa de espera(mesa_espera) dimensiones
ANCHO_MENU_MESA_ESPERA = ANCHO_VENTANA
ALTO_MENU_MESA_ESPERA = ALTO_VENTANA
#Fin de menu Cantidad de Jugadores

#Menu Mesa de espera(mesa_espera) dimensiones
ANCHO_MENU_MESA = ANCHO_VENTANA*0.98
ALTO_MENU_MESA = ALTO_VENTANA*0.98
#Fin de menu Cantidad de Jugadores

#Menu Nombre de usario dimensiones
ANCHO_MENU_NOM_USUARIO = ANCHO_MENU_CNT_J
ALTO_MENU_NOM_USUARIO = ALTO_MENU_CNT_J
#Fin de menu Cantidad de Jugadores

# Menu Selección de Sala dimensiones
ANCHO_MENU_SELECCION_SALA = ANCHO_VENTANA * 0.95
ALTO_MENU_SELECCION_SALA = ALTO_VENTANA * 0.95

ESCALA_CARTAS = 0.10
ESCALA_DEMAS_CARTAS = 0.07
ESCALA_DMUCHAS_CARTAS = 0.08

#Evento jugador conectado
EVENTO_NUEVO_JUGADOR = pygame.USEREVENT + 1
EVENTO_SALAS_ENCONTRADAS = pygame.USEREVENT + 2
EVENTO_INICIAR_PARTIDA = pygame.USEREVENT + 3
# Agrega esto después de importar pygame
REDIBUJAR_CARTAS = pygame.USEREVENT + 4