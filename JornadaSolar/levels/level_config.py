"""
JORNADA SOLAR - LEVEL CONFIGURATIONS
Configurações de todas as 9 fases do jogo
Cada fase define seu objetivo, velocidades, spawn rates e mecânicas especiais
"""

from panda3d.core import Vec4


# ====================================
# CONFIGURAÇÕES POR FASE
# ====================================

LEVEL_CONFIGS = {
    
    # ========== NETUNO (Fase 1 - Tutorial) ==========
    "netuno": {
        "index": 0,
        "name": "netuno",
        "display_name": "Netuno",
        "subtitle": "Chuva de Cristais",
        "objective_count": 20,
        "spawn_interval_collectible": 1.0,
        "spawn_interval_hazard": 999,  # Sem perigos pq é tutorial
        "spawn_interval_powerup": 999,  # Sem power-ups
        "collectible_speed": 0.05,
        "hazard_speed": 0.0,
        "has_corrupted": False,
        "has_powerups": False,
        "special_mechanic": None,
        "lighting": {
            "ambient": Vec4(0.6, 0.6, 0.6, 1),
            "directional": Vec4(0.8, 0.8, 0.7, 1)
        },
        "description": "Fase introdutória. Colete 20 cristais roxos.",
        "tip": "Use A/D para mover horizontalmente e W/S verticalmente."
    },
    
    # ========== URANO (Fase 2) ==========
    "urano": {
        "index": 1,
        "name": "urano",
        "display_name": "Urano",
        "subtitle": "Ventos Laterais",
        "objective_count": 20,
        "spawn_interval_collectible": 1.0,
        "spawn_interval_hazard": 999,  # Sem perigos ainda
        "spawn_interval_powerup": 999,
        "collectible_speed": 0.05,
        "hazard_speed": 0.0,
        "has_corrupted": False,
        "has_powerups": False,
        "special_mechanic": "wind",
        "wind_force": 0.05,
        "wind_change_interval": 10.0,
        "lighting": {
            "ambient": Vec4(0.4, 0.7, 0.9, 1),
            "directional": Vec4(0.6, 0.9, 1.0, 1)
        },
        "description": "Vento lateral empurra a nave. Adapte seu movimento!",
        "tip": "O vento muda de direção a cada 10 segundos."
    },
    
    # ========== SATURNO (Fase 3) ==========
    "saturno": {
        "index": 2,
        "name": "saturno",
        "display_name": "Saturno",
        "subtitle": "Chuva de Detritos",
        "objective_count": 20,
        "spawn_interval_collectible": 1.0,
        "spawn_interval_hazard": 1.5,
        "spawn_interval_powerup": 999,
        "collectible_speed": 0.05,
        "hazard_speed": 0.06,
        "has_corrupted": False,
        "has_powerups": False,
        "special_mechanic": None,
        "lighting": {
            "ambient": Vec4(0.8, 0.75, 0.5, 1),
            "directional": Vec4(1.0, 0.95, 0.8, 1)
        },
        "description": "Meteoros aparecem! Desvie enquanto coleta fragmentos.",
        "tip": "Meteoros cinzas causam dano. Evite-os!"
    },
    
    # ========== JÚPITER (Fase 4) ==========
    "jupiter": {
        "index": 3,
        "name": "jupiter",
        "display_name": "Júpiter",
        "subtitle": "Tempestade Elétrica",
        "objective_count": 20,
        "spawn_interval_collectible": 1.0,
        "spawn_interval_hazard": 4,
        "spawn_interval_powerup": 999,
        "collectible_speed": 0.05,
        "hazard_speed": 0.06,
        "has_corrupted": False,
        "has_powerups": False,
        "special_mechanic": "lightning",
        "lightning_spawn_interval": 8.0,
        "lightning_speed": 0.07,
        "lighting": {
            "ambient": Vec4(0.9, 0.6, 0.3, 1),
            "directional": Vec4(1.0, 0.8, 0.5, 1)
        },
        "description": "Raios elétricos se movem horizontalmente de forma imprevisível.",
        "tip": "Raios mudam de direção! Fique atento."
    },
    
    # ========== MARTE (Fase 5) ==========
    "marte": {
        "index": 4,
        "name": "marte",
        "display_name": "Marte",
        "subtitle": "Coleta Seletiva",
        "objective_count": 20,
        "spawn_interval_collectible": 1.0,
        "spawn_interval_hazard": 1.6,
        "spawn_interval_powerup": 999,
        "collectible_speed": 0.05,
        "hazard_speed": 0.06,
        "has_corrupted": True,
        "corrupted_chance": 0.3,  # 30% de fragmentos corrompidos
        "has_powerups": False,
        "special_mechanic": "corrupted_fragments",
        "lighting": {
            "ambient": Vec4(0.7, 0.3, 0.2, 1),
            "directional": Vec4(1.0, 0.6, 0.4, 1)
        },
        "description": "Fragmentos corrompidos (vermelhos piscantes) deixam você lento!",
        "tip": "Evite fragmentos vermelhos - eles são armadilhas!"
    },
    
    # ========== TERRA (Fase 6) ==========
    "terra": {
        "index": 5,
        "name": "terra",
        "display_name": "Terra",
        "subtitle": "Defesa Orbital",
        "objective_count": 30,  
        "spawn_interval_collectible": 1.0,
        "spawn_interval_hazard": 1.6,      
        "spawn_interval_powerup": 8.0,    
        "collectible_speed": 0.05,         
        "hazard_speed": 0.07,
        "has_corrupted": False,
        "has_powerups": True,
        "special_mechanic": "space_trash",
        "lighting": {
            "ambient": Vec4(0.6, 0.7, 1.0, 1),
            "directional": Vec4(0.9, 0.95, 1.0, 1)
        },
        "description": "Lixo espacial e power-ups! Use escudo, imã e slow-motion.",
        "tip": "Power-ups: Azul=Escudo, Verde=Imã, Amarelo=Slow-Motion"
    },
    
    # ========== VÊNUS (Fase 7) ==========
    "venus": {
        "index": 6,
        "name": "venus",
        "display_name": "Vênus",
        "subtitle": "Chuva Ácida",
        "objective_count": 40,
        "spawn_interval_collectible": 1.0,
        "spawn_interval_hazard": 1.7,
        "spawn_interval_powerup": 6.0,
        "collectible_speed": 0.10,
        "hazard_speed": 0.12,
        "has_corrupted": False,
        "has_powerups": True,
        "special_mechanic": "acid_rain",
        "acid_spawn_interval": 2.0,
        "acid_speed": 0.14,
        "acid_pool_duration": 6.0,
        "acid_pool_damage_interval": 0.8,
        "lighting": {
            "ambient": Vec4(0.9, 0.8, 0.4, 1),
            "directional": Vec4(1.0, 0.9, 0.5, 1)
        },
        "description": "Gotas de ácido criam poças no chão que causam dano contínuo!",
        "tip": "Continue se movendo para não ser atingido pelas poças!"
    },
    
    # ========== MERCÚRIO (Fase 8) ==========
    "mercurio": {
        "index": 7,
        "name": "mercurio",
        "display_name": "Mercúrio",
        "subtitle": "Inferno de Velocidade",
        "objective_count": 40,
        "spawn_interval_collectible": 0.8,
        "spawn_interval_hazard": 1.2,
        "spawn_interval_powerup": 5.0,
        "collectible_speed": 0.10, 
        "hazard_speed": 0.12,
        "has_corrupted": True,
        "corrupted_chance": 0.3,
        "has_powerups": True,
        "special_mechanic": "extreme_speed",
        "lighting": {
            "ambient": Vec4(0.4, 0.4, 0.45, 1),
            "directional": Vec4(0.8, 0.75, 0.7, 1)
        },
        "description": "TUDO cai 2x mais rápido! Teste de reflexos extremo!",
        "tip": "Use slow-motion para ter controle. Foque nos fragmentos roxos!"
    },
    
    # ========== SOL (Fase 9 - BOSS FINAL) ==========
    "sol": {
        "index": 8,
        "name": "sol",
        "display_name": "Sol",
        "subtitle": "Onda de Erupção (BOSS)",
        "objective_count": 40,
        "spawn_interval_collectible": 0.8,
        "spawn_interval_hazard": 1.2,
        "spawn_interval_powerup": 5.0,
        "collectible_speed": 0.10,
        "hazard_speed": 0.12,
        "has_corrupted": True,
        "corrupted_chance": 0.3,
        "has_powerups": True,
        "special_mechanic": "solar_eruption",
        "eruption_interval": 15.0,
        "eruption_warning_time": 3.0,
        "eruption_duration": 3.0,
        "num_shadows": 2,
        "shadow_scale": 0.4,
        "shadow_radius": 1.0,
        "beam_height": 20.0,
        "lighting": {
            "ambient": Vec4(1.0, 0.85, 0.5, 1),
            "directional": Vec4(1.0, 0.9, 0.6, 1)
        },
        "description": "BOSS FINAL! Erupções solares varrem a tela. Esconda-se nas sombras!",
        "tip": "Quando o aviso aparecer, procure as áreas escuras no chão!"
    }
}


