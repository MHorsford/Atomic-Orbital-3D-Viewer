"""
physics/coulomb.py

Cálculos de força eletrostática e energia de Coulomb para o simulador.
Útil para visualizar interações entre partículas e estimar energias de ionização.

Referência: Lei de Coulomb e energia eletrostática em SI.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from physics.constants import K_COULOMB, E_CHARGE, EV_TO_JOULE, E_IONIZATION_H


# ─────────────────────────────────────────────────────────────────────────
# FORÇA DE COULOMB
# ─────────────────────────────────────────────────────────────────────────

def coulomb_force(q1: float, q2: float, r: float) -> float:
    """
    Calcula a magnitude da força eletrostática entre duas cargas.

    Lei de Coulomb:  F = k · |q1| · |q2| / r²

    Parâmetros:
        q1, q2 : Cargas em Coulombs [C]
        r      : Distância em metros [m]

    Retorna:
        Magnitude da força em Newtons [N]
    """
    if r <= 0:
        return float('inf')
    return K_COULOMB * abs(q1) * abs(q2) / (r ** 2)


def coulomb_force_vectors(pos1: np.ndarray, q1: float,
                          pos2: np.ndarray, q2: float) -> np.ndarray:
    """
    Calcula a força vetorial sobre a partícula 1 devido à partícula 2.

    Retorna um vetor 3D que aponta da carga 2 para a carga 1 (repulsivo se q1·q2 > 0).

    Parâmetros:
        pos1, pos2 : Posições em 3D [m]
        q1, q2     : Cargas em Coulombs [C]

    Retorna:
        Força vetorial (3,) em Newtons [N]
    """
    dr = pos1 - pos2
    r_mag = np.linalg.norm(dr)

    if r_mag < 1e-15:
        return np.zeros(3)

    r_hat = dr / r_mag  # vetor unitário
    F_mag = coulomb_force(q1, q2, r_mag)

    # Força aponta na direção de dr se repulsivo, oposto se atrativo
    if q1 * q2 > 0:  # mesma carga → repulsivo
        return F_mag * r_hat
    else:  # cargas opostas → atrativo
        return -F_mag * r_hat


# ─────────────────────────────────────────────────────────────────────────
# ENERGIA DE COULOMB
# ─────────────────────────────────────────────────────────────────────────

def coulomb_potential_energy(q1: float, q2: float, r: float) -> float:
    """
    Calcula a energia potencial eletrostática entre duas cargas.

    U = k · q1 · q2 / r

    Parâmetros:
        q1, q2 : Cargas em Coulombs [C]
        r      : Distância em metros [m]

    Retorna:
        Energia em Joules [J]

    Nota: Negativa para cargas opostas (atrativo), positiva para mesma carga (repulsivo).
    """
    if r <= 0:
        return float('inf')
    return K_COULOMB * q1 * q2 / r


def coulomb_potential_energy_ev(q1: float, q2: float, r: float) -> float:
    """
    O mesmo que coulomb_potential_energy, mas retorna em eV.
    """
    U_joule = coulomb_potential_energy(q1, q2, r)
    return U_joule / EV_TO_JOULE


# ─────────────────────────────────────────────────────────────────────────
# ENERGIA DE IONIZAÇÃO EFETIVA (Bohr)
# ─────────────────────────────────────────────────────────────────────────

def ionization_energy_bohr(Z_eff: float, n: int) -> float:
    """
    Estima a energia de ionização de um elétron no nível n de um átomo
    com carga nuclear efetiva Z_eff.

    Fórmula de Bohr:  E_n = -13.6 eV · (Z_eff)² / n²

    Parâmetros:
        Z_eff : Carga nuclear efetiva (após screening)
        n     : Número quântico principal

    Retorna:
        Energia de ionização em eV (sempre positiva).
    """
    E_n = E_IONIZATION_H * (Z_eff ** 2) / (n ** 2)
    return abs(E_n)  # retorna valor positivo (energia necessária para ionizar)


def binding_energy(Z_eff: float, n: int) -> float:
    """
    Retorna a energia de ligação (negativa) do elétron no nível n.
    É o negativo da energia de ionização.

    E_n = -13.6 eV · (Z_eff)² / n²
    """
    return -ionization_energy_bohr(Z_eff, n)


# ─────────────────────────────────────────────────────────────────────────
# RAIO ORBITAL MÉDIO (Bohr)
# ─────────────────────────────────────────────────────────────────────────

def bohr_orbital_radius(Z_eff: float, n: int) -> float:
    """
    Estima o raio médio do orbital no nível n com carga nuclear efetiva Z_eff.

    Fórmula de Bohr:  <r> = a₀ · n² / Z_eff

    onde a₀ = 0.529 Å é o raio de Bohr.

    Parâmetros:
        Z_eff : Carga nuclear efetiva
        n     : Número quântico principal

    Retorna:
        Raio médio em Angstroms [Å]
    """
    from physics.constants import A0_ANGSTROM
    return A0_ANGSTROM * (n ** 2) / Z_eff


# ─────────────────────────────────────────────────────────────────────────
# REPULSÃO NÚCLEO-ELÉTRON E ELÉTRON-ELÉTRON
# ─────────────────────────────────────────────────────────────────────────

def nuclear_attraction_energy(Z: int, Z_eff: float, n: int) -> float:
    """
    Energia de atração elétron-núcleo para um elétron no nível n.

    Para um elétron a uma distância média <r> = a₀ · n² / Z_eff:
        U = -k · Z_eff · e² / <r>

    Retorna em eV.
    """
    from physics.constants import A0_METERS
    r_avg = bohr_orbital_radius(Z_eff, n) * 1e-10  # Å → m
    U_joule = coulomb_potential_energy(Z_eff * E_CHARGE, -E_CHARGE, r_avg)
    return U_joule / EV_TO_JOULE


def electron_electron_repulsion_estimate(Z: int, n1: int, n2: int) -> float:
    """
    Estimativa grosseira da repulsão entre dois elétrons em diferentes níveis.

    Assume que os elétrons estão a uma distância aproximada de |<r₁> - <r₂>|
    e usam Z_eff ≈ (Z - σ) onde σ é um screening grosseiro.

    Retorna em eV.

    Nota: Esta é uma estimativa muito simplificada. Cálculos reais requerem
    integração numérica das funções de onda.
    """
    # Estimativa de Z_eff para cada nível (muito simplificado)
    Z_eff_1 = max(1, Z - 0.5)  # primeiro orbital vê mais da carga nuclear
    Z_eff_2 = max(1, Z - (n1 + n2 - 1))  # orbital externo vê mais screening

    r1 = bohr_orbital_radius(Z_eff_1, n1) * 1e-10  # → m
    r2 = bohr_orbital_radius(Z_eff_2, n2) * 1e-10  # → m
    r_sep = abs(r1 - r2) if abs(r1 - r2) > 1e-12 else 1e-12

    U_joule = coulomb_potential_energy(-E_CHARGE, -E_CHARGE, r_sep)
    return U_joule / EV_TO_JOULE


# ─────────────────────────────────────────────────────────────────────────
# TESTE E DEMONSTRAÇÃO
# ─────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from physics.constants import A0_METERS

    print("=" * 70)
    print("TESTE: CÁLCULOS ELETROSTÁTICOS")
    print("=" * 70)

    # --- Força de Coulomb ---
    print("\n[FORÇA DE COULOMB]")
    q_e = -E_CHARGE  # elétron
    q_p = +E_CHARGE  # próton
    r = A0_METERS    # a um raio de Bohr
    F = coulomb_force(q_e, q_p, r)
    print(f"  Força elétron-próton a r=a₀: {F:.6e} N")
    print(f"  Equivalente a: {F / 1e-8:.2f} nanoNewtons")

    # --- Energia de Coulomb ---
    print("\n[ENERGIA DE COULOMB]")
    U_joule = coulomb_potential_energy(q_e, q_p, r)
    U_ev = coulomb_potential_energy_ev(q_e, q_p, r)
    print(f"  U(e⁻, p⁺) a r=a₀: {U_joule:.6e} J = {U_ev:.2f} eV")
    print(f"  (Esperado ≈ -27.2 eV para dois raios de Bohr)")

    # --- Energia de ionização ---
    print("\n[ENERGIA DE IONIZAÇÃO (Bohr)]")
    for Z in [1, 2, 6, 8]:
        E_ion_1s = ionization_energy_bohr(Z, 1)
        E_ion_2s = ionization_energy_bohr(Z, 2)
        print(f"  Z={Z:2d}: E_ion(1s)={E_ion_1s:6.2f} eV, E_ion(2s)={E_ion_2s:6.2f} eV")

    # --- Raio orbital ---
    print("\n[RAIO ORBITAL MÉDIO]")
    r_1s_H = bohr_orbital_radius(1, 1)
    r_1s_He = bohr_orbital_radius(2, 1)
    r_2s_H = bohr_orbital_radius(1, 2)
    print(f"  1s do H:  {r_1s_H:.4f} Å (esperado ≈ 0.529 Å)")
    print(f"  1s do He: {r_1s_He:.4f} Å (esperado ≈ 0.265 Å)")
    print(f"  2s do H:  {r_2s_H:.4f} Å (esperado ≈ 2.116 Å)")

    # --- Atração nuclear ---
    print("\n[ATRAÇÃO ELÉTRON-NÚCLEO]")
    U_nuc_H_1s = nuclear_attraction_energy(1, 1, 1)
    U_nuc_He_1s = nuclear_attraction_energy(2, 2, 1)
    print(f"  H (1s):  U = {U_nuc_H_1s:.2f} eV")
    print(f"  He (1s): U = {U_nuc_He_1s:.2f} eV (mais negativo = mais ligado)")

    print("\n" + "=" * 70)