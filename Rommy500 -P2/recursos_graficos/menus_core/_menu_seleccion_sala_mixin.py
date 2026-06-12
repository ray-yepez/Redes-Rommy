"""Mixin para el menú de selección de salas"""

from recursos_graficos import constantes
from recursos_graficos.menu import Menu
from recursos_graficos.elementos_de_interfaz_de_usuario import Elemento_texto, BotonRadio, Boton
from redes_interfaz import controladores


class MenuSeleccionSalaMixin:
    """Mixin con métodos para el menú de selección de salas disponibles"""
    
    def Menu_seleccion_sala(self):
        """Crea el menú para mostrar y seleccionar salas disponibles en la red
        
        Returns:
            Menu: Instancia del menú de selección de salas
        """
        x_menu, y_menu = self.centrar(
            constantes.ANCHO_MENU_SELECCION_SALA,
            constantes.ALTO_MENU_SELECCION_SALA
        )
    
        menu_seleccion_sala = Menu(
            self,
            constantes.ANCHO_MENU_SELECCION_SALA,
            constantes.ALTO_MENU_SELECCION_SALA,
            x_menu,
            y_menu,
            constantes.ELEMENTO_FONDO_SECUNDARO,
            constantes.ELEMENTO_BORDE_SECUNDARIO,
            constantes.BORDE_PRONUNCIADO,
            constantes.REDONDEO_PRONUNCIADO
        )
    
        # Título del menú
        menu_seleccion_sala.crear_elemento(
            Clase=Elemento_texto,
            x=(constantes.ANCHO_MENU_SELECCION_SALA - constantes.ELEMENTO_GRANDE_ANCHO * 1.5) * 0.5,
            y=(constantes.ALTO_MENU_SELECCION_SALA - constantes.ELEMENTO_MEDIANO_ALTO) * 0.05,
            un_juego=self,
            texto="ELIJA LA SALA",
            ancho=constantes.ELEMENTO_GRANDE_ANCHO * 1.5,
            alto=constantes.ELEMENTO_MEDIANO_ALTO,
            tamaño_fuente=constantes.F_GRANDE,
            fuente=constantes.FUENTE_LLAMATIVA,
            color=constantes.ELEMENTO_FONDO_PRINCIPAL,
            radio_borde=constantes.REDONDEO_NORMAL,
            color_texto=constantes.COLOR_TEXTO_PRINCIPAL,
            color_borde=constantes.ELEMENTO_BORDE_SECUNDARIO,
            grosor_borde=constantes.BORDE_INTERMEDIO,
        )
    
        # Obtener salas disponibles
        salas_disponibles = self.lista_elementos["salas_disponibles"]
    
        # Si no hay salas disponibles, mostrar mensaje
        if not salas_disponibles:
            menu_seleccion_sala.crear_elemento(
                Clase=Elemento_texto,
                x=(constantes.ANCHO_MENU_SELECCION_SALA - constantes.ELEMENTO_GRANDE_ANCHO) * 0.5,
                y=(constantes.ALTO_MENU_SELECCION_SALA - constantes.ELEMENTO_MEDIANO_ALTO) * 0.5,
                un_juego=self,
                texto="No hay salas disponibles\nVuelva a intentar más tarde",
                ancho=constantes.ELEMENTO_GRANDE_ANCHO,
                alto=constantes.ELEMENTO_MEDIANO_ALTO,
                tamaño_fuente=constantes.F_MEDIANA,
                fuente=constantes.FUENTE_ESTANDAR,
                color=constantes.ELEMENTO_FONDO_PRINCIPAL,
                radio_borde=constantes.REDONDEO_NORMAL,
                color_texto=constantes.COLOR_TEXTO_PRINCIPAL,
                color_borde=constantes.ELEMENTO_BORDE_SECUNDARIO,
                grosor_borde=constantes.BORDE_INTERMEDIO,
            )
        else:
            # Crear botones para cada sala
            self.crear_botones_salas(menu_seleccion_sala, salas_disponibles)
    
        # Agregar botones de control
        self.agregar_botones_control_salas(menu_seleccion_sala)
    
        self.elementos_creados.append(menu_seleccion_sala)
        return menu_seleccion_sala
    
    def crear_botones_salas(self, menu, salas):
        """Crea un radio button por cada sala disponible en grid de 3 columnas
        
        Args:
            menu: Instancia del menú
            salas: Lista de diccionarios con información de cada sala
        """
        grupo_salas = []
        columnas = 3
        espaciado_x = constantes.ANCHO_MENU_SELECCION_SALA * 0.05
        espaciado_y = constantes.ALTO_MENU_SELECCION_SALA * 0.05
    
        ancho_boton = (constantes.ELEMENTO_PEQUENO_ANCHO)
        alto_boton = constantes.ELEMENTO_PEQUENO_ALTO * 0.95

        for i, sala in enumerate(salas):
            fila = i // columnas
            columna = i % columnas
        
            x_pos = espaciado_x + columna * (ancho_boton + espaciado_x)
            y_pos = constantes.ALTO_MENU_SELECCION_SALA * 0.22 + fila * (alto_boton + espaciado_y)
        
            # Verificar si la sala está llena
            sala_llena = sala["jugadores"] >= sala["max_jugadores"]
        
            texto_sala = f"{sala['nombre']}/{sala['jugadores']}/{sala['max_jugadores']}"
            
            menu.crear_elemento(
                Clase=Boton,
                x=x_pos,
                y=y_pos,
                un_juego=self,
                texto=texto_sala,
                ancho=ancho_boton,
                alto=alto_boton,
                tamaño_fuente=constantes.F_MEDIANA,
                fuente=constantes.FUENTE_ESTANDAR,
                color=constantes.ELEMENTO_FONDO_PRINCIPAL,
                radio_borde=constantes.REDONDEO_NORMAL,
                color_texto=constantes.COLOR_TEXTO_PRINCIPAL,
                color_borde=constantes.ELEMENTO_BORDE_SECUNDARIO,
                grosor_borde=constantes.BORDE_LIGERO,
                color_borde_hover=constantes.ELEMENTO_HOVER_PRINCIPAL,
                color_borde_clicado=constantes.ELEMENTO_CLICADO_PRINCIPAL,
                deshabilitado=sala_llena,
                accion= lambda: controladores.Unirse_a_sala_seleccionada(self, sala)
            )
            grupo_salas.append(menu.botones[-1])
    
    def agregar_botones_control_salas(self, menu):
        """Agrega botones VOLVER y ACTUALIZAR al menú
        
        Args:
            menu: Instancia del menú
        """
        y = (constantes.ALTO_MENU_SELECCION_SALA - constantes.ELEMENTO_MEDIANO_ALTO) * 0.9
        x = (constantes.ANCHO_MENU_SELECCION_SALA - constantes.ELEMENTO_PEQUENO_ANCHO)
        elementos_textos = ("VOLVER", "ACTUALIZAR")
        funciones = (
            lambda: controladores.Mostrar_seccion(self, self.menu_nombre_usuario),
            lambda: self.actualizar_lista_salas()
        )

        incremento_x = 0.3
        for i, texto in enumerate(elementos_textos):
            ancho = constantes.ELEMENTO_PEQUENO_ANCHO
            alto = constantes.ELEMENTO_MEDIANO_ALTO
            menu.crear_elemento(
                x=x * incremento_x,
                y=y,
                funcion=True,
                ancho=ancho,
                alto=alto,
                texto=texto,
                accion=funciones[i],
                tp_color="s",
                tp_borde="g"
            )
            incremento_x += 0.45

    def actualizar_lista_salas(self):
        """Refresca la lista de salas disponibles recreando el menú"""
        print("Actualizando lista de salas...")
        # Remover el menú actual
        if hasattr(self, "menu_seleccion_sala") and self.menu_seleccion_sala in self.elementos_creados:
            self.elementos_creados.remove(self.menu_seleccion_sala)
    
        # Crear nuevo menú con salas actualizadas
        self.menu_seleccion_sala = self.Menu_seleccion_sala()
        controladores.Mostrar_seccion(self, self.menu_seleccion_sala)
