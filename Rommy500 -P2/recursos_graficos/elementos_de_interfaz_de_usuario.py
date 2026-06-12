#IMPORTANTE 
##Querido colega programador:
##
##
## Cuando escribí este código, sólo Dios y yo
##
# sabíamos cómo funcionaba.
##
#Ahora, ¡sólo Dios lo sabe!
##
##
# Así que si está tratando de 'optimizarlo'
##
# y fracasa (seguramente), por favor,
##
# incremente el contador a continuación
##
# como una advertencia para su siguiente colega:
##
## total_horas_perdidas_aquí = 3000

from recursos_graficos.archivo_de_importaciones import importar_desde_carpeta
constantes = importar_desde_carpeta("constantes.py",nombre_carpeta="recursos_graficos")
# import constantes
import pygame

class Elemento_texto:
    def __init__(self, un_juego, texto, ancho, alto, x, y, tamaño_fuente, fuente, color, radio_borde=0, color_texto=(0, 0, 0), color_borde=(0, 0, 0), grosor_borde=0,alineacion="centro", alineacion_vertical=None,**kwargs):
        self.pantalla = un_juego.pantalla
        self.ancho, self.alto = ancho, alto
        self.x, self.y = x, y
        self.texto = texto
        self.tamaño_fuente = tamaño_fuente
        self.fuente = self.cargar_fuente(fuente)
        self.color = color
        self.color_actual = color
        self.color_texto = color_texto
        self.radio_borde = radio_borde
        self.color_borde = color_borde
        self.grosor_borde = grosor_borde
        self.color_borde_actual = self.color_borde
        self.alineacion = alineacion.lower()
        self.alineacion_vertical = alineacion_vertical
        
        #Atributos para el scrolleable
        self.scroll_offset = 0   # cuanto se ha desplazado hacia arriba/abajo
        self.scroll_activo = False
        self.scroll_rect = None  # rectángulo de la barra
        self.scroll_drag = False # si estoy arrastrando con el ratón


        # Crear rectángulo del elemento de texto
        self.rect = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        self.esta_hover = False
        self.visible = True
        
        # Preparar el texto
        self.prepar_texto()
    
    def cargar_fuente(self, fuente):
        try:
            return pygame.font.Font(fuente, self.tamaño_fuente)
        except FileNotFoundError:
            return pygame.font.SysFont(fuente, self.tamaño_fuente)
    
    def prepar_texto(self):
        """Divide el texto en líneas automáticamente si es muy largo"""
        # Calcular ancho máximo permitido (con margen) y guardar el ancho del texto renderizado
        ancho_maximo = self.ancho * 0.9
        ancho_texto = self.fuente.size(self.texto)[0]
        
        # Si el texto cabe en una línea, lo dejamos así
        if ancho_texto <= ancho_maximo:
            #la superficie de texto es el texto renderizado con el color
            self.superficie_texto = self.fuente.render(self.texto, True, self.color_texto)
            self.texto_una_linea()
            return
        
        # Si no cabe, preparamos texto con multiples lineas
        self.prepar_texto_multiple(ancho_maximo)
    # def prepar_scroll(self):
        
    def prepar_texto_multiple(self, ancho_maximo):
        # dividir por saltos de párrafo "\n"
        saltos_elementos = self.texto.split('\n')
        self.elementos_saltos = []

        # generar superficies para este bloque (puede ocupar varias líneas)
        for linea in saltos_elementos:
            #se guarda en superficies el arreglo con todas las superficies de el elemento
            superficies = self.texto_mutiple_maximo_espacio(linea, ancho_maximo) 
            self.elementos_saltos.append(superficies) #se agrega ese arreglo a otro [[],..]

        # posicionar cada bloque de superficies
        self.rects_texto = []
        self.ajustar_posicion_elementos()


    def texto_mutiple_maximo_espacio(self, linea, ancho_maximo):
        #Definimos lineas que guarda cada linea nececesaria para dividir la "linea" de parametro, en varias
        lineas = []
        linea_actual = ""
        palabras = linea.split(' ')

        for palabra in palabras:
            #Prueba concatena si es que linea actual ya tiene una palabra
            prueba = f"{linea_actual} {palabra}".strip() if linea_actual else palabra
            
            #tamño del ancho del texto que tenga palabra ya renderizado
            ancho_texto_prueba = self.fuente.size(prueba)[0] 
            
            #actualiza la linea actual si es que se puede, sino simplemente termina la linea y solo la agrega a lineas
            if ancho_texto_prueba <= ancho_maximo:
                linea_actual = prueba 
            else:
                if linea_actual:
                    lineas.append(linea_actual)
                linea_actual = palabra #-> se reinicia linea_actual con la palabra que no se pudo agregar

        #Permite agregar la ultima linea
        if linea_actual:
            lineas.append(linea_actual)

        #Se recorre lineas, cada linea si renderiza y si agrega a superficie, es decir es exactamente el arreglo pero cada elemento ya esta renderizado
        superficies = []
        for linea in lineas:
            superficie = self.fuente.render(linea, True, self.color_texto)
            superficies.append(superficie)

        return superficies  # devolver el conjunto de lineas renderizadas


    def ajustar_posicion_elementos(self):
        """Posicionar cada bloque de líneas (separados por '\n')."""

        y_actual = self.rect.top + self.alto * 0.02  # margen arriba
        espacio_dejar_x = self.ancho * 0.02
        self.rects_texto = []
        self.superficies_texto_planas = []

        #Recorre el elementos_saltos, cada bloque es un arreglo (que tiene todos los textos renderizados de ese bloque)
        for bloque in self.elementos_saltos:
            #guardamos en rects_bloque el arreglo con las posiciones
            rects_bloque = self.ajustar_posicion_lineas(bloque, y_actual, espacio_dejar_x)
            
            #Agregas elementos a las listas correspondientes
            self.rects_texto.extend(rects_bloque)
            self.superficies_texto_planas.extend(bloque)  

            #se suma el valor del altro de cada superficie del bloque, y se le suma la longitud del (bloque-1)*5
            alto_bloque = sum(superficie.get_height() for superficie in bloque) + (len(bloque)-1)*5
            y_actual += alto_bloque + 20

        # altura total de todo el texto
        alto_total = self.rects_texto[-1].bottom - self.rects_texto[0].top  

        # activar scroll si sobrepasa
        if alto_total > self.alto:
            self.scroll_activo = True
            # calcular altura de la barra proporcional
            visible_ratio = self.alto / alto_total
            barra_altura = max(20, self.alto * visible_ratio)
            self.scroll_rect = pygame.Rect(
                self.rect.right - self.ancho*0.05,  # pegada al borde derecho
                self.rect.top,
                self.ancho*0.01,  # ancho barra
                barra_altura
            )
        else:
            self.scroll_activo = False
            self.scroll_rect = None




    def ajustar_posicion_lineas(self, bloque, y_inicial, espacio_dejar_x):
        rects_texto = []
        y = y_inicial

        #recorremos bloque(lista de superficies)
        for superficie in bloque:
            ancho_linea = superficie.get_width()

            if self.alineacion == "izquierda":
                x = self.rect.left + espacio_dejar_x
            elif self.alineacion == "derecha":
                x = self.rect.right - ancho_linea - espacio_dejar_x
            else:  # centro
                x = self.rect.centerx - ancho_linea / 2

            rects_texto.append(pygame.Rect(x, y, ancho_linea, superficie.get_height()))
            y += superficie.get_height() + 5  # 5px entre líneas del mismo bloque
        
        return rects_texto

    
    def texto_una_linea(self):
        """Posiciona texto de una sola línea, dependiendo de la alineacion y la alineacion_vertical, usamos .right por ejemplo para saber la ubicacion del borde derecho sin tenerr que calcular nada"""
        espacio_dejar_x = self.ancho*0.02
        espacio_dejar_y = self.alto*0.02
        match self.alineacion:
            case "izquierda":  x_pos = self.rect.left + espacio_dejar_x
            case "derecha": x_pos = self.rect.right - espacio_dejar_x
            case _: x_pos = self.rect.centerx
        match self.alineacion_vertical:
            case "arriba": y_pos = self.rect.top + espacio_dejar_y
            case "abajo": y_pos = self.rect.bottom - espacio_dejar_y
            case _: y_pos = self.rect.centery
        
        #Determina la ubicacion, los "midleft" posicionan desde la izquierda en el eje x, es decir miden desde la izquierda del eje horizontal, y centran el "centro del elemento a ubicar" en una linea imaginaria y que tambien representa una posicion, y mide desde arriba.
        if self.alineacion == "izquierda":
            self.rect_texto = self.superficie_texto.get_rect(midleft=(x_pos, y_pos))
        elif self.alineacion == "derecha":
            self.rect_texto = self.superficie_texto.get_rect(midright=(x_pos, y_pos))
        else:
            self.rect_texto = self.superficie_texto.get_rect(center=(x_pos, y_pos))

    def dibujar(self):
        if self.visible:
            # Dibujar fondo y borde
            pygame.draw.rect(self.pantalla, self.color_actual, self.rect, border_radius=self.radio_borde)
            if self.grosor_borde > 0:
                pygame.draw.rect(self.pantalla, self.color_borde_actual, self.rect, 
                                self.grosor_borde, border_radius=self.radio_borde)
            
            # Dibujar texto
            if hasattr(self, 'superficies_texto_planas'):
                for superficie, rect in zip(self.superficies_texto_planas, self.rects_texto):
                    rect_scroll = rect.move(0, -self.scroll_offset)  # aplicar offset
                    if rect_scroll.colliderect(self.rect):  # pintar solo si está dentro del área
                        self.pantalla.blit(superficie, rect_scroll)
            else:
                rect_scroll = self.rect_texto.move(0, -self.scroll_offset)
                if rect_scroll.colliderect(self.rect):
                    self.pantalla.blit(self.superficie_texto, rect_scroll)

            # dibujar scroll si corresponde
            if self.scroll_activo and self.scroll_rect:
                pygame.draw.rect(self.pantalla, (100,100,100), self.scroll_rect)


    
    def mostrar(self): self.visible = True
    def ocultar(self): self.visible = False
    def verificar_hover(self, posicion_raton): pass
    def max_scroll(self):
        return (self.rects_texto[-1].bottom - self.rects_texto[0].top) - self.alto
    def sync_barra(self):
        """Sincroniza la posición de la barra según el scroll_offset actual."""
        if not self.scroll_activo or not self.scroll_rect:
            return
        ratio = self.scroll_offset / self.max_scroll() if self.max_scroll() > 0 else 0
        self.scroll_rect.top = self.rect.top + ratio * (self.rect.height - self.scroll_rect.height)

    def manejar_evento(self, evento):
        if not self.visible:  # Solo procesar eventos si es visible
            return False
        if not self.scroll_activo:
            return

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 4:  # rueda arriba
                self.scroll_offset = max(0, self.scroll_offset - 20)
                self.sync_barra()
            elif evento.button == 5:  # rueda abajo
                self.scroll_offset = min(
                    self.max_scroll(),
                    self.scroll_offset + 20
                )
                self.sync_barra()
            elif self.scroll_rect and self.scroll_rect.collidepoint(evento.pos):
                self.scroll_drag = True
                self.drag_y = evento.pos[1] - self.scroll_rect.top

        elif evento.type == pygame.MOUSEBUTTONUP:
            self.scroll_drag = False

        elif evento.type == pygame.MOUSEMOTION and self.scroll_drag:
            # mover barra con el ratón
            nueva_top = evento.pos[1] - self.drag_y
            nueva_top = max(self.rect.top, min(nueva_top, self.rect.bottom - self.scroll_rect.height))
            self.scroll_rect.top = nueva_top

            # convertir posición barra -> scroll_offset
            ratio = (self.scroll_rect.top - self.rect.top) / (self.rect.height - self.scroll_rect.height)
            self.scroll_offset = ratio * self.max_scroll()



