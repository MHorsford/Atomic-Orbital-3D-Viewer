# Simulador Tridimensional de Orbitais Atômicos
> Física para Computação — Modelo Quântico Mecânico

---

## Estrutura de diretórios

```
atomic_orbital_simulator/
├── main.py
├── config.py
├── requirements.txt
├── data/
│   └── periodic_table.csv
├── particles/
│   ├── __init__.py
│   ├── particle.py
│   ├── proton.py
│   ├── neutron.py
│   └── electron.py
├── nucleus/
│   ├── __init__.py
│   └── nucleus.py
├── orbitals/                  ← módulo mais crítico
│   ├── __init__.py
│   ├── wavefunction.py
│   ├── orbital.py
│   └── orbital_types.py
├── atom/
│   ├── __init__.py
│   ├── atom.py
│   └── presets.py
├── simulator/                 ← reestruturado
│   ├── __init__.py
│   ├── simulator.py
│   ├── scene.py
│   └── renderer.py
├── ui/                        ← reestruturado
│   ├── __init__.py
│   ├── controls.py
│   ├── controller.py
│   └── styles.py
├── physics/                   ← ampliado
│   ├── __init__.py
│   ├── constants.py
│   ├── coulomb.py
│   └── screening.py
├── utils/
│   ├── __init__.py
│   ├── grid.py
│   ├── sampling.py
│   └── helpers.py
└── tests/
    ├── test_wavefunction.py
    └── test_atom.py
```

---

## Descrição detalhada de cada arquivo

### Raiz

**`main.py`**
Ponto de entrada da aplicação. Instancia o `Atom` (com o número atômico inicial), passa para o `Simulator`, inicializa a cena 3D e dispara o loop principal de renderização. Toda a sequência de boot fica aqui: lê config, cria objetos na ordem certa, abre a janela.

**`config.py`**
Configurações globais que qualquer módulo pode importar sem criar dependência circular. Inclui: resolução do grid (ex. `GRID_SIZE = 80`), valor de isosurface padrão (ex. `ISO_VALUE = 0.02`), tamanho do átomo na cena, paleta de cores dos orbitais, raio visual de prótons/nêutrons, FPS alvo.

**`requirements.txt`**
```
numpy
scipy
pyvista
pyvistaqt
PyQt5
pandas
```

---

### `data/`

**`periodic_table.csv`**
Tabela com uma linha por elemento. Colunas mínimas necessárias: `Z` (número atômico), `symbol`, `name`, `mass`, `electron_config` (ex. `"1s2 2s2 2p6"`). O `nucleus.py` e o `atom.py` consultam esse arquivo para identificar o elemento e validar a configuração eletrônica.

---

### `particles/`

**`particle.py`**
Classe base abstrata `Particle`. Atributos comuns: `position: np.ndarray`, `mass: float`, `charge: float`, `color: str`, `radius: float`. Não instanciar diretamente — serve só de contrato para as subclasses.

**`proton.py`**
Classe `Proton(Particle)`. Define `charge = +1.602e-19`, `mass = 1.673e-27`, `color = "#E55"`, `radius` visual padrão. Sem lógica adicional — é um dado com identidade.

**`neutron.py`**
Classe `Neutron(Particle)`. Define `charge = 0`, `mass = 1.675e-27`, `color = "#888"`. Mesmo padrão do próton.

**`electron.py`**
Classe `Electron(Particle)`. Define `charge = -1.602e-19`, `mass = 9.109e-31`. O elétron no modelo quântico não tem posição definida — essa classe representa a partícula como entidade (usada pelo `Orbital`), não como ponto no espaço.

---

### `nucleus/`

**`nucleus.py`**
Classe `Nucleus`. Guarda listas de `Proton` e `Neutron`. Calcula e expõe `Z` (número atômico = len(protons)) e `A` (número de massa = Z + len(neutrons)). Método `identify_element()` consulta `periodic_table.csv` e retorna símbolo e nome com base em `Z`. Método `add_proton()` e `remove_proton()` disparam recálculo automático de Z.

---

### `orbitals/` — módulo mais crítico

**`wavefunction.py`**
Implementa as funções de onda hidrogenoides ψ(n, l, m, r, θ, φ) e a densidade de probabilidade |ψ|². Usa obrigatoriamente `scipy.special.sph_harm` para os harmônicos esféricos Y_l^m e `scipy.special.genlaguerre` para os polinômios de Laguerre associados L_n^k. Não reimplementar essas funções na mão — a precisão numérica nos orbitais d e f depende disso. Função principal: `psi_squared(n, l, m, r, theta, phi) -> float`, que retorna a densidade de probabilidade num ponto do espaço.

