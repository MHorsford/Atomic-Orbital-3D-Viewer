"""
atom/presets.py

Configurações pré-prontas de átomos para testes rápidos e demonstrações.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from atom.atom import Atom


# Dicionário com presets
ATOM_PRESETS = {
    'H': {'Z': 1, 'name': 'Hidrogênio'},
    'He': {'Z': 2, 'name': 'Hélio'},
    'C': {'Z': 6, 'name': 'Carbono'},
    'N': {'Z': 7, 'name': 'Nitrogênio'},
    'O': {'Z': 8, 'name': 'Oxigênio'},
    'F': {'Z': 9, 'name': 'Flúor'},
    'Ne': {'Z': 10, 'name': 'Neônio'},
    'Na': {'Z': 11, 'name': 'Sódio'},
    'Mg': {'Z': 12, 'name': 'Magnésio'},
    'S': {'Z': 16, 'name': 'Enxofre'},
    'Cl': {'Z': 17, 'name': 'Cloro'},
    'Ar': {'Z': 18, 'name': 'Argônio'},
    'Fe': {'Z': 26, 'name': 'Ferro'},
    'Cu': {'Z': 29, 'name': 'Cobre'},
    'Zn': {'Z': 30, 'name': 'Zinco'},
    'Br': {'Z': 35, 'name': 'Bromo'},
    'Ag': {'Z': 47, 'name': 'Prata'},
    'Sn': {'Z': 50, 'name': 'Estanho'},
    'Au': {'Z': 79, 'name': 'Ouro'},
    'Pb': {'Z': 82, 'name': 'Chumbo'},
    'U': {'Z': 92, 'name': 'Urânio'},
}


def load_preset(symbol: str) -> Atom:
    """
    Carrega um preset de átomo pelo símbolo.
    
    Parâmetros:
        symbol : símbolo do elemento (ex: 'H', 'C', 'O')
    
    Retorna:
        Objeto Atom já construído
    
    Levanta:
        ValueError : se o símbolo não for reconhecido
    """
    if symbol not in ATOM_PRESETS:
        available = ', '.join(sorted(ATOM_PRESETS.keys()))
        raise ValueError(
            f"Preset '{symbol}' desconhecido.\n"
            f"Disponíveis: {available}"
        )
    
    preset = ATOM_PRESETS[symbol]
    return Atom(Z=preset['Z'])


def list_presets():
    """Lista todos os presets disponíveis."""
    print("Presets de Átomos Disponíveis:")
    print("─" * 40)
    
    for symbol, info in sorted(ATOM_PRESETS.items()):
        Z = info['Z']
        name = info['name']
        print(f"  {symbol:3s} (Z={Z:2d}) — {name}")
    
    print("─" * 40)
    print(f"Total: {len(ATOM_PRESETS)} presets")


def get_preset_by_z(Z: int):
    """
    Encontra o preset mais próximo a um número atômico.
    
    Parâmetros:
        Z : número atômico
    
    Retorna:
        Símbolo do elemento mais próximo ou None
    """
    for symbol, info in ATOM_PRESETS.items():
        if info['Z'] == Z:
            return symbol
    
    return None


# Exemplos de uso
if __name__ == "__main__":
    print("=" * 60)
    print("PRESETS DE ÁTOMOS")
    print("=" * 60)
    
    list_presets()
    
    print("\n" + "=" * 60)
    print("EXEMPLOS DE CARREGAMENTO")
    print("=" * 60)
    
    # Carregar alguns presets
    for symbol in ['H', 'C', 'O', 'Fe']:
        atom = load_preset(symbol)
        print(f"\n{symbol}: {atom}")