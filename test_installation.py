"""
JORNADA SOLAR - SCRIPT DE TESTE
Verifica se tudo está instalado corretamente
"""

import sys
import os

def test_python_version():
    """Testa versão do Python"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"Python {version.major}.{version.minor} - Necessário 3.8+")
        return False

def test_panda3d():
    """Testa se Panda3D está instalado"""
    try:
        import direct.showbase.ShowBase
        print("Panda3D instalado - OK")
        return True
    except ImportError:
        print("Panda3D não encontrado - Execute: pip install panda3d")
        return False

def test_imports():
    """Testa imports dos módulos do jogo"""
    modules = [
        ("core.constants", "Constants"),
        ("core.resource_loader", "ResourceLoader"),
        ("core.save_manager", "SaveManager"),
        ("core.sound_manager", "SoundManager"),
        ("core.ui_manager", "UIManager"),
        ("core.collision_manager", "CollisionManager"),
        ("core.particle_manager", "ParticleManager"),
        ("core.base_level", "BaseLevel"),
        ("entities.player", "Player"),
        ("entities.game_entities", "Collectible"),
        ("levels.level_config", "LEVEL_CONFIGS"),
        ("levels.specific_levels", "create_level"),
    ]
    
    all_ok = True
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"{module_name} - OK")
        except Exception as e:
            print(f"{module_name} - ERRO: {e}")
            all_ok = False
    
    return all_ok

def test_directories():
    """Testa se diretórios necessários existem"""
    dirs = [
        "core",
        "entities",
        "levels",
        "screens",
        "sounds",
        "music"
    ]
    
    all_ok = True
    for dir_name in dirs:
        if os.path.isdir(dir_name):
            print(f"Diretório '{dir_name}' - OK")
        else:
            print(f"Diretório '{dir_name}' - FALTANDO")
            all_ok = False
    
    return all_ok

def test_level_files():
    """Testa se arquivos de fase existem"""
    phases = [
        "levels/fase_netuno.py",
        "levels/fase_urano.py",
        "levels/fase_saturno.py",
        "levels/fase_jupiter.py",
        "levels/fase_marte.py",
        "levels/fase_terra.py",
        "levels/fase_venus.py",
        "levels/fase_mercurio.py",
        "levels/fase_sol.py"
    ]
    
    all_ok = True
    for phase in phases:
        if os.path.isfile(phase):
            print(f"{phase} - OK")
        else:
            print(f"{phase} - FALTANDO")
            all_ok = False
    
    return all_ok

def test_main_files():
    """Testa se arquivos principais existem"""
    files = [
        "main.py",
        "screens/main_menu.py",
        "screens/lobby_3d.py",
        "screens/objectives_screen.py",
        "screens/achievements_screen.py",
        "screens/settings_screen.py"
    ]
    
    all_ok = True
    for file in files:
        if os.path.isfile(file):
            print(f"{file} - OK")
        else:
            print(f"{file} - FALTANDO")
            all_ok = False
    
    return all_ok

def check_assets():
    """Verifica assets (não obrigatório)"""
    print("\n⚠️ VERIFICAÇÃO DE ASSETS (OPCIONAL):")
    
    if os.path.isdir("imgs"):
        print("Diretório 'imgs/' encontrado")
    else:
        print("⚠️ Diretório 'imgs/' não encontrado (copie do projeto original)")
    
    if os.path.isdir("models"):
        print("Diretório 'models/' encontrado")
    else:
        print("⚠️ Diretório 'models/' não encontrado (copie do projeto original)")
    
    # Sons são opcionais
    sound_files = [f for f in os.listdir("sounds") if f.endswith(".wav")] if os.path.isdir("sounds") else []
    if sound_files:
        print(f"{len(sound_files)} arquivos de som encontrados")
    else:
        print("Nenhum som encontrado (opcional - jogo funciona sem)")
    
    music_files = [f for f in os.listdir("music") if f.endswith(".ogg")] if os.path.isdir("music") else []
    if music_files:
        print(f"{len(music_files)} arquivos de música encontrados")
    else:
        print("Nenhuma música encontrada (opcional - jogo funciona sem)")

def main():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("JORNADA SOLAR - TESTE DE INSTALAÇÃO")
    print("="*60 + "\n")
    
    results = []
    
    print("TESTANDO PRÉ-REQUISITOS:")
    results.append(("Python", test_python_version()))
    results.append(("Panda3D", test_panda3d()))
    
    print("\nTESTANDO IMPORTS:")
    results.append(("Imports", test_imports()))
    
    print("\nTESTANDO ESTRUTURA:")
    results.append(("Diretórios", test_directories()))
    results.append(("Fases", test_level_files()))
    results.append(("Telas", test_main_files()))
    
    check_assets()
    
    print("\n" + "="*60)
    print("RESUMO DOS TESTES:")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "PASSOU" if passed else "FALHOU"
        print(f"{name:20} {status}")
        if not passed:
            all_passed = False
    
    print("="*60 + "\n")
    
    if all_passed:
        print("TODOS OS TESTES PASSARAM!")
        print("O jogo está pronto para rodar!")
        print("\nPara iniciar:")
        print("  python main.py")
        print("\nOu testar fase individual:")
        print("  python fase_netuno.py")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM")
        print("Verifique os erros acima e corrija antes de rodar o jogo.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)