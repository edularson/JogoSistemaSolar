"""
JORNADA SOLAR - OBJECTIVES SCREEN
Tela de objetivos exibida antes de cada fase
"""

from direct.gui.DirectGui import DirectFrame, DirectButton
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import Vec4, TextNode


class ObjectivesScreen:
    """Tela de objetivos pré-fase"""
    
    def __init__(self, base, level_config: dict, start_callback, back_callback):
        """
        Inicializa tela de objetivos
        
        Args:
            base: ShowBase instance
            level_config: Configuração da fase
            start_callback: Função para iniciar fase
            back_callback: Função para voltar
        """
        self.base = base
        self.config = level_config
        self.start_callback = start_callback
        self.back_callback = back_callback
        
        # Cria overlay
        self.frame = DirectFrame(
            frameSize=(-2, 2, -2, 2),
            frameColor=(0.02, 0.02, 0.1, 0.98)
        )
        
        # Título da fase
        self.title = OnscreenText(
            text=f"*** {level_config['display_name'].upper()} ***",
            pos=(0, 0.75),
            scale=0.12,
            fg=Vec4(1, 0.84, 0, 1),
            align=TextNode.ACenter,
            parent=self.frame
        )
        self.title.setShadow((0.05, 0.05, 0, 0))
        
        # Subtítulo
        self.subtitle = OnscreenText(
            text=level_config['subtitle'],
            pos=(0, 0.62),
            scale=0.06,
            fg=Vec4(0.8, 0.8, 1.0, 1),
            align=TextNode.ACenter,
            parent=self.frame
        )
        
        # Objetivo principal
        objective_text = f"OBJETIVO: Coletar {level_config['objective_count']} fragmentos"
        self.objective = OnscreenText(
            text=objective_text,
            pos=(0, 0.45),
            scale=0.055,
            fg=Vec4(0.5, 1, 0.5, 1),
            align=TextNode.ACenter,
            parent=self.frame
        )
        
        # Descrição da fase
        self.description = OnscreenText(
            text=level_config['description'],
            pos=(0, 0.3),
            scale=0.05,
            fg=Vec4(1, 1, 1, 1),
            align=TextNode.ACenter,
            parent=self.frame,
            wordwrap=30
        )
        
        # Mecânica especial
        mechanic = level_config.get('special_mechanic', 'Nenhuma')
        if mechanic and mechanic != 'None':
            mechanic_names = {
                'wind': '💨 Ventos Laterais',
                'lightning': '⚡ Raios Elétricos',
                'corrupted_fragments': '☣️ Fragmentos Corrompidos',
                'space_trash': '🛸 Lixo Espacial',
                'acid_rain': '☣️ Chuva Ácida',
                'extreme_speed': '⚡ Velocidade Extrema',
                'solar_eruption': '☀️ Erupções Solares (BOSS)'
            }
            
            mechanic_text = f"Mecanica: {mechanic_names.get(mechanic, mechanic)}"
        else:
            mechanic_text = "Mecanica: Coleta Basica"
        
        self.mechanic = OnscreenText(
            text=mechanic_text,
            pos=(0, 0.15),
            scale=0.05,
            fg=Vec4(1, 0.7, 0.3, 1),
            align=TextNode.ACenter,
            parent=self.frame
        )
        
        # Dica
        tip_text = f"DICA: {level_config['tip']}"
        self.tip = OnscreenText(
            text=tip_text,
            pos=(0, 0.0),
            scale=0.045,
            fg=Vec4(1, 1, 0.5, 1),
            align=TextNode.ACenter,
            parent=self.frame,
            wordwrap=35
        )
        
        # Controles (se for tutorial)
        if level_config['name'] == 'netuno':
            controls_text = """
CONTROLES:
A/D - Mover Horizontalmente
W/S - Mover Verticalmente
P - Pausar
ESC - Sair
            """
            self.controls = OnscreenText(
                text=controls_text.strip(),
                pos=(0, -0.3),
                scale=0.04,
                fg=Vec4(0.8, 0.8, 0.8, 1),
                align=TextNode.ACenter,
                parent=self.frame
            )
        
        # Botão JOGAR
        self.btn_start = DirectButton(
            text=">>> INICIAR FASE <<<",
            text_scale=0.07,
            scale=1,
            pos=(0, 0, -0.6),
            command=self.start_level,
            frameColor=(0.2, 0.6, 0.2, 0.9),
            text_fg=Vec4(1, 1, 1, 1),
            relief=1,
            pressEffect=1,
            parent=self.frame
        )
        
        # Botão VOLTAR
        self.btn_back = DirectButton(
            text="<<< VOLTAR",
            text_scale=0.06,
            scale=1,
            pos=(0, 0, -0.8),
            command=self.go_back,
            frameColor=(0.3, 0.3, 0.5, 0.9),
            text_fg=Vec4(1, 1, 1, 1),
            relief=1,
            pressEffect=1,
            parent=self.frame
        )
        
        # Hover effects
        self.btn_start.bind("DGG.ENTER", lambda x: self.btn_start.setColor(1.3, 1.3, 1.3, 1))
        self.btn_start.bind("DGG.EXIT", lambda x: self.btn_start.setColor(1, 1, 1, 1))
        self.btn_back.bind("DGG.ENTER", lambda x: self.btn_back.setColor(1.3, 1.3, 1.3, 1))
        self.btn_back.bind("DGG.EXIT", lambda x: self.btn_back.setColor(1, 1, 1, 1))
    
    def start_level(self):
        """Inicia a fase"""
        self.cleanup()
        self.start_callback()
    
    def go_back(self):
        """Volta ao lobby"""
        self.cleanup()
        self.back_callback()
    
    def cleanup(self):
        """Remove a tela"""
        if self.frame:
            self.frame.destroy()