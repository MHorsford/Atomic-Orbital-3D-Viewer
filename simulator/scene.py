"""
simulator/scene.py

Classe Scene — gerencia a cena 3D com PyVista.
Responsável pela câmera, iluminação, e adição/remoção de objetos 3D.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import pyvista as pv
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, BG_COLOR,
    SHOW_AXES, SHOW_NUCLEUS, CAMERA_INITIAL_POSITION, CAMERA_FOCAL_POINT,
    COLOR_NUCLEUS, AMBIENT_LIGHT_INTENSITY, DIRECTIONAL_LIGHT_INTENSITY
)


class Scene:
    """
    Encapsula o PyVista Plotter e gerencia a cena 3D.
    """
    
    def __init__(self, title: str = "Atomic Orbital Simulator"):
        """
        Parâmetros:
            title : título da janela
        """
        # Criar plotter
        self.plotter = pv.Plotter(
            window_size=(WINDOW_WIDTH, WINDOW_HEIGHT),
            title=title,
            off_screen=False
        )
        
        # Configurar cor de fundo
        self.plotter.background_color = BG_COLOR
        
        # Armazenar referências dos objetos na cena
        self.actors = {}  # {name: actor}
        self.orbital_meshes = {}  # {orbital_id: mesh}
        
        # Configurar câmera e iluminação
        self._setup_camera()
        self._setup_lighting()
        
        # Adicionar eixos se configurado
        if SHOW_AXES:
            self._add_axes()
        
        # Adicionar núcleo (esfera central) se configurado
        if SHOW_NUCLEUS:
            self._add_nucleus_sphere()
    
    def _setup_camera(self) -> None:
        """Configura a câmera inicial."""
        self.plotter.camera.position = CAMERA_INITIAL_POSITION
        self.plotter.camera.focal_point = CAMERA_FOCAL_POINT
        self.plotter.camera.up = (0, 0, 1)  # Eixo Z aponta para cima
        self.plotter.camera.zoom(0.8)  # Zoom inicial
    
    def _setup_lighting(self) -> None:
        """Configura iluminação ambient e direcional."""
        # Usar o kit de iluminação padrão do PyVista (3 luzes)
        self.plotter.enable_3_lights()
    
    def _add_axes(self) -> None:
        """Adiciona eixos de coordenadas à cena."""
        self.plotter.add_axes(
            xlabel='X', ylabel='Y', zlabel='Z',
            x_color='red', y_color='green', z_color='blue'
        )
    
    def _add_nucleus_sphere(self) -> None:
        """Adiciona uma esfera dourada no centro representando o núcleo."""
        nucleus = pv.Sphere(radius=0.2, center=[0, 0, 0], theta_resolution=20, phi_resolution=20)
        self.plotter.add_mesh(
            nucleus,
            color=COLOR_NUCLEUS,
            opacity=0.9,
            show_edges=False,
            label='Núcleo'
        )
        self.actors['nucleus'] = nucleus
    
    def add_orbital_mesh(self, mesh, orbital_id: str, color, opacity: float = 0.8):
        """
        Adiciona uma malha 3D de orbital à cena.
        
        Parâmetros:
            mesh       : pyvista.PolyData ou similar
            orbital_id : identificador único (ex: "1s", "2p_z")
            color      : cor (RGB tupla ou nome)
            opacity    : opacidade [0, 1]
        """
        actor = self.plotter.add_mesh(
            mesh,
            color=color,
            opacity=opacity,
            show_edges=False,
            smooth_shading=True
        )
        
        self.orbital_meshes[orbital_id] = {
            'mesh': mesh,
            'actor': actor,
            'color': color,
            'opacity': opacity
        }
    
    def update_orbital_mesh(self, orbital_id: str, mesh, color=None, opacity=None):
        """
        Atualiza uma malha de orbital já existente na cena.
        
        Parâmetros:
            orbital_id : identificador do orbital
            mesh       : nova malha
            color      : nova cor (None = manter)
            opacity    : nova opacidade (None = manter)
        """
        if orbital_id not in self.orbital_meshes:
            print(f"⚠ Orbital {orbital_id} não encontrado na cena")
            return
        
        old_data = self.orbital_meshes[orbital_id]
        
        # Usar valores antigos se novos não fornecidos
        color = color or old_data['color']
        opacity = opacity if opacity is not None else old_data['opacity']
        
        # Remover malha antiga
        self.plotter.remove_actor(old_data['actor'])
        
        # Adicionar malha nova
        self.add_orbital_mesh(mesh, orbital_id, color, opacity)
    
    def remove_orbital_mesh(self, orbital_id: str):
        """
        Remove uma malha de orbital da cena.
        
        Parâmetros:
            orbital_id : identificador do orbital
        """
        if orbital_id not in self.orbital_meshes:
            return
        
        data = self.orbital_meshes[orbital_id]
        self.plotter.remove_actor(data['actor'])
        del self.orbital_meshes[orbital_id]
    
    def clear_orbital_meshes(self):
        """Remove todas as malhas de orbitais (mantém núcleo e eixos)."""
        for orbital_id in list(self.orbital_meshes.keys()):
            self.remove_orbital_mesh(orbital_id)
    
    def set_camera_position(self, position, focal_point=None):
        """
        Define a posição da câmera.
        
        Parâmetros:
            position    : tupla (x, y, z)
            focal_point : tupla (x, y, z) ou None para manter
        """
        self.plotter.camera.position = position
        if focal_point is not None:
            self.plotter.camera.focal_point = focal_point
    
    def get_camera_position(self):
        """Retorna a posição atual da câmera."""
        return self.plotter.camera.position
    
    def reset_camera(self):
        """Reseta a câmera para posição inicial."""
        self.set_camera_position(CAMERA_INITIAL_POSITION, CAMERA_FOCAL_POINT)
    
    def set_background_color(self, color):
        """
        Define a cor de fundo.
        
        Parâmetros:
            color : tupla RGB (0-1) ou string
        """
        self.plotter.background_color = color
    
    def show(self):
        """Inicia o loop de renderização interativo."""
        self.plotter.show()
    
    def close(self):
        """Fecha a janela."""
        self.plotter.close()
    
    def update(self):
        """Atualiza a cena (redraw)."""
        self.plotter.render()
    
    def screenshot(self, filename: str = "screenshot.png"):
        """
        Captura uma screenshot da cena.
        
        Parâmetros:
            filename : nome do arquivo de saída
        """
        self.plotter.screenshot(filename)
        print(f"✓ Screenshot salva em {filename}")