# ====================================
# FUNÇÕES UTILITÁRIAS
# ====================================

def get_level_config(level_name: str) -> dict:
    """
    Retorna configuração de uma fase
    
    Args:
        level_name: Nome da fase
        
    Returns:
        Dicionário de configuração
    """
    if level_name in LEVEL_CONFIGS:
        return LEVEL_CONFIGS[level_name].copy()
    else:
        print(f"⚠️ Configuração não encontrada para: {level_name}")
        return LEVEL_CONFIGS["netuno"].copy()  # Fallback


def get_all_level_names() -> list:
    """Retorna lista com nomes de todas as fases"""
    return list(LEVEL_CONFIGS.keys())


def get_level_by_index(index: int) -> dict:
    """
    Retorna configuração por índice
    
    Args:
        index: Índice da fase (0-8)
        
    Returns:
        Dicionário de configuração
    """
    for config in LEVEL_CONFIGS.values():
        if config["index"] == index:
            return config.copy()
    
    return LEVEL_CONFIGS["netuno"].copy()


def get_next_level_name(current_level: str) -> str:
    """
    Retorna nome da próxima fase
    
    Args:
        current_level: Nome da fase atual
        
    Returns:
        Nome da próxima fase ou None se for a última
    """
    if current_level not in LEVEL_CONFIGS:
        return None
    
    current_index = LEVEL_CONFIGS[current_level]["index"]
    next_index = current_index + 1
    
    if next_index >= 9:
        return None
    
    return get_level_by_index(next_index)["name"]