class Boton(Elemento_texto):
    def __init__(self, *args, color_hover=None, color_borde_hover=None, 
                 color_borde_clicado=None, accion=None,deshabilitado=None, **kwargs):
        
        # Pasar todos los argumentos posicionales y nombrados al padre
        super().__init__(*args, **kwargs)
        
        # Atributos específicos de Boton
        self.deshabilitado = deshabilitado
        self.color_hover = color_hover
        self.color_borde_hover = color_borde_hover
        self.color_borde_clicado = color_borde_clicado
        self.accion = accion
        self.presionado = False
        
        # SOLO AGREGANDO ESTOS DOS ATRIBUTOS
        self.color_texto_original = self.color_texto
        self.color_borde_original = self.color_borde

    def ocultar(self):
        return super().ocultar()

    def verificar_hover(self, posicion_raton):
        estaba_hover = self.esta_hover
        self.esta_hover = self.rect.collidepoint(posicion_raton) 
        if self.deshabilitado:
            return False
        if self.esta_hover != estaba_hover:
            if self.esta_hover and self.color_borde_hover:
                self.color_borde_actual = self.color_borde_hover
            elif not self.esta_hover:
                self.color_borde_actual = self.color_borde
            return True
        return False

    def manejar_evento(self, evento):
        if not self.visible or self.deshabilitado:
            self.deshabilitar()
            return False

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.esta_hover:
                if self.color_borde_clicado:
                    self.color_borde_actual = self.color_borde_clicado
                self.presionado = True
                return True

        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            if self.presionado and self.esta_hover:
                if self.accion:
                    self.accion()
            self.presionado = False
            return True

        return False
    def deshabilitar(self):
        if self.deshabilitado:
            self.color_borde_actual = (100, 100, 100)  # Gris para deshabilitado
            self.color_texto = (100, 100, 100)
    def habilitar(self):
        if not self.deshabilitado:
            self.color_borde_actual = self.color_borde_original  # Restaurar color original
            self.color_texto = self.color_texto_original         # Restaurar color original



