from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta
import pygame

Mazo = importar_desde_carpeta("mazo.py", "Mazo")
Menu = importar_desde_carpeta("menu.py", "Menu", "recursos_graficos")

CartelAlerta = importar_desde_carpeta(
    nombre_archivo="elementos_de_interfaz_de_usuario.py",
    nombre_clase="CartelAlerta",
    nombre_carpeta="recursos_graficos",
)
BotonRadioImagenes = importar_desde_carpeta(
    nombre_archivo="elementos_de_interfaz_de_usuario.py",
    nombre_clase="BotonRadioImagenes",
    nombre_carpeta="recursos_graficos",
)
constantes = importar_desde_carpeta(
    nombre_archivo="constantes.py",
    nombre_carpeta="recursos_graficos",
)


class Mazo_interfaz():
    def __init__(self, cantidad_cartas, x, y, scala, accion, un_juego=None):
        self.un_juego     = un_juego
        self.cantidad_cartas = cantidad_cartas
        self.mazo_al_100  = self.un_juego._mazo_imagenes["mazo(1)"]
        self.mazo_al_50   = self.un_juego._mazo_imagenes["mazo(2)"]
        self.mazo_al_25   = self.un_juego._mazo_imagenes["mazo(3)"]
        self.mazo_al_5    = self.un_juego._mazo_imagenes["mazo(4)"]
        self.mazo_al_0    = self.un_juego._mazo_imagenes["mazo(5)"]
        self.x     = x
        self.y     = y
        self.scala = scala
        self.imagen = None
        self.prepar_imagen()
        self.elemento_mazo = None
        self.Elemento_mazo()

    # ── Imagen según cantidad de cartas ───────────────────────────────────

    def prepar_imagen(self):
        if self.cantidad_cartas >= 54:
            self.imagen = self.mazo_al_100
        elif 27 <= self.cantidad_cartas < 54:
            self.imagen = self.mazo_al_50
        elif 10 <= self.cantidad_cartas < 27:
            self.imagen = self.mazo_al_25
        elif 0 < self.cantidad_cartas < 10:
            self.imagen = self.mazo_al_5
        else:
            self.imagen = self.mazo_al_0

    # ── Elemento visual del mazo ──────────────────────────────────────────

    def Elemento_mazo(self):
        accion = lambda x: print(".")
        self.elemento_mazo = BotonRadioImagenes(
            un_juego=self.un_juego,
            imagen=self.imagen,
            scala=self.scala,
            x=self.x,
            y=self.y,
            radio_borde=5,
            color_borde=constantes.ELEMENTO_FONDO_TERCIARIO,
            color_borde_hover=constantes.ELEMENTO_FONDO_TERCIARIO,
            color_borde_clicado=constantes.ELEMENTO_FONDO_TERCIARIO,
            grupo=None,
            valor=None,
            deshabilitado=False,
            accion=accion,
            lift_offset=0
        )

    def Actualizar_mazo(self):
        self.prepar_imagen()
        self.elemento_mazo.scala  = 0.05
        self.elemento_mazo.imagen = self.imagen

    def retornar_datos(self):
        return {
            "un_juego":        self.un_juego,
            "cantidad_cartas": self.cantidad_cartas,
            "x":               self.x,
            "y":               self.y,
            "scala":           self.scala,
            "imagen":          self.imagen,
        }

    # ══════════════════════════════════════════════════════════════════════
    # NUEVO: callback visual para repartir_cartas / repartir_para_red
    # ══════════════════════════════════════════════════════════════════════

    @staticmethod
    def actualizar_visual_mano(idx_jugador, mano, un_juego):
        """
        Callback que se pasa a Mazo.repartir_cartas() para reposicionar
        visualmente las cartas del jugador LOCAL en pantalla tras la repartición.

        Solo actúa sobre la mano que corresponde al jugador local
        (identificado por mesa_juego.elementos_mesa["id_jugador"]).
        Las demás manos se ignoran porque no se renderizan en la vista propia.

        Distribución horizontal:
        • Las cartas se reparten en el 80 % central del ancho de pantalla.
        • Si no caben sin solaparse, se aplica solapamiento mínimo automático.
        • Se actualiza x, y, y_base y rect de cada BotonRadioImagenes.
        • Se invalida la caché de ranuras para que el sistema de arrastre
          recalcule posiciones en el siguiente frame.

        Uso:
            manos = mazo.repartir_cartas(
                jugadores_reordenados,
                actualizar_visual=Mazo_interfaz.actualizar_visual_mano,
                un_juego=un_juego
            )

        Args:
            idx_jugador (int): Índice del jugador en la lista repartida (0-based).
            mano (list):       Lista de objetos Carta asignados a ese jugador.
            un_juego:          Instancia Ventana / Mesa con acceso a mesa_juego.
        """
        try:
            mesa = getattr(un_juego, "mesa_juego", None)
            if mesa is None:
                return

            # Solo actualizar la mano del jugador local
            id_local = getattr(mesa, "elementos_mesa", {}).get("id_jugador")
            if id_local is not None and (idx_jugador + 1) != id_local:
                return

            # ── Parámetros de posicionamiento ─────────────────────────────
            ancho_ventana = constantes.ANCHO_VENTANA
            alto_ventana  = constantes.ALTO_VENTANA
            scala_carta   = constantes.ESCALA_CARTAS      # escala estándar

            # Franja inferior donde se muestra la mano del jugador local
            y_base = int(alto_ventana * 0.82)

            # Ancho visual de una carta escalada (usamos imagen de referencia)
            ref_img = None
            cartas_imgs = getattr(un_juego, "_cartas_imagenes", None)
            if cartas_imgs:
                ref_img = next(iter(cartas_imgs.values()), None)
            ancho_carta = int(ref_img.get_width() * scala_carta) if ref_img else 80

            total_cartas = len(mano)
            if total_cartas == 0:
                return

            # Espacio disponible: 80 % del ancho de pantalla centrado
            espacio_disponible = int(ancho_ventana * 0.80)
            x_inicio           = int(ancho_ventana * 0.10)

            # Espaciado entre cartas (puede ser negativo → solapamiento)
            if total_cartas == 1:
                espaciado = 0
            else:
                espaciado = min(
                    ancho_carta + 4,
                    (espacio_disponible - ancho_carta) // (total_cartas - 1)
                )

            # ── Actualizar coordenadas en los elementos visuales ──────────
            elementos_mano = mesa.referencia_elementos.get("elementos_mis_cartas", [])

            for k, elemento in enumerate(elementos_mano):
                if k >= total_cartas:
                    break
                nuevo_x = x_inicio + k * espaciado
                elemento.x      = nuevo_x
                elemento.y      = y_base
                elemento.y_base = y_base
                elemento.rect.x = nuevo_x
                elemento.rect.y = y_base

                # Invalidar caché de ranuras para forzar recálculo al arrastrar
                try:
                    elemento.invalidar_ranuras_grupo()
                except Exception:
                    pass

            print(
                f"[Mazo_interfaz] Mano visual actualizada — "
                f"{total_cartas} cartas, x_inicio={x_inicio}, espaciado={espaciado}."
            )

        except Exception as e:
            print(f"[Mazo_interfaz] Error en actualizar_visual_mano: {e}")
