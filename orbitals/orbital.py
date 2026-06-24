"""
orbitals/orbital.py

Classe que representa um orbital atômico individual (ex: 1s, 2p_z, 3d_xy, etc.).
Responsável por gerenciar os dados e calcular sua densidade de probabilidade.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orbitals.wavefunction import HydrogenWavefunction
from orbitals.orbital_types import get_orbital_type, get_orbital_name, get_default_color
import numpy as np
# ===================================================================

class Orbital:
    """
    Representa um orbital quântico específico.
    """

    def __init__(self, 
                 n: int, 
                 l: int, 
                 m: int = 0, 
                 electrons: int = 0, 
                 Z_eff: float = 1.0):
        """
        Parâmetros:
            n        : Número quântico principal (nível de energia)
            l        : Número quântico azimutal (0=s, 1=p, 2=d, 3=f)
            m        : Número quântico magnético (orientação)
            electrons: Quantidade de elétrons ocupando este orbital
            Z_eff    : Carga nuclear efetiva (para átomos multi-eletrônicos)
        """
        self.n = n
        self.l = l
        self.m = m
        self.electrons = electrons
        self._Z_eff = Z_eff          # armazenado internamente; acesso via property

        # Informações do tipo de orbital
        self.type_info = get_orbital_type(l)
        self.name = get_orbital_name(n, l)

        # Visualização
        self.color = get_default_color(l)
        self.opacity = 0.75
        self.is_visible = True

        # Cálculo de onda
        self.wavefunction = HydrogenWavefunction()

        # Cache da densidade (para não recalcular toda hora)
        self.density_grid = None
        self.X = None
        self.Y = None
        self.Z = None

    # ── Fix bug 3: property garante que mudar Z_eff invalida o cache ──
    @property
    def Z_eff(self) -> float:
        return self._Z_eff

    @Z_eff.setter
    def Z_eff(self, value: float) -> None:
        if value != self._Z_eff:
            self._Z_eff = value
            self.density_grid = None   # cache obsoleto — força recálculo
            self.X = self.Y = self.Z = None

    def calculate_density(self, size: int = 80, range_max: float = 8.0) -> None:
        """Calcula e armazena a amplitude da função de onda 3D (fases)"""
        wave_data, X, Y, Z = self.wavefunction.evaluate_on_grid(
            n=self.n,
            l=self.l,
            m=self.m,
            Z=self.Z_eff,
            size=size,
            range_max=range_max
        )
        
        # Normaliza usando o valor ABSOLUTO máximo.
        # Isso garante que a fase positiva vá até +1.0 e a negativa até -1.0
        max_amplitude = np.max(np.abs(wave_data)) + 1e-10
        self.density_grid = wave_data / max_amplitude 
        
        self.X = X
        self.Y = Y
        self.Z = Z

    def get_density(self, size: int = 80, range_max: float = 8.0):
        """Retorna a densidade, calculando apenas se necessário"""
        if self.density_grid is None:
            self.calculate_density(size, range_max)
        return self.density_grid, self.X, self.Y, self.Z

    # Princípio de Pauli: um orbital individual comporta no máximo 2 elétrons.
    # type_info.max_electrons refere-se ao SUBNÍVEL completo (p=6, d=10, f=14),
    # não ao orbital individual — não usar aqui.
    MAX_ELECTRONS_PER_ORBITAL = 2

    def add_electron(self, quantity: int = 1) -> bool:
        """Adiciona elétron(es) respeitando o Princípio de Pauli (máx 2 por orbital)"""
        if self.electrons + quantity <= self.MAX_ELECTRONS_PER_ORBITAL:
            self.electrons += quantity
            return True
        return False

    def remove_electron(self, quantity: int = 1) -> bool:
        """Remove elétron(es)"""
        if self.electrons >= quantity:
            self.electrons -= quantity
            return True
        return False

    def is_full(self) -> bool:
        """Verifica se o orbital está completamente preenchido (2 elétrons, Pauli)"""
        return self.electrons >= self.MAX_ELECTRONS_PER_ORBITAL

    def is_empty(self) -> bool:
        """Verifica se não tem nenhum elétron"""
        return self.electrons == 0

    def __str__(self):
        return f"Orbital {self.name} (m={self.m}) - {self.electrons}/{self.type_info.max_electrons} elétrons"

    def __repr__(self):
        return self.__str__()

# ===================== TESTE =====================
if __name__ == "__main__":
    orb_1s = Orbital(n=1, l=0, electrons=2)
    orb_2pz = Orbital(n=2, l=1, m=0, electrons=2)
    
    print(orb_1s)
    print(orb_2pz)
    print(f"1s está cheio? {orb_1s.is_full()}")
    print(f"2p_z está cheio? {orb_2pz.is_full()}")