"""En caso de ser un boton tipo radio"""
class BotonRadio(Boton):
    def __init__(self, *args, grupo=None, valor=None, deshabilitado=False, **kwargs):
        super().__init__(*args, deshabilitado=deshabilitado, **kwargs)
        
        self.seleccionado = False
        self.valor = valor
        
        # Gestionar grupo automáticamente
        self.grupo = grupo if grupo is not None else []
        if self not in self.grupo:
            self.grupo.append(self)
        
        # Aplicar estado deshabilitado
        if self.deshabilitado:
            self.color_borde_actual = (100, 100, 100)
            self.color_texto = (100, 100, 100)

    def verificar_hover(self, posicion_raton):
        if self.deshabilitado:
            return False

        estaba_hover = self.esta_hover
        self.esta_hover = self.rect.collidepoint(posicion_raton)

        if self.esta_hover != estaba_hover and not self.seleccionado:
            self.color_borde_actual = self.color_borde_hover if self.esta_hover else self.color_borde
            return True

    def sobre_el_elemento(self, con_retorno, funcion=None):
        if self.esta_hover and not self.seleccionado:
            self.seleccionar()
            if self.accion:
                self.accion(self)
            if con_retorno:
                return True
            if funcion:
                funcion()
        return False

    def manejar_evento(self, evento):
        if not self.visible or self.deshabilitado:
            return False
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if hasattr(evento, 'pos') and self.rect.collidepoint(evento.pos):
                self.sobre_el_elemento(True)
                return True
        return False

    def seleccionar(self):
        if self.grupo:
            for boton in self.grupo:
                if boton != self:
                    boton.deseleccionar()
        self.seleccionado = True
        self.color_borde_actual = self.color_borde_clicado

    def deseleccionar(self):
        self.seleccionado = False
        if not self.deshabilitado:
            self.color_borde_actual = self.color_borde

