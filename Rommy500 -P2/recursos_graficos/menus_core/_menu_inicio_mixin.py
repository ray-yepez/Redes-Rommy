"""Mixin para el menú de inicio"""

from recursos_graficos import constantes
from recursos_graficos.menu import Menu
from redes_interfaz import controladores


class MenuInicioMixin:
    """Mixin con métodos para el menú principal de inicio"""
    
    def Menu_inicio(self):
        """Crea el menú principal con 4 botones y el logo
        
        Returns:
            Menu: Instancia del menú de inicio
        """
        x, y = self.centrar(constantes.ANCHO_MENU_I, constantes.ALTO_MENU_I)
        
        menu_inicio = Menu(
            un_juego=self,
            ancho=constantes.ANCHO_MENU_I,
            alto=constantes.ALTO_MENU_I,
            x=x,
            y=y,
            fondo_color=constantes.FONDO_VENTANA,  # Mismo color que ventana (invisible)
            borde_color=constantes.SIN_COLOR,
            grosor_borde=constantes.SIN_BORDE,
            redondeo=constantes.REDONDEO_PRONUNCIADO
        )
        
        self.crear_elementos_control_inicio(menu_inicio)
        
        # Agregar logo en esquina superior izquierda
        posicion_logo = (constantes.ANCHO_MENU_I * 0.05, constantes.ALTO_MENU_I * 0.1)
        menu_inicio.agregar_imagen(self.logo_rummy, posicion_logo, constantes.SCALA)
        
        self.elementos_creados.append(menu_inicio)
        return menu_inicio
    
    def crear_elementos_control_inicio(self, menu_inicio):
        """Crea los 4 botones principales del menú de inicio
        
        Botones: CREAR SALA, UNIRSE A LA SALA, COMO JUGAR, SALIR DEL JUEGO
        
        Args:
            menu_inicio: Instancia del menú donde agregar los botones
        """
        ancho = constantes.ELEMENTO_GRANDE_ANCHO
        alto = constantes.ELEMENTO_GRANDE_ALTO
        
        # Textos y acciones de los botones
        botones = (
            ("CREAR SALA", lambda: controladores.Mostrar_seccion(self, self.menu_Cantidad_Jugadores)),
            ("UNIRSE A LA SALA", lambda: controladores.mostrar_menu_nombre_usuario(self, False)),
            ("COMO JUGAR", lambda: controladores.Mostrar_seccion(self, self.menu_instrucciones)),
            ("SALIR DEL JUEGO", lambda: self.salir())
        )
        
        incrementar_y = 0
        for i, (texto, accion) in enumerate(botones):
            x = (constantes.ANCHO_MENU_I - ancho) * 0.9  # 90% hacia la derecha
            y = (constantes.ALTO_MENU_I - alto) * (0.17 + incrementar_y)
            
            menu_inicio.crear_elemento(
                x=x,
                y=y,
                funcion=True,
                ancho=ancho,
                alto=alto,
                texto=texto,
                accion=accion,
                tp_color="p",
                tp_borde="g"
            )
            incrementar_y += 0.25  # 25% de espacio entre botones
