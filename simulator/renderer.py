"""
simulator/renderer.py

Classe Renderer — converte orbitais em malhas 3D para renderização.
Suporta 3 modos: isosurface, grid_points (grade densa), points (nuvem Monte Carlo).
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import pyvista as pv
from config import ISO_VALUE, GRID_SIZE, GRID_RANGE, NUM_POINTS_CLOUD
from config import HIGH_QUALITY_RENDER, METALLIC, ROUGHNESS, SPECULAR, SPECULAR_POWER
from utils.grid import make_grid, normalize_array, cartesian_to_spherical
from utils.sampling import sample_orbital_grid
from utils.helpers import quantum_label
from orbitals.wavefunction import HydrogenWavefunction


class Renderer:
    """
    Responsável por converter dados de orbital em geometria 3D (PyVista).
    """
    
    def __init__(self, config=None):
        """Inicializa o renderizador."""
        self.mode = 'isosurface'  # 'isosurface', 'grid_points', 'points'
        self.iso_value = ISO_VALUE
        self.grid_size = GRID_SIZE
        self.grid_range = GRID_RANGE
        self.point_cloud_size = NUM_POINTS_CLOUD
        self.roughness = ROUGHNESS
        self.specular = SPECULAR
        self.specular_power = SPECULAR_POWER
        self.config = config
        # Fator em relação ao valor máximo absoluto do orbital (|ψ| máx)
        # 0.1 a 0.2 é um bom padrão para o valor de contorno de ψ
        self.relative_iso_factor = 0.15 
    
    def set_mode(self, mode: str):
        """
        Define o modo de renderização.
        
        Parâmetros:
            mode : 'isosurface', 'grid_points', ou 'points'
        """
        if mode not in ['isosurface', 'grid_points', 'points']:
            print(f"⚠ Modo desconhecido: {mode}. Mantendo: {self.mode}")
            return
        self.mode = mode
        print(f"✓ Modo de renderização: {mode}")
    
    # ─────────────────────────────────────────────────────────────────────
    # MODO: ISOSURFACE
    # ─────────────────────────────────────────────────────────────────────
    
    def render_isosurface(self, orbital):
        n = orbital.n
        range_max = self._get_range_for_n(n)

        # Ajuste de resolução dinâmica
        if n <= 2:
            current_grid_size = self.grid_size
        elif n == 3:
            current_grid_size = int(self.grid_size * 0.9)
        elif n == 4:
            current_grid_size = int(self.grid_size * 0.75)
        else:
            current_grid_size = int(self.grid_size * 0.6)

        current_grid_size = max(current_grid_size, 80)

        wave, X, Y, Z = orbital.get_density(current_grid_size, range_max)

        wave_max = np.max(np.abs(wave))
        if not np.isfinite(wave_max) or wave_max < 1e-15:
            print(f"⚠ Orbital com amplitude inválida")
            return (None, None)

        grid = pv.ImageData()
        # IMPORTANTE: Garanta que as dimensões casem com a ordem Fortran 'F'
        grid.dimensions = wave.shape

        x_min, x_max = X.min(), X.max()
        y_min, y_max = Y.min(), Y.max()
        z_min, z_max = Z.min(), Z.max()

        grid.origin = (x_min, y_min, z_min)
        grid.spacing = (
            (x_max - x_min) / (wave.shape[0] - 1) if wave.shape[0] > 1 else 1.0,
            (y_max - y_min) / (wave.shape[1] - 1) if wave.shape[1] > 1 else 1.0,
            (z_max - z_min) / (wave.shape[2] - 1) if wave.shape[2] > 1 else 1.0,
        )

        if wave_max > 1e-12:
            wave_norm = wave / wave_max
        else:
            wave_norm = wave

        # CORREÇÃO 2: PyVista exige obrigatoriamente order='F' para mapear os eixos corretamente
        grid['wave'] = wave_norm.flatten(order='F')

        # CORREÇÃO 1: Isosuperfície adaptativa baseada na interface + fator relativo
        # Se self.iso_value for muito pequeno no slider, usamos o fator dinâmico baseado no pico do orbital
        iso_val = self.iso_value if self.iso_value > 0.05 else self.relative_iso_factor
        
        mesh_pos, mesh_neg = None, None

        try:
            contour_pos = grid.contour(isosurfaces=[iso_val], scalars='wave')
            if contour_pos.n_points > 0:
                mesh_pos = contour_pos.smooth(n_iter=80, relaxation_factor=0.2)
                mesh_pos.compute_normals(inplace=True)

            contour_neg = grid.contour(isosurfaces=[-iso_val], scalars='wave')
            if contour_neg.n_points > 0:
                mesh_neg = contour_neg.smooth(n_iter=80, relaxation_factor=0.2)
                mesh_neg.compute_normals(inplace=True)

            return (mesh_pos, mesh_neg)

        except Exception as e:
            print(f"⚠ Erro controlado ao gerar isosurface: {e}")
            return (None, None)

    # ─────────────────────────────────────────────────────────────────────
    # MODO: VOLUME (VOLUMETRIC)
    # ─────────────────────────────────────────────────────────────────────

    def render_grid_points(self, orbital):
        """
        Renderiza um orbital como uma nuvem de pontos densa filtrada.
        """
        n = orbital.n
        range_max = self._get_range_for_n(n)

        density, X, Y, Z = orbital.get_density(self.grid_size // 2, range_max)
        
        # CORREÇÃO 3: Filtrar pontos com densidade praticamente nula 
        # Isso impede que o orbital vire um bloco/cubo opaco de pontos vazios
        dens_flat = density.flatten()
        max_dens = np.max(dens_flat)
        
        # Mantém apenas pontos com mais de 0.5% da densidade máxima
        threshold = max_dens * 0.005 if max_dens > 1e-15 else 1e-15
        mask = dens_flat > threshold
        
        points = np.column_stack([X.flatten(), Y.flatten(), Z.flatten()])
        
        # Se nenhum ponto passar pelo filtro, retorna malha vazia
        if not np.any(mask):
            return self._empty_mesh()
            
        mesh = pv.PolyData(points[mask])
        mesh['density'] = dens_flat[mask]
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
            # Converter para esféricas
            r, theta, phi = cartesian_to_spherical(x, y, z)
            
            # Calcular psi²
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
        elif self.mode == 'grid_points':
            return self.render_grid_points(orbital)
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
        # Permite valores até 2.0 para capturar orbitais muito difusos
        self.iso_value = max(0.001, min(2.0, iso_value))
    
    def set_grid_resolution(self, size: int):
        """Define a resolução do grid para cálculo de densidade."""
        self.grid_size = max(20, min(150, size))
    
    def set_point_cloud_size(self, n_points: int):
        """Define o número de pontos na nuvem Monte Carlo."""
        self.point_cloud_size = max(1000, min(50000, n_points))

    def _get_range_for_n(self, n):
        if n <= 2: return 12.0
        elif n == 3: return 28.0
        elif n == 4: return 55.0
        else: return 95.0