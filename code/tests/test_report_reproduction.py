"""The published tables of the report must come back out of the library.

The values below are transcribed from Chapter 4 of the PDF, which were produced
by the MATLAB code in ``matlab/``. Reproducing them here to six significant
digits means the Python implementation and the original MATLAB implementation
agree, and that the report's numbers are still the numbers the code produces.
``matlab/verify.sh`` checks the same values from the MATLAB side.
"""

import numpy as np
import pytest

from lmm.catalog import METHOD_A, METHOD_B, bdf
from lmm.problems import DECAY

H = 0.1

# t -> Y_n as printed in the report.
METHOD_A_TABLE = {
    0.5: 6.081996e-01,
    1.0: -6.677259e00,
    2.0: -1.243391e08,
    4.0: -3.872979e22,
    6.0: -1.206376e37,
}

METHOD_B_TABLE = {
    0.5: -4.362861e00,
    1.0: -5.683881e03,
    2.0: -7.286041e09,
    4.0: -1.197068e22,
    6.0: -1.966737e34,
}

# Errors at T = 2 printed by matlab/bdf_convergence.m for h = 0.1.
BDF_ERRORS_AT_H_0_1 = {1: 1.3308e-02, 2: 9.0148e-04, 3: 6.6843e-05}


def _solution_at(method, checkpoints):
    sol = method.solve(DECAY.f, DECAY.t_span, H, startup=DECAY.exact)
    return {t: sol.y[int(np.argmin(np.abs(sol.t - t)))] for t in checkpoints}


@pytest.mark.parametrize(
    ("method", "table"),
    [(METHOD_A, METHOD_A_TABLE), (METHOD_B, METHOD_B_TABLE)],
    ids=["method-a", "method-b"],
)
def test_python_reproduces_the_published_matlab_table(method, table):
    got = _solution_at(method, table)
    for t, expected in table.items():
        assert got[t] == pytest.approx(expected, rel=1e-6), f"t = {t}"


@pytest.mark.parametrize("k", sorted(BDF_ERRORS_AT_H_0_1))
def test_python_reproduces_the_matlab_bdf_errors(k):
    """Same problem, same step, same startup as matlab/bdf_convergence.m."""
    sol = bdf(k).solve(DECAY.f, (0.0, 2.0), H, startup=DECAY.exact)
    error = abs(sol.y[-1] - np.exp(-2.0))
    assert error == pytest.approx(BDF_ERRORS_AT_H_0_1[k], rel=1e-4)


# The characteristic polynomial each method induces on y' = -y, as derived in
# Chapter 4. Substituting f = -Y moves the h terms across with a plus sign.
CHARACTERISTIC = {
    # method A: Y_{n+2} + 4(1+h) Y_{n+1} - (5-2h) Y_n = 0
    "method-a": lambda h: [1.0, 4.0 * (1.0 + h), -(5.0 - 2.0 * h)],
    # method B: (1-2h) Y_{n+2} - 4 Y_{n+1} + 3 Y_n = 0
    "method-b": lambda h: [1.0 - 2.0 * h, -4.0, 3.0],
}


def _measured_growth(method, h=H):
    """Per-step ratio |E_{n+1}| / |E_n| once the parasitic mode dominates."""
    sol = method.solve(DECAY.f, DECAY.t_span, h, startup=DECAY.exact)
    exact = np.array([DECAY.exact(t) for t in sol.t]).ravel()
    err = np.abs(sol.y - exact)
    return float(np.mean(err[25:50] / err[24:49]))


@pytest.mark.parametrize(
    ("key", "method"), [("method-a", METHOD_A), ("method-b", METHOD_B)]
)
def test_characteristic_root_predicts_the_observed_error_growth(key, method):
    """The algebra in the report must match what the integrator actually does.

    This is the test that catches a sign slip. The published derivation of
    method A once read ``4(1-h)`` and ``-(5+2h)``, which predicts a growth of
    4.705 and a *growing* principal root for a decaying problem; the solver
    grows the error by 5.305 per step, and the corrected polynomial gives
    exactly that, with a principal root equal to e^{-h}.
    """
    roots = np.roots(CHARACTERISTIC[key](H))
    parasitic = max(abs(roots))
    assert _measured_growth(method) == pytest.approx(parasitic, rel=1e-3)


def test_method_a_principal_root_reproduces_the_exact_decay():
    """The non-parasitic root must approximate e^{-h} for y' = -y."""
    roots = np.roots(CHARACTERISTIC["method-a"](H))
    principal = min(abs(roots))
    assert principal == pytest.approx(np.exp(-H), abs=5e-5)


def test_characteristic_polynomials_reduce_to_rho_when_h_is_zero():
    """At h = 0 the difference equation must collapse back onto rho."""
    for key, method in (("method-a", METHOD_A), ("method-b", METHOD_B)):
        got = np.array(CHARACTERISTIC[key](0.0), dtype=float)
        assert np.allclose(got / got[0], method.rho / method.rho[0])
