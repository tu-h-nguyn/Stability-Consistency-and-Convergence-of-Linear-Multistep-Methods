"""Consistency, order, the root condition and the Dahlquist barriers."""

import numpy as np
import pytest

from lmm.catalog import (
    METHOD_A,
    METHOD_B,
    MIDPOINT,
    SIMPSON,
    adams_bashforth,
    adams_moulton,
    bdf,
)
from lmm.core import LinearMultistepMethod


def test_method_a_is_consistent_of_order_three_but_not_zero_stable():
    """Chapter 4, Example 1: high order, still divergent."""
    assert METHOD_A.is_consistent
    assert METHOD_A.order == 3
    assert not METHOD_A.is_zero_stable
    assert not METHOD_A.is_convergent
    roots = sorted(METHOD_A.root_condition().roots.real)
    assert np.allclose(roots, [-5.0, 1.0])


def test_method_b_is_consistent_of_order_one_but_not_zero_stable():
    """Chapter 4, Example 2: implicit is not a substitute for zero-stability."""
    assert METHOD_B.is_consistent
    assert METHOD_B.order == 1
    assert not METHOD_B.is_explicit
    assert not METHOD_B.is_zero_stable
    roots = sorted(METHOD_B.root_condition().roots.real)
    assert np.allclose(roots, [1.0, 3.0])


def test_consistency_is_equivalent_to_order_at_least_one():
    for m in [bdf(2), adams_bashforth(3), METHOD_A, METHOD_B, MIDPOINT]:
        assert m.is_consistent == (m.order >= 1)


def test_consistency_conditions_are_rho_one_and_rho_prime_equals_sigma():
    m = bdf(3)
    assert abs(m.rho_at(1.0)) < 1e-12
    assert abs(m.rho_prime_at(1.0) - m.sigma_at(1.0)) < 1e-12


def test_inconsistent_method_is_detected():
    """rho(1) != 0 kills consistency outright."""
    bad = LinearMultistepMethod((-2.0, 1.0), (1.0, 0.0), "inconsistent")
    assert not bad.is_consistent
    assert bad.order == 0


@pytest.mark.parametrize("k", range(1, 7))
def test_bdf_is_zero_stable_up_to_six_steps(k):
    assert bdf(k).is_zero_stable


@pytest.mark.parametrize("k", (7, 8))
def test_bdf_loses_zero_stability_beyond_six_steps(k):
    assert not bdf(k).is_zero_stable


def test_midpoint_is_zero_stable_with_two_simple_roots_on_the_circle():
    rc = MIDPOINT.root_condition()
    assert rc.satisfied
    assert np.allclose(sorted(rc.roots.real), [-1.0, 1.0])


def test_repeated_root_on_the_unit_circle_violates_the_condition():
    """rho(z) = (z - 1)^2 is the classic borderline failure."""
    m = LinearMultistepMethod((1.0, -2.0, 1.0), (0.0, 2.0, 0.0), "double root at 1")
    assert not m.is_zero_stable
    assert m.root_condition().repeated_on_circle.size == 2


@pytest.mark.parametrize("k", range(1, 7))
def test_first_dahlquist_barrier(k):
    """A zero-stable k-step method has order <= k + 2 (k even) or k + 1 (k odd)."""
    bound = k + 2 if k % 2 == 0 else k + 1
    for m in (adams_bashforth(k), adams_moulton(k), bdf(k)):
        if m.is_zero_stable:
            assert m.order <= bound


def test_simpson_attains_the_barrier():
    assert SIMPSON.k == 2
    assert SIMPSON.order == 4 == SIMPSON.k + 2
    assert SIMPSON.is_zero_stable


def test_error_constants_match_reference_values():
    assert bdf(1).error_constant == pytest.approx(-0.5)
    assert bdf(2).error_constant == pytest.approx(-1 / 3)
    assert adams_bashforth(2).error_constant == pytest.approx(5 / 12)
    assert adams_moulton(2).error_constant == pytest.approx(-1 / 24)


def test_second_dahlquist_barrier_no_a_stable_method_above_order_two():
    """A-stable => order <= 2; BDF3 must therefore lose part of the left half-plane."""
    # BDF3 is unstable in a thin wedge hugging the imaginary axis.
    assert not bdf(3).is_absolutely_stable_at(complex(-0.05, 1.0))
    for hlam in (-1.0, -10.0, -1e4, complex(-1.0, 1.0)):
        assert bdf(1).is_absolutely_stable_at(hlam)
        assert bdf(2).is_absolutely_stable_at(hlam)
