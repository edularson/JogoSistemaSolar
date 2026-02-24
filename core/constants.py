"""
JORNADA SOLAR - CONSTANTES DO JOGO
Híbrido: Suporta tanto importação direta quanto via Classe
"""
import sys
from panda3d.core import Vec4

# ============================================
# 1. DEFINIÇÕES GLOBAIS (O QUE O JOGO USA)
# ============================================

# JANELA
WINDOW_TITLE = "Jornada Solar"
FULLSCREEN = True
TARGET_FPS = 60

# GAMEPLAY
PLAYER_POSITION_Y = 0
PLAYER_POSITION_Z_START = -7.5
PLAYER_MIN_Z = -7.5
PLAYER_MAX_Z = 5.0
PLAYER_MIN_X = -15
PLAYER_MAX_X = 15
PLAYER_HORIZONTAL_SPEED = 0.15
PLAYER_COLLISION_RADIUS = 15
PLAYER_SCALE = 0.05

# PONTUAÇÃO
SCORE_FRAGMENT = 100
SCORE_COMBO_BONUS = 50
SCORE_NO_DAMAGE_BONUS = 200
SCORE_TIME_BONUS = 10
COMBO_TIME_WINDOW = 1.5

# DIFICULDADE
DIFFICULTY_SETTINGS = {
    "facil": {"lives": 5, "speed_multiplier": 0.8, "score_multiplier": 0.8},
    "normal": {"lives": 3, "speed_multiplier": 1.0, "score_multiplier": 1.0},
    "dificil": {"lives": 1, "speed_multiplier": 1.3, "score_multiplier": 1.5}
}

# POWER-UPS
POWERUP_DURATION_SHIELD = 1
POWERUP_DURATION_MAGNET = 5.0
POWERUP_DURATION_SLOWMOTION = 3.0
POWERUP_MAGNET_RADIUS = 10.0
POWERUP_MAGNET_FORCE = 6.0
POWERUP_SLOWMOTION_MULTIPLIER = 0.4
DEBUFF_SLOW_MULTIPLIER = 0.4
DEBUFF_SLOW_DURATION = 3.0

# SPAWN E VELOCIDADE
SPAWN_INTERVAL_COLLECTIBLE = 1.0
SPAWN_INTERVAL_HAZARD = 1.5
SPAWN_INTERVAL_POWERUP = 6.0
VELOCITY_COLLECTIBLE_BASE = 0.05
VELOCITY_HAZARD_BASE = 0.06
VELOCITY_POWERUP_BASE = 0.05

SPEED_MULTIPLIER_BY_LEVEL = {
    "netuno": 1.0, "urano": 1.0, "saturno": 1.0,
    "jupiter": 1.0, "marte": 1.0, "terra": 1.0,
    "venus": 1.3, "mercurio": 1.3, "sol": 1.3
}

# MODELOS
MODEL_PLAYER = "models/fighter"
MODEL_COLLECTIBLE = "models/purplecrystal"
MODEL_COLLECTIBLE_CORRUPTED = "models/redcrystal"
MODEL_HAZARD_METEOR = "models/goldcrystal"
MODEL_HAZARD_TRASH_1 = "models/boeing707"
MODEL_HAZARD_TRASH_2 = "models/strecher"
MODEL_HAZARD_TRASH_3 = "models/r2d2"
MODEL_POWERUP_SHIELD = "models/sphere"
MODEL_LIGHTNING = "models/square"
TEXTURE_LIGHTNING = "imgs/lightning.png"
MODEL_ACID_DROP = "models/sphere"
MODEL_ACID_SPLASH = "models/plants1"
MODEL_PLANE = "models/square"

# TEXTURAS
TEXTURE_PLAYER = "models/texturemap.png"
TEXTURE_COLLECTIBLE = "models/purple.png"
TEXTURE_COLLECTIBLE_CORRUPTED = "imgs/red.png"
TEXTURE_TRASH_1 = "imgs/texturemap.png"
TEXTURE_TRASH_2 = "imgs/bed-material-12-cl.png"
TEXTURE_TRASH_3 = "imgs/r2.png"

# CORES
COLOR_WHITE = Vec4(1, 1, 1, 1)
COLOR_BLACK = Vec4(0, 0, 0, 1)
COLOR_RED = Vec4(1, 0, 0, 1)
COLOR_GREEN = Vec4(0, 1, 0, 1)
COLOR_BLUE = Vec4(0, 0, 1, 1)
COLOR_YELLOW = Vec4(1, 1, 0, 1)
COLOR_PURPLE = Vec4(0.5, 0, 0.5, 1)
COLOR_GOLD = Vec4(1, 0.84, 0, 1)

COLOR_NETUNO = Vec4(0, 0, 0.545, 1)
COLOR_URANO = Vec4(0, 1, 1, 1)
COLOR_SATURNO = Vec4(0.941, 0.902, 0.549, 1)
COLOR_JUPITER = Vec4(0.824, 0.412, 0.118, 1)
COLOR_MARTE = Vec4(0.698, 0.133, 0.133, 1)
COLOR_TERRA = Vec4(0, 0.392, 1, 1)
COLOR_VENUS = Vec4(0.855, 0.647, 0.125, 1)
COLOR_MERCURIO = Vec4(0.663, 0.663, 0.663, 1)
COLOR_SOL = Vec4(1, 0.271, 0, 1)

