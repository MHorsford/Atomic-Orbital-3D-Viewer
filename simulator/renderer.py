"""
simulator/renderer.py

Classe Renderer — converte orbitais em malhas 3D para renderização.
Suporta 3 modos: isosurface, volume (volumetric), points (nuvem).
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import pyvista as pv
from config import ISO_VALUE, GRID_SIZE, GRID_RANGE, NUM_POINTS_CLOUD
from utils.grid import make_grid, normalize_array
from utils.sampling import sample_orbital_grid
from utils.helpers import quantum_label


class Renderer:
    """
    Responsável por converter dados de orbital em geometria 3D (PyVista).
    """
    
    def __init__(self):
        """Inicializa o renderizador."""
        self.mode = 'isosurface'  # 'isosurface', 'volume', 'points'
        self.iso_value = ISO_VALUE
        self.grid_size = GRID_SIZE
        self.grid_range = GRID_RANGE
        self.point_cloud_size = NUM_POINTS_CLOUD
    
    def set_mode(self, mode: str):
        """
        Define o modo de renderização.
        
        Parâmetros:
            mode : 'isosurface', 'volume', ou 'points'
        """
        if mode not in ['isosurface', 'volume', 'points']:
            print(f"⚠ Modo desconhecido: {mode}. Mantendo: {self.mode}")
            return
        self.mode = mode
        print(f"✓ Modo de renderização: {mode}")
    
    # ─────────────────────────────────────────────────────────────────────
    # MODO: ISOSURFACE
    # ─────────────────────────────────────────────────────────────────────
    
    def render_isosurface(self, orbital):
        """
        Renderiza um orbital como isosuperfície (superfície de probabilidade constante).
        
        Parâmetros:
            orbital : objeto Orbital
        
        Retorna:
            pyvista.PolyData com a malha
        """
        # Calcular densidade no grid
        density, X, Y, Z = orbital.get_density(self.grid_size, self.grid_range)
        
        # Criar grid ImageData (mais apropriado para dados regulares)
        grid = pv.ImageData()
        grid.dimensions = density.shape
        
        # Definir origem e espaçamento
        x_min, x_max = X.min(), X.max()
        y_min, y_max = Y.min(), Y.max()
        z_min, z_max = Z.min(), Z.max()
        
        grid.origin = (x_min, y_min, z_min)
        grid.spacing = (
            (x_max - x_min) / (density.shape[0] - 1) if density.shape[0] > 1 else 1.0,
            (y_max - y_min) / (density.shape[1] - 1) if density.shape[1] > 1 else 1.0,
            (z_max - z_min) / (density.shape[2] - 1) if density.shape[2] > 1 else 1.0
        )
        grid['density'] = density.flatten(order='F')
        
        # Extrair isosurface
        iso_value = self.iso_value * density.max()
        
        try:
            mesh = grid.contour(
                isosurfaces=[iso_value],
                scalars='density'
            )
            
            if mesh.n_cells == 0:
                print(f"⚠ Isosurface vazia para orbital {orbital.name}")
                return self._empty_mesh()
            
            mesh.compute_normals(inplace=True)
            return mesh
        
        except Exception as e:
            print(f"⚠ Erro ao gerar isosurface: {e}")
            return self._empty_mesh()
    
    # ─────────────────────────────────────────────────────────────────────
    # MODO: VOLUME (VOLUMETRIC)
    # ─────────────────────────────────────────────────────────────────────
    
    def render_volume(self, orbital):
        """
        Renderiza um orbital como nuvem volumétrica (raycasting).
        
        Para isso, retornamos uma point cloud densa com cores proporcionais à densidade.
        
        Parâmetros:
            orbital : objeto Orbital
        
        Retorna:
            pyvista.PolyData com pontos coloridos
        """
        # Calcular densidade
        density, X, Y, Z = orbital.get_density(self.grid_size // 2, self.grid_range)
        
        # Criar grid de pontos
        points = np.column_stack([X.flatten(), Y.flatten(), Z.flatten()])
        
        # Valores de densidade para colorir
        density_values = density.flatten()
        
        # Criar PolyData (point cloud)
        mesh = pv.PolyData(points)
        mesh['density'] = density_values
        
        # Adicionar células (para não aparecerem como pontos soltos)
        # Usar vertices para manter como nuvem
        mesh.point_data['density'] = density_values
        
        return mesh
    
    # ─────────────────────────────────────────────────────────────────────
    # MODO: POINT CLOUD (MONTE CARLO)
    # ─────────────────────────────────────────────────────────────────────
    
    def render_points(self, orbital):
        """
        Renderiza um orbital como nuvem de pontos amostrada via Monte Carlo.
        
        Parâmetros:
            orbital : objeto Orbital
        
        Retorna:
            pyvista.PolyData com pontos
        """
        # Função psi² que retorna valores num ponto (x, y, z)
        def psi_squared_func(x, y, z):
            from utils.grid import cartesian_to_spherical
            
            # Converter para esféricas
            r, theta, phi = cartesian_to_spherical(x, y, z)
            
            # Calcular psi²
            from orbitals.wavefunction import HydrogenWavefunction
            wf = HydrogenWavefunction(use_angstrom=True)
            psi = wf.psi(r, theta, phi, orbital.n, orbital.l, orbital.m, orbital.Z_eff)
            return np.abs(psi) ** 2
        
        try:
            # Amostragem
            points = sample_orbital_grid(
                psi_squared_func,
                n_samples=self.point_cloud_size,
                size=30,
                range_max=self.grid_range
            )
            
            if len(points) == 0:
                return self._empty_mesh()
            
            # Criar PolyData
            mesh = pv.PolyData(points)
            
            # Adicionar densidade como propriedade escalar
            densities = np.array([psi_squared_func(
                np.array([p[0]]), np.array([p[1]]), np.array([p[2]])
            )[0] for p in points])
            mesh['density'] = densities
            
            return mesh
        
        except Exception as e:
            print(f"⚠ Erro ao gerar point cloud: {e}")
            return self._empty_mesh()
    
    # ─────────────────────────────────────────────────────────────────────
    # INTERFACE PÚBLICA
    # ─────────────────────────────────────────────────────────────────────
    
    def render_orbital(self, orbital):
        """
        Renderiza um orbital usando o modo selecionado.
        
        Parâmetros:
            orbital : objeto Orbital
        
        Retorna:
            pyvista.PolyData
        """
        if self.mode == 'isosurface':
            return self.render_isosurface(orbital)
        elif self.mode == 'volume':
            return self.render_volume(orbital)
        elif self.mode == 'points':
            return self.render_points(orbital)
        else:
            print(f"⚠ Modo desconhecido: {self.mode}")
            return self._empty_mesh()
    
    def render_nucleus(self, nucleus, radius: float = 0.2):
        """
        Renderiza o núcleo como esfera.
        
        Parâmetros:
            nucleus : objeto Nucleus
            radius  : raio da esfera
        
        Retorna:
            pyvista.PolyData
        """
        sphere = pv.Sphere(
            radius=radius,
            center=[0, 0, 0],
            theta_resolution=30,
            phi_resolution=30
        )
        return sphere
    
    # ─────────────────────────────────────────────────────────────────────
    # UTILITÁRIOS
    # ─────────────────────────────────────────────────────────────────────
    
    def _empty_mesh(self):
        """Retorna uma malha vazia (útil para erros)."""
        return pv.PolyData()
    
    def set_iso_value(self, iso_value: float):
        """Define o valor de isosurface."""
        self.iso_value = max(0.001, min(1.0, iso_value))
    
    def set_grid_resolution(self, size: int):
        """Define a resolução do grid para cálculo de densidade."""
        self.grid_size = max(20, min(150, size))
    
    def set_point_cloud_size(self, n_points: int):
        """Define o número de pontos na nuvem Monte Carlo."""
        self.point_cloud_size = max(1000, min(50000, n_points))