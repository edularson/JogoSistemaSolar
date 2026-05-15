"""
JORNADA SOLAR - GAME ENTITIES
Classes para todas as entidades do jogo:
- Collectible (fragmentos/cristais)
- Hazard (meteoros/lixo/raios)
- Powerup (escudo/imã/slow)
"""

from panda3d.core import Vec3, Vec4
from typing import Optional
import random


# ====================================
# COLLECTIBLE (Fragmentos/Cristais)
# ====================================

class Collectible:
    """Entidade coletável (fragmento/cristal)"""
    
    def __init__(self, resource_loader, collision_manager, position: Vec3,
                 is_corrupted: bool = False):
        """
        Inicializa coletável
        
        Args:
            resource_loader: ResourceLoader
            collision_manager: CollisionManager
            position: Posição inicial
            is_corrupted: Se é fragmento corrompido
        """
        from core.constants import (
            MODEL_COLLECTIBLE, MODEL_COLLECTIBLE_CORRUPTED,
            TEXTURE_COLLECTIBLE, TEXTURE_COLLECTIBLE_CORRUPTED
        )
        
        self.is_corrupted = is_corrupted
        self.rotation_speed = random.uniform(4, 6)
        
        # Carrega modelo apropriado
        model_path = MODEL_COLLECTIBLE_CORRUPTED if is_corrupted else MODEL_COLLECTIBLE
        self.node = resource_loader.load_model(model_path)
        if self.node is None:
            print(f"⚠️ Modelo {model_path} não encontrado! Usando cubo como Fallback.")
            # Carrega um cubo simples do próprio Panda3D como tapa-buraco
            from core.constants import MODEL_PLANE
            self.node = resource_loader.load_model(MODEL_PLANE)
            
            if self.node is None:
                raise Exception(f"Falha crítica: Nem o modelo de fallback carregou!")
        
        self.node.setScale(0.010)
        self.node.setPos(position)
        
        # Textura
        texture_path = TEXTURE_COLLECTIBLE_CORRUPTED if is_corrupted else TEXTURE_COLLECTIBLE
        resource_loader.apply_texture_to_model(self.node, texture_path)
        
        # Se corrompido, adiciona cor vermelha
        if is_corrupted:
            self.node.setColor(1.0, 0.2, 0.2, 1)
        
        # Collider
        col_type = 'corrupted' if is_corrupted else 'fragment'
        self.collider = collision_manager.create_collectible_collider(
            self.node,
            radius=1.0,
            collectible_type=col_type
        )
        
        self.is_alive = True
    
    def update(self, dt: float, speed: float, speed_multiplier: float = 1.0):
        """
        Atualiza coletável
        
        Args:
            dt: Delta time
            speed: Velocidade de queda
            speed_multiplier: Multiplicador (para slow-motion)
        """
        if not self.is_alive:
            return
        
        # Rotação
        current_h = self.node.getH()
        current_r = self.node.getR()
        self.node.setHpr(
            current_h + dt * self.rotation_speed,
            self.node.getP(),
            current_r + dt * self.rotation_speed
        )
        
        # Movimento descendente
        final_speed = speed * speed_multiplier
        new_z = self.node.getZ() - final_speed
        self.node.setZ(new_z)
        
        # Morre se saiu da tela
        if new_z < -9:
            self.is_alive = False
    
    def apply_magnet_force(self, player_pos: Vec3, magnet_force: float, 
                          magnet_radius: float, dt: float):
        """
        Aplica força de imã
        
        Args:
            player_pos: Posição do jogador
            magnet_force: Força do imã
            magnet_radius: Raio de atração
            dt: Delta time
        """
        if not self.is_alive:
            return
        
        frag_pos = self.node.getPos()
        vec = player_pos - Vec3(frag_pos.x, frag_pos.y, frag_pos.z)
        dist = vec.length()
        
        if dist < magnet_radius and dist > 0.01:
            direction = vec / dist
            new_pos = frag_pos + direction * magnet_force * dt
            self.node.setPos(new_pos)
    
    def destroy(self):
        """Remove da cena"""
        self.is_alive = False
        if self.node:
            self.node.removeNode()


# ====================================
# HAZARD (Meteoros/Lixo/Raios)
# ====================================

