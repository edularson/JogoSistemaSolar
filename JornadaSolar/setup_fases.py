import os

# Conteúdo base para todas as fases
TEMPLATE = """from core.base_level import BaseLevel

class {class_name}(BaseLevel):
    \"\"\"Fase {number}: {name} - {desc}\"\"\"
    def __init__(self, manager):
        super().__init__(manager, "{slug}")

if __name__ == "__main__":
    import sys
    import os
    # Adiciona diretório raiz ao path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from core.run_level import run_level
    run_level("{slug}")
"""

# Configuração de cada fase
fases = [
    {"slug": "netuno",   "class": "FaseNetuno",   "name": "Netuno",   "desc": "Introdutória"},
    {"slug": "urano",    "class": "FaseUrano",    "name": "Urano",    "desc": "Ventos Laterais"},
    {"slug": "saturno",  "class": "FaseSaturno",  "name": "Saturno",  "desc": "Chuva de Detritos"},
    {"slug": "jupiter",  "class": "FaseJupiter",  "name": "Júpiter",  "desc": "Tempestade Elétrica"},
    {"slug": "marte",    "class": "FaseMarte",    "name": "Marte",    "desc": "Coleta Seletiva"},
    {"slug": "terra",    "class": "FaseTerra",    "name": "Terra",    "desc": "Defesa Orbital"},
    {"slug": "venus",    "class": "FaseVenus",    "name": "Vênus",    "desc": "Chuva Ácida"},
    {"slug": "mercurio", "class": "FaseMercurio", "name": "Mercúrio", "desc": "Inferno de Velocidade"},
    {"slug": "sol",      "class": "FaseSol",      "name": "Sol",      "desc": "Boss Final"},
]

def criar_fases():
    # Garante que a pasta levels existe
    if not os.path.exists("levels"):
        os.makedirs("levels")
        print("📁 Pasta 'levels' criada.")

    print("Gerando arquivos de fase...")
    
    for i, fase in enumerate(fases, 1):
        filename = f"levels/fase_{fase['slug']}.py"
        
        # Formata o conteúdo
        content = TEMPLATE.format(
            class_name=fase["class"],
            number=i,
            name=fase["name"],
            desc=fase["desc"],
            slug=fase["slug"]
        )
        
        # Escreve o arquivo
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"Criado: {filename}")

    print("\nTudo pronto! Agora rode o test_installation.py novamente.")

if __name__ == "__main__":
    criar_fases()