# 🎨 Guia de Renderização — Simulador de Orbitais Atômicos

## Visão Geral

A camada de renderização converte dados quânticos (funções de onda `ψ`) em geometria 3D interativa usando **PyVista**.

### Arquitetura

```
Atom (modelo)
    ↓
Orbital (com funções de onda)
    ↓
Renderer (converte psi² em mesh)
    ↓
Scene (gerencia PyVista Plotter)
    ↓
Visualização 3D Interativa
```

---

## Componentes Principais

### 1. **Renderer** (`simulator/renderer.py`)

Converte orbitais em malhas 3D. Suporta **3 modos**:

#### A) **Isosurface** (padrão)
- Renderiza uma superfície de probabilidade constante
- Usa **contour plots** em grid 3D
- **Rápido** e **elegante**
- Melhor para: visualizar formato dos orbitais

```python
sim.set_render_mode('isosurface')
sim.set_iso_value(0.1)  # 10% do máximo
```

#### B) **Volume** (Volumétrico)
- Renderiza como nuvem de pontos colorida
- Densidade = cor
- Mostra distribuição real de probabilidade
- **Mais lento**, mais realista

```python
sim.set_render_mode('volume')
```

#### C) **Points** (Nuvem Monte Carlo)
- Amostragem estocástica de |ψ|²
- Cada ponto representa possível posição do elétron
- **Mais imersivo** visualmente
- Padrão: 10.000 pontos

```python
sim.set_render_mode('points')
sim.renderer.set_point_cloud_size(50000)  # mais denso
```

---

### 2. **Scene** (`simulator/scene.py`)

Gerencia a cena 3D:

#### Câmera
```python
# Posição inicial
sim.scene.set_camera_position((15, 15, 15))

# Resetar
sim.scene.reset_camera()
```

#### Iluminação
- Luz ambiente: 30% de intensidade
- Luz direcional: 80% de intensidade
- Eixos X (vermelho), Y (verde), Z (azul)

#### Captura de Screenshots
```python
sim.screenshot('orbital_1s.png')
```

---

### 3. **Simulator** (`simulator/simulator.py`)

Orquestrador — conecta modelo, renderização e UI:

```python
from atom.atom import Atom
from simulator_simulator import Simulator

# Criar átomo (ex: Oxigênio)
atom = Atom(Z=8)

# Criar simulador
sim = Simulator(atom=atom)

# Mudar modo de renderização
sim.set_render_mode('isosurface')

# Mudar elemento
sim.set_atom_z(26)  # Ferro

# Executar
sim.run()
```

---

## Uso Via Linha de Comando

### Exemplo 1: Hidrogênio (padrão - isosurface)
```bash
python main.py --z 1
```

### Exemplo 2: Carbono com ponto cloud
```bash
python main.py --z 6 --mode points
```

### Exemplo 3: Ferro com renderização volumétrica
```bash
python main.py --z 26 --mode volume
```

### Exemplo 4: Xenônio (Z=54)
```bash
python main.py --z 54 --title "Xenônio 3D"
```

---

## Uso Via Código

### Setup Básico
```python
from atom.atom import Atom
from simulator_simulator import Simulator

# Criar átomo
atom = Atom(Z=6)  # Carbono

# Criar simulador
sim = Simulator(atom=atom)

# Renderizar
sim.run()
```

### Controlar Renderização
```python
# Mudar modo
sim.set_render_mode('points')

# Ajustar isosurface (apenas para 'isosurface')
sim.set_iso_value(0.05)  # 5% do máximo

# Mudar resolução de grid
sim.set_grid_resolution(100)  # mais refinado, mais lento

# Mudar número de pontos (apenas para 'points')
sim.renderer.set_point_cloud_size(20000)
```

### Mudar Elemento Dinamicamente
```python
# Começar com Hidrogênio
sim = Simulator(Atom(Z=1))
sim.run()

# Depois, mudar para Oxigênio
sim.set_atom_z(8)
```

### Usar Presets
```python
from atom_presets import load_preset

# Carregar um preset
atom = load_preset('Fe')  # Ferro

# Criar simulador com esse átomo
sim = Simulator(atom=atom)
sim.run()
```

---

## Parâmetros de Configuração

Todos em `config.py`:

### Renderização
```python
GRID_SIZE = 80              # Pontos por dimensão (20-150)
GRID_RANGE = 8.0            # Extensão em Bohr (±8 a.u.)
ISO_VALUE = 0.02            # Isosurface = 2% do máximo
NUM_POINTS_CLOUD = 10000    # Pontos para mode='points'
```

### Visualização
```python
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
FPS_TARGET = 30

BG_COLOR = (0.05, 0.05, 0.08)  # Azul muito escuro
ORBITAL_OPACITY_ISO = 0.8
ORBITAL_OPACITY_VOLUME = 0.5
```

### Câmera
```python
CAMERA_INITIAL_POSITION = (15, 15, 15)
CAMERA_FOCAL_POINT = (0, 0, 0)
```

