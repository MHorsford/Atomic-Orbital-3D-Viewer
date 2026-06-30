"""
ui/orbital_explorer.py

Interface PyQt5 para explorar orbitais atômicos de forma interativa.
Permite visualizar qualquer orbital (n, l, m) do hidrogênio e outros átomos.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel,
    QPushButton, QComboBox, QSpinBox, QGroupBox, QGridLayout, QTextEdit,
    QApplication, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from simulator.simulator import Simulator
from simulator.scene import Scene
from orbitals.orbital import Orbital
from utils.helpers import quantum_label
from config import MAX_N, MAX_Z, ISO_VALUE
import numpy as np


class OrbitalExplorer(QMainWindow):
    """
    Janela principal da UI para exploração de orbitais.
    """
    
    def __init__(self, simulator):
        """
        Parâmetros:
            simulator : objeto Simulator já inicializado
        """
        super().__init__()
        self.simulator = simulator
        self.setWindowTitle("🧪 Orbital Explorer — Simulador de Orbitais Atômicos")
        self.setGeometry(100, 100, 1400, 700)
        
        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Criar painéis
        self.create_control_panel()
        self.create_info_panel()
        
        # Timer para atualizações suaves
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.on_slider_changed)
        self.update_timer.setInterval(100)  # 100ms debounce
        self.timer_pending = False

    def load_all_elements(self):
        """Carrega todos os elementos do CSV."""
        csv_path = Path(__file__).parent.parent / "data" / "periodic_table.csv"
        if not csv_path.exists():
            csv_path = Path("data/periodic_table.csv")
        
        try:
            df = pd.read_csv(csv_path)
            elements = []
            for _, row in df.iterrows():
                name = f"{row['name']} ({row['symbol']})"
                Z = int(row['atomic_number'])
                elements.append((name, Z))
            return elements
        except Exception as e:
            print(f"⚠ Erro: {e}. Usando fallback.")
            return [("Hydrogen (H)", 1), ("Helium (He)", 2), ("Carbon (C)", 6)]
    
    # ─────────────────────────────────────────────────────────────────────
    # CRIAÇÃO DA UI
    # ─────────────────────────────────────────────────────────────────────
    
    def create_control_panel(self):
            control_panel = QGroupBox("Controles de Orbital")
            layout = QGridLayout()

            # Elemento
            layout.addWidget(QLabel("Elemento (Z):"), 0, 0)
            self.combo_element = QComboBox()
            for name, Z in self.load_all_elements():
                if Z <= MAX_Z:  # <--- Respeita o limite do config
                    self.combo_element.addItem(name, Z)
            self.combo_element.currentIndexChanged.connect(self.on_element_changed)
            layout.addWidget(self.combo_element, 0, 1)

            # n            
            layout.addWidget(QLabel("Nível Quântico (n):"), 1, 0)
            self.slider_n = QSlider(Qt.Horizontal)
            self.slider_n.setRange(1, MAX_N)  # <--- Puxa dinamicamente do config
            self.slider_n.setValue(1)
            self.slider_n.sliderMoved.connect(self.schedule_update)
            self.slider_n.valueChanged.connect(self.on_n_changed)
            layout.addWidget(self.slider_n, 1, 1)
            self.label_n = QLabel("n = 1")
            self.label_n.setFont(QFont("Courier", 11, QFont.Bold))
            layout.addWidget(self.label_n, 1, 2)

            # l
            layout.addWidget(QLabel("Tipo Orbital (l):"), 2, 0)
            self.slider_l = QSlider(Qt.Horizontal)
            self.slider_l.setRange(0, MAX_N - 1)  # <--- l vai até n-1 máximo global
            self.slider_l.setValue(0)
            self.slider_l.sliderMoved.connect(self.schedule_update)
            self.slider_l.valueChanged.connect(self.on_l_changed)
            layout.addWidget(self.slider_l, 2, 1)
            self.label_l = QLabel("l = 0 (s)")
            self.label_l.setFont(QFont("Courier", 11, QFont.Bold))
            layout.addWidget(self.label_l, 2, 2)

            # m
            layout.addWidget(QLabel("Orientação (m):"), 3, 0)
            self.slider_m = QSlider(Qt.Horizontal)
            self.slider_m.setRange(-3, 3)
            self.slider_m.setValue(0)
            self.slider_m.sliderMoved.connect(self.schedule_update)
            self.slider_m.valueChanged.connect(self.on_m_changed)
            layout.addWidget(self.slider_m, 3, 1)
            self.label_m = QLabel("m = 0")
            self.label_m.setFont(QFont("Courier", 11, QFont.Bold))
            layout.addWidget(self.label_m, 3, 2)

            # Modo renderização
            layout.addWidget(QLabel("Modo Renderização:"), 4, 0)
            self.combo_mode = QComboBox()
            self.combo_mode.addItems(["isosurface", "volume", "points"])
            self.combo_mode.currentTextChanged.connect(self.on_mode_changed)
            layout.addWidget(self.combo_mode, 4, 1)

            # Iso value
            layout.addWidget(QLabel("Isosurface Value:"), 5, 0)
            self.slider_iso = QSlider(Qt.Horizontal)
            self.slider_iso.setRange(0, 200)
            
            # Converte o valor do config (ex: 0.12 -> 12)
            initial_iso_slider_val = int(ISO_VALUE * 100)
            self.slider_iso.setValue(initial_iso_slider_val) 
            self.slider_iso.sliderMoved.connect(self.schedule_update)
            layout.addWidget(self.slider_iso, 5, 1)
            
            self.label_iso = QLabel(f"{ISO_VALUE:.3f}") # Texto sincronizado
            layout.addWidget(self.label_iso, 5, 2)

            # Alta qualidade
            layout.addWidget(QLabel("Alta Qualidade:"), 6, 0)
            self.check_quality = QCheckBox("PBR + Fundo Preto")
            self.check_quality.setChecked(self.simulator.scene.high_quality)
            self.check_quality.stateChanged.connect(self.on_quality_toggled)
            layout.addWidget(self.check_quality, 6, 1)

            # Botões
            button_layout = QVBoxLayout()
            self.btn_render = QPushButton("🎨 Renderizar Orbital")
            self.btn_render.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold;")
            self.btn_render.clicked.connect(self.on_render_clicked)
            button_layout.addWidget(self.btn_render)

            self.btn_all_filled = QPushButton("📊 Mostrar Preenchidos")
            self.btn_all_filled.setStyleSheet("background-color: #3498db; color: white;")
            self.btn_all_filled.clicked.connect(self.on_show_filled)
            button_layout.addWidget(self.btn_all_filled)

            self.btn_sequence = QPushButton("📈 Sequência Aufbau")
            self.btn_sequence.setStyleSheet("background-color: #e74c3c; color: white;")
            self.btn_sequence.clicked.connect(self.on_sequence_clicked)
            button_layout.addWidget(self.btn_sequence)

            layout.addLayout(button_layout, 7, 0, 1, 3)

            control_panel.setLayout(layout)
            self.main_layout.addWidget(control_panel, stretch=1)
    
    def create_info_panel(self):
        """Cria o painel de informações."""
        info_panel = QGroupBox("Informações do Orbital")
        layout = QVBoxLayout()
        
        # Título do orbital
        self.label_orbital_name = QLabel()
        self.label_orbital_name.setFont(QFont("Arial", 20, QFont.Bold))
        self.label_orbital_name.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_orbital_name)
        
        # Informações detalhadas
        self.text_info = QTextEdit()
        self.text_info.setReadOnly(True)
        self.text_info.setFont(QFont("Courier", 10))
        layout.addWidget(self.text_info)
        
        # Descrição
        self.label_description = QLabel()
        self.label_description.setWordWrap(True)
        self.label_description.setFont(QFont("Arial", 9))
        layout.addWidget(self.label_description)
        
        info_panel.setLayout(layout)
        self.main_layout.addWidget(info_panel, stretch=1)
    
    # ─────────────────────────────────────────────────────────────────────
    # CALLBACKS DOS SLIDERS
    # ─────────────────────────────────────────────────────────────────────
    
        
    def on_element_changed(self, index):
        Z = self.combo_element.currentData()
        from atom.atom import Atom
        self.simulator.atom = Atom(Z=Z)
        self.update_limits()   # já chama on_render_clicked internamente

    def on_n_changed(self):
        """Quando muda o nível quântico n."""
        n = self.slider_n.value()
        self.label_n.setText(f"n = {n}")
        
        # Limitar l dinamicamente baseado em n
        max_l = n - 1
        self.slider_l.setMaximum(max_l)
        if self.slider_l.value() > max_l:
            self.slider_l.setValue(max_l)
        
        # Apenas chama o próximo da cadeia de validação
        self.on_l_changed()
    
    def on_l_changed(self):
        """Quando muda o tipo orbital l."""
        from orbitals.orbital_types import get_orbital_type
        
        l = self.slider_l.value()
        orbital_type = get_orbital_type(l)
        self.label_l.setText(f"l = {l} ({orbital_type.letter})")
        
        # 🔥 REMOVIDO: Tiramos os métodos self.slider_iso.setValue() 
        # que causavam o erro de float/int e derrubavam a UI.
        
        # Limitar m dinamicamente baseado em l
        self.slider_m.setRange(-l, l)
        if abs(self.slider_m.value()) > l:
            self.slider_m.setValue(0)
        
        # Finaliza a cadeia de atualização com segurança
        self.on_m_changed()

    
    def on_m_changed(self):
        """Quando muda a orientação m."""
        m = self.slider_m.value()
        self.label_m.setText(f"m = {m:+d}")
        
        # Agora que n, l e m estão 100% validados e em harmonia, agenda o cálculo seguro
        self.schedule_update()


    def on_quality_toggled(self, state):
        """Alterna entre renderização normal e de alta qualidade."""
        high = (state == Qt.Checked)
        self.simulator.set_high_quality(high)
        self.on_render_clicked()   # re-renderiza para ver a diferença
    

    
    def on_mode_changed(self, mode):
        """Quando muda o modo de renderização."""
        self.simulator.set_render_mode(mode)
        self.on_render_clicked()
    
    def schedule_update(self):
        """Agenda uma atualização (debounce)."""
        self.timer_pending = True
        if not self.update_timer.isActive():
            self.update_timer.start()
    
    def on_slider_changed(self):
        """Timer callback para debouncing."""
        if self.timer_pending:
            self.on_render_clicked()
            self.timer_pending = False
            self.update_timer.stop()
    
    def on_render_clicked(self):
        """Renderiza o orbital selecionado."""
        n = self.slider_n.value()
        l = self.slider_l.value()
        m = self.slider_m.value()
        
        # Validar m
        if abs(m) > l:
            m = 0
            self.slider_m.setValue(0)
        
        # Validar l
        if l >= n:
            l = n - 1
            self.slider_l.setValue(l)
        
        # Atualizar iso value
        iso_val = self.slider_iso.value() / 100.0  
        self.label_iso.setText(f"{iso_val:.3f}")
        self.simulator.set_iso_value(iso_val)
        
        # Renderizar
        self.visualize_orbital(n, l, m)
        
        # Atualizar info
        self.update_info(n, l, m)
    
    def on_show_filled(self):
        """Mostra os orbitais preenchidos."""
        self.simulator.update_atom_display()
        self.update_info_filled()
    
    def on_sequence_clicked(self):
        """Mostra a sequência de Aufbau."""
        from physics.screening import get_orbital_sequence
        from utils.helpers import quantum_label
        
        seq = get_orbital_sequence()
        info = "SEQUÊNCIA DE AUFBAU (Ordem de Preenchimento)\n"
        info += "=" * 50 + "\n\n"
        
        count = 0
        for n, l in seq[:20]:
            label = quantum_label(n, l)
            max_e = 2 * (2*l + 1)
            count += 1
            info += f"{count:2d}. {label:5s}  (máx {max_e:2d} e⁻)\n"
            
            if count == 10:
                info += "\n"
        
        self.text_info.setText(info)
    
    # ─────────────────────────────────────────────────────────────────────
    # RENDERIZAÇÃO DE ORBITAIS
    # ─────────────────────────────────────────────────────────────────────
    
    def visualize_orbital(self, n: int, l: int, m: int = 0):
        from physics.screening import slater_effective_charge
        Z_eff = slater_effective_charge(self.simulator.atom.Z, n, l)
        if Z_eff is None or Z_eff <= 0:
            Z_eff = self.simulator.atom.Z - (n - 1)
            if Z_eff < 0.1:
                Z_eff = 0.1

        orbital = Orbital(n=n, l=l, m=m, electrons=1, Z_eff=Z_eff)
        mesh = self.simulator.renderer.render_orbital(orbital)
        orbital_label = quantum_label(n, l, m)
        self.simulator.scene.clear_orbital_meshes()
        self.simulator.scene.add_orbital_mesh(mesh, orbital_label, orbital.color, 0.8)
        
        # 🔥 Ajusta a câmera para o tamanho do orbital
        range_max = self.simulator.renderer._get_range_for_n(n)
        self.simulator.scene.set_camera_for_range(range_max)
        
        self.simulator.scene.update()

    
    def update_limits(self):
        """
        Versão blindada e inteligente: sugere a camada de valência 
        sem causar erro de recursão/crash na UI.
        """
        if not self.simulator.atom:
            return

        # 1. BLOQUEIO ESSENCIAL: impede a UI de tentar renderizar no meio da atualização
        self.slider_n.blockSignals(True)
        self.slider_l.blockSignals(True)
        self.slider_m.blockSignals(True)

        try:
            # 2. LÓGICA DE VALÊNCIA: Encontra o nível n mais externo com elétrons
            max_n_occupied = max(
                (orb.n for orb in self.simulator.atom.orbitals if orb.electrons > 0),
                default=1
            )

            # Garante que não ultrapasse MAX_N (definido no config)
            if max_n_occupied > MAX_N:
                max_n_occupied = MAX_N

            # 3. CONFIGURA N
            self.slider_n.setValue(max_n_occupied)
            self.label_n.setText(f"n = {max_n_occupied}")

            # 4. CONFIGURA L (reseta para s)
            max_l = max_n_occupied - 1
            self.slider_l.setRange(0, max_l)
            self.slider_l.setValue(0)
            from orbitals.orbital_types import get_orbital_type
            self.label_l.setText(f"l = 0 ({get_orbital_type(0).letter})")

            # 5. CONFIGURA M (reseta para 0)
            self.slider_m.setRange(0, 0)   # l=0 → m só pode ser 0
            self.slider_m.setValue(0)
            self.label_m.setText("m = +0")

        finally:
            # 6. LIBERAÇÃO: Agora a UI pode voltar a ouvir os comandos do usuário
            self.slider_n.blockSignals(False)
            self.slider_l.blockSignals(False)
            self.slider_m.blockSignals(False)

        # 7. RENDER FINAL: Agora sim, com tudo validado, desenha o orbital na tela
        self.on_render_clicked()

    
    # ─────────────────────────────────────────────────────────────────────
    # ATUALIZAÇÃO DE INFORMAÇÕES
    # ─────────────────────────────────────────────────────────────────────
    
    def update_info(self, n: int, l: int, m: int):
        """Atualiza o painel de informações."""
        from orbitals.orbital_types import get_orbital_type, ORBITAL_TYPES
        from physics.screening import slater_effective_charge
        
        # Nome do orbital
        orbital_type = get_orbital_type(l)
        orbital_name = quantum_label(n, l, m)
        self.label_orbital_name.setText(f"{orbital_name}")
        
        # Informações detalhadas
        orbital_type = get_orbital_type(l)
        Z_eff = slater_effective_charge(self.simulator.atom.Z, n, l)
        
        info = f"Números Quânticos:\n"
        info += f"  n (principal)  = {n}    (nível de energia)\n"
        info += f"  l (azimutal)   = {l}    (tipo: {orbital_type.letter})\n"
        info += f"  m (magnético)  = {m:+d}  (orientação)\n"
        info += f"  s (spin)       = ±½   (não visualizado)\n\n"
        
        info += f"Parâmetros do Elemento:\n"
        info += f"  Z (nuclear)    = {self.simulator.atom.Z}\n"
        info += f"  Z_eff          = {Z_eff:.2f}\n"
        info += f"  Elemento       = {self.simulator.atom.get_element_symbol()}\n\n"
        
        info += f"Características:\n"
        info += f"  {orbital_type.description}\n"
        info += f"  Capacidade: {orbital_type.max_electrons} e⁻ (subnível)\n"
        info += f"  Degeneração: {orbital_type.degeneracy} orbitais\n"
        
        self.text_info.setText(info)
        
        # Descrição
        descriptions = {
            (1, 0): "🔵 Esférico perfeito, menor e mais energético.",
            (2, 0): "🔵 Esférico com nó radial interno.",
            (2, 1): "🥁 Haltere em 3 orientações (x, y, z).",
            (3, 0): "🔵 Esférico com 2 nós radiais.",
            (3, 1): "🥁 Halteres maiores e mais afastados.",
            (3, 2): "🍀 Trevos com 4-5 lobos complexos.",
            (4, 0): "🔵 Esférico com 3 nós radiais.",
            (4, 1): "🥁 Halteres ainda maiores.",
        }
        
        desc = descriptions.get((n, l), "Orbital de alta energia")
        self.label_description.setText(orbital_type.description)
    
    def update_info_filled(self):
        """Atualiza info mostrando configuração eletrônica."""
        atom = self.simulator.atom
        config = atom.get_electron_config()
        
        info = f"CONFIGURAÇÃO ELETRÔNICA\n"
        info += f"{'=' * 50}\n\n"
        info += f"Elemento: {atom.get_element_name()} ({atom.get_element_symbol()})\n"
        info += f"Z = {atom.Z} | Elétrons = {atom.N_electrons}\n\n"
        info += f"Configuração:\n{config}\n\n"
        info += f"Elétrons de valência: {atom.get_valence_electrons()}\n\n"
        info += f"Orbitais preenchidos:\n"
        
        for orbital in atom.orbitals:
            if orbital.electrons > 0:
                label = quantum_label(orbital.n, orbital.l, orbital.m)
                info += f"  {label:5s} — {orbital.electrons} e⁻\n"
        
        self.text_info.setText(info)


def launch_explorer(simulator):
    """
    Lança a UI de exploração de orbitais.
    
    Parâmetros:
        simulator : objeto Simulator já rodando
    
    Uso:
        app, explorer = launch_explorer(sim)
        app.exec_()
    """
    app = QApplication.instance()  # Pegar app existente ou criar
    if app is None:
        app = QApplication(sys.argv)
    
    explorer = OrbitalExplorer(simulator)
    explorer.show()
    
    return app, explorer


if __name__ == "__main__":
    # Teste
    from atom.atom import Atom
    from simulator.simulator import Simulator
    
    print("Iniciando Orbital Explorer...")
    
    atom = Atom(Z=1)
    sim = Simulator(atom=atom, title="Orbital Explorer — Teste")
    
    app, explorer = launch_explorer(sim)
    
    sys.exit(app.exec_())