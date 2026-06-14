import pygame
from recursos_graficos import constantes
from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta

# ===== IMPORTACIONES =====
# Importaciones de clases de interfaz
Mazo = importar_desde_carpeta(
    nombre_archivo="mazo_interfaz.py",
    nombre_clase="Mazo_interfaz",
    nombre_carpeta="logica_interfaz"
)
Jugador = importar_desde_carpeta(
    nombre_archivo="jugador_interfaz.py",
    nombre_clase="Jugador_interfaz",
    nombre_carpeta="logica_interfaz"
)
Carta = importar_desde_carpeta(
    nombre_archivo="cartas_interfaz.py",
    nombre_clase="Cartas_interfaz",
    nombre_carpeta="logica_interfaz"
)
BotonLogoMenu = importar_desde_carpeta("elementos_de_interfaz_de_usuario.py","BotonLogoMenu","recursos_graficos")

# Importar recursos graficos
Menu = importar_desde_carpeta("menu.py","Menu","recursos_graficos")
Boton = importar_desde_carpeta("elementos_de_interfaz_de_usuario.py","Boton","recursos_graficos")
CartelAlerta = importar_desde_carpeta("elementos_de_interfaz_de_usuario.py","CartelAlerta","recursos_graficos")

# ===== IMPORTACIONES DE MIXINS =====
from logica_interfaz.core.layout.posicionamiento import PosicionamientoMixin
from logica_interfaz.core.configuracion.utilidades import UtilidadesMixin
from logica_interfaz.core.datos.carga_datos import CargaDatosMixin
from logica_interfaz.core.datos.carga_visuales import CargaVisualesMixin
from logica_interfaz.core.logica_juego.turnos import TurnosMixin
from logica_interfaz.core.controles_ui.botones import BotonesMixin
from logica_interfaz.core.renderizado.mostrar import MostrarMixin
from logica_interfaz.core.configuracion.creacion import CreacionMesaMixin
from logica_interfaz.core.renderizado.actualizacion import ActualizacionMixin
from logica_interfaz.core.logica_juego.procesamiento import ProcesamientoMixin
from logica_interfaz.core.logica_juego.mano import ManoMixin
from logica_interfaz.core.red.acciones_red import AccionesRedMixin
from logica_interfaz.core.logica_juego.puntos import PuntosMixin
from logica_interfaz.core.controles_ui.menu_opciones import MenuOpcionesMixin
from logica_interfaz.core.controles_ui.alertas import AlertasMixin
from logica_interfaz.core.logica_juego.rondas import RondasMixin
from logica_interfaz.core.ui.menu_adaptado import Menu_adaptado

# ===== MIXIN ORDENAMIENTO (NUEVO) =====
from logica_interfaz.core.controles_ui.ordenamiento_mano import OrdenamientoManoMixin


# =============================================================================
# ── JUGADAS PRECARGADAS (Cheat/Admin) ────────────────────────────────────────
#
# Cada ronda tiene una lista de cartas con las que se reemplazará la mano del
# Host al presionar "Concluir Ronda".  Las cartas se expresan como tuplas
# (numero, figura) que coinciden con los valores usados en Cartas(numero, figura).
#
# Formato de cada carta:  (numero, figura)
#   - numero: 'A','2'..'10','J','Q','K','Joker'
#   - figura: 'Pica','Corazon','Diamante','Trebol','Especial'
#
# Deja las listas vacías [] y el sistema las ignorará (la mano no cambiará).
# Rellena cada lista con exactamente las cartas que quieras que tenga el Host
# al inicio del turno de conclusión; no tienen que sumar 10, pueden ser menos.
#
# EJEMPLO con cartas reales (descomenta y ajusta a tu gusto):
#
#   RONDA_1: [
#       # Trío de 7
#       ("7", "Pica"), ("7", "Corazon"), ("7", "Diamante"),
#       # Seguidilla de Corazon 4-5-6-7  (el 7 ya está arriba, pero el servidor
#       # acepta duplicados en la mano del Host para que él los juegue)
#       ("4", "Trebol"), ("5", "Trebol"), ("6", "Trebol"), ("7", "Trebol"),
#   ],
#
# =============================================================================
JUGADAS_PRECARGADAS = {
    # Ronda 1: 1 trío + 1 seguidilla  ─────────────────────────────────────────
    1: [],   # ← rellena con tuplas (numero, figura)

    # Ronda 2: 2 seguidillas  ──────────────────────────────────────────────────
    2: [],   # ← rellena con tuplas (numero, figura)

    # Ronda 3: 3 tríos  ────────────────────────────────────────────────────────
    3: [],   # ← rellena con tuplas (numero, figura)

    # Ronda 4: 2 tríos + 1 seguidilla  ────────────────────────────────────────
    4: [],   # ← rellena con tuplas (numero, figura)
}
# =============================================================================


