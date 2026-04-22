"""Módulo interno para sistema de menú de opciones"""

from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta
from recursos_graficos import constantes
from recursos_graficos.elementos_de_interfaz_de_usuario import Boton
from redes_interfaz import controladores

Menu = importar_desde_carpeta("menu.py","Menu","recursos_graficos")
BotonLogoMenu = importar_desde_carpeta("elementos_de_interfaz_de_usuario.py","BotonLogoMenu","recursos_graficos")


class MenuOpcionesMixin:
    """Mixin con métodos para sistema de menú de opciones"""
    
    def crear_boton_menu(self):
        """Crea el botón de menú en la esquina superior derecha"""
        ancho_boton = 40
        alto_boton = 30
        
        x = constantes.ANCHO_MENU_MESA - ancho_boton - 5
        y = 10
        boton = BotonLogoMenu(
            un_juego=self.un_juego,
            x=x, y=y,
            radio_borde=5,
            color_rayas=(0, 0, 0),
            color_rayas_hover=constantes.ELEMENTO_BORDE_CUATERNARIO,
            color_rayas_clicado=constantes.ELEMENTO_CLICADO_PRINCIPAL,
            deshabilitado=False,
            accion=lambda: self.mostrar_menu_opciones(),
        )
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
            constantes.ELEMENTO_FONDO_SECUNDARO,
            constantes.ELEMENTO_BORDE_SECUNDARIO,
            constantes.BORDE_PRONUNCIADO,
            constantes.REDONDEO_NORMAL
        )
        
        self.crear_botones_menu_opciones()
        # Agregar botón silenciar dentro del menú de opciones (mutear durante la partida)
        try:
            self.crear_boton_silenciar_menu()
        except Exception:
            pass
        self.un_juego.mesa_opciones = self.menu_opciones
        self.un_juego.mesa_opciones.mostrar()
        # self.menus_activos.append(self.menu_opciones)
        print(f"DEBUG: Menú de opciones creado con {len(self.menu_opciones.botones)} botones")

    def crear_botones_menu_opciones(self):
        """Crea los botones del menú de opciones"""
        ancho_boton = self.menu_opciones.ancho * 0.6
        alto_boton = constantes.ELEMENTO_PEQUENO_ALTO * 0.8
        espacio = 20
        
        x_base = (self.menu_opciones.x + ancho_boton) * 0.575
        y_base = self.menu_opciones.y + (self.menu_opciones.alto * 0.25)
        
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
                tamaño_fuente=constantes.F_PEQUENA,
                fuente=constantes.FUENTE_ESTANDAR,
                color=constantes.ELEMENTO_FONDO_PRINCIPAL,
                radio_borde=constantes.REDONDEO_NORMAL,
                color_texto=constantes.COLOR_TEXTO_PRINCIPAL,
                color_borde=constantes.ELEMENTO_BORDE_SECUNDARIO,
                grosor_borde=constantes.BORDE_INTERMEDIO,
                color_borde_hover=constantes.ELEMENTO_HOVER_PRINCIPAL,
                color_borde_clicado=constantes.ELEMENTO_CLICADO_PRINCIPAL,
                grupo=[],
                valor=texto.lower().replace(" ", "_"),
                accion=accion
            )
            
            self.menu_opciones.botones.append(boton)

    def crear_boton_silenciar_menu(self):
        """Añade un botón pequeño de silenciar dentro del menú de opciones."""
        try:
            # Tamaño y posición relativa dentro del menú
            tamaño = int(min(self.menu_opciones.ancho, self.menu_opciones.alto) * 0.08)
            ancho = tamaño
            alto = tamaño
            x = int(self.menu_opciones.x + self.menu_opciones.ancho - ancho - 10)
            y = int(self.menu_opciones.y + 10)

            def accion():
                try:
                    juego = self.un_juego
                    # Alternar volumen maestro
                    juego.master_volume = 0 if getattr(juego, 'master_volume', 1) == 1 else 1
                    try:
                        if pygame.mixer.get_init():
                            pygame.mixer.music.set_volume(juego.master_volume)
                    except Exception:
                        pass

                    # Actualizar borde del boton dentro del menu
                    try:
                        if juego.master_volume == 1:
                            boton.color_borde = constantes.ELEMENTO_CLICADO_PRINCIPAL
                        else:
                            boton.color_borde = constantes.GRIS
                        boton.color_borde_actual = boton.color_borde
                    except Exception:
                        pass

                    # Sincronizar con el boton principal en la ventana, si existe
                    try:
                        if hasattr(juego, 'boton_silenciar') and juego.boton_silenciar:
                            if juego.master_volume == 1:
                                juego.boton_silenciar.color_borde = constantes.ELEMENTO_CLICADO_PRINCIPAL
                            else:
                                juego.boton_silenciar.color_borde = constantes.GRIS
                            juego.boton_silenciar.color_borde_actual = juego.boton_silenciar.color_borde
                    except Exception:
                        pass
                except Exception as e:
                    print(f"Error alternando sonido desde menú opciones: {e}")

            # Crear el botón (sin texto) y asignar imagen
            boton = Boton(
                un_juego=self.un_juego,
                texto="",
                ancho=ancho,
                alto=alto,
                x=x,
                y=y,
                tamaño_fuente=constantes.F_PEQUENA,
                fuente=constantes.FUENTE_ESTANDAR,
                color=self.menu_opciones.fondo_color if hasattr(self.menu_opciones, 'fondo_color') else constantes.ELEMENTO_FONDO_PRINCIPAL,
                radio_borde=constantes.REDONDEO_NORMAL,
                color_texto=constantes.COLOR_TEXTO_PRINCIPAL,
                color_borde=constantes.ELEMENTO_CLICADO_PRINCIPAL if getattr(self.un_juego, 'master_volume', 1) == 1 else constantes.GRIS,
                grosor_borde=constantes.BORDE_LIGERO,
                color_borde_hover=constantes.ELEMENTO_HOVER_PRINCIPAL,
                color_borde_clicado=constantes.ELEMENTO_CLICADO_PRINCIPAL,
                grupo=[],
                valor="silenciar_menu",
                accion=accion,
            )

            # Cargar imagen y usarla como superficie
            try:
                ruta_img = importar_desde_carpeta(nombre_archivo="Imagenes/Logos/Mute.png", nombre_carpeta="assets")
                import pygame
                img = pygame.image.load(ruta_img).convert_alpha()
                img = pygame.transform.smoothscale(img, (ancho, alto))
                boton.superficie_texto = img
                boton.rect_texto = img.get_rect(center=boton.rect.center)
                boton.color_actual = self.menu_opciones.fondo_color
            except Exception as e:
                print(f"No se pudo cargar imagen Mute.png en menu opciones: {e}")

            # Agregar al menú
            self.menu_opciones.botones.append(boton)
            return boton
        except Exception:
            return None

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