**`orbital.py`**
Classe `Orbital`. Atributos: `n` (nível), `l` (subnível: 0=s, 1=p, 2=d, 3=f), `m_l` (número magnético), `electrons: int` (0, 1 ou 2), `color: str`, `visible: bool`. Método `probability_density(r, theta, phi)` delega para `wavefunction.psi_squared`. Método `get_label()` retorna string legível como `"2p_x"`.

**`orbital_types.py`**
Dicionário/configuração estática com metadados dos tipos de orbital. Para cada tipo (s, p, d, f): capacidade máxima de elétrons, número de orbitais no subnível, cor padrão, descrição textual. Exemplo: `"p": {"max_electrons": 6, "count": 3, "color": "#4AF", "desc": "lobes along axes"}`. Usado por `atom.py` ao montar a configuração eletrônica.

---

### `atom/`

**`atom.py`**
Classe `Atom` — coração do simulador. Compõe um `Nucleus` e uma lista de `Orbital`. Método `build(Z: int)`: lê `periodic_table.csv`, cria o núcleo com Z prótons, preenche os orbitais seguindo a regra de Aufbau (ordem crescente de energia: 1s → 2s → 2p → 3s → 3p → 4s → 3d...), aplica a regra de Hund (maximiza spin antes de parear) e o Princípio de Pauli (max 2 elétrons por orbital). Método `add_proton()` incrementa Z e rechama `build()`. Método `get_electron_config()` retorna string no formato `"1s² 2s² 2p⁶"`.

**`presets.py`**
Configurações pré-prontas de átomos para testes rápidos e demonstrações. Dicionário com elementos comuns: H (Z=1), He (Z=2), C (Z=6), N (Z=7), O (Z=8), Ne (Z=10), Na (Z=11), Fe (Z=26). Função `load_preset(symbol: str) -> Atom` retorna um `Atom` já construído e pronto para renderizar. Antes estava em `visualizations/presets.py` — foi movido para cá porque presets são dados de domínio atômico, não de visualização.

---

### `simulator/` — reestruturado em três arquivos

**`simulator.py`**
Classe `Simulator` — orquestrador geral. Recebe um `Atom` e conecta os outros módulos. Gerencia o loop principal: a cada tick, verifica se o estado do átomo mudou (via `controller`), chama `scene.update()` e `renderer.render()`. Não contém lógica de renderização nem de cena — só coordena.

**`scene.py`**
Classe `Scene`. Encapsula o `pyvista.Plotter`: cria a janela, configura luz e câmera, gerencia os objetos 3D presentes na cena (núcleo, nuvem de probabilidade, eixos). Método `add_mesh(mesh, color, opacity)`, `clear()`, `set_camera(position)`. Separado de `renderer.py` para que a lógica de câmera e luz não se misture com a lógica de cálculo de malhas.

**`renderer.py`**
Classe `Renderer`. Recebe um `Orbital` e um grid 3D de densidades (vindo de `grid.py` + `wavefunction.py`) e produz a malha PyVista correspondente. Três modos: `isosurface(iso_val)` — superfície de probabilidade constante; `volume()` — renderização volumétrica com opacidade proporcional a |ψ|²; `point_cloud(n_points)` — nuvem de pontos amostrada via Monte Carlo (`sampling.py`). Retorna um `pyvista.PolyData` que `scene.py` adiciona à cena.

---

### `ui/` — reestruturado com mediador

**`controls.py`**
Widgets visuais puros: slider de número atômico (Z), slider de nível energético (n), botões de modo de renderização (iso/volume/cloud), toggle de visibilidade por orbital, painel de informações do elemento. Não chama nada do domínio diretamente — emite sinais/callbacks que `controller.py` intercepta.

**`controller.py`**
Classe `Controller` — arquivo novo. Faz a ponte entre a UI e o domínio. Quando o slider de Z muda, `controller` chama `atom.build(new_Z)`, notifica `simulator` para atualizar a cena e atualiza os labels da UI com a nova configuração eletrônica. Sem esse mediador, `controls.py` ficaria acoplado diretamente a `Atom` e `Simulator`, tornando difícil testar e alterar qualquer um dos dois.

**`styles.py`**
Paleta de cores, temas visuais (dark/light), tamanhos de fonte, espaçamentos. Define constantes usadas por `controls.py` para manter consistência visual.

---

### `physics/` — ampliado

