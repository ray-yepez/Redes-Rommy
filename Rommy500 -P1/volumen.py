import pygame

class ControlVolumen:
    def __init__(self, x=1000, y=0):
        # Niveles de volumen
        self.niveles = [0.0, 0.33, 0.66, 1.0]
        self.nivel_actual = 2 
        self.nivel_anterior = -1  # Para detectar cambios (inicial diferente para forzar primera actualización)
        self.clic_previo = False 
        
        # Configuración Visual
        self.x = x
        self.y = y
        self.ancho_icono = 420
        self.alto_icono = 110
        
        # Cargar imágenes de volumen (Windows 10 style)
        # ENLAZA TUS IMÁGENES AQUÍ:
        # - icono_mudo.png: volumen 0 (mudo)
        # - icono_1_rayita.png: volumen 1 (bajo)
        # - icono_2_rayitas.png: volumen 2 (medio)
        # - icono_3_rayitas.png: volumen 3 (alto)
        try:
            self.icono_mudo = pygame.image.load("assets/volumen/icono_mudo.png.png")
            self.icono_1 = pygame.image.load("assets/volumen/icono_1_rayitas.png.png")
            self.icono_2 = pygame.image.load("assets/volumen/icono_2_rayitas.png.png")
            self.icono_3 = pygame.image.load("assets/volumen/icono_3_rayitas.png.png")
            
            # Escalar imágenes al tamaño deseado
            self.icono_mudo = pygame.transform.scale(self.icono_mudo, (self.ancho_icono, self.alto_icono))
            self.icono_1 = pygame.transform.scale(self.icono_1, (self.ancho_icono, self.alto_icono))
            self.icono_2 = pygame.transform.scale(self.icono_2, (self.ancho_icono, self.alto_icono))
            self.icono_3 = pygame.transform.scale(self.icono_3, (self.ancho_icono, self.alto_icono))
            
            self.iconos = [self.icono_mudo, self.icono_1, self.icono_2, self.icono_3]
            self.imagenes_cargadas = True
        except:
            print("Error: No se pudieron cargar las imágenes de volumen. Asegúrate de colocar las imágenes en assets/volumen/")
            self.imagenes_cargadas = False
            
        # Rectángulo para detectar clics
        self.rect = pygame.Rect(x, y, self.ancho_icono, self.alto_icono)
            
        self.aplicar_volumen()

    def aplicar_volumen(self):
        try:
            vol = self.niveles[self.nivel_actual]
            pygame.mixer.music.set_volume(vol)
        except:
            pass

    def actualizar_y_dibujar(self):
        pantalla = pygame.display.get_surface()
        if not pantalla: return 

        # 1. LÓGICA DE MOUSE
        mouse_pos = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0] 

        if click and not self.clic_previo:
            if self.rect.collidepoint(mouse_pos):
                # Ciclar entre los 4 niveles de volumen
                self.nivel_actual = (self.nivel_actual + 1) % len(self.niveles)
                self.aplicar_volumen()
        self.clic_previo = click

        # 2. DIBUJADO DEL ICONO DE VOLUMEN
        if self.imagenes_cargadas:
            # Mostrar el icono correspondiente al nivel actual
            icono_actual = self.iconos[self.nivel_actual]
            pantalla.blit(icono_actual, (self.x, self.y))
        else:
            # Fallback: dibujar un rectángulo si no hay imágenes
            color = (50, 205, 50) if self.nivel_actual > 0 else (80, 80, 80)
            pygame.draw.rect(pantalla, color, self.rect)
            pygame.draw.rect(pantalla, (0, 0, 0), self.rect, 2)