class EntradaTexto(BotonRadio):
    def __init__(self, *args, valor="", limite_caracteres=None, grupo=None, permitir_espacios=False, permitir_numeros=False, permitir_especiales=False, cartel_alerta= None, **kwargs):
        self.permitir_espacios = permitir_espacios
        self.permitir_numeros = permitir_numeros
        self.permitir_especiales = permitir_especiales
        self.texto_valido = True
        self.cartel_alerta = cartel_alerta
        super().__init__(*args, grupo=grupo, valor=None, **kwargs)
        self.valor = valor
        self.limite_caracteres = limite_caracteres
        self.pos_cursor = len(valor)
        self.mostrar_cursor = True
        self.ultima_tecla = None
        self.tiempo_repeticion = 30
        self.retardo_inicial = 200
        self.ultimo_borrado = 0
        self.ultimo_parpadeo = pygame.time.get_ticks()

        self.actualizar_texto()
    def mover_cursor(self,evento):
        click_x = evento.pos[0]
        x_texto_inicial = self.rect_texto.x
        self.pos_cursor = len(self.valor)
        for i in range(len(self.valor) + 1):
            ancho_parcial = self.fuente.render(self.valor[:i], True, self.color_texto).get_width()
            if x_texto_inicial + ancho_parcial >= click_x:
                self.pos_cursor = i
                break
    def procesar_tecla(self,evento):
        if self.seleccionado and evento.type == pygame.KEYDOWN:
            self.ultima_tecla = evento.key
            self.mostrar_cursor = True
            self.ultimo_parpadeo = pygame.time.get_ticks()

            if evento.key == pygame.K_BACKSPACE:
                self.ultimo_borrado = pygame.time.get_ticks()
                if self.pos_cursor > 0:
                    self.valor = self.valor[:self.pos_cursor-1] + self.valor[self.pos_cursor:]
                    self.pos_cursor -= 1
            elif evento.key == pygame.K_RETURN:
                self.deseleccionar()
            elif evento.key == pygame.K_LEFT and self.pos_cursor > 0:
                self.pos_cursor -= 1
            elif evento.key == pygame.K_RIGHT and self.pos_cursor < len(self.valor):
                self.pos_cursor += 1
            elif evento.key == pygame.K_SPACE and not self.permitir_espacios:
                # No permitir espacios
                return True
            else:
                if (not self.limite_caracteres or len(self.valor) < self.limite_caracteres) and evento.unicode:
                    # Validar el carácter antes de agregarlo
                    if not self.validar_caracter(evento.unicode):
                        return True  # No agregar el carácter, ya se mostró el cartel
                    self.valor = self.valor[:self.pos_cursor] + evento.unicode + self.valor[self.pos_cursor:]
                    self.pos_cursor += 1
                    self.validar_texto()

            self.actualizar_texto()
            return True

    def mostrar_alerta(self, mensaje):
        """Muestra un mensaje de alerta en el cartel"""
        if self.cartel_alerta:
            # Posicionar el cartel cerca del campo de entrada
            cartel_x = self.rect.x
            cartel_y = self.rect.y - 110  # Sobre el campo de entrada
            self.cartel_alerta.x = cartel_x
            self.cartel_alerta.y = cartel_y
            self.cartel_alerta.rect = pygame.Rect(cartel_x, cartel_y, 
                                                self.cartel_alerta.ancho, 
                                                self.cartel_alerta.alto)
            self.cartel_alerta.boton_cerrar_rect = pygame.Rect(
                cartel_x + self.cartel_alerta.ancho - 30, 
                cartel_y + 10, 20, 20
            )
            self.cartel_alerta.mostrar(mensaje)
        
        # También cambiar color del borde para feedback visual
        self.color_borde_actual = (255, 0, 0)
        
    def validar_caracter(self, caracter):
        """Valida si un carácter es permitido"""
            # No permitir espacios
        if caracter.isspace() and not self.permitir_espacios:
            self.mostrar_alerta("¡Nombre no válido! Recuerda no utilizar números o caracteres especiales.")
            return False
            
            # No permitir números
        if caracter.isdigit() and not self.permitir_numeros:
            self.mostrar_alerta("¡Nombre no válido! Recuerda no utilizar números o caracteres especiales.")
            return False
            
            # Permitir letras y caracteres especiales básicos
        if not self.permitir_especiales and not caracter.isalpha():
            self.mostrar_alerta("¡Nombre no válido! Recuerda no utilizar números o caracteres especiales.")
            return False
        return caracter.isprintable()
        
        
    def validar_texto(self):
        texto = self.valor.strip()

        if len(texto) > self.limite_caracteres:
            self.texto_valido = False
            self.color_borde_actual = (255, 0, 0)
            return

        if len(texto) == 0:
            self.texto_valido = False
            self.color_borde_actual = (255, 0, 0)
            return
        
        if not self.permitir_espacios and ' ' in texto:
            self.texto_valido = False
            self.color_borde_actual = (255, 0, 0)
            return

        if not self.permitir_numeros and any(caracter.isdigit() for caracter in texto):
            self.texto_valido = False
            self.color_borde_actual = (255, 0, 0)
            return

        self.texto_valido = True
        self.color_borde_actual = self.color_borde
        return True
    
    def obtener_texto_validado(self):
        """Retorna el texto validado y limpio"""
        texto = self.valor.strip()
        if not self.permitir_espacios:
            texto = texto.replace(' ', '')
        if not self.permitir_numeros:
            texto = ''.join(c for c in texto if not c.isdigit())
        return texto
    
    def manejar_evento(self, evento):
        if not self.visible:
            return False
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if hasattr(evento, 'pos') and self.rect.collidepoint(evento.pos):
                self.sobre_el_elemento(False, lambda: self.mover_cursor(evento))
                return True
        self.procesar_tecla(evento)
        if self.seleccionado and evento.type == pygame.KEYUP:
            if evento.key == pygame.K_BACKSPACE:
                self.ultima_tecla = None
                self.ultimo_borrado = 0
            else:
                self.ultima_tecla = None

        return False

    def actualizar(self):
        ahora = pygame.time.get_ticks()

        if self.seleccionado and self.ultima_tecla == pygame.K_BACKSPACE:
            if self.ultimo_borrado != 0 and ahora - self.ultimo_borrado > self.retardo_inicial:
                if (ahora - self.ultimo_borrado) % self.tiempo_repeticion < 20:
                    if self.pos_cursor > 0:
                        self.valor = self.valor[:self.pos_cursor-1] + self.valor[self.pos_cursor:]
                        self.pos_cursor -= 1
                        self.actualizar_texto()
                    self.mostrar_cursor = True
                    self.ultimo_parpadeo = ahora
        elif ahora - self.ultimo_parpadeo > 500:
            self.mostrar_cursor = not self.mostrar_cursor
            self.ultimo_parpadeo = ahora

    def actualizar_texto(self):
        self.texto = self.valor
        self.prepar_texto()
        self.validar_texto()

        # Cambiar color del borde según validación
        if not self.texto_valido:
            self.color_borde_actual = (255, 0, 0)  # Rojo para error
        else:
            self.color_borde_actual = self.color_borde  # Color normal

    def dibujar(self):
        self.actualizar()
        super().dibujar()
        if self.seleccionado and self.mostrar_cursor:
            if self.valor:  # Solo si hay texto
                ancho_texto_parcial = self.fuente.render(self.valor[:self.pos_cursor], True, self.color_texto).get_width()
            else:
                ancho_texto_parcial = 0  # No hay nada escrito
            
            x_texto_inicial = self.rect_texto.x
            x_cursor = x_texto_inicial + ancho_texto_parcial
            y_inicio = self.rect.y + 5
            y_fin = self.rect.y + self.rect.height - 5
            pygame.draw.line(self.pantalla, self.color_texto, (x_cursor, y_inicio), (x_cursor, y_fin), 2)
    def verificar_hover(self, posicion_raton):
        return super().verificar_hover(posicion_raton)
