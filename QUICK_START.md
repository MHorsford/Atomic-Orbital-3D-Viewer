# ⚡ Quick Start — Renderização de Orbitais

## Instalação

```bash
# Clonar/baixar os arquivos

# Instalar dependências
pip install -r requirements.txt

# Rodar com padrão (Carbono)
python main.py

# Ou com opções
python main.py --z 8 --mode isosurface
python main.py --z 26 --mode points
python main.py --z 1 --mode volume
```

---

## Exemplos de Código

### 1️⃣ Exemplo Mínimo

```python
from atom.atom import Atom
from simulator_simulator import Simulator

# Criar e renderizar Oxigênio
atom = Atom(Z=8)
sim = Simulator(atom)
sim.run()
```

### 2️⃣ Com Modo de Renderização

```python
from atom.atom import Atom
from simulator_simulator import Simulator

atom = Atom(Z=6)  # Carbono
sim = Simulator(atom)

# Escolher modo
sim.set_render_mode('isosurface')  # ou 'volume' ou 'points'

sim.run()
```

### 3️⃣ Mudar Elemento (Dinâmico)

```python
sim = Simulator(Atom(Z=1))
sim.run()

# ... enquanto rodando ...
# Depois mudar para outro elemento:
sim.set_atom_z(8)  # Oxigênio agora
sim.set_render_mode('points')
```

### 4️⃣ Usar Presets

```python
from atom_presets import load_preset
from simulator_simulator import Simulator

# Carregar preset (disponíveis: H, He, C, N, O, Ne, Na, Fe, ...)
atom = load_preset('Fe')  # Ferro

sim = Simulator(atom)
sim.set_render_mode('volume')
sim.run()
```

### 5️⃣ Capturar Screenshot

```python
atom = Atom(Z=8)
sim = Simulator(atom)

sim.set_render_mode('isosurface')
sim.screenshot('oxigenio_iso.png')

sim.close()
```

### 6️⃣ Ajustar Parâmetros de Renderização

```python
sim = Simulator(Atom(Z=6))

# Isosurface
sim.set_render_mode('isosurface')
sim.set_iso_value(0.05)  # 5% do máximo (padrão: 2%)
sim.set_grid_resolution(100)  # Mais refinado, mais lento

# Ou: Point cloud
sim.set_render_mode('points')
sim.renderer.set_point_cloud_size(50000)  # Mais denso

sim.run()
```

### 7️⃣ Informações do Elemento

```python
atom = Atom(Z=26)

print(f"Nome: {atom.get_element_name()}")          # Ferro
print(f"Símbolo: {atom.get_element_symbol()}")     # Fe
print(f"Config: {atom.get_electron_config()}")     # 1s² 2s² 2p⁶ ...
print(f"Valência: {atom.get_valence_electrons()}")  # 8
print(f"Total elétrons: {atom.N_electrons}")       # 26
```

### 8️⃣ Loop Manual (sem `run()`)

```python
from atom.atom import Atom
from simulator_simulator import Simulator
import time

sim = Simulator(Atom(Z=6))

# Renderizar por 10 segundos
start = time.time()
while time.time() - start < 10:
    sim.step(dt=0.016)  # 60 FPS

sim.close()
```

### 9️⃣ Comparar Elementos

```python
from atom.atom import Atom
from simulator_simulator import Simulator

elementos = [
    (1, "Hidrogênio"),
    (6, "Carbono"),
    (8, "Oxigênio"),
    (26, "Ferro"),
]

for z, nome in elementos:
    print(f"\n{'='*40}")
    print(f"  {nome} (Z={z})")
    print(f"{'='*40}")
    
    atom = Atom(Z=z)
    sim = Simulator(atom, title=f"{nome} - Renderizador 3D")
    
    sim.set_render_mode('isosurface')
    sim.screenshot(f'elemento_{nome.lower()}.png')
    
    print(f"Config: {atom.get_electron_config()}")
    sim.close()

print(f"\n✓ Screenshots salvos!")
```

