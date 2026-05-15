from core.base_level import BaseLevel

class FaseUrano(BaseLevel):
    """Fase 2: Urano - Ventos Laterais"""
    def __init__(self, manager):
        super().__init__(manager, "urano")

if __name__ == "__main__":
    import sys
    import os
    # Adiciona diretório raiz ao path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from core.run_level import run_level
    run_level("urano")
