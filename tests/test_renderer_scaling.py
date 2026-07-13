import pytest

from orbitals.orbital import Orbital
from simulator.renderer import Renderer


def test_orbital_range_scales_inversely_with_effective_charge():
    renderer = Renderer()
    compact = Orbital(3, 2, 1, Z_eff=1.0)
    diffuse = Orbital(3, 2, 1, Z_eff=0.5)

    assert renderer._get_range_for_orbital(diffuse) == pytest.approx(
        2 * renderer._get_range_for_orbital(compact)
    )
