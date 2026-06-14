"""Módulo interno para sistema de menú de opciones"""
import pygame
from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta
from recursos_graficos import constantes
from recursos_graficos.elementos_de_interfaz_de_usuario import Boton
from redes_interfaz import controladores

Menu = importar_desde_carpeta("menu.py","Menu","recursos_graficos")
BotonLogoMenu = importar_desde_carpeta("elementos_de_interfaz_de_usuario.py","BotonLogoMenu","recursos_graficos")


class MenuOpcionesMixin:
    """Mixin con métodos para sistema de menú de opciones"""
    #cambio lismar
    def crear_boton_menu(self):
        """Crea el botón de menú anclado a Tus Puntos, centrado, y MÁS GRANDE"""
        import pygame
        from recursos_graficos import constantes
        from recursos_graficos.elementos_de_interfaz_de_usuario import BotonLogoMenu
        
        # 1. Aumentamos el tamaño fijo para que sea mucho más visible y cómodo
        ancho_boton = 115  # Antes era 90
        alto_boton = 100    # Antes era 70
        
        # 2. Buscamos a "Tus Puntos" para usarlo de referencia posicional
        boton_puntos = self.referencia_elementos.get("contador_puntos")
        
        if boton_puntos:
            # Posición X: A la derecha de "Tus Puntos" con 15 px de separación
            x = boton_puntos.x + boton_puntos.ancho + 15
            
            # Posición Y: Alineamos los CENTROS para que se vean parejos
            centro_y_puntos = boton_puntos.y + (boton_puntos.alto // 2)
            y = int(centro_y_puntos - (alto_boton // 2))
        else:
            x = constantes.ANCHO_MENU_MESA - ancho_boton - 20
            y = 10
            
        # Cargar la imagen del menú
        ruta_menu = importar_desde_carpeta(
            nombre_archivo="Imagenes/botones/menu.png",
            nombre_carpeta="assets"
        )

        imagen_aux = pygame.image.load(ruta_menu).convert_alpha()
        
        # Escalar la imagen aprovechando el nuevo tamaño gigante
        rect_img = imagen_aux.get_rect()
        margen = 4 
        factor_escala = min((ancho_boton - margen) / rect_img.width, (alto_boton - margen) / rect_img.height)
        
        nuevo_ancho = int(rect_img.width * factor_escala)
        nuevo_alto = int(rect_img.height * factor_escala)
        
        imagen_final = pygame.transform.smoothscale(imagen_aux, (nuevo_ancho, nuevo_alto))

        boton = BotonLogoMenu(
            un_juego=self.un_juego,
            x=x, y=y,
            ancho=ancho_boton, 
            alto=alto_boton,
            radio_borde=constantes.REDONDEO_NORMAL,
            color_rayas=(0, 0, 0),
            color_rayas_hover=constantes.ELEMENTO_BORDE_CUATERNARIO,
            color_rayas_clicado=constantes.ELEMENTO_CLICADO_PRINCIPAL,
            deshabilitado=False,
            accion=lambda: self.mostrar_menu_opciones(),
        )
        
        # Forzamos los colores Vinotinto y Dorado
        boton.color = (128, 0, 32)
        boton.color_actual = (128, 0, 32)
        boton.color_borde = (218, 165, 32)
        boton.color_borde_actual = (218, 165, 32)
        
        boton.imagen_menu = imagen_final
        
        return boton
    
    
    def mostrar_menu_opciones(self):
        """Muestra el menú de opciones"""
        print("DEBUG: Mostrando menú de opciones")
        
        if self.menu_opciones is None:
            self.crear_menu_opciones()
        
        if self.menu_opciones:
            self.un_juego.mesa_opciones.mostrar()
            # self.menus_activos.append(self.menu_opciones)
            print(f"DEBUG: Menú agregado a menus_activos. Total: {len(self.menus_activos)}")

    def crear_menu_opciones(self):
        """Crea el menú de opciones"""
        

        ancho_menu = constantes.ANCHO_VENTANA * 0.6
        alto_menu = constantes.ALTO_VENTANA * 0.8

        x, y = self.un_juego.centrar(ancho_menu, alto_menu)

        self.menu_opciones = Menu(
            self.un_juego,
            ancho_menu,
            alto_menu,
            x,
            y,
            None,
            constantes.SIN_COLOR,
            constantes.SIN_BORDE,
            0
        )

        try:
            ruta_fondo = importar_desde_carpeta(
                nombre_archivo="Imagenes/fondos/fondo_pausa.png",
                nombre_carpeta="assets"
            )

            imagen_aux = pygame.image.load(ruta_fondo).convert_alpha()
            fondo_personalizado = pygame.transform.smoothscale(
                imagen_aux,
                (int(ancho_menu), int(alto_menu))
            )

            self.menu_opciones.agregar_imagen(fondo_personalizado, (0, 0), 1)

        except Exception as e:
            print(f"Error cargando la imagen de fondo: {e}")

        self.crear_botones_menu_opciones()

        try:
            self.crear_controles_volumen()
        except Exception as e:
            print(f"Error cargando controles de volumen: {e}")

        self.un_juego.mesa_opciones = self.menu_opciones
        self.un_juego.mesa_opciones.mostrar()

        print(f"DEBUG: Menú de opciones creado con {len(self.menu_opciones.botones)} botones")

    def crear_botones_menu_opciones(self):
        """Crea los botones del menú de opciones"""
        ancho_boton = self.menu_opciones.ancho * 0.6
        alto_boton = constantes.ELEMENTO_PEQUENO_ALTO * 0.8
        espacio = 20
        
        x_base = (self.menu_opciones.x + ancho_boton) * 0.575
        y_base = self.menu_opciones.y + (self.menu_opciones.alto * 0.30) #cambio lismar 
        
        
        opciones = [
            ("REANUDAR", self.reanudar_juego),
            ("CÓMO SE JUEGA", self.mostrar_instrucciones),
            ("SALIR DE LA PARTIDA", self.salir_partida)
        ]
        
        for i, (texto, accion) in enumerate(opciones):
            y_pos = y_base + (i * (alto_boton + espacio))
            
            boton = Boton(
                un_juego=self.un_juego,
                texto=texto,
                ancho=ancho_boton,
                alto=alto_boton,
                x=x_base,
                y=y_pos,
                tamaño_fuente=24,
                fuente=constantes.FUENTE_ESTANDAR,
                color=constantes.ELEMENTO_FONDO_PRINCIPAL,
                radio_borde=constantes.REDONDEO_NORMAL,
                color_texto=(218, 165, 32),
                color_borde=constantes.ELEMENTO_BORDE_SECUNDARIO,
                grosor_borde=constantes.BORDE_INTERMEDIO,
                color_borde_hover=constantes.ELEMENTO_HOVER_PRINCIPAL,
                color_borde_clicado=constantes.ELEMENTO_CLICADO_PRINCIPAL,
                grupo=[],
                valor=texto.lower().replace(" ", "_"),
                accion=accion,
                ruta_imagen_fondo="Imagenes/botones/boton_base.png"
            )
            
            self.menu_opciones.botones.append(boton)

    def ajustar_volumen(self, cantidad):
        """Sube o baja el volumen de la música entre 0.0 y 1.0"""
        juego = self.un_juego
        vol_actual = getattr(juego, 'master_volume', 1.0)
        
        # Sumar o restar y evitar que se pase de 1.0 (100%) o baje de 0.0 (0%)
        nuevo_vol = max(0.0, min(1.0, vol_actual + cantidad))
        juego.master_volume = nuevo_vol
        
        # Aplicar el volumen real al mixer de Pygame
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(nuevo_vol)
        except Exception as e:
            print(f"Error de audio: {e}")
            
        # Actualizar el porcentaje en el texto visual
        if hasattr(self, 'texto_volumen'):
            porcentaje = int(nuevo_vol * 100)
            self.texto_volumen.texto = f"Vol: {porcentaje}%"
            self.texto_volumen.prepar_texto()

    def crear_controles_volumen(self):
        """Crea los botones de [+] y [-] con bordes dorados y desplazados a la derecha"""
        from recursos_graficos.elementos_de_interfaz_de_usuario import Boton, Elemento_texto
        from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta
        import pygame
        
        ancho_icono = 35
        ancho_btn = 40
        alto_btn = 40
        ancho_texto = 130
        
        # Colores
        color_vino_tinto = (128, 0, 32) 
        color_dorado = (218, 165, 32)
        
        centro_x_menu = self.menu_opciones.x + (self.menu_opciones.ancho // 2)
        
        # Le sumamos + 20 al final para rodar todo el bloque hacia la derecha
        x_base = int(centro_x_menu - (270 // 2))
        y = int(self.menu_opciones.y + (self.menu_opciones.alto * 0.18))
        
        # 1. Ícono de volumen
        icono = Boton(
            un_juego=self.un_juego, texto="",
            ancho=ancho_icono, alto=ancho_icono, x=x_base, y=y + 2,
            tamaño_fuente=10, fuente=constantes.FUENTE_ESTANDAR,
            color=None, radio_borde=0, color_texto=(0,0,0),
            color_borde=None, grosor_borde=0, deshabilitado=True
        )
        try:
            ruta_img = importar_desde_carpeta(nombre_archivo="Imagenes/Logos/Mute.png", nombre_carpeta="assets")
            img = pygame.image.load(ruta_img).convert_alpha()
            img = pygame.transform.smoothscale(img, (ancho_icono, ancho_icono))
            icono.superficie_texto = img
            icono.rect_texto = img.get_rect(center=icono.rect.center)
            icono.color_actual = None 
        except Exception as e:
            print(f"No se pudo cargar el icono de volumen: {e}")

        # 2. Botón Menos (-)
        boton_menos = Boton(
            un_juego=self.un_juego, texto="-",
            ancho=ancho_btn, alto=alto_btn, x=x_base + 45, y=y,
            tamaño_fuente=34, fuente=constantes.FUENTE_ESTANDAR,
            color=color_vino_tinto, radio_borde=10, 
            color_texto=color_dorado,
            color_borde=color_dorado, grosor_borde=2,  # <── Borde Dorado
            color_borde_hover=constantes.ELEMENTO_HOVER_PRINCIPAL,
            color_borde_clicado=constantes.ELEMENTO_CLICADO_PRINCIPAL,
            accion=lambda: self.ajustar_volumen(-0.1)
        )
        
        # 3. Texto indicador de porcentaje
        vol_actual = getattr(self.un_juego, 'master_volume', 1.0)
        self.texto_volumen = Elemento_texto(
            un_juego=self.un_juego, texto=f"Vol: {int(vol_actual * 100)}%",
            ancho=ancho_texto, alto=alto_btn, x=x_base + 90, y=y,
            tamaño_fuente=24, fuente=constantes.FUENTE_ESTANDAR,
            color=None, radio_borde=0, color_texto=color_dorado,
            color_borde=None, grosor_borde=0
        )
        
        # 4. Botón Más (+)
        boton_mas = Boton(
            un_juego=self.un_juego, texto="+",
            ancho=ancho_btn, alto=alto_btn, x=x_base + 230, y=y,
            tamaño_fuente=30, fuente=constantes.FUENTE_ESTANDAR,
            color=color_vino_tinto, radio_borde=10, 
            color_texto=color_dorado,
            color_borde=color_dorado, grosor_borde=2,  # <── Borde Dorado
            color_borde_hover=constantes.ELEMENTO_HOVER_PRINCIPAL,
            color_borde_clicado=constantes.ELEMENTO_CLICADO_PRINCIPAL,
            accion=lambda: self.ajustar_volumen(0.1)
        )
        
        # Inyectar los 4 elementos
        self.menu_opciones.botones.extend([icono, boton_menos, self.texto_volumen, boton_mas])
        
    def reanudar_juego(self):
        """Cierra el menú de opciones"""
        print("DEBUG: Reanudar juego")
        self.un_juego.mesa_opciones.ocultar()

    def mostrar_instrucciones(self):
        """Muestra las instrucciones del juego"""
        print("DEBUG: Mostrar instrucciones")
        if hasattr(self.un_juego, 'mesa_opciones'):
            self.un_juego.mesa_opciones.ocultar()
        
        # Mostrar el menú de instrucciones
        if hasattr(self.un_juego, 'menu_instrucciones'):
            for elemento in self.un_juego.menu_instrucciones.botones:
                if elemento.texto == "VOLVER":
                    elemento.accion = lambda: controladores.Mostrar_seccion(self.un_juego, self.un_juego.menu_inicio,solo_ocultar=True)
            self.un_juego.menu_instrucciones.mostrar()
            # Agregar a menus activos para que se maneje correctamente
            if hasattr(self, 'menus_activos'):
                self.menus_activos.append(self.un_juego.menu_instrucciones)

    def salir_partida(self):
        """Sale de la partida actual"""
        print("DEBUG: Salir de partida - Desconectando...")
    
        self._desconectar_del_servidor()
        self._limpiar_interfaz()
        # Detener música de la partida y volver a reproducir la música del menú
        try:
            if hasattr(self.un_juego, 'detener_musica'):
                self.un_juego.detener_musica()
        except Exception:
            pass
        try:
            if hasattr(self.un_juego, 'reproducir_musica_menu'):
                self.un_juego.reproducir_musica_menu()
        except Exception:
            pass

        self._mostrar_menu_principal()
        self.un_juego.mesa_juego = None
    def _desconectar_del_servidor(self):
        """Maneja la desconexión del servidor"""
        if hasattr(self, 'instacia_conexion') and self.instacia_conexion:
            try:
                self.instacia_conexion.desconectar()
                print("Desconexión del servidor completada")
            except Exception as e:
                print(f"Error al desconectar: {e}")

    def _limpiar_interfaz(self):
        """Limpia todos los elementos de la interfaz de la partida"""
        # Limpiar menús activos
        if hasattr(self, 'menus_activos'):
            self.menus_activos.clear()
        
        # Ocultar menú de opciones si está visible
        if hasattr(self.un_juego, 'mesa_opciones'):
            self.un_juego.mesa_opciones.ocultar()
        
        # Ocultar mesa actual
        if hasattr(self.un_juego, 'mesa') and self.un_juego.mesa:
            self.un_juego.mesa.ocultar()
    
    def _mostrar_menu_principal(self):
        """Muestra el menú principal"""
        from redes_interfaz import controladores
        controladores.Mostrar_seccion(self.un_juego, self.un_juego.menu_inicio)

