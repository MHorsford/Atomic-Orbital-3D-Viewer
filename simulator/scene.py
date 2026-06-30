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
    WINDOW_WIDTH, WINDOW_HEIGHT, BG_COLOR, BG_COLOR_HQ,
    SHOW_AXES, SHOW_NUCLEUS, CAMERA_INITIAL_POSITION, CAMERA_FOCAL_POINT,
    COLOR_NUCLEUS, METALLIC, ROUGHNESS, SPECULAR, SPECULAR_POWER
)


class Scene:
    def __init__(self, title: str = "Atomic Orbital Simulator", high_quality: bool = True):
        self.high_quality = high_quality
        self.metallic = METALLIC
        self.roughness = ROUGHNESS
        self.specular = SPECULAR
        self.specular_power = SPECULAR_POWER

        self.plotter = pv.Plotter(
            window_size=(WINDOW_WIDTH, WINDOW_HEIGHT),
            title=title,
            off_screen=False
        )

        # Fundo: preto se alta qualidade, senão azul escuro
        if self.high_quality:
            self.plotter.background_color = BG_COLOR_HQ
        else:
            self.plotter.background_color = BG_COLOR

        self.actors = {}
        self.orbital_meshes = {}

        self._setup_camera()
        # SEMPRE usa o sistema de 3 luzes (não precisamos de custom)
        self.plotter.enable_3_lights()

        if SHOW_AXES:
            self._add_axes()
        if SHOW_NUCLEUS:
            self._add_nucleus_sphere()

    def _setup_camera(self):
        self.plotter.camera.position = CAMERA_INITIAL_POSITION
        self.plotter.camera.focal_point = CAMERA_FOCAL_POINT
        self.plotter.camera.up = (0, 0, 1)
        self.plotter.camera.zoom(0.8)

    def _add_axes(self):
        self.plotter.add_axes(
            xlabel='X', ylabel='Y', zlabel='Z',
            x_color='red', y_color='green', z_color='blue'
        )

    def _add_nucleus_sphere(self):
        nucleus = pv.Sphere(radius=0.2, center=[0,0,0], theta_resolution=20, phi_resolution=20)
        self.plotter.add_mesh(
            nucleus,
            color=COLOR_NUCLEUS,
            opacity=0.9,
            show_edges=False,
            label='Núcleo'
        )
        self.actors['nucleus'] = nucleus

    def set_high_quality(self, high: bool):
        """Alterna entre modos normal e de alta qualidade."""
        from config import BG_COLOR, BG_COLOR_HQ
        self.high_quality = high
        self.plotter.background_color = BG_COLOR_HQ if high else BG_COLOR
        # A iluminação não muda, mas forçamos redesenho
        self.plotter.render()

    # ─── MÉTODO NOVO PARA AJUSTAR A CÂMERA ───

    def set_camera_for_range(self, range_max):
        """Ajusta a câmera para que o orbital caiba na tela."""
        distance = range_max * 2.5   # fator empírico
        self.plotter.camera.position = (distance, distance, distance)
        self.plotter.camera.focal_point = (0, 0, 0)
        self.plotter.camera.up = (0, 0, 1)
        self.plotter.render()

    # ─── MÉTODOS ADICIONAIS (mantidos do seu arquivo original) ───

    def update_orbital_mesh(self, orbital_id: str, mesh, color=None, opacity=None):
        """Atualiza uma malha de orbital já existente na cena."""
        if orbital_id not in self.orbital_meshes:
            print(f"⚠ Orbital {orbital_id} não encontrado na cena")
            return
        old_data = self.orbital_meshes[orbital_id]
        color = color or old_data['color']
        opacity = opacity if opacity is not None else old_data['opacity']
        self.plotter.remove_actor(old_data['actor'])
        self.add_orbital_mesh(mesh, orbital_id, color, opacity)

    def add_orbital_mesh(self, mesh_data, orbital_id: str, color, opacity: float = 0.8, **kwargs):
        extra_kwargs = {
            'smooth_shading': True,
            'show_edges': False,
        }
        if self.high_quality:
            extra_kwargs.update({
                'pbr': True,
                'metallic': self.metallic,
                'roughness': self.roughness,
                'specular': self.specular,
                'specular_power': self.specular_power,
            })
        extra_kwargs.update(kwargs)

        # Se recebermos duas malhas (isossuperfície com fases)
        if isinstance(mesh_data, tuple) and len(mesh_data) == 2:
            mesh_pos, mesh_neg = mesh_data
            
            actor_pos = None
            if mesh_pos is not None and mesh_pos.n_points > 0:
                actor_pos = self.plotter.add_mesh(mesh_pos, color=color, opacity=opacity, **extra_kwargs)
            
            actor_neg = None
            if mesh_neg is not None and mesh_neg.n_points > 0:
                actor_neg = self.plotter.add_mesh(mesh_neg, color='white', opacity=opacity, **extra_kwargs)
                
            self.orbital_meshes[orbital_id] = {
                'mesh': mesh_data,
                'actor': (actor_pos, actor_neg),
                'color': color,
                'opacity': opacity
            }
        else:
            actor = self.plotter.add_mesh(mesh_data, color=color, opacity=opacity, **extra_kwargs)
            self.orbital_meshes[orbital_id] = {
                'mesh': mesh_data,
                'actor': actor,
                'color': color,
                'opacity': opacity
            }

    def remove_orbital_mesh(self, orbital_id: str):
        if orbital_id not in self.orbital_meshes:
            return
        
        data = self.orbital_meshes[orbital_id]
        actors = data['actor']
        
        if isinstance(actors, tuple):
            for act in actors:
                if act is not None:
                    self.plotter.remove_actor(act)
        else:
            if actors is not None:
                self.plotter.remove_actor(actors)
                
        del self.orbital_meshes[orbital_id]

    def clear_orbital_meshes(self):
        for orbital_id in list(self.orbital_meshes.keys()):
            self.remove_orbital_mesh(orbital_id)

    def set_camera_position(self, position, focal_point=None):
        self.plotter.camera.position = position
        if focal_point is not None:
            self.plotter.camera.focal_point = focal_point

    def get_camera_position(self):
        return self.plotter.camera.position

    def reset_camera(self):
        self.set_camera_position(CAMERA_INITIAL_POSITION, CAMERA_FOCAL_POINT)

    def set_background_color(self, color):
        self.plotter.background_color = color

    def show(self):
        self.plotter.show()

    def close(self):
        self.plotter.close()

    def update(self):
        self.plotter.render()

    def screenshot(self, filename: str = "screenshot.png"):
        self.plotter.screenshot(filename)
        print(f"✓ Screenshot salva em {filename}")