class Hazard:
    """Entidade de perigo (meteoro/lixo/raio)"""
    
    def __init__(self, resource_loader, collision_manager, position: Vec3,
                 hazard_type: str = "meteor"):
        """
        Inicializa perigo
        
        Args:
            resource_loader: ResourceLoader
            collision_manager: CollisionManager
            position: Posição inicial
            hazard_type: Tipo (meteor, trash, lightning, acid_drop)
        """
        from core.constants import (
            MODEL_HAZARD_METEOR, MODEL_HAZARD_TRASH_1, MODEL_HAZARD_TRASH_2,
            MODEL_HAZARD_TRASH_3, MODEL_LIGHTNING, MODEL_ACID_DROP,
            TEXTURE_TRASH_1, TEXTURE_TRASH_2, TEXTURE_TRASH_3
        )
        
        self.hazard_type = hazard_type
        self.rotation_speed = random.uniform(5, 8)
        self.velocity_x = 0  # Para raios que se movem horizontalmente
        
        # Seleciona modelo baseado no tipo
        if hazard_type == "meteor":
            model_path = MODEL_HAZARD_METEOR
            scale = 0.015
            color = Vec4(0.5, 0.5, 0.5, 1)
        elif hazard_type == "trash":
            model_path = random.choice([MODEL_HAZARD_TRASH_1, MODEL_HAZARD_TRASH_2, MODEL_HAZARD_TRASH_3])
            scale = 0.015
            color = Vec4(0.7, 0.7, 0.7, 1)
        elif hazard_type == "lightning":
            model_path = MODEL_LIGHTNING
            scale = 0.015
            color = Vec4(1.0, 1.0, 0.4, 1)
            self.velocity_x = random.uniform(-0.18, 0.18)
            if -0.05 < self.velocity_x < 0.05:
                self.velocity_x = 0.1 if random.random() < 0.5 else -0.1
        elif hazard_type == "acid_drop":
            model_path = MODEL_ACID_DROP
            scale = 0.15
            color = Vec4(1.0, 0.9, 0.3, 1)
        else:
            model_path = MODEL_HAZARD_METEOR
            scale = 0.01
            color = Vec4(0.5, 0.5, 0.5, 1)
        
        # Carrega modelo
        self.node = resource_loader.load_model(model_path)
        if self.node is None:
            print(f"⚠️ Modelo {model_path} não encontrado! Usando cubo como Fallback.")
            # Carrega um cubo simples do próprio Panda3D como tapa-buraco
            from core.constants import MODEL_PLANE
            self.node = resource_loader.load_model(MODEL_PLANE)
            
            if self.node is None:
                raise Exception(f"Falha crítica: Nem o modelo de fallback carregou!")
        
        self.node.setScale(scale)
        self.node.setPos(position)
        self.node.setColor(color)
        
        # Collider
        collision_radius = 1.6 if hazard_type != "lightning" else 1.3
        self.collider = collision_manager.create_hazard_collider(
            self.node,
            radius=collision_radius,
            hazard_type=hazard_type
        )
        
        self.is_alive = True
    
    def update(self, dt: float, speed: float, speed_multiplier: float = 1.0):
        """
        Atualiza perigo
        
        Args:
            dt: Delta time
            speed: Velocidade de queda
            speed_multiplier: Multiplicador
        """
        if not self.is_alive:
            return
        
        # Rotação
        current_h = self.node.getH()
        current_r = self.node.getR()
        self.node.setHpr(
            current_h - dt * self.rotation_speed,
            self.node.getP(),
            current_r + dt * self.rotation_speed
        )
        
        # Movimento descendente
        final_speed = speed * speed_multiplier
        new_z = self.node.getZ() - final_speed
        self.node.setZ(new_z)
        
        # Movimento horizontal (raios)
        if self.velocity_x != 0:
            new_x = self.node.getX() + self.velocity_x
            self.node.setX(new_x)
            
            # Inverte direção aleatoriamente
            if random.random() < 0.03:
                self.velocity_x = -self.velocity_x
        
        # Morre se saiu da tela
        if new_z < -9 or abs(self.node.getX()) > 18:
            self.is_alive = False
    
    def destroy(self):
        """Remove da cena"""
        self.is_alive = False
        if self.node:
            self.node.removeNode()


# ====================================
# POWERUP (Escudo/Imã/Slow-Motion)
# ====================================

class Powerup:
    """Entidade de power-up"""
    
    def __init__(self, resource_loader, collision_manager, position: Vec3,
                 powerup_type: str = "shield"):
        """
        Inicializa power-up
        
        Args:
            resource_loader: ResourceLoader
            collision_manager: CollisionManager
            position: Posição inicial
            powerup_type: Tipo (shield, magnet, slow)
        """
        from core.constants import MODEL_POWERUP_SHIELD, MODEL_PLANE
        
        self.powerup_type = powerup_type
        
        # Define modelo e cor baseado no tipo
        if powerup_type == "shield":
            try:
                model_path = MODEL_POWERUP_SHIELD
                self.node = resource_loader.load_model(model_path)
            except:
                model_path = MODEL_PLANE
                self.node = resource_loader.load_model(model_path)
            scale = 0.2
            color = Vec4(0.2, 0.5, 1.0, 1)  # Azul
        elif powerup_type == "magnet":
            model_path = MODEL_PLANE
            self.node = resource_loader.load_model(model_path)
            scale = 0.2
            color = Vec4(0.2, 1.0, 0.2, 1)  # Verde
        elif powerup_type == "slow":
            model_path = MODEL_PLANE
            self.node = resource_loader.load_model(model_path)
            scale = 0.2
            color = Vec4(1.0, 1.0, 0.3, 1)  # Amarelo
        else:
            model_path = MODEL_PLANE
            self.node = resource_loader.load_model(model_path)
            scale = 0.2
            color = Vec4(1, 1, 1, 1)
        
        if self.node is None:
            raise Exception(f"Falha ao carregar modelo de power-up: {powerup_type}")
        
        self.node.setScale(scale)
        self.node.setPos(position)
        self.node.setColor(color)
        
        # Collider
        self.collider = collision_manager.create_powerup_collider(
            self.node,
            radius=0.8,
            powerup_type=powerup_type
        )
        
        self.is_alive = True
    
    def update(self, dt: float, speed: float, speed_multiplier: float = 1.0):
        """
        Atualiza power-up
        
        Args:
            dt: Delta time
            speed: Velocidade de queda
            speed_multiplier: Multiplicador
        """
        if not self.is_alive:
            return
        
        # Rotação suave
        current_h = self.node.getH()
        self.node.setH(current_h + dt * 30)
        
        # Movimento descendente (mais lento que fragmentos)
        final_speed = speed * speed_multiplier * 0.75
        new_z = self.node.getZ() - final_speed
        self.node.setZ(new_z)
        
        # Morre se saiu da tela
        if new_z < -9:
            self.is_alive = False
    
    def destroy(self):
        """Remove da cena"""
        self.is_alive = False
        if self.node:
            self.node.removeNode()


print("GameEntities (Collectible, Hazard, Powerup) definidos com sucesso!")