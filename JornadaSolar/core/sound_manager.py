"""
JORNADA SOLAR - SOUND MANAGER
Gerencia toda parte de áudio do jogo:
- Música de fundo (com transições suaves)
- Efeitos sonoros
- Controle de volume
- Fade in/out
"""

from panda3d.core import AudioSound
from typing import Optional, Dict
from direct.interval.IntervalGlobal import Sequence, LerpFunc, Func


class SoundManager:
    """
    Gerenciador de áudio do jogo.
    Controla música de fundo e efeitos sonoros.
    """
    
    def __init__(self, resource_loader, config_manager):
        """
        Inicializa o Sound Manager
        
        Args:
            resource_loader: ResourceLoader para carregar sons
            config_manager: SaveManager para pegar volumes das configs
        """
        self.resource_loader = resource_loader
        self.config_manager = config_manager
        
        # Música de fundo atual
        self.current_music: Optional[AudioSound] = None
        self.current_music_name: str = ""
        
        # Cache de sons para evitar recarregar
        self.sound_cache: Dict[str, AudioSound] = {}
        
        # Volumes
        self.music_volume = config_manager.get_config("music_volume", 0.7)
        self.sfx_volume = config_manager.get_config("sfx_volume", 0.8)
        
        # Estado
        self.music_enabled = True
        self.sfx_enabled = True
        
        print("SoundManager inicializado")
    
    # ====================================
    # MÚSICA DE FUNDO
    # ====================================
    
    def play_music(self, music_path: str, loop: bool = True, fade_in: float = 1.0):
        """
        Toca uma música de fundo
        
        Args:
            music_path: Caminho da música
            loop: Se deve repetir em loop
            fade_in: Duração do fade in em segundos
        """
        # Se já está tocando esta música, não faz nada
        if self.current_music_name == music_path and self.current_music:
            if self.current_music.status() == AudioSound.PLAYING:
                return
        
        # Para música anterior com fade out
        if self.current_music:
            self.stop_music(fade_out=fade_in)
        
        # Carrega nova música
        music = self.resource_loader.load_music(music_path)
        if music is None:
            print(f"⚠️ Não foi possível carregar música: {music_path}")
            return
        
        # Configura música
        music.setLoop(loop)
        music.setVolume(0)  # Começa em volume 0 para fade in
        
        if self.music_enabled:
            music.play()
        
        self.current_music = music
        self.current_music_name = music_path
        
        # Fade in
        if fade_in > 0:
            self._fade_music_to(self.music_volume, fade_in)
        else:
            music.setVolume(self.music_volume)
        
        print(f"Tocando música: {music_path}")
    
    def stop_music(self, fade_out: float = 1.0):
        """
        Para a música atual
        
        Args:
            fade_out: Duração do fade out em segundos
        """
        if self.current_music is None:
            return
        
        if fade_out > 0:
            # Fade out e depois para
            def stop_after_fade():
                if self.current_music:
                    self.current_music.stop()
            
            self._fade_music_to(0, fade_out, callback=stop_after_fade)
        else:
            self.current_music.stop()
        
        print("Música parada")
    
    def pause_music(self):
        """Pausa a música atual"""
        if self.current_music and self.current_music.status() == AudioSound.PLAYING:
            self.current_music.stop()
            print("⏸Música pausada")
    
    def resume_music(self):
        """Resume a música pausada"""
        if self.current_music and self.music_enabled:
            self.current_music.play()
            print("Música resumida")
    
    def set_music_volume(self, volume: float):
        """
        Define volume da música
        
        Args:
            volume: Volume de 0.0 a 1.0
        """
        self.music_volume = max(0.0, min(1.0, volume))
        
        if self.current_music:
            self.current_music.setVolume(self.music_volume)
        
        # Salva nas configurações
        self.config_manager.update_config("music_volume", self.music_volume)
    
    def toggle_music(self) -> bool:
        """
        Liga/desliga música
        
        Returns:
            Estado atual (True = ligado)
        """
        self.music_enabled = not self.music_enabled
        
        if self.music_enabled:
            if self.current_music:
                self.current_music.play()
        else:
            if self.current_music:
                self.current_music.stop()
        
        return self.music_enabled
    
    def _fade_music_to(self, target_volume: float, duration: float, callback=None):
        """
        Faz fade da música para um volume específico
        
        Args:
            target_volume: Volume alvo
            duration: Duração do fade
            callback: Função para chamar ao terminar
        """
        if self.current_music is None:
            return
        
        start_volume = self.current_music.getVolume()
        
        def lerp_volume(t):
            if self.current_music:
                volume = start_volume + (target_volume - start_volume) * t
                self.current_music.setVolume(volume)
        
        # Cria sequência de fade
        fade_sequence = Sequence(
            LerpFunc(lerp_volume, duration=duration, fromData=0, toData=1)
        )
        
        if callback:
            fade_sequence.append(Func(callback))
        
        fade_sequence.start()
    
    # ====================================
    # EFEITOS SONOROS
    # ====================================
    
    def play_sound(self, sound_path: str, volume: Optional[float] = None):
        """
        Toca um efeito sonoro
        
        Args:
            sound_path: Caminho do som
            volume: Volume específico (None = usa padrão)
        """
        if not self.sfx_enabled:
            return
        
        sound = self.resource_loader.load_sound(sound_path)
        if sound is None:
            print(f"⚠️ Não foi possível tocar som: {sound_path}")
            return
        
        # Define volume
        if volume is None:
            volume = self.sfx_volume
        else:
            volume = volume * self.sfx_volume  # Aplica volume master
        
        sound.setVolume(volume)
        sound.play()
    
    def play_sound_named(self, sound_name: str, volume: Optional[float] = None):
        """
        Toca um som usando nome da constante
        
        Args:
            sound_name: Nome do som (ex: "collect", "damage")
            volume: Volume específico
        """
        from core.constants import SOUNDS
        
        if sound_name in SOUNDS:
            self.play_sound(SOUNDS[sound_name], volume)
        else:
            print(f"⚠️ Som não encontrado nas constantes: {sound_name}")
    
    def set_sfx_volume(self, volume: float):
        """
        Define volume dos efeitos sonoros
        
        Args:
            volume: Volume de 0.0 a 1.0
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
        
        # Salva nas configurações
        self.config_manager.update_config("sfx_volume", self.sfx_volume)
    
    def toggle_sfx(self) -> bool:
        """
        Liga/desliga efeitos sonoros
        
        Returns:
            Estado atual (True = ligado)
        """
        self.sfx_enabled = not self.sfx_enabled
        return self.sfx_enabled
    
    # ====================================
    # MÚSICAS POR CONTEXTO
    # ====================================
    
    def play_menu_music(self):
        """Toca música do menu principal"""
        from core.constants import MUSIC
        self.play_music(MUSIC["menu"], loop=True, fade_in=2.0)
    
    def play_lobby_music(self):
        """Toca música do lobby 3D"""
        from core.constants import MUSIC
        self.play_music(MUSIC["lobby"], loop=True, fade_in=2.0)
    
    def play_level_music(self, level_name: str):
        """
        Toca música apropriada para a fase
        
        Args:
            level_name: Nome da fase
        """
        from core.constants import MUSIC
        
        # Planetas exteriores (Netuno, Urano, Saturno)
        outer_planets = ["netuno", "urano", "saturno"]
        
        # Planetas interiores (Júpiter até Mercúrio)
        inner_planets = ["jupiter", "marte", "terra", "venus", "mercurio"]
        
        if level_name in outer_planets:
            self.play_music(MUSIC["outer_planets"], loop=True, fade_in=1.5)
        elif level_name in inner_planets:
            self.play_music(MUSIC["inner_planets"], loop=True, fade_in=1.5)
        elif level_name == "sol":
            self.play_music(MUSIC["boss"], loop=True, fade_in=1.5)
    
    def play_victory_music(self):
        """Toca música de vitória"""
        from core.constants import MUSIC
        self.play_music(MUSIC["victory"], loop=False, fade_in=0.5)
    
    # ====================================
    # SONS DE UI RÁPIDOS
    # ====================================
    
    def play_collect_sound(self):
        """Som de coletar fragmento"""
        self.play_sound_named("collect")
    
    def play_damage_sound(self):
        """Som de tomar dano"""
        self.play_sound_named("damage")
    
    def play_powerup_sound(self):
        """Som de pegar power-up"""
        self.play_sound_named("powerup")
    
    def play_victory_sound(self):
        """Som de vitória"""
        self.play_sound_named("victory")
    
    def play_defeat_sound(self):
        """Som de derrota"""
        self.play_sound_named("defeat")
    
    def play_menu_click_sound(self):
        """Som de clique em menu"""
        self.play_sound_named("menu_click", volume=0.5)
    
    def play_combo_sound(self):
        """Som de combo"""
        self.play_sound_named("combo")
    
    def play_achievement_sound(self):
        """Som de conquista desbloqueada"""
        self.play_sound_named("achievement")
    
    def play_warning_sound(self):
        """Som de aviso (ex: erupção solar)"""
        self.play_sound_named("warning")
    
    # ====================================
    # UTILITÁRIOS
    # ====================================
    
    def mute_all(self):
        """Silencia tudo"""
        self.music_enabled = False
        self.sfx_enabled = False
        if self.current_music:
            self.current_music.stop()
        print("Áudio totalmente silenciado")
    
    def unmute_all(self):
        """Reativa áudio"""
        self.music_enabled = True
        self.sfx_enabled = True
        if self.current_music:
            self.current_music.play()
        print("Áudio reativado")
    
    def get_status(self) -> Dict:
        """
        Retorna status atual do áudio
        
        Returns:
            Dicionário com informações
        """
        music_playing = False
        if self.current_music:
            music_playing = self.current_music.status() == AudioSound.PLAYING
        
        return {
            "music_enabled": self.music_enabled,
            "sfx_enabled": self.sfx_enabled,
            "music_volume": self.music_volume,
            "sfx_volume": self.sfx_volume,
            "current_music": self.current_music_name,
            "music_playing": music_playing
        }
    
    def cleanup(self):
        """Limpa recursos de áudio"""
        if self.current_music:
            self.current_music.stop()
        self.current_music = None
        self.sound_cache.clear()
        print("Áudio limpo")


print("SoundManager class definida com sucesso!")