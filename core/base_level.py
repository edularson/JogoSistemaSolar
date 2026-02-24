"""
JORNADA SOLAR - BASE LEVEL
Classe base reutilizável para TODAS as fases
Implementa toda lógica comum e permite override de mecânicas específicas
"""

from panda3d.core import Vec3, Vec4, WindowProperties, AmbientLight, DirectionalLight
from typing import Optional, Dict, List
import time


class BaseLevel:
    """
    Classe base para todas as fases do jogo (Estado).
    Fases específicas herdam desta classe.
    """
    
    def __init__(self, app, level_config: Dict):
        """
        Inicializa a fase base
        
        Args:
            level_config: Dicionário com configurações da fase
        """
        self.app = app
        
        # Importa managers
        from core.resource_loader import ResourceLoader
        from core.save_manager import SaveManager
        from core.sound_manager import SoundManager
        from core.ui_manager import UIManager
        from core.collision_manager import CollisionManager
        from core.particle_manager import ParticleManager
        from entities.player import Player
        from entities.game_entities import Collectible, Hazard, Powerup
        
        # Configuração da fase
        self.level_data = level_config
        self.level_name = level_config.get("name", "unnamed")
        
        # Setup janela
        self.setup_window()
        
        # Inicializa managers
        self.save_manager = self.app.save_manager
        self.resource_loader = self.app.resource_loader
        self.sound_manager = self.app.sound_manager
        self.ui_manager = UIManager(self, self.app.aspect2d, self.app.render2d)
        self.collision_manager = CollisionManager()
        self.particle_manager = ParticleManager(self.app.render, self.app.loader)
        
        # Setup básico de cena
        self.app.disableMouse()
        self.app.render.setShaderAuto()
        self.app.render.setAntialias(1)
        self.app.camera.setPos(0, -30, 5)
        self.app.camera.lookAt(0, 0, 0)
        
        # Setup iluminação e cenário
        self.setup_lighting()
        self.setup_background()
        self.setup_ground()
        
        # Cria jogador
        from core.constants import PLAYER_POSITION_Y, PLAYER_POSITION_Z_START
        initial_pos = Vec3(0, PLAYER_POSITION_Y, PLAYER_POSITION_Z_START)
        self.player = Player(self.resource_loader, self.collision_manager, initial_pos)
        self.player.node.reparentTo(self.app.render)
        
        # Estado do jogo
        self.score = 0
        self.objective = level_config.get("objective_count", 20)
        self.is_paused = False
        self.is_game_over = False
        self.is_victory = False
        
        # Listas de entidades
        self.collectibles: List[Collectible] = []
        self.hazards: List[Hazard] = []
        self.powerups: List[Powerup] = []
        
        # Timers de spawn
        self.spawn_timer_collectible = 0
        self.spawn_interval_collectible = level_config.get("spawn_interval_collectible", 1.0)
        self.spawn_timer_hazard = 0
        self.spawn_interval_hazard = level_config.get("spawn_interval_hazard", 1.5)
        self.spawn_timer_powerup = 0
        self.spawn_interval_powerup = level_config.get("spawn_interval_powerup", 6.0)
        
        # Velocidades
        from core.constants import SPEED_MULTIPLIER_BY_LEVEL
        self.collectible_speed = level_config.get("collectible_speed", 0.05)
        self.hazard_speed = level_config.get("hazard_speed", 0.06)
        self.level_speed_mult = SPEED_MULTIPLIER_BY_LEVEL.get(self.level_name, 1.0)
        
        # Sistema de pontuação e combo
        self.combo_count = 0
        self.combo_timer = 0.0
        from core.constants import COMBO_TIME_WINDOW
        self.combo_window = COMBO_TIME_WINDOW
        
        # Tracking de estatísticas
        self.start_time = time.time()
        self.damage_taken = 0
        self.powerups_collected = 0
        
        # UI
        self.hud = self.ui_manager.create_hud()
        self.pause_overlay = None
        
        # Relógio
        self.clock = self.app.taskMgr.globalClock
        
        # Controles
        self.setup_controls()
        
        print(f"Fase '{self.level_name}' inicializada!")

    def start_level(self):
        """Chamado pelo main.py para iniciar os loops após instanciar a classe"""
        # Tasks
        self.app.taskMgr.add(self.game_loop, "GameLoop")
        self.app.taskMgr.add(self.spawn_collectible_task, "SpawnCollectibleTask")
        self.app.taskMgr.add(self.spawn_hazard_task, "SpawnHazardTask")
        self.app.taskMgr.add(self.spawn_powerup_task, "SpawnPowerupTask")
        
        # Música
        self.sound_manager.play_level_music(self.level_name)
    
    # ====================================
    # SETUP
    # ====================================
    
    def setup_window(self):
        """Configura janela"""
        props = WindowProperties()
        props.setFullscreen(True)
        props.setSize(self.app.pipe.getDisplayWidth(), self.app.pipe.getDisplayHeight())
        self.app.win.requestProperties(props)
    
    def setup_lighting(self):
        """Configura iluminação (pode ser overridden)"""
        # Luz ambiente padrão
        ambient = AmbientLight("ambient")
        ambient.setColor(Vec4(0.6, 0.6, 0.6, 1))
        self.ambient_np = self.app.render.attachNewNode(ambient)
        self.app.render.setLight(self.ambient_np)
        
        # Luz direcional
        directional = DirectionalLight("directional")
        directional.setColor(Vec4(0.8, 0.8, 0.7, 1))
        self.directional_np = self.app.render.attachNewNode(directional)
        self.directional_np.setHpr(30, -60, 0)
        self.app.render.setLight(self.directional_np)
    
    def setup_background(self):
        """Configura background"""
        bg_path = f"imgs/{self.level_name}/{self.level_name}_fundo.png"
        aspect = self.app.getAspectRatio()
        
        self.bg = self.resource_loader.load_background(bg_path, aspect)
        if self.bg:
            self.bg.reparentTo(self.app.render2d)
            self.app.camNode.getDisplayRegion(0).setSort(20)
            self.app.setBackgroundColor(0, 0, 0, 0)
        else:
            self.app.setBackgroundColor(0, 0, 0.1, 1)
    
    def setup_ground(self):
        """Configura chão"""
        from core.constants import MODEL_PLANE, PLAYER_POSITION_Y
        
        self.ground = self.resource_loader.load_model(MODEL_PLANE)
        if self.ground:
            self.ground.reparentTo(self.app.render)
            self.ground.setScale(12, 10, 1)
            self.ground.setPos(0, PLAYER_POSITION_Y, -8.0)
            self.ground.setP(-90)
            
            ground_texture = f"imgs/{self.level_name}/chao_{self.level_name}.png"
            self.resource_loader.apply_texture_to_model(self.ground, ground_texture)
    
    def setup_controls(self):
        """Configura controles"""
        # Movimento
        self.app.accept('a', self.player.set_move_direction_x, [-1])
        self.app.accept('d', self.player.set_move_direction_x, [1])
        self.app.accept('a-up', self.player.set_move_direction_x, [0])
        self.app.accept('d-up', self.player.set_move_direction_x, [0])
        
        self.app.accept('w', self.player.set_move_direction_z, [1])
        self.app.accept('s', self.player.set_move_direction_z, [-1])
        self.app.accept('w-up', self.player.set_move_direction_z, [0])
        self.app.accept('s-up', self.player.set_move_direction_z, [0])
        
        # Pausa
        self.app.accept('p', self.toggle_pause)
        
        # Sair
        self.app.accept('escape', self.exit_to_lobby)
    
    # ====================================
    # SPAWN DE ENTIDADES
    # ====================================
    
    def spawn_collectible_task(self, task):
        """Task de spawn de coletáveis"""
        if self.is_paused or self.is_game_over:
            return task.cont
        
        if self.score < self.objective:
            dt = self.clock.getDt()
            if self.player.slowmotion_active:
                from core.constants import POWERUP_SLOWMOTION_MULTIPLIER
                dt *= POWERUP_SLOWMOTION_MULTIPLIER
            
            self.spawn_timer_collectible += dt
            
            if self.spawn_timer_collectible >= self.spawn_interval_collectible:
                self.create_collectible()
                self.spawn_timer_collectible = 0
        
        return task.cont
    
    def spawn_hazard_task(self, task):
        """Task de spawn de perigos"""
        if self.is_paused or self.is_game_over:
            return task.cont
        
        if self.player.is_alive and self.score < self.objective:
            dt = self.clock.getDt()
            if self.player.slowmotion_active:
                from core.constants import POWERUP_SLOWMOTION_MULTIPLIER
                dt *= POWERUP_SLOWMOTION_MULTIPLIER
            
            self.spawn_timer_hazard += dt
            
            if self.spawn_timer_hazard >= self.spawn_interval_hazard:
                self.create_hazard()
                self.spawn_timer_hazard = 0
        
        return task.cont
    
    def spawn_powerup_task(self, task):
        """Task de spawn de power-ups"""
        if self.is_paused or self.is_game_over:
            return task.cont
        
        if self.player.is_alive and self.score < self.objective:
            dt = self.clock.getDt()
            if self.player.slowmotion_active:
                from core.constants import POWERUP_SLOWMOTION_MULTIPLIER
                dt *= POWERUP_SLOWMOTION_MULTIPLIER
            
            self.spawn_timer_powerup += dt
            
            if self.spawn_timer_powerup >= self.spawn_interval_powerup:
                self.create_powerup()
                self.spawn_timer_powerup = 0
        
        return task.cont
    
    
    def create_collectible(self):
        """Cria coletável (override para fragmentos corrompidos)"""
        import random
        from entities.game_entities import Collectible
        from core.constants import PLAYER_POSITION_Y
        
        x_pos = random.uniform(-15, 15)
        pos = Vec3(x_pos, PLAYER_POSITION_Y, 5)
        
        collectible = Collectible(
            self.resource_loader,
            self.collision_manager,
            pos,
            is_corrupted=False
        )
        collectible.node.reparentTo(self.app.render)
        self.collectibles.append(collectible)
    
    def create_hazard(self):
        """Cria perigo"""
        import random
        from entities.game_entities import Hazard
        from core.constants import PLAYER_POSITION_Y
        
        x_pos = random.uniform(-15, 15)
        pos = Vec3(x_pos, PLAYER_POSITION_Y, 5.5)
        
        hazard = Hazard(
            self.resource_loader,
            self.collision_manager,
            pos,
            hazard_type="meteor"
        )
        hazard.node.reparentTo(self.app.render)
        self.hazards.append(hazard)
    
    def create_powerup(self):
        """Cria power-up"""
        import random
        from entities.game_entities import Powerup
        from core.constants import PLAYER_POSITION_Y
        
        x_pos = random.uniform(-15, 15)
        pos = Vec3(x_pos, PLAYER_POSITION_Y, 5.2)
        
        powerup_type = random.choice(["shield", "magnet", "slow"])
        
        powerup = Powerup(
            self.resource_loader,
            self.collision_manager,
            pos,
            powerup_type=powerup_type
        )
        powerup.node.reparentTo(self.app.render)
        self.powerups.append(powerup)
    
    # ====================================
    # GAME LOOP
    # ====================================
    
    def game_loop(self, task):
        """Loop principal do jogo"""
        if self.is_paused or self.is_game_over:
            return task.cont
        
        dt = self.clock.getDt()
        
        # Multiplicador de velocidade global
        speed_mult = 1.0
        if self.player.slowmotion_active:
            from core.constants import POWERUP_SLOWMOTION_MULTIPLIER
            speed_mult = POWERUP_SLOWMOTION_MULTIPLIER
        
        # Atualiza jogador
        self.player.update(dt, speed_mult)
        
        # Atualiza entidades
        self.update_collectibles(dt, speed_mult)
        self.update_hazards(dt, speed_mult)
        self.update_powerups(dt, speed_mult)
        
        # Verifica colisões
        self.check_collisions()
        
        # Atualiza partículas
        self.particle_manager.update_particles(dt)
        
        # Atualiza combo
        self.update_combo(dt)
        
        # Atualiza HUD
        self.update_hud()
        
        # Verifica condições de vitória/derrota
        self.check_win_lose_conditions()
        
        return task.cont
    
    def update_collectibles(self, dt: float, speed_mult: float):
        """Atualiza coletáveis"""
        to_remove = []
        
        for col in self.collectibles:
            # Aplica imã se ativo
            if self.player.magnet_active:
                from core.constants import POWERUP_MAGNET_RADIUS, POWERUP_MAGNET_FORCE
                col.apply_magnet_force(
                    self.player.get_position(),
                    POWERUP_MAGNET_FORCE,
                    POWERUP_MAGNET_RADIUS,
                    dt
                )
            
            # Atualiza movimento
            col.update(dt, self.collectible_speed * self.level_speed_mult, speed_mult)
            
            if not col.is_alive:
                to_remove.append(col)
        
        # Remove mortos
        for col in to_remove:
            if col in self.collectibles:
                self.collectibles.remove(col)
            col.destroy()
    
    def update_hazards(self, dt: float, speed_mult: float):
        """Atualiza perigos"""
        to_remove = []
        
        for haz in self.hazards:
            haz.update(dt, self.hazard_speed * self.level_speed_mult, speed_mult)
            
            if not haz.is_alive:
                to_remove.append(haz)
        
        for haz in to_remove:
            if haz in self.hazards:
                self.hazards.remove(haz)
            haz.destroy()
    
    def update_powerups(self, dt: float, speed_mult: float):
        """Atualiza power-ups"""
        to_remove = []
        
        for pu in self.powerups:
            pu.update(dt, self.collectible_speed * self.level_speed_mult, speed_mult)
            
            if not pu.is_alive:
                to_remove.append(pu)
        
        for pu in to_remove:
            if pu in self.powerups:
                self.powerups.remove(pu)
            pu.destroy()
    
    def check_collisions(self):
        """Verifica todas as colisões"""
        collisions = self.collision_manager.check_collisions(self.app.render)
        
        for collision in collisions:
            col_type = collision['type']
            col_node = collision['node']
            
            # Fragmento coletado
            if col_type == 'fragment':
                self.on_collect_fragment(col_node)
            
            # Fragmento corrompido
            elif col_type == 'corrupted':
                self.on_collect_corrupted(col_node)
            
            # Perigo (meteoro/lixo/raio)
            elif col_type in ['meteor', 'trash', 'lightning', 'acid_drop']:
                self.on_hit_hazard(col_node, col_type)
            
            # Power-up
            elif col_type in ['shield', 'magnet', 'slow']:
                self.on_collect_powerup(col_node, col_type)
    
    # ====================================
    # EVENTOS DE COLISÃO
    # ====================================
    
    def on_collect_fragment(self, fragment_node):
        """Evento: fragmento coletado"""
        for col in self.collectibles:
            if col.node == fragment_node:
                from core.constants import SCORE_FRAGMENT
                self.score += 1
                
                self.combo_count += 1
                self.combo_timer = 0.0
                
                if self.combo_count >= 3:
                    self.ui_manager.show_combo_text(self.combo_count)
                
                self.particle_manager.create_collect_effect(col.node.getPos())
                self.sound_manager.play_collect_sound()
                
                self.collectibles.remove(col)
                col.destroy()
                break
    
    def on_collect_corrupted(self, corrupted_node):
        """Evento: fragmento corrompido coletado"""
        for col in self.collectibles:
            if col.node == corrupted_node:
                self.player.apply_slow_debuff()
                self.collectibles.remove(col)
                col.destroy()
                break
    
    def on_hit_hazard(self, hazard_node, hazard_type):
        """Evento: atingido por perigo"""
        for haz in self.hazards:
            if haz.node == hazard_node:
                still_alive = self.player.take_damage(1)
                self.damage_taken += 1
                
                self.particle_manager.create_damage_effect(self.player.get_position())
                self.sound_manager.play_damage_sound()
                
                self.hazards.remove(haz)
                haz.destroy()
                
                if not still_alive:
                    self.trigger_game_over()
                break
    
    def on_collect_powerup(self, powerup_node, powerup_type):
        """Evento: power-up coletado"""
        for pu in self.powerups:
            if pu.node == powerup_node:
                self.player.activate_powerup(powerup_type)
                self.powerups_collected += 1
                
                self.particle_manager.create_powerup_effect(pu.node.getPos(), powerup_type)
                self.sound_manager.play_powerup_sound()
                
                self.powerups.remove(pu)
                pu.destroy()
                break
    
    # ====================================
    # UI E HUD
    # ====================================
    
    def update_hud(self):
        """Atualiza HUD"""
        self.ui_manager.update_hud_text(
            self.hud["score"],
            f"Fragmentos: {self.score}/{self.objective}"
        )
        
        self.ui_manager.update_hud_text(
            self.hud["lives"],
            f"Vidas: {self.player.lives}"
        )
        
        # Power-ups ativos
        states = []
        if self.player.shield_charges > 0:
            states.append("Escudo")
        if self.player.magnet_active:
            states.append("Imã")
        if self.player.slowmotion_active:
            states.append("Slow-Motion")
        
        powerup_text = "Power-ups: " + (", ".join(states) if states else "nenhum")
        self.ui_manager.update_hud_text(self.hud["powerups"], powerup_text)
        
        # Timer
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        self.ui_manager.update_hud_text(self.hud["timer"], f"Tempo: {minutes:02d}:{seconds:02d}")
    
    def update_combo(self, dt: float):
        """Atualiza sistema de combo"""
        if self.combo_count > 0:
            self.combo_timer += dt
            if self.combo_timer >= self.combo_window:
                self.combo_count = 0
                self.combo_timer = 0.0
    
    # ====================================
    # PAUSA E CONTROLE DE FLUXO
    # ====================================
    
    def toggle_pause(self):
        """Alterna o estado de pausa e a visibilidade do menu"""
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.show_pause_menu()
            self.sound_manager.pause_music()
        else:
            if hasattr(self, 'pause_frame'):
                self.pause_frame.destroy()
            
            props = WindowProperties()
            props.setCursorHidden(True)
            self.app.win.requestProperties(props)
            
            self.sound_manager.resume_music()
    
    def show_pause_menu(self):
        """Cria a interface visual do menu de pausa"""
        from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel
        from panda3d.core import Vec4, WindowProperties

        # 1. Mostra o mouse para poder clicar nos botões
        props = WindowProperties()
        props.setCursorHidden(False)
        self.app.win.requestProperties(props)

        # 2. Frame Central
        self.pause_frame = DirectFrame(
            frameSize=(-0.6, 0.6, -0.5, 0.5),
            frameColor=(0.05, 0.05, 0.1, 0.9),
            pos=(0, 0, 0),
            parent=self.app.aspect2d
        )

        # 3. Título
        DirectLabel(
            text="JOGO PAUSADO",
            text_scale=0.08,
            pos=(0, 0, 0.3),
            frameColor=(0, 0, 0, 0),
            text_fg=(1, 1, 0, 1),
            parent=self.pause_frame
        )

        # 4. Botões (Usando a mesma lógica de escala que funcionou na Settings)
        DirectButton(
            text="CONTINUAR",
            text_scale=0.2,
            scale=(0.8, 1, 0.12),
            pos=(0, 0, 0.05),
            command=self.toggle_pause, # Chama a mesma função que despausa
            frameColor=(0.2, 0.5, 0.2, 1),
            parent=self.pause_frame
        )

        DirectButton(
            text="SAIR PARA LOBBY",
            text_scale=0.2,
            scale=(0.8, 1, 0.12),
            pos=(0, 0, -0.2),
            command=self.exit_to_lobby,
            frameColor=(0.5, 0.2, 0.2, 1),
            parent=self.pause_frame
        )
    
    def check_win_lose_conditions(self):
        """Verifica condições de vitória/derrota"""
        if self.score >= self.objective and self.player.is_alive and not self.is_victory:
            self.trigger_victory()
        elif not self.player.is_alive and not self.is_game_over:
            self.trigger_game_over()
    
    def trigger_victory(self):
        """Aciona vitória"""
        self.is_victory = True
        self.is_game_over = True
        
        self.app.taskMgr.remove("GameLoop")
        self.app.taskMgr.remove("SpawnCollectibleTask")
        self.app.taskMgr.remove("SpawnHazardTask")
        self.app.taskMgr.remove("SpawnPowerupTask")
        
        elapsed = time.time() - self.start_time
        stats = self.calculate_stats(elapsed)
        self.save_progress(stats)
        
        self.ui_manager.show_game_over_screen(
            victory=True,
            stats=stats,
            restart_callback=self.restart_level,
            menu_callback=self.exit_to_lobby
        )
        self.sound_manager.play_victory_sound()
    
    def trigger_game_over(self):
        """Aciona game over"""
        self.is_game_over = True
        
        self.app.taskMgr.remove("GameLoop")
        self.app.taskMgr.remove("SpawnCollectibleTask")
        self.app.taskMgr.remove("SpawnHazardTask")
        self.app.taskMgr.remove("SpawnPowerupTask")
        
        elapsed = time.time() - self.start_time
        stats = self.calculate_stats(elapsed)
        
        self.ui_manager.show_game_over_screen(
            victory=False,
            stats=stats,
            restart_callback=self.restart_level,
            menu_callback=self.exit_to_lobby
        )
        self.sound_manager.play_defeat_sound()
    
    # ====================================
    # ESTATÍSTICAS E SAVE
    # ====================================
    
    def calculate_stats(self, elapsed_time: float) -> Dict:
        """Calcula estatísticas da partida"""
        from core.constants import SCORE_FRAGMENT, SCORE_NO_DAMAGE_BONUS, SCORE_TIME_BONUS
        
        points = self.score * SCORE_FRAGMENT
        
        no_damage = self.damage_taken == 0
        if no_damage:
            points += SCORE_NO_DAMAGE_BONUS
        
        time_bonus = max(0, int((300 - elapsed_time) * SCORE_TIME_BONUS))
        points += time_bonus
        
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        return {
            'collected': self.score,
            'total': self.objective,
            'time': time_str,
            'time_seconds': elapsed_time,
            'score': points,
            'damage_taken': self.damage_taken,
            'new_highscore': False 
        }
    
    def save_progress(self, stats: Dict):
        """Salva progresso da fase"""
        is_new_highscore = self.save_manager.update_highscore(
            level_name=self.level_name,
            score=stats['score'],
            time=stats['time_seconds'],
            no_damage=(stats['damage_taken'] == 0),
            challenge_completed=False 
        )
        stats['new_highscore'] = is_new_highscore
        
        level_index = self.level_data.get("index", 0)
        self.save_manager.complete_level(level_index)
    
    # ====================================
    # TRANSIÇÕES
    # ====================================
    
    def restart_level(self):
        """Reinicia a fase"""
        self.app.change_state(f"fase_{self.level_name}")
    
    def exit_to_lobby(self):
        """Sai para o lobby limpando o menu de pausa"""
        self.app.change_state("lobby")
    
    # ====================================
    # LIMPEZA
    # ====================================
    
    def cleanup(self):
        """Limpa recursos da fase de forma segura"""
        print(f"Limpando Fase {self.level_name}...")
        
        # 1. Desliga o teclado e para as Tasks imediatamente
        self.app.ignoreAll()
        self.app.taskMgr.remove("GameLoop")
        self.app.taskMgr.remove("SpawnCollectibleTask")
        self.app.taskMgr.remove("SpawnHazardTask")
        self.app.taskMgr.remove("SpawnPowerupTask")
        
        # 2. Limpa o Menu de Pausa se ele estiver aberto
        if hasattr(self, 'pause_frame') and self.pause_frame:
            self.pause_frame.destroy()
            self.pause_frame = None
        
        # 3. Limpa Entidades
        for entities in [self.collectibles, self.hazards, self.powerups]:
            for item in entities:
                item.destroy()
            entities.clear()
        
        # 4. Limpa Jogador
        if hasattr(self, 'player') and self.player:
            self.player.cleanup()
            self.player = None
        
        # 5. Limpa Cenário
        if hasattr(self, 'ground') and self.ground:
            self.ground.removeNode()
            self.ground = None
        if hasattr(self, 'bg') and self.bg:
            self.bg.removeNode()
            self.bg = None
            
        # 6. LIMPEZA DE LUZES (Onde estava o erro)
        # Usamos .node() para passar a Luz em vez do NodePath
        if hasattr(self, 'ambient_np') and self.ambient_np:
            self.app.render.clearLight(self.ambient_np) # Tenta remover o NP
            self.ambient_np.removeNode()
            self.ambient_np = None
            
        if hasattr(self, 'directional_np') and self.directional_np:
            self.app.render.clearLight(self.directional_np)
            self.directional_np.removeNode()
            self.directional_np = None
        
        # 7. Limpa Managers
        if hasattr(self, 'ui_manager'): 
            self.ui_manager.clear_all()
        if hasattr(self, 'particle_manager'): 
            self.particle_manager.clear_all_effects()
        
        if hasattr(self, 'sound_manager'): 
            self.sound_manager.stop_music()