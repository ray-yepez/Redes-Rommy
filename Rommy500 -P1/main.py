import pygame
import sys
from ui import UIManager
from network import NetworkManager


def main():
    pygame.init()
    
    SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
    network_manager = NetworkManager()
    ui_manager = UIManager(SCREEN_WIDTH, SCREEN_HEIGHT, network_manager)

    pygame.mixer.init()  
    pygame.mixer.music.load("assets/sonido/musica_fondo.mp3")  
    pygame.mixer.music.play(-1)

    running = True
    while running:
        result = ui_manager.handle_events()
        if result == "launch_ui2":
            if network_manager.is_host:
                jugadores = network_manager.connected_players
                print(f"Inicializando juego con {len(jugadores)}")
                # Para verificar que el network_manager siga ejecutándose
                network_manager.running = True

                import ui2
                # Pasa el objeto network_manager que contiene el estado de la conexión
                ui2.main(network_manager)
                ui_manager.current_screen = "main"
                
                # Resetear estado para próxima partida
                network_manager.game_started = False
                continue
            else:
                # Para verificar que el network_manager siga ejecutándose
                network_manager.running = True
                
                import ui2
                # Pasa el objeto network_manager que contiene el estado de la conexión
                ui2.main(network_manager)
                ui_manager.current_screen = "main"
                
                # Resetear estado para próxima partida
                network_manager.game_started = False
                continue
                
        elif result is False:
            running = False
        else:
            ui_manager.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
{
    
}