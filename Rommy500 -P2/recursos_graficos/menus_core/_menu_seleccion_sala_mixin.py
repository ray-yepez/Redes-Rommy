"""Mixin para el menú de selección de salas"""
import pygame
from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta

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
            tamaño_fuente=60,
            fuente=constantes.FUENTE_TITULO,
            color= None, # Para que el fondo del texto sea transparente y se vea el fondo del menú
            radio_borde= 0,
            color_texto=(187, 165, 113), # Un color dorado que resalte sobre el fondo verde,
            color_borde=None,
            grosor_borde= 0,
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
                tamaño_fuente=45,
                fuente=constantes.FUENTE_TITULO,
                color= None, # Para que el fondo del texto sea transparente y se vea el fondo del menú
                radio_borde= 0,
                color_texto=(187, 165, 113), # Un color dorado que resalte sobre el fondo verde
                color_borde= None,
                grosor_borde= 0,
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
        """Agrega botones VOLVER y ACTUALIZAR con imágenes al menú, asegurando igual tamaño
        
        Args:
            menu: Instancia del menú
        """
        # 1. Definir un alto fijo para ambos botones en píxeles
        # Prueba con 120 para ver cuál se ajusta mejor a tu diseño
        ALTO_FIJO_BOTONES = 120 

        # Configuración de posiciones relativas
        y_relativa = (constantes.ALTO_MENU_SELECCION_SALA - constantes.ELEMENTO_MEDIANO_ALTO) * 0.9
        x_base = (constantes.ANCHO_MENU_SELECCION_SALA - constantes.ELEMENTO_PEQUENO_ANCHO)
        
        datos_botones = [
            {
                "texto": "VOLVER",
                "archivo": "boton_volver.png",
                "accion": lambda: controladores.Mostrar_seccion(self, self.menu_nombre_usuario),
                "x_inc": 0.3
            },
            {
                "texto": "ACTUALIZAR",
                "archivo": "b_unirse_sala.png", # Este es el que se veía diferente
                "accion": lambda: self.actualizar_lista_salas(),
                "x_inc": 0.75
            }
        ]

        for datos in datos_botones:
            # 2. Crear el botón base
            x_relativa = x_base * datos["x_inc"]
            boton = menu.crear_elemento(
                x=x_relativa,
                y=y_relativa,
                funcion=True,
                ancho=constantes.ELEMENTO_PEQUENO_ANCHO,
                alto=constantes.ELEMENTO_MEDIANO_ALTO,
                texto=datos["texto"],
                accion=datos["accion"],
                tp_color="s",
                tp_borde="n"
            )

            # 3. Cargar y escalar la imagen a una altura fija
            try:
                ruta_img = importar_desde_carpeta(
                    nombre_archivo=f"Imagenes/botones/{datos['archivo']}",
                    nombre_carpeta="assets"
                )

                img = pygame.image.load(ruta_img).convert_alpha()

                # --- NUEVA LÓGICA DE ESCALADO ---
                # 1. Obtener dimensiones originales
                ancho_orig = img.get_width()
                alto_orig = img.get_height()
                
                # 2. Calcular factor de escala basado solo en la altura
                factor_escala_y = ALTO_FIJO_BOTONES / alto_orig
                
                # 3. Calcular nuevo ancho manteniendo la proporción original
                nuevo_ancho = int(ancho_orig * factor_escala_y)
                nuevo_alto = ALTO_FIJO_BOTONES

                # 4. Escalar la imagen a las nuevas dimensiones precisas
                img = pygame.transform.smoothscale(img, (nuevo_ancho, nuevo_alto))

                # Posicionamiento absoluto
                x_absoluto = menu.x + x_relativa
                y_absoluto = menu.y + y_relativa

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

                # Asignar imagen
                boton.superficie_texto = img
                boton.rect_texto = img.get_rect(center=boton.rect.center)

                # Quitar estilos genéricos
                boton.color_actual = None
                boton.color = None
                boton.color_hover = None
                boton.color_clicado = None
                boton.grosor_borde = 0
                boton.color_borde = None
                boton.color_borde_actual = None

            except Exception as e:
                print(f"Error cargando imagen {datos['archivo']}: {e}")

    def actualizar_lista_salas(self):
        """Refresca la lista de salas disponibles recreando el menú"""
        print("Actualizando lista de salas...")
        # Remover el menú actual
        if hasattr(self, "menu_seleccion_sala") and self.menu_seleccion_sala in self.elementos_creados:
            self.elementos_creados.remove(self.menu_seleccion_sala)
    
        # Crear nuevo menú con salas actualizadas
        self.menu_seleccion_sala = self.Menu_seleccion_sala()
        controladores.Mostrar_seccion(self, self.menu_seleccion_sala)
