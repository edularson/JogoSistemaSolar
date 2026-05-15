"""
JORNADA SOLAR - LOBBY DE VOO LIVRE (3D)
Exploração espacial em primeira pessoa para selecionar fases.
Adaptado para State Manager de Janela Única.
"""

from panda3d.core import WindowProperties, Vec4, Vec3, PointLight, AmbientLight, TextNode
from direct.gui.OnscreenText import OnscreenText
import math
import random
import os

class Lobby3D:
    """Lobby de exploração espacial (Estado)"""
    
    def __init__(self, app):
        print("Inicializando Lobby de Voo Livre...")
        self.app = app
        self.clock = self.app.taskMgr.globalClock
        
        # Listas para limpeza
        self.ui_elements = []
        self.planets = []
        self.star_particles = []
        
        # Configura caminhos de modelo
        from panda3d.core import get_model_path
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        get_model_path().prepend_directory(base_path)
        from levels.level_config import get_all_level_names, get_level_config
        
        self.save_manager = self.app.save_manager
        self.sound_manager = self.app.sound_manager
        self.resource_loader = self.app.resource_loader
        
        # Configurações de Voo
        self.speed = 50.0             
        self.boost_speed = 120.0      
        self.current_speed = 0.0
        self.mouse_sensitivity = 0.15 
        self.detection_radius = 15.0  
        self.controls_enabled = True
        self.planet_cooldown = 0.0    
        
        # Estado das teclas de movimento
        self.keys = {
            "forward": False, "backward": False,
            "left": False, "right": False, "boost": False
        }
        
        # Setup inicial
        self.setup_window(hide_cursor=True)
        self.app.disableMouse() 
        self.app.render.setShaderAuto()
        self.sound_manager.play_lobby_music()
        
        # Dados das fases
        self.level_names = get_all_level_names()
        self.level_configs = {}
        for name in self.level_names:
            self.level_configs[name] = get_level_config(name)
            
        # Criação do Universo
        self.setup_lighting()
        self.create_sun()
        self.create_planets()
        self.create_starfield(num_stars=400) 
        self.create_ui()
        
        # Posiciona a nave inicialmente
        self.app.camera.setPos(0, -200, 30)
        self.app.camera.lookAt(0, 0, 0) 
        
        # Controles
        self.setup_controls()
        
        # Task principal de atualização
        self.app.taskMgr.add(self.update_lobby, "UpdateLobbyTask")
        
        self.sound_manager.play_lobby_music()
        
        print("Lobby de Voo Livre pronto!")
        
    def setup_window(self, hide_cursor=True):
        """Configura janela e esconde/trava o mouse"""
        props = WindowProperties()
        props.setFullscreen(True)
        props.setSize(self.app.pipe.getDisplayWidth(), self.app.pipe.getDisplayHeight())
        props.setCursorHidden(hide_cursor)
        
        self.app.win.requestProperties(props)
        self.app.setBackgroundColor(0.005, 0.005, 0.01, 1) 
        
        if hide_cursor and self.app.mouseWatcherNode.hasMouse():
            cx = self.app.win.getProperties().getXSize() / 2
            cy = self.app.win.getProperties().getYSize() / 2
            self.app.win.movePointer(0, int(cx), int(cy))

    def setup_lighting(self):
        """Iluminação clara do espaço"""
        # Luz ambiente aumentada para clarear o lado escuro dos planetas
        ambient = AmbientLight("ambient")
        ambient.setColor(Vec4(0.4, 0.4, 0.45, 1)) 
        self.ambient_np = self.app.render.attachNewNode(ambient)
        self.app.render.setLight(self.ambient_np)
        
        # O SOL é a luz principal
        self.sun_light = PointLight("sun_light")
        self.sun_light.setColor(Vec4(1.0, 0.95, 0.8, 1))
        # Atenuação removida: A luz viaja infinitamente para iluminar todos os planetas bem!
        
        self.plight_np = self.app.render.attachNewNode(self.sun_light)
        self.plight_np.setPos(0, 0, 0)
        self.app.render.setLight(self.plight_np)

    def create_sun(self):
        """Cria o modelo visual do Sol"""
        sun_model = self.resource_loader.load_model("models/sphere")
        if sun_model:
            sun_model.reparentTo(self.app.render)
            sun_model.setPos(0, 0, 0)
            sun_model.setScale(12)
            
            # Tenta aplicar a textura do Sol
            self.resource_loader.apply_texture_to_model(sun_model, "imgs/sol/sol_fundo.png")
            
            # Ajusta a rotação para a textura ficar em pé
            sun_model.setHpr(0, 90, 0) 
            
            sun_model.setLightOff() # O Sol emite luz, não recebe
            self.sun_node = sun_model

    def create_planets(self):
        """Posiciona os planetas em órbitas e aplica as texturas reais"""
        orbital_distances = {
            'mercurio': 45, 'venus': 70, 'terra': 100, 'marte': 130,
            'jupiter': 180, 'saturno': 230, 'urano': 280, 'netuno': 330,
            'sol': 0 
        }
        
        planet_scales = {
            'mercurio': 0.7, 'venus': 1.8, 'terra': 2.0, 'marte': 1.6,
            'jupiter': 5.0, 'saturno': 4.5, 'urano': 3.0, 'netuno': 3.0,
            'sol': 0.1 
        }

        for i, lvl_name in enumerate(self.level_names):
            config = self.level_configs[lvl_name]
            dist = orbital_distances.get(lvl_name, 100 + i*20)
            
            angle = random.uniform(0, math.pi * 2)
            pos_x = math.cos(angle) * dist
            pos_y = math.sin(angle) * dist
            pos_z = random.uniform(-15, 15) 
            
            if lvl_name == 'sol': pos = Vec3(0,0,0) 
            else: pos = Vec3(pos_x, pos_y, pos_z)

            p_node = self.resource_loader.load_model("models/sphere")
            if not p_node: p_node = self.resource_loader.load_model("models/square")
            
            if p_node:
                p_node.reparentTo(self.app.render)
                p_node.setPos(pos)
                scale = planet_scales.get(lvl_name, 2.0)
                p_node.setScale(scale)
                
                # Ajusta a orientação da esfera para a textura não ficar "deitada"
                p_node.setHpr(0, 90, 0)
                
                # --- APLICAÇÃO DA TEXTURA ---
                texture_path = f"imgs/{lvl_name}/{lvl_name}.jpg"
                success = self.resource_loader.apply_texture_to_model(p_node, texture_path)
                
                if not success:
                    p_node.setColor(0.5, 0.5, 0.5, 1)
                
                is_unlocked = self.save_manager.is_level_unlocked(i)
                if not is_unlocked:
                    p_node.setColorScale(0.2, 0.2, 0.2, 1) 
                
                # --- LÓGICA DO ANEL DE SATURNO - falta fazer

                # Nome do planeta acima dele
                text = TextNode(f"txt_{lvl_name}")
                text.setText(config['display_name'].upper())
                text.setAlign(TextNode.ACenter)
                text_np = self.app.render.attachNewNode(text)
                text_np.setPos(pos.x, pos.y, pos.z + scale * 1.5)
                text_np.setScale(1.5)
                text_np.setBillboardPointEye() 
                if not is_unlocked: text.setTextColor(0.5, 0.5, 0.5, 1)
                
                self.planets.append({
                    'node': p_node,
                    'text_node': text_np,
                    'config': config,
                    'index': i,
                    'unlocked': is_unlocked,
                    'pos': pos,
                    'radius': scale,
                    'rot_speed': random.uniform(10, 30) # Velocidade de rotação aleatória
                })

    def create_starfield(self, num_stars=400):
        """Cria poeira estelar ao redor da câmera"""
        star_base = self.resource_loader.load_model("models/square")
        if not star_base: return

        for _ in range(num_stars):
            star = star_base.copyTo(self.app.render)
            x = random.uniform(-400, 400)
            y = random.uniform(-400, 400)
            z = random.uniform(-200, 200)
            star.setPos(x, y, z)
            # REDUZIDO: Partículas agora são apenas pontinhos brilhantes!
            star.setScale(random.uniform(0.02, 0.08)) 
            star.setColor(1, 1, 1, random.uniform(0.3, 0.8)) 
            star.setLightOff() 
            star.setBillboardPointEye()
            self.star_particles.append(star)
            
        star_base.removeNode()

    def create_ui(self):
        """Interface 2D"""
        self.ui_title = OnscreenText(
            text="SISTEMA SOLAR - VOO LIVRE", pos=(0, 0.92), scale=0.07,
            fg=Vec4(1, 0.8, 0.2, 1), align=TextNode.ACenter, shadow=(0,0,0,0.5)
        )
        self.ui_instructions = OnscreenText(
            text="[MOUSE] Olhar | [W/A/S/D] Mover | [SHIFT] Turbo | [F] Ir p/ Sol | [ESC] Menu",
            pos=(0, -0.95), scale=0.04, fg=Vec4(0.7, 0.7, 0.7, 1), align=TextNode.ACenter
        )
        self.ui_approach = OnscreenText(
            text="", pos=(0, -0.2), scale=0.06, fg=Vec4(1, 1, 1, 1),
            align=TextNode.ACenter, shadow=(0,0,0,0.5)
        )
        self.ui_elements.extend([self.ui_title, self.ui_instructions, self.ui_approach])

    def setup_controls(self):
        """Define as teclas de movimento e atalhos"""
        map = {"w": "forward", "s": "backward", "a": "left", "d": "right", "shift": "boost"}
        for key, action in map.items():
            self.app.accept(key, self.set_key, [action, True])
            self.app.accept(f"{key}-up", self.set_key, [action, False])
        
        self.app.accept('escape', self.back_to_menu)
        self.app.accept('f', self.teleport_to_sun)

    def set_key(self, key_name, value):
        if self.controls_enabled:
            self.keys[key_name] = value
            
    def teleport_to_sun(self):
        """Teleporta a nave instantaneamente para perto do Sol"""
        if not self.controls_enabled: return
        self.app.camera.setPos(0, -60, 10)
        self.app.camera.lookAt(0, 0, 0)
        try: self.sound_manager.play_menu_click_sound()
        except: pass

    def update_lobby(self, task):
        """Loop principal: Movimento da câmera e lógica"""
        dt = self.clock.getDt()
        self.planet_cooldown -= dt

        if not self.controls_enabled: return task.cont

        # 1. CONTROLE DO MOUSE
        if self.app.mouseWatcherNode.hasMouse():
            md = self.app.win.getPointer(0)
            x, y = md.getX(), md.getY()
            
            cx = self.app.win.getProperties().getXSize() / 2
            cy = self.app.win.getProperties().getYSize() / 2
            
            dx = (x - cx) * self.mouse_sensitivity
            dy = (y - cy) * self.mouse_sensitivity
            
            self.app.camera.setH(self.app.camera.getH() - dx)
            self.app.camera.setP(self.app.camera.getP() - dy)
            
            self.app.win.movePointer(0, int(cx), int(cy))

        # 2. CONTROLE DA NAVE
        speed = self.boost_speed if self.keys["boost"] else self.speed
        
        move_vec = Vec3(0, 0, 0)
        if self.keys["forward"]: move_vec.setY(move_vec.getY() + 1)
        if self.keys["backward"]: move_vec.setY(move_vec.getY() - 1)
        if self.keys["left"]: move_vec.setX(move_vec.getX() - 1)
        if self.keys["right"]: move_vec.setX(move_vec.getX() + 1)
        
        if move_vec.lengthSquared() > 0:
            move_vec.normalize()
            
        self.app.camera.setPos(self.app.camera, move_vec * speed * dt)
        
        for planet in self.planets:
            # Faz o planeta girar no seu próprio eixo (H = Heading)
            current_h = planet['node'].getH()
            planet['node'].setH(current_h + planet['rot_speed'] * dt)

        # 3. POEIRA ESTELAR INFINITA
        cam_pos = self.app.camera.getPos()
        for star in self.star_particles:
            v_to_star = star.getPos() - cam_pos
            if v_to_star.lengthSquared() > 500*500: 
                new_pos = cam_pos + Vec3(random.uniform(-400,400), random.uniform(-400,400), random.uniform(-400,400))
                star.setPos(new_pos)

        # 4. GATILHO DE PROXIMIDADE
        if self.planet_cooldown <= 0:
            closest_planet = None
            min_dist = self.detection_radius

            for planet in self.planets:
                dist = (cam_pos - planet['pos']).length()
                trigger_dist = self.detection_radius + planet['radius'] * 2
                
                if dist < trigger_dist:
                    if dist < min_dist:
                        min_dist = dist
                        closest_planet = planet
            
            if closest_planet:
                self.ui_approach.setText(f"Aproximando de: {closest_planet['config']['display_name'].upper()}")
                if min_dist < (planet['radius'] * 3 + 5): 
                    self.trigger_planet_entry(closest_planet)
            else:
                 self.ui_approach.setText("")

        return task.cont

    def trigger_planet_entry(self, planet_data):
        if not planet_data['unlocked']:
            self.ui_approach.setText("PLANETA BLOQUEADO! Complete as fases anteriores.")
            self.ui_approach.setFg((1, 0.3, 0.3, 1))
            self.sound_manager.play_damage_sound()
            self.planet_cooldown = 3.0 
            return

        print(f"Entrando na órbita de: {planet_data['config']['name']}")
        self.controls_enabled = False 
        self.ui_approach.setText("")
        self.sound_manager.play_menu_click_sound()
        self.show_objectives(planet_data['config'])

    def show_objectives(self, level_config):
        self.setup_window(hide_cursor=False) 
        from screens.objectives_screen import ObjectivesScreen
        self.objectives_screen = ObjectivesScreen(
            self, level_config,
            start_callback=lambda: self.start_level(level_config['name']),
            back_callback=self.cancel_entry
        )

    def cancel_entry(self):
        if hasattr(self, 'objectives_screen'): del self.objectives_screen
        self.setup_window(hide_cursor=True) 
        self.controls_enabled = True
        self.planet_cooldown = 2.0 

    def start_level(self, level_name):
        if self.sound_manager: self.sound_manager.stop_music(fade_out=0.5)
        self.app.change_state(f"fase_{level_name}")

    def back_to_menu(self):
        if self.sound_manager: self.sound_manager.stop_music(fade_out=0.5)
        self.app.change_state("menu")

    def cleanup(self):
        print("Limpando Lobby de Voo Livre...")
        self.app.ignoreAll()
        self.app.taskMgr.remove("UpdateLobbyTask")
        self.setup_window(hide_cursor=False)
        
        # Jeito correto de limpar luzes para não dar erro
        if hasattr(self, 'ambient_np') and self.ambient_np:
            self.app.render.clearLight(self.ambient_np)
            self.ambient_np.removeNode()
            
        if hasattr(self, 'plight_np') and self.plight_np:
            self.app.render.clearLight(self.plight_np)
            self.plight_np.removeNode()
        
        if hasattr(self, 'sun_node') and self.sun_node:
            self.sun_node.removeNode()
            self.sun_node = None

        for p in self.planets:
            p['node'].removeNode()
            p['text_node'].removeNode()
        self.planets.clear()
        
        for s in self.star_particles:
            s.removeNode()
        self.star_particles.clear()
        
        for elem in self.ui_elements: elem.destroy()
        self.ui_elements.clear()

if __name__ == "__main__":
    lobby = Lobby3D()
    lobby.run()