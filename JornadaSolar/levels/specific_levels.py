"""
JORNADA SOLAR - SPECIFIC LEVELS
Classes específicas de cada fase
Herdam de BaseLevel e implementam apenas mecânicas únicas
Adaptado para receber o 'app' do State Manager
"""

from core.base_level import BaseLevel
from levels.level_config import get_level_config
from panda3d.core import Vec3, Vec4
import random


# ====================================
# FASE 1: NETUNO (Tutorial)
# ====================================

class NetunoLevel(BaseLevel):
    """Fase tutorial - apenas coleta básica"""
    
    def __init__(self, app):
        config = get_level_config("netuno")
        super().__init__(app, config)
        print("Fase Netuno carregada (Tutorial)")


# ====================================
# FASE 2: URANO (Vento Lateral)
# ====================================

class UranoLevel(BaseLevel):
    """Fase com vento lateral que muda de direção"""
    
    def __init__(self, app):
        config = get_level_config("urano")
        super().__init__(app, config)
        
        # Estado do vento
        self.wind_direction = 1  # 1 = direita, -1 = esquerda
        self.wind_timer = 0.0
        self.wind_force = config.get("wind_force", 0.05)
        self.wind_change_interval = config.get("wind_change_interval", 10.0)
        
        # UI do vento
        self.wind_indicator = self.ui_manager.create_text(
            "Vento: →",
            (-1.3, 0.6)
        )
        
        print("Fase Urano carregada (Vento Lateral)")
    
    def game_loop(self, task):
        """Override do game loop para adicionar vento"""
        if self.is_paused or self.is_game_over:
            return task.cont
        
        dt = self.clock.getDt()
        
        # Atualiza timer do vento
        self.wind_timer += dt
        if self.wind_timer >= self.wind_change_interval:
            self.wind_direction *= -1
            self.wind_timer = 0.0
            
            # Atualiza UI
            wind_text = "Vento: →" if self.wind_direction > 0 else "Vento: ←"
            self.wind_indicator.setText(wind_text)
        
        # Aplica força do vento no jogador
        self.player.apply_external_force(self.wind_direction * self.wind_force, 0)
        
        # Chama game loop base
        return super().game_loop(task)


# ====================================
# FASE 3: SATURNO (Básico com meteoros)
# ====================================

class SaturnoLevel(BaseLevel):
    """Fase básica com meteoros"""
    
    def __init__(self, app):
        config = get_level_config("saturno")
        super().__init__(app, config)
        print("Fase Saturno carregada (Meteoros)")


# ====================================
# FASE 4: JÚPITER (Raios Elétricos)
# ====================================

class JupiterLevel(BaseLevel):
    """Fase com raios elétricos que se movem horizontalmente"""
    
    def __init__(self, app):
        config = get_level_config("jupiter")
        super().__init__(app, config)
        
        # Sobrescreve intervalo de hazard para raios
        self.spawn_interval_hazard = config.get("lightning_spawn_interval", 4.0)
        
        print("Fase Júpiter carregada (Raios)")
    
    def create_hazard(self):
        """Cria raios ao invés de meteoros"""
        from entities.game_entities import Hazard
        from core.constants import PLAYER_POSITION_Y
        
        x_pos = random.uniform(-15, 15)
        pos = Vec3(x_pos, PLAYER_POSITION_Y, 5.5)
        
        hazard = Hazard(
            self.resource_loader,
            self.collision_manager,
            pos,
            hazard_type="lightning"  # Tipo específico
        )
        hazard.node.reparentTo(self.app.render)
        
        # Escala especial para raios (compridos verticalmente)
        hazard.node.setScale(0.1, 0.012, 25)
        
        self.hazards.append(hazard)


# ====================================
# FASE 5: MARTE (Fragmentos Corrompidos)
# ====================================

class MarteLevel(BaseLevel):
    """Fase com fragmentos corrompidos que deixam lento"""
    
    def __init__(self, app):
        config = get_level_config("marte")
        super().__init__(app, config)
        
        self.corrupted_chance = config.get("corrupted_chance", 0.3)
        
        print("Fase Marte carregada (Fragmentos Corrompidos)")
    
    def create_collectible(self):
        """30% de chance de spawnar fragmento corrompido"""
        from entities.game_entities import Collectible
        from core.constants import PLAYER_POSITION_Y
        
        x_pos = random.uniform(-15, 15)
        pos = Vec3(x_pos, PLAYER_POSITION_Y, 5)
        
        # 30% corrompido
        is_corrupted = random.random() < self.corrupted_chance
        
        collectible = Collectible(
            self.resource_loader,
            self.collision_manager,
            pos,
            is_corrupted=is_corrupted
        )
        collectible.node.reparentTo(self.app.render)
        self.collectibles.append(collectible)


