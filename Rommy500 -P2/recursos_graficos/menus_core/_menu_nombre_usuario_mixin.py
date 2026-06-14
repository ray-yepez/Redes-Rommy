"""Mixin para el menú de nombre de usuario"""

import pygame
from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta

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
        ancho_menu = 1200
        alto_menu = 900

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
        
        # Fondo personalizado SOLO para UNIRSE A LA SALA
        if not creador_sala:
            ruta_panel = importar_desde_carpeta(
                nombre_archivo="Imagenes/fondos/caja_servidor.png",
                nombre_carpeta="assets"
            )

            panel = pygame.image.load(ruta_panel).convert_alpha()
            # Tamaño deseado de la imagen
            ancho_panel = 800
            alto_panel = 600

            # Escalar la imagen
            panel = pygame.transform.smoothscale(panel, (ancho_panel, alto_panel))

            # Calcular posición centrada
            x_panel = (ancho_menu - ancho_panel) // 2 + 25
            y_panel = (alto_menu - alto_panel) // 2 - 100

            # Agregar imagen centrada
            menu_nombre_usuario.agregar_imagen(panel, (x_panel, y_panel), 1)

            self.crear_elementos_unirse(menu_nombre_usuario, ancho_menu, alto_menu)
        else:
            self.crear_elementos_usuario(menu_nombre_usuario, creador_sala)

        self.crear_elementos_control_usuario(menu_nombre_usuario, creador_sala)

        self.elementos_creados.append(menu_nombre_usuario)
        return menu_nombre_usuario

    def crear_elementos_unirse(self, menu_nombre_usuario, ancho_menu, alto_menu):
        """Diseño personalizado para UNIRSE A LA SALA con imagen caja_servidor."""

        # Borde izquierdo
        ruta_borde_izq = importar_desde_carpeta(
            nombre_archivo="Imagenes/botones/borde_1_izquierda.png",
            nombre_carpeta="assets"
        )

        img_borde_izq = pygame.image.load(ruta_borde_izq).convert_alpha()

        ancho_borde_izq = 180
        alto_borde_izq = 120

        img_borde_izq = pygame.transform.smoothscale(
            img_borde_izq,
            (ancho_borde_izq, alto_borde_izq)
        )

        x_borde_izq = 325
        y_borde_izq = 95

        menu_nombre_usuario.agregar_imagen(
            img_borde_izq,
            (x_borde_izq, y_borde_izq),
            1
        )


        # Borde derecho
        ruta_borde_der = importar_desde_carpeta(
            nombre_archivo="Imagenes/botones/borde_1_derecha.png",
            nombre_carpeta="assets"
        )

        img_borde_der = pygame.image.load(ruta_borde_der).convert_alpha()

        ancho_borde_der = 180
        alto_borde_der = 120

        img_borde_der = pygame.transform.smoothscale(
            img_borde_der,
            (ancho_borde_der, alto_borde_der)
        )

        x_borde_der = 745
        y_borde_der = 116

        menu_nombre_usuario.agregar_imagen(
            img_borde_der,
            (x_borde_der, y_borde_der),
            1
        )



        # Título dentro de la parte blanca de la imagen
        menu_nombre_usuario.crear_elemento(
            Clase=Elemento_texto,
            x=293,
            y=110,
            un_juego=self,
            texto="INGRESE SU NOMBRE",
            ancho=660,
            alto=120,
            tamaño_fuente=50,
            fuente=constantes.FUENTE_TITULO,
            color=None,
            radio_borde=0,
            color_texto=(187, 165, 113),
            color_borde=None,
            grosor_borde=0,
            alineacion="centro",
            alineacion_vertical="centro"
        )



        # Entrada de texto dentro de la zona roja
        menu_nombre_usuario.crear_elemento(
            Clase=EntradaTexto,
            x=335,
            y=315,
            un_juego=self,
            limite_caracteres=20,
            texto="nombre",
            ancho=660,
            alto=100,
            tamaño_fuente=55,
            fuente=constantes.FUENTE_ESTANDAR,
            color=None,
            radio_borde=0,
            color_texto=(255, 230, 230),
            color_borde=None,
            grosor_borde=0,
            grupo=[],
            permitir_espacios=False,
            permitir_numeros=False,
            permitir_especiales=False,
            cartel_alerta=self.cartel_alerta,
            alineacion="izquierda",
            alineacion_vertical="centro"
        )
    
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
                    tamaño_fuente=60,
                    fuente=constantes.FUENTE_TITULO,
                    color= None,
                    radio_borde= 0,
                    color_texto= (187, 165, 113), # Un color dorado que resalte sobre el fondo verde
                    color_borde= None,
                    grosor_borde= 0,
                )

                # Subrayado SOLO para los títulos
                if texto in ("DATOS DE LA PARTIDA Y USUARIO", "INGRESA TU NOMBRE", "NOMBRE DE LA SALA"):
                    ruta_subrayado = importar_desde_carpeta(
                        nombre_archivo="Imagenes/botones/subrayado_2.png",
                        nombre_carpeta="assets"
                    )

                    img_subrayado = pygame.image.load(ruta_subrayado).convert_alpha()

                    ancho_subrayado = int(ancho * 0.93)
                    alto_subrayado = 110

                    img_subrayado = pygame.transform.smoothscale(
                        img_subrayado,
                        (ancho_subrayado, alto_subrayado)
                    )

                    x_subrayado = x + (ancho - ancho_subrayado) // 2
                    y_subrayado = y + alto * 0.25

                    menu_nombre_usuario.imagenes.append(
                        (
                            img_subrayado,
                            (
                                menu_nombre_usuario.x + x_subrayado,
                                menu_nombre_usuario.y + y_subrayado
                            )
                        )
                    )

            elif clase == EntradaTexto:
                permitir_espacios = False
                permitir_numeros = False

                # Cargar imagen del bloque de texto
                ruta_bloque = importar_desde_carpeta(
                    nombre_archivo="Imagenes/botones/bloque_texto.png",
                    nombre_carpeta="assets"
                )

                img_bloque = pygame.image.load(ruta_bloque).convert_alpha()
                img_bloque = pygame.transform.smoothscale(img_bloque, (int(ancho), int(alto)))

                # Color blanco semitransparente (RGBA)
                color_linea = (255, 255, 255, 220)

                # Margen izquierdo y derecho
                margen_x = 40

                # Posición vertical de la línea (cerca de la parte inferior)
                y_linea = int(alto * 0.72)

                # Grosor de la línea
                grosor = 4

                # Dibujar línea horizontal principal
                pygame.draw.line(
                    img_bloque,
                    color_linea,
                    (margen_x, y_linea),
                    (int(ancho) - margen_x, y_linea),
                    grosor
                )

                # Insertar imagen detrás del input
                menu_nombre_usuario.imagenes.append(
                    (img_bloque, (menu_nombre_usuario.x + x, menu_nombre_usuario.y + y))
                )

                menu_nombre_usuario.crear_elemento(
                    Clase=clase,
                    x=x,
                    y=y,
                    un_juego=self,
                    limite_caracteres=20,
                    texto=texto,
                    ancho=ancho,
                    alto=alto,
                    tamaño_fuente=55,
                    fuente=constantes.FUENTE_ESTANDAR,
                    color=None,
                    radio_borde=0,
                    color_texto=constantes.COLOR_TEXTO_PRINCIPAL,
                    grupo=grupos_elementos_entrada,
                    permitir_espacios=permitir_espacios,
                    permitir_numeros=permitir_numeros,
                    permitir_especiales=False,
                    cartel_alerta=self.cartel_alerta
                )

                
    
    def crear_elementos_control_usuario(self, menu_nombre_usuario, creador_sala):
        """Crea botones VOLVER y CONFIRMAR con imágenes personalizadas y escala simétrica
        
        Args:
            menu_nombre_usuario: Instancia del menú
            creador_sala (bool): Determina las acciones de los botones
        """
        import pygame
        from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta
         
        
        if not creador_sala:
            mostrar = self.menu_inicio
            accion_confirmar = lambda: controladores.validar_y_unirse_sala(self, menu_nombre_usuario)
        else:
            mostrar = self.menu_Cantidad_Jugadores
            accion_confirmar = lambda: controladores.validar_y_crear_servidor(self, menu_nombre_usuario)

        # Configuración diferente para cada pantalla
        if creador_sala:
            # BOTONES DE CREAR SALA
            ALTO_FIJO_BOTONES = 88
            y_factor = 0.95

            datos_botones = [
                {
                    "texto": "VOLVER",
                    "archivo": "boton_volver.png",
                    "accion": lambda: controladores.Mostrar_seccion(self, mostrar),
                    "lado": 0.299
                },
                {
                    "texto": "CONFIRMAR",
                    "archivo": "boton_confirmar.png",
                    "accion": accion_confirmar,
                    "lado": 0.70
                }
            ]
        else:
            # BOTONES DE UNIRSE A SALA
            ALTO_FIJO_BOTONES = 88
            y_factor = 0.85

            datos_botones = [
                {
                    "texto": "VOLVER",
                    "archivo": "boton_volver.png",
                    "accion": lambda: controladores.Mostrar_seccion(self, mostrar),
                    "lado": 0.32
                },
                {
                    "texto": "CONFIRMAR",
                    "archivo": "boton_confirmar.png",
                    "accion": accion_confirmar,
                    "lado": 0.73
                }
            
            ]
        
        for datos in datos_botones:
            # 2. Crear el botón base (esqueleto)
            ancho_base = constantes.ELEMENTO_MEDIANO_ANCHO
            y_base = (constantes.ALTO_MENU_NOM_USUARIO - constantes.ELEMENTO_MEDIANO_ALTO) * y_factor
            x_relativa = (constantes.ANCHO_MENU_NOM_USUARIO - ancho_base) * datos["lado"]
            
            boton = menu_nombre_usuario.crear_elemento(
                x=x_relativa,
                y=y_base,
                funcion=True,
                ancho=ancho_base,
                alto=constantes.ELEMENTO_MEDIANO_ALTO,
                texto=datos["texto"],
                accion=datos["accion"],
                tp_color="s",
                tp_borde="n"
            )

            # 3. Cargar y aplicar la imagen escalada
            try:
                ruta_img = importar_desde_carpeta(
                    nombre_archivo=f"Imagenes/botones/{datos['archivo']}",
                    nombre_carpeta="assets"
                )
                img = pygame.image.load(ruta_img).convert_alpha()

                # Escalado proporcional basado en altura fija
                ancho_orig, alto_orig = img.get_size()
                factor_escala = ALTO_FIJO_BOTONES / alto_orig
                nuevo_ancho = int(ancho_orig * factor_escala)
                nuevo_alto = ALTO_FIJO_BOTONES

                img = pygame.transform.smoothscale(img, (nuevo_ancho, nuevo_alto))

                # Ajustar el área de detección (Rect) a la posición absoluta
                x_absoluto = menu_nombre_usuario.x + x_relativa - (nuevo_ancho - ancho_base) // 2
                y_absoluto = menu_nombre_usuario.y + y_base

                boton.ancho = nuevo_ancho
                boton.alto = nuevo_alto
                boton.rect = pygame.Rect(int(x_absoluto), int(y_absoluto), nuevo_ancho, nuevo_alto)

                # Asignar imagen y limpiar estilos
                boton.superficie_texto = img
                boton.rect_texto = img.get_rect(center=boton.rect.center)
                
                boton.color_actual = boton.color = boton.color_hover = boton.color_clicado = None
                boton.grosor_borde = 0
                boton.color_borde = None

            except Exception as e:
                print(f"Error cargando imagen para {datos['texto']} en menú usuario: {e}")