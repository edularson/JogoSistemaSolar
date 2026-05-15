from core.base_level import BaseLevel

class FaseSaturno(BaseLevel):
    """Fase 3: Saturno - Chuva de Detritos"""
    def __init__(self, manager):
        super().__init__(manager, "saturno")

if __name__ == "__main__":
    import sys
    import os
    # Adiciona diretório raiz ao path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from core.run_level import run_level
    run_level("saturno")
