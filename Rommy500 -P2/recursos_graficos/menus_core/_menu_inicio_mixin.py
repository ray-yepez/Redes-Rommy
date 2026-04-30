import pygame
from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta
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
            fondo_color= None,  # Mismo color que ventana (invisible)
            borde_color=constantes.SIN_COLOR,
            grosor_borde=constantes.SIN_BORDE,
            redondeo=constantes.REDONDEO_PRONUNCIADO
        )
        
        self.crear_elementos_control_inicio(menu_inicio)
        
        # Agregar logo
        escala_logo = 0.7 
        x_centro = (constantes.ANCHO_MENU_I - self.logo_rummy.get_width()) // 2
        posicion_logo = (
            x_centro - 100,
            int(constantes.ALTO_MENU_I * 0.10)
        )
        
        menu_inicio.agregar_imagen(self.logo_rummy, posicion_logo, escala_logo)
        
        self.elementos_creados.append(menu_inicio)
        return menu_inicio
    
    def crear_elementos_control_inicio(self, menu_inicio):
        """Crea los 4 botones principales del menú de inicio
        
        Botones: CREAR SALA, UNIRSE A LA SALA, COMO JUGAR, SALIR DEL JUEGO
        
        Args:
            menu_inicio: Instancia del menú donde agregar los botones
        """
        factor_escala = 0.85 
        ancho = int(constantes.ELEMENTO_GRANDE_ANCHO * factor_escala)
        alto = int(constantes.ELEMENTO_GRANDE_ALTO * factor_escala)
        
        # Textos y acciones de los botones
        botones = (
            ("CREAR SALA", lambda: controladores.Mostrar_seccion(self, self.menu_Cantidad_Jugadores)),
            ("UNIRSE A LA SALA", lambda: controladores.mostrar_menu_nombre_usuario(self, False)),
            ("COMO JUGAR", lambda: controladores.Mostrar_seccion(self, self.menu_instrucciones)),
            ("SALIR DEL JUEGO", lambda: self.salir())
        )

         # 👇 AQUÍ VA
        imagenes_botones = {
            "CREAR SALA": "Imagenes/botones/b_crear_sala.png",
            "UNIRSE A LA SALA": "Imagenes/botones/b_unirse_sala.png",
            "COMO JUGAR": "Imagenes/botones/b_como_jugar.png",
            "SALIR DEL JUEGO": "Imagenes/botones/b_salir_juego.png"
        }
        
        espacio = 150  # separación entre botones
        y_inicial = 60  # sube o baja todo el grupo
        for i, (texto, accion) in enumerate(botones):
            x = (constantes.ANCHO_MENU_I - ancho) * 0.9
            y = y_inicial + (i *espacio)

            ruta_imagen = imagenes_botones.get(texto)

            boton = menu_inicio.crear_elemento(
                x=x,
                y=y,
                funcion=True,
                ancho=ancho,
                alto=alto,
                texto=" " if ruta_imagen else texto,
                accion=accion,
                tp_color="s" if ruta_imagen else "p",
                tp_borde="n" if ruta_imagen else "g"
            )

            if ruta_imagen:
                try:
                    ruta_img = importar_desde_carpeta(
                        nombre_archivo=ruta_imagen,
                        nombre_carpeta="assets"
                    )

                    img = pygame.image.load(ruta_img).convert_alpha()

                    proporcion = img.get_width() / img.get_height()
                    nuevo_ancho = ancho
                    nuevo_alto = int(nuevo_ancho / proporcion)

                    img = pygame.transform.smoothscale(img, (nuevo_ancho, nuevo_alto))

                    x_absoluto = menu_inicio.x + x
                    y_absoluto = menu_inicio.y + y

                    boton.x = int(x_absoluto)
                    boton.y = int(y_absoluto)
                    boton.ancho = nuevo_ancho
                    boton.alto = nuevo_alto

                    boton.rect = pygame.Rect(
                        int(x_absoluto),
                        int(y_absoluto),
                        nuevo_ancho,
                        nuevo_alto
                    )

                    boton.superficie_texto = img
                    boton.rect_texto = img.get_rect(center=boton.rect.center)

                    boton.color_actual = None
                    boton.color = None
                    boton.color_hover = None
                    boton.color_clicado = None
                    boton.grosor_borde = 0
                    boton.color_borde_actual = None

                    boton.grosor_borde = 0
                    boton.color_borde = None
                    boton.color_borde_actual = None
                    boton.color_borde_hover = None
                    boton.color_borde_clicado = None

                    # Muy importante: recalcular hover con el rect nuevo
                    boton.esta_hover = False

                except Exception as e:
                    print(f"Error cargando imagen del botón {texto}: {e}")
