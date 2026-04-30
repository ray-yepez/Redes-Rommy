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

    # pasamos los eventos como argumento:
    def actualizar_y_dibujar(self, eventos):
        pantalla = pygame.display.get_surface()
        if not pantalla: return 

        mouse_pos = pygame.mouse.get_pos()
        
        # 1. LÓGICA DE MOUSE BASADA EN EVENTOS (Evita saturar el CPU)
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1: # Clic izquierdo
                for i, rect in enumerate(self.rects):
                    if rect.collidepoint(mouse_pos):
                        self.nivel_actual = i
                        self.aplicar_volumen()
                        break 

        # 2. DIBUJADO DE LOS BOTONES
        for i, rect in enumerate(self.rects):
            color = self.color_activo if i <= self.nivel_actual else self.color_inactivo
            pygame.draw.rect(pantalla, color, rect)
            pygame.draw.rect(pantalla, self.color_borde, rect, 2)
        
        #En el paso 3, se utilizaba pygame.display.update(self.rects) definiéndolo como "LA SOLUCIÓN MAGICA".
#El error: Aunque la actualización parcial (Dirty Rectangles) es una técnica excelente para optimizar rendimiento, entra en conflicto directo si en la clase de la UI (ui_manager.update()) utiliza paralelamente pygame.display.flip() u otro actualizador de pantalla completa. Tener dos órdenes de refresco distintas peleando por el buffer de video en hardware gráfico integrado genera un parpadeo severo (flickering) y caídas de cuadros. Estas caídas de fotogramas congelan momentáneamente el envío de paquetes (el send_atomic que tenemos en la red).
#La solución: El control de volumen solo debe encargarse de dibujar los rectángulos sobre la superficie de la pantalla. Eliminamos por completo la línea pygame.display.update(self.rects). La orden de actualizar la pantalla debe ser única y residir exclusivamente al final del bucle principal while running: en main.py.