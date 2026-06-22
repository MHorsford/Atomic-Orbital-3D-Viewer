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
from orbitals.orbital_types import get_orbital_type, max_electrons_in_subshell
from physics.screening import (
    slater_effective_charge,
    get_orbital_sequence,
    max_electrons_in_subshell as max_e_in_subshell,
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
        Cria todos os orbitais necessários para um átomo com Z elétrons.
        Preenche-os seguindo a regra de Aufbau com as restrições de Hund e Pauli.

        Algoritmo:
            1. Gera a sequência de (n, l) em ordem de energia (Aufbau)
            2. Para cada orbital, calcula Z_eff (Slater)
            3. Preenche com até 2 elétrons (Pauli)
            4. Obedece a regra de Hund (maximiza spin)
        """
        self.orbitals = []
        electrons_to_place = Z

        # Sequência de Aufbau
        orbital_sequence = get_orbital_sequence()

        for n, l in orbital_sequence:
            if electrons_to_place <= 0:
                break

            # Para cada m_l possível (degenerescência = 2l+1)
            # m_l varia de -l até +l
            for m_l in range(-l, l + 1):
                if electrons_to_place <= 0:
                    break

                # Calcula Z_eff para este orbital
                Z_eff = slater_effective_charge(Z, n, l)

                # Cria o orbital
                orbital = Orbital(n=n, l=l, m=m_l, electrons=0, Z_eff=Z_eff)

                # Preenche de acordo com Hund e Pauli
                # Regra de Hund: coloca 1 elétron primeiro (spin up)
                if electrons_to_place >= 1:
                    orbital.add_electron()
                    electrons_to_place -= 1

                # Depois coloca o segundo elétron (spin down) se houver
                if electrons_to_place >= 1 and orbital.electrons < 2:
                    orbital.add_electron()
                    electrons_to_place -= 1

                self.orbitals.append(orbital)

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
        from orbitals.orbital_types import get_orbital_type

        config_dict: Dict[Tuple[int, int], int] = {}

        # Agrupa elétrons por (n, l)
        for orbital in self.orbitals:
            if orbital.electrons > 0:
                key = (orbital.n, orbital.l)
                if key not in config_dict:
                    config_dict[key] = 0
                config_dict[key] += orbital.electrons

        # Converte para string
        config_str = ""
        for (n, l), electron_count in sorted(config_dict.items()):
            l_letter = get_orbital_type(l).letter
            superscript_num = str(electron_count)  # em texto puro
            config_str += f"{n}{l_letter}{superscript_num} "

        return config_str.strip()

    def get_valence_electrons(self) -> int:
        """
        Retorna o número de elétrons de valência (mais simples possível).

        Para elementos do bloco s/p: é o número de elétrons no nível mais externo.
        Para metais de transição: depende, mas usamos a heurística simples.
        """
        if not self.orbitals:
            return 0

        # Nível mais externo (maior n)
        max_n = max(orb.n for orb in self.orbitals if orb.electrons > 0)

        # Conta elétrons no nível max_n
        valence = sum(orb.electrons for orb in self.orbitals if orb.n == max_n)
        return valence

    def get_orbital_filling_order(self) -> str:
        """
        Retorna uma representação visual de como os orbitais foram preenchidos.
        Útil para debug.

        Exemplo:
            1s²↓↑ 2s²↓↑ 2p²↓ 3s¹↓
        """
        config = ""
        for orbital in self.orbitals:
            if orbital.electrons == 0:
                continue
            label = f"{orbital.n}{orbital.name.split()[0][-1]}"
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
                f"  [{i:2d}] {orb.name:4s} (m={orb.m:+d}) — "
                f"{orb.electrons}/{2} e⁻ | Z_eff={orb.Z_eff:.2f}"
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
    print(f"  Símbolo: {H.get_element_symbol()}")
    print(f"  Nome: {H.get_element_name()}")
    print(f"  Config eletrônica: {H.get_electron_config()}")
    print(f"  Elétrons de valência: {H.get_valence_electrons()}")
    print(f"  Neutro? {H.is_neutral}")

    # Teste 2: Hélio
    print("\n[TESTE 2: Hélio (Z=2)]")
    He = Atom(Z=2)
    print(f"  {He}")
    print(f"  Config: {He.get_electron_config()}")
    print(f"  Valência: {He.get_valence_electrons()}")

    # Teste 3: Carbono
    print("\n[TESTE 3: Carbono (Z=6)]")
    C = Atom(Z=6)
    print(f"  {C}")
    print(f"  Config: {C.get_electron_config()}")
    print(f"  Valência: {C.get_valence_electrons()}")
    print(f"  Preenchimento visual: {C.get_orbital_filling_order()}")

    # Teste 4: Oxigênio
    print("\n[TESTE 4: Oxigênio (Z=8)]")
    O = Atom(Z=8)
    print(f"  {O}")
    print(f"  Config: {O.get_electron_config()}")
    print(f"  Valência: {O.get_valence_electrons()}")

    # Teste 5: Neônio (shell completa)
    print("\n[TESTE 5: Neônio (Z=10) — shell completa]")
    Ne = Atom(Z=10)
    print(f"  {Ne}")
    print(f"  Config: {Ne.get_electron_config()}")
    print(f"  Valência: {Ne.get_valence_electrons()}")

    # Teste 6: Ferro (transição)
    print("\n[TESTE 6: Ferro (Z=26) — metal de transição]")
    Fe = Atom(Z=26)
    print(f"  {Fe}")
    print(f"  Config: {Fe.get_electron_config()}")
    print(f"  Valência: {Fe.get_valence_electrons()}")
    print(f"  Total de orbitais: {len(Fe.orbitals)}")

    # Teste 7: Lista de orbitais para He (pequeno e legível)
    print("\n[TESTE 7: Lista de orbitais do Hélio]")
    print(He.list_orbitals())

    # Teste 8: Buscar orbital específico
    print("\n[TESTE 8: Buscar orbital (n=2, l=1, m=0) do Carbono]")
    orb = C.get_orbital_by_quantum_numbers(2, 1, 0)
    if orb:
        print(f"  Encontrado: {orb.name} com {orb.electrons} elétrons")
    else:
        print(f"  Não encontrado")

    print("\n" + "=" * 80)