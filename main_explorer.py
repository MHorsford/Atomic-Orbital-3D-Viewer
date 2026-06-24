"""
main_explorer.py

Ponto de entrada para o Orbital Explorer — UI interativa com sliders.
Permite explorar qualquer orbital do hidrogênio com controles visuais.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


from atom.atom import Atom
from simulator.simulator import Simulator
from ui.orbital_explorer import launch_explorer
from config import HIGH_QUALITY_RENDER

def main():
    print("=" * 70)
    print("  🧪 ORBITAL EXPLORER — Simulador Interativo de Orbitais")
    print("=" * 70)
    print("\nIniciando simulador...")

    # Criar átomo (padrão: Hidrogênio)
    atom = Atom(Z=1)

    # Criar simulador com a flag de qualidade
    sim = Simulator(atom=atom, title="Orbital Explorer — 3D Interactive", high_quality=HIGH_QUALITY_RENDER)
    sim.set_render_mode('isosurface')

    # A UI será aberta e o plotter será mostrado separadamente
    print(f"✓ Simulador criado: {atom.get_element_name()}")
    print("✓ Abrindo UI interativa...")

    # Lançar UI (isso cria o QApplication e a janela)
    app, explorer = launch_explorer(sim)

    # Mostrar a janela 3D (PyVista) de forma não-bloqueante
    # Use show(interactive_update=True) para permitir que o Qt rode junto
    sim.scene.plotter.show(interactive_update=True)

    # Agora executa o loop do Qt (a janela 3D já está aberta)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()