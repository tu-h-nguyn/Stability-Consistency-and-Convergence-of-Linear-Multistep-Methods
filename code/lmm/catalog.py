"""A catalogue of linear multistep methods.

Families whose coefficients follow a closed-form construction (BDF, Adams)
are *generated* rather than typed in, so any order can be inspected; the
hand-written entries are the textbook methods and the two deliberately
non-convergent methods studied in Chapter 4 of the report.
"""

from __future__ import annotations

from fractions import Fraction
from math import comb

import numpy as np

from .core import LinearMultistepMethod

__all__ = [
    "bdf",
    "adams_bashforth",
    "adams_moulton",
    "METHOD_A",
    "METHOD_B",
    "EULER_EXPLICIT",
    "EULER_IMPLICIT",
    "TRAPEZOID",
    "MIDPOINT",
    "SIMPSON",
    "CLASSIC_METHODS",
    "get",
]


def bdf(k: int) -> LinearMultistepMethod:
    """The ``k``-step backward differentiation formula.

    Built straight from the defining relation of the report,

    ``sum_{j=1}^{k} (1/j) nabla^j Y_{n+k} = h f_{n+k}``,

    by expanding the backward differences. Zero-stable exactly for
    ``1 <= k <= 6`` -- a fact this project verifies numerically rather than
    assumes.
    """
    if k < 1:
        raise ValueError("k must be at least 1")
    alpha = [Fraction(0)] * (k + 1)
    for j in range(1, k + 1):
        for i in range(j + 1):
            alpha[k - i] += Fraction((-1) ** i * comb(j, i), j)
    beta = [Fraction(0)] * (k + 1)
    beta[k] = Fraction(1)
    return LinearMultistepMethod(
        tuple(float(a) for a in alpha),
        tuple(float(b) for b in beta),
        name=f"BDF{k}",
        description=f"{k}-step backward differentiation formula (implicit, order {k})",
    )


def _lagrange_weights(nodes: list[float]) -> list[float]:
    """Integrals over ``[0, 1]`` of the Lagrange basis on ``nodes``."""
    weights = []
    for j, sj in enumerate(nodes):
        basis = np.poly1d([1.0])
        for i, si in enumerate(nodes):
            if i == j:
                continue
            basis = basis * np.poly1d([1.0, -si]) / (sj - si)
        anti = np.polyint(basis)
        weights.append(float(np.polyval(anti, 1.0) - np.polyval(anti, 0.0)))
    return weights


def adams_bashforth(k: int) -> LinearMultistepMethod:
    """The explicit ``k``-step Adams-Bashforth method (order ``k``)."""
    if k < 1:
        raise ValueError("k must be at least 1")
    alpha = [0.0] * (k + 1)
    alpha[k], alpha[k - 1] = 1.0, -1.0
    nodes = [float(j - (k - 1)) for j in range(k)]  # s-coordinates of t_{n+j}
    beta = [*_lagrange_weights(nodes), 0.0]
    return LinearMultistepMethod(
        tuple(alpha), tuple(beta), name=f"AB{k}",
        description=f"{k}-step Adams-Bashforth method (explicit, order {k})",
    )


def adams_moulton(k: int) -> LinearMultistepMethod:
    """The implicit ``k``-step Adams-Moulton method (order ``k + 1``)."""
    if k < 1:
        raise ValueError("k must be at least 1")
    alpha = [0.0] * (k + 1)
    alpha[k], alpha[k - 1] = 1.0, -1.0
    nodes = [float(j - (k - 1)) for j in range(k + 1)]
    beta = _lagrange_weights(nodes)
    return LinearMultistepMethod(
        tuple(alpha), tuple(beta), name=f"AM{k}",
        description=f"{k}-step Adams-Moulton method (implicit, order {k + 1})",
    )


# --------------------------------------------------------------------------
# Named one-off methods
# --------------------------------------------------------------------------
EULER_EXPLICIT = LinearMultistepMethod(
    (-1.0, 1.0), (1.0, 0.0), "Euler hiện",
    "Y_{n+1} = Y_n + h f_n -- order 1, zero-stable",
)

EULER_IMPLICIT = LinearMultistepMethod(
    (-1.0, 1.0), (0.0, 1.0), "Euler ẩn (BDF1)",
    "Y_{n+1} = Y_n + h f_{n+1} -- order 1, A-stable",
)

TRAPEZOID = LinearMultistepMethod(
    (-1.0, 1.0), (0.5, 0.5), "Quy tắc hình thang (AM1)",
    "Order 2, A-stable, the optimal second-order A-stable method",
)

MIDPOINT = LinearMultistepMethod(
    (-1.0, 0.0, 1.0), (0.0, 2.0, 0.0), "Quy tắc điểm giữa",
    "Order 2 and zero-stable, yet only weakly stable: both roots sit on |z| = 1",
)

SIMPSON = LinearMultistepMethod(
    (-1.0, 0.0, 1.0), (1 / 3, 4 / 3, 1 / 3), "Công thức Simpson",
    "Order 4 with k = 2 -- attains the first Dahlquist barrier, weakly stable",
)

#: Chapter 4, Example 1: consistent of order 3 but the root z = -5 breaks the
#: root condition, so the method diverges.
METHOD_A = LinearMultistepMethod(
    (-5.0, 4.0, 1.0), (2.0, 4.0, 0.0), "Phương pháp A",
    "Y_{n+2} + 4Y_{n+1} - 5Y_n = h(4 f_{n+1} + 2 f_n) -- consistent, NOT zero-stable",
)

#: Chapter 4, Example 2: an implicit method, consistent of order 1, with the
#: parasitic root z = 3.
METHOD_B = LinearMultistepMethod(
    (3.0, -4.0, 1.0), (0.0, 0.0, -2.0), "Phương pháp B",
    "Y_{n+2} - 4Y_{n+1} + 3Y_n = -2h f_{n+2} -- consistent, NOT zero-stable",
)

CLASSIC_METHODS: dict[str, LinearMultistepMethod] = {
    "euler": EULER_EXPLICIT,
    "backward-euler": EULER_IMPLICIT,
    "trapezoid": TRAPEZOID,
    "midpoint": MIDPOINT,
    "simpson": SIMPSON,
    "method-a": METHOD_A,
    "method-b": METHOD_B,
    **{f"bdf{k}": bdf(k) for k in range(1, 7)},
    **{f"ab{k}": adams_bashforth(k) for k in range(1, 5)},
    **{f"am{k}": adams_moulton(k) for k in range(1, 5)},
}


def get(name: str) -> LinearMultistepMethod:
    """Look up a method by its catalogue key (case-insensitive)."""
    key = name.strip().lower()
    if key not in CLASSIC_METHODS:
        raise KeyError(f"unknown method {name!r}; available: {', '.join(sorted(CLASSIC_METHODS))}")
    return CLASSIC_METHODS[key]
