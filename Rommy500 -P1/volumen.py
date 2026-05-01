import pygame

class ControlVolumen:
    def __init__(self, x=950, y=20):
        self.rects = []
        # Niveles de volumen
        self.niveles = [0.0, 0.15, 0.25, 0.50, 0.75, 1.0]
        self.nivel_actual = 3 
        self.clic_previo = False 
        
        # Configuración Visual
        self.ancho_btn = 20
        self.alto_btn = 30
        self.espacio = 5
        self.color_activo = (50, 205, 50)     # Verde
        self.color_inactivo = (80, 80, 80)    # Gris oscuro
        self.color_borde = (0, 0, 0)          # Negro
        
        # Generar las cajas
        for i in range(len(self.niveles)):
            pos_x = x + (i * (self.ancho_btn + self.espacio))
            rect = pygame.Rect(pos_x, y, self.ancho_btn, self.alto_btn)
            self.rects.append(rect)
            
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
            for i, rect in enumerate(self.rects):
                if rect.collidepoint(mouse_pos):
                    self.nivel_actual = i
                    self.aplicar_volumen()
                    break 
        self.clic_previo = click

        # 2. DIBUJADO DE LOS BOTONES
        for i, rect in enumerate(self.rects):
            color = self.color_activo if i <= self.nivel_actual else self.color_inactivo
            pygame.draw.rect(pantalla, color, rect)
            pygame.draw.rect(pantalla, self.color_borde, rect, 2)

        # 3. ACTUALIZACIÓN PARCIAL (LA SOLUCIÓN MAGICA)
        # Esto le dice a Pygame: "Muestra YA estos rectángulos, no toques el resto de la pantalla".
        pygame.display.update(self.rects)