class CartelAlerta:
    def __init__(self, pantalla, mensaje, x, y, ancho=500, alto=300, mostrar_boton_cerrar=True, duracion_ms=None): #====Jesua: añadido mostrar_boton_cerrar para la alerta de ronda finalizada, duracion_ms para temporizacion
            self.pantalla = pantalla
            self.mensaje = mensaje
            self.ancho = ancho
            self.alto = alto
            self.x = x
            self.y = y
            self.visible = False
            self.rect = pygame.Rect(x, y, ancho, alto)
            
            # Temporización automática
            self.duracion_ms = duracion_ms  # Duración en milisegundos (None = sin límite)
            self.tiempo_mostrado = None  # Marca cuando se mostró por primera vez
            
            # Colores
            self.color_fondo = constantes.ELEMENTO_FONDO_PRINCIPAL
            self.color_borde = constantes.ELEMENTO_BORDE_CUATERNARIO
            self.color_texto = constantes.COLOR_TEXTO_PRINCIPAL
            self.radio_borde = constantes.REDONDEO_NORMAL
            self.grosor_borde = constantes.BORDE_PRONUNCIADO
            
        #========Inicio Jesua========
            # Botón de cerrar (opcional)
            self.mostrar_boton_cerrar = mostrar_boton_cerrar
            self.boton_cerrar_rect = pygame.Rect(x + ancho - 30, y + 10, 20, 20)
            self.deshabilitado = False
            self.esta_hover = False
            
            # Preparar texto
            self.fuente = pygame.font.SysFont(constantes.FUENTE_LLAMATIVA, 50)
            self.preparar_texto()
        
    def preparar_texto(self):
            """Divide el mensaje en líneas, respetando saltos de línea '\n' y envolviendo palabras.

            Se procesa por párrafos separados por '\n' y para cada párrafo se realiza
            el wrap por palabras para no exceder el ancho del cartel.
            """
            lineas = []
            # Respetar saltos de línea explícitos
            parrafos = self.mensaje.split('\n') if isinstance(self.mensaje, str) else [str(self.mensaje)]

            for parrafo in parrafos:
                if parrafo == "":
                    # Mantener línea en blanco
                    lineas.append("")
                    continue
                palabras = parrafo.split(' ')
                linea_actual = ""
                for palabra in palabras:
                    prueba = f"{linea_actual} {palabra}".strip() if linea_actual else palabra
                    ancho_prueba = self.fuente.size(prueba)[0]
                    if ancho_prueba <= self.ancho - 20:  # Margen de 20px
                        linea_actual = prueba
                    else:
                        if linea_actual:
                            lineas.append(linea_actual)
                        linea_actual = palabra
                if linea_actual:
                    lineas.append(linea_actual)

            self.lineas = lineas

    def centrar_en_pantalla(self):
        ancho_pantalla = self.pantalla.get_width()
        alto_pantalla = self.pantalla.get_height()
        self.x = (ancho_pantalla - self.ancho) // 2
        self.y = (alto_pantalla - self.alto) // 2
        self.rect.topleft = (self.x, self.y)
        self.boton_cerrar_rect.topleft = (self.x + self.ancho - 30, self.y + 10)
        
    def mostrar(self, mensaje=None):
            """Muestra el cartel con un mensaje opcional"""
            if mensaje:
                self.mensaje = mensaje
                self.preparar_texto()
            self.centrar_en_pantalla()
            self.visible = True
            # Iniciar temporizador cuando se muestra
            if self.duracion_ms is not None:
                self.tiempo_mostrado = pygame.time.get_ticks()
        
    def ocultar(self):
            """Oculta el cartel"""
            self.visible = False
        
    def manejar_evento(self, evento):
            """Maneja eventos del ratón para cerrar el cartel"""
            if not self.visible:
                return False
                
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # Si el botón de cerrar está habilitado, permitir cerrar por click
                if self.mostrar_boton_cerrar and self.boton_cerrar_rect.collidepoint(evento.pos):
                    self.ocultar()
                    return True
                    
            return False
        
    def verificar_hover(self, posicion_raton):
            """Verifica hover sobre el botón de cerrar"""
            if not self.visible:
                return False
            if not self.mostrar_boton_cerrar:
                return False
            return self.boton_cerrar_rect.collidepoint(posicion_raton)
        
    def dibujar(self):
            """Dibuja el cartel de alerta"""
            if not self.visible:
                return
            
            # Verificar si debe ocultarse automáticamente
            if self.duracion_ms is not None and self.tiempo_mostrado is not None:
                tiempo_actual = pygame.time.get_ticks()
                if tiempo_actual - self.tiempo_mostrado >= self.duracion_ms:
                    self.ocultar()
                    return
                
            # Dibujar fondo y borde
            pygame.draw.rect(self.pantalla, self.color_fondo, self.rect, border_radius=self.radio_borde)
            pygame.draw.rect(self.pantalla, self.color_borde, self.rect, self.grosor_borde, border_radius=self.radio_borde)
            
            # Dibujar botón de cerrar (X) si está permitido
            if self.mostrar_boton_cerrar:
                pygame.draw.rect(self.pantalla, (255, 100, 100), self.boton_cerrar_rect, border_radius=5)
                pygame.draw.line(self.pantalla, (255, 255, 255), 
                                (self.boton_cerrar_rect.left + 5, self.boton_cerrar_rect.top + 5),
                                (self.boton_cerrar_rect.right - 5, self.boton_cerrar_rect.bottom - 5), 2)
                pygame.draw.line(self.pantalla, (255, 255, 255),
                                (self.boton_cerrar_rect.right - 5, self.boton_cerrar_rect.top + 5),
                                (self.boton_cerrar_rect.left + 5, self.boton_cerrar_rect.bottom - 5), 2)    
            #=======Fin Jesua========
            
            # --- CENTRAR EL TEXTO ---
            # Calcular altura total del bloque de texto
            total_text_height = 0
            text_surfaces = []
            for linea in self.lineas:
                surface = self.fuente.render(linea, True, self.color_texto)
                text_surfaces.append(surface)
                total_text_height += surface.get_height()
            total_text_height += 5 * (len(self.lineas) - 1)  # Espacio entre líneas

            # Coordenada Y inicial para centrar verticalmente
            y_texto = self.rect.y + (self.alto - total_text_height) // 2

            # Dibujar cada línea centrada horizontalmente
            for surface in text_surfaces:
                x_texto = self.rect.x + (self.ancho - surface.get_width()) // 2
                self.pantalla.blit(surface, (x_texto, y_texto))
                y_texto += surface.get_height() + 5
    def actualizar(self, eventos):
        """Método necesario para compatibilidad con tu sistema de botones"""
        if not self.visible or self.deshabilitado:
            return False
            
        for evento in eventos:
            if self.manejar_evento(evento):
                return True
        return False

    def dibujar_boton(self):
        """Método alias para compatibilidad - usa el mismo dibujar existente"""
        self.dibujar()

    def deshabilitar(self):
        """Método necesario para compatibilidad"""
        self.deshabilitado = True
        
    def habilitar(self):
        """Método necesario para compatibilidad"""
        self.deshabilitado = False

    # Tu método verificar_hover necesita una pequeña corrección:
    def verificar_hover(self, posicion_raton):
        """Verifica hover sobre el botón de cerrar"""
        if not self.visible:
            return False
            
        estaba_hover = self.esta_hover  # Necesitas el atributo esta_hover
        self.esta_hover = self.boton_cerrar_rect.collidepoint(posicion_raton)
        
        return self.esta_hover != estaba_hover

