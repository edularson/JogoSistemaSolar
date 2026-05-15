"""
JORNADA SOLAR - UI MANAGER
Sistema de interface de usuário reutilizável
Gerencia HUD, textos, menus, notificações e popups
"""

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectFrame, DirectButton, DirectSlider, DirectLabel
from panda3d.core import TextNode, Vec4, TransparencyAttrib
from typing import Optional, List, Callable, Dict
from direct.interval.IntervalGlobal import Sequence, Func, Wait, LerpColorScaleInterval


class UIManager:
    """
    Gerenciador de UI do jogo.
    Fornece métodos para criar elementos de interface reutilizáveis.
    """
    
    def __init__(self, base, aspect2d, render2d):
        """
        Inicializa o UI Manager
        
        Args:
            base: ShowBase instance
            aspect2d: aspect2d node para UI proporcional
            render2d: render2d node para UI fixa
        """
        self.base = base
        self.aspect2d = aspect2d
        self.render2d = render2d
        
        # Listas de elementos ativos
        self.active_texts: List[OnscreenText] = []
        self.active_frames: List[DirectFrame] = []
        self.active_buttons: List[DirectButton] = []
        self.active_notifications: List[Dict] = []
        
        # Configurações de fonte (ajustar tamanho baseado na resolução)
        self.base_text_scale = 0.05
        self.title_scale = 0.08
        self.small_scale = 0.04
        
        print("UIManager inicializado")
    
    # ====================================
    # TEXTOS BÁSICOS
    # ====================================
    
    def create_text(self, text: str, pos: tuple, scale: float = None,
                   color: Vec4 = None, align: int = TextNode.ALeft,
                   parent=None, shadow: bool = True) -> OnscreenText:
        """
        Cria um texto na tela
        
        Args:
            text: Texto a exibir
            pos: Posição (x, y) normalizada (-1 a 1)
            scale: Escala do texto
            color: Cor RGBA
            align: Alinhamento (TextNode.ALeft, ACenter, ARight)
            parent: Node pai (None = aspect2d)
            shadow: Se deve ter sombra
            
        Returns:
            OnscreenText criado
        """
        if scale is None:
            scale = self.base_text_scale
        if color is None:
            color = Vec4(1, 1, 1, 1)
        if parent is None:
            parent = self.aspect2d
        
        text_obj = OnscreenText(
            text=text,
            pos=pos,
            scale=scale,
            fg=color,
            align=align,
            parent=parent,
            mayChange=True
        )
        
        if shadow:
            text_obj.setShadow((0.05, 0.05, 0, 0))
        
        self.active_texts.append(text_obj)
        return text_obj
    
    def create_title(self, text: str, y_pos: float = 0.8, color: Vec4 = None) -> OnscreenText:
        """
        Cria um título centralizado
        
        Args:
            text: Texto do título
            y_pos: Posição Y (0 = centro, 1 = topo)
            color: Cor do texto
            
        Returns:
            OnscreenText do título
        """
        if color is None:
            from core.constants import COLOR_GOLD
            color = COLOR_GOLD
        
        return self.create_text(
            text=text,
            pos=(0, y_pos),
            scale=self.title_scale,
            color=color,
            align=TextNode.ACenter,
            shadow=True
        )
    
    def create_subtitle(self, text: str, y_pos: float = 0.7, color: Vec4 = None) -> OnscreenText:
        """Cria um subtítulo"""
        if color is None:
            from core.constants import COLOR_WHITE
            color = COLOR_WHITE
        
        return self.create_text(
            text=text,
            pos=(0, y_pos),
            scale=self.base_text_scale * 0.8,
            color=color,
            align=TextNode.ACenter,
            shadow=True
        )
    
    # ====================================
    # HUD DE JOGO
    # ====================================
    
    def create_hud(self) -> Dict[str, OnscreenText]:
        """
        Cria HUD completo do jogo
        
        Returns:
            Dicionário com elementos do HUD
        """
        hud = {
            "score": self.create_text("Fragmentos: 0/20", (-1.3, 0.9)),
            "lives": self.create_text("Vidas: 3", (-1.3, 0.8)),
            "powerups": self.create_text("Power-ups: nenhum", (-1.3, 0.7)),
            "timer": self.create_text("Tempo: 00:00", (1.0, 0.9), align=TextNode.ARight),
            "combo": self.create_text("", (0, -0.7), align=TextNode.ACenter, scale=self.base_text_scale * 1.2)
        }
        
        return hud
    
    def update_hud_text(self, hud_element: OnscreenText, new_text: str):
        """
        Atualiza texto de um elemento do HUD
        
        Args:
            hud_element: Elemento a atualizar
            new_text: Novo texto
        """
        if hud_element:
            hud_element.setText(new_text)
    
    def create_health_bar(self, max_hp: int, current_hp: int, 
                         pos: tuple = (0, 0.85)) -> DirectFrame:
        """
        Cria uma barra de vida visual
        
        Args:
            max_hp: Vida máxima
            current_hp: Vida atual
            pos: Posição central da barra
            
        Returns:
            DirectFrame da barra
        """
        # Frame de fundo (barra vazia)
        bg_frame = DirectFrame(
            frameSize=(-0.3, 0.3, -0.03, 0.03),
            frameColor=(0.2, 0.2, 0.2, 0.8),
            pos=(pos[0], 0, pos[1])
        )
        
        # Frame de vida (barra preenchida)
        health_width = 0.6 * (current_hp / max_hp)
        health_frame = DirectFrame(
            frameSize=(-0.3, -0.3 + health_width, -0.025, 0.025),
            frameColor=(1, 0.2, 0.2, 1),
            pos=(pos[0], 0, pos[1]),
            parent=bg_frame
        )
        
        # Texto de HP
        hp_text = OnscreenText(
            text=f"{current_hp}/{max_hp}",
            pos=(pos[0], pos[1] - 0.08),
            scale=0.04,
            fg=Vec4(1, 1, 1, 1),
            align=TextNode.ACenter,
            parent=self.aspect2d
        )
        
        self.active_frames.append(bg_frame)
        return bg_frame
    
    # ====================================
    # BOTÕES
    # ====================================
    
    def create_button(self, text: str, pos: tuple, command: Callable,
                     scale: float = 0.1, color: Vec4 = None) -> DirectButton:
        """
        Cria um botão clicável
        
        Args:
            text: Texto do botão
            pos: Posição (x, y, z)
            command: Função a chamar ao clicar
            scale: Escala do botão
            color: Cor do botão
            
        Returns:
            DirectButton criado
        """
        if color is None:
            color = Vec4(0.2, 0.2, 0.3, 0.9)
        
        button = DirectButton(
            text=text,
            text_scale=scale * 0.6,
            scale=scale,
            pos=pos,
            command=command,
            frameSize=(-2, 2, -0.5, 0.8),
            frameColor=color,
            text_fg=Vec4(1, 1, 1, 1),
            relief=1,
            borderWidth=(0.01, 0.01)
        )
        
        # Efeitos de hover
        button.bind("DGG.ENTER", lambda _: button.setColor(1.2, 1.2, 1.2, 1))
        button.bind("DGG.EXIT", lambda _: button.setColor(1, 1, 1, 1))
        
        self.active_buttons.append(button)
        return button
    
    def create_menu_buttons(self, buttons_config: List[Dict]) -> List[DirectButton]:
        """
        Cria múltiplos botões de menu verticalmente
        
        Args:
            buttons_config: Lista de dicts com 'text' e 'command'
            
        Returns:
            Lista de botões criados
        """
        buttons = []
        start_y = 0.2
        spacing = 0.15
        
        for i, config in enumerate(buttons_config):
            y_pos = start_y - (i * spacing)
            button = self.create_button(
                text=config["text"],
                pos=(0, 0, y_pos),
                command=config["command"]
            )
            buttons.append(button)
        
        return buttons
    
    
    # ====================================
    # NOTIFICAÇÕES E POPUPS
    # ====================================
    
    def show_notification(self, text: str, duration: float = 3.0,
                         pos: tuple = (0, 0.5), color: Vec4 = None):
        """
        Mostra uma notificação temporária
        
        Args:
            text: Texto da notificação
            duration: Duração em segundos
            pos: Posição na tela
            color: Cor do texto
        """
        if color is None:
            from core.constants import COLOR_GOLD
            color = COLOR_GOLD
        
        notification = self.create_text(
            text=text,
            pos=pos,
            scale=self.base_text_scale * 1.3,
            color=color,
            align=TextNode.ACenter,
            shadow=True
        )
        
        # Animação de fade out
        def remove_notification():
            if notification in self.active_texts:
                self.active_texts.remove(notification)
            notification.destroy()
        
        # Sequência: espera -> fade out -> remove
        fade_sequence = Sequence(
            Wait(duration - 0.5),
            LerpColorScaleInterval(notification, 0.5, Vec4(1, 1, 1, 0)),
            Func(remove_notification)
        )
        fade_sequence.start()
    
    def show_achievement_popup(self, achievement_name: str, achievement_icon: str,
                              achievement_desc: str):
        """
        Mostra popup de conquista desbloqueada
        
        Args:
            achievement_name: Nome da conquista
            achievement_icon: Emoji/ícone
            achievement_desc: Descrição
        """
        # Frame de fundo
        popup_frame = DirectFrame(
            frameSize=(-0.5, 0.5, -0.15, 0.15),
            frameColor=(0.1, 0.1, 0.2, 0.95),
            pos=(0, 0, 0.6)
        )
        
        # Título
        title = OnscreenText(
            text="CONQUISTA DESBLOQUEADA!",
            pos=(0, 0.1),
            scale=0.045,
            fg=Vec4(1, 0.84, 0, 1),
            align=TextNode.ACenter,
            parent=popup_frame
        )
        
        # Nome e ícone
        achievement_text = OnscreenText(
            text=f"{achievement_icon} {achievement_name}",
            pos=(0, 0.03),
            scale=0.05,
            fg=Vec4(1, 1, 1, 1),
            align=TextNode.ACenter,
            parent=popup_frame
        )
        
        # Descrição
        desc_text = OnscreenText(
            text=achievement_desc,
            pos=(0, -0.05),
            scale=0.035,
            fg=Vec4(0.8, 0.8, 0.8, 1),
            align=TextNode.ACenter,
            parent=popup_frame
        )
        
        # Remove após 4 segundos
        def remove_popup():
            popup_frame.destroy()
        
        Sequence(
            Wait(4.0),
            LerpColorScaleInterval(popup_frame, 0.5, Vec4(1, 1, 1, 0)),
            Func(remove_popup)
        ).start()
    
    def show_combo_text(self, combo_count: int, pos: tuple = (0, -0.6)):
        """
        Mostra texto de combo
        
        Args:
            combo_count: Número do combo
            pos: Posição na tela
        """
        combo_text = self.create_text(
            text=f"COMBO x{combo_count}!",
            pos=pos,
            scale=self.base_text_scale * 1.5,
            color=Vec4(1, 0.5, 0, 1),
            align=TextNode.ACenter
        )
        
        # Anima e remove
        def remove_combo():
            if combo_text in self.active_texts:
                self.active_texts.remove(combo_text)
            combo_text.destroy()
        
        Sequence(
            LerpColorScaleInterval(combo_text, 0.3, Vec4(1.5, 1.5, 0.5, 1)),
            Wait(1.0),
            LerpColorScaleInterval(combo_text, 0.5, Vec4(1, 1, 1, 0)),
            Func(remove_combo)
        ).start()
    
    # ====================================
    # TELAS DE PAUSA/GAME OVER
    # ====================================
    
    def show_pause_overlay(self) -> DirectFrame:
        """
        Mostra overlay de pausa
        
        Returns:
            Frame do overlay
        """
        # Fundo escuro semitransparente
        overlay = DirectFrame(
            frameSize=(-2, 2, -2, 2),
            frameColor=(0, 0, 0, 0.7),
            pos=(0, 0, 0)
        )
        
        # Texto "PAUSADO"
        pause_text = OnscreenText(
            text="⏸JOGO PAUSADO",
            pos=(0, 0.1),
            scale=0.1,
            fg=Vec4(1, 1, 1, 1),
            align=TextNode.ACenter,
            parent=overlay
        )
        
        # Instruções
        instructions = OnscreenText(
            text="Pressione P para continuar\nESC para sair",
            pos=(0, -0.1),
            scale=0.05,
            fg=Vec4(0.8, 0.8, 0.8, 1),
            align=TextNode.ACenter,
            parent=overlay
        )
        
        self.active_frames.append(overlay)
        return overlay
    
    def show_game_over_screen(self, victory: bool, stats: Dict,
                             restart_callback: Callable,
                             menu_callback: Callable) -> DirectFrame:
        """
        Mostra tela de fim de jogo
        
        Args:
            victory: Se foi vitória ou derrota
            stats: Estatísticas da partida
            restart_callback: Função para reiniciar
            menu_callback: Função para voltar ao menu
            
        Returns:
            Frame da tela
        """
        # Fundo
        overlay = DirectFrame(
            frameSize=(-2, 2, -2, 2),
            frameColor=(0, 0, 0, 0.9),
            pos=(0, 0, 0)
        )
        
        # Título
        if victory:
            title_text = "VITORIA!"
            title_color = Vec4(0, 1, 0, 1)
        else:
            title_text = "GAME OVER"
            title_color = Vec4(1, 0, 0, 1)
        
        title = OnscreenText(
            text=title_text,
            pos=(0, 0.5),
            scale=0.12,
            fg=title_color,
            align=TextNode.ACenter,
            parent=overlay
        )
        
        # Estatísticas
        stats_y = 0.3
        stats_text = f"""
Fragmentos coletados: {stats.get('collected', 0)}/{stats.get('total', 0)}
Tempo: {stats.get('time', '00:00')}
Pontuação: {stats.get('score', 0)}
Dano recebido: {stats.get('damage_taken', 0)}
        """
        
        stats_label = OnscreenText(
            text=stats_text.strip(),
            pos=(0, stats_y),
            scale=0.05,
            fg=Vec4(1, 1, 1, 1),
            align=TextNode.ACenter,
            parent=overlay
        )
        
        # Recorde?
        if stats.get('new_highscore', False):
            highscore_text = OnscreenText(
                text="NOVO RECORDE!",
                pos=(0, 0.05),
                scale=0.06,
                fg=Vec4(1, 0.84, 0, 1),
                align=TextNode.ACenter,
                parent=overlay
            )
        
        # Botões
        tamanho_fixo = (-0.4, 0.4, -0.05, 0.1)

        btn_restart = DirectButton(
            text="JOGAR NOVAMENTE",
            text_scale=0.06,
            scale=0.6,
            pos=(0, 0, -0.2),
            command=restart_callback,
            frameColor=(0.2, 0.5, 0.2, 0.9),
            frameSize=tamanho_fixo,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0.02, 0.02, 0, 1),
            parent=overlay
        )
        
        btn_menu = DirectButton(
            text="MENU PRINCIPAL",
            text_scale=0.06,
            scale=0.6,
            pos=(0, 0, -0.4),
            command=menu_callback,
            frameColor=(0.3, 0.3, 0.5, 0.9),
            frameSize=tamanho_fixo,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0.02, 0.02, 0, 1),
            parent=overlay
        )
        
        self.active_frames.append(overlay)
        return overlay
    
    # ====================================
    # SLIDERS (para configurações)
    # ====================================
    
    def create_slider(self, label: str, pos: tuple, initial_value: float,
                     callback: Callable, range_vals: tuple = (0, 1)) -> DirectSlider:
        """
        Cria um slider com label
        
        Args:
            label: Texto do label
            pos: Posição (x, y, z)
            initial_value: Valor inicial
            callback: Função chamada ao mudar valor
            range_vals: (min, max)
            
        Returns:
            DirectSlider criado
        """
        # Label
        label_text = DirectLabel(
            text=label,
            text_scale=0.05,
            pos=(pos[0] - 0.3, pos[1], pos[2]),
            frameColor=(0, 0, 0, 0)
        )
        
        # Slider
        slider = DirectSlider(
            range=range_vals,
            value=initial_value,
            pageSize=0.1,
            command=callback,
            pos=pos,
            scale=0.3
        )
        
        return slider
    
    # ====================================
    # TUTORIAL
    # ====================================
    
    def show_tutorial_message(self, message: str, duration: float = 3.0):
        """
        Mostra mensagem de tutorial
        
        Args:
            message: Texto da mensagem
            duration: Duração em segundos
        """
        tutorial_bg = DirectFrame(
            frameSize=(-0.6, 0.6, -0.1, 0.1),
            frameColor=(0.1, 0.1, 0.3, 0.8),
            pos=(0, 0, -0.8)
        )
        
        tutorial_text = OnscreenText(
            text=f"💡 {message}",
            pos=(0, 0),
            scale=0.045,
            fg=Vec4(1, 1, 0.5, 1),
            align=TextNode.ACenter,
            parent=tutorial_bg
        )
        
        def remove_tutorial():
            tutorial_bg.destroy()
        
        Sequence(
            Wait(duration),
            LerpColorScaleInterval(tutorial_bg, 0.5, Vec4(1, 1, 1, 0)),
            Func(remove_tutorial)
        ).start()
    
    # ====================================
    # LIMPEZA
    # ====================================
    
    def clear_all(self):
        """Remove todos os elementos de UI ativos"""
        for text in self.active_texts:
            text.destroy()
        for frame in self.active_frames:
            frame.destroy()
        for button in self.active_buttons:
            button.destroy()
        
        self.active_texts.clear()
        self.active_frames.clear()
        self.active_buttons.clear()
        
        print("UI limpa")
    
    def remove_element(self, element):
        """
        Remove um elemento específico
        
        Args:
            element: Elemento a remover
        """
        try:
            if element in self.active_texts:
                self.active_texts.remove(element)
            elif element in self.active_frames:
                self.active_frames.remove(element)
            elif element in self.active_buttons:
                self.active_buttons.remove(element)
            
            element.destroy()
        except:
            pass


print("UIManager class definida com sucesso!")