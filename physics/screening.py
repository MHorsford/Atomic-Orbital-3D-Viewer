"""
physics/screening.py

Cálculo de carga nuclear efetiva (Z_eff) usando as Regras de Slater.

Para átomos com múltiplos elétrons, cada elétron "vê" uma carga nuclear
reduzida devido ao screening (blindagem) dos outros elétrons.

Referência: Slater, J. C. (1930). Phys. Rev. 36(1), 57-64.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Dict, Tuple


# ─────────────────────────────────────────────────────────────────────────
# CLASSIFICAÇÃO DE ORBITAIS (Slater)
# ─────────────────────────────────────────────────────────────────────────

def slater_group(n: int, l: int) -> int:
    """
    Retorna o "grupo" de Slater para um orbital (n, l).

    Os grupos determinam quanto screening cada orbital sofre.
    Referência rápida:
        - 1s → grupo 0
        - 2s, 2p → grupo 1
        - 3s, 3p → grupo 2
        - 3d → grupo 2 (mesmo que 3s/3p, penetram menos)
        - 4s, 4p → grupo 3
        - 4d, 4f → grupo 3 (penetram menos)

    Parâmetros:
        n : número quântico principal
        l : número quântico de momento angular (0=s, 1=p, 2=d, 3=f)

    Retorna:
        Grupo de Slater (0, 1, 2, 3, ...)
    """
    if n == 1:
        return 0
    elif n == 2:
        return 1
    elif n == 3:
        return 2
    elif n == 4:
        return 3
    else:  # n >= 5
        return n - 1


# ─────────────────────────────────────────────────────────────────────────
# REGRAS DE SLATER ORIGINAIS
# ─────────────────────────────────────────────────────────────────────────

def slater_screening_constant(n: int, l: int, total_electrons: int = None) -> float:
    """
    Calcula a constante de screening σ (Slater) para um elétron em (n, l).

    Regras de Slater:
        1. Elétrons no mesmo grupo (nl) que o elétron em questão contribuem 0.35 cada
           (exceto para 1s, que contribuem 0.30)
        2. Elétrons em grupos (n-1) contribuem 0.85 cada
        3. Elétrons em grupos (n-2) ou inferiores contribuem 1.00 cada
        4. Para l=0 (orbitais s/p), há regras especiais adicionais

    Parâmetros:
        n : número quântico principal
        l : número quântico de momento angular
        total_electrons : (opcional) número total de elétrons no átomo
                         não é usado neste cálculo simplificado

    Retorna:
        Constante de screening σ (adimensional)

    Nota: Esta é uma aproximação. Para cálculos mais precisos, usa-se a
    função slater_effective_charge() que é parametrizada para átomos reais.
    """
    if n == 1 and l == 0:
        # 1s: nenhum outro elétron 1s (no máximo 2)
        return 0.0  # sem screening para o primeiro 1s

    # Cálculo genérico (simplificado)
    # Sem acesso ao estado completo do átomo, assumimos:
    # - máximo screening de orbitais internos
    group_target = slater_group(n, l)

    # Contribuição dos orbitais no mesmo grupo
    sigma_same_group = 0.35  # padrão (0.30 para 1s, mas 1s já foi tratado acima)

    # Contribuição dos orbitais internos
    sigma_inner = 0.85 * 3  # aproximação: assume ~3 orbitais internos

    return sigma_same_group + sigma_inner


# ─────────────────────────────────────────────────────────────────────────
# CARGA NUCLEAR EFETIVA — TABELA PARAMETRIZADA
# ─────────────────────────────────────────────────────────────────────────

# Valores tabelados de Z_eff para orbitais específicos em átomos reais
# (Fonte: valores calculados e experimentais)
SLATER_Z_EFF: Dict[Tuple[int, int], Dict[int, float]] = {
    # (n, l): {Z: Z_eff}
    (1, 0): {  # 1s
        1:  1.00,   2:  1.68,   3:  2.68,   4:  3.68,   5:  4.68,
        6:  5.68,   7:  6.68,   8:  7.68,   9:  8.68,  10:  9.68,
        11: 10.68,  12: 11.68,  13: 12.68,  14: 13.68,  15: 14.68,
        18: 17.67,  26: 25.64,  29: 28.65,  36: 35.65,
    },
    (2, 0): {  # 2s
        3:  2.00,   4:  2.68,   5:  3.68,   6:  4.68,   7:  5.68,
        8:  6.68,   9:  7.68,  10:  8.68,  11:  3.00,  12:  4.00,
        13:  5.00,  14:  6.00,  15:  7.00,  18: 10.00,  26:  8.40,
    },
    (2, 1): {  # 2p
        5:  2.68,   6:  3.68,   7:  4.68,   8:  5.68,   9:  6.68,
        10: 7.68,  11:  4.00,  12:  5.00,  13:  6.00,  14:  7.00,
        15:  8.00,  18: 11.00,  26:  9.35,
    },
    (3, 0): {  # 3s
        11: 2.00,  12:  3.00,  13:  4.00,  14:  5.00,  15:  6.00,
        18:  9.00,  19:  2.00,  20:  3.00,
    },
    (3, 1): {  # 3p
        13: 3.00,  14:  4.00,  15:  5.00,  18:  9.50,  26: 10.30,
    },
    (3, 2): {  # 3d
        21: 1.00,  22:  2.00,  23:  3.00,  24:  4.00,  25:  5.00,
        26:  5.93,  27:  7.00,  28:  8.00,  29:  9.20,  30: 10.00,
    },
    (4, 0): {  # 4s
        19: 1.00,  20:  2.00,  29:  1.92,  36:  1.00,
    },
}


def slater_effective_charge(Z: int, n: int, l: int) -> float:
    """
    Retorna a carga nuclear efetiva Z_eff para um elétron em (n, l) de um átomo com Z prótons.

    Usa valores tabelados quando disponíveis (mais precisos).
    Fallback: estimativa via regras de Slater.

    Parâmetros:
        Z : número atômico (número de prótons)
        n : número quântico principal
        l : número quântico de momento angular

    Retorna:
        Carga nuclear efetiva Z_eff (sempre > 0)
    """
    # Tentar usar tabela
    orbital_key = (n, l)
    if orbital_key in SLATER_Z_EFF:
        if Z in SLATER_Z_EFF[orbital_key]:
            return SLATER_Z_EFF[orbital_key][Z]

    # Fallback: estimativa genérica (screening = 0.5 por elétron interno)
    # Muito simplificado, mas funciona para geometria básica
    inner_electrons = Z - 1  # todos exceto o que estamos calculando
    sigma = inner_electrons * 0.5
    Z_eff = Z - sigma
    return max(1.0, Z_eff)  # Z_eff nunca é menor que 1


# ─────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO ELETRÔNICA E PREENCHIMENTO
# ─────────────────────────────────────────────────────────────────────────

def get_orbital_sequence() -> list:
    """
    Retorna a sequência de orbitais no preenchimento (regra de Aufbau).

    Ordem: 1s → 2s → 2p → 3s → 3p → 4s → 3d → 4p → 5s → 4d → ...
    """
    return [
        (1, 0),              # 1s (2 elétrons)
        (2, 0),              # 2s (2 elétrons)
        (2, 1),              # 2p (6 elétrons)
        (3, 0),              # 3s (2 elétrons)
        (3, 1),              # 3p (6 elétrons)
        (4, 0),              # 4s (2 elétrons)
        (3, 2),              # 3d (10 elétrons)
        (4, 1),              # 4p (6 elétrons)
        (5, 0),              # 5s (2 elétrons)
        (4, 2),              # 4d (10 elétrons)
        (5, 1),              # 5p (6 elétrons)
        (6, 0),              # 6s (2 elétrons)
        (4, 3),              # 4f (14 elétrons)
        (5, 2),              # 5d (10 elétrons)
        (6, 1),              # 6p (6 elétrons)
        (7, 0),              # 7s (2 elétrons)
        (5, 3),              # 5f (14 elétrons)
        (6, 2),              # 6d (10 elétrons)
        (6, 3),              # 6f (14 elétrons — raramente usado)
    ]


def max_electrons_in_subshell(l: int) -> int:
    """Retorna o número máximo de elétrons num subnível l."""
    return 2 * (2 * l + 1)


# ─────────────────────────────────────────────────────────────────────────
# TESTE E DEMONSTRAÇÃO
# ─────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("TESTE: CARGA NUCLEAR EFETIVA (SLATER)")
    print("=" * 70)

    print("\n[Z_eff PARA DIFERENTES ÁTOMOS]")
    for Z in [1, 2, 6, 8, 11, 18, 26, 29]:
        Z_eff_1s = slater_effective_charge(Z, 1, 0)
        Z_eff_2s = slater_effective_charge(Z, 2, 0) if Z > 2 else 0
        Z_eff_3d = slater_effective_charge(Z, 3, 2) if Z > 18 else 0

        print(f"\n  Z={Z:2d}:")
        print(f"    1s: Z_eff = {Z_eff_1s:.2f}")
        if Z > 2:
            print(f"    2s: Z_eff = {Z_eff_2s:.2f}")
        if Z > 18:
            print(f"    3d: Z_eff = {Z_eff_3d:.2f}")

    print("\n[SEQUÊNCIA DE AUFBAU]")
    seq = get_orbital_sequence()
    print("  Ordem de preenchimento:")
    for i, (n, l) in enumerate(seq[:12]):
        label = ["s", "p", "d", "f"][l]
        max_e = max_electrons_in_subshell(l)
        print(f"    {i+1:2d}. {n}{label} (máx {max_e} e⁻)")

    print("\n" + "=" * 70)