# ====================================
# FASE 6: TERRA (Power-ups + Lixo Espacial)
# ====================================

class TerraLevel(BaseLevel):
    """Fase com power-ups e lixo espacial variado"""
    
    def __init__(self, app): # Adicionado o parâmetro app
        config = get_level_config("terra")
        super().__init__(app, config)
        print("Fase Terra carregada (Power-ups)")
    
    def create_hazard(self):
        """Cria lixo espacial variado"""
        from entities.game_entities import Hazard
        from core.constants import PLAYER_POSITION_Y
        
        x_pos = random.uniform(-15, 15)
        pos = Vec3(x_pos, PLAYER_POSITION_Y, 5.5)
        
        hazard = Hazard(
            self.resource_loader,
            self.collision_manager,
            pos,
            hazard_type="trash"
        )
        # Ajustado para usar self.app.render como nas outras fases
        hazard.node.reparentTo(self.app.render)
        self.hazards.append(hazard)


# ====================================
# FASE 7: VÊNUS (Chuva Ácida)
# ====================================

class VenusLevel(BaseLevel):
    """Fase com gotas de ácido que criam poças no chão"""
    
    def __init__(self, app): # Adicionado o parâmetro app
        config = get_level_config("venus")
        super().__init__(app, config)
        
        # Lista de poças ácidas
        self.acid_pools = []
        
        # Timer de spawn de ácido
        self.acid_spawn_timer = 0
        self.acid_spawn_interval = config.get("acid_spawn_interval", 2.0)
        
        # Configurações de ácido
        self.acid_pool_duration = config.get("acid_pool_duration", 6.0)
        self.acid_damage_interval = config.get("acid_pool_damage_interval", 0.8)
        self.last_pool_damage_time = 0.0
        
        # Ajustado para usar self.app.taskMgr
        self.app.taskMgr.add(self.spawn_acid_task, "SpawnAcidTask")
        
        print("Fase Vênus carregada (Chuva Ácida)")
    
    def spawn_acid_task(self, task):
        """Task de spawn de gotas ácidas"""
        if self.is_paused or self.is_game_over:
            return task.cont
        
        if self.player.is_alive:
            # Usando o relógio da classe base para consistência
            dt = self.clock.getDt()
            if self.player.slowmotion_active:
                from core.constants import POWERUP_SLOWMOTION_MULTIPLIER
                dt *= POWERUP_SLOWMOTION_MULTIPLIER
            
            self.acid_spawn_timer += dt
            
            if self.acid_spawn_timer >= self.acid_spawn_interval:
                self.create_acid_drop()
                self.acid_spawn_timer = 0
        
        return task.cont
    
    def create_acid_drop(self):
        """Cria gota de ácido"""
        from entities.game_entities import Hazard
        from core.constants import PLAYER_POSITION_Y
        
        x_pos = random.uniform(-15, 15)
        pos = Vec3(x_pos, PLAYER_POSITION_Y, 7.0)
        
        hazard = Hazard(
            self.resource_loader,
            self.collision_manager,
            pos,
            hazard_type="acid_drop"
        )
        # Ajustado para usar self.app.render
        hazard.node.reparentTo(self.app.render)
        self.hazards.append(hazard)
    
    def game_loop(self, task):
        return super().game_loop(task)
    

# ====================================
# FASE 8: MERCÚRIO (Velocidade Extrema)
# ====================================

class MercurioLevel(BaseLevel):
    """Fase com velocidade 2x mais rápida"""
    
    def __init__(self, app):
        config = get_level_config("mercurio")
        super().__init__(app, config)
        
        self.corrupted_chance = config.get("corrupted_chance", 0.3)
        
        print("Fase Mercúrio carregada (Velocidade Extrema)")
    
    def create_collectible(self):
        """Fragmentos normais e corrompidos"""
        from entities.game_entities import Collectible
        from core.constants import PLAYER_POSITION_Y
        
        x_pos = random.uniform(-15, 15)
        pos = Vec3(x_pos, PLAYER_POSITION_Y, 5)
        
        is_corrupted = random.random() < self.corrupted_chance
        
        collectible = Collectible(
            self.resource_loader,
            self.collision_manager,
            pos,
            is_corrupted=is_corrupted
        )
        collectible.node.reparentTo(self.app.render)
        self.collectibles.append(collectible)