# =============================================================================
# ── MIXIN CHEAT/ADMIN ─────────────────────────────────────────────────────────
#
# Toda la lógica del botón "Concluir Ronda" está encapsulada en este mixin
# para no ensuciar el __init__ de Mesa_interfaz.  Se integra simplemente
# añadiendo CheatAdminMixin a la lista de herencias de Mesa_interfaz.
# =============================================================================
class CheatAdminMixin:
    """
    Mixin que añade el botón "Concluir Ronda" exclusivo para el Host.

    Responsabilidades:
      1. crear_boton_concluir_ronda(mesa_menu) → construye el Boton y lo
         adjunta al menú de la mesa.
      2. _es_host() → True si este cliente es el creador de la sala (id == 1
         o su nombre coincide con nombre_creador).
      3. _accion_concluir_ronda() → reemplaza la mano del Host con las cartas
         precargadas para la ronda actual y envía el mensaje de red
         "concluir_ronda" al servidor.
      4. _construir_mano_cheat(ronda) → convierte las tuplas de
         JUGADAS_PRECARGADAS en objetos Cartas_interfaz listos para usar.
    """

    # ── Identificación del Host ───────────────────────────────────────────────

    def _es_host(self):
        """
        Devuelve True si este cliente es el Host (creador de la sala).

        Criterios (en orden de prioridad):
          a) id_jugador == 1  (el primer jugador que se conecta siempre es el host)
          b) El nombre del jugador coincide con lista_elementos["nombre_creador"]
        """
        try:
            id_jugador = self.elementos_mesa.get("id_jugador")
            if id_jugador is not None and int(id_jugador) == 1:
                return True

            # Respaldo: comparar nombre
            nombre_creador = ""
            if self.un_juego and hasattr(self.un_juego, "lista_elementos"):
                nombre_creador = self.un_juego.lista_elementos.get("nombre_creador", "")

            datos_jugadores = self.elementos_mesa.get("datos_lista_jugadores") or []
            for dato in datos_jugadores:
                if isinstance(dato, dict):
                    if (dato.get("id") == id_jugador and
                            dato.get("nombre", "").strip().lower() ==
                            nombre_creador.strip().lower()):
                        return True
        except Exception as e:
            print(f"[CheatAdmin] Error en _es_host: {e}")
        return False

    # ── Construcción de la mano cheat ─────────────────────────────────────────

    def _construir_mano_cheat(self, ronda):
        """
        Convierte las tuplas de JUGADAS_PRECARGADAS[ronda] en objetos
        Cartas_interfaz con imagen asociada.

        Devuelve una lista de Cartas_interfaz o [] si la lista está vacía o
        la ronda no tiene jugada precargada.
        """
        try:
            tuplas = JUGADAS_PRECARGADAS.get(ronda, [])
            if not tuplas:
                print(f"[CheatAdmin] No hay jugada precargada para ronda {ronda}.")
                return []

            imagenes = getattr(self.un_juego, "_cartas_imagenes", None) or {}

            cartas_cheat = []
            for numero, figura in tuplas:
                # Clave de imagen: "Pica (A)", "Corazon (5)", "Especial (Joker)"
                if str(numero).lower() == "joker":
                    clave_img = "Especial (Joker)"
                else:
                    clave_img = f"{figura} ({numero})"

                ruta_img = None
                imagen_surf = imagenes.get(clave_img)

                # Cartas_interfaz necesita ruta_imagen; si no la tenemos usamos None
                # y asignamos la Surface directamente después de construir el objeto.
                try:
                    # Importar Cartas_interfaz dinámicamente para no generar
                    # dependencia circular a nivel de módulo
                    from logica_interfaz.cartas_interfaz import Cartas_interfaz as _CI
                except Exception:
                    # Si el import directo falla, usamos la referencia del módulo
                    _CI = Carta  # Carta fue importado en el módulo principal

                carta_obj = _CI(
                    numero,
                    figura,
                    un_juego=self.un_juego,
                    ruta_imagen=ruta_img,
                )
                # Asignar imagen de surface directamente
                if imagen_surf is not None:
                    carta_obj.parte_superior = imagen_surf

                cartas_cheat.append(carta_obj)

            print(f"[CheatAdmin] Mano cheat construida para ronda {ronda}: "
                  f"{[str(c) for c in cartas_cheat]}")
            return cartas_cheat

        except Exception as e:
            print(f"[CheatAdmin] Error en _construir_mano_cheat: {e}")
            return []

    # ── Acción del botón ──────────────────────────────────────────────────────

    def _accion_concluir_ronda(self):
        """
        Lógica ejecutada al hacer clic en "Concluir Ronda":

        1. Determina la ronda actual desde la conexión o desde un atributo
           propio de la mesa.
        2. Obtiene la mano precargada para esa ronda.
        3. Si la mano está vacía (no configurada) avisa y aborta.
        4. Envía al servidor el mensaje JSON:
              {"tipo": "concluir_ronda",
               "id_jugador": <id_host>,
               "ronda": <nro_ronda>,
               "cartas_cheat": [{"numero":..,"figura":..}, ...]}
           El servidor se encargará de reemplazar la mano del host, bajar las
           cartas a la mesa y notificar a todos los clientes.
        5. Muestra un cartel de confirmación en pantalla.
        """
        try:
            # ── 1. Verificar que sigue siendo el host ─────────────────────────
            if not self._es_host():
                print("[CheatAdmin] Solo el Host puede concluir la ronda.")
                return

            # ── 2. Obtener ronda actual ───────────────────────────────────────
            ronda_actual = 1
            try:
                # La instancia de conexion_Rummy (servidor) guarda self.ronda
                conn = self.instacia_conexion
                if conn and hasattr(conn, "ronda"):
                    ronda_actual = int(conn.ronda)
            except Exception:
                pass

            # Fallback: atributo propio de Mesa_interfaz si existe
            if hasattr(self, "_ronda_actual"):
                ronda_actual = int(self._ronda_actual)

            print(f"[CheatAdmin] Concluir ronda {ronda_actual} solicitado por Host.")

            # ── 3. Construir mano cheat ───────────────────────────────────────
            cartas_cheat = self._construir_mano_cheat(ronda_actual)
            if not cartas_cheat:
                # Aviso visual al host
                try:
                    if hasattr(self.un_juego, "cartel_alerta"):
                        self.un_juego.cartel_alerta.mostrar(
                            f"Ronda {ronda_actual}: no hay jugada precargada.\n"
                            "Configura JUGADAS_PRECARGADAS en mesa_interfaz.py"
                        )
                except Exception:
                    pass
                return

            # ── 4. Enviar mensaje al servidor ─────────────────────────────────
            id_jugador = self.elementos_mesa.get("id_jugador", 1)
            payload = {
                "tipo": "concluir_ronda",
                "id_jugador": id_jugador,
                "ronda": ronda_actual,
                "cartas_cheat": [
                    {"numero": str(c.numero), "figura": str(c.figura)}
                    for c in cartas_cheat
                ],
            }

            enviado = False
            try:
                conn = self.instacia_conexion
                if conn and hasattr(conn, "enviar_mensaje"):
                    import json as _json
                    conn.enviar_mensaje(_json.dumps(payload))
                    enviado = True
                    print(f"[CheatAdmin] Mensaje 'concluir_ronda' enviado al servidor.")
            except Exception as e:
                print(f"[CheatAdmin] Error enviando mensaje: {e}")

            # ── 5. Feedback visual para el Host ───────────────────────────────
            try:
                if hasattr(self.un_juego, "cartel_alerta"):
                    if enviado:
                        self.un_juego.cartel_alerta.mostrar(
                            f"[HOST] Ronda {ronda_actual} concluida.\n"
                            "Las cartas cheat han sido enviadas al servidor."
                        )
                    else:
                        # Sin conexión (prueba local): aplicar directamente
                        self._aplicar_mano_cheat_local(cartas_cheat, ronda_actual)
            except Exception as e:
                print(f"[CheatAdmin] Error mostrando feedback: {e}")

        except Exception as e:
            print(f"[CheatAdmin] Error en _accion_concluir_ronda: {e}")

    def _aplicar_mano_cheat_local(self, cartas_cheat, ronda_actual):
        """
        Fallback sin red: reemplaza la mano visual del host directamente.
        Útil para pruebas locales donde no hay servidor activo.
        """
        try:
            print(f"[CheatAdmin] Aplicando mano cheat LOCAL para ronda {ronda_actual}.")
            # Actualizar datos de mano en elementos_mesa
            self.elementos_mesa["datos_mano_jugador"] = [
                {"numero": str(c.numero), "figura": str(c.figura)}
                for c in cartas_cheat
            ]
            # Disparar evento Pygame para que controladores.py recargue la mesa
            import pygame as _pg
            from recursos_graficos import constantes as _cte
            evento = _pg.event.Event(_cte.EVENTO_CONCLUIR_RONDA, {
                "ronda": ronda_actual,
                "cartas_cheat": self.elementos_mesa["datos_mano_jugador"],
                "id_jugador": self.elementos_mesa.get("id_jugador", 1),
            })
            _pg.event.post(evento)
            print("[CheatAdmin] Evento EVENTO_CONCLUIR_RONDA disparado localmente.")
        except Exception as e:
            print(f"[CheatAdmin] Error en _aplicar_mano_cheat_local: {e}")

    # ── Creación del botón en la mesa ─────────────────────────────────────────

    def crear_boton_concluir_ronda(self, mesa_menu):
        """
        Crea el botón "Concluir Ronda" y lo añade a mesa_menu.botones.

        SOLO lo crea si este cliente es el Host; de lo contrario no hace nada,
        garantizando que el botón nunca aparezca en los clientes no-host.

        Parámetro
        ---------
        mesa_menu : Menu
            El objeto Menu que representa la mesa de juego (un_juego.mesa).

        Retorna
        -------
        Boton | None
            La instancia del botón creado, o None si no es el host.
        """
        try:
            if not self._es_host():
                print("[CheatAdmin] No es host → botón 'Concluir Ronda' NO creado.")
                return None

            # ── Posición: esquina superior derecha de la pantalla ─────────────
            # Se coloca encima del área de la mesa para no tapar cartas.
            ancho_btn   = int(constantes.ANCHO_VENTANA * 0.14)   # 14% del ancho
            alto_btn    = int(constantes.ALTO_VENTANA  * 0.055)  # 5.5% del alto
            margen_der  = int(constantes.ANCHO_VENTANA * 0.01)
            margen_top  = int(constantes.ALTO_VENTANA  * 0.01)
            x_btn       = constantes.ANCHO_VENTANA - ancho_btn - margen_der
            y_btn       = margen_top

            boton = Boton(
                un_juego     = self.un_juego,
                texto        = "Concluir Ronda",
                ancho        = ancho_btn,
                alto         = alto_btn,
                x            = x_btn,
                y            = y_btn,
                tamaño_fuente= constantes.F_PEQUENA,
                fuente       = constantes.FUENTE_ESTANDAR,
                # Fondo rojo llamativo
                color        = constantes.CHEAT_BOTON_FONDO,
                color_hover  = constantes.CHEAT_BOTON_HOVER,
                radio_borde  = constantes.REDONDEO_NORMAL,
                color_texto  = constantes.CHEAT_BOTON_TEXTO,
                color_borde  = constantes.CHEAT_BOTON_BORDE,
                color_borde_hover   = constantes.CHEAT_BOTON_BORDE,
                color_borde_clicado = constantes.CHEAT_BOTON_CLIC,
                grosor_borde = 3,
                accion       = self._accion_concluir_ronda,
                deshabilitado= False,
            )

            # Guardar referencia para poder habilitarlo/deshabilitarlo luego
            self._boton_concluir_ronda = boton

            # Añadir al menú de la mesa para que se dibuje y reciba eventos
            if mesa_menu and hasattr(mesa_menu, "botones"):
                mesa_menu.botones.append(boton)
                print(f"[CheatAdmin] Botón 'Concluir Ronda' creado en ({x_btn}, {y_btn}) "
                      f"tamaño {ancho_btn}x{alto_btn}.")
            else:
                print("[CheatAdmin] WARN: mesa_menu no tiene lista 'botones'.")

            return boton

        except Exception as e:
            print(f"[CheatAdmin] Error en crear_boton_concluir_ronda: {e}")
            return None

    # ── Visibilidad dinámica (opcional, llamada desde manejar_partida) ────────

    def actualizar_visibilidad_boton_cheat(self):
        """
        Re-evalúa si el botón debe ser visible.  Llama a este método desde
        manejar_partida() o desde el game-loop si quieres que el botón
        aparezca/desaparezca según el estado del turno.

        Por defecto el botón es siempre visible para el Host.
        Puedes añadir condiciones aquí, por ejemplo:
          - Solo visible en el turno del host
          - Solo visible si quedan cartas en la mano
        """
        btn = getattr(self, "_boton_concluir_ronda", None)
        if btn is None:
            return
        try:
            # El botón es siempre visible mientras la partida esté activa
            btn.visible = True
        except Exception as e:
            print(f"[CheatAdmin] Error actualizando visibilidad botón cheat: {e}")


