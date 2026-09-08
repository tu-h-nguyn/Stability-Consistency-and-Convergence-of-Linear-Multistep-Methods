"""The generated coefficient families must match the textbook tables."""

import numpy as np
import pytest

from lmm.catalog import EULER_IMPLICIT, TRAPEZOID, adams_bashforth, adams_moulton, bdf

# Reference values from Hairer, Norsett & Wanner, and from Chapter 3 of the report.
BDF_ALPHA = {
    1: (-1, 1),
    2: (1 / 2, -2, 3 / 2),
    3: (-1 / 3, 3 / 2, -3, 11 / 6),
    4: (1 / 4, -4 / 3, 3, -4, 25 / 12),
    5: (-1 / 5, 5 / 4, -10 / 3, 5, -5, 137 / 60),
    6: (1 / 6, -6 / 5, 15 / 4, -20 / 3, 15 / 2, -6, 147 / 60),
}

AB_BETA = {
    1: (1, 0),
    2: (-1 / 2, 3 / 2, 0),
    3: (5 / 12, -16 / 12, 23 / 12, 0),
    4: (-9 / 24, 37 / 24, -59 / 24, 55 / 24, 0),
}

AM_BETA = {
    1: (1 / 2, 1 / 2),
    2: (-1 / 12, 8 / 12, 5 / 12),
    3: (1 / 24, -5 / 24, 19 / 24, 9 / 24),
}


@pytest.mark.parametrize("k", sorted(BDF_ALPHA))
def test_bdf_alpha_matches_reference(k):
    assert np.allclose(bdf(k).alpha, BDF_ALPHA[k])
    assert np.allclose(bdf(k).beta, [0.0] * k + [1.0])


@pytest.mark.parametrize("k", sorted(AB_BETA))
def test_adams_bashforth_beta_matches_reference(k):
    assert np.allclose(adams_bashforth(k).beta, AB_BETA[k])


@pytest.mark.parametrize("k", sorted(AM_BETA))
def test_adams_moulton_beta_matches_reference(k):
    assert np.allclose(adams_moulton(k).beta, AM_BETA[k])


def test_bdf1_is_backward_euler():
    assert np.allclose(bdf(1).alpha, EULER_IMPLICIT.alpha)
    assert np.allclose(bdf(1).beta, EULER_IMPLICIT.beta)


def test_am1_is_the_trapezoidal_rule():
    assert np.allclose(adams_moulton(1).beta, TRAPEZOID.beta)


@pytest.mark.parametrize("k", range(1, 7))
def test_bdf_order_equals_step_count(k):
    assert bdf(k).order == k


@pytest.mark.parametrize("k", range(1, 5))
def test_adams_orders(k):
    assert adams_bashforth(k).order == k
    assert adams_moulton(k).order == k + 1
