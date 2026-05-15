#!/usr/bin/env python3
"""
JORNADA SOLAR - BUILD SCRIPT
Empacota o jogo como executável standalone usando PyInstaller.
Funciona em Windows, Linux e macOS.
"""

import os
import sys
import shutil
import subprocess
import platform

SYSTEM = platform.system()

def print_header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60 + "\n")

def check_dependencies():
    """Verifica se PyInstaller está instalado"""
    try:
        import PyInstaller
        print(f"PyInstaller {PyInstaller.__version__} encontrado")
        return True
    except ImportError:
        print("PyInstaller não encontrado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        return True

def build():
    print_header("JORNADA SOLAR - BUILD")

    check_dependencies()

    output_dir = os.path.join(os.path.dirname(__file__), "dist")
    build_dir = os.path.join(os.path.dirname(__file__), "build_temp")

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    name = "JornadaSolar"
    icon = None

    # Localiza DLLs do panda3d para incluir no build
    panda3d_dlls_pattern = None
    try:
        import panda3d
        p3d_dir = os.path.dirname(panda3d.__file__)
        panda3d_dlls_pattern = os.path.join(p3d_dir, "*.dll")
        print(f"DLLs do panda3d encontradas em: {p3d_dir}")
    except Exception as e:
        print(f"Aviso: não foi possível localizar DLLs do panda3d: {e}")

    pyinstaller_args = [
        sys.executable, "-m", "PyInstaller",
        "--name", name,
        "--noconfirm",
        "--clean",
        "--onefile",
        "--add-data", f"imgs{os.pathsep}imgs",
        "--add-data", f"models{os.pathsep}models",
        "--add-data", f"music{os.pathsep}music",
        "--add-data", f"sounds{os.pathsep}sounds",
        "--add-data", f"config.json{os.pathsep}.",
        "--add-data", f"core{os.pathsep}core",
        "--add-data", f"entities{os.pathsep}entities",
        "--add-data", f"levels{os.pathsep}levels",
        "--add-data", f"screens{os.pathsep}screens",
        *(["--add-binary", f"{panda3d_dlls_pattern}{os.pathsep}panda3d"] if panda3d_dlls_pattern else []),
        "--hidden-import", "direct.showbase.ShowBase",
        "--hidden-import", "panda3d.core",
        "--hidden-import", "direct.gui.DirectGui",
        "--hidden-import", "direct.gui.OnscreenText",
        "--hidden-import", "direct.actor.Actor",
        "--hidden-import", "direct.interval.IntervalGlobal",
        "--collect-all", "direct",
        "--collect-all", "panda3d",
        "main.py",
    ]

    if SYSTEM == "Darwin":
        icon_path = os.path.join(os.path.dirname(__file__), "imgs", "icon.icns")
        if os.path.exists(icon_path):
            pyinstaller_args.extend(["--icon", icon_path])
        pyinstaller_args.extend([
            "--osx-bundle-identifier", "com.jornadasolar.app",
        ])
    elif SYSTEM == "Windows":
        icon_path = os.path.join(os.path.dirname(__file__), "imgs", "icon.ico")
        if os.path.exists(icon_path):
            pyinstaller_args.extend(["--icon", icon_path])
        pyinstaller_args.extend([
            "--console",
        ])
    else:
        pyinstaller_args.extend([
            "--console",
        ])

    print(f"Executando PyInstaller para {SYSTEM}...")
    subprocess.check_call(pyinstaller_args, cwd=os.path.dirname(__file__))

    print("\n" + "=" * 60)
    print("BUILD CONCLUÍDO!")
    print("=" * 60)
    
    executable_name = name
    if SYSTEM == "Windows":
        executable_name = f"{name}.exe"
    
    exe_path = os.path.join(output_dir, name, executable_name)
    if os.path.exists(exe_path):
        print(f"\nExecutável gerado: {exe_path}")
    
    dist_folder = os.path.join(output_dir, name)
    print(f"\nPasta do executável: {dist_folder}")
    print(f"\nTamanho total: {get_folder_size(dist_folder) / 1024 / 1024:.1f} MB")

def get_folder_size(folder):
    total = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total += os.path.getsize(fp)
    return total

if __name__ == "__main__":
    try:
        build()
    except KeyboardInterrupt:
        print("\nBuild cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\nERRO durante build: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
