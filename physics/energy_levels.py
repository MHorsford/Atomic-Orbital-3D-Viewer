"""Estimativas didáticas de níveis e transições eletrônicas."""

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from physics.constants import C, E_CHARGE, H, RY_EV
from physics.screening import (
    get_orbital_sequence, max_electrons_in_subshell,
    orbital_state_effective_charge,
)


@dataclass(frozen=True)
class EnergyLevel:
    n: int
    l: int
    occupancy: int
    energy_ev: float
    z_eff: float
    aufbau_index: int

    @property
    def key(self) -> Tuple[int, int]:
        return self.n, self.l


@dataclass(frozen=True)
class TransitionResult:
    initial: Tuple[int, int]
    final: Tuple[int, int]
    delta_energy_ev: float
    photon_energy_ev: float
    frequency_hz: float
    wavelength_nm: float
    process: str
    dipole_l_allowed: bool
    spectral_region: str


def relevant_subshells(electron_count: int, extra_levels: int = 4) -> List[Tuple[int, int]]:
    """Subníveis necessários para acomodar N elétrons mais níveis seguintes."""
    sequence = get_orbital_sequence()
    capacity = 0
    last_index = 0
    for index, (_, l) in enumerate(sequence):
        capacity += max_electrons_in_subshell(l)
        last_index = index
        if capacity >= max(1, electron_count):
            break
    return sequence[:min(len(sequence), last_index + 1 + extra_levels)]


def diagram_subshells(
        electron_count: int, selected: Tuple[int, int] = None,
        extra_levels: int = 4,
) -> List[Tuple[int, int]]:
    """Inclui no diagrama o subnível selecionado e seu contexto energético."""
    sequence = get_orbital_sequence()
    subshells = relevant_subshells(electron_count, extra_levels)
    if selected is None or selected in subshells:
        return subshells
    if selected in sequence:
        return sequence[:max(len(subshells), sequence.index(selected) + 1)]
    return subshells + [selected]


def approximate_orbital_energy(
        Z: int, n: int, l: int, electron_count: int = None,
        configuration: Dict[Tuple[int, int], int] = None,
) -> Tuple[float, float]:
    """Retorna (E, Z_eff) pela aproximação hidrogenoide E=-Ry·Z_eff²/n²."""
    z_eff = orbital_state_effective_charge(
        Z, n, l, electron_count=electron_count, configuration=configuration,
    )
    energy_ev = -RY_EV * (z_eff ** 2) / (n ** 2)
    return energy_ev, z_eff


def build_energy_levels(
        Z: int, electron_count: int,
        configuration: Dict[Tuple[int, int], int],
        subshells: Iterable[Tuple[int, int]] = None,
) -> List[EnergyLevel]:
    """Constrói níveis aproximados para a configuração eletrônica atual."""
    sequence = get_orbital_sequence()
    selected = list(subshells or relevant_subshells(electron_count))
    levels = []
    for n, l in selected:
        energy_ev, z_eff = approximate_orbital_energy(
            Z, n, l, electron_count=electron_count,
            configuration=configuration,
        )
        aufbau_index = (
            sequence.index((n, l))
            if (n, l) in sequence else len(sequence) + n + l
        )
        levels.append(EnergyLevel(
            n=n,
            l=l,
            occupancy=configuration.get((n, l), 0),
            energy_ev=energy_ev,
            z_eff=z_eff,
            aufbau_index=aufbau_index,
        ))
    return levels


def spectral_region(wavelength_nm: float) -> str:
    if wavelength_nm < 0.01:
        return "raios gama"
    if wavelength_nm < 10:
        return "raios X"
    if wavelength_nm < 380:
        return "ultravioleta"
    if wavelength_nm < 750:
        return "visível"
    if wavelength_nm < 1_000_000:
        return "infravermelho"
    return "micro-ondas ou rádio"


def calculate_transition(initial: EnergyLevel, final: EnergyLevel) -> TransitionResult:
    """Calcula propriedades aproximadas de uma transição entre dois subníveis."""
    if initial.key == final.key:
        raise ValueError("Os níveis inicial e final devem ser diferentes")
    delta = final.energy_ev - initial.energy_ev
    photon_energy = abs(delta)
    if photon_energy <= 1e-12:
        raise ValueError("A diferença de energia é pequena demais para a estimativa")
    energy_joule = photon_energy * E_CHARGE
    frequency = energy_joule / H
    wavelength_nm = (C / frequency) * 1e9
    return TransitionResult(
        initial=initial.key,
        final=final.key,
        delta_energy_ev=delta,
        photon_energy_ev=photon_energy,
        frequency_hz=frequency,
        wavelength_nm=wavelength_nm,
        process="absorção" if delta > 0 else "emissão",
        dipole_l_allowed=abs(final.l - initial.l) == 1,
        spectral_region=spectral_region(wavelength_nm),
    )
