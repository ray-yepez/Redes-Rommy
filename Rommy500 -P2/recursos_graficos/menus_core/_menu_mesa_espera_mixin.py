"""Mixin para el menú de mesa de espera (lobby)"""

from recursos_graficos import constantes
from recursos_graficos.menu import Menu
from recursos_graficos.elementos_de_interfaz_de_usuario import Elemento_texto
from redes_interfaz import controladores


class MenuMesaEsperaMixin:
    """Mixin con métodos para el menú de sala de espera (lobby)"""
    
    def Menu_mesa_espera(self):
        """Crea el menú de espera mientras los jugadores se conectan
        
        Returns:
            Menu: Instancia del menú de mesa de espera
        """
        x_menu, y_menu = self.centrar(
            constantes.ANCHO_MENU_MESA_ESPERA,
            constantes.ALTO_MENU_MESA_ESPERA
        )
        
        menu_mesa_espera = Menu(
            self,
            constantes.ANCHO_MENU_MESA_ESPERA,
            constantes.ALTO_MENU_MESA_ESPERA,
            x_menu,
            y_menu,
            constantes.ELEMENTO_FONDO_TERCIARIO,
            constantes.ELEMENTO_BORDE_TERCIARIO,
            constantes.BORDE_PRONUNCIADO,
            constantes.REDONDEO_NORMAL
        )
        
        elemento_texto = self.crear_elementos_mesa_espera(menu_mesa_espera)
        
        # Guardar referencia al elemento de texto para poder actualizarlo
        menu_mesa_espera.elemento_texto_espera = elemento_texto
        self.elementos_creados.append(menu_mesa_espera)
        return menu_mesa_espera
    
    def crear_elementos_mesa_espera(self, menu_mesa_espera):
        """Crea el elemento de texto centrado que muestra el estado del lobby
        
        Args:
            menu_mesa_espera: Instancia del menú
            
        Returns:
            Elemento_texto: Referencia al elemento de texto creado
        """
        ancho_txt_esperando = constantes.ELEMENTO_GRANDE_ANCHO * 1.7
        alto_txt_esperando = constantes.ELEMENTO_MEDIANO_ALTO * 3.2
        x_txt_esperando = (constantes.ANCHO_MENU_MESA_ESPERA - ancho_txt_esperando) * (0.5)
        y_txt_esperando = (constantes.ALTO_MENU_MESA_ESPERA - alto_txt_esperando) * (0.5)
        
        elemento_texto = menu_mesa_espera.crear_elemento(
            Clase=Elemento_texto,
            x=x_txt_esperando,
            y=y_txt_esperando,
            un_juego=self,
            texto=self.texto_menu_mesa_espera(),
            ancho=ancho_txt_esperando,
            alto=alto_txt_esperando,
            tamaño_fuente=constantes.F_GRANDE,
            fuente=constantes.FUENTE_TITULO,
            color=constantes.ELEMENTO_FONDO_TERCIARIO,
            radio_borde=constantes.REDONDEO_NORMAL,
            color_texto=(187, 165, 113),
            color_borde=constantes.SIN_COLOR,
            grosor_borde=constantes.SIN_BORDE,
            alineacion="izquierda"
        )
        return elemento_texto

    def texto_menu_mesa_espera(self):
        """Genera el texto dinámico del lobby con información actual
        
        Returns:
            str: Texto formateado con información de la sala
        """
        lista_jugadores = self.lista_elementos.get("lista_jugadores") or []
        jugadores_actuales = len(lista_jugadores)
        max_esperados = self.lista_elementos.get("cantidad_jugadores", 0)
        nombre_sala = self.lista_elementos.get("nombre_sala", "No definido")
        nombre_creador = self.lista_elementos.get("nombre_creador", "No definido")

        faltan = max(0, max_esperados - jugadores_actuales)
    
        texto = (
            f"NOMBRE DE LA SALA: {nombre_sala}\n"
            f"CREADOR DE LA SALA: {nombre_creador}\n"
            f"JUGADORES CONECTADOS: {jugadores_actuales} de {max_esperados}\n"
            f"ESPERANDO JUGADORES...\nFALTAN: {faltan}"
        )
    
        print(f"Generando texto para mesa de espera:")
        print(f"- Sala: {nombre_sala}")
        print(f"- Creador: {nombre_creador}")
        print(f"- Jugadores: {jugadores_actuales}/{max_esperados}")
        print(f"- Faltan: {faltan}")
    
        return texto

    def actualizar_mesa_espera(self):
        """Actualiza el texto del menú de espera cuando cambian los jugadores conectados"""
        print("Actualizando mesa de espera...")
    
        if hasattr(self, "menu_mesa_espera") and self.menu_mesa_espera in self.elementos_creados:
            texto_actualizado = self.texto_menu_mesa_espera()
            print(f"Texto actualizado: {texto_actualizado}")
        
            if hasattr(self.menu_mesa_espera, 'elemento_texto_espera'):
                self.menu_mesa_espera.elemento_texto_espera.texto = texto_actualizado
                self.menu_mesa_espera.elemento_texto_espera.prepar_texto()
                print("✓ Texto del elemento actualizado")
            else:
                # Fallback: buscar en la lista de botones
                for boton in self.menu_mesa_espera.botones:
                    if isinstance(boton, Elemento_texto):
                        boton.texto = texto_actualizado
                        boton.prepar_texto()
                        print("✓ Texto del elemento encontrado y actualizado")
                        break
        else:
            print("Menú de mesa de espera no encontrado, creando nuevo...")
            # Crear nuevo menú si no existe
            self.menu_mesa_espera = self.Menu_mesa_espera()
            self.elementos_creados.append(self.menu_mesa_espera)
            controladores.Mostrar_seccion(self, self.menu_mesa_espera)
