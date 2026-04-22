"""Mixin para el menú de instrucciones"""

from recursos_graficos import constantes
from recursos_graficos.menu import Menu
from recursos_graficos.elementos_de_interfaz_de_usuario import Elemento_texto
from redes_interfaz import controladores


class MenuInstruccionesMixin:
    """Mixin con métodos para el menú de instrucciones (Cómo Jugar)"""
    
    def Menu_instrucciones(self):
        """Crea el menú que explica las reglas del Rummy 500
        
        Returns:
            Menu: Instancia del menú de instrucciones
        """
        x_menu, y_menu = self.centrar(
            constantes.ANCHO_MENU_INSTRUCCIONES,
            constantes.ALTO_MENU_INSTRUCCIONES
        )
        
        menu_instrucciones = Menu(
            un_juego=self,
            ancho=constantes.ANCHO_MENU_INSTRUCCIONES,
            alto=constantes.ALTO_MENU_INSTRUCCIONES,
            x=x_menu,
            y=y_menu,
            fondo_color=constantes.ELEMENTO_FONDO_PRINCIPAL,
            borde_color=constantes.ELEMENTO_BORDE_PRINCIPAL,
            grosor_borde=constantes.BORDE_PRONUNCIADO,
            redondeo=constantes.REDONDEO_PRONUNCIADO
        )
        
        self.crear_elementos_instrucciones(menu_instrucciones)
        self.crear_elementos_control_instrucciones(menu_instrucciones)
        
        self.elementos_creados.append(menu_instrucciones)
        return menu_instrucciones
    
    def crear_elementos_instrucciones(self, menu_instrucciones):
        """Agrega el texto de instrucciones al menú
        
        Args:
            menu_instrucciones: Instancia del menú donde agregar los elementos
        """
        # Texto ocupa casi todo el ancho y 70% de la altura
        menu_instrucciones.crear_elemento(
            Clase=Elemento_texto,
            x=constantes.BORDE_PRONUNCIADO,
            y=constantes.ALTO_MENU_INSTRUCCIONES * 0.10,
            un_juego=self,
            texto=constantes.TEXTO_DE_INSTRUCCIONES,
            ancho=constantes.ANCHO_MENU_INSTRUCCIONES - (constantes.BORDE_PRONUNCIADO * 2),
            alto=constantes.ALTO_MENU_INSTRUCCIONES * 0.70,
            tamaño_fuente=constantes.F_MEDIANA,
            fuente=constantes.FUENTE_ESTANDAR,
            color=constantes.ELEMENTO_FONDO_PRINCIPAL,
            radio_borde=constantes.REDONDEO_INTERMEDIO,
            color_texto=constantes.COLOR_TEXTO_PRINCIPAL,
            color_borde=constantes.BLANCO,
            grosor_borde=constantes.BORDE_LIGERO,
            alineacion_vertical="arriba",
            alineacion="izquierda"
        )
    
    def crear_elementos_control_instrucciones(self, menu_instrucciones,solo_ocultar=False):
        """Crea el botón VOLVER al final del menú de instrucciones
        
        Args:
            menu_instrucciones: Instancia del menú donde agregar los controles
        """
        x = (constantes.ANCHO_MENU_INSTRUCCIONES - constantes.ELEMENTO_PEQUENO_ANCHO) / 2
        y = constantes.ALTO_MENU_INSTRUCCIONES - constantes.ELEMENTO_PEQUENO_ALTO * 1.2
        ancho = constantes.ELEMENTO_PEQUENO_ANCHO
        alto = constantes.ELEMENTO_PEQUENO_ALTO
        accion = lambda: controladores.Mostrar_seccion(self, self.menu_inicio,solo_ocultar=solo_ocultar)
        
        
        menu_instrucciones.crear_elemento(
            x=x,
            y=y,
            funcion=True,
            ancho=ancho,
            alto=alto,
            texto="VOLVER",
            accion=accion,
            tp_color="p",
            tp_borde="i"
        )
