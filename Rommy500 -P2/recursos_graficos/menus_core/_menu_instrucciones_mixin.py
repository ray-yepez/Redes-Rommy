import pygame
from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta

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
            fondo_color=None,
            borde_color=None,
            grosor_borde=constantes.BORDE_PRONUNCIADO,
            redondeo=constantes.REDONDEO_PRONUNCIADO
        )

        ruta_fondo = importar_desde_carpeta(
            nombre_archivo="Imagenes/fondos/panel_como_jugar.png",
            nombre_carpeta="assets"
        )

        fondo_instrucciones = pygame.image.load(ruta_fondo).convert_alpha()

        fondo_instrucciones = pygame.transform.smoothscale(
            fondo_instrucciones,
            (constantes.ANCHO_MENU_INSTRUCCIONES, constantes.ALTO_MENU_INSTRUCCIONES)
        )

        menu_instrucciones.agregar_imagen(
            fondo_instrucciones,
            (0, 0),1
        )
        
        self.crear_elementos_instrucciones(menu_instrucciones)
        self.crear_elementos_control_instrucciones(menu_instrucciones)
        
        self.elementos_creados.append(menu_instrucciones)
        return menu_instrucciones
    #cambio lismar
    def crear_elementos_instrucciones(self, menu_instrucciones):
        """Agrega el texto de instrucciones al menú con márgenes ajustados"""
        
        margen_x = constantes.ANCHO_MENU_INSTRUCCIONES * 0.10
        ancho_texto = constantes.ANCHO_MENU_INSTRUCCIONES * 0.80
        
        menu_instrucciones.crear_elemento(
            Clase=Elemento_texto,
            x=margen_x,
            y=constantes.ALTO_MENU_INSTRUCCIONES * 0.15,
            un_juego=self,
            texto=constantes.TEXTO_DE_INSTRUCCIONES,
            ancho=ancho_texto,
            alto=constantes.ALTO_MENU_INSTRUCCIONES * 0.65, 
            tamaño_fuente=constantes.F_MEDIANA,  # <── Regresamos a la fuente mediana original
            fuente=constantes.FUENTE_ESTANDAR,
            color=None,
            radio_borde=constantes.REDONDEO_INTERMEDIO,
            color_texto=(187, 165, 113),
            color_borde=constantes.BLANCO,
            grosor_borde=0,
            alineacion_vertical="arriba",
            alineacion="izquierda"
        )
    
    #cambio lismar
    def crear_elementos_control_instrucciones(self, menu_instrucciones,solo_ocultar=False):
        """Crea el botón VOLVER al final del menú de instrucciones, centrado"""
        import pygame
        from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta
        
        accion = lambda: controladores.Mostrar_seccion(self, self.menu_inicio,solo_ocultar=solo_ocultar)

        # 1. Cargar imagen y calcular escala ANTES de crear el botón
        try:
            ruta_img = importar_desde_carpeta(
                nombre_archivo="Imagenes/botones/boton_volver.png",
                nombre_carpeta="assets"
            )
            img = pygame.image.load(ruta_img).convert_alpha()
            escala = 0.35  # Tamaño reducido para que no estorbe
            nuevo_ancho = int(img.get_width() * escala)
            nuevo_alto = int(img.get_height() * escala)
            img = pygame.transform.smoothscale(img, (nuevo_ancho, nuevo_alto))
        except Exception as e:
            print(f"Error cargando imagen VOLVER: {e}")
            nuevo_ancho = 150
            nuevo_alto = 50
            img = None

        # 2. Calcular la posición centrada
        x_relativo = (constantes.ANCHO_MENU_INSTRUCCIONES - nuevo_ancho) / 2
        y_relativo = constantes.ALTO_MENU_INSTRUCCIONES * 0.82 # 82% hacia abajo

        # 3. Crear el botón con las medidas y posiciones reales
        boton_volver = menu_instrucciones.crear_elemento(
            x=x_relativo,
            y=y_relativo,
            funcion=True,
            ancho=nuevo_ancho,
            alto=nuevo_alto,
            texto="VOLVER",
            accion=accion,
            tp_color="s",
            tp_borde="n"
        )

        # 4. Asignarle la imagen si se cargó correctamente y limpiar los bordes
        if img:
            x_absoluto = menu_instrucciones.x + x_relativo
            y_absoluto = menu_instrucciones.y + y_relativo

            boton_volver.x = int(x_absoluto)
            boton_volver.y = int(y_absoluto)
            boton_volver.ancho = nuevo_ancho
            boton_volver.alto = nuevo_alto

            boton_volver.rect = pygame.Rect(
                int(x_absoluto), int(y_absoluto), nuevo_ancho, nuevo_alto
            )

            boton_volver.superficie_texto = img
            boton_volver.rect_texto = img.get_rect(center=boton_volver.rect.center)

            # Quitar fondos blancos
            boton_volver.color_actual = None
            boton_volver.color = None
            boton_volver.color_hover = None
            boton_volver.color_clicado = None
            boton_volver.grosor_borde = 0
            boton_volver.color_borde = None
            boton_volver.color_borde_actual = None
            boton_volver.color_borde_hover = None
            boton_volver.color_borde_clicado = None