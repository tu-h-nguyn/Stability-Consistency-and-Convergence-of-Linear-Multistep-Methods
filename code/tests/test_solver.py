"""The integrator itself: startup, implicit solves, systems, and convergence."""

import numpy as np
import pytest

from lmm.analysis import convergence_study
from lmm.catalog import (
    EULER_EXPLICIT,
    METHOD_A,
    METHOD_B,
    TRAPEZOID,
    adams_bashforth,
    adams_moulton,
    bdf,
)
from lmm.problems import DECAY, LOGISTIC, OSCILLATOR, STIFF

STEPS = [0.1, 0.05, 0.025, 0.0125, 0.00625]
#: Higher-order methods reach the round-off floor (~1e-12) on this problem before
#: the finest step, so their order is measured on a coarser sequence.
COARSE_STEPS = [0.2, 0.1, 0.05, 0.025]


def test_forward_euler_reproduces_its_closed_form():
    sol = EULER_EXPLICIT.solve(DECAY.f, (0.0, 1.0), 0.1, y0=1.0)
    assert np.allclose(sol.y, (1 - 0.1) ** np.arange(11))


def test_backward_euler_reproduces_its_closed_form():
    sol = bdf(1).solve(DECAY.f, (0.0, 1.0), 0.1, y0=1.0)
    assert np.allclose(sol.y, (1 / 1.1) ** np.arange(11))


def test_implicit_solver_handles_a_nonlinear_right_hand_side():
    sol = adams_moulton(2).solve(LOGISTIC.f, LOGISTIC.t_span, 0.05, startup=LOGISTIC.exact)
    assert sol.newton_iterations > 0
    assert sol.error_against(LOGISTIC.exact)[-1] < 1e-6


@pytest.mark.parametrize(
    ("method", "steps"),
    [
        (bdf(1), STEPS),
        (bdf(2), STEPS),
        (bdf(3), STEPS),
        (bdf(4), COARSE_STEPS),
        (adams_bashforth(2), STEPS),
        (adams_bashforth(3), STEPS),
        (adams_moulton(2), STEPS),
        (adams_moulton(3), COARSE_STEPS),
    ],
    ids=lambda arg: arg.name if hasattr(arg, "name") else "",
)
def test_observed_order_matches_theoretical_order(method, steps):
    """The decisive check: measured slope must land on p, within 0.25."""
    study = convergence_study(method, LOGISTIC, steps)
    assert study.estimated_order == pytest.approx(method.order, abs=0.25)


@pytest.mark.parametrize("method", [METHOD_A, METHOD_B], ids=lambda m: m.name)
def test_non_zero_stable_methods_blow_up_however_small_the_step(method):
    """Refining h does not help: this is Dahlquist's theorem seen numerically."""
    study = convergence_study(method, DECAY, STEPS)
    assert np.all(study.errors > 1e3)
    assert study.estimated_order < 0.5


def test_rk4_startup_does_not_degrade_a_low_order_method():
    with_exact = convergence_study(bdf(2), LOGISTIC, STEPS, exact_startup=True)
    with_rk4 = convergence_study(bdf(2), LOGISTIC, STEPS, exact_startup=False)
    assert with_rk4.estimated_order == pytest.approx(with_exact.estimated_order, abs=0.2)


def test_systems_are_integrated_componentwise():
    sol = bdf(2).solve(OSCILLATOR.f, (0.0, 2 * np.pi), 0.01, startup=OSCILLATOR.exact)
    assert sol.y.shape == (len(sol.t), 2)
    assert sol.error_against(OSCILLATOR.exact)[-1] < 1e-3


def test_bdf_survives_a_stiff_problem_at_a_step_an_explicit_method_cannot_take():
    """h = 0.05 is far outside AB2's stability region for lambda = -1000."""
    h = 0.05
    stable = bdf(2).solve(STIFF.f, STIFF.t_span, h, startup=STIFF.exact)
    unstable = adams_bashforth(2).solve(STIFF.f, STIFF.t_span, h, startup=STIFF.exact)
    assert stable.error_against(STIFF.exact)[-1] < 1e-2
    assert unstable.error_against(STIFF.exact)[-1] > 1e3


def test_divergence_is_flagged_instead_of_producing_nan():
    sol = METHOD_A.solve(DECAY.f, (0.0, 20.0), 0.1, startup=DECAY.exact)
    assert sol.diverged
    assert np.all(np.isfinite(sol.y))


def test_trapezoid_preserves_the_oscillator_amplitude():
    """A-stable and symmetric: no artificial damping over many periods."""
    sol = TRAPEZOID.solve(OSCILLATOR.f, (0.0, 200.0), 0.05, startup=OSCILLATOR.exact)
    amplitude = np.linalg.norm(sol.y, axis=1)
    assert np.allclose(amplitude, 1.0, atol=1e-3)


def test_startup_values_are_validated():
    with pytest.raises(ValueError):
        bdf(3).solve(DECAY.f, (0.0, 1.0), 0.1, startup=[1.0])
    with pytest.raises(ValueError):
        bdf(2).solve(DECAY.f, (0.0, 1.0), 0.1)
    with pytest.raises(ValueError):
        bdf(2).solve(DECAY.f, (0.0, 1.0), 1.0, y0=1.0)
