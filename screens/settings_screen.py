"""
JORNADA SOLAR - SETTINGS SCREEN
Tela de configurações (volume, dificuldade, etc)
VERSÃO MELHORADA - Botões e sliders maiores!
"""

from direct.gui.DirectGui import DirectFrame, DirectButton, DirectSlider, DirectLabel
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import Vec4, TextNode


class SettingsScreen:
    """Tela de configurações"""
    
    def __init__(self, base, sound_manager, back_callback):
        """
        Inicializa tela de configurações
        
        Args:
            base: ShowBase instance
            sound_manager: SoundManager
            back_callback: Função para voltar
        """
        self.base = base
        self.sound_manager = sound_manager
        self.back_callback = back_callback
        
        # Frame principal
        self.frame = DirectFrame(
            frameSize=(-2, 2, -2, 2),
            frameColor=(0.02, 0.02, 0.1, 0.98)
        )
        
        # Título
        self.title = OnscreenText(
            text="*** CONFIGURACOES ***",
            pos=(0, 0.85),
            scale=0.15,
            fg=Vec4(1, 0.84, 0, 1),
            align=TextNode.ACenter,
            parent=self.frame
        )
        self.title.setShadow((0.05, 0.05, 0, 0))
        
        # ========== VOLUME DA MÚSICA ==========
        self.label_music = OnscreenText(
            text="VOLUME DA MUSICA",
            pos=(0, 0.6),
            scale=0.07, 
            fg=Vec4(1, 1, 1, 1),
            align=TextNode.ACenter,
            parent=self.frame
        )
        
        current_music_vol = self.sound_manager.music_volume
        
        self.slider_music = DirectSlider(
            range=(0, 1),
            value=current_music_vol,
            pageSize=0.1,
            command=self.on_music_volume_change,
            pos=(0, 0, 0.48),
            scale=0.6,
            parent=self.frame,
            thumb_frameSize=(-0.05, 0.05, -0.08, 0.08),
            thumb_relief=1
        )
        
        self.music_value = OnscreenText(
            text=f"{int(current_music_vol * 100)}%",
            pos=(0, 0.35),
            scale=0.08, 
            fg=Vec4(0.5, 1, 0.5, 1),
            align=TextNode.ACenter,
            parent=self.frame
        )
        
        # ========== VOLUME DOS EFEITOS ==========
        self.label_sfx = OnscreenText(
            text="VOLUME DOS EFEITOS",
            pos=(0, 0.2),
            scale=0.07,
            fg=Vec4(1, 1, 1, 1),
            align=TextNode.ACenter,
            parent=self.frame
        )
        
        current_sfx_vol = self.sound_manager.sfx_volume
        
        # Slider de SFX MAIOR
        self.slider_sfx = DirectSlider(
            range=(0, 1),
            value=current_sfx_vol,
            pageSize=0.1,
            command=self.on_sfx_volume_change,
            pos=(0, 0, 0.08),
            scale=0.6, 
            parent=self.frame,
            thumb_frameSize=(-0.05, 0.05, -0.08, 0.08),
            thumb_relief=1
        )
        
        self.sfx_value = OnscreenText(
            text=f"{int(current_sfx_vol * 100)}%",
            pos=(0, -0.05),
            scale=0.08,
            fg=Vec4(0.5, 1, 0.5, 1),
            align=TextNode.ACenter,
            parent=self.frame
        )
        
        # ========== BOTÃO RESETAR ==========
        self.btn_reset = DirectButton(
            text="RESETAR PROGRESSO",
            text_scale=0.15,
            scale=0.4, 
            pos=(0, 0, -0.3),
            command=self.confirm_reset,
            frameColor=(0.6, 0.2, 0.2, 0.9),
            text_fg=Vec4(1, 1, 1, 1),
            relief=1,
            pressEffect=1,
            parent=self.frame
        )
        
        # Aviso
        self.warning = OnscreenText(
            text="!!! Isso apagara todo seu progresso !!!",
            pos=(0, -0.45),
            scale=0.05,
            fg=Vec4(1, 0.5, 0.5, 1),
            align=TextNode.ACenter,
            parent=self.frame
        )
        
        # ========== BOTÕES INFERIORES ==========
        # Botão Salvar
        self.btn_save = DirectButton(
            text="SALVAR",
            text_scale=0.15,
            scale=0.4, 
            pos=(-0.35, 0, -0.7),
            command=self.save_settings,
            frameColor=(0.2, 0.6, 0.2, 0.9),
            text_fg=Vec4(1, 1, 1, 1),
            relief=1,
            pressEffect=1,
            parent=self.frame
        )
        
        # Botão Voltar
        self.btn_back = DirectButton(
            text="<<< VOLTAR",
            text_scale=0.15, 
            scale=0.4,
            pos=(0.35, 0, -0.7),
            command=self.go_back,
            frameColor=(0.3, 0.3, 0.5, 0.9),
            text_fg=Vec4(1, 1, 1, 1),
            relief=1,
            pressEffect=1,
            parent=self.frame
        )
        
        # Hover effects
        self.btn_reset.bind("DGG.ENTER", lambda x: self.btn_reset.setColor(1.3, 1.3, 1.3, 1))
        self.btn_reset.bind("DGG.EXIT", lambda x: self.btn_reset.setColor(1, 1, 1, 1))
        self.btn_save.bind("DGG.ENTER", lambda x: self.btn_save.setColor(1.3, 1.3, 1.3, 1))
        self.btn_save.bind("DGG.EXIT", lambda x: self.btn_save.setColor(1, 1, 1, 1))
        self.btn_back.bind("DGG.ENTER", lambda x: self.btn_back.setColor(1.3, 1.3, 1.3, 1))
        self.btn_back.bind("DGG.EXIT", lambda x: self.btn_back.setColor(1, 1, 1, 1))
        
        # Frame de confirmação (inicialmente escondido)
        self.confirm_frame = None
    
    def on_music_volume_change(self):
        """Callback quando volume da música muda"""
        value = self.slider_music['value']
        self.sound_manager.set_music_volume(value)
        self.music_value.setText(f"{int(value * 100)}%")
    
    def on_sfx_volume_change(self):
        """Callback quando volume dos efeitos muda"""
        value = self.slider_sfx['value']
        self.sound_manager.set_sfx_volume(value)
        self.sfx_value.setText(f"{int(value * 100)}%")
        
        # Toca som de teste
        try:
            self.sound_manager.play_menu_click_sound()
        except:
            pass
    
    def confirm_reset(self):
        """Mostra confirmação de reset"""
        # Cria frame de confirmação MAIOR
        self.confirm_frame = DirectFrame(
            frameSize=(-0.8, 0.8, -0.4, 0.4),
            frameColor=(0.15, 0.05, 0.05, 0.95),
            pos=(0, 0, 0.1),
            parent=self.frame
        )
        
        confirm_text = OnscreenText(
            text="!!! TEM CERTEZA ???\n\nTodo progresso sera perdido!",
            pos=(0, 0.15),
            scale=0.07,
            fg=Vec4(1, 1, 1, 1),
            align=TextNode.ACenter,
            parent=self.confirm_frame
        )
        
        btn_yes = DirectButton(
            text="SIM, RESETAR",
            text_scale=0.07,
            scale=0.15, 
            pos=(-0.3, 0, -0.2),
            command=self.do_reset,
            frameColor=(0.6, 0.1, 0.1, 1),
            parent=self.confirm_frame,
            pressEffect=1
        )
        
        btn_no = DirectButton(
            text="NAO, CANCELAR",
            text_scale=0.07,
            scale=0.15,
            pos=(0.3, 0, -0.2),
            command=self.cancel_reset,
            frameColor=(0.2, 0.5, 0.2, 1),
            parent=self.confirm_frame,
            pressEffect=1
        )
    
    def do_reset(self):
        """Executa reset do progresso"""
        from core.save_manager import SaveManager
        
        save_mgr = SaveManager()
        save_mgr.reset_progress()
        
        # Remove confirmação
        if self.confirm_frame:
            self.confirm_frame.destroy()
            self.confirm_frame = None
        
        # Mostra mensagem
        self.reset_msg = OnscreenText(
            text="Progresso resetado com sucesso!",
            pos=(0, -0.55),
            scale=0.06, 
            fg=Vec4(0.5, 1, 0.5, 1),
            align=TextNode.ACenter,
            parent=self.frame
        )
    
    def cancel_reset(self):
        """Cancela reset"""
        if self.confirm_frame:
            self.confirm_frame.destroy()
            self.confirm_frame = None
    
    def save_settings(self):
        """Salva configurações"""
        try:
            self.sound_manager.play_menu_click_sound()
        except:
            pass
        
        # Mostra mensagem
        save_msg = OnscreenText(
            text="Configuracoes salvas!",
            pos=(0, -0.55),
            scale=0.06, 
            fg=Vec4(0.5, 1, 0.5, 1),
            align=TextNode.ACenter,
            parent=self.frame
        )
        
        # Remove mensagem após 2 segundos
        from direct.task import Task
        def remove_msg(task):
            try:
                save_msg.destroy()
            except:
                pass
            return Task.done
        
        self.base.taskMgr.doMethodLater(2.0, remove_msg, 'removeSaveMsg')
    
    def go_back(self):
        """Volta ao menu"""
        self.cleanup()
        self.back_callback()
    
    def cleanup(self):
        """Remove a tela"""
        if self.frame:
            self.frame.destroy()