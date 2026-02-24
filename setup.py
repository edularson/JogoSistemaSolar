#!/usr/bin/env python3
"""
JORNADA SOLAR - SETUP AUTOMÁTICO
Script para configurar o jogo automaticamente
"""

import os
import sys
import shutil

def print_header(text):
    """Imprime cabeçalho"""
    print("\n" + "="*60)
    print(text)
    print("="*60 + "\n")

def check_python():
    """Verifica versão do Python"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"Python {version.major}.{version.minor}.{version.micro} OK")
        return True
    else:
        print(f"Python {version.major}.{version.minor} - INCOMPATÍVEL")
        print("   Necessário Python 3.8 ou superior")
        return False

def check_panda3d():
    """Verifica se Panda3D está instalado"""
    try:
        import direct.showbase.ShowBase
        print("Panda3D instalado")
        return True
    except ImportError:
        print("Panda3D não instalado")
        return False

def install_panda3d():
    """Tenta instalar Panda3D"""
    print("\n🔧 Tentando instalar Panda3D...")
    
    import subprocess
    try:
        subprocess.check_call([
            sys.executable, 
            "-m", 
            "pip", 
            "install", 
            "panda3d",
            "--break-system-packages"
        ])
        print("Panda3D instalado com sucesso!")
        return True
    except:
        print("Falha ao instalar Panda3D")
        print("   Execute manualmente: pip install panda3d --break-system-packages")
        return False

def find_original_project():
    """Tenta encontrar projeto original"""
    possible_paths = [
        "../SISTEMASOLAR",
        "../../SISTEMASOLAR",
        "../SistemaSolar",
        "../../SistemaSolar"
    ]
    
    for path in possible_paths:
        if os.path.isdir(path):
            if os.path.isdir(os.path.join(path, "imgs")) and \
               os.path.isdir(os.path.join(path, "models")):
                return path
    
    return None

def copy_assets(source_path):
    """Copia assets do projeto original"""
    print(f"\nCopiando assets de {source_path}...")
    
    # Copia imgs
    src_imgs = os.path.join(source_path, "imgs")
    if os.path.isdir(src_imgs):
        if os.path.isdir("imgs"):
            print("⚠️ Diretório imgs/ já existe, pulando...")
        else:
            shutil.copytree(src_imgs, "imgs")
            print("Diretório imgs/ copiado")
    
    # Copia models
    src_models = os.path.join(source_path, "models")
    if os.path.isdir(src_models):
        if os.path.isdir("models"):
            print("⚠️ Diretório models/ já existe, pulando...")
        else:
            shutil.copytree(src_models, "models")
            print("Diretório models/ copiado")
    
    # Tenta copiar sons (opcional)
    src_sounds = os.path.join(source_path, "sons")
    if os.path.isdir(src_sounds):
        for f in os.listdir(src_sounds):
            if f.endswith(('.wav', '.ogg', '.mp3')):
                shutil.copy2(
                    os.path.join(src_sounds, f),
                    os.path.join("sounds", f)
                )
        print("Sons copiados (se existirem)")
    
    # Tenta copiar músicas (opcional)
    src_music = os.path.join(source_path, "musicas")
    if os.path.isdir(src_music):
        for f in os.listdir(src_music):
            if f.endswith(('.wav', '.ogg', '.mp3')):
                shutil.copy2(
                    os.path.join(src_music, f),
                    os.path.join("music", f)
                )
        print("Músicas copiadas (se existirem)")

def manual_asset_instructions():
    """Mostra instruções para copiar assets manualmente"""
    print("\nCOPIE OS ASSETS MANUALMENTE:")
    print("\n1. Localize seu projeto original (SISTEMASOLAR/)")
    print("2. Execute os seguintes comandos:")
    print("\n   cp -r /caminho/do/SISTEMASOLAR/imgs ./")
    print("   cp -r /caminho/do/SISTEMASOLAR/models ./")
    print("\n3. Opcional (sons):")
    print("   cp /caminho/do/SISTEMASOLAR/sons/* ./sounds/")
    print("   cp /caminho/do/SISTEMASOLAR/musicas/* ./music/")

def create_missing_directories():
    """Cria diretórios faltantes"""
    dirs = ["sounds", "music"]
    for d in dirs:
        if not os.path.isdir(d):
            os.makedirs(d)
            print(f"Diretório {d}/ criado")

def main():
    """Executa setup"""
    print_header("JORNADA SOLAR - SETUP AUTOMÁTICO")
    
    print("Verificando Python...")
    if not check_python():
        print("\nSetup abortado - Python incompatível")
        return False
    
    print("\nVerificando Panda3D...")
    if not check_panda3d():
        response = input("\nDeseja instalar Panda3D? (s/n): ")
        if response.lower() in ['s', 'sim', 'y', 'yes']:
            if not install_panda3d():
                print("\n⚠️ Continue manualmente instalando Panda3D")
        else:
            print("\n⚠️ Panda3D é necessário para rodar o jogo")
            return False
    
    print("\nCriando diretórios...")
    create_missing_directories()
    
    print("\nProcurando projeto original...")
    original_path = find_original_project()
    
    if original_path:
        print(f"Encontrado: {original_path}")
        response = input("\nDeseja copiar assets automaticamente? (s/n): ")
        if response.lower() in ['s', 'sim', 'y', 'yes']:
            copy_assets(original_path)
        else:
            manual_asset_instructions()
    else:
        print("⚠️ Projeto original não encontrado automaticamente")
        manual_asset_instructions()
    
    print_header("EXECUTANDO TESTE DE INSTALAÇÃO")
    
    import test_installation
    success = test_installation.main()
    
    if success:
        print_header("SETUP CONCLUÍDO COM SUCESSO!")
        print("\nPara jogar:")
        print("   python main.py")
        print("\nOu testar uma fase:")
        print("   python fase_netuno.py")
    else:
        print_header("⚠️ SETUP INCOMPLETO")
        print("\nVerifique os erros acima e:")
        print("1. Certifique-se que Panda3D está instalado")
        print("2. Copie os assets (imgs/ e models/)")
        print("3. Execute: python test_installation.py")
    
    return success

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\nERRO DURANTE SETUP: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)