**`constants.py`**
Constantes físicas em SI e em unidades atômicas. Inclui: `A0 = 5.292e-11` (raio de Bohr em metros), `E_CHARGE = 1.602e-19`, `M_ELECTRON = 9.109e-31`, `HBAR = 1.055e-34`, `K_COULOMB = 8.988e9`. Importado por `wavefunction.py` e `coulomb.py`.

**`coulomb.py`**
Funções para calcular força eletrostática entre partículas (`coulomb_force(q1, q2, r)`) e energia de ionização aproximada. Funcionalidade bônus — não é necessária para a visualização dos orbitais, mas enriquece o projeto com física real.

**`screening.py`**
Arquivo novo. Implementa as regras de screening de Slater para átomos multieletrônicos. A função `slater_screening(Z, n, l)` retorna a carga nuclear efetiva Z* que um elétron no nível (n, l) enxerga, descontando o efeito de blindagem dos outros elétrons. Necessário para que os orbitais de He, C, O etc. tenham tamanhos fisicamente plausíveis (sem isso, todos os átomos usam as funções de onda do hidrogênio com Z=1, o que superestima muito o tamanho dos orbitais internos).

---

### `utils/`

**`grid.py`**
Funções para gerar grids 3D cartesianos e convertê-los para coordenadas esféricas (r, θ, φ). Função principal: `make_grid(size, resolution) -> (X, Y, Z, R, THETA, PHI)` — retorna arrays numpy prontos para serem passados a `wavefunction.psi_squared`. O parâmetro `resolution` controla o trade-off entre qualidade visual e tempo de cálculo.

**`sampling.py`**
Amostragem Monte Carlo para gerar nuvens de pontos probabilísticas. Função `sample_orbital(orbital, n_points) -> np.ndarray`: amostra `n_points` posições no espaço com probabilidade proporcional a |ψ(r, θ, φ)|². Usa rejection sampling: gera pontos aleatórios no cubo, aceita com probabilidade `psi_sq / psi_max`. Retorna array (N, 3) com coordenadas cartesianas dos pontos aceitos.

**`helpers.py`**
Funções auxiliares gerais: `spherical_to_cartesian(r, theta, phi)`, `cartesian_to_spherical(x, y, z)`, `normalize_array(arr)` (normaliza para [0, 1]), `quantum_label(n, l, m)` (retorna string como `"3d_z²"`).

---

### `tests/`

**`test_wavefunction.py`**
Testa `wavefunction.psi_squared` para os orbitais conhecidos. Verificações: valor em r=0 para orbitais s (deve ser não-nulo), valor em r=0 para orbitais p (deve ser zero), normalização (integral de |ψ|² sobre o espaço deve ser ≈ 1.0), simetria dos orbitais p (psi(x) = -psi(-x)). Use `scipy.integrate.quad` para as integrais de teste.

**`test_atom.py`**
Testa `atom.build(Z)` para elementos conhecidos. Verificações: H (Z=1) → 1 elétron em 1s; C (Z=6) → config `1s² 2s² 2p²` com 2 orbitais 2p semi-preenchidos (regra de Hund); Ne (Z=10) → camada completa; número total de elétrons igual a Z para todo elemento testado.

---

## Ordem de implementação recomendada

1. `physics/constants.py` — nenhuma dependência, define a base numérica
2. `utils/` — grid, sampling e helpers; testáveis de forma isolada
3. `particles/` e `nucleus/` — estrutura de dados simples
4. `orbitals/wavefunction.py` — o coração matemático; testar com `test_wavefunction.py` antes de continuar
5. `orbitals/orbital.py` e `orbital_types.py` — encapsulam os resultados de wavefunction
6. `atom/atom.py` e `atom/presets.py` — integra tudo; testar com `test_atom.py`
7. `simulator/scene.py` e `simulator/renderer.py` — primeira visualização 3D
8. `ui/controls.py` e `ui/controller.py` — interface interativa
9. `physics/screening.py` e `physics/coulomb.py` — refinamentos físicos

---

## Dependências entre módulos

```
constants ──► wavefunction ──► orbital ──► atom ──► simulator ──► scene
                                                          │
grid ────────────────────────────────────────────► renderer ◄── sampling
                                                          │
                                                         ui ◄── controller
```

---

## Como rodar

```bash
pip install -r requirements.txt
python main.py
```

Para carregar um preset diretamente:

```python
from atom.presets import load_preset
from simulator.simulator import Simulator

atom = load_preset("O")   # Oxigênio, Z=8
sim = Simulator(atom)
sim.run()
```
