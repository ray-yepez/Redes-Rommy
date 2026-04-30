"""En la parte donde está def obtener_salas_disponibles(self), se coloco como ejemplo un arreglo de salas, puedes cambiarlo por la logica propia de redes para obtener la lista de salas disponibles desde la red."""

import pygame
import sys
import threading


from recursos_graficos import constantes

from recursos_graficos.elementos_de_interfaz_de_usuario import Elemento_texto, Boton, BotonRadio, EntradaTexto, CartelAlerta
from recursos_graficos.menu import Menu
from redes_interfaz import controladores
from logica_interfaz.mesa_interfaz import Mesa_interfaz
from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta

# Importar mixins de menús
from recursos_graficos.menus_core import (
    MenuBaseMixin,
    MenuInstruccionesMixin,
    MenuInicioMixin,
    MenuNombreUsuarioMixin,
    MenuCantidadJugadoresMixin,
    MenuMesaEsperaMixin,
    MenuSeleccionSalaMixin
)


"""Clase ventana donde estaran todos los diseños e interacciones"""
class Ventana(
    MenuBaseMixin,
    MenuInstruccionesMixin,
    MenuInicioMixin,
    MenuNombreUsuarioMixin,
    MenuCantidadJugadoresMixin,
    MenuMesaEsperaMixin,
    MenuSeleccionSalaMixin
):
    _cartas_imagenes = None
    _mazo_imagenes = None
    """Inicializar pygame, fuentes, crear pantalla, nombre de la misma, cargar imagenes, crear menus y botones"""
    def __init__(self):
        pygame.init()
        pygame.font.init()
        # Intentar inicializar el mezclador de audio (no crítico si falla)
        try:
            pygame.mixer.init()
        except Exception:
            pass
        self.pantalla = pygame.display.set_mode((constantes.ANCHO_VENTANA,constantes.ALTO_VENTANA))
        self.cartel_alerta = CartelAlerta(self.pantalla, "", 0, 0)
        pygame.display.set_caption("Rummy500")
        # Datos de juego
        self.lista_elementos = {
            "nombre_creador": "",
            "nombre_sala": "",
            "cantidad_jugadores":0,
            "ip_sala":"",
            "lista_jugadores": [],
            "nombre_unirse": "",
            "salas_disponibles" : []
        }

        self.elementos_creados = []

        # Logo
        ruta_logo = importar_desde_carpeta(
            nombre_archivo="Imagenes/Logos/Logo_O.png",
            nombre_carpeta="assets"
        )

        self.logo_rummy = pygame.image.load(ruta_logo).convert_alpha()

        # ================= NUEVO: CARGA DE FONDOS (Carpeta fondos) =================
        try:
            # Usando los nombres exactos de tu carpeta 'fondos': fondo.png y fondo_mesa.png
            ruta_fondo_menus = importar_desde_carpeta(nombre_archivo="fondos/fondo.png", nombre_carpeta="assets/Imagenes")
            self.img_fondo_menus = pygame.image.load(ruta_fondo_menus).convert()
            self.img_fondo_menus = pygame.transform.scale(self.img_fondo_menus, (constantes.ANCHO_VENTANA, constantes.ALTO_VENTANA))

            ruta_fondo_mesa = importar_desde_carpeta(nombre_archivo="fondos/fondo_mesa.png", nombre_carpeta="assets/Imagenes")
            self.img_fondo_mesa = pygame.image.load(ruta_fondo_mesa).convert()
            self.img_fondo_mesa = pygame.transform.scale(self.img_fondo_mesa, (constantes.ANCHO_VENTANA, constantes.ALTO_VENTANA))
        except Exception as e:
            print(f"Error cargando imágenes de fondo desde la carpeta fondos: {e}")
            # Respaldo en caso de error
            self.img_fondo_menus = pygame.Surface((constantes.ANCHO_VENTANA, constantes.ALTO_VENTANA))
            self.img_fondo_menus.fill(constantes.FONDO_VENTANA)
            self.img_fondo_mesa = pygame.Surface((constantes.ANCHO_VENTANA, constantes.ALTO_VENTANA))
            self.img_fondo_mesa.fill((0, 100, 0)) 
        # ===========================================================================

        # Menús iniciales
        self.menu_instrucciones = self.Menu_instrucciones()
        self.menu_seleccion_sala = self.Menu_seleccion_sala()
        self.menu_inicio = self.Menu_inicio()
        self.boton_jugar = self.Boton_jugar()
        # Estado de música de menú
        self.musica_activa = False
        # volumen maestro
        self.master_volume = 1

        # Crear botón silenciar
        try:
            self.crear_boton_silenciar()
        except Exception:
            self.boton_silenciar = None
        self.menu_Cantidad_Jugadores = self.Menu_Cantidad_Jugadores()
        self.menu_mesa_espera = self.Menu_mesa_espera()
        Buscar_salas = controladores.Buscar_salas(self)

        #Temporizador
        self.clock = pygame.time.Clock()

    @classmethod
    def preparar_imagenes_cartas(cls):
        if cls._cartas_imagenes is not None:
            return cls._cartas_imagenes  # ya están cargadas

        palos = ('Pica', 'Corazon', 'Diamante', 'Trebol')
        nro_carta = ('A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K')
        cartas_imagenes = {}

        for palo in palos:
            for carta in nro_carta:
                ruta = importar_desde_carpeta(
                    nombre_archivo=f"Imagenes/Cartas/{palo} ({carta}).png",
                    nombre_carpeta="assets"
                )
                cart = pygame.image.load(ruta).convert_alpha()
                cartas_imagenes[f"{palo} ({carta})"] = cart


        ruta = importar_desde_carpeta(
            nombre_archivo="Imagenes/Cartas/!Joker.png",
            nombre_carpeta="assets"
        )
        cartas_imagenes["Especial (Joker)"] = pygame.image.load(ruta).convert_alpha()
        

        ruta2 = importar_desde_carpeta(
            nombre_archivo="Imagenes/Cartas/!Reverso.png",
            nombre_carpeta="assets"
        )
        cartas_imagenes["Reverso"] = pygame.image.load(ruta2).convert_alpha()

        cls._cartas_imagenes = cartas_imagenes
        return cls._cartas_imagenes
        
    @classmethod
    def preparar_imagenes_mazo(cls):
        if cls._mazo_imagenes is not None:
            return cls._mazo_imagenes 
        mazo_imagenes = {}
        for x in range(1,6):
            imagen_mazo = importar_desde_carpeta(
            nombre_archivo=f"Imagenes/Mazo/mazo{x}.png",
            nombre_carpeta="assets"
            )
            mazo_imagenes[f"mazo({x})"] = pygame.image.load(imagen_mazo).convert_alpha()
        cls._mazo_imagenes = mazo_imagenes
        return mazo_imagenes

    def reproducir_musica_menu(self):
        try:
            ruta = importar_desde_carpeta(
                nombre_archivo="Audio/Main_menu.ogg",
                nombre_carpeta="assets"
            )
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
            except Exception:
                pass

            pygame.mixer.music.load(ruta)
            pygame.mixer.music.play(-1)  # -1 para loop infinito
            pygame.mixer.music.set_volume(self.master_volume)
        except Exception as e:
            print(f"No se pudo reproducir música de menú: {e}")

    def detener_musica(self):
        """Detiene la música en reproducción si existe."""
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
            self.musica_activa = False
        except Exception as e:
            print(f"Error al detener música: {e}")

    def reproducir_musica_espera(self):
        """Reproduce la música de sala de espera (loop)."""
        try:
            ruta = importar_desde_carpeta(
                nombre_archivo="Audio/Waiting_room.ogg",
                nombre_carpeta="assets"
            )
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
            except Exception:
                pass
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.set_volume(self.master_volume)
            pygame.mixer.music.play(-1)
            self.musica_activa = True
        except Exception as e:
            print(f"No se pudo reproducir música de espera: {e}")

    def reproducir_musica_partida(self):
        """Reproduce la música principal durante la partida (loop)."""
        try:
            ruta = importar_desde_carpeta(
                nombre_archivo="Audio/Rummy Time!.ogg",
                nombre_carpeta="assets"
            )
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
            except Exception:
                pass
            # Cargar y reproducir en loop
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.set_volume(self.master_volume)
            pygame.mixer.music.play(-1)
            self.musica_activa = True
        except Exception as e:
            print(f"No se pudo reproducir música de partida: {e}")

    """Funcion que crea el boton Jugar, se pasa por parametros las constantes, las posiciones se definen manualemente"""

    def Boton_jugar(self):
        x,y = self.centrar(constantes.ELEMENTO_MEDIANO_ANCHO,constantes.ELEMENTO_MEDIANO_ALTO)
        ancho= constantes.ELEMENTO_MEDIANO_ANCHO
        alto= constantes.ELEMENTO_MEDIANO_ALTO
        def accion():
            try:
                # reproducir musica del menu al presionar JUGAR
                self.reproducir_musica_menu()
            except Exception:
                pass
            controladores.Mostrar_seccion(self,self.menu_inicio)

        boton_jugar = self.boton_generico(x,y,ancho,alto," ",accion,)

        try:
            ruta_img = importar_desde_carpeta(
                nombre_archivo="Imagenes/Botones/boton_jugar.png",
                nombre_carpeta="assets"
            )

            img = pygame.image.load(ruta_img).convert_alpha()

            escala = 0.85  # ajusta este número
            nuevo_ancho = int(img.get_width() * escala)
            nuevo_alto = int(img.get_height() * escala)

            img = pygame.transform.smoothscale(img, (nuevo_ancho, nuevo_alto))

            boton_jugar.rect.width = nuevo_ancho
            boton_jugar.rect.height = nuevo_alto
            boton_jugar.rect.center = (x + ancho // 2, y + alto // 2)

            boton_jugar.superficie_texto = img
            boton_jugar.rect_texto = img.get_rect(center=boton_jugar.rect.center)

            boton_jugar.color_actual = None
            boton_jugar.color = None
            boton_jugar.color_hover = None
            boton_jugar.color_clicado = None
            boton_jugar.grosor_borde = 0
            boton_jugar.color_borde_actual = None

        except Exception as e:
                print(f"Error cargando imagen del botón jugar: {e}")

        self.elementos_creados.append(boton_jugar)
        return boton_jugar

    def crear_boton_silenciar(self):
        """Crea el botón de silenciar/activar música mostrado en el menú principal."""
        # Tamaño y posición: esquina inferior izquierda
        tamaño = int(min(constantes.ANCHO_VENTANA, constantes.ALTO_VENTANA) * 0.06)  # tamaño relativo
        ancho = tamaño * 1.2
        alto = tamaño
        x = 100
        y = constantes.ALTO_VENTANA - alto - 60

        def accion():
            try:
                # alternar volumen maestro
                self.master_volume = 0 if self.master_volume == 1 else 1
                # aplicar volumen actual al canal de música
                try:
                    if pygame.mixer.get_init():
                        pygame.mixer.music.set_volume(self.master_volume)
                except Exception:
                    pass
                # actualizar borde para reflejar estado ON/OFF
                try:
                    if self.master_volume == 1:
                        boton.color_borde = constantes.ELEMENTO_CLICADO_PRINCIPAL
                    else:
                        boton.color_borde = constantes.GRIS
                    boton.color_borde_actual = boton.color_borde
                except Exception:
                    pass
            except Exception as e:
                print(f"Error al alternar sonido: {e}")


        # Crear botón base (sin texto) y luego reemplazar su superficie_texto por la imagen
        boton = self.boton_generico(x, y, ancho, alto, "", accion, tp_color="s", tp_borde="n")

        # Quitar fondo y bordes
        boton.color_actual = None
        boton.color = None
        boton.color_hover = None
        boton.color_clicado = None

        boton.grosor_borde = 0
        boton.color_borde = None
        boton.color_borde_actual = None
        boton.color_borde_hover = None
        boton.color_borde_clicado = None

        # Cargar imagen del botón volumen
        try:
            ruta_img = importar_desde_carpeta(
                nombre_archivo="Imagenes/botones/boton_volumen.png",
                nombre_carpeta="assets"
            )

            img = pygame.image.load(ruta_img).convert_alpha()
            img = pygame.transform.smoothscale(img, (ancho, alto))

            boton.superficie_texto = img
            boton.rect_texto = img.get_rect(center=boton.rect.center)

        except Exception as e:
            print(f"No se pudo cargar imagen boton_volumen.png: {e}")

        self.boton_silenciar = boton
        return self.boton_silenciar

    """Boton de salir del juego"""
    def salir(self):
        pygame.quit()
        sys.exit()

    def menus_condicionales(self):
        menu_condicional = [
            "menu_mesa_espera", 
            "menu_nombre_creador", 
            "menu_nombre_usuario", 
            "menu_seleccion_sala",
            "mesa",
            "mesa_opciones",
            "menu_instrucciones"
        ]
        return menu_condicional

    def menus_principales(self):
        menus = [
            self.menu_seleccion_sala, 
            self.menu_instrucciones, 
            self.menu_inicio, 
            self.menu_Cantidad_Jugadores
        ]
        return menus

    """Funciones auxiliares para el ciclo principal del juego"""
    def ejecutar_manejo_eventos(self, evento):
        if self.cartel_alerta.manejar_evento(evento):
            return
        
        self.boton_jugar.manejar_evento(evento)
        # manejar evento del boton silenciar solo cuando el menu inicio esté visible
        try:
            menu_visible = getattr(self.menu_inicio, 'visible', False) if hasattr(self, 'menu_inicio') else False
            boton_inicio_visible = getattr(self.boton_jugar, 'visible', False) if hasattr(self, 'boton_jugar') else False
            if hasattr(self, 'boton_silenciar') and self.boton_silenciar and (menu_visible or boton_inicio_visible):
                self.boton_silenciar.manejar_evento(evento)
        except Exception:
            pass
        
        menus = self.menus_principales()
    
        for menu in menus:
            menu.manejar_eventos(evento)

        menu_condicionales = self.menus_condicionales()
    
        for menu_name in menu_condicionales:
            if hasattr(self, menu_name):
                getattr(self, menu_name).manejar_eventos(evento)

        if hasattr(self, 'mesa') and self.mesa and hasattr(self.mesa, 'menus_activos'):
            for menu in self.mesa.menus_activos:
                menu.manejar_eventos(evento)

        if hasattr(self, 'menu_instrucciones') and self.menu_instrucciones in self.elementos_creados:
            self.menu_instrucciones.manejar_eventos(evento)
            #======Jesua:Detectar secuencia de teclas para la tabla de puntuacion
        if evento.type == pygame.KEYDOWN:
            # Registrar tiempo de la última tecla (ms)
            try:
                self.last_key_time = pygame.time.get_ticks()
            except Exception:
                self.last_key_time = None

    def ejecutar_verificacion_hovers(self, posicion_raton):
        self.cartel_alerta.verificar_hover(posicion_raton)
        self.boton_jugar.verificar_hover(posicion_raton)
        try:
            menu_visible = getattr(self.menu_inicio, 'visible', False) if hasattr(self, 'menu_inicio') else False
            boton_inicio_visible = getattr(self.boton_jugar, 'visible', False) if hasattr(self, 'boton_jugar') else False
            if hasattr(self, 'boton_silenciar') and self.boton_silenciar and (menu_visible or boton_inicio_visible):
                self.boton_silenciar.verificar_hover(posicion_raton)
        except Exception:
            pass
        # Menús principales
        menus = self.menus_principales()
    
        for menu in menus:
            if menu:
                menu.verificar_hovers(posicion_raton)
    
 
        menu_condicionales = self.menus_condicionales()
    
        for menu_name in menu_condicionales:
            if hasattr(self, menu_name):
                getattr(self, menu_name).verificar_hovers(posicion_raton)

        if hasattr(self, 'mesa') and self.mesa and hasattr(self.mesa, 'menus_activos'):
            for menu in self.mesa.menus_activos:
                menu.verificar_hovers(posicion_raton)

    def ejecutar_dibujado(self):
        # SUSTITUCIÓN DE: self.pantalla.fill(constantes.FONDO_VENTANA)
        # Lógica para decidir qué fondo dibujar según la sección actual
        if hasattr(self, 'mesa') and self.mesa and getattr(self.mesa, 'visible', False):
            self.pantalla.blit(self.img_fondo_mesa, (0, 0))
        else:
            self.pantalla.blit(self.img_fondo_menus, (0, 0))
        
        self.boton_jugar.dibujar()
        
        menus = self.menus_principales()
    
        for menu in menus:
            if menu:
                menu.dibujar_menu()

        menu_condicionales = self.menus_condicionales()
        for nombre_menu in menu_condicionales:
            if hasattr(self, nombre_menu):
                menu = getattr(self, nombre_menu)

                if nombre_menu == "mesa" and hasattr(self.mesa, 'menus_activos') and self.mesa.menus_activos:
                    continue

                menu.dibujar_menu()

        if hasattr(self, 'mesa') and self.mesa and hasattr(self.mesa, 'menus_activos'):
            for menu in self.mesa.menus_activos:
                menu.dibujar_menu()

        self.cartel_alerta.dibujar()
        
        # dibujar boton silenciar al final para que quede por encima de los menus
        try:
            menu_visible = getattr(self.menu_inicio, 'visible', False) if hasattr(self, 'menu_inicio') else False
            boton_inicio_visible = getattr(self.boton_jugar, 'visible', False) if hasattr(self, 'boton_jugar') else False
            if hasattr(self, 'boton_silenciar') and self.boton_silenciar and (menu_visible or boton_inicio_visible):
                self.boton_silenciar.dibujar()
        except Exception:
            pass

    def Correr_juego(self):
        ejecutar = True
        
        hilo_imagenes_cartas = threading.Thread(target=Ventana.preparar_imagenes_cartas)
        hilo_imagenes_mazo = threading.Thread(target=Ventana.preparar_imagenes_mazo)
        hilo_imagenes_cartas.start()
        hilo_imagenes_mazo.start()

        while ejecutar:
            posicion_raton = pygame.mouse.get_pos()
            eventos = pygame.event.get()
            self.ejecutar_verificacion_hovers(posicion_raton)

            for evento in eventos:
                if evento.type == pygame.QUIT:
                    controladores.Salir()
                    ejecutar = False
                controladores.modificacion_real_datos(self,evento,constantes)
                self.ejecutar_manejo_eventos(evento)

            # ELIMINADO: self.pantalla.fill(constantes.FONDO_VENTANA)
            # Ya no es necesario limpiar con un color, porque ejecutar_dibujado()
            # ahora dibuja la imagen de fondo (blit) que cubre toda la pantalla.

            self.ejecutar_dibujado()
            
            # ======Jesua:Mostrar tabla de puntuación mientras se mantiene presionada la tecla TAB
            try:
                keys = pygame.key.get_pressed()
                if hasattr(self, 'mesa_juego') and self.mesa_juego:
                    if keys[pygame.K_TAB]:
                        # Mostrar menú de puntuación
                        self.mesa_juego.mostrar_menu_puntuacion()
                    else:
                        # Ocultar menú de puntuación cuando no se presiona TAB
                        self.mesa_juego.ocultar_menu_puntuacion()
                    
                    # Dibujar menú de puntuación si está visible
                    if (hasattr(self.mesa_juego, 'menu_puntuacion') and 
                        self.mesa_juego.menu_puntuacion and 
                        self.mesa_juego.menu_puntuacion.visible):
                        self.mesa_juego.menu_puntuacion.dibujar_menu()
            except Exception as e:
                # no bloquear el bucle de juego por errores en el overlay
                print(f"Error al mostrar tabla de puntuación: {e}")

            pygame.display.flip()
            self.clock.tick(constantes.FPS)
        pygame.quit()

ventana = Ventana()
ventana.Correr_juego()