### 🔟 Renderizar Múltiplas Vistas

```python
atom = Atom(Z=8)  # Oxigênio
sim = Simulator(atom)
sim.set_render_mode('points')

# Vista 1: Default
sim.scene.set_camera_position((15, 15, 15))
sim.screenshot('oxigenio_vista1.png')

# Vista 2: De cima
sim.scene.set_camera_position((0, 0, 20))
sim.screenshot('oxigenio_vista2.png')

# Vista 3: De lado
sim.scene.set_camera_position((20, 0, 0))
sim.screenshot('oxigenio_vista3.png')

sim.close()
```

---

## Atalhos na Visualização

Quando a janela 3D está aberta:

| Ação | Tecla/Mouse |
|------|-----------|
| **Rotacionar** | Arrastar com mouse |
| **Zoom in/out** | Scroll |
| **Reset câmera** | **R** ou **Home** |
| **Sair** | **Q** ou fechar janela |

---

## Trocar Modos de Renderização

```python
# Modo 1: ISOSURFACE (padrão, mais rápido)
sim.set_render_mode('isosurface')
sim.set_iso_value(0.02)  # Quanto menor, mais próximo do núcleo

# Modo 2: VOLUME (mais realista)
sim.set_render_mode('volume')

# Modo 3: POINTS (mais imersivo)
sim.set_render_mode('points')
sim.renderer.set_point_cloud_size(20000)  # Default: 10000
```

---

## Dicas de Performance

| Ação | Impacto |
|------|--------|
| Aumentar `grid_size` | ⬆️ Qualidade, ⬇️ Velocidade |
| Usar `isosurface` | ⬆️ Velocidade |
| Usar `points` | ⬇️ Velocidade, ⬆️ Visualização |
| Reduzir Z | ⬆️ Velocidade (menos elétrons) |

---

## Elementos Recomendados para Testar

```python
# Simples (rápido)
load_preset('H')   # Hidrogênio - 1 elétron
load_preset('He')  # Hélio - 2 elétrons
load_preset('C')   # Carbono - 6 elétrons

# Intermediário
load_preset('O')   # Oxigênio - 8 elétrons
load_preset('Ne')  # Neônio - 10 elétrons (camada fechada!)
load_preset('Na')  # Sódio - 11 elétrons

# Complexo (mais lento, mas interessante)
load_preset('Fe')  # Ferro - 26 elétrons (transição d)
load_preset('Cu')  # Cobre - 29 elétrons
load_preset('Ag')  # Prata - 47 elétrons
```

---

## Estrutura de Arquivos

Depois de rodar, você terá:

```
seu_diretorio/
├── config.py                  # ← EDITAR para customizar
├── main.py
├── atom/
│   ├── atom.py               # (já fornecido)
│   ├── atom_presets.py       # ← NOVO
│   └── ...
├── simulator/
│   ├── simulator.py           # ← NOVO (orquestrador)
│   ├── scene.py              # ← NOVO (cena PyVista)
│   ├── renderer.py           # ← NOVO (conversor 3D)
│   └── ...
├── utils/
│   ├── utils_grid.py         # ← NOVO
│   ├── utils_sampling.py     # ← NOVO
│   ├── utils_helpers.py      # ← NOVO
│   └── ...
├── requirements.txt
├── RENDERING_GUIDE.md         # ← LEIA ISTO
└── QUICK_START.md            # ← VOCÊ ESTÁ AQUI
```

---

## Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| Isosurface vazia | `sim.set_iso_value(0.01)` |
| Muito lento | `sim.set_grid_resolution(50)` |
| Janela não abre | `export DISPLAY=:0` (Linux) |

---

## Próximo Passo

Leia `RENDERING_GUIDE.md` para documentação completa!

---

**Divirta-se visualizando orbitais! 🚀**
