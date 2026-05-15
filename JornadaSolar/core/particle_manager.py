"""
JORNADA SOLAR - PARTICLE MANAGER
Sistema de partículas para efeitos visuais
Cria explosões, trails, brilhos e outros efeitos
"""
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, Vec4, Point3
from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect
from direct.particles.ForceGroup import ForceGroup
from direct.interval.IntervalGlobal import Sequence, Func, Wait, LerpColorScaleInterval, LerpScaleInterval
from typing import Optional, List
import random


class ParticleManager:
    """
    Gerenciador de efeitos de partículas.
    Cria e controla efeitos visuais do jogo.
    """
    
    def __init__(self, render, loader):
        """
        Inicializa o Particle Manager
        
        Args:
            render: Nó render do Panda3D
            loader: Loader para carregar modelos de partículas
        """
        self.render = render
        self.loader = loader
        
        # Lista de efeitos ativos
        self.active_effects: List = []
        
        print("ParticleManager inicializado")
    
    # ====================================
    # EFEITOS SIMPLES (usando modelos)
    # ====================================
    
    def create_simple_particle(self, position: Vec3, color: Vec4, 
                              velocity: Vec3, lifetime: float = 0.5,
                              scale: float = 0.05):
        """
        Cria uma partícula simples usando um modelo esférico
        
        Args:
            position: Posição inicial
            color: Cor RGBA
            velocity: Vetor de velocidade
            lifetime: Tempo de vida em segundos
            scale: Escala da partícula
            
        Returns:
            NodePath da partícula
        """
        from core.constants import MODEL_PLANE
        
        # Carrega modelo simples
        particle = self.loader.loadModel(MODEL_PLANE)
        particle.reparentTo(self.render)
        particle.setPos(position)
        particle.setScale(scale)
        particle.setColor(color)
        particle.setTransparency(True)
        
        # Define velocidade como tag para update
        particle.setPythonTag("velocity", velocity)
        particle.setPythonTag("lifetime", lifetime)
        particle.setPythonTag("age", 0.0)
        
        self.active_effects.append(particle)
        
        return particle
    
    def create_explosion(self, position: Vec3, color: Vec4, 
                        particle_count: int = 15, speed: float = 3.0):
        """
        Cria efeito de explosão de partículas
        
        Args:
            position: Posição da explosão
            color: Cor das partículas
            particle_count: Número de partículas
            speed: Velocidade das partículas
        """
        for _ in range(particle_count):
            # Direção aleatória
            direction = Vec3(
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                random.uniform(-1, 1)
            ).normalized()
            
            velocity = direction * speed
            
            # Cria partícula
            particle = self.create_simple_particle(
                position=position,
                color=color,
                velocity=velocity,
                lifetime=random.uniform(0.3, 0.7),
                scale=random.uniform(0.03, 0.08)
            )
            
            # Animação de fade out
            Sequence(
                LerpColorScaleInterval(particle, 0.5, Vec4(1, 1, 1, 0)),
                Func(self._remove_particle, particle)
            ).start()
    
    def create_collect_effect(self, position: Vec3):
        """
        Efeito de coletar fragmento (partículas roxas)
        
        Args:
            position: Posição do fragmento coletado
        """
        from core.constants import COLOR_PURPLE, PARTICLE_COUNT_COLLECT
        
        self.create_explosion(
            position=position,
            color=Vec4(0.7, 0.2, 1.0, 1),
            particle_count=PARTICLE_COUNT_COLLECT,
            speed=2.5
        )
    
    def create_damage_effect(self, position: Vec3):
        """
        Efeito de tomar dano (partículas vermelhas)
        
        Args:
            position: Posição do impacto
        """
        from core.constants import COLOR_RED, PARTICLE_COUNT_DAMAGE
        
        self.create_explosion(
            position=position,
            color=Vec4(1.0, 0.2, 0.0, 1),
            particle_count=PARTICLE_COUNT_DAMAGE,
            speed=3.0
        )
    
    def create_powerup_effect(self, position: Vec3, powerup_type: str):
        """
        Efeito de pegar power-up (cor varia por tipo)
        
        Args:
            position: Posição do power-up
            powerup_type: Tipo (shield, magnet, slow)
        """
        from core.constants import PARTICLE_COUNT_POWERUP
        
        # Define cor por tipo
        colors = {
            "shield": Vec4(0.2, 0.5, 1.0, 1),  # Azul
            "magnet": Vec4(0.2, 1.0, 0.2, 1),  # Verde
            "slow": Vec4(1.0, 1.0, 0.3, 1)     # Amarelo
        }
        
        color = colors.get(powerup_type, Vec4(1, 1, 1, 1))
        
        self.create_explosion(
            position=position,
            color=color,
            particle_count=PARTICLE_COUNT_POWERUP,
            speed=2.0
        )
    
    # ====================================
    # TRAILS (Rastros)
    # ====================================
    
    def create_trail_particle(self, position: Vec3, color: Vec4):
        """
        Cria partícula de rastro que desaparece rapidamente
        
        Args:
            position: Posição da partícula
            color: Cor da partícula
        """
        from core.constants import MODEL_PLANE
        
        trail = self.loader.loadModel(MODEL_PLANE)
        trail.reparentTo(self.render)
        trail.setPos(position)
        trail.setScale(0.03)
        trail.setColor(color)
        trail.setTransparency(True)
        
        # Fade out rápido
        Sequence(
            LerpColorScaleInterval(trail, 0.3, Vec4(1, 1, 1, 0)),
            LerpScaleInterval(trail, 0.3, 0.01),
            Func(trail.removeNode)
        ).start()
    
    def create_meteor_trail(self, meteor_node):
        """
        Cria rastro de meteoro
        
        Args:
            meteor_node: NodePath do meteoro
        """
        pos = meteor_node.getPos()
        self.create_trail_particle(
            position=Vec3(pos.x, pos.y, pos.z),
            color=Vec4(1.0, 0.5, 0.0, 0.6)  # Laranja translúcido
        )
    
    def create_lightning_flash(self, position: Vec3):
        """
        Cria flash de luz (para raios de Júpiter)
        
        Args:
            position: Posição do flash
        """
        from core.constants import MODEL_PLANE
        
        flash = self.loader.loadModel(MODEL_PLANE)
        flash.reparentTo(self.render)
        flash.setPos(position)
        flash.setScale(0.5)
        flash.setColor(1, 1, 0.8, 0.9)
        flash.setTransparency(True)
        
        # Pisca e some
        Sequence(
            LerpColorScaleInterval(flash, 0.1, Vec4(1.5, 1.5, 1.0, 1)),
            LerpColorScaleInterval(flash, 0.2, Vec4(1, 1, 1, 0)),
            Func(flash.removeNode)
        ).start()
    
    # ====================================
    # EFEITOS AMBIENTAIS
    # ====================================
    
    def create_ambient_sparkles(self, position: Vec3, count: int = 5):
        """
        Cria brilhos ambientais (para chuva de cristais, etc)
        
        Args:
            position: Posição central
            count: Número de brilhos
        """
        for _ in range(count):
            offset = Vec3(
                random.uniform(-2, 2),
                random.uniform(-1, 1),
                random.uniform(-2, 2)
            )
            
            sparkle_pos = position + offset
            
            self.create_simple_particle(
                position=sparkle_pos,
                color=Vec4(1, 1, 1, 0.8),
                velocity=Vec3(0, 0, 0),
                lifetime=random.uniform(0.2, 0.5),
                scale=random.uniform(0.02, 0.05)
            )
    
    def create_acid_bubble(self, position: Vec3):
        """
        Cria bolha de ácido (para Vênus)
        
        Args:
            position: Posição da bolha
        """
        from core.constants import MODEL_PLANE
        
        bubble = self.loader.loadModel(MODEL_PLANE)
        bubble.reparentTo(self.render)
        bubble.setPos(position)
        bubble.setScale(0.02)
        bubble.setColor(1.0, 0.95, 0.3, 0.6) 
        bubble.setTransparency(True)
        
        # Sobe e estoura
        final_pos = position + Vec3(0, 0, random.uniform(0.5, 1.5))
        
        Sequence(
            bubble.posInterval(random.uniform(0.5, 1.0), final_pos),
            LerpScaleInterval(bubble, 0.1, 0.05),
            LerpColorScaleInterval(bubble, 0.1, Vec4(1, 1, 1, 0)),
            Func(bubble.removeNode)
        ).start()
    
    def create_heat_wave(self, position: Vec3, width: float = 5.0):
        """
        Cria onda de calor visual (para Mercúrio/Sol)
        
        Args:
            position: Posição da onda
            width: Largura da onda
        """
        from core.constants import MODEL_PLANE
        
        wave = self.loader.loadModel(MODEL_PLANE)
        wave.reparentTo(self.render)
        wave.setPos(position)
        wave.setScale(0.1, 1, width)
        wave.setColor(1.0, 0.6, 0.0, 0.3)
        wave.setTransparency(True)
        
        # Expande e desaparece
        Sequence(
            LerpScaleInterval(wave, 1.0, (width, 1, width)),
            LerpColorScaleInterval(wave, 0.5, Vec4(1, 1, 1, 0)),
            Func(wave.removeNode)
        ).start()
    
    # ====================================
    # EFEITOS DE POWER-UP ATIVOS
    # ====================================
    
    def create_shield_aura(self, player_node):
        """
        Cria aura de escudo ao redor do jogador
        
        Args:
            player_node: NodePath do jogador
            
        Returns:
            NodePath da aura (para remover depois)
        """
        from core.constants import MODEL_PLANE
        
        aura = self.loader.loadModel(MODEL_PLANE)
        aura.reparentTo(player_node)
        aura.setScale(1.5)
        aura.setColor(0.2, 0.5, 1.0, 0.4)
        aura.setTransparency(True)
        
        # Animação de pulsar
        def pulse_aura(task):
            if aura:
                scale = 1.5 + 0.2 * (task.time * 4) % 1
                aura.setScale(scale)
            return task.cont
        
        taskMgr.add(pulse_aura, "shield_aura_pulse")
        
        return aura
    
    def remove_shield_aura(self, aura_node):
        """
        Remove aura de escudo
        
        Args:
            aura_node: NodePath da aura
        """
        taskMgr.remove("shield_aura_pulse")
        if aura_node:
            aura_node.removeNode()
    
    def create_magnet_effect(self, player_node):
        """
        Cria efeito visual de imã ativo
        
        Args:
            player_node: NodePath do jogador
            
        Returns:
            NodePath do efeito
        """
        from core.constants import MODEL_PLANE
        
        magnet_ring = self.loader.loadModel(MODEL_PLANE)
        magnet_ring.reparentTo(player_node)
        magnet_ring.setScale(2.0)
        magnet_ring.setColor(0.2, 1.0, 0.2, 0.3)
        magnet_ring.setTransparency(True)
        
        # Rotação constante
        magnet_ring.hprInterval(2.0, (360, 0, 0)).loop()
        
        return magnet_ring
    
    # ====================================
    # UPDATE E LIMPEZA
    # ====================================
    
    def update_particles(self, dt: float):
        """
        Atualiza todas as partículas ativas
        
        Args:
            dt: Delta time
        """
        particles_to_remove = []
        
        for particle in self.active_effects:
            if not particle:
                continue
            
            # Atualiza idade
            age = particle.getPythonTag("age") if particle.hasPythonTag("age") else 0
            lifetime = particle.getPythonTag("lifetime") if particle.hasPythonTag("lifetime") else 1.0
            
            age += dt
            particle.setPythonTag("age", age)
            
            # Move partícula
            if particle.hasPythonTag("velocity"):
                velocity = particle.getPythonTag("velocity")
                current_pos = particle.getPos()
                new_pos = current_pos + velocity * dt
                particle.setPos(new_pos)
            
            # Remove se expirou
            if age >= lifetime:
                particles_to_remove.append(particle)
        
        # Limpa partículas expiradas
        for particle in particles_to_remove:
            self._remove_particle(particle)
    
    def _remove_particle(self, particle):
        """
        Remove uma partícula
        
        Args:
            particle: NodePath da partícula
        """
        if particle in self.active_effects:
            self.active_effects.remove(particle)
        
        try:
            particle.removeNode()
        except:
            pass
    
    def clear_all_effects(self):
        """Remove todos os efeitos ativos"""
        for effect in self.active_effects:
            try:
                effect.removeNode()
            except:
                pass
        
        self.active_effects.clear()
        print("Todos efeitos de partículas limpos")
    
    def get_active_effects_count(self) -> int:
        """Retorna número de efeitos ativos"""
        return len(self.active_effects)


print("ParticleManager class definida com sucesso!")