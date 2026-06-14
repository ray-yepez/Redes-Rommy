"""
ordenamiento_mano.py
====================
Mixin de ordenamiento de mano para Mesa_interfaz.

DÓNDE COPIAR ESTE ARCHIVO:
    logica_interfaz/core/controles_ui/ordenamiento_mano.py
"""

from itertools import groupby


class OrdenamientoManoMixin:
    """
    Agrega ordenamiento de mano al jugador local.

    Modos:
        'trios'       → agrupa números iguales juntos.  Jokers al final.
        'seguidillas' → agrupa por palo, valor ascendente. Jokers al final.

    El botón alterna entre modos con cada click mostrando
    "Ord: Tríos" o "Ord: Runs" según el modo activo.
    """

    _modo_orden: str = 'trios'
    _boton_ordenar = None

    # ═══════════════════════════════════════════════════════════════════════════
    # API PÚBLICA
    # ═══════════════════════════════════════════════════════════════════════════

    def ordenar_mano(self, modo: str = None) -> None:
        """
        Ordena self.mano y sincroniza los elementos visuales.

        Args:
            modo: 'trios', 'seguidillas', o None para alternar automáticamente.
        """
        if modo is None:
            self._modo_orden = (
                'seguidillas' if self._modo_orden == 'trios' else 'trios'
            )
        else:
            self._modo_orden = modo

        if not self.mano:
            self._actualizar_texto_boton_orden()
            return

        elementos = self.referencia_elementos.get("elementos_mis_cartas", [])

        if elementos and len(elementos) == len(self.mano):
            self._ordenar_con_visuales(elementos)
        else:
            self.mano.sort(key=self._clave_carta)

        self._actualizar_texto_boton_orden()
