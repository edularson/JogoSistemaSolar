from core.base_level import BaseLevel

class FaseTerra(BaseLevel):
    """Fase 6: Terra - Defesa Orbital"""
    def __init__(self, manager):
        super().__init__(manager, "terra")

if __name__ == "__main__":
    import sys
    import os
    # Adiciona diretório raiz ao path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from core.run_level import run_level
    run_level("terra")
