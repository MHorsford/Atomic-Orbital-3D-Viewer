"""
simulator/simulator.py

Classe Simulator — orquestrador geral.
Conecta o modelo atômico (Atom) com a renderização (Scene + Renderer).
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
from config import FPS_TARGET
from simulator.scene import Scene
from simulator.renderer import Renderer
from utils.helpers import orbital_info_string, element_info_string


class Simulator:
    """
    Orquestrador principal do simulador.
    Gerencia o loop de simulação e atualização da cena.
    """
    
    def __init__(self, atom=None, title: str = "Atomic Orbital Simulator"):
        """
        Parâmetros:
            atom  : objeto Atom (criado aqui se None)
            title : título da janela
        """
        if atom is None:
            from atom.atom import Atom
            atom = Atom(Z=6)  # Padrão: Carbono
        
        self.atom = atom
        self.scene = Scene(title=title)
        self.renderer = Renderer()
        
        # Estado do simulador
        self.is_running = False
        self.frame_count = 0
        self.last_update_time = time.time()
        self.fps = 0
        
        # Orbitais visíveis (por padrão, mostrar todos com elétrons)
        self.visible_orbitals = {}
        
        # Inicializar renderização
        self._initialize_rendering()
    
    def _initialize_rendering(self):
        """Renderiza o estado inicial do átomo."""
        self.update_atom_display()
    
    def update_atom_display(self):
        """
        Atualiza a renderização para o estado atual do átomo.
        Chamado quando o número atômico ou configuração muda.
        """
        # Limpar orbitais antigos
        self.scene.clear_orbital_meshes()
        self.visible_orbitals.clear()
        
        # Renderizar núcleo
        nucleus_mesh = self.renderer.render_nucleus(self.atom.nucleus)
        self.scene.add_orbital_mesh(nucleus_mesh, 'nucleus', (0.95, 0.7, 0.1), 0.9)
        
        # Renderizar cada orbital com elétrons
        for i, orbital in enumerate(self.atom.orbitals):
            if orbital.electrons > 0:
                orbital_id = f"{orbital.n}{chr(97+orbital.l)}_{orbital.m}"
                
                # Renderizar malha do orbital
                mesh = self.renderer.render_orbital(orbital)
                
                # Usar cor do tipo de orbital
                color = orbital.color
                opacity = 0.7 if orbital.electrons == 2 else 0.5
                
                self.scene.add_orbital_mesh(mesh, orbital_id, color, opacity)
                self.visible_orbitals[orbital_id] = orbital
    
    def set_atom_z(self, Z: int):
        """
        Muda o número atômico do átomo.
        
        Parâmetros:
            Z : novo número atômico
        """
        if Z < 1 or Z == self.atom.Z:
            return
        
        # Reconstruir átomo
        from atom.atom import Atom
        self.atom = Atom(Z=Z)
        
        # Atualizar renderização
        self.update_atom_display()
        print(f"✓ Átomo atualizado: {element_info_string(self.atom)}")
    
    def set_render_mode(self, mode: str):
        """
        Muda o modo de renderização.
        
        Parâmetros:
            mode : 'isosurface', 'volume', ou 'points'
        """
        self.renderer.set_mode(mode)
        self.update_atom_display()
    
    def set_iso_value(self, iso_value: float):
        """
        Ajusta o valor de isosurface (apenas para modo isosurface).
        
        Parâmetros:
            iso_value : valor entre 0 e 1
        """
        self.renderer.set_iso_value(iso_value)
        if self.renderer.mode == 'isosurface':
            self.update_atom_display()
    
    def set_grid_resolution(self, size: int):
        """
        Ajusta a resolução do grid de cálculo.
        
        Parâmetros:
            size : número de pontos por dimensão (20-150)
        """
        self.renderer.set_grid_resolution(size)
        self.update_atom_display()
    
    def toggle_orbital_visibility(self, orbital_id: str):
        """
        Alterna a visibilidade de um orbital.
        
        Parâmetros:
            orbital_id : identificador do orbital (ex: "1s", "2p_z")
        """
        if orbital_id in self.visible_orbitals:
            self.scene.remove_orbital_mesh(orbital_id)
            del self.visible_orbitals[orbital_id]
            print(f"✗ Orbital {orbital_id} ocultado")
        elif orbital_id == 'all':
            self.scene.clear_orbital_meshes()
            self.visible_orbitals.clear()
            print("✗ Todos os orbitais ocultados")
    
    def show_all_orbitals(self):
        """Mostra todos os orbitais preenchidos."""
        self.update_atom_display()
        print(f"✓ {len(self.visible_orbitals)} orbitais visíveis")
    
    def reset_camera(self):
        """Reseta a câmera para posição inicial."""
        self.scene.reset_camera()
    
    def screenshot(self, filename: str = "screenshot.png"):
        """
        Captura uma screenshot.
        
        Parâmetros:
            filename : nome do arquivo
        """
        self.scene.screenshot(filename)
    
    def run(self):
        """Inicia o loop principal de renderização."""
        self.is_running = True
        print("🟢 Simulador iniciado")
        print(f"   Elemento: {element_info_string(self.atom)}")
        print(f"   Modo: {self.renderer.mode}")
        print("\nControles interativos:")
        print("  - Mouse: rotacionar câmera")
        print("  - Scroll: zoom")
        print("  - 'r': reset câmera")
        print("  - 'q': sair")
        
        self.scene.show()
        self.is_running = False
    
    def step(self, dt: float = 0.016):
        """
        Executa um passo de simulação.
        
        Parâmetros:
            dt : tempo decorrido em segundos
        """
        self.frame_count += 1
        
        # Calcular FPS
        current_time = time.time()
        elapsed = current_time - self.last_update_time
        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.last_update_time = current_time
        
        # Atualizar cena
        self.scene.update()
    
    def close(self):
        """Fecha o simulador e libera recursos."""
        self.scene.close()
        self.is_running = False
        print("🔴 Simulador encerrado")
    
    def get_info_string(self) -> str:
        """Retorna uma string com informações do simulador."""
        info = f"{element_info_string(self.atom)}\n"
        info += f"Modo: {self.renderer.mode}\n"
        info += f"Orbitais visíveis: {len(self.visible_orbitals)}\n"
        info += f"FPS: {self.fps:.1f}"
        return info