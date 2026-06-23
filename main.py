"""
main.py

Ponto de entrada do simulador de orbitais atômicos.
"""

import sys
import os

# Adicionar caminho ao path Python para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import argparse
from atom.atom import Atom
from simulator.simulator import Simulator


def main():
    """Função principal."""
    
    # Argumentos de linha de comando
    parser = argparse.ArgumentParser(
        description='Simulador 3D de Orbitais Atômicos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python main.py                    # Carbono (padrão)
  python main.py --z 1             # Hidrogênio
  python main.py --z 8             # Oxigênio
  python main.py --z 26            # Ferro
  python main.py --z 54 --mode points   # Xenônio com ponto cloud
        """
    )
    
    parser.add_argument(
        '--z', type=int, default=6,
        help='Número atômico (padrão: 6 = Carbono)'
    )
    
    parser.add_argument(
        '--mode', type=str, default='isosurface',
        choices=['isosurface', 'volume', 'points'],
        help='Modo de renderização (padrão: isosurface)'
    )
    
    parser.add_argument(
        '--preset', type=str, default=None,
        help='Carregar um preset (H, He, C, N, O, Ne, Na, Fe)'
    )
    
    parser.add_argument(
        '--title', type=str, default='Atomic Orbital Simulator',
        help='Título da janela'
    )
    
    args = parser.parse_args()
    
    # Validar número atômico
    if args.z < 1 or args.z > 118:
        print(f"❌ Número atômico inválido: {args.z} (deve estar entre 1 e 118)")
        sys.exit(1)
    
    # Criar átomo
    print("🔧 Inicializando simulador...")
    atom = Atom(Z=args.z)
    
    # Criar simulador
    sim = Simulator(atom=atom, title=args.title)
    
    # Configurar modo
    sim.set_render_mode(args.mode)
    
    # Imprimir informações
    print(f"\n{'='*60}")
    print(f"  SIMULADOR DE ORBITAIS ATÔMICOS")
    print(f"{'='*60}")
    print(f"\n{atom.get_element_name()} (Z={atom.Z})")
    print(f"Configuração: {atom.get_electron_config()}")
    print(f"Elétrons de valência: {atom.get_valence_electrons()}")
    print(f"\nModo: {sim.renderer.mode}")
    print(f"\n{'='*60}\n")
    
    # Executar
    try:
        sim.run()
    except KeyboardInterrupt:
        print("\n⚙️  Encerrando...")
    finally:
        sim.close()


if __name__ == "__main__":
    main()