"""
orbitals/orbital_types.py

Configurações e metadados dos tipos de orbitais (s, p, d, f).
Este arquivo serve como referência central para características 
comuns de cada tipo de orbital.
"""

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class OrbitalType:
    """Representa as características de um tipo de orbital (s, p, d, f)"""
    letter: str
    max_electrons: int
    degeneracy: int          # quantidade de orbitais 
    default_color: Tuple[float, float, float]
    description: str


# Configuração central dos tipos de orbitais
ORBITAL_TYPES: Dict[int, OrbitalType] = {
    0: OrbitalType(  # s
        letter="s",
        max_electrons=2,
        degeneracy=1,
        default_color=(0.2, 0.8, 1.0),      # Azul claro
        description="Esférico, simétrico em todas as direções"
    ),
    1: OrbitalType(  # p
        letter="p",
        max_electrons=6,
        degeneracy=3,
        default_color=(1.0, 0.55, 0.0),     # Laranja
        description="Formato de haltere (dumbbell) em 3 orientações"
    ),
    2: OrbitalType(  # d
        letter="d",
        max_electrons=10,
        degeneracy=5,
        default_color=(0.8, 0.2, 1.0),      # Roxo
        description="Formas complexas com 4 ou 5 lobos"
    ),
    3: OrbitalType(  # f
        letter="f",
        max_electrons=14,
        degeneracy=7,
        default_color=(0.2, 1.0, 0.4),      # Verde
        description="Orbitais muito complexos com múltiplos lobos"
    )
}


def get_orbital_type(l: int) -> OrbitalType:
    """Retorna as informações do tipo de orbital baseado no número quântico l"""
    return ORBITAL_TYPES.get(l, ORBITAL_TYPES[0])


def get_orbital_name(n: int, l: int) -> str:
    """Retorna o nome padrão do orbital (ex: 1s, 2p, 3d)"""
    letter = get_orbital_type(l).letter
    return f"{n}{letter}"


def get_max_electrons(l: int) -> int:
    """Retorna a capacidade máxima de elétrons para o subnível"""
    return get_orbital_type(l).max_electrons


def get_default_color(l: int) -> Tuple[float, float, float]:
    """Retorna a cor padrão do tipo de orbital"""
    return get_orbital_type(l).default_color


def list_all_orbital_types() -> None:
    """Imprime todos os tipos de orbitais (útil para debug)"""
    print("Tipos de Orbitais Disponíveis:")
    for l, ot in ORBITAL_TYPES.items():
        print(f"  l={l} ({ot.letter}) → {ot.max_electrons} elétrons, {ot.degeneracy} orientações")