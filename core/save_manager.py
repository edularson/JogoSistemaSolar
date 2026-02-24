"""
JORNADA SOLAR - SAVE MANAGER
Gerencia salvamento e carregamento de:
- Progresso do jogador
- Recordes (highscores)
- Conquistas (achievements)
- Configurações
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime


class SaveManager:
    """
    Gerenciador de salvamento do jogo.
    Centraliza toda persistência de dados.
    """
    
    def __init__(self):
        """Inicializa o Save Manager"""
        from core.constants import (
            FILE_SAVE, FILE_CONFIG, FILE_HIGHSCORES, 
            FILE_ACHIEVEMENTS, DIFFICULTY_SETTINGS
        )
        
        self.save_file = FILE_SAVE
        self.config_file = FILE_CONFIG
        self.highscores_file = FILE_HIGHSCORES
        self.achievements_file = FILE_ACHIEVEMENTS
        
        # Estruturas de dados
        self.progress = self._load_or_create_progress()
        self.config = self._load_or_create_config()
        self.highscores = self._load_or_create_highscores()
        self.achievements = self._load_or_create_achievements()
        
        print("SaveManager inicializado")
    
    # ====================================
    # PROGRESSO DO JOGO
    # ====================================
    
    def _load_or_create_progress(self) -> Dict:
        """Carrega ou cria progresso inicial"""
        default_progress = {
            "levels_unlocked": [True] + [False] * 8,  # Só Netuno desbloqueado
            "levels_completed": [False] * 9,
            "last_level_played": 0,
            "total_playtime": 0.0,
            "game_completed": False,
            "difficulty": "normal"
        }
        
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    progress = json.load(f)
                print(f"Progresso carregado de {self.save_file}")
                return progress
            except Exception as e:
                print(f"⚠️ Erro ao carregar progresso: {e}")
                return default_progress
        else:
            print("Criando novo progresso")
            return default_progress
    
    def save_progress(self):
        """Salva progresso atual"""
        try:
            with open(self.save_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
            print(f"Progresso salvo em {self.save_file}")
            return True
        except Exception as e:
            print(f"Erro ao salvar progresso: {e}")
            return False
    
    def unlock_level(self, level_index: int):
        """
        Desbloqueia uma fase
        
        Args:
            level_index: Índice da fase (0-8)
        """
        if 0 <= level_index < 9:
            self.progress["levels_unlocked"][level_index] = True
            self.save_progress()
            print(f"Fase {level_index} desbloqueada")
    
    def complete_level(self, level_index: int):
        """
        Marca uma fase como completa
        
        Args:
            level_index: Índice da fase (0-8)
        """
        if 0 <= level_index < 9:
            self.progress["levels_completed"][level_index] = True
            
            # Desbloqueia próxima fase
            if level_index < 8:
                self.unlock_level(level_index + 1)
            
            # Se completou o Sol, marca jogo como zerado
            if level_index == 8:
                self.progress["game_completed"] = True
                self.unlock_achievement("master")
            
            self.save_progress()
            print(f"Fase {level_index} completada")
    
    def is_level_unlocked(self, level_index: int) -> bool:
        """Verifica se fase está desbloqueada"""
        if 0 <= level_index < 9:
            return self.progress["levels_unlocked"][level_index]
        return False
    
    def is_level_completed(self, level_index: int) -> bool:
        """Verifica se fase foi completada"""
        if 0 <= level_index < 9:
            return self.progress["levels_completed"][level_index]
        return False
    
    def reset_progress(self):
        """Reseta todo o progresso do jogo"""
        self.progress = self._load_or_create_progress()
        # Limpa também os recordes
        self.highscores = self._load_or_create_highscores()
        self.achievements = self._load_or_create_achievements()
        
        self.save_progress()
        self.save_highscores()
        self.save_achievements()
        
        print("Progresso resetado!")
    
    # ====================================
    # RECORDES (HIGHSCORES)
    # ====================================
    
    def _load_or_create_highscores(self) -> Dict:
        """Carrega ou cria recordes iniciais"""
        level_names = ["netuno", "urano", "saturno", "jupiter", "marte", 
                      "terra", "venus", "mercurio", "sol"]
        
        default_highscores = {
            level: {
                "score": 0,
                "time": 999.9,
                "no_damage": False,
                "challenge_completed": False,
                "date": None
            } for level in level_names
        }
        
        if os.path.exists(self.highscores_file):
            try:
                with open(self.highscores_file, 'r') as f:
                    highscores = json.load(f)
                print(f"Recordes carregados de {self.highscores_file}")
                return highscores
            except Exception as e:
                print(f"⚠️ Erro ao carregar recordes: {e}")
                return default_highscores
        else:
            return default_highscores
    
    def save_highscores(self):
        """Salva recordes atuais"""
        try:
            with open(self.highscores_file, 'w') as f:
                json.dump(self.highscores, f, indent=2)
            print(f"Recordes salvos em {self.highscores_file}")
            return True
        except Exception as e:
            print(f"Erro ao salvar recordes: {e}")
            return False
    
    def update_highscore(self, level_name: str, score: int, time: float, 
                        no_damage: bool, challenge_completed: bool) -> bool:
        """
        Atualiza recorde se for melhor
        
        Args:
            level_name: Nome da fase
            score: Pontuação obtida
            time: Tempo em segundos
            no_damage: Se completou sem dano
            challenge_completed: Se completou desafio
            
        Returns:
            True se bateu recorde de score
        """
        is_new_highscore = False
        
        if level_name in self.highscores:
            current = self.highscores[level_name]
            
            # Verifica se bateu recorde de pontuação
            if score > current["score"]:
                current["score"] = score
                current["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                is_new_highscore = True
                print(f"NOVO RECORDE em {level_name}: {score} pontos!")
            
            # Atualiza melhor tempo
            if time < current["time"]:
                current["time"] = time
                print(f"Novo melhor tempo em {level_name}: {time:.2f}s!")
            
            # Marca conquistas especiais
            if no_damage and not current["no_damage"]:
                current["no_damage"] = True
                self.unlock_achievement("no_damage")
            
            if challenge_completed and not current["challenge_completed"]:
                current["challenge_completed"] = True
            
            self.save_highscores()
        
        return is_new_highscore
    
    def get_highscore(self, level_name: str) -> Optional[Dict]:
        """Retorna recorde de uma fase"""
        return self.highscores.get(level_name)
    
    # ====================================
    # CONQUISTAS (ACHIEVEMENTS)
    # ====================================
    
    def _load_or_create_achievements(self) -> Dict:
        """Carrega ou cria conquistas iniciais"""
        from core.constants import ACHIEVEMENTS
        
        default_achievements = {
            key: {
                "unlocked": False,
                "unlock_date": None
            } for key in ACHIEVEMENTS.keys()
        }
        
        if os.path.exists(self.achievements_file):
            try:
                with open(self.achievements_file, 'r') as f:
                    achievements = json.load(f)
                print(f"Conquistas carregadas de {self.achievements_file}")
                return achievements
            except Exception as e:
                print(f"⚠️ Erro ao carregar conquistas: {e}")
                return default_achievements
        else:
            return default_achievements
    
    def save_achievements(self):
        """Salva conquistas atuais"""
        try:
            with open(self.achievements_file, 'w') as f:
                json.dump(self.achievements, f, indent=2)
            print(f"Conquistas salvas em {self.achievements_file}")
            return True
        except Exception as e:
            print(f"Erro ao salvar conquistas: {e}")
            return False
    
    def unlock_achievement(self, achievement_key: str) -> bool:
        """
        Desbloqueia uma conquista
        
        Args:
            achievement_key: Chave da conquista
            
        Returns:
            True se foi desbloqueada agora (não antes)
        """
        from core.constants import ACHIEVEMENTS
        
        if achievement_key in self.achievements:
            if not self.achievements[achievement_key]["unlocked"]:
                self.achievements[achievement_key]["unlocked"] = True
                self.achievements[achievement_key]["unlock_date"] = \
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_achievements()
                
                achievement_info = ACHIEVEMENTS[achievement_key]
                print(f"CONQUISTA DESBLOQUEADA: {achievement_info['icon']} {achievement_info['name']}")
                return True
        
        return False
    
    def is_achievement_unlocked(self, achievement_key: str) -> bool:
        """Verifica se conquista está desbloqueada"""
        if achievement_key in self.achievements:
            return self.achievements[achievement_key]["unlocked"]
        return False
    
    def get_achievement_progress(self) -> Dict[str, int]:
        """
        Retorna progresso geral de conquistas
        
        Returns:
            Dict com total e desbloqueadas
        """
        total = len(self.achievements)
        unlocked = sum(1 for a in self.achievements.values() if a["unlocked"])
        
        return {
            "total": total,
            "unlocked": unlocked,
            "percentage": (unlocked / total * 100) if total > 0 else 0
        }
    
    # ====================================
    # CONFIGURAÇÕES
    # ====================================
    
    def _load_or_create_config(self) -> Dict:
        """Carrega ou cria configurações padrão"""
        from core.constants import DEFAULT_MUSIC_VOLUME, DEFAULT_SFX_VOLUME
        
        default_config = {
            "music_volume": DEFAULT_MUSIC_VOLUME,
            "sfx_volume": DEFAULT_SFX_VOLUME,
            "fullscreen": True,
            "show_fps": False,
            "tutorial_completed": False,
            "language": "pt-br"
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                print(f"⚙️ Configurações carregadas de {self.config_file}")
                return config
            except Exception as e:
                print(f"⚠️ Erro ao carregar configurações: {e}")
                return default_config
        else:
            return default_config
    
    def save_config(self):
        """Salva configurações atuais"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"Configurações salvas em {self.config_file}")
            return True
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
            return False
    
    def update_config(self, key: str, value: Any):
        """
        Atualiza uma configuração
        
        Args:
            key: Chave da configuração
            value: Novo valor
        """
        self.config[key] = value
        self.save_config()
        print(f"⚙️ Configuração atualizada: {key} = {value}")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Retorna valor de uma configuração
        
        Args:
            key: Chave da configuração
            default: Valor padrão se não existir
            
        Returns:
            Valor da configuração ou default
        """
        return self.config.get(key, default)
    
    # ====================================
    # UTILITÁRIOS
    # ====================================
    
    def get_all_stats(self) -> Dict:
        """
        Retorna todas as estatísticas do jogador
        
        Returns:
            Dicionário completo com stats
        """
        achievement_progress = self.get_achievement_progress()
        levels_completed_count = sum(self.progress["levels_completed"])
        
        return {
            "progress": self.progress,
            "achievement_progress": achievement_progress,
            "levels_completed": levels_completed_count,
            "game_completed": self.progress["game_completed"],
            "total_playtime": self.progress["total_playtime"],
            "highscores": self.highscores
        }
    
    def export_save(self, filepath: str = "jornada_solar_backup.json"):
        """
        Exporta todos os dados para backup
        
        Args:
            filepath: Caminho do arquivo de backup
        """
        try:
            backup_data = {
                "progress": self.progress,
                "highscores": self.highscores,
                "achievements": self.achievements,
                "config": self.config,
                "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(filepath, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            print(f"Backup exportado para {filepath}")
            return True
        except Exception as e:
            print(f"Erro ao exportar backup: {e}")
            return False
    
    def import_save(self, filepath: str):
        """
        Importa dados de um backup
        
        Args:
            filepath: Caminho do arquivo de backup
        """
        try:
            with open(filepath, 'r') as f:
                backup_data = json.load(f)
            
            self.progress = backup_data.get("progress", self.progress)
            self.highscores = backup_data.get("highscores", self.highscores)
            self.achievements = backup_data.get("achievements", self.achievements)
            self.config = backup_data.get("config", self.config)
            
            # Salva tudo
            self.save_progress()
            self.save_highscores()
            self.save_achievements()
            self.save_config()
            
            print(f"Backup importado de {filepath}")
            return True
        except Exception as e:
            print(f"Erro ao importar backup: {e}")
            return False


print("SaveManager class definida com sucesso!")