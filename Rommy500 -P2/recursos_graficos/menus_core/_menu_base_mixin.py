"""Mixin base con métodos comunes para todos los menús"""

from recursos_graficos import constantes
from recursos_graficos.elementos_de_interfaz_de_usuario import Boton


class MenuBaseMixin:
    """Mixin con métodos compartidos por todos los menús"""
    
    def centrar(self, ancho_elemento, alto_elemento):
        """Calcula posición (x, y) para centrar un elemento en la ventana
        
        Args:
            ancho_elemento: Ancho del elemento a centrar
            alto_elemento: Alto del elemento a centrar
            
        Returns:
            tuple: (x, y) posición centrada
        """
        x = (constantes.ANCHO_VENTANA - ancho_elemento) / 2
        y = (constantes.ALTO_VENTANA - alto_elemento) / 2
        return (x, y)
    
    def boton_generico(self, x=0, y=0, ancho=0, alto=0, texto="", accion=None, tp_color="p", tp_borde="g"):
        """Factory method para crear botones con estilo consistente
        
        Args:
            x, y: Posición del botón
            ancho, alto: Dimensiones del botón
            texto: Texto a mostrar
            accion: Función a ejecutar al hacer click
            tp_color: Tipo de color ("p" = principal, "s" = secundario)
            tp_borde: Tipo de borde ("i" = intermedio, "g" = grueso, "p" = pequeño)
            
        Returns:
            Boton: Instancia del botón configurado
        """
        # Mapeo de tipo de borde
        if tp_borde == "i":
            borde = constantes.BORDE_INTERMEDIO
        elif tp_borde == "g":
            borde = constantes.BORDE_PRONUNCIADO
        elif tp_borde == "p":
            borde = constantes.BORDE_LIGERO
        else:
            borde = constantes.BORDE_PRONUNCIADO
            
        # Mapeo de color de borde
        if tp_color == "p":
            color_borde = constantes.ELEMENTO_BORDE_PRINCIPAL
        elif tp_color == "s":
            color_borde = constantes.ELEMENTO_BORDE_SECUNDARIO
        else:
            color_borde = constantes.ELEMENTO_BORDE_PRINCIPAL
            
        return Boton(
            un_juego=self,
            texto=texto,
            ancho=ancho,
            alto=alto,
            x=x,
            y=y,
            tamaño_fuente=constantes.F_MEDIANA,
            fuente=constantes.FUENTE_LLAMATIVA,
            color=constantes.ELEMENTO_FONDO_PRINCIPAL,
            radio_borde=constantes.REDONDEO_NORMAL,
            color_texto=constantes.COLOR_TEXTO_PRINCIPAL,
            color_borde=color_borde,
            grosor_borde=borde,
            color_borde_hover=constantes.ELEMENTO_HOVER_PRINCIPAL,
            color_borde_clicado=constantes.ELEMENTO_CLICADO_PRINCIPAL,
            accion=accion
        )
