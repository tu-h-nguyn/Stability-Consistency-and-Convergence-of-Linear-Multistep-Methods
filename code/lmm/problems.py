"""Initial value problems used as test beds.

Each problem carries an exact solution, which is what makes the convergence
tables in this project honest: the reported errors are true errors, not
differences against a finer numerical run.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

__all__ = ["IVP", "DECAY", "LOGISTIC", "OSCILLATOR", "STIFF", "PROBLEMS", "get"]


@dataclass(frozen=True)
class IVP:
    """An initial value problem with a known closed-form solution."""

    name: str
    f: Callable[[float, np.ndarray], np.ndarray]
    exact: Callable[[float], np.ndarray]
    t0: float
    T: float
    latex: str = ""

    @property
    def y0(self) -> np.ndarray:
        return np.atleast_1d(np.asarray(self.exact(self.t0), dtype=float))

    @property
    def t_span(self) -> tuple[float, float]:
        return (self.t0, self.T)


#: The test equation of the report: y' = -y, y(0) = 1.
DECAY = IVP(
    name="phân rã mũ",
    f=lambda t, y: -y,
    exact=lambda t: np.exp(-t),
    t0=0.0,
    T=6.0,
    latex=r"y' = -y,\ y(0) = 1,\quad y(t) = e^{-t}",
)

#: A genuinely nonlinear problem, so implicit methods must actually iterate.
LOGISTIC = IVP(
    name="logistic",
    f=lambda t, y: y * (1.0 - y),
    exact=lambda t: 1.0 / (1.0 + 9.0 * np.exp(-t)),
    t0=0.0,
    T=8.0,
    latex=r"y' = y(1-y),\ y(0) = 0.1",
)

#: A 2x2 system with purely imaginary eigenvalues -- weakly stable methods
#: such as the explicit midpoint rule show their parasitic behaviour here.
OSCILLATOR = IVP(
    name="dao động điều hoà",
    f=lambda t, y: np.array([y[1], -y[0]]),
    exact=lambda t: np.array([np.sin(t), np.cos(t)]),
    t0=0.0,
    T=20.0,
    latex=r"y'' = -y \Leftrightarrow (y_1, y_2)' = (y_2, -y_1)",
)

#: A stiff problem: the transient decays 1000x faster than the smooth part.
STIFF = IVP(
    name="bài toán cứng (stiff)",
    f=lambda t, y: -1000.0 * (y - np.cos(t)) - np.sin(t),
    exact=lambda t: np.cos(t),
    t0=0.0,
    T=2.0,
    latex=r"y' = -1000\,(y - \cos t) - \sin t,\ y(0) = 1",
)

PROBLEMS: dict[str, IVP] = {
    "decay": DECAY,
    "logistic": LOGISTIC,
    "oscillator": OSCILLATOR,
    "stiff": STIFF,
}


def get(name: str) -> IVP:
    key = name.strip().lower()
    if key not in PROBLEMS:
        raise KeyError(f"unknown problem {name!r}; available: {', '.join(sorted(PROBLEMS))}")
    return PROBLEMS[key]