def print_level_info(level_name: str):
    """
    Imprime informações de uma fase (debug)
    
    Args:
        level_name: Nome da fase
    """
    if level_name not in LEVEL_CONFIGS:
        print(f"Fase não encontrada: {level_name}")
        return
    
    config = LEVEL_CONFIGS[level_name]
    
    print(f"\n{'='*50}")
    print(f"FASE: {config['display_name']} ({config['name']})")
    print(f"{'='*50}")
    print(f"Subtítulo: {config['subtitle']}")
    print(f"Objetivo: Coletar {config['objective_count']} fragmentos")
    print(f"Mecânica Especial: {config.get('special_mechanic', 'Nenhuma')}")
    print(f"Descrição: {config['description']}")
    print(f"Dica: {config['tip']}")
    print(f"{'='*50}\n")


def print_all_levels():
    """Imprime informações de todas as fases"""
    print("\n" + "="*60)
    print("JORNADA SOLAR - TODAS AS FASES")
    print("="*60)
    
    for level_name in get_all_level_names():
        config = LEVEL_CONFIGS[level_name]
        print(f"{config['index'] + 1}. {config['display_name']:12} - {config['subtitle']}")
    
    print("="*60 + "\n")


# ====================================
# VALIDAÇÃO (executado ao importar)
# ====================================

def validate_configs():
    """Valida se todas as configurações estão corretas"""
    required_keys = [
        "index", "name", "display_name", "subtitle", "objective_count",
        "spawn_interval_collectible", "spawn_interval_hazard",
        "spawn_interval_powerup", "collectible_speed", "hazard_speed",
        "has_corrupted", "has_powerups", "special_mechanic",
        "lighting", "description", "tip"
    ]
    
    all_valid = True
    
    for level_name, config in LEVEL_CONFIGS.items():
        # Verifica chaves obrigatórias
        for key in required_keys:
            if key not in config:
                print(f"Fase '{level_name}' está faltando a chave: {key}")
                all_valid = False
    
    if all_valid:
        print("Todas as configurações de fases são válidas!")
    else:
        print("⚠️ Algumas configurações precisam de correção")
    
    return all_valid


# Valida ao importar
validate_configs()

print("LevelConfig carregado com sucesso!")
print(f"{len(LEVEL_CONFIGS)} fases configuradas")