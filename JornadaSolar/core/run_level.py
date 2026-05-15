"""
JORNADA SOLAR - LEVEL RUNNER
Launcher universal que pode rodar qualquer fase
Chamado pelos arquivos fase_*.py individuais
"""

import sys
import os


def run_level(level_name: str):
    """
    Executa uma fase específica
    
    Args:
        level_name: Nome da fase (netuno, urano, saturno, etc)
    """
    from levels.specific_levels import create_level
    
    print(f"\n{'='*60}")
    print(f"INICIANDO FASE: {level_name.upper()}")
    print(f"{'='*60}\n")
    
    try:
        # Cria e roda a fase
        level = create_level(level_name)
        level.run()
    except Exception as e:
        print(f"\nERRO FATAL na fase {level_name}:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        
        # Volta pro lobby em caso de erro
        with open("transicao.txt", "w") as f:
            f.write("lobby")
        
        sys.exit(1)


if __name__ == "__main__":
    # Se chamado diretamente, espera nome da fase como argumento
    if len(sys.argv) > 1:
        level_name = sys.argv[1]
    else:
        level_name = "netuno"  # Default
    
    run_level(level_name)