# ARQUIVOS
FILE_SAVE = "save.json"
FILE_CONFIG = "config.json"
FILE_HIGHSCORES = "highscores.json"
FILE_ACHIEVEMENTS = "achievements.json"

# CONQUISTAS
ACHIEVEMENTS = {
    "first_blood": {"name": "Primeira Vitória", "description": "Complete a primeira fase", "icon": "🏆"},
    "no_damage": {"name": "Intocável", "description": "Complete uma fase sem tomar dano", "icon": "🛡️"},
    "speed_demon": {"name": "Demônio da Velocidade", "description": "Complete Mercúrio em menos de 2 minutos", "icon": "⚡"},
    "collector": {"name": "Colecionador", "description": "Pegue todos os power-ups em uma fase", "icon": "💎"},
    "master": {"name": "Mestre Solar", "description": "Zere o jogo", "icon": "⭐"},
    "combo_master": {"name": "Combo Master", "description": "Faça um combo de 10 fragmentos", "icon": "🔥"},
    "perfectionist": {"name": "Perfeccionista", "description": "Obtenha 100% dos fragmentos em uma fase", "icon": "💯"},
    "survivor": {"name": "Sobrevivente", "description": "Complete o Sol (Boss final)", "icon": "☀️"}
}

# DESAFIOS
CHALLENGES = {
    "netuno": {"name": "Estático", "description": "Colete sem se mover no eixo Z", "reward": 500},
    "urano": {"name": "Contra a Corrente", "description": "Colete indo sempre contra o vento", "reward": 500},
    "saturno": {"name": "Reflexos Rápidos", "description": "Complete sem deixar nenhum meteoro passar", "reward": 500},
    "jupiter": {"name": "Desviando Raios", "description": "Não seja atingido por nenhum raio", "reward": 500},
    "marte": {"name": "Seleção Perfeita", "description": "Não pegue nenhum fragmento corrompido", "reward": 500},
    "terra": {"name": "Purista", "description": "Complete sem usar power-ups", "reward": 500},
    "venus": {"name": "Passos Certeiros", "description": "Não seja atingido por poças de ácido", "reward": 500},
    "mercurio": {"name": "Velocista", "description": "Complete em menos de 1 minuto", "reward": 1000},
    "sol": {"name": "Sombras Perfeitas", "description": "Fique apenas nas sombras durante erupções", "reward": 1500}
}

# SONS
SOUNDS = {
    "collect": "sounds/collect.wav", # tem
    "damage": "sounds/damage.wav", # tem
    "powerup": "sounds/powerup.wav", # tem
    "victory": "sounds/victory.wav", # tem
    "defeat": "sounds/defeat.wav",
    "menu_click": "sounds/click.wav", #tem
    "combo": "sounds/combo.wav", # tem
    "achievement": "sounds/achievement.wav", #tem
    "warning": "sounds/warning.wav"
}

MUSIC = {
    "menu": "music/menu.mp3",
    "lobby": "music/lobby.mp3",
    "outer_planets": "music/outer_space.ogg",
    "inner_planets": "music/intense.ogg",
    "boss": "music/boss.ogg",
    "victory": "music/victory.mp3"
}

DEFAULT_MUSIC_VOLUME = 0.7
DEFAULT_SFX_VOLUME = 0.8

# UI
UI_MESSAGES = {
    "paused": "JOGO PAUSADO",
    "victory": "FASE CONCLUÍDA!",
    "defeat": "GAME OVER",
    "loading": "Carregando...",
    "press_enter": "Pressione ENTER para continuar",
    "press_esc": "Pressione ESC para voltar",
    "new_highscore": "NOVO RECORDE!",
    "achievement_unlocked": "CONQUISTA DESBLOQUEADA!",
    "challenge_completed": "DESAFIO CONCLUÍDO!"
}

# TUTORIAL
TUTORIAL_STEPS = [
    {"text": "Use A e D para mover horizontalmente", "duration": 3.0},
    {"text": "Use W e S para mover verticalmente", "duration": 3.0},
    {"text": "Colete os fragmentos roxos!", "duration": 3.0},
    {"text": "Evite os meteoros cinzas!", "duration": 3.0},
    {"text": "Pressione P para pausar", "duration": 2.0}
]

CAMERA_DEFAULT_POS = (0, -30, 5)
CAMERA_SHAKE_INTENSITY = 0.3
CAMERA_SHAKE_DURATION = 0.2
PARTICLE_COUNT_COLLECT = 15
PARTICLE_COUNT_DAMAGE = 10
PARTICLE_COUNT_POWERUP = 20
PARTICLE_LIFETIME = 0.5
DEBUG_MODE = False
SHOW_FPS = False
SHOW_COLLIDERS = False
SHOW_SPAWNTIMERS = False

# ============================================
# 2. CLASSE DE COMPATIBILIDADE (O QUE O TESTE USA)
# ============================================
class Constants:
    pass

# Magia do Python: Copia todas as variáveis acima para dentro da Classe automaticamente
current_module = sys.modules[__name__]
for var_name, var_value in list(vars(current_module).items()):
    if var_name.isupper(): # Pega apenas as constantes (letras maiúsculas)
        setattr(Constants, var_name, var_value)

print("Constants.py (Híbrido) carregado!")