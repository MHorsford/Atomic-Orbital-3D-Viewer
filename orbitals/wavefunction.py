"""
orbitals/wavefunction.py
Funções de onda hidrogenoides (ψ) para orbitais atômicos.
"""

import numpy as np
import math
from scipy.special import assoc_laguerre, sph_harm_y   


class HydrogenWavefunction:
    """
    Classe responsável por calcular as funções de onda do átomo de Hidrogênio
    e átomos hidrogenoides (usando Z efetivo).
    """
    
    def __init__(self):
        # Constantes físicas importantes
        self.a0 = 0.529177  # Raio de Bohr em Angstroms
    
    # ============================
    # PARTE RADIAL
    # ============================
    
    def radial_wavefunction(self, r, n, l, Z=1):
        """
        Calcula a parte radial R_{n,l}(r)
        """
        # rho (variável adimensional)
        rho = (2 * Z * r) / (n * self.a0)
        
        # Normalização
        norm = np.sqrt( (2*Z/(n*self.a0))**3 * math.factorial(n - l - 1) / 
                   (2 * n * (math.factorial(n + l))**2) )
        
        # Termos
        exp_term = np.exp(-rho / 2)
        rho_term = rho ** l
        laguerre_poly = assoc_laguerre(rho, n - l - 1, 2 * l + 1)
        
        R_nl = norm * rho_term * exp_term * laguerre_poly
        return R_nl

    # ============================
    # PARTE ANGULAR
    # ============================
    
    def angular_part(self, theta, phi, l, m):
        """
        Calcula a parte angular Y_{l,m}(θ, φ) - Harmônicos Esféricos
        """
        # sph_harm_y(l, m, theta, phi) -> theta = azimuthal, phi = polar
        return sph_harm_y(l, m, theta, phi)
    
    # ============================
    # FUNÇÃO DE ONDA COMPLETA
    # ============================
    
    def psi(self, r, theta, phi, n, l, m, Z=1):
        """
        Função de onda completa ψ_{n,l,m}(r, θ, φ)
        """
        R_nl = self.radial_wavefunction(r, n, l, Z)
        Y_lm = self.angular_part(theta, phi, l, m)
        return R_nl * Y_lm
    
    def probability_density(self, r, theta, phi, n, l, m, Z=1):
        """ |ψ|² """
        wave = self.psi(r, theta, phi, n, l, m, Z)
        return np.abs(wave)**2

    # ============================
    # FUNÇÕES PRONTAS POR ORBITAL (Conveniência)
    # ============================
    
    def psi_1s(self, r, theta=None, phi=None, Z=1):
        """Orbital 1s - não depende de theta/phi"""
        rho = (2 * Z * r) / self.a0
        norm = np.sqrt((Z**3) / (np.pi * self.a0**3))
        return norm * np.exp(-rho / 2)
    
    def psi_2s(self, r, theta=None, phi=None, Z=1):
        """Orbital 2s"""
        rho = (2 * Z * r) / (2 * self.a0)
        norm = np.sqrt((Z**3) / (8 * np.pi * self.a0**3))
        return norm * (2 - rho) * np.exp(-rho / 2)
    
    def psi_2p_z(self, r, theta, phi=None, Z=1):
        """Orbital 2p_z"""
        rho = (2 * Z * r) / (2 * self.a0)
        norm = np.sqrt((Z**3) / (32 * np.pi * self.a0**3))
        return norm * rho * np.exp(-rho / 2) * np.cos(theta)
    
    def psi_2p_x(self, r, theta, phi, Z=1):
        """Orbital 2p_x"""
        rho = (2 * Z * r) / (2 * self.a0)
        norm = np.sqrt((Z**3) / (32 * np.pi * self.a0**3))
        return norm * rho * np.exp(-rho / 2) * np.sin(theta) * np.cos(phi)
    
    def psi_2p_y(self, r, theta, phi, Z=1):
        """Orbital 2p_y"""
        rho = (2 * Z * r) / (2 * self.a0)
        norm = np.sqrt((Z**3) / (32 * np.pi * self.a0**3))
        return norm * rho * np.exp(-rho / 2) * np.sin(theta) * np.sin(phi)

    # ============================
    # MÉTODOS PARA VISUALIZAÇÃO 3D
    # ============================
    
    def generate_grid(self, size=80, range_max=8.0):
        """
        Cria grid 3D cartesiano e converte para coordenadas esféricas
        """
        x = np.linspace(-range_max, range_max, size)
        y = np.linspace(-range_max, range_max, size)
        z = np.linspace(-range_max, range_max, size)
        
        X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
        
        # Coordenadas esféricas
        R = np.sqrt(X**2 + Y**2 + Z**2)
        Theta = np.arctan2(np.sqrt(X**2 + Y**2), Z)   # polar angle
        Phi = np.arctan2(Y, X)                        # azimuthal angle
        
        # Evitar divisão por zero
        R[R == 0] = 1e-10
        
        return X, Y, Z, R, Theta, Phi
    
    def evaluate_on_grid(self, n, l, m, Z=1, size=80, range_max=8.0):
        """
        Avalia |ψ|² em todo o grid 3D
        """
        X, Y, Z_coord, R, Theta, Phi = self.generate_grid(size, range_max)
        
        if n == 1 and l == 0:
            density = self.psi_1s(R, Theta, Phi, Z)
        elif n == 2 and l == 0:
            density = self.psi_2s(R, Theta, Phi, Z)
        elif n == 2 and l == 1:
            if m == 0:
                density = self.psi_2p_z(R, Theta, Phi, Z)
            elif m == 1:
                density = self.psi_2p_x(R, Theta, Phi, Z)  # simplificado
            else:
                density = self.psi_2p_y(R, Theta, Phi, Z)
        else:
            # Usa a função geral para outros casos
            density = self.probability_density(R, Theta, Phi, n, l, m, Z)
        
        return density, X, Y, Z_coord

if __name__ == "__main__":
    wf = HydrogenWavefunction()
    
    print("Testando grid 3D e evaluate_on_grid...")
    
    # Teste 1s
    density_1s, X, Y, Z = wf.evaluate_on_grid(n=1, l=0, m=0, Z=1, size=60, range_max=6.0)
    
    print(f"✓ Grid 1s gerado com sucesso!")
    print(f"   Shape da densidade: {density_1s.shape}")
    print(f"   Densidade máxima: {density_1s.max():.6f}")
    print(f"   Posição aproximada do núcleo: {density_1s[30,30,30]:.6f}")  # centro
    
    # Teste 2p_z
    density_2pz, X, Y, Z = wf.evaluate_on_grid(n=2, l=1, m=0, Z=1, size=60, range_max=8.0)
    print(f"✓ Grid 2p_z gerado com sucesso!")
    print(f"   Shape da densidade: {density_2pz.shape}")