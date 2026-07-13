import pytest

from physics.energy_levels import (
    approximate_orbital_energy,
    build_energy_levels,
    calculate_transition,
    diagram_subshells,
)
from physics.screening import build_ground_state_config


def test_hydrogen_1s_uses_rydberg_energy():
    energy, z_eff = approximate_orbital_energy(
        1, 1, 0, electron_count=1, configuration={(1, 0): 1}
    )
    assert z_eff == pytest.approx(1.0)
    assert energy == pytest.approx(-13.605693122994)


def test_empty_hydrogen_levels_relocate_the_same_electron():
    energy, z_eff = approximate_orbital_energy(
        1, 3, 2, electron_count=1, configuration={(1, 0): 1}
    )

    assert z_eff == pytest.approx(1.0)
    assert energy == pytest.approx(-13.605693122994 / 9)


def test_energy_levels_include_occupancy_and_future_levels():
    config = build_ground_state_config(11, electron_count=10)
    levels = build_energy_levels(11, 10, config)
    by_key = {level.key: level for level in levels}
    assert by_key[(2, 1)].occupancy == 6
    assert (3, 0) in by_key
    assert all(level.energy_ev < 0 for level in levels)


def test_energy_diagram_includes_selected_distant_subshell():
    subshells = diagram_subshells(1, selected=(4, 2))

    assert (4, 2) in subshells
    assert subshells.index((4, 2)) > subshells.index((3, 1))


def test_energy_diagram_accepts_exploratory_subshell_outside_aufbau_sequence():
    subshells = diagram_subshells(1, selected=(5, 4))
    levels = build_energy_levels(1, 1, {(1, 0): 1}, subshells=subshells)

    assert levels[-1].key == (5, 4)


def test_transition_reports_absorption_emission_and_selection_rule():
    levels = build_energy_levels(1, 1, {(1, 0): 1})
    by_key = {level.key: level for level in levels}

    absorption = calculate_transition(by_key[(1, 0)], by_key[(2, 1)])
    emission = calculate_transition(by_key[(2, 1)], by_key[(1, 0)])
    forbidden_l = calculate_transition(by_key[(1, 0)], by_key[(2, 0)])

    assert absorption.process == "absorção"
    assert emission.process == "emissão"
    assert absorption.photon_energy_ev == pytest.approx(emission.photon_energy_ev)
    assert absorption.frequency_hz > 0
    assert absorption.wavelength_nm == pytest.approx(121.5, abs=0.5)
    assert absorption.dipole_l_allowed
    assert not forbidden_l.dipole_l_allowed


def test_hydrogen_1s_to_4d_matches_selected_orbital_case():
    subshells = diagram_subshells(1, selected=(4, 2))
    levels = build_energy_levels(1, 1, {(1, 0): 1}, subshells=subshells)
    by_key = {level.key: level for level in levels}

    transition = calculate_transition(by_key[(1, 0)], by_key[(4, 2)])

    assert transition.wavelength_nm == pytest.approx(97.20, abs=0.05)
    assert not transition.dipole_l_allowed


def test_same_level_transition_is_rejected():
    level = build_energy_levels(1, 1, {(1, 0): 1})[0]
    with pytest.raises(ValueError):
        calculate_transition(level, level)