---

## Controles Interativos (PyVista)

Na janela 3D:

| Ação | Controle |
|------|----------|
| Rotacionar câmera | **Mouse (arrastar)** |
| Zoom | **Scroll ou pinch** |
| Mover câmera | **Shift + Mouse** |
| Reset câmera | **Home** ou **r** |
| Sair | **q** ou fechar janela |

---

## Algoritmos de Renderização

### 1. Isosurface (Marching Cubes)

```
1. Calcular |ψ|² em grid 3D (80³ pontos padrão)
2. Definir valor de isosurface: iso = ISO_VALUE * max(|ψ|²)
3. Usar contour plot para extrair superfície
4. Calcular normais para iluminação
5. Renderizar malha
```

**Complexidade**: O(n³) onde n = GRID_SIZE
**Tempo típico**: 100-500ms para n=80

### 2. Volume (Point Cloud com Densidade)

```
1. Calcular |ψ|² em grid reduzido (40³)
2. Criar ponto para cada célula do grid
3. Colorir por densidade: cor ∝ |ψ|²
4. Renderizar como ponto cloud
```

**Complexidade**: O(n³)
**Tempo típico**: 50-200ms

### 3. Monte Carlo Sampling

```
1. Definir função psi_squared(x, y, z)
2. Usar rejection sampling:
   - Gerar ponto aleatório no cubo
   - Aceitar com prob ∝ |ψ|²
3. Repetir até ter N_POINTS pontos
4. Renderizar como malha de vértices
```

**Complexidade**: O(N × tentativas)
**Tempo típico**: 500-2000ms para N=10000

---

## Troubleshooting

### ❌ "Module not found"
```bash
pip install -r requirements.txt
```

### ❌ Isosurface vazia
- Aumentar `GRID_RANGE`
- Diminuir `ISO_VALUE`
- Aumentar `GRID_SIZE` (mais lento)

### ❌ Renderização lenta
- Diminuir `GRID_SIZE`
- Usar modo 'points' em vez de 'isosurface'
- Reduzir `NUM_POINTS_CLOUD`

### ❌ PyVista não abre janela (Linux)
```bash
# Pode ser necessário:
export DISPLAY=:0
python main.py --z 6
```

---

## Exemplos Avançados

### Renderizar todos os elementos da primeira linha
```python
from atom.atom import Atom
from simulator_simulator import Simulator

for Z in range(1, 11):  # H até Ne
    atom = Atom(Z=Z)
    sim = Simulator(atom)
    sim.screenshot(f'element_z{Z:02d}.png')
    sim.close()
```

### Comparar dois modos
```python
atom = Atom(Z=8)

# Modo 1: Isosurface
sim = Simulator(atom, title="Oxigênio - Isosurface")
sim.set_render_mode('isosurface')
sim.screenshot('O_iso.png')
sim.close()

# Modo 2: Points
sim = Simulator(atom, title="Oxigênio - Point Cloud")
sim.set_render_mode('points')
sim.screenshot('O_points.png')
sim.close()
```

### Animar mudança de Z
```python
from atom.atom import Atom
from simulator_simulator import Simulator
import time

sim = Simulator(Atom(Z=1))
sim.set_render_mode('points')

# Animar de Z=1 a Z=18
for Z in range(1, 19):
    print(f"Renderizando Z={Z}...")
    sim.set_atom_z(Z)
    sim.screenshot(f'animation_frame_{Z:02d}.png')
    time.sleep(0.5)

sim.close()

# Depois convertê-los em vídeo:
# ffmpeg -framerate 2 -i animation_frame_%02d.png output.mp4
```

---

## Performance

### Benchmarks (MacBook Pro, 2019)

| Modo | Z=1 | Z=6 | Z=26 | Z=54 |
|------|-----|-----|------|------|
| Isosurface | 80ms | 120ms | 250ms | 400ms |
| Volume | 50ms | 80ms | 150ms | 250ms |
| Points (10k) | 800ms | 1200ms | 2000ms | 3000ms |

---

## Estrutura de Arquivos da Renderização

```
.
├── config.py                    # Configurações globais
├── simulator/
│   ├── simulator.py            # Orquestrador
│   ├── scene.py                # Gerenciador de cena PyVista
│   └── renderer.py             # Conversor orbital → mesh
├── utils/
│   ├── grid.py                 # Grid 3D e conversões esféricas
│   ├── sampling.py             # Amostragem Monte Carlo
│   └── helpers.py              # Funções auxiliares
└── main.py                     # Ponto de entrada
```

---

## Próximos Passos

- [ ] Adicionar UI com sliders (PyQt5)
- [ ] Exportar malhas para formatos 3D (OBJ, STL)
- [ ] Raycasting volumétrico em tempo real (GLSL shaders)
- [ ] Animação de transições eletrônicas
- [ ] Realidade aumentada (ARKit/ARCore)

---

**Criado com 🧪 para visualizar a beleza da mecânica quântica!**
