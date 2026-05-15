"""
JORNADA SOLAR - ACHIEVEMENTS SCREEN
Tela de conquistas desbloqueáveis
"""

from direct.gui.DirectGui import DirectFrame, DirectButton, DirectScrolledFrame
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import Vec4, TextNode


class AchievementsScreen:
    """Tela de conquistas"""
    
    def __init__(self, base, back_callback):
        """
        Inicializa tela de conquistas
        
        Args:
            base: ShowBase instance
            back_callback: Função para voltar
        """
        self.base = base
        self.back_callback = back_callback
        
        from core.constants import ACHIEVEMENTS
        from core.save_manager import SaveManager
        
        self.save_manager = SaveManager()
        
        # Frame principal
        self.frame = DirectFrame(
            frameSize=(-2, 2, -2, 2),
            frameColor=(0.02, 0.02, 0.1, 0.98)
        )
        
        # Título
        self.title = OnscreenText(
            text="CONQUISTAS",
            pos=(0, 0.85),
            scale=0.1,
            fg=Vec4(1, 0.84, 0, 1),
            align=TextNode.ACenter,
            parent=self.frame,
            shadow=(0.05, 0.05)
        )
        
        # Progresso
        progress = self.save_manager.get_achievement_progress()
        progress_text = f"{progress['unlocked']}/{progress['total']} Desbloqueadas ({progress['percentage']:.0f}%)"
        
        self.progress = OnscreenText(
            text=progress_text,
            pos=(0, 0.7),
            scale=0.05,
            fg=Vec4(0.5, 1, 0.5, 1),
            align=TextNode.ACenter,
            parent=self.frame
        )
        
        # Lista de conquistas
        y_pos = 0.55
        spacing = 0.15
        
        for i, (key, data) in enumerate(ACHIEVEMENTS.items()):
            if i >= 8:  # Limita a 8 conquistas visíveis
                break
            
            y = y_pos - (i * spacing)
            
            is_unlocked = self.save_manager.is_achievement_unlocked(key)
            
            if is_unlocked:
                icon = data['icon']
                name = data['name']
                desc = data['description']
                color = Vec4(1, 1, 1, 1)
            else:
                icon = "🔒"
                name = "???"
                desc = "Conquista bloqueada"
                color = Vec4(0.5, 0.5, 0.5, 1)
            
            # Frame da conquista
            ach_frame = DirectFrame(
                frameSize=(-0.8, 0.8, -0.06, 0.06),
                frameColor=(0.1, 0.1, 0.2, 0.8),
                pos=(0, 0, y),
                parent=self.frame
            )
            
            # Ícone e nome
            achievement_text = OnscreenText(
                text=f"{icon} {name}",
                pos=(-0.7, -0.02),
                scale=0.045,
                fg=color,
                align=TextNode.ALeft,
                parent=ach_frame
            )
            
            # Descrição
            desc_text = OnscreenText(
                text=desc,
                pos=(-0.7, -0.05),
                scale=0.035,
                fg=Vec4(0.7, 0.7, 0.7, 1),
                align=TextNode.ALeft,
                parent=ach_frame
            )
        
        # Botão voltar
        self.btn_back = DirectButton(
            text="VOLTAR",
            text_scale=0.06,
            scale=0.12,
            pos=(0, 0, -0.85),
            command=self.go_back,
            frameColor=(0.3, 0.3, 0.5, 0.9),
            text_fg=Vec4(1, 1, 1, 1),
            relief=1,
            pressEffect=1,
            parent=self.frame
        )
    
    def go_back(self):
        """Volta ao menu"""
        self.cleanup()
        self.back_callback()
    
    def cleanup(self):
        """Remove a tela"""
        if self.frame:
            self.frame.destroy()