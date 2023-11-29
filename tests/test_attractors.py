"""Test functions for the attractors.py module."""
import pytest

import attractors2023.attractors as at


def test_attractor():
    """Test the Attractor class."""
    attractor = at.Attractor()
    assert attractor.a == 1.7
    assert attractor.colormap == 'kgy'

    fd = at.FractalDream()
    assert fd.d == 2.34
    assert fd.colormap == 'kgy'
    assert fd.equations[0] == '$x_{n+1} = \\sin\\ by_n + c\\ \\sin\\ bx_n$'
    assert fd.fn(1, 2, 3, 4, 5, 6) == pytest.approx((-2.7946542299162593, -1.535372981133688))


def test_parametersets():
    """Test the ParameterSets class."""
    params = at.ParameterSets(name='Attractors')
    assert params.example == ['Svensson', 'fire', 0, 0, 1.4, 1.56, 1.4, -6.56]
    assert len(params.param.example.objects) == 75
    assert len(params.args('Svensson')) == 4
    assert params.attractors['GumowskiMira'].name == 'GumowskiMira parameters'
