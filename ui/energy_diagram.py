"""Diagrama didático de níveis e transições eletrônicas."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox, QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from orbitals.orbital_types import get_orbital_type
from physics.energy_levels import (
    build_energy_levels, calculate_transition, diagram_subshells,
)


SUPERSCRIPT = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def subshell_label(n, l, occupancy=None):
    label = f"{n}{get_orbital_type(l).letter}"
    if occupancy is not None:
        label += str(occupancy).translate(SUPERSCRIPT)
    return label


class EnergyDiagramWidget(QWidget):
    """Apresenta a ordem qualitativa dos subníveis e energias aproximadas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.levels = []
        self.level_by_key = {}
        self.selected_key = None
        self.species = "espécie atual"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.help_label = QLabel(
            "A posição vertical segue a ordem qualitativa de Aufbau. "
            "Os valores E são estimativas hidrogenoides com Z_eff de Slater."
        )
        self.help_label.setObjectName("helpBanner")
        self.help_label.setWordWrap(True)
        self.help_label.setToolTip(
            "A escala vertical não representa distâncias proporcionais entre "
            "energias; ela organiza os subníveis pela sequência de Aufbau."
        )
        layout.addWidget(self.help_label)

        self.figure = Figure(figsize=(7.5, 5.2), facecolor="#07111f")
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas, stretch=1)

        controls = QGridLayout()
        controls.setHorizontalSpacing(8)
        controls.addWidget(QLabel("Estado inicial:"), 0, 0)
        controls.addWidget(QLabel("Estado final:"), 0, 1)
        self.combo_initial = QComboBox()
        self.combo_final = QComboBox()
        self.combo_initial.setToolTip(
            "Escolha um subnível ocupado como origem do elétron."
        )
        self.combo_final.setToolTip(
            "O orbital selecionado nos controles quânticos aparece aqui como "
            "destino sugerido."
        )
        controls.addWidget(self.combo_initial, 1, 0)
        controls.addWidget(self.combo_final, 1, 1)
        self.btn_transition = QPushButton("Calcular transição")
        self.btn_transition.setProperty("variant", "primary")
        self.btn_transition.setToolTip(
            "Calcula ΔE, frequência e comprimento de onda do fóton pela "
            "aproximação exibida."
        )
        self.btn_transition.clicked.connect(self.calculate_selected_transition)
        controls.addWidget(self.btn_transition, 1, 2)
        layout.addLayout(controls)

        self.transition_result = QLabel(
            "Selecione dois subníveis para estimar absorção ou emissão."
        )
        self.transition_result.setObjectName("transitionResult")
        self.transition_result.setWordWrap(True)
        self.transition_result.setTextFormat(Qt.RichText)
        layout.addWidget(self.transition_result)

    def update_state(self, Z, electron_count, configuration, selected, species):
        selection_changed = selected != self.selected_key
        self.selected_key = selected
        self.species = species
        self.levels = build_energy_levels(
            Z, electron_count, configuration,
            subshells=diagram_subshells(electron_count, selected),
        )
        self.level_by_key = {level.key: level for level in self.levels}
        self._populate_transition_controls()
        if selection_changed:
            destination = self.combo_final.currentData()
            if destination == selected:
                self.transition_result.setText(
                    f"Destino sincronizado com <b>{subshell_label(*selected)}</b>. "
                    "Clique em “Calcular transição”."
                )
            else:
                self.transition_result.setText(
                    "Escolha estados diferentes para estimar absorção ou emissão."
                )
        self._draw(species)

    @staticmethod
    def _index_for_data(combo, value):
        """Localiza dados compostos sem depender da conversão QVariant do Qt."""
        return next(
            (index for index in range(combo.count())
             if combo.itemData(index) == value),
            -1,
        )

    def _populate_transition_controls(self):
        previous_initial = self.combo_initial.currentData()
        previous_final = self.combo_final.currentData()
        self.combo_initial.blockSignals(True)
        self.combo_final.blockSignals(True)
        self.combo_initial.clear()
        self.combo_final.clear()

        occupied = [level for level in self.levels if level.occupancy]
        for level in occupied:
            self.combo_initial.addItem(
                f"{subshell_label(*level.key, level.occupancy)}  ({level.energy_ev:.2f} eV)",
                level.key,
            )
        for level in self.levels:
            self.combo_final.addItem(
                f"{subshell_label(*level.key, level.occupancy)}  ({level.energy_ev:.2f} eV)",
                level.key,
            )

        initial_index = self._index_for_data(
            self.combo_initial, previous_initial
        )
        if initial_index >= 0:
            self.combo_initial.setCurrentIndex(initial_index)
        initial_key = self.combo_initial.currentData()
        preferred_final = (
            self.selected_key
            if self.selected_key in self.level_by_key
            and self.selected_key != initial_key
            else previous_final
        )
        final_index = self._index_for_data(self.combo_final, preferred_final)
        if final_index < 0 and occupied:
            final_index = next(
                (i for i in range(self.combo_final.count())
                 if self.combo_final.itemData(i) != initial_key),
                0,
            )
        if final_index >= 0:
            self.combo_final.setCurrentIndex(final_index)

        enabled = bool(occupied) and self.combo_final.count() > 1
        self.combo_initial.setEnabled(enabled)
        self.combo_final.setEnabled(enabled)
        self.btn_transition.setEnabled(enabled)
        self.combo_initial.blockSignals(False)
        self.combo_final.blockSignals(False)

    def _draw(self, species, transition=None):
        self.figure.clear()
        axis = self.figure.add_subplot(111)
        axis.set_facecolor("#07111f")
        axis.set_xlim(0, 1)
        axis.set_ylim(-0.7, max(1, len(self.levels) - 0.3))
        axis.set_xticks([])
        axis.set_yticks([])
        for spine in axis.spines.values():
            spine.set_visible(False)

        label_font_size = 9 if len(self.levels) <= 12 else 7
        value_font_size = 8 if len(self.levels) <= 12 else 6.5
        for position, level in enumerate(self.levels):
            is_selected = level.key == self.selected_key
            color = "#ffd166" if is_selected else ("#49d7a5" if level.occupancy else "#60788d")
            linewidth = 4.0 if is_selected else 2.5
            axis.hlines(position, 0.24, 0.72, color=color, linewidth=linewidth)
            axis.text(
                0.21, position, subshell_label(*level.key, level.occupancy),
                ha="right", va="center", color=color, fontsize=label_font_size,
                fontweight="bold" if is_selected else "normal",
            )
            axis.text(
                0.75, position,
                f"E≈{level.energy_ev:.2f} eV   Z_eff={level.z_eff:.2f}",
                ha="left", va="center", color="#c7d8e8", fontsize=value_font_size,
            )

        if transition is not None:
            positions = {level.key: index for index, level in enumerate(self.levels)}
            y0 = positions[transition.initial]
            y1 = positions[transition.final]
            arrow_color = "#62d8ff" if transition.process == "absorção" else "#ff8fb8"
            axis.annotate(
                "", xy=(0.48, y1), xytext=(0.48, y0),
                arrowprops=dict(arrowstyle="->", color=arrow_color, lw=2.5),
            )

        axis.set_title(
            f"Níveis de energia — {species}", color="#edf7ff", fontsize=12, pad=10
        )
        axis.text(
            0.01, 0.01, "posição vertical: ordem de Aufbau (escala qualitativa)",
            transform=axis.transAxes, color="#7790a5", fontsize=7,
        )
        self.figure.tight_layout(pad=1.2)
        self.canvas.draw_idle()

    def calculate_selected_transition(self):
        initial_key = self.combo_initial.currentData()
        final_key = self.combo_final.currentData()
        if initial_key not in self.level_by_key or final_key not in self.level_by_key:
            return
        try:
            result = calculate_transition(
                self.level_by_key[initial_key], self.level_by_key[final_key]
            )
        except ValueError as error:
            self.transition_result.setText(f"<b>Transição inválida:</b> {error}")
            return

        selection = (
            "Δl = ±1 atendida"
            if result.dipole_l_allowed
            else "Δl = ±1 não atendida (dipolo elétrico proibido)"
        )
        self.transition_result.setText(
            f"<b>{result.process.upper()}</b> &nbsp; "
            f"ΔE = {result.delta_energy_ev:+.4f} eV &nbsp; | &nbsp; "
            f"f ≈ {result.frequency_hz:.3e} Hz &nbsp; | &nbsp; "
            f"λ ≈ {result.wavelength_nm:.2f} nm ({result.spectral_region})<br>"
            f"Regra parcial de seleção: {selection}. A condição Δm depende da orientação escolhida."
        )
        self._draw(self.species, transition=result)
