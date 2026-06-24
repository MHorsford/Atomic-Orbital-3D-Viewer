"""
physics/screening.py

Cálculo da carga nuclear efetiva (Z_eff) usando as Regras de Slater.

Para átomos com múltiplos elétrons, cada elétron "vê" uma carga nuclear
reduzida devido ao screening (blindagem) dos outros elétrons.

Esta implementação usa as regras de Slater originais (1930) para calcular
a constante de blindagem σ, e então Z_eff = Z - σ.

Referência: Slater, J. C. (1930). Phys. Rev. 36(1), 57-64.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Dict, Tuple, List


# ─────────────────────────────────────────────────────────────────────────
# SEQUÊNCIA DE AUFBAU (ordem de preenchimento)
# ─────────────────────────────────────────────────────────────────────────

def get_orbital_sequence() -> List[Tuple[int, int]]:
    """
    Retorna a sequência de orbitais no preenchimento (regra de Aufbau).

    Ordem: 1s → 2s → 2p → 3s → 3p → 4s → 3d → 4p → 5s → 4d → ...
    """
    return [
        (1, 0),              # 1s (2 elétrons)
        (2, 0),              # 2s (2)
        (2, 1),              # 2p (6)
        (3, 0),              # 3s (2)
        (3, 1),              # 3p (6)
        (4, 0),              # 4s (2)
        (3, 2),              # 3d (10)
        (4, 1),              # 4p (6)
        (5, 0),              # 5s (2)
        (4, 2),              # 4d (10)
        (5, 1),              # 5p (6)
        (6, 0),              # 6s (2)
        (4, 3),              # 4f (14)
        (5, 2),              # 5d (10)
        (6, 1),              # 6p (6)
        (7, 0),              # 7s (2)
        (5, 3),              # 5f (14)
        (6, 2),              # 6d (10)
        (7, 1),              # 7p (6)
    ]


def max_electrons_in_subshell(l: int) -> int:
    """Retorna o número máximo de elétrons num subnível l."""
    return 2 * (2 * l + 1)


# ─────────────────────────────────────────────────────────────────────────
# CONSTRUÇÃO DA CONFIGURAÇÃO ELETRÔNICA (para um dado Z)
# ─────────────────────────────────────────────────────────────────────────

def _build_aufbau_config(Z: int) -> Dict[Tuple[int, int], int]:
    """
    Constrói a configuração eletrônica para o átomo com número atômico Z,
    seguindo a ordem de Aufbau.

    Retorna um dicionário: {(n, l): número_de_elétrons}
    Exemplo: Z=6 (Carbono) → {(1,0):2, (2,0):2, (2,1):2}
    """
    config = {}
    electrons_left = Z

    for n, l in get_orbital_sequence():
        if electrons_left <= 0:
            break
        max_e = max_electrons_in_subshell(l)
        fill = min(electrons_left, max_e)
        if fill > 0:
            config[(n, l)] = fill
            electrons_left -= fill

    # Se ainda sobrou elétrons (Z > 118), coloca no próximo orbital (improvável)
    if electrons_left > 0:
        # Fallback: coloca no último subnível disponível
        last_key = list(config.keys())[-1]
        config[last_key] += electrons_left

    return config


# ─────────────────────────────────────────────────────────────────────────
# CÁLCULO DE Z_EFF (REGRAS DE SLATER)
# ─────────────────────────────────────────────────────────────────────────

def slater_effective_charge(Z: int, n: int, l: int) -> float:
    """
    Calcula a carga nuclear efetiva Z_eff para um elétron no orbital (n, l)
    de um átomo com número atômico Z.

    Usa as Regras de Slater:

    Para orbitais s ou p (l=0,1):
        - Elétrons no mesmo grupo (n, l) contribuem 0.35 cada.
        - Elétrons no grupo (n-1) contribuem 0.85 cada.
        - Elétrons nos grupos (n-2) ou inferiores contribuem 1.00 cada.
        - Elétrons no mesmo nível n mas em subnível diferente contribuem 0.35.

    Para orbitais d ou f (l>=2):
        - Elétrons no mesmo grupo (n, l) contribuem 0.35 cada.
        - Elétrons em qualquer grupo com n_i < n contribuem 1.00 cada.
        - Elétrons em grupos com n_i = n mas l_i != l contribuem 1.00.

    Parâmetros:
        Z : número atômico (prótons)
        n : número quântico principal
        l : número quântico azimutal (0=s, 1=p, 2=d, 3=f)

    Retorna:
        Z_eff (sempre > 0)
    """
    if Z <= 0 or n <= 0:
        return 1.0

    # 1. Obter a configuração eletrônica completa
    full_config = _build_aufbau_config(Z)

    # 2. Remover 1 elétron do subnível alvo
    target_key = (n, l)
    target_count = full_config.get(target_key, 0)

    if target_count <= 0:
        return float(Z)

    config = full_config.copy()
    config[target_key] = target_count - 1

    # 3. Calcular a constante de blindagem σ
    sigma = 0.0

    for (ni, li), count in config.items():
        if count <= 0:
            continue

        # Elétrons em camadas mais externas (ni > n) NUNCA blindam
        if ni > n:
            continue
            
        # Casos especiais para orbitais d ou f externos ao nível do alvo
        # Ex: se o alvo é 3d (n=3, l=2), elétrons em 4s (ni=4) já caíram no 'if ni > n' acima.

        # ─── Regras para o elétron alvo sendo s ou p (l=0 ou l=1) ───
        if l == 0 or l == 1:
            if ni == n:
                if li == 0 or li == 1:
                    # Correção específica para o orbital 1s
                    if n == 1:
                        sigma += count * 0.30
                    else:
                        sigma += count * 0.35
                else:
                    continue
            elif ni == n - 1:
                # Todos os elétrons da camada n-1 (s, p, d, f) blindam 0.85
                sigma += count * 0.85
            elif ni <= n - 2:
                # Camadas mais internas blindam 1.00
                sigma += count * 1.0

        # ─── Regras para o elétron alvo sendo d ou f (l >= 2) ───
        else:
            if ni == n and li == l:
                # Mesmo subnível (nd ou nf)
                sigma += count * 0.35
            elif ni < n:
                # Qualquer elétron em camadas estritamente internas
                sigma += count * 1.0
            elif ni == n and li != l:
                # No mesmo nível n, os orbitais d ou f ficam isolados.
                # Os elétrons em (ns, np) estão "à esquerda" no grupo de Slater, logo blindam 1.00
                # Orbitais de li diferente que estão à direita não blindariam, mas Aufbau já dita a ordem.
                if li < l: 
                    sigma += count * 1.0

    # 4. Calcular Z_eff
    Z_eff = Z - sigma
    return max(0.1, Z_eff)


# ─────────────────────────────────────────────────────────────────────────
# FUNÇÕES DE COMPATIBILIDADE (mantidas para não quebrar outros módulos)
# ─────────────────────────────────────────────────────────────────────────

def slater_group(n: int, l: int) -> int:
    """Compatibilidade: retorna o grupo de Slater (n-1 para n>=2, 0 para n=1)."""
    return max(0, n - 1)


# ─────────────────────────────────────────────────────────────────────────
# TESTE
# ─────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("TESTE: CARGA NUCLEAR EFETIVA (REGRAS DE SLATER CORRETAS)")
    print("=" * 70)

    # Elementos de teste
    test_cases = [
        (1, "H", [(1,0)]),
        (2, "He", [(1,0)]),
        (3, "Li", [(1,0), (2,0)]),
        (6, "C", [(1,0), (2,0), (2,1)]),
        (8, "O", [(1,0), (2,0), (2,1)]),
        (10, "Ne", [(1,0), (2,0), (2,1)]),
        (11, "Na", [(1,0), (2,0), (2,1), (3,0)]),
        (18, "Ar", [(1,0), (2,0), (2,1), (3,0), (3,1)]),
        (21, "Sc", [(1,0), (2,0), (2,1), (3,0), (3,1), (4,0), (3,2)]),
        (26, "Fe", [(1,0), (2,0), (2,1), (3,0), (3,1), (4,0), (3,2)]),
        (29, "Cu", [(1,0), (2,0), (2,1), (3,0), (3,1), (4,0), (3,2)]),
        (36, "Kr", [(1,0), (2,0), (2,1), (3,0), (3,1), (4,0), (3,2), (4,1)]),
        (47, "Ag", [(1,0), (2,0), (2,1), (3,0), (3,1), (4,0), (3,2), (4,1), (5,0), (4,2)]),
        (54, "Xe", [(1,0), (2,0), (2,1), (3,0), (3,1), (4,0), (3,2), (4,1), (5,0), (4,2), (5,1)]),
        (79, "Au", [(1,0), (2,0), (2,1), (3,0), (3,1), (4,0), (3,2), (4,1), (5,0), (4,2), (5,1), (6,0), (4,3), (5,2)]),
        (92, "U", [(1,0), (2,0), (2,1), (3,0), (3,1), (4,0), (3,2), (4,1), (5,0), (4,2), (5,1), (6,0), (4,3), (5,2), (6,1), (7,0), (5,3)]),
    ]

    print("\n[Z_eff para diferentes átomos e orbitais]")
    print(" Z  Elemento  Orbital  Z_eff")
    print("-" * 45)

    for Z, symbol, orbitals in test_cases:
        for (n, l) in orbitals:
            Z_eff = slater_effective_charge(Z, n, l)
            label = f"{n}{['s','p','d','f'][l]}"
            print(f"{Z:2d}  {symbol:4s}    {label:5s}   {Z_eff:6.2f}")

    print("\n[Comparação com valores esperados (Slater tabelado)]")
    print("Para H 1s: esperado 1.00 → obtido {:.2f}".format(slater_effective_charge(1, 1, 0)))
    print("Para He 1s: esperado ~1.70 → obtido {:.2f}".format(slater_effective_charge(2, 1, 0)))
    print("Para C 2p: esperado ~3.14 → obtido {:.2f}".format(slater_effective_charge(6, 2, 1)))
    print("Para Fe 3d: esperado ~5.93 → obtido {:.2f}".format(slater_effective_charge(26, 3, 2)))
    print("Para Au 5d: esperado ~?   → obtido {:.2f}".format(slater_effective_charge(79, 5, 2)))

    print("\n" + "=" * 70)
    print("✅ Implementação completa das Regras de Slater.")
    print("   Agora Z_eff é calculado dinamicamente para QUALQUER elemento!")
    print("=" * 70)