class BotonRadioImagenes(BotonRadio):
    """
    Botón de imagen con capacidad de arrastre y selección.
    Soporta click simple (selección) y arrastre (reordenamiento).
    """

    def __init__(self, un_juego, imagen, scala, x, y,
                 radio_borde=0, lift_offset=20, grupo=None,
                 valor=None, deshabilitado=False, accion=None,
                 color_borde=(0,0,0), color_borde_hover=(255,0,0),
                 color_borde_clicado=(0,255,0), mesa=None, arrastre_disponible=True):

        # Inicializar imagen y dimensiones
        self.imagen_original = imagen
        self.mesa = mesa
        self.scala = scala
        self.lift_offset = lift_offset
        self.prioridad = None
        self.seleccion_multiple = False

        if self.imagen_original:
            self.ancho = int(imagen.get_width() * scala)
            self.alto = int(imagen.get_height() * scala)
            self.imagen = pygame.transform.smoothscale(imagen, (self.ancho, self.alto))
        else:
            self.imagen = None
            self.ancho = 0
            self.alto = 0

        # Llamada a constructor base
        super().__init__(
            un_juego=un_juego,
            texto="",
            ancho=self.ancho,
            alto=self.alto,
            x=x,
            y=y,
            tamaño_fuente=0,
            fuente=None,
            color=(200, 200, 200),
            radio_borde=radio_borde,
            grupo=grupo,
            valor=valor,
            deshabilitado=deshabilitado,
            accion=accion,
            color_borde=color_borde,
            color_borde_hover=color_borde_hover,
            color_borde_clicado=color_borde_clicado
        )
        
        self.arrastre_disponible = arrastre_disponible

        # Estado de posición y arrastre
        self.y_base = self.y
        self.grosor_borde = 2
        self.arrastrando = False
        self.desplazamiento_x = 0
        self._posicion_raton_inicio_arrastre_x = None
        self._movio_durante_arrastre = False
        self._umbral_pixeles_arrastre = 6
        self.presionada = False
        self.arrastrada = False
        self.click_finalizado = False

        # Caché de ranuras del grupo
        self._limite_izquierdo_grupo = None
        self._limite_derecho_grupo = None
        self._ranuras_x_grupo = None
        self._centros_ranuras_grupo = None
        self._ancho_carta_grupo = self.ancho
        self._grupo_bloqueado = False

        # Asegurar color_borde_actual existe
        if not hasattr(self, 'color_borde_actual'):
            self.color_borde_actual = color_borde

    # ------------------ Gestión de Ranuras del Grupo ------------------

    def _obtener_limites_grupo(self):
        """Obtiene los límites izquierdo y derecho del grupo."""
        if not self.grupo:
            return None, None
        
        izquierdas = [getattr(b, "x", getattr(b, "rect", pygame.Rect(0,0,0,0)).x) for b in self.grupo]
        derechas = [getattr(b, "x", 0) + getattr(b, "ancho", 0) for b in self.grupo]
        
        if not izquierdas or not derechas:
            return None, None
        
        return min(izquierdas), max(derechas)

    def _intentar_usar_cache_ranuras(self, limite_izq, limite_der):
        """Intenta usar la caché de ranuras si es válida."""
        for miembro in self.grupo:
            if not getattr(miembro, "_grupo_bloqueado", False):
                continue
            
            ranuras = getattr(miembro, "_ranuras_x_grupo", None)
            lim_izq = getattr(miembro, "_limite_izquierdo_grupo", None)
            lim_der = getattr(miembro, "_limite_derecho_grupo", None)
            
            if (ranuras and len(ranuras) == len(self.grupo) and 
                lim_izq is not None and lim_der is not None and
                lim_izq <= limite_izq and lim_der >= limite_der):
                
                # Copiar caché válida
                self._limite_izquierdo_grupo = miembro._limite_izquierdo_grupo
                self._limite_derecho_grupo = miembro._limite_derecho_grupo
                self._ranuras_x_grupo = miembro._ranuras_x_grupo.copy()
                self._centros_ranuras_grupo = miembro._centros_ranuras_grupo.copy()
                self._ancho_carta_grupo = miembro._ancho_carta_grupo
                self._grupo_bloqueado = True
                return True
        return False

    def _calcular_ranuras(self, limite_izq, limite_der):
        """Calcula las ranuras y centros para el grupo."""
        cantidad = len(self.grupo)
        ancho_carta = self._ancho_carta_grupo or (self.ancho if self.ancho > 0 else 1)
        
        if cantidad == 1:
            ranuras_x = [limite_izq]
        else:
            izquierda_primera = limite_izq
            izquierda_ultima = limite_der - ancho_carta
            rango_total = izquierda_ultima - izquierda_primera
            espaciado = rango_total / (cantidad - 1) if (cantidad - 1) > 0 else 0
            ranuras_x = [int(izquierda_primera + i * espaciado) for i in range(cantidad)]
        
        centros_ranuras = [pos_x + ancho_carta // 2 for pos_x in ranuras_x]
        return ranuras_x, centros_ranuras, ancho_carta

    def _aplicar_posiciones_ranuras(self):
        """Aplica las posiciones de ranuras a los miembros del grupo que no están arrastrando."""
        for idx, miembro in enumerate(self.grupo):
            if not miembro.arrastrando and not getattr(miembro, "seleccionado", False):
                miembro.x = miembro._ranuras_x_grupo[idx]
                miembro.y = getattr(miembro, "y_base", getattr(miembro, "y", miembro.y))

    def asegurar_ranuras_grupo(self):
        """Asegura que las ranuras del grupo estén actualizadas. Usa caché si es válida."""
        if not self.grupo:
            return
        
        limite_izq, limite_der = self._obtener_limites_grupo()
        if limite_izq is None or limite_der is None:
            return
        
        # Intentar usar caché existente
        if self._intentar_usar_cache_ranuras(limite_izq, limite_der):
            self._aplicar_posiciones_ranuras()
            return
        
        # Recalcular ranuras
        ranuras_x, centros_ranuras, ancho_carta = self._calcular_ranuras(limite_izq, limite_der)
        
        # Asignar caché a todos los miembros
        for miembro in self.grupo:
            miembro._limite_izquierdo_grupo = limite_izq
            miembro._limite_derecho_grupo = limite_der
            miembro._ranuras_x_grupo = ranuras_x.copy()
            miembro._centros_ranuras_grupo = centros_ranuras.copy()
            miembro._ancho_carta_grupo = ancho_carta
            miembro._grupo_bloqueado = True
        
        self._aplicar_posiciones_ranuras()
    def invalidar_ranuras_grupo(self):
        """Marca la caché de ranuras como inválida para forzar recálculo."""
        if not self.grupo:
            return
        for miembro in self.grupo:
            miembro._grupo_bloqueado = False
            # Limpiar atributos de caché
            for attr in ["_ranuras_x_grupo", "_centros_ranuras_grupo", 
                        "_limite_izquierdo_grupo", "_limite_derecho_grupo"]:
                if hasattr(miembro, attr):
                    delattr(miembro, attr)

    def obtener_indice_ranura_para_centro(self, centro_x):
        """Obtiene el índice de la ranura más cercana al centro_x dado."""
        if not self._centros_ranuras_grupo:
            return None
        return min(range(len(self._centros_ranuras_grupo)),
                   key=lambda i: abs(self._centros_ranuras_grupo[i] - centro_x))

    # ------------------ Dibujo ------------------

    def dibujar(self):
        if not self.visible:
            return
        
        # SINCRONIZAR: self.rect con self.x y self.y
        self.rect.x = self.x
        self.rect.y = self.y
        
        pygame.draw.rect(self.pantalla, self.color_borde_actual, self.rect,
                         width=self.grosor_borde, border_radius=self.radio_borde)
        
        if self.imagen:
            rect_imagen = self.imagen.get_rect(center=self.rect.center)
            self.pantalla.blit(self.imagen, rect_imagen)
            
        if self.deshabilitado:
            superposicion = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
            superposicion.fill((100, 100, 100, 120))
            self.pantalla.blit(superposicion, self.rect.topleft)

    # ------------------ Manejo de Eventos ------------------

    def _verificar_prioridad_click(self, posicion_raton):
        """Verifica si esta carta tiene la mayor prioridad en el click."""
        if not self.grupo:
            return True
        candidatos = [b for b in self.grupo if b.rect.collidepoint(posicion_raton)]
        if not candidatos:
            return True
        candidatos.sort(key=lambda b: (b.prioridad if b.prioridad is not None else -10**9), reverse=True)
        return candidatos[0] is self

    def _inicializar_arrastre(self, posicion_raton):
        """Inicializa el estado de arrastre."""
        self.presionada = True
        self.arrastrada = False
        self.click_finalizado = False
        self.arrastrando = True
        self._posicion_raton_inicio_arrastre_x = posicion_raton[0]
        self._movio_durante_arrastre = False
        self.desplazamiento_x = posicion_raton[0] - self.x

    def _mover_carta_durante_arrastre(self, posicion_raton):
        """Mueve la carta durante el arrastre respetando límites."""
        if self._grupo_bloqueado:
            limite_izq = self._limite_izquierdo_grupo
            limite_der = self._limite_derecho_grupo - self._ancho_carta_grupo
            nuevo_x = max(limite_izq, min(posicion_raton[0] - self.desplazamiento_x, limite_der))
            self.x = int(nuevo_x)
        else:
            self.x = posicion_raton[0] - self.desplazamiento_x

    def _intercambiar_posicion_en_grupo(self, indice_nuevo):
        """Intercambia la posición de esta carta en el grupo y actualiza referencias."""
        if not self.grupo or not self.mesa:
            return
        
        indice_actual = self.grupo.index(self)
        if indice_nuevo == indice_actual:
            return
        
        # Reorganizar grupo
        self.grupo.pop(indice_actual)
        self.grupo.insert(indice_nuevo, self)
        
        # Actualizar referencias en la mesa
        if hasattr(self.mesa, 'referencia_elementos') and hasattr(self.mesa, 'mesa'):
            elementos = self.mesa.referencia_elementos.get("elementos_mis_cartas", [])
            for elemento in elementos:
                if elemento in self.mesa.mesa.botones:
                    self.mesa.mesa.botones.remove(elemento)
            self.mesa.referencia_elementos["elementos_mis_cartas"] = list(self.grupo)
            for elemento in self.mesa.referencia_elementos["elementos_mis_cartas"]:
                self.mesa.mesa.botones.append(elemento)
        
        # Recalcular ranuras y actualizar prioridades
        self._recalcular_ranuras_durante_arrastre()
        for i, miembro in enumerate(self.grupo):
            miembro.prioridad = i

    def _recalcular_ranuras_durante_arrastre(self):
        """Recalcula las ranuras durante el arrastre."""
        cantidad = len(self.grupo)
        izquierda_primera = self._limite_izquierdo_grupo
        izquierda_ultima = self._limite_derecho_grupo - self._ancho_carta_grupo
        rango_total = izquierda_ultima - izquierda_primera
        espaciado = rango_total / (cantidad - 1) if (cantidad - 1) > 0 else 0
        ranuras_x = [int(izquierda_primera + i * espaciado) for i in range(cantidad)]
        centros_ranuras = [pos_x + self._ancho_carta_grupo // 2 for pos_x in ranuras_x]
        
        for miembro in self.grupo:
            miembro._ranuras_x_grupo = ranuras_x.copy()
            miembro._centros_ranuras_grupo = centros_ranuras.copy()
            miembro._grupo_bloqueado = True
        
        # Mover cartas no arrastrando a sus nuevas ranuras
        for indice, miembro in enumerate(self.grupo):
            if miembro is not self:
                miembro.x = miembro._ranuras_x_grupo[indice]

    def _procesar_movimiento_raton(self, evento):
        """Procesa el evento de movimiento del ratón."""
        # Si hay selección múltiple, deshabilitar el arrastre completamente
        if self.seleccion_multiple:
            return False
        
        if not (self.presionada and not self.click_finalizado):
            return False
        if self._posicion_raton_inicio_arrastre_x is None:
            return False
        
        delta_x = evento.pos[0] - self._posicion_raton_inicio_arrastre_x
        
        if abs(delta_x) > self._umbral_pixeles_arrastre:
            self.arrastrada = True
            self._mover_carta_durante_arrastre(evento.pos)
            
            centro = self.x + (self.ancho // 2)
            indice_mas_cercano = self.obtener_indice_ranura_para_centro(centro)
            
            if indice_mas_cercano is not None and self.grupo:
                self._intercambiar_posicion_en_grupo(indice_mas_cercano)
                # Actualizar desplazamiento después del intercambio
                self.desplazamiento_x = evento.pos[0] - self.x
            
            if self.seleccionado:
                self.y = self.y_base - self.lift_offset
        
        return True

    def _verificar_puede_procesar_soltar(self, evento):
        """Verifica si esta carta puede procesar el evento de soltar."""
        if not self.presionada:
            return False
        
        # Con selección múltiple, solo verificar que el ratón esté sobre la carta
        if self.seleccion_multiple:
            if hasattr(evento, 'pos') and not self.rect.collidepoint(evento.pos):
                self.presionada = False
                return False
            return True
        
        # Sin selección múltiple, verificar arrastre
        if self.grupo and hasattr(evento, 'pos'):
            otra_arrastrando = any(b.arrastrando for b in self.grupo if b is not self)
            if not self.arrastrando and otra_arrastrando:
                self.presionada = False
                return False
            if not self.arrastrando and not self.rect.collidepoint(evento.pos):
                self.presionada = False
                return False
        
        return True

    def _aplicar_posicion_final(self):
        """Aplica la posición final según las ranuras."""
        if self._ranuras_x_grupo and self.grupo:
            try:
                indice = self.grupo.index(self)
                self.x = int(self._ranuras_x_grupo[indice])
            except ValueError:
                pass

    def _limpiar_estado_arrastre(self):
        """Limpia todas las banderas de estado de arrastre."""
        self.presionada = False
        self.arrastrada = False
        self.arrastrando = False
        self.click_finalizado = True
        self._posicion_raton_inicio_arrastre_x = None
        self._movio_durante_arrastre = False
        if hasattr(self, "_indice_ranura_arrastre"):
            delattr(self, "_indice_ranura_arrastre")
        if hasattr(self, "_ultima_carta_intercambiada_valor"):
            delattr(self, "_ultima_carta_intercambiada_valor")

    def _procesar_soltar_boton(self, evento):
        """Procesa el evento de soltar el botón."""
        if not self._verificar_puede_procesar_soltar(evento):
            return False
        
        # Si hay selección múltiple, solo seleccionar/deseleccionar sin arrastre
        if self.seleccion_multiple:
            # Alternar basándose en el estado inicial guardado al hacer click
            estado_inicial = getattr(self, '_estado_seleccion_inicial', self.seleccionado)
            if estado_inicial:
                # Estaba seleccionada, deseleccionar
                self.deseleccionar()
            else:
                # No estaba seleccionada, seleccionar
                self.seleccionar()
            # Limpiar atributo temporal
            if hasattr(self, '_estado_seleccion_inicial'):
                delattr(self, '_estado_seleccion_inicial')
            self.presionada = False
            return True
        
        # Calcular distancia para determinar si fue click o arrastre
        distancia_total = 0
        if hasattr(evento, 'pos') and self._posicion_raton_inicio_arrastre_x is not None:
            distancia_total = abs(evento.pos[0] - self._posicion_raton_inicio_arrastre_x)
        
        fue_click_simple = distancia_total <= self._umbral_pixeles_arrastre
        
        # Aplicar posición final
        self._aplicar_posicion_final()
        
        # Aplicar lógica según tipo de interacción
        if fue_click_simple:
            self.seleccionar()
        else:
            self.seleccionado = True
            self.color_borde_actual = self.color_borde_clicado
            self.y = self.y_base
            if not self.seleccion_multiple and self.grupo:
                for boton in self.grupo:
                    if boton is not self:
                        boton.deseleccionar()
        
        # Actualizar prioridades y limpiar estado
        if self.grupo:
            for i, miembro in enumerate(self.grupo):
                miembro.prioridad = i
        
        self._limpiar_estado_arrastre()
        return True

    def manejar_evento(self, evento):
        if not self.visible or self.deshabilitado:
            return False
            
        if self.grupo:
            self.asegurar_ranuras_grupo()

        # Presionar botón
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if hasattr(evento, 'pos') and self.rect.collidepoint(evento.pos):
                if not self._verificar_prioridad_click(evento.pos):
                    self.presionada = False
                    return False
                
                # Limpiar estado de otras cartas solo si NO hay selección múltiple
                if self.grupo and not self.seleccion_multiple:
                    for boton in self.grupo:
                        if boton is not self:
                            boton.presionada = False
                            boton.deseleccionar()
                elif self.grupo:
                    # Con selección múltiple, solo limpiar estado de presionada
                    for boton in self.grupo:
                        if boton is not self:
                            boton.presionada = False
                
                # Solo inicializar arrastre si NO hay selección múltiple
                if not self.seleccion_multiple and self.arrastre_disponible:
                    self._inicializar_arrastre(evento.pos)
                    self.seleccionar()
                else:
                    # Con selección múltiple, solo marcar como presionada
                    # Guardar el estado inicial de selección para alternar al soltar
                    self.presionada = True
                    self.arrastrando = False  # Deshabilitar arrastre
                    self._estado_seleccion_inicial = self.seleccionado
                    # NO seleccionar aquí, se hará al soltar
                
                return True
        
        # Movimiento del ratón
        if evento.type == pygame.MOUSEMOTION:
            return self._procesar_movimiento_raton(evento)
        
        # Soltar botón
        if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            return self._procesar_soltar_boton(evento)
        
        return False

    # ------------------ Selección / Deselección ------------------

    def seleccionar(self):
        """Selecciona esta carta y deselecciona las demás si no hay selección múltiple."""
        if not self.seleccion_multiple and self.grupo:
            for boton in self.grupo:
                if boton != self:
                    boton.deseleccionar()
        
        self.seleccionado = True
        self.color_borde_actual = self.color_borde_clicado
        self.y = self.y_base - self.lift_offset

    def deseleccionar(self):
        """Deselecciona esta carta y la baja a su posición normal."""
        self.seleccionado = False
        self.color_borde_actual = self.color_borde
        self.y = self.y_base
class BotonLogoMenu(Boton):
    def __init__(self, un_juego, x, y, ancho=40, alto=30,
                 radio_borde=5, deshabilitado=False, accion=None,
                 color_rayas=(0, 0, 0), color_rayas_hover=(100, 100, 255),
                 color_rayas_clicado=(0, 255, 0), grosor_raya=3,
                 espacio_rayas=5, **kwargs):
        
        # Llamar al constructor de Boton
        super().__init__(
            un_juego=un_juego,
            texto="",  # Sin texto
            ancho=ancho,
            alto=alto,
            x=x,
            y=y,
            tamaño_fuente=0,
            fuente=None,
            color=(240, 240, 240),  # Fondo claro
            radio_borde=radio_borde,
            color_texto=(0, 0, 0),
            color_borde=(150, 150, 150),
            color_borde_hover=(100, 100, 255),
            color_borde_clicado=(0, 255, 0),
            accion=accion,
            deshabilitado=deshabilitado,
            **kwargs
        )
        
        # Atributos específicos del logo de menú
        self.color_rayas = color_rayas
        self.color_rayas_hover = color_rayas_hover
        self.color_rayas_clicado = color_rayas_clicado
        self.grosor_raya = grosor_raya
        self.espacio_rayas = espacio_rayas
        self.color_rayas_actual = color_rayas

    def dibujar(self):
        if not self.visible:
            return

        # Dibujar fondo y borde (comportamiento normal del botón)
        super().dibujar()

        # Calcular posición de las rayas (centradas)
        margen_vertical = self.alto * 0.2
        ancho_rayas = self.ancho * 0.6
        x_rayas = self.rect.centerx - ancho_rayas / 2
        espacio_total = self.alto - (2 * margen_vertical)
        espacio_entre_rayas = espacio_total / 3

        # Determinar color de las rayas según el estado
        if self.deshabilitado:
            color_raya = (150, 150, 150)  # Gris para deshabilitado
        elif self.presionado:
            color_raya = self.color_rayas_clicado
        elif self.esta_hover:
            color_raya = self.color_rayas_hover
        else:
            color_raya = self.color_rayas

        # Dibujar las tres rayas
        for i in range(3):
            y_raya = self.rect.y + margen_vertical + (i * espacio_entre_rayas)
            inicio = (x_rayas, y_raya)
            fin = (x_rayas + ancho_rayas, y_raya)
            pygame.draw.line(self.pantalla, color_raya, inicio, fin, self.grosor_raya)

    def verificar_hover(self, posicion_raton):
        """Actualiza el estado de hover y devuelve si cambió"""
        cambio = super().verificar_hover(posicion_raton)
        return cambio

    def manejar_evento(self, evento):
        """Maneja eventos del botón menú"""
        return super().manejar_evento(evento)