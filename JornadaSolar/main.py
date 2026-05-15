"""
JORNADA SOLAR - MAIN (State Manager)
Gerenciador central de janela única.
Mantém o ShowBase vivo e alterna apenas as telas (Estados).
"""

from direct.showbase.ShowBase import ShowBase
from screens.settings_screen import SettingsScreen
from core.save_manager import SaveManager
from core.sound_manager import SoundManager
from core.resource_loader import ResourceLoader
import sys

class JornadaSolarApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        self.save_manager = SaveManager()
        
        self.resource_loader = ResourceLoader(
            self.loader, 
            self.sfxManagerList[0], 
            self.musicManager
        )
        self.sound_manager = SoundManager(self.resource_loader, self.save_manager)
        
        self.current_state = None
        self.change_state("menu")

    def change_state(self, new_state_name, level_config=None):
        """
        Troca a tela do jogo sem fechar a janela.
        """
        state_key = new_state_name.upper()
        print(f"\nTrocando estado para: {state_key}")
        
        if self.current_state is not None:
            if hasattr(self.current_state, 'cleanup'):
                self.current_state.cleanup()
            self.current_state = None

        if state_key == "MENU":
            from screens.main_menu import MainMenu
            self.current_state = MainMenu(self)
            
        elif state_key == "CONFIGURACOES":
            self.current_state = SettingsScreen(
                base=self, 
                sound_manager=self.sound_manager, 
                back_callback=lambda: self.change_state("MENU")
            )
            
        elif state_key == "LOBBY":
            from screens.lobby_3d import Lobby3D
            self.current_state = Lobby3D(self)
            
        elif state_key.startswith("FASE_"):
            from levels.specific_levels import level_classes
            planet_name = new_state_name.lower().replace("fase_", "")
            
            if planet_name in level_classes:
                self.current_state = level_classes[planet_name](app=self)
                self.current_state.start_level()
            else:
                print(f"Fase não encontrada: {planet_name}")
                self.change_state("LOBBY")
                
        elif state_key == "SAIR":
            sys.exit(0)

if __name__ == "__main__":
    app = JornadaSolarApp()
    app.run()