"""Módulo interno para métodos auxiliares de búsqueda y utilidades"""

from recursos_graficos.elementos_de_interfaz_de_usuario import Boton
from logica_interfaz.core.controles_ui.botones import BotonTransparente
from recursos_graficos import constantes


class UtilidadesMixin:
    """Mixin con métodos auxiliares de búsqueda y utilidades"""
    
    def obtener_jugador_local(self):
        """Retorna el jugador local (evita duplicación)"""
        id_local = self.elementos_mesa.get("id_jugador")
        if id_local is None:
            return None
        # Optimización: usar diccionario si existe, sino búsqueda lineal
        if not hasattr(self, '_jugadores_dict') or self._jugadores_dict is None:
            self._jugadores_dict = {j.nro_jugador: j for j in self.lista_jugadores_objetos}
        return self._jugadores_dict.get(id_local)
    
    def jugador_esta_bajado(self, nro_jugador):
        """Determina (de forma robusta) si un jugador ya se ha bajado.
        """
        datos = self.elementos_mesa.get("jugadas_jugadores")
        if not datos:
            return False

        if isinstance(datos, dict):

            val = None
            if nro_jugador in datos:
                val = datos[nro_jugador]
            else:
                val = datos.get(str(nro_jugador))
            if val and isinstance(val, list) and len(val) > 0:
                return True
            return False

        if isinstance(datos, list):
            for item in datos:
                if isinstance(item, list):
                    for elem in item:
                        try:
                            if int(elem) == nro_jugador:
                                return True
                        except Exception:
                            pass
            return False

        return False

    def obtener_grupo_cartas(self):
        """Obtiene el grupo de las cartas existentes"""
        if self.referencia_elementos["elementos_mis_cartas"]:
            return self.referencia_elementos["elementos_mis_cartas"][-1].grupo
        return []
    
    def obtener_carta_logica_por_valor(self, valor_carta_visual):
        """Busca la carta lógica que coincide con el valor de la carta visual.
        Esto evita problemas cuando el usuario ha reorganizado las cartas visualmente."""
        for carta_logica in self.mano:
            if carta_logica.__str__() == valor_carta_visual:
                return carta_logica
        return None

    def crear_boton_generico(self, texto, x, y, ancho, alto, accion, deshabilitado=False):
        """Crea un botón con configuración estándar"""
        return Boton(
            un_juego=self.un_juego,
            texto=texto,
            ancho=ancho,
            alto=alto,
            x=x,
            y=y,
            tamaño_fuente=constantes.F_PEQUENA,
            fuente=constantes.FUENTE_ESTANDAR,
            color=constantes.ELEMENTO_FONDO_PRINCIPAL,
            radio_borde=constantes.REDONDEO_NORMAL,
            color_texto=constantes.COLOR_TEXTO_PRINCIPAL,
            color_borde=constantes.ELEMENTO_BORDE_PRINCIPAL,
            grosor_borde=constantes.BORDE_INTERMEDIO,
            color_borde_hover=constantes.ELEMENTO_HOVER_PRINCIPAL,
            color_borde_clicado=constantes.ELEMENTO_CLICADO_PRINCIPAL,
            grupo=[],
            valor=texto.lower().replace(" ", "_"),
            accion=accion,
            deshabilitado=deshabilitado
        )

    def crear_boton_transparente(self, texto, x, y, ancho, alto, accion, deshabilitado=False):
        """Crea un botón transparente (invisible) pero funcional"""
        return BotonTransparente(
            un_juego=self.un_juego,
            texto=texto,
            ancho=ancho,
            alto=alto,
            x=x,
            y=y,
            tamaño_fuente=constantes.F_PEQUENA,
            fuente=constantes.FUENTE_ESTANDAR,
            accion=accion,
            deshabilitado=deshabilitado
        )

    def configurar_posicion_jugador(self, jugador, direccion, alineacion, ancho_jugador, alto_jugador):
        """Configura la posición y orientación de un jugador"""
        x, y, fila_cartas = self.determinar_alineacion_jugador(direccion, ancho_jugador, alto_jugador, alineacion)
        
        jugador.x = x 
        jugador.y = y 
        jugador.ancho = ancho_jugador 
        jugador.alto = alto_jugador
        jugador.fila_cartas = fila_cartas 
        jugador.direccion = direccion 
        jugador.offset_cartas = 40 if jugador.nro_jugador == self.elementos_mesa["id_jugador"] else 20
        
        return jugador

