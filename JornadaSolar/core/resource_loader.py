import os
import sys
from direct.showbase.Loader import Loader
from panda3d.core import AudioSound, Texture, NodePath, getModelPath, Filename
from typing import Dict, Optional


class ResourceLoader:
    """
    Gerenciador de recursos do jogo.
    Responsável por carregar e cachear todos os assets.
    """
    
    def __init__(self, loader: Loader, sfx_manager, music_manager):
        """
        Inicializa o Resource Loader
        
        Args:
            loader: Loader do Panda3D (self.loader da ShowBase)
            sfx_manager: Gerenciador de efeitos sonoros
            music_manager: Gerenciador de música
        """
        self.loader = loader
        self.sfx_manager = sfx_manager
        self.music_manager = music_manager
        
        # Adiciona caminhos de busca para assets
        # 1. Diretório atual (útil em dev)
        root_dir = Filename.fromOsSpecific(os.getcwd())
        getModelPath().appendDirectory(root_dir)
        # 2. Diretório do executável PyInstaller (sys._MEIPASS)
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            meipass_dir = Filename.fromOsSpecific(sys._MEIPASS)
            getModelPath().appendDirectory(meipass_dir)
        
        # Caches para evitar recarregar assets
        self.model_cache: Dict[str, NodePath] = {}
        self.texture_cache: Dict[str, Texture] = {}
        self.sound_cache: Dict[str, AudioSound] = {}
        self.music_cache: Dict[str, AudioSound] = {}
        
        print("ResourceLoader inicializado")
    
    # ====================================
    # MODELOS 3D
    # ====================================
    
    def load_model(self, model_path: str, force_reload: bool = False) -> Optional[NodePath]:
        """
        Carrega um modelo 3D com cache e tratamento de erros
        
        Args:
            model_path: Caminho do modelo (ex: "models/fighter")
            force_reload: Se True, ignora cache e recarrega
            
        Returns:
            NodePath do modelo ou None se falhar
        """
        # Verifica cache
        if not force_reload and model_path in self.model_cache:
            return self.model_cache[model_path].copyTo(NodePath())
        
        try:
            model = self.loader.loadModel(model_path)
            if model:
                self.model_cache[model_path] = model
                print(f"Modelo carregado: {model_path}")
                return model.copyTo(NodePath())
            else:
                print(f"⚠️ Modelo não encontrado: {model_path}")
                return None
        except Exception as e:
            print(f"Erro ao carregar modelo {model_path}: {e}")
            return None
    
    def load_model_with_fallback(self, primary_path: str, fallback_path: str) -> NodePath:
        """
        Tenta carregar modelo primário, se falhar usa fallback
        
        Args:
            primary_path: Modelo preferencial
            fallback_path: Modelo alternativo
            
        Returns:
            NodePath do modelo (primário ou fallback)
        """
        model = self.load_model(primary_path)
        if model is None:
            print(f"Usando fallback: {fallback_path}")
            model = self.load_model(fallback_path)
        return model
    
    # ====================================
    # TEXTURAS
    # ====================================
    
    def load_texture(self, texture_path: str, force_reload: bool = False) -> Optional[Texture]:
        """
        Carrega uma textura com cache e tratamento de erros
        
        Args:
            texture_path: Caminho da textura (ex: "models/purple.png")
            force_reload: Se True, ignora cache
            
        Returns:
            Texture ou None se falhar
        """
        # Verifica cache
        if not force_reload and texture_path in self.texture_cache:
            return self.texture_cache[texture_path]
        
        try:
            texture = self.loader.loadTexture(texture_path)
            if texture:
                self.texture_cache[texture_path] = texture
                print(f"Textura carregada: {texture_path}")
                return texture
            else:
                print(f"⚠️ Textura não encontrada: {texture_path}")
                return None
        except Exception as e:
            print(f"Erro ao carregar textura {texture_path}: {e}")
            return None
    
    def apply_texture_to_model(self, model: NodePath, texture_path: str) -> bool:
        """
        Aplica textura a um modelo
        
        Args:
            model: NodePath do modelo
            texture_path: Caminho da textura
            
        Returns:
            True se sucesso, False se falhou
        """
        texture = self.load_texture(texture_path)
        if texture and model:
            model.setTexture(texture, 1)
            return True
        return False
    
    # ====================================
    # SONS (SFX)
    # ====================================
    
    def load_sound(self, sound_path: str, force_reload: bool = False) -> Optional[AudioSound]:
        """
        Carrega um efeito sonoro com cache
        
        Args:
            sound_path: Caminho do som (ex: "sounds/collect.wav")
            force_reload: Se True, ignora cache
            
        Returns:
            AudioSound ou None se falhar
        """
        # Verifica cache
        if not force_reload and sound_path in self.sound_cache:
            return self.sound_cache[sound_path]
        
        resolved = self._resolve_path(sound_path)
        
        try:
            sound = self.loader.loadSfx(resolved)
            if sound:
                self.sound_cache[sound_path] = sound
                print(f"Som carregado: {sound_path}")
                return sound
            else:
                print(f"⚠️ Falha ao carregar som: {sound_path}")
                return None
        except Exception as e:
            print(f"Erro ao carregar som {sound_path}: {e}")
            return None
    
    def play_sound(self, sound_path: str, volume: float = 1.0) -> bool:
        """
        Carrega e reproduz um som
        
        Args:
            sound_path: Caminho do som
            volume: Volume (0.0 a 1.0)
            
        Returns:
            True se tocou, False se falhou
        """
        sound = self.load_sound(sound_path)
        if sound:
            sound.setVolume(volume)
            sound.play()
            return True
        return False
    
    # ====================================
    # MÚSICA
    # ====================================
    
    def load_music(self, music_path: str, force_reload: bool = False) -> Optional[AudioSound]:
        """
        Carrega uma música com cache
        
        Args:
            music_path: Caminho da música (ex: "music/menu.ogg")
            force_reload: Se True, ignora cache
            
        Returns:
            AudioSound ou None se falhar
        """
        # Verifica cache
        if not force_reload and music_path in self.music_cache:
            return self.music_cache[music_path]
        
        resolved = self._resolve_path(music_path)
        
        try:
            music = self.loader.loadMusic(resolved)
            if music:
                self.music_cache[music_path] = music
                print(f"Música carregada: {music_path}")
                return music
            else:
                print(f"⚠️ Falha ao carregar música: {music_path}")
                return None
        except Exception as e:
            print(f"Erro ao carregar música {music_path}: {e}")
            return None
    
    # ====================================
    # BACKGROUNDS (Imagens 2D)
    # ====================================
    
    def load_background(self, image_path: str, aspect_ratio: float) -> Optional[NodePath]:
        """
        Carrega uma imagem de fundo para render2d
        
        Args:
            image_path: Caminho da imagem
            aspect_ratio: Aspect ratio da janela
            
        Returns:
            NodePath do fundo ou None se falhar
        """
        from core.constants import MODEL_PLANE
        
        try:
            texture = self.load_texture(image_path)
            if texture is None:
                print(f"⚠️ Fundo não carregado: {image_path}")
                return None
            
            bg_model = self.load_model(MODEL_PLANE)
            if bg_model is None:
                print(f"⚠️ Modelo de plano não disponível para fundo")
                return None
            
            bg_model.setTexture(texture)
            bg_model.setScale(aspect_ratio, 1, 1)
            bg_model.setPos(0, 0, 0)
            
            print(f"Background carregado: {image_path}")
            return bg_model
            
        except Exception as e:
            print(f"Erro ao carregar background {image_path}: {e}")
            return None
    
    # ====================================
    # UTILITÁRIOS
    # ====================================
    
    def preload_level_assets(self, level_name: str):
        """
        Pré-carrega todos os assets de uma fase
        Útil para evitar lag durante gameplay
        
        Args:
            level_name: Nome da fase (ex: "netuno")
        """
        from core.constants import (
            MODEL_PLAYER, MODEL_COLLECTIBLE, MODEL_PLANE,
            TEXTURE_PLAYER, TEXTURE_COLLECTIBLE
        )
        
        print(f"Pré-carregando assets da fase: {level_name}")
        
        # Modelos comuns
        self.load_model(MODEL_PLAYER)
        self.load_model(MODEL_COLLECTIBLE)
        self.load_model(MODEL_PLANE)
        
        # Texturas comuns
        self.load_texture(TEXTURE_PLAYER)
        self.load_texture(TEXTURE_COLLECTIBLE)
        
        # Background específico da fase
        bg_path = self._resolve_path(f"imgs/{level_name}/{level_name}_fundo.png")
        if os.path.exists(bg_path):
            self.load_texture(bg_path)
        
        # Chão específico da fase
        ground_path = self._resolve_path(f"imgs/{level_name}/chao_{level_name}.png")
        if os.path.exists(ground_path):
            self.load_texture(ground_path)
        
        print(f"Assets pré-carregados: {level_name}")
    
    def _resolve_path(self, path: str) -> Filename:
        """Resolve caminho como Filename Panda3D (suporta PyInstaller)"""
        full = path
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            full = os.path.join(sys._MEIPASS, path)
        return Filename.fromOsSpecific(os.path.normpath(full))

    def clear_cache(self):
        """Limpa todos os caches (use ao mudar de fase)"""
        self.model_cache.clear()
        self.texture_cache.clear()
        # Mantém sons e músicas em cache para economizar memória
        print("Cache de modelos e texturas limpo")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """
        Retorna estatísticas do cache
        
        Returns:
            Dicionário com contagens de cada tipo
        """
        return {
            "models": len(self.model_cache),
            "textures": len(self.texture_cache),
            "sounds": len(self.sound_cache),
            "music": len(self.music_cache)
        }
    
    def print_cache_stats(self):
        """Imprime estatísticas do cache"""
        stats = self.get_cache_stats()
        print("Cache Stats:")
        print(f"   Modelos: {stats['models']}")
        print(f"   Texturas: {stats['textures']}")
        print(f"   Sons: {stats['sounds']}")
        print(f"   Músicas: {stats['music']}")


print("ResourceLoader class definida com sucesso!")