# =============================================================================


class Mesa_interfaz(
    CheatAdminMixin,            # ← NUEVO: lógica Cheat/Admin
    OrdenamientoManoMixin,      # ordenamiento de mano del jugador
    PosicionamientoMixin,
    UtilidadesMixin,
    CargaDatosMixin,
    CargaVisualesMixin,
    TurnosMixin,
    BotonesMixin,
    MostrarMixin,
    CreacionMesaMixin,
    ActualizacionMixin,
    ProcesamientoMixin,
    ManoMixin,
    AccionesRedMixin,
    PuntosMixin,
    MenuOpcionesMixin,
    AlertasMixin,
    RondasMixin
):
    _cartas_imagenes = None  # cache estático

    def __init__(self, un_juego):
        # Inicialización de datos del juego interfaz-redes
        self.elementos_mesa = {
            "id_jugador": None,
            "jugador_mano": None,
            "cantidad_cartas_mazo": 0,
            "cantidad_cartas_quema": 0,
            "dato_carta_quema":None,
            "dato_carta_descarte": None,
            "datos_mano_jugador": [],
            "cantidad_manos_jugadores": [],
            "datos_lista_jugadores": [],
            "turno_robar": False,
            "jugada":[],
            "jugadas_jugadores":[],
            "nro_jugada":1,
        }

        # Objetos del juego
        self.carta_descarte = None
        self.lista_jugadores_objetos = []
        self._jugadores_dict = None  # Cache para búsqueda optimizada de jugadores
        self.mano = []
        self.mazo_quema = None
        self.carta_quema = None
        self.un_juego = un_juego
        self.instacia_conexion = None
        self.mesa = None
        self.jugadores = []
        self.jugadas_jugadores = {}
        self.jugada = []
        self.trio = []
        self.seguidilla = []

        # Estados del juego
        self.tu_turno = False
        self.turno_robar = False

        # Contador de puntos
        self.puntos_acumulados = 0
        self.puntos_ronda_actual = 0

        self.menu_opciones = None
        self.menu_puntuacion = None
        self.menus_activos = []  # Lista para menus activos de la mesa
        self.boton_menu_opciones = None

        # Elementos de interfaz
        self.botones_accion = {}
        self.accion_seleccionada = None

        # Estado del ordenamiento (instancia propia para no compartir con otras instancias)
        self._modo_orden = 'trios'
        self._boton_ordenar = None

        # ── Cheat/Admin ───────────────────────────────────────────────────────
        # Referencia al botón; se asigna en crear_boton_concluir_ronda()
        self._boton_concluir_ronda = None
        # Ronda actual (se puede actualizar externamente)
        self._ronda_actual = 1
        # ─────────────────────────────────────────────────────────────────────

        # Referencia de elementos surface mesa-ventana
        self.referencia_elementos = {
                    "elementos_mis_cartas":[],
                    "elemento_carta_descarte":None,
                    "elemento_mazo_quema":None,
                    "elemento_jugadores":[],
                    "reversos_por_jugador":[],
                    "contadores_mano_por_jugador":[],
                    "jugadas_por_jugador":[],
                    "elementos_jugadas_jugadores":[],
                    "elementos_mi_jugada":[],
                    "elemento_mazo":None,
                    "elemento_carta_quema":None,
                    "indicador_turno":None,
                    "contador_puntos":None
        }

        # Configuración de posiciones
        self._inicializar_configuracion_posiciones()

    # ===== INICIALIZACIÓN Y CONFIGURACIÓN =====
    def _inicializar_configuracion_posiciones(self):
        self.posiciones_por_cantidad = {
            2: [
                ("abajo", 0.50),
                ("arriba", 0.50),
            ],

            3: [
                ("abajo", 0.50),
                ("derecha", 0.75),
                ("izquierda", 0.75),
            ],

            4: [
                ("abajo", 0.50),
                ("derecha", 0.75),
                ("arriba", 0.50),
                ("izquierda", 0.75),
            ],

            5: [
                ("abajo", 0.50),
                ("arriba", 0.65),
                ("derecha", 0.75),
                ("arriba", 0.33),
                ("izquierda", 0.75),
            ],

            6: [
                ("abajo", 0.50),
                ("derecha", 0.95),
                ("derecha", 0.50),
                ("arriba", 0.50),
                ("izquierda", 0.50),
                ("izquierda", 0.95),
            ],

            7: [
                ("abajo", 0.50),
                ("derecha", 0.95),
                ("derecha", 0.50),
                ("arriba", 0.65),
                ("arriba", 0.33),
                ("izquierda", 0.50),
                ("izquierda", 0.95),
            ],

            8: [
                ("abajo", 0.50),
                ("derecha", 0.85),
                ("derecha", 0.50),
                ("arriba", 0.80),
                ("arriba", 0.20),
                ("izquierda", 0.50),
                ("izquierda", 0.85),
                ("arriba", 0.50),
            ],
        }

        self.permutaciones_por_jugador = {
            2: {
                1: [0, 1],
                2: [1, 0],
            },

            3: {
                1: [0, 1, 2],
                2: [2, 0, 1],
                3: [1, 2, 0],
            },

            4: {
                1: [0, 1, 2, 3],
                2: [3, 0, 1, 2],
                3: [2, 3, 0, 1],
                4: [1, 2, 3, 0],
            },

            5: {
                1: [0, 1, 2, 3, 4],
                2: [4, 0, 1, 2, 3],
                3: [3, 4, 0, 1, 2],
                4: [2, 3, 4, 0, 1],
                5: [1, 2, 3, 4, 0],
            },

            6: {
                1: [0, 1, 2, 3, 4, 5],
                2: [5, 0, 1, 2, 3, 4],
                3: [4, 5, 0, 1, 2, 3],
                4: [3, 4, 5, 0, 1, 2],
                5: [2, 3, 4, 5, 0, 1],
                6: [1, 2, 3, 4, 5, 0],
            },

            7: {
                1: [0, 1, 2, 3, 4, 5, 6],
                2: [6, 0, 1, 2, 3, 4, 5],
                3: [5, 6, 0, 1, 2, 3, 4],
                4: [4, 5, 6, 0, 1, 2, 3],
                5: [3, 4, 5, 6, 0, 1, 2],
                6: [2, 3, 4, 5, 6, 0, 1],
                7: [1, 2, 3, 4, 5, 6, 0],
            },
        }

    def dibujar_debug_posiciones_jugadores(self, cantidad = 7):
            ancho = constantes.ANCHO_VENTANA
            alto = constantes.ALTO_VENTANA

            posiciones = self.posiciones_por_cantidad[cantidad]

            for i, (lado, factor) in enumerate(posiciones):
                if lado == "abajo":
                    x = int(ancho * factor)
                    y = int(alto * 0.82)
                elif lado == "arriba":
                    x = int(ancho * factor)
                    y = int(alto * 0.08)
                elif lado == "derecha":
                    x = int(ancho * 0.88)
                    y = int(alto * factor)
                elif lado == "izquierda":
                    x = int(ancho * 0.08)
                    y = int(alto * factor)

                rect = pygame.Rect(x - 60, y - 35, 120, 70)

                pygame.draw.rect(self.un_juego.pantalla, (255, 255, 255), rect, 2)
                pygame.draw.circle(self.un_juego.pantalla, (255, 0, 0), (x, y), 6)

                fuente = pygame.font.SysFont(None, 28)
                texto = fuente.render(f"J{i+1} {lado} {factor}", True, (255, 255, 255))
                self.un_juego.pantalla.blit(texto, (x - 55, y - 10))     

