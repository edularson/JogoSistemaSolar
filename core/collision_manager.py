"""
JORNADA SOLAR - COLLISION MANAGER
Sistema centralizado de gerenciamento de colisões
Simplifica detecção e resposta a colisões
"""
from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionHandlerQueue, CollisionNode, CollisionSphere, BitMask32
from typing import Callable, Dict, List, Optional


class CollisionManager:
    """
    Gerenciador de colisões do jogo.
    Centraliza criação de colliders e detecção de colisões.
    """
    
    def __init__(self):
        """Inicializa o Collision Manager"""
        # Traverser principal do jogo
        self.traverser = CollisionTraverser("main_traverser")
        
        # Handler de filas para colisões
        self.handler = CollisionHandlerQueue()
        
        # Dicionário de colliders ativos {nome: (node_path, tipo)}
        self.active_colliders: Dict[str, tuple] = {}
        
        # Callbacks de colisão {tipo_colidido: função}
        self.collision_callbacks: Dict[str, Callable] = {}
        
        # Máscaras de colisão (bitwise)
        self.MASK_PLAYER = BitMask32.bit(1)
        self.MASK_COLLECTIBLE = BitMask32.bit(2)
        self.MASK_HAZARD = BitMask32.bit(3)
        self.MASK_POWERUP = BitMask32.bit(4)
        self.MASK_SPECIAL = BitMask32.bit(5)  # Para mecânicas especiais
        
        print("CollisionManager inicializado")
    
    # ====================================
    # CRIAÇÃO DE COLLIDERS
    # ====================================
    
    def create_sphere_collider(self, node_path, name: str, radius: float,
                              from_mask: BitMask32, into_mask: BitMask32,
                              tag_type: Optional[str] = None):
        """
        Cria um collider esférico e anexa ao node
        
        Args:
            node_path: NodePath onde anexar
            name: Nome do collider
            radius: Raio da esfera
            from_mask: Máscara "FROM" (o que este objeto procura colidir)
            into_mask: Máscara "INTO" (com o que este objeto pode colidir)
            tag_type: Tag de tipo para identificação
            
        Returns:
            NodePath do collider
        """
        # Cria esfera de colisão
        collision_sphere = CollisionSphere(0, 0, 0, radius)
        
        # Cria nó de colisão
        collision_node = CollisionNode(name)
        collision_node.addSolid(collision_sphere)
        
        # Define máscaras
        collision_node.setFromCollideMask(from_mask)
        collision_node.setIntoCollideMask(into_mask)
        
        # Anexa ao node_path
        collider_np = node_path.attachNewNode(collision_node)
        
        # Adiciona tag se fornecido
        if tag_type:
            collider_np.setTag('type', tag_type)
        
        # Registra no dicionário
        self.active_colliders[name] = (collider_np, tag_type)
        
        return collider_np
    
    def create_player_collider(self, player_node, radius: float = 15):
        """
        Cria collider específico para o jogador
        
        Args:
            player_node: NodePath do jogador
            radius: Raio de colisão
            
        Returns:
            NodePath do collider
        """
        collider = self.create_sphere_collider(
            node_path=player_node,
            name='player_collider',
            radius=radius,
            from_mask=self.MASK_PLAYER,
            into_mask=BitMask32.all_off(),
            tag_type='player'
        )
        
        # Adiciona ao traverser
        self.traverser.addCollider(collider, self.handler)
        
        print(f"Collider do jogador criado (raio: {radius})")
        return collider
    
    def create_collectible_collider(self, collectible_node, radius: float = 1.0,
                                   collectible_type: str = 'fragment'):
        """
        Cria collider para fragmento/cristal coletável
        
        Args:
            collectible_node: NodePath do coletável
            radius: Raio de colisão
            collectible_type: Tipo (fragment, crystal, etc)
            
        Returns:
            NodePath do collider
        """
        return self.create_sphere_collider(
            node_path=collectible_node,
            name=f'collectible_{id(collectible_node)}',
            radius=radius,
            from_mask=BitMask32.all_off(),
            into_mask=self.MASK_PLAYER, 
            tag_type=collectible_type
        )
    
    def create_hazard_collider(self, hazard_node, radius: float = 1.2,
                              hazard_type: str = 'meteor'):
        """
        Cria collider para perigo (meteoro, lixo, etc)
        
        Args:
            hazard_node: NodePath do perigo
            radius: Raio de colisão
            hazard_type: Tipo (meteor, trash, lightning, etc)
            
        Returns:
            NodePath do collider
        """
        return self.create_sphere_collider(
            node_path=hazard_node,
            name=f'hazard_{id(hazard_node)}',
            radius=radius,
            from_mask=BitMask32.all_off(),
            into_mask=self.MASK_PLAYER,
            tag_type=hazard_type
        )
    
    def create_powerup_collider(self, powerup_node, radius: float = 0.8,
                               powerup_type: str = 'shield'):
        """
        Cria collider para power-up
        
        Args:
            powerup_node: NodePath do power-up
            radius: Raio de colisão
            powerup_type: Tipo (shield, magnet, slow)
            
        Returns:
            NodePath do collider
        """
        return self.create_sphere_collider(
            node_path=powerup_node,
            name=f'powerup_{id(powerup_node)}',
            radius=radius,
            from_mask=BitMask32.all_off(),
            into_mask=self.MASK_PLAYER,
            tag_type=powerup_type
        )
    
    def create_special_collider(self, node, radius: float, special_type: str):
        """
        Cria collider para mecânicas especiais
        (ex: poças de ácido, sombras do Sol, áreas de vento)
        
        Args:
            node: NodePath do objeto especial
            radius: Raio de colisão
            special_type: Tipo especial (pool, shadow, wind_zone)
            
        Returns:
            NodePath do collider
        """
        return self.create_sphere_collider(
            node_path=node,
            name=f'special_{id(node)}',
            radius=radius,
            from_mask=BitMask32.all_off(),
            into_mask=self.MASK_PLAYER,
            tag_type=special_type
        )
    
    # ====================================
    # DETECÇÃO DE COLISÕES
    # ====================================
    
    def check_collisions(self, render) -> List[Dict]:
        """
        Verifica todas as colisões do frame atual
        
        Args:
            render: Nó render para traversar
            
        Returns:
            Lista de colisões detectadas com info
        """
        # Executa o traverser
        self.traverser.traverse(render)
        
        # Processa entradas da fila
        collisions = []
        
        for i in range(self.handler.getNumEntries()):
            entry = self.handler.getEntry(i)
            
            # Pega o node que foi colidido
            into_node = entry.getIntoNodePath()
            parent_node = into_node.getParent()
            
            # Pega o tipo via tag
            collision_type = into_node.getTag('type') if into_node.hasTag('type') else 'unknown'
            
            # Adiciona à lista
            collision_info = {
                'type': collision_type,
                'node': parent_node,
                'collider': into_node,
                'entry': entry
            }
            
            collisions.append(collision_info)
        
        return collisions
    
    def register_collision_callback(self, collision_type: str, callback: Callable):
        """
        Registra callback para tipo de colisão
        
        Args:
            collision_type: Tipo de colisão (fragment, meteor, etc)
            callback: Função a chamar (recebe collision_info)
        """
        self.collision_callbacks[collision_type] = callback
        print(f"📞 Callback registrado para colisão: {collision_type}")
    
    def process_collisions_with_callbacks(self, render):
        """
        Verifica colisões e chama callbacks registrados
        
        Args:
            render: Nó render
        """
        collisions = self.check_collisions(render)
        
        for collision in collisions:
            col_type = collision['type']
            
            # Se existe callback para este tipo, chama
            if col_type in self.collision_callbacks:
                self.collision_callbacks[col_type](collision)
    
    # ====================================
    # HELPERS
    # ====================================
    
    def remove_collider(self, collider_name: str):
        """
        Remove um collider registrado
        
        Args:
            collider_name: Nome do collider
        """
        if collider_name in self.active_colliders:
            collider_np, _ = self.active_colliders[collider_name]
            
            # Remove do traverser se for do jogador
            if 'player' in collider_name:
                self.traverser.removeCollider(collider_np)
            
            # Remove do dicionário
            del self.active_colliders[collider_name]
            
            print(f"Collider removido: {collider_name}")
    
    def clear_all_colliders(self):
        """Remove todos os colliders registrados"""
        for name in list(self.active_colliders.keys()):
            self.remove_collider(name)
        
        self.active_colliders.clear()
        print("Todos colliders limpos")
    
    def show_collision_spheres(self, show: bool = True):
        """
        Mostra/esconde esferas de colisão (debug)
        
        Args:
            show: True para mostrar, False para esconder
        """
        if show:
            self.traverser.showCollisions(render)
            print("Esferas de colisão visíveis (DEBUG)")
        else:
            self.traverser.hideCollisions()
            print("Esferas de colisão escondidas")
    
    def get_active_colliders_count(self) -> int:
        """Retorna número de colliders ativos"""
        return len(self.active_colliders)
    
    def print_collision_stats(self):
        """Imprime estatísticas de colisões"""
        print("Collision Stats:")
        print(f"   Colliders ativos: {len(self.active_colliders)}")
        
        # Conta por tipo
        types_count = {}
        for _, (_, col_type) in self.active_colliders.items():
            if col_type:
                types_count[col_type] = types_count.get(col_type, 0) + 1
        
        for col_type, count in types_count.items():
            print(f"   {col_type}: {count}")
    
    # ====================================
    # DETECÇÃO MANUAL (sem traverser)
    # ====================================
    
    def check_distance_collision(self, pos1: tuple, pos2: tuple, 
                                 radius1: float, radius2: float) -> bool:
        """
        Verifica colisão por distância (útil para checks manuais)
        
        Args:
            pos1: Posição (x, y, z) do objeto 1
            pos2: Posição (x, y, z) do objeto 2
            radius1: Raio do objeto 1
            radius2: Raio do objeto 2
            
        Returns:
            True se estão colidindo
        """
        from panda3d.core import Vec3
        
        vec1 = Vec3(*pos1)
        vec2 = Vec3(*pos2)
        
        distance = (vec2 - vec1).length()
        collision_distance = radius1 + radius2
        
        return distance <= collision_distance
    
    def get_closest_collectible(self, player_pos: tuple, 
                               collectibles: list) -> Optional[tuple]:
        """
        Encontra coletável mais próximo do jogador
        
        Args:
            player_pos: Posição do jogador
            collectibles: Lista de NodePaths de coletáveis
            
        Returns:
            (NodePath, distância) ou None
        """
        from panda3d.core import Vec3
        
        player_vec = Vec3(*player_pos)
        closest = None
        min_distance = float('inf')
        
        for collectible in collectibles:
            col_pos = collectible.getPos()
            col_vec = Vec3(col_pos.x, col_pos.y, col_pos.z)
            
            distance = (col_vec - player_vec).length()
            
            if distance < min_distance:
                min_distance = distance
                closest = (collectible, distance)
        
        return closest


print("CollisionManager class definida com sucesso!")