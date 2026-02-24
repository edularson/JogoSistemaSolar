"""
JORNADA SOLAR - PLAYER
Entidade do jogador reutilizável em todas as fases
Gerencia movimento, colisão, power-ups e estado
"""

from panda3d.core import Vec3, Vec4
from typing import Optional


class Player:
    """
    Classe do jogador.
    Controla movimento, estado e interações.
    """
    
    def __init__(self, resource_loader, collision_manager, position: Vec3):
        """
        Inicializa o jogador
        
        Args:
            resource_loader: ResourceLoader para carregar modelo
            collision_manager: CollisionManager para criar collider
            position: Posição inicial
        """
        from core.constants import (
            MODEL_PLAYER, TEXTURE_PLAYER, PLAYER_SCALE,
            PLAYER_COLLISION_RADIUS, PLAYER_HORIZONTAL_SPEED,
            PLAYER_MIN_X, PLAYER_MAX_X, PLAYER_MIN_Z, PLAYER_MAX_Z
        )
        
        self.resource_loader = resource_loader
        self.collision_manager = collision_manager
        
        # Carrega modelo
        self.node = resource_loader.load_model(MODEL_PLAYER)
        if self.node is None:
            raise Exception("Falha ao carregar modelo do jogador!")
        
        self.node.setScale(PLAYER_SCALE)
        self.node.setPos(position)
        
        # Aplica textura
        resource_loader.apply_texture_to_model(self.node, TEXTURE_PLAYER)
        
        # Cria collider
        self.collider = collision_manager.create_player_collider(
            self.node, 
            radius=PLAYER_COLLISION_RADIUS
        )
        
        # Configurações de movimento
        self.speed = PLAYER_HORIZONTAL_SPEED
        self.min_x = PLAYER_MIN_X
        self.max_x = PLAYER_MAX_X
        self.min_z = PLAYER_MIN_Z
        self.max_z = PLAYER_MAX_Z
        
        # Direção de movimento
        self.move_direction_x = 0  # -1 = esquerda, 1 = direita
        self.move_direction_z = 0  # -1 = baixo, 1 = cima
        
        # Estado
        self.lives = 3
        self.is_alive = True
        
        # Power-ups ativos
        self.shield_charges = 0
        self.magnet_active = False
        self.magnet_timer = 0.0
        self.slowmotion_active = False
        self.slowmotion_timer = 0.0
        
        # Debuffs
        self.is_slowed = False
        self.slow_timer = 0.0
        
        # Efeitos visuais dos power-ups
        self.shield_aura = None
        self.magnet_effect = None
        
        print(f"Jogador criado em {position}")
    
    # ====================================
    # MOVIMENTO
    # ====================================
    
    def set_move_direction_x(self, direction: int):
        """
        Define direção horizontal (-1, 0, 1)
        
        Args:
            direction: -1 = esquerda, 0 = parado, 1 = direita
        """
        self.move_direction_x = direction
    
    def set_move_direction_z(self, direction: int):
        """
        Define direção vertical (-1, 0, 1)
        
        Args:
            direction: -1 = baixo, 0 = parado, 1 = cima
        """
        self.move_direction_z = direction
    
    def update_movement(self, dt: float, speed_multiplier: float = 1.0):
        """
        Atualiza posição do jogador baseado em direções
        
        Args:
            dt: Delta time
            speed_multiplier: Multiplicador de velocidade (para slow-motion, debuffs)
        """
        from core.constants import DEBUFF_SLOW_MULTIPLIER
        
        # Aplica debuff de lentidão se ativo
        if self.is_slowed:
            speed_multiplier *= DEBUFF_SLOW_MULTIPLIER
        
        # Calcula velocidade final
        final_speed = self.speed * speed_multiplier
        
        # Movimento horizontal (X)
        new_x = self.node.getX() + self.move_direction_x * final_speed
        new_x = max(min(new_x, self.max_x), self.min_x)
        self.node.setX(new_x)
        
        # Movimento vertical (Z)
        new_z = self.node.getZ() + self.move_direction_z * final_speed
        new_z = max(min(new_z, self.max_z), self.min_z)
        self.node.setZ(new_z)
    
    def apply_external_force(self, force_x: float, force_z: float = 0):
        """
        Aplica força externa (vento, knockback, etc)
        
        Args:
            force_x: Força no eixo X
            force_z: Força no eixo Z
        """
        new_x = self.node.getX() + force_x
        new_x = max(min(new_x, self.max_x), self.min_x)
        self.node.setX(new_x)
        
        if force_z != 0:
            new_z = self.node.getZ() + force_z
            new_z = max(min(new_z, self.max_z), self.min_z)
            self.node.setZ(new_z)
    
    # ====================================
    # VIDA E DANO
    # ====================================
    
    def take_damage(self, amount: int = 1) -> bool:
        """
        Jogador toma dano
        
        Args:
            amount: Quantidade de dano
            
        Returns:
            True se ainda está vivo
        """
        # Se tem escudo, consome uma carga
        if self.shield_charges > 0:
            self.shield_charges -= 1
            print(f"Escudo absorveu dano! Cargas restantes: {self.shield_charges}")
            
            # Remove aura se acabou o escudo
            if self.shield_charges <= 0:
                self.deactivate_shield()
            
            return True
        
        # Sem escudo, perde vida
        self.lives -= amount
        print(f"Jogador tomou {amount} de dano! Vidas: {self.lives}")
        
        if self.lives <= 0:
            self.lives = 0
            self.is_alive = False
            print("Jogador morreu!")
            return False
        
        return True
    
    def heal(self, amount: int = 1):
        """
        Cura o jogador
        
        Args:
            amount: Quantidade de cura
        """
        max_lives = 5  # Limite máximo
        self.lives = min(self.lives + amount, max_lives)
        print(f"Jogador curado! Vidas: {self.lives}")
    
    def reset_health(self, max_lives: int = 3):
        """
        Reseta vida para o máximo
        
        Args:
            max_lives: Vida máxima a definir
        """
        self.lives = max_lives
        self.is_alive = True
    
    # ====================================
    # POWER-UPS
    # ====================================
    
    def activate_shield(self, charges: int = 1):
        """
        Ativa escudo
        
        Args:
            charges: Número de cargas
        """
        from core.constants import POWERUP_DURATION_SHIELD
        
        self.shield_charges = charges
        print(f"Escudo ativado! Cargas: {charges}")
    
    def deactivate_shield(self):
        """Desativa escudo"""
        self.shield_charges = 0
        print("Escudo desativado")
    
    def activate_magnet(self):
        """Ativa imã de fragmentos"""
        from core.constants import POWERUP_DURATION_MAGNET
        
        self.magnet_active = True
        self.magnet_timer = 0.0
        print(f"Imã ativado! Duração: {POWERUP_DURATION_MAGNET}s")
    
    def deactivate_magnet(self):
        """Desativa imã"""
        self.magnet_active = False
        self.magnet_timer = 0.0
        print("Imã desativado")
    
    def activate_slowmotion(self):
        """Ativa slow-motion"""
        from core.constants import POWERUP_DURATION_SLOWMOTION
        
        self.slowmotion_active = True
        self.slowmotion_timer = 0.0
        print(f"Slow-Motion ativado! Duração: {POWERUP_DURATION_SLOWMOTION}s")
    
    def deactivate_slowmotion(self):
        """Desativa slow-motion"""
        self.slowmotion_active = False
        self.slowmotion_timer = 0.0
        print("Slow-Motion desativado")
    
    def activate_powerup(self, powerup_type: str):
        """
        Ativa power-up baseado no tipo
        
        Args:
            powerup_type: Tipo (shield, magnet, slow)
        """
        if powerup_type == "shield":
            self.activate_shield()
        elif powerup_type == "magnet":
            self.activate_magnet()
        elif powerup_type == "slow":
            self.activate_slowmotion()
        else:
            print(f"⚠️ Power-up desconhecido: {powerup_type}")
    
    def update_powerup_timers(self, dt: float):
        """
        Atualiza timers dos power-ups
        
        Args:
            dt: Delta time
        """
        from core.constants import POWERUP_DURATION_MAGNET, POWERUP_DURATION_SLOWMOTION
        
        # Timer do imã
        if self.magnet_active:
            self.magnet_timer += dt
            if self.magnet_timer >= POWERUP_DURATION_MAGNET:
                self.deactivate_magnet()
        
        # Timer do slow-motion
        if self.slowmotion_active:
            self.slowmotion_timer += dt
            if self.slowmotion_timer >= POWERUP_DURATION_SLOWMOTION:
                self.deactivate_slowmotion()
    
    # ====================================
    # DEBUFFS
    # ====================================
    
    def apply_slow_debuff(self):
        """Aplica debuff de lentidão"""
        from core.constants import DEBUFF_SLOW_DURATION
        
        self.is_slowed = True
        self.slow_timer = 0.0
        print(f"Jogador está lento! Duração: {DEBUFF_SLOW_DURATION}s")
    
    def update_debuff_timers(self, dt: float):
        """
        Atualiza timers de debuffs
        
        Args:
            dt: Delta time
        """
        from core.constants import DEBUFF_SLOW_DURATION
        
        if self.is_slowed:
            self.slow_timer += dt
            if self.slow_timer >= DEBUFF_SLOW_DURATION:
                self.is_slowed = False
                self.slow_timer = 0.0
                print("Jogador não está mais lento")
    
    # ====================================
    # UPDATE GERAL
    # ====================================
    
    def update(self, dt: float, speed_multiplier: float = 1.0):
        """
        Update completo do jogador
        
        Args:
            dt: Delta time
            speed_multiplier: Multiplicador global de velocidade
        """
        # Atualiza timers
        self.update_powerup_timers(dt)
        self.update_debuff_timers(dt)
        
        # Atualiza movimento
        self.update_movement(dt, speed_multiplier)
    
    # ====================================
    # UTILIDADES
    # ====================================
    
    def get_position(self) -> Vec3:
        """Retorna posição atual"""
        pos = self.node.getPos()
        return Vec3(pos.x, pos.y, pos.z)
    
    def set_position(self, position: Vec3):
        """
        Define nova posição
        
        Args:
            position: Nova posição
        """
        self.node.setPos(position)
    
    def reset_position(self):
        """Reseta para posição inicial"""
        from core.constants import PLAYER_POSITION_Y, PLAYER_POSITION_Z_START
        
        self.node.setPos(0, PLAYER_POSITION_Y, PLAYER_POSITION_Z_START)
        print("Jogador resetado para posição inicial")
    
    def get_state(self) -> dict:
        """
        Retorna estado completo do jogador
        
        Returns:
            Dicionário com todo o estado
        """
        return {
            "position": self.get_position(),
            "lives": self.lives,
            "is_alive": self.is_alive,
            "shield_charges": self.shield_charges,
            "magnet_active": self.magnet_active,
            "slowmotion_active": self.slowmotion_active,
            "is_slowed": self.is_slowed
        }
    
    def reset(self, max_lives: int = 3):
        """
        Reseta jogador completamente
        
        Args:
            max_lives: Vidas iniciais
        """
        self.reset_position()
        self.reset_health(max_lives)
        
        # Limpa power-ups
        self.deactivate_shield()
        self.deactivate_magnet()
        self.deactivate_slowmotion()
        
        # Limpa debuffs
        self.is_slowed = False
        self.slow_timer = 0.0
        
        # Para movimento
        self.move_direction_x = 0
        self.move_direction_z = 0
        
        print("Jogador completamente resetado")
    
    def cleanup(self):
        """Limpa recursos do jogador"""
        if self.node:
            self.node.removeNode()
        
        print("Jogador limpo")


print("Player class definida com sucesso!")