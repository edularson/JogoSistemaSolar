"""
JORNADA SOLAR - MENU PRINCIPAL
Menu principal do jogo (Adaptado para State Manager de Janela Única)
"""

from panda3d.core import WindowProperties, Vec4, TextNode
from direct.gui.DirectGui import DirectButton, DirectFrame
from direct.gui.OnscreenText import OnscreenText

class MainMenu:
    """Menu principal do jogo (Estado)"""
    
    def __init__(self, app):
        print("Inicializando Menu Principal...")
        
        # Guarda a referência para a janela principal do jogo
        self.app = app
        
        # Listas para guardar os elementos da UI e limpar depois
        self.ui_elements = []
        self.buttons = []
        
        try:
            # Setup janela usando o app
            self.setup_window()
            
            # Cor de fundo espacial
            self.app.setBackgroundColor(0.02, 0.02, 0.1, 1)
            self.app.disableMouse()
            
            # Inicializa managers básicos
            print("Carregando managers...")
            self.init_managers()
            
            # UI
            print("Criando interface...")
            self.create_ui()
            
            # Controles - Note o self.app.accept
            self.app.accept('escape', self.quit_game)
            
            print("Menu Principal carregado com sucesso!")
            
        except Exception as e:
            print(f"ERRO ao inicializar menu: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_window(self):
        """Configura janela"""
        try:
            props = WindowProperties()
            # Diz para o Panda3D usar o tamanho exato do seu monitor
            props.setSize(self.app.pipe.getDisplayWidth(), self.app.pipe.getDisplayHeight())
            props.setFullscreen(True)
            props.setTitle("Jornada Solar")
            self.app.win.requestProperties(props)
            self.app.setFrameRateMeter(True)  # Mostra FPS
        except Exception as e:
            print(f"⚠️ Aviso ao configurar janela: {e}")
    
    def init_managers(self):
        """Usa os managers já inicializados no App principal"""
        # Pegamos as referências do main.py (self.app)
        self.save_manager = self.app.save_manager
        self.sound_manager = self.app.sound_manager
        self.resource_loader = self.app.resource_loader
        
        # Toca a música usando o SoundManager global
        if self.sound_manager:
            try:
                self.sound_manager.play_menu_music()
                print("  SoundManager sincronizado e música tocando")
            except Exception as e:
                print(f"  ⚠️ Erro ao tocar música no menu: {e}")
    
    def create_ui(self):
        """Cria interface do menu"""
        try:
            # Título principal
            title = OnscreenText(
                text="JORNADA SOLAR",
                pos=(0, 0.6),
                scale=0.15,
                fg=Vec4(1, 0.84, 0, 1),
                align=TextNode.ACenter
            )
            title.setShadow((0.05, 0.05, 0, 0))
            self.ui_elements.append(title)
            
            # Subtítulo
            subtitle = OnscreenText(
                text="Aventura Espacial de Coleta",
                pos=(0, 0.45),
                scale=0.06,
                fg=Vec4(0.8, 0.8, 1.0, 1),
                align=TextNode.ACenter
            )
            subtitle.setShadow((0.03, 0.03, 0, 0))
            self.ui_elements.append(subtitle)
            
            # Estatísticas do jogador
            status_text, status_color = self.get_player_status()
            
            status = OnscreenText(
                text=status_text,
                pos=(0, 0.3),
                scale=0.05,
                fg=status_color,
                align=TextNode.ACenter
            )
            self.ui_elements.append(status)
            
            # Botões principais
            self.create_buttons()
            
            # Versão
            version = OnscreenText(
                text="v2 - Versao final",
                pos=(0, -0.95),
                scale=0.04,
                fg=Vec4(0.5, 0.5, 0.5, 1),
                align=TextNode.ACenter
            )
            self.ui_elements.append(version)
            
        except Exception as e:
            print(f"Erro ao criar UI: {e}")
    
    def get_player_status(self):
        """Retorna status do jogador"""
        if self.app.save_manager:
            try:
                stats = self.app.save_manager.get_all_stats()
                levels_completed = stats.get('levels_completed', 0)
                game_completed = stats.get('game_completed', False)
                
                if game_completed:
                    return "JOGO ZERADO!", Vec4(1, 0.84, 0, 1)
                elif levels_completed > 0:
                    return f"Progresso: {levels_completed}/9 fases", Vec4(0.5, 1, 0.5, 1)
            except:
                pass
        
        return "Novo Jogo", Vec4(1, 1, 1, 1)
    
    def create_buttons(self):
        """Cria botões do menu"""
        button_config = [
            {"text": "JOGAR", "command": self.start_game, "color": (0.2, 0.6, 0.2, 1)},
            {"text": "CONFIGURACOES", "command": self.show_settings, "color": (0.3, 0.3, 0.5, 1)},
            {"text": "CREDITOS", "command": self.show_credits, "color": (0.2, 0.3, 0.5, 1)},
            {"text": "SAIR", "command": self.quit_game, "color": (0.5, 0.2, 0.2, 1)}
        ]
        
        start_y = 0.2
        spacing = 0.25  
        
        for i, config in enumerate(button_config):
            y_pos = start_y - (i * spacing)
            
            btn = DirectButton(
                text=config["text"],
                text_scale=0.5,
                scale=0.15,
                pos=(0, 0, y_pos),
                command=config["command"],
                frameColor=config["color"],
                text_fg=Vec4(1, 1, 1, 1),
                relief=1,
                frameSize=(-4, 4, -0.6, 0.9), 
                borderWidth=(0.02, 0.02),
                pressEffect=1
            )
            
            btn.bind("DGG.ENTER", lambda x, b=btn: b.setColor(1.3, 1.3, 1.3, 1))
            btn.bind("DGG.EXIT", lambda x, b=btn: b.setColor(1, 1, 1, 1))
            
            self.buttons.append(btn)
    
    def start_game(self):
        """Inicia o jogo"""
        self.play_sound()
        self.transition_to("lobby")
    
    def show_settings(self):
        """Chama a tela de configurações real através do app"""
        self.play_sound()
        self.transition_to("CONFIGURACOES")
    
    def show_credits(self):
        self.play_sound()
        
        credits_frame = DirectFrame(
            frameSize=(-1.4, 1.4, -0.85, 0.85),
            frameColor=(0.05, 0.05, 0.15, 0.98)
        )
        
        texto_creditos = (
            "*** CRÉDITOS ***\n\n"
            "\nAlunos:\n"
            "Eduardo Larson\n"
            "João Samuel Luy\n\n"
            "2026\n\n"
            "Este jogo foi desenvolvido como projeto da disciplina de Computação Gráfica e "
            "Processamento Digital de Imagens.\n\n"
            "A proposta do trabalho foi aplicar os conhecimentos adquiridos em sala, "
            "incluindo conceitos de renderização, manipulação de imagens, interação "
            "gráfica e lógica de programação, na criação de um jogo no estilo "
            "\"Drop and Catch\" ambientado no Sistema Solar.\n\n"
            "O projeto foi orientado pelo professor Jotair Elio Kwiatkowski Junior.\n\n"
            "Agradecemos pela orientação, pelos desafios propostos e pela oportunidade "
            "de transformar teoria em prática."
        )
        
        msg = OnscreenText(
            text=texto_creditos,
            pos=(0, 0.65),
            scale=0.045,
            fg=Vec4(1, 1, 1, 1),
            align=TextNode.ACenter,
            parent=credits_frame,
            wordwrap=55
        )
        
        close_btn = DirectButton(
            text="FECHAR",
            text_scale=0.05,
            scale=1.5,
            pos=(0, 0, -0.7),     
            command=lambda: credits_frame.destroy(),
            parent=credits_frame,
            frameColor=(0.5, 0.2, 0.2, 1),
            text_fg=Vec4(1, 1, 1, 1),
            relief=1,
            borderWidth=(0.02, 0.02)
        )
        
        self.ui_elements.extend([credits_frame, msg, close_btn])
    
    def show_temp_message(self, message: str):
        temp_frame = DirectFrame(frameSize=(-1, 1, -0.5, 0.5), frameColor=(0.1, 0.1, 0.2, 0.95))
        msg = OnscreenText(text=message, pos=(0, 0.1), scale=0.06, fg=Vec4(1, 1, 1, 1), parent=temp_frame)
        close_btn = DirectButton(text="OK", scale=0.1, pos=(0, 0, -0.3), command=lambda: temp_frame.destroy(), parent=temp_frame)
        self.ui_elements.extend([temp_frame, msg, close_btn]) 
    
    def play_sound(self):
        if self.sound_manager:
            try:
                self.sound_manager.play_menu_click_sound()
            except:
                pass
    
    def quit_game(self):
        self.play_sound()
        self.transition_to("sair")
    
    def transition_to(self, destination: str):
        """Chama a mudança de estado na janela principal"""
        if destination.upper() not in ["CONFIGURACOES", "LOBBY"]:
            if self.sound_manager:
                try:
                    self.sound_manager.stop_music(fade_out=0.3)
                except:
                    pass
    
        self.app.change_state(destination)
        
    def cleanup(self):
        """Limpa a tela antes de ir pro próximo estado"""
        print("Limpando Menu...")
        # Remove os controles do teclado
        self.app.ignoreAll()
        
        # Destrói os botões
        for btn in self.buttons:
            btn.destroy()
        self.buttons.clear()
        
        # Destrói os textos e frames
        for elem in self.ui_elements:
            elem.destroy()
        self.ui_elements.clear()