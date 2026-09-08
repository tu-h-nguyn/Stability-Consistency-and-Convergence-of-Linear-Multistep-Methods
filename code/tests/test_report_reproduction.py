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
