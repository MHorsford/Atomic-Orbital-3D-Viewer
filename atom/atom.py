"""
atom/atom.py

Classe Atom — representa um átomo completo.
Combina núcleo (Nucleus) com orbitais eletrônicos (lista de Orbital).
Aplica as regras de preenchimento: Aufbau, Hund e Princípio de Pauli.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import List, Dict, Tuple
import numpy as np

from nucleus.nucleus import Nucleus
from orbitals.orbital import Orbital
from orbitals.orbital_types import get_orbital_type
from physics.screening import (
    slater_effective_charge,
    get_orbital_sequence,
)


class Atom:
    """
    Representa um átomo completo com núcleo e nuvem eletrônica.

    Atributos:
        nucleus       : objeto Nucleus (prótons + nêutrons)
        orbitals      : lista de objetos Orbital preenchidos
        Z             : número atômico (prótons)
        N             : número de elétrons (igual a Z para átomo neutro)
        position      : posição do átomo no espaço
    """

    def __init__(self, Z: int = 1):
        """
        Cria um átomo com número atômico Z.

        Parâmetros:
            Z : número atômico (número de prótons)
        """
        self.nucleus = Nucleus(Z=Z, N=0)  # Por enquanto, isótopo natural (padrão)
        self.orbitals: List[Orbital] = []
        self.position = np.array([0.0, 0.0, 0.0])

        # Constrói e preenche os orbitais
        self._build_orbitals(Z)

    def _build_orbitals(self, Z: int) -> None:
        """
        Cria e preenche orbitais subnível por subnível.
        
        Algoritmo:
            Para cada subnível (n, l) na ordem de Aufbau:
                1. Cria todos os orbitais do subnível (m_l = -l até +l)
                2. Preenche até capacidade (máx 2 elétrons por orbital)
                3. Aplica Hund (1 por orbital antes do 2º)
                4. Aplica Pauli (máx 2 por orbital)
        """
        self.orbitals = []
        electrons_to_place = Z
        
        # Sequência de Aufbau
        orbital_sequence = get_orbital_sequence()
        
        for n, l in orbital_sequence:
            if electrons_to_place <= 0:
                break
            
            # Calcula Z_eff uma vez para todo o subnível
            Z_eff = slater_effective_charge(Z, n, l)
            
            # Cria todos os orbitais deste subnível
            subshell_orbitals = []
            for m_l in range(-l, l + 1):
                orbital = Orbital(n=n, l=l, m=m_l, electrons=0, Z_eff=Z_eff)
                subshell_orbitals.append(orbital)
                self.orbitals.append(orbital)
            
            # Preenche o subnível: Hund (1 elétron em cada) depois Pauli (2º elétron)
            # PASSO A: Hund — 1 elétron em cada orbital (spin up)
            for orbital in subshell_orbitals:
                if electrons_to_place <= 0:
                    break
                orbital.add_electron()
                electrons_to_place -= 1
            
            # PASSO B: Pauli — segundo elétron em cada orbital (spin down)
            for orbital in subshell_orbitals:
                if electrons_to_place <= 0:
                    break
                if orbital.electrons == 1:
                    orbital.add_electron()
                    electrons_to_place -= 1

    @property
    def Z(self) -> int:
        """Número atômico (número de prótons)"""
        return self.nucleus.Z

    @property
    def N_electrons(self) -> int:
        """Número total de elétrons"""
        return sum(orb.electrons for orb in self.orbitals)

    @property
    def is_neutral(self) -> bool:
        """Retorna True se o átomo é neutro (N_elétrons == Z)"""
        return self.N_electrons == self.Z

    def get_element_symbol(self) -> str:
        """Retorna o símbolo do elemento (ex: 'H', 'C')"""
        return self.nucleus.get_element_symbol()

    def get_element_name(self) -> str:
        """Retorna o nome do elemento (ex: 'Hydrogen')"""
        return self.nucleus.get_element_name()

    def get_electron_config(self) -> str:
        """
        Retorna a configuração eletrônica atual baseada nos orbitais preenchidos.

        Exemplo: "1s¹ 2s² 2p² 3s¹"
        """
        config_dict: Dict[Tuple[int, int], int] = {}

        # Agrupa elétrons por (n, l)
        for orbital in self.orbitals:
            if orbital.electrons > 0:
                key = (orbital.n, orbital.l)
                if key not in config_dict:
                    config_dict[key] = 0
                config_dict[key] += orbital.electrons

        # Converte para string (mantém ordem de Aufbau)
        config_str = ""
        for (n, l), electron_count in sorted(config_dict.items()):
            l_letter = get_orbital_type(l).letter
            superscript_num = str(electron_count)
            config_str += f"{n}{l_letter}{superscript_num} "

        return config_str.strip()

    def get_valence_electrons(self) -> int:
        """
        Retorna o número de elétrons de valência (mais simples possível).

        Para elementos do bloco s/p: é o número de elétrons no nível mais externo.
        """
        if not self.orbitals:
            return 0

        # Nível mais externo (maior n com elétrons)
        max_n = max(orb.n for orb in self.orbitals if orb.electrons > 0)

        # Conta elétrons no nível max_n
        valence = sum(orb.electrons for orb in self.orbitals if orb.n == max_n)
        return valence

    def get_orbital_filling_order(self) -> str:
        """
        Retorna uma representação visual de como os orbitais foram preenchidos.

        Exemplo:
            1s²↓↑ 2s²↓↑ 2p²↓ 3s¹↓
        """
        config = ""
        for orbital in self.orbitals:
            if orbital.electrons == 0:
                continue
            label = f"{orbital.n}{get_orbital_type(orbital.l).letter}"
            if orbital.electrons == 1:
                config += f"{label}¹↓ "
            else:  # 2 elétrons
                config += f"{label}²↓↑ "
        return config.strip()

    def get_orbital_by_quantum_numbers(self, n: int, l: int, m: int) -> Orbital:
        """
        Procura um orbital específico pelos números quânticos (n, l, m).

        Retorna None se não encontrar.
        """
        for orbital in self.orbitals:
            if orbital.n == n and orbital.l == l and orbital.m == m:
                return orbital
        return None

    def list_orbitals(self) -> str:
        """Retorna uma lista legível de todos os orbitais e seus preenchimentos"""
        lines = []
        for i, orb in enumerate(self.orbitals):
            lines.append(
                f"  [{i:2d}] {orb.n}{get_orbital_type(orb.l).letter:1s}(m={orb.m:+d}) — "
                f"{orb.electrons}/2 e⁻ | Z_eff={orb.Z_eff:.2f}"
            )
        return "\n".join(lines)

    def __str__(self) -> str:
        symbol = self.get_element_symbol()
        config = self.get_electron_config()
        return (
            f"{symbol} (Z={self.Z}) | "
            f"Elétrons: {self.N_electrons} | "
            f"Config: {config}"
        )

    def __repr__(self) -> str:
        return self.__str__()


# ─────────────────────────────────────────────────────────────────────────
# TESTE E DEMONSTRAÇÃO
# ─────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 80)
    print("TESTE: CLASSE ATOM")
    print("=" * 80)

    # Teste 1: Hidrogênio
    print("\n[TESTE 1: Hidrogênio (Z=1)]")
    H = Atom(Z=1)
    print(f"  {H}")
    print(f"  Config: {H.get_electron_config()}")

    # Teste 2: Hélio
    print("\n[TESTE 2: Hélio (Z=2)]")
    He = Atom(Z=2)
    print(f"  {He}")
    print(f"  Config: {He.get_electron_config()}")

    # Teste 3: Carbono
    print("\n[TESTE 3: Carbono (Z=6)]")
    C = Atom(Z=6)
    print(f"  {C}")
    print(f"  Config: {C.get_electron_config()}")

    # Teste 4: Oxigênio
    print("\n[TESTE 4: Oxigênio (Z=8)]")
    O = Atom(Z=8)
    print(f"  {O}")
    print(f"  Config: {O.get_electron_config()}")

    # Teste 5: Neônio
    print("\n[TESTE 5: Neônio (Z=10)]")
    Ne = Atom(Z=10)
    print(f"  {Ne}")
    print(f"  Config: {Ne.get_electron_config()}")

    # Teste 6: Ferro
    print("\n[TESTE 6: Ferro (Z=26)]")
    Fe = Atom(Z=26)
    print(f"  {Fe}")
    print(f"  Config: {Fe.get_electron_config()}")

    print("\n" + "=" * 80)