#cambio lismar
    def crear_boton_ordenar(self, mesa) -> None:
        """Crea el botón de ordenamiento con imagen toggle."""
        import pygame
        from recursos_graficos.elementos_de_interfaz_de_usuario import Boton
        from recursos_graficos import constantes

        # =========================
        # TAMAÑO DEL BOTÓN
        # =========================
        ancho = 190
        alto = 98

        # =========================
        # POSICIÓN DEL BOTÓN
        # =========================
        x = int(constantes.ANCHO_VENTANA * 0.17)
        y = int(constantes.ALTO_VENTANA * 0.86)

        def _accion_ordenar():
            self.ordenar_mano()

        boton = Boton(
            self.un_juego,
            " ",
            ancho,
            alto,
            x,
            y,
            constantes.F_PEQUENA,
            constantes.FUENTE_ESTANDAR,
            color=None,
            radio_borde=0,
            color_texto=(255, 255, 255),
            color_borde=None,
            grosor_borde=0,
            color_hover=None,
            color_borde_hover=None,
            color_borde_clicado=None,
            accion=_accion_ordenar,
            deshabilitado=False,
        )

        # Asegurar rect y dimensiones
        boton.rect = pygame.Rect(x, y, ancho, alto)
        boton.x = x
        boton.y = y
        boton.ancho = ancho
        boton.alto = alto

        self._boton_ordenar = boton
        mesa.botones.append(boton)

        print("CREANDO BOTON ORDENAR EN:", x, y, ancho, alto)

        self._actualizar_imagen_boton_orden()
        
    def _clave_carta(self, carta) -> tuple:
        """
        Clave de comparación según el modo activo.
        Jokers siempre al final (es_joker=True → 1 > 0).
        """
        es_joker = str(carta.numero).strip().lower() == 'joker'
        valor    = carta.valor_numerico()
        figura   = str(carta.figura).strip().lower()

        if self._modo_orden == 'trios':
            return (int(es_joker), valor, figura)
        else:
            return (int(es_joker), figura, valor)

    def _ordenar_con_visuales(self, elementos: list) -> None:
        """
        Ordena self.mano y BotonRadioImagenes simultáneamente con zip+sort.

        1. Empareja carta <-> elemento por índice con zip().
        2. Ordena los pares con la clave de la carta.
        3. Escribe de vuelta en las listas originales (in-place).
        4. Actualiza .grupo interno de cada BotonRadioImagenes.
        5. Invalida caché de ranuras → posiciones X se recalculan.
        6. Recalcula .prioridad para superposición visual correcta.
        7. Sincroniza con mesa.botones si el Menu existe.
        """
        # 1 y 2 – emparejar y ordenar
        pares = list(zip(self.mano, elementos))
        pares.sort(key=lambda p: self._clave_carta(p[0]))

        # 3 – escribir de vuelta in-place
        cartas_ord, elementos_ord = zip(*pares)
        self.mano[:]   = list(cartas_ord)
        elementos[:]   = list(elementos_ord)
        self.referencia_elementos["elementos_mis_cartas"] = list(elementos_ord)

        grupo_nuevo = list(elementos_ord)

        # 4 – actualizar grupo interno
        for elemento in grupo_nuevo:
            elemento.grupo[:] = grupo_nuevo

        # 5 – invalidar caché de ranuras y recalcular posiciones
        if grupo_nuevo:
            grupo_nuevo[0].invalidar_ranuras_grupo()
            grupo_nuevo[0].asegurar_ranuras_grupo()

        # 6 – recalcular prioridades de superposición
        for i, elemento in enumerate(grupo_nuevo):
            elemento.prioridad = i

        # 7 – sincronizar con mesa.botones
        if hasattr(self, 'mesa') and self.mesa is not None:
            botones_mesa = getattr(self.mesa, 'botones', [])
            for el in grupo_nuevo:
                if el not in botones_mesa:
                    botones_mesa.append(el)

    def _actualizar_texto_boton_orden(self) -> None:
        """Mantiene compatibilidad, pero ahora actualiza imagen."""
        self._actualizar_imagen_boton_orden()

    def _actualizar_imagen_boton_orden(self) -> None:
        """Cambia la imagen del botón según el modo actual."""
        if self._boton_ordenar is None:
            return

        import pygame
        from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta

        archivo = "boton_trio.png" if self._modo_orden == "trios" else "boton_runs.png"

        try:
            ruta_img = importar_desde_carpeta(
                nombre_archivo=f"Imagenes/botones/{archivo}",
                nombre_carpeta="assets"
            )

            img = pygame.image.load(ruta_img).convert_alpha()

            ancho = self._boton_ordenar.ancho
            alto = self._boton_ordenar.alto

            img = pygame.transform.smoothscale(img, (ancho, alto))

            self._boton_ordenar.superficie_texto = img
            self._boton_ordenar.rect_texto = img.get_rect(
            center=self._boton_ordenar.rect.center
            )

            self._boton_ordenar.texto = " "

            self._boton_ordenar.color_actual = None
            self._boton_ordenar.color = None
            self._boton_ordenar.color_hover = None
            self._boton_ordenar.color_clicado = None
            self._boton_ordenar.grosor_borde = 0
            self._boton_ordenar.color_borde = None
            self._boton_ordenar.color_borde_actual = None

        except Exception as e:
            print(f"Error actualizando imagen del botón ordenar: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # UTILIDADES DE DEBUG
    # ═══════════════════════════════════════════════════════════════════════════

    def grupos_por_valor(self) -> dict:
        """Devuelve {valor_numerico: [cartas]} usando itertools.groupby."""
        mano_ord = sorted(self.mano, key=lambda c: c.valor_numerico())
        return {k: list(v) for k, v in groupby(mano_ord, key=lambda c: c.valor_numerico())}

    def grupos_por_figura(self) -> dict:
        """Devuelve {figura: [cartas]} usando itertools.groupby."""
        mano_ord = sorted(self.mano, key=lambda c: str(c.figura).lower())
        return {k: list(v) for k, v in groupby(mano_ord, key=lambda c: str(c.figura).lower())}