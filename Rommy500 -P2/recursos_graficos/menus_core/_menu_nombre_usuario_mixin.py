"""Mixin para el menú de nombre de usuario"""

from recursos_graficos import constantes
from recursos_graficos.menu import Menu
from recursos_graficos.elementos_de_interfaz_de_usuario import Elemento_texto, EntradaTexto
from redes_interfaz import controladores


class MenuNombreUsuarioMixin:
    """Mixin con métodos para el menú de ingreso de nombre de usuario y sala"""
    
    def Menu_nombre_usuario(self, creador_sala):
        """Crea el formulario para ingresar nombre de usuario (y datos de sala si es creador)
        
        Args:
            creador_sala (bool): True si es el creador de la sala, False si se está uniendo
            
        Returns:
            Menu: Instancia del menú de nombre de usuario
        """
        x_menu, y_menu = self.centrar(
            constantes.ANCHO_MENU_NOM_USUARIO,
            constantes.ALTO_MENU_NOM_USUARIO
        )
        
        menu_nombre_usuario = Menu(
            self,
            constantes.ANCHO_MENU_NOM_USUARIO,
            constantes.ALTO_MENU_NOM_USUARIO,
            x_menu,
            y_menu,
            constantes.ELEMENTO_FONDO_SECUNDARO,
            constantes.ELEMENTO_BORDE_SECUNDARIO,
            constantes.BORDE_PRONUNCIADO,
            constantes.REDONDEO_PRONUNCIADO
        )
        
        self.crear_elementos_usuario(menu_nombre_usuario, creador_sala)
        self.crear_elementos_control_usuario(menu_nombre_usuario, creador_sala)
        
        self.elementos_creados.append(menu_nombre_usuario)
        return menu_nombre_usuario
    
    def crear_elementos_usuario(self, menu_nombre_usuario, creador_sala):
        """Crea los campos de entrada dinámicamente según el modo
        
        Args:
            menu_nombre_usuario: Instancia del menú
            creador_sala (bool): Si es creador, muestra campos adicionales
        """
        textos = ("DATOS DE LA PARTIDA Y USUARIO", "INGRESA TU NOMBRE", "NOMBRE DE LA SALA", "nombre", "nombre sala")
        grupos_elementos_entrada = []
        posiciones_x = [0.06, 0.94]
        
        if not creador_sala:
            textos = ("INGRESA TU NOMBRE", "nombre")
            
        for i, texto in enumerate(textos):
            columna = (i - 1) % 2
            fila = (i - 1) // 2
            posicion_x = posiciones_x[columna]
            posicion_y = 0.35 + (0.23 * fila)
            clase = Elemento_texto if texto in (textos[0:3]) else EntradaTexto
            
            ancho = constantes.ELEMENTO_GRANDE_ANCHO * 1.05
            alto = constantes.ELEMENTO_MEDIANO_ALTO * 0.95

            if texto == textos[0]:
                posicion_x = 0.5
                posicion_y = 0.1
                ancho = constantes.ELEMENTO_GRANDE_ANCHO * 2
                
            if not creador_sala:
                clase = Elemento_texto if texto in (textos[0]) else EntradaTexto
                if texto == "INGRESA TU NOMBRE":
                    posicion_x, posicion_y = 0.5, 0.1
                    ancho = constantes.ELEMENTO_GRANDE_ANCHO * 1.7
                else:
                    posicion_x, posicion_y = 0.5, 0.5
                    ancho = constantes.ELEMENTO_GRANDE_ANCHO * 1.5

            x = (constantes.ANCHO_MENU_NOM_USUARIO - ancho) * posicion_x
            y = (constantes.ALTO_MENU_NOM_USUARIO - alto) * posicion_y
            
            if clase == Elemento_texto:
                menu_nombre_usuario.crear_elemento(
                    Clase=clase,
                    x=x,
                    y=y,
                    un_juego=self,
                    texto=texto,
                    ancho=ancho,
                    alto=alto,
                    tamaño_fuente=constantes.F_GRANDE,
                    fuente=constantes.FUENTE_ESTANDAR,
                    color=constantes.ELEMENTO_FONDO_PRINCIPAL,
                    radio_borde=constantes.REDONDEO_NORMAL,
                    color_texto=constantes.COLOR_TEXTO_PRINCIPAL,
                    color_borde=constantes.ELEMENTO_BORDE_SECUNDARIO,
                    grosor_borde=constantes.BORDE_INTERMEDIO
                )
            elif clase == EntradaTexto:
                permitir_espacios = False
                permitir_numeros = False
                menu_nombre_usuario.crear_elemento(
                    Clase=clase,
                    x=x,
                    y=y,
                    un_juego=self,
                    limite_caracteres=20,
                    texto=texto,
                    ancho=ancho,
                    alto=alto,
                    tamaño_fuente=constantes.F_MEDIANA,
                    fuente=constantes.FUENTE_ESTANDAR,
                    color=constantes.ELEMENTO_FONDO_PRINCIPAL,
                    radio_borde=constantes.REDONDEO_NORMAL,
                    color_texto=constantes.COLOR_TEXTO_PRINCIPAL,
                    grupo=grupos_elementos_entrada,
                    permitir_espacios=permitir_espacios,
                    permitir_numeros=permitir_numeros,
                    permitir_especiales=False,
                    cartel_alerta=self.cartel_alerta
                )
    
    def crear_elementos_control_usuario(self, menu_nombre_usuario, creador_sala):
        """Crea botones VOLVER y CONFIRMAR con comportamiento según el modo
        
        Args:
            menu_nombre_usuario: Instancia del menú
            creador_sala (bool): Determina las acciones de los botones
        """
        texto_botones = ("VOLVER", "CONFIRMAR")
        
        if not creador_sala:
            mostrar = self.menu_inicio
            unirse_servidor = lambda: (controladores.validar_y_unirse_sala(self, menu_nombre_usuario))
            accion_confirmar = unirse_servidor
        else:
            mostrar = self.menu_Cantidad_Jugadores
            crear_sevidor = lambda: (controladores.validar_y_crear_servidor(self, menu_nombre_usuario))
            accion_confirmar = crear_sevidor

        accion_por_boton = (lambda: controladores.Mostrar_seccion(self, mostrar), accion_confirmar)
        incrementar_x = 0
        
        for i, texto_boton in enumerate(texto_botones):
            x = (constantes.ANCHO_MENU_NOM_USUARIO - constantes.ELEMENTO_MEDIANO_ANCHO) * (0.25 + incrementar_x)
            y = (constantes.ALTO_MENU_NOM_USUARIO - constantes.ELEMENTO_MEDIANO_ALTO) * (0.85)
            ancho = constantes.ELEMENTO_MEDIANO_ANCHO
            alto = constantes.ELEMENTO_MEDIANO_ALTO
            
            menu_nombre_usuario.crear_elemento(
                x=x,
                y=y,
                funcion=True,
                ancho=ancho,
                alto=alto,
                texto=texto_boton,
                accion=accion_por_boton[i],
                tp_color="s",
                tp_borde="g"
            )
            incrementar_x = 0.55