# ====================================
# FASE 9: SOL (BOSS - Erupções Solares)
# ====================================

class SolLevel(BaseLevel):
    """BOSS FINAL - Erupções solares que varrem a tela"""
    
    def __init__(self, app):
        config = get_level_config("sol")
        super().__init__(app, config)
        
        self.corrupted_chance = config.get("corrupted_chance", 0.3)
        
        # Estado da erupção
        self.eruption_timer = 0.0
        self.eruption_interval = config.get("eruption_interval", 15.0)
        self.eruption_warning_time = config.get("eruption_warning_time", 3.0)
        self.eruption_duration = config.get("eruption_duration", 3.0)
        
        self.in_warning = False
        self.warning_timer = 0.0
        self.in_eruption = False
        self.eruption_elapsed = 0.0
        
        # Beam da erupção
        self.beam_x = -20.0
        self.beam_speed = 0.0
        self.eruption_beam_node = None
        
        # Sombras (zonas seguras)
        self.shadows = []
        self.num_shadows = config.get("num_shadows", 2)
        self.shadow_scale = config.get("shadow_scale", 0.4)
        self.shadow_radius = config.get("shadow_radius", 1.0)
        
        # Textos de aviso
        self.warning_text = None
        self.eruption_flash = None
        
        # Flag de dano
        self.already_damaged_by_eruption = False
        
        print("Fase Sol carregada (BOSS)")
    
    def create_collectible(self):
        """Fragmentos normais e corrompidos"""
        from entities.game_entities import Collectible
        from core.constants import PLAYER_POSITION_Y
        
        x_pos = random.uniform(-15, 15)
        pos = Vec3(x_pos, PLAYER_POSITION_Y, 5)
        
        is_corrupted = random.random() < self.corrupted_chance
        
        collectible = Collectible(
            self.resource_loader,
            self.collision_manager,
            pos,
            is_corrupted=is_corrupted
        )
        collectible.node.reparentTo(self.app.render)
        self.collectibles.append(collectible)
    
    def game_loop(self, task):
        """Override com lógica de erupção"""
        if self.is_paused or self.is_game_over:
            return task.cont
        
        dt = self.clock.getDt()
        
        # === SISTEMA DE ERUPÇÃO ===
        self.eruption_timer += dt
        
        # Inicia aviso
        if not self.in_warning and not self.in_eruption and self.eruption_timer >= self.eruption_interval:
            self.start_eruption_warning()
            self.eruption_timer = 0.0
        
        # Durante aviso
        if self.in_warning:
            self.warning_timer += dt
            
            # Pisca o texto de aviso
            if self.warning_text:
                blink = int(self.warning_timer * 6) % 2
                color = Vec4(1, 1, 0, 1) if blink == 0 else Vec4(1, 0.4, 0, 1)
                self.warning_text.setFg(color)
            
            if self.warning_timer >= self.eruption_warning_time:
                self.begin_eruption()
        
        # Durante erupção
        if self.in_eruption:
            self.eruption_elapsed += dt
            
            # Move o beam
            self.beam_x += self.beam_speed * dt
            if self.eruption_beam_node:
                from core.constants import PLAYER_POSITION_Y
                self.eruption_beam_node.setPos(self.beam_x, PLAYER_POSITION_Y, 0)
            
            # Verifica se jogador foi atingido
            if not self.already_damaged_by_eruption and abs(self.player.get_position().x - self.beam_x) < 1.2:
                if not self.player_in_shadow():
                    # MORTE INSTANTÂNEA
                    self.player.lives = 0
                    self.player.is_alive = False
                    self.trigger_game_over()
                    return task.done
                else:
                    self.already_damaged_by_eruption = True
            
            # Termina erupção
            if self.eruption_elapsed >= self.eruption_duration:
                self.end_eruption()
        
        # Chama game loop base
        return super().game_loop(task)
    
    def start_eruption_warning(self):
        """Inicia aviso de erupção"""
        self.in_warning = True
        self.warning_timer = 0.0
        
        self.warning_text = self.ui_manager.create_text(
            "ERUPÇÃO IMINENTE!",
            (0, 0.85),
            align=2,  # ACenter
            scale=0.06,
            color=Vec4(1, 1, 0, 1)
        )
        
        self.sound_manager.play_warning_sound()
    
    def begin_eruption(self):
        """Começa a erupção"""
        self.in_warning = False
        if self.warning_text:
            self.warning_text.removeNode()
            self.warning_text = None
        
        self.in_eruption = True
        self.eruption_elapsed = 0.0
        self.beam_x = -20.0
        self.beam_speed = 40.0 / self.eruption_duration
        self.already_damaged_by_eruption = False
        
        # Cria sombras (zonas seguras)
        self.clear_shadows()
        for _ in range(self.num_shadows):
            self.create_shadow()
        
        # Cria beam visual
        from core.constants import MODEL_PLANE, PLAYER_POSITION_Y
        beam = self.resource_loader.load_model(MODEL_PLANE)
        if beam:
            beam.reparentTo(self.app.render)
            beam.setScale(0.8, 1.0, 20.0)
            beam.setPos(self.beam_x, PLAYER_POSITION_Y, 0)
            beam.setColor(1.0, 0.6, 0.0, 0.85)
            beam.setTransparency(True)
            self.eruption_beam_node = beam
        
        # Texto de erupção
        self.eruption_flash = self.ui_manager.create_text(
            "ERUPÇÃO!",
            (0, 0.95),
            align=2,
            scale=0.07,
            color=Vec4(1, 0.5, 0, 1)
        )
    
    def end_eruption(self):
        """Termina erupção"""
        self.in_eruption = False
        self.eruption_elapsed = 0.0
        
        if self.eruption_beam_node:
            self.eruption_beam_node.removeNode()
            self.eruption_beam_node = None
        
        if self.eruption_flash:
            self.eruption_flash.removeNode()
            self.eruption_flash = None
        
        self.clear_shadows()
    
    def create_shadow(self):
        """Cria zona de sombra (área segura)"""
        from core.constants import MODEL_PLANE, PLAYER_POSITION_Y
        
        sx = random.uniform(-10, 10)
        sz = random.uniform(-6.0, -3.0)
        
        shadow = self.resource_loader.load_model(MODEL_PLANE)
        if shadow:
            shadow.reparentTo(self.app.render)
            shadow.setScale(self.shadow_scale, self.shadow_scale, self.shadow_scale)
            shadow.setPos(sx, PLAYER_POSITION_Y, sz)
            shadow.setColor(0.03, 0.03, 0.03, 1.0)
            shadow.setTransparency(True)
            
            self.shadows.append({
                'node': shadow,
                'x': sx,
                'z': sz,
                'r': self.shadow_radius
            })
    
    def clear_shadows(self):
        """Remove todas as sombras"""
        for s in self.shadows:
            try:
                s['node'].removeNode()
            except:
                pass
        self.shadows.clear()
    
    def player_in_shadow(self) -> bool:
        """Verifica se jogador está em zona de sombra"""
        px = self.player.get_position().x
        pz = self.player.get_position().z
        
        for s in self.shadows:
            dx = px - s['x']
            dz = pz - s['z']
            if (dx*dx + dz*dz) <= (s['r']*s['r']):
                return True
        
        return False


# ====================================
# EXPORTANDO AS CLASSES PARA O MAIN
# ====================================

# Dicionário exposto na raiz do arquivo para o main.py encontrar
level_classes = {
    "netuno": NetunoLevel,
    "urano": UranoLevel,
    "saturno": SaturnoLevel,
    "jupiter": JupiterLevel,
    "marte": MarteLevel,
    "terra": TerraLevel,
    "venus": VenusLevel,
    "mercurio": MercurioLevel,
    "sol": SolLevel
}

# (Opcional) A função antiga mantida só por segurança
def create_level(app, level_name: str) -> BaseLevel:
    if level_name in level_classes:
        return level_classes[level_name](app)
    else:
        print(f"⚠️ Fase desconhecida: {level_name}, usando Netuno")
        return NetunoLevel(app)

print("Todas as 9 fases definidas com sucesso!")