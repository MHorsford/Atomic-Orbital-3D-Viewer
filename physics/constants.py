"""
physics/constants.py

Constantes físicas fundamentais e derivadas para o simulador de orbitais atômicos.
Todas as constantes estão em SI (Sistema Internacional) por padrão.

Referências:
  - CODATA 2018: https://physics.nist.gov/cuu/Constants/
  - IUPAC 2021: https://iupac.qmul.ac.uk/
"""

import math

# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTES FUNDAMENTAIS (SI)
# ═══════════════════════════════════════════════════════════════════════════

# Constante de Planck
H = 6.62607015e-34        # [J·s] Constante de Planck completa
HBAR = H / (2 * math.pi)  # [J·s] Constante de Planck reduzida (ℏ)

# Velocidade da luz
C = 299792458             # [m/s] Velocidade da luz no vácuo

# Carga elementar
E_CHARGE = 1.602176634e-19  # [C] Carga do elétron (em módulo)
EV_TO_JOULE = E_CHARGE      # [J/eV] 1 eV em Joules — mesmo que a carga elementar

# Massa de repouso
M_ELECTRON = 9.1093837015e-31    # [kg] Massa do elétron
M_PROTON = 1.67262192369e-27     # [kg] Massa do próton
M_NEUTRON = 1.67492749804e-27    # [kg] Massa do nêutron

# Permitividade do vácuo
EPSILON_0 = 8.8541878128e-12  # [F/m] Permitividade do vácuo

# Constante de Coulomb
K_COULOMB = 1 / (4 * math.pi * EPSILON_0)  # [N·m²/C²] ≈ 8.9875517923e9

# Constante gravitacional
G = 6.67430e-11  # [m³·kg⁻¹·s⁻²] Constante gravitacional


# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTES ATÔMICAS (Unidades Atômicas - a.u.)
# ═══════════════════════════════════════════════════════════════════════════

# Raio de Bohr (unidade de comprimento)
A0_METERS = 5.29177210903e-11  # [m] Raio de Bohr em metros (SI)
A0_ANGSTROM = 0.529177210903   # [Å] Raio de Bohr em Angstroms

# Energia de Rydberg
RY_EV = 13.605693122994          # [eV] Energia de Rydberg
RY_JOULE = RY_EV * E_CHARGE      # [J] Energia de Rydberg em Joules
RY_HARTREE = RY_EV / 27.21138505 # [E_h] Energia de Rydberg em Hartrees

# Energia de ionização do hidrogênio
E_IONIZATION_H = 13.605693122994  # [eV] Primeira energia de ionização do H

# Comprimento de Compton do elétron
COMPTON_WAVELENGTH = H / (M_ELECTRON * C)  # [m]

# Raio clássico do elétron
ELECTRON_RADIUS = K_COULOMB * E_CHARGE**2 / (M_ELECTRON * C**2)  # [m]

# Magnetão de Bohr (momento magnético do elétron)
MU_B = E_CHARGE * HBAR / (2 * M_ELECTRON)  # [A·m² ou J/T]


# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTES ATÔMICAS DERIVADAS
# ═══════════════════════════════════════════════════════════════════════════

# Frequência de Rydberg (para cálculos espectrais)
RY_FREQ = RY_JOULE / HBAR  # [Hz]

# Comprimento de onda de Rydberg (série H)
RY_WAVELENGTH = C / RY_FREQ  # [m]

# Número de massa atômica (unidade de massa atômica)
AMU = 1.66053906660e-27  # [kg] Unidade de massa atômica

# Razão de massa próton/elétron
MASS_RATIO_P_E = M_PROTON / M_ELECTRON  # ≈ 1836.15


# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTES PARA SCREENING E CÁLCULOS MULTIELETRÔNICOS
# ═══════════════════════════════════════════════════════════════════════════

# Fator de screening padrão (usado nas regras de Slater)
# Diferentes para cada subnível: s, p, d, f
SLATER_SCREENING = {
    's': 0.30,  # Orbitais s internos blindam 30% da carga nuclear
    'p': 0.35,  # Orbitais p internos blindam 35% da carga nuclear
    'd': 0.35,  # Orbitais d internos blindam 35% da carga nuclear
    'f': 0.35   # Orbitais f internos blindam 35% da carga nuclear
}

# Fator de penetração (Slater)
# Mais alto = mais perto do núcleo = menos blindado
PENETRATION_FACTOR = {
    's': 0.85,  # Orbitais s penetram bem perto do núcleo
    'p': 0.85,  # Orbitais p penetram moderadamente
    'd': 0.35,  # Orbitais d penetram menos
    'f': 0.35   # Orbitais f penetram pouco
}


# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTES DE VISUALIZAÇÃO E SIMULAÇÃO
# ═══════════════════════════════════════════════════════════════════════════

# Raios visuais para as partículas nucleares (em Angstroms)
PROTON_RADIUS_VISUAL = 0.1    # [Å] Raio visual do próton
NEUTRON_RADIUS_VISUAL = 0.1   # [Å] Raio visual do nêutron
ELECTRON_RADIUS_VISUAL = 0.05 # [Å] Raio visual do elétron (bem pequeno)

# Isosurface de probabilidade padrão para visualização
ISO_VALUE_DEFAULT = 0.02  # Superfície onde |ψ|² = 2% do valor máximo

# Resolução padrão do grid 3D
GRID_SIZE_DEFAULT = 80  # Número de pontos por dimensão
GRID_RANGE_DEFAULT = 8.0  # [Bohr] Extensão da caixa (±8 a.u.)


# ═══════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE CONVENIÊNCIA
# ═══════════════════════════════════════════════════════════════════════════

def bohr_to_meters(r_bohr):
    """Converte raio em unidades de Bohr para metros"""
    return r_bohr * A0_METERS

def meters_to_bohr(r_meters):
    """Converte raio em metros para unidades de Bohr"""
    return r_meters / A0_METERS

def bohr_to_angstrom(r_bohr):
    """Converte raio em unidades de Bohr para Angstroms"""
    return r_bohr * A0_ANGSTROM

def angstrom_to_bohr(r_angstrom):
    """Converte raio em Angstroms para unidades de Bohr"""
    return r_angstrom / A0_ANGSTROM

def ev_to_joule(energy_ev):
    """Converte energia em eV para Joules"""
    return energy_ev * E_CHARGE

def joule_to_ev(energy_j):
    """Converte energia em Joules para eV"""
    return energy_j / E_CHARGE

def hartree_to_ev(energy_hartree):
    """Converte energia em Hartrees para eV"""
    return energy_hartree * 27.21138505

def ev_to_hartree(energy_ev):
    """Converte energia em eV para Hartrees"""
    return energy_ev / 27.21138505


# ═══════════════════════════════════════════════════════════════════════════
# TABELA DE REFERÊNCIA RÁPIDA
# ═══════════════════════════════════════════════════════════════════════════

"""
RESUMO DAS CONSTANTES MAIS USADAS:

┌─────────────────────┬──────────────────┬─────────────────────────────┐
│ Quantidade          │ Símbolo          │ Valor (SI)                  │
├─────────────────────┼──────────────────┼─────────────────────────────┤
│ Raio de Bohr        │ a₀               │ 5.292e-11 m                 │
│ Carga do elétron    │ e                │ 1.602e-19 C                 │
│ Massa do elétron    │ mₑ               │ 9.109e-31 kg                │
│ Constante de Planck │ ℏ                │ 1.055e-34 J·s               │
│ Const. de Coulomb   │ k                │ 8.988e+9 N·m²/C²            │
│ Energia Rydberg     │ Ry               │ 13.61 eV = 2.180e-18 J      │
│ Magnetão de Bohr    │ μB               │ 9.285e-24 J/T               │
└─────────────────────┴──────────────────┴─────────────────────────────┘

UNIDADES ATÔMICAS (a.u.):
  - Comprimento: a₀ (raio de Bohr)
  - Energia: Eₕ (Hartree) = 2 Ry
  - Carga: e (carga elementar)
"""


# ═══════════════════════════════════════════════════════════════════════════
# TESTE
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("CONSTANTES FÍSICAS DO SIMULADOR DE ORBITAIS ATÔMICOS")
    print("=" * 70)
    
    print("\n[CONSTANTES FUNDAMENTAIS]")
    print(f"  Constante de Planck (ℏ): {HBAR:.6e} J·s")
    print(f"  Velocidade da luz (c):    {C:.6e} m/s")
    print(f"  Carga do elétron (e):     {E_CHARGE:.6e} C")
    print(f"  Massa do elétron (mₑ):    {M_ELECTRON:.6e} kg")
    print(f"  Const. de Coulomb (k):    {K_COULOMB:.6e} N·m²/C²")
    
    print("\n[CONSTANTES ATÔMICAS]")
    print(f"  Raio de Bohr (a₀):        {A0_METERS:.6e} m = {A0_ANGSTROM:.6f} Å")
    print(f"  Energia Rydberg:          {RY_EV:.6f} eV = {RY_JOULE:.6e} J")
    print(f"  Magnetão de Bohr (μB):    {MU_B:.6e} J/T")
    
    print("\n[CONVERSÕES DE EXEMPLO]")
    r_bohr = 1.0
    print(f"  {r_bohr} Bohr = {bohr_to_meters(r_bohr):.6e} m = {bohr_to_angstrom(r_bohr):.6f} Å")
    
    E_ev = 13.6
    print(f"  {E_ev} eV = {ev_to_joule(E_ev):.6e} J = {ev_to_hartree(E_ev):.6f} Hartree")
    
    print("\n[VISUALIZAÇÃO]")
    print(f"  Grid padrão: {GRID_SIZE_DEFAULT}³ pontos em ±{GRID_RANGE_DEFAULT} a.u.")
    print(f"  Isosurface: |ψ|² = {ISO_VALUE_DEFAULT}")
    print(f"  Raio visual próton: {PROTON_RADIUS_VISUAL} Å")
    
    print("\n" + "=" * 70)