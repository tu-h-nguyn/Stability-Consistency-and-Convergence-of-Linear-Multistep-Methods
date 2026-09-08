"""Core abstractions for linear multistep methods (LMM).

A linear multistep method with ``k`` steps applied to the initial value problem

.. math::

    y'(t) = f(t, y(t)), \\qquad y(t_0) = y_0,

is written throughout this project in the normalised form

.. math::

    \\sum_{j=0}^{k} \\alpha_j\\, Y_{n+j} = h \\sum_{j=0}^{k} \\beta_j\\, f_{n+j},
    \\qquad f_{n+j} = f(t_{n+j}, Y_{n+j}).

Everything the report proves by hand -- consistency, order, the error
constant, the root condition and zero-stability -- is derived here directly
from the coefficient vectors ``alpha`` and ``beta``, so the theory and the
numerics can never drift apart.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

import numpy as np

__all__ = ["LinearMultistepMethod", "Solution", "RootConditionReport"]

#: Roots of modulus within this tolerance of 1 count as lying *on* the unit circle.
UNIT_CIRCLE_TOL = 1e-8


@dataclass(frozen=True)
class RootConditionReport:
    """Outcome of testing Dahlquist's root condition on the polynomial rho."""

    roots: np.ndarray
    satisfied: bool
    strictly_outside: np.ndarray
    repeated_on_circle: np.ndarray

    def __str__(self) -> str:  # pragma: no cover - presentation only
        lines = [f"root condition: {'SATISFIED' if self.satisfied else 'VIOLATED'}"]
        for z in self.roots:
            tag = ""
            if any(abs(z - w) < UNIT_CIRCLE_TOL for w in self.strictly_outside):
                tag = "  <- |z| > 1"
            elif any(abs(z - w) < UNIT_CIRCLE_TOL for w in self.repeated_on_circle):
                tag = "  <- repeated root on |z| = 1"
            lines.append(f"  z = {z.real:+.6f} {z.imag:+.6f}i   |z| = {abs(z):.6f}{tag}")
        return "\n".join(lines)


@dataclass
class Solution:
    """Result of integrating an IVP with a linear multistep method."""

    t: np.ndarray
    y: np.ndarray
    method: LinearMultistepMethod
    h: float
    newton_iterations: int = 0
    newton_failures: int = 0
    diverged: bool = False

    @property
    def y_final(self) -> np.ndarray:
        return self.y[-1]

    def error_against(self, exact: Callable[[float], object]) -> np.ndarray:
        """Absolute error (Euclidean norm per time level) against ``exact``."""
        ref = np.array([np.atleast_1d(np.asarray(exact(t), dtype=float)) for t in self.t])
        diff = np.atleast_2d(self.y.reshape(len(self.t), -1)) - ref.reshape(len(self.t), -1)
        with np.errstate(over="ignore", invalid="ignore"):
            return np.linalg.norm(diff, axis=1)


@dataclass(frozen=True)
class LinearMultistepMethod:
    """An explicit or implicit linear multistep method defined by its coefficients.

    Parameters
    ----------
    alpha, beta:
        Coefficients indexed from ``0`` to ``k``; ``alpha[j]`` multiplies
        ``Y_{n+j}`` and ``beta[j]`` multiplies ``h f_{n+j}``.
    name:
        Human readable label used in plots and tables.
    """

    alpha: tuple[float, ...]
    beta: tuple[float, ...]
    name: str = "LMM"
    description: str = ""
    _cache: dict = field(default_factory=dict, compare=False, repr=False, hash=False)

    def __post_init__(self) -> None:
        if len(self.alpha) != len(self.beta):
            raise ValueError("alpha and beta must have the same length (k + 1 entries)")
        if len(self.alpha) < 2:
            raise ValueError("a linear multistep method needs at least one step")
        if abs(self.alpha[-1]) < 1e-14:
            raise ValueError("alpha_k must be non-zero, otherwise the method has fewer steps")
        object.__setattr__(self, "alpha", tuple(float(a) for a in self.alpha))
        object.__setattr__(self, "beta", tuple(float(b) for b in self.beta))

    # ------------------------------------------------------------------
    # Structure
    # ------------------------------------------------------------------
    @property
    def k(self) -> int:
        """Number of steps."""
        return len(self.alpha) - 1

    @property
    def is_explicit(self) -> bool:
        return abs(self.beta[-1]) < 1e-14

    @property
    def rho(self) -> np.ndarray:
        """Coefficients of the first characteristic polynomial, highest power first."""
        return np.array(self.alpha[::-1], dtype=float)

    @property
    def sigma(self) -> np.ndarray:
        """Coefficients of the second characteristic polynomial, highest power first."""
        return np.array(self.beta[::-1], dtype=float)

    def rho_at(self, z: complex) -> complex:
        return np.polyval(self.rho, z)

    def sigma_at(self, z: complex) -> complex:
        return np.polyval(self.sigma, z)

    def rho_prime_at(self, z: complex) -> complex:
        return np.polyval(np.polyder(self.rho), z)

    def normalised(self) -> LinearMultistepMethod:
        """Return the same method scaled so that ``alpha_k = 1``."""
        s = self.alpha[-1]
        return LinearMultistepMethod(
            tuple(a / s for a in self.alpha),
            tuple(b / s for b in self.beta),
            self.name,
            self.description,
        )

    # ------------------------------------------------------------------
    # Consistency and order (linear difference operator)
    # ------------------------------------------------------------------
    def residual(self, q: int) -> float:
        """The coefficient ``C_q`` of the linear difference operator.

        With ``C_0 = sum alpha_j`` and, for ``q >= 1``,

        ``C_q = (1/q!) sum j^q alpha_j - (1/(q-1)!) sum j^(q-1) beta_j``.

        Applying the operator to a smooth ``y`` gives
        ``L[y; h] = C_0 y + C_1 h y' + C_2 h^2 y'' + ...``
        """
        if q < 0:
            raise ValueError("q must be non-negative")
        js = np.arange(self.k + 1, dtype=float)
        if q == 0:
            return float(np.sum(self.alpha))
        first = np.sum(js**q * np.asarray(self.alpha)) / math.factorial(q)
        second = np.sum(js ** (q - 1) * np.asarray(self.beta)) / math.factorial(q - 1)
        return float(first - second)

    def error_constants(self, up_to: int | None = None) -> list[float]:
        up_to = up_to if up_to is not None else 2 * self.k + 3
        return [self.residual(q) for q in range(up_to + 1)]

    @property
    def order(self) -> int:
        """Order of consistency ``p``: the largest ``p`` with ``C_0 = ... = C_p = 0``."""
        if "order" not in self._cache:
            tol = 1e-10
            p = -1
            for q in range(0, 2 * self.k + 4):
                if abs(self.residual(q)) > tol:
                    break
                p = q
            self._cache["order"] = max(p, 0) if p >= 0 else 0
        return self._cache["order"]

    @property
    def error_constant(self) -> float:
        """The leading error coefficient ``C_{p+1}``."""
        return self.residual(self.order + 1)

    @property
    def normalised_error_constant(self) -> float:
        """``C_{p+1} / sigma(1)`` -- the constant used to compare methods of equal order."""
        s1 = self.sigma_at(1.0)
        return float("nan") if abs(s1) < 1e-14 else self.error_constant / s1

    @property
    def is_consistent(self) -> bool:
        """Consistency: ``rho(1) = 0`` and ``rho'(1) = sigma(1)``, i.e. order >= 1."""
        return (
            abs(self.rho_at(1.0)) < 1e-10
            and abs(self.rho_prime_at(1.0) - self.sigma_at(1.0)) < 1e-10
        )

    # ------------------------------------------------------------------
    # Zero-stability
    # ------------------------------------------------------------------
    def root_condition(self) -> RootConditionReport:
        """Test Dahlquist's root condition on ``rho``.

        Every root must satisfy ``|z| <= 1`` and every root of modulus one must
        be simple.
        """
        roots = np.roots(self.rho)
        outside = np.array([z for z in roots if abs(z) > 1 + UNIT_CIRCLE_TOL])
        repeated = []
        for i, z in enumerate(roots):
            if abs(abs(z) - 1.0) > UNIT_CIRCLE_TOL:
                continue
            for j, w in enumerate(roots):
                if i != j and abs(z - w) < 1e-6:
                    repeated.append(z)
                    break
        repeated_arr = np.array(repeated)
        satisfied = outside.size == 0 and repeated_arr.size == 0
        return RootConditionReport(roots, bool(satisfied), outside, repeated_arr)

    @property
    def is_zero_stable(self) -> bool:
        return self.root_condition().satisfied

    @property
    def is_convergent(self) -> bool:
        """Dahlquist equivalence theorem: convergent <=> consistent and zero-stable."""
        return self.is_consistent and self.is_zero_stable

    # ------------------------------------------------------------------
    # Absolute stability
    # ------------------------------------------------------------------
    def boundary_locus(self, n_points: int = 1000) -> np.ndarray:
        """Boundary of the region of absolute stability.

        The image of the unit circle under ``z -> rho(z) / sigma(z)`` bounds the
        set of ``h*lambda`` for which the method damps the test equation
        ``y' = lambda y``.
        """
        theta = np.linspace(0.0, 2.0 * np.pi, n_points)
        z = np.exp(1j * theta)
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.polyval(self.rho, z) / np.polyval(self.sigma, z)

    def is_absolutely_stable_at(self, hlam: complex) -> bool:
        """Are all roots of ``rho(z) - h*lambda*sigma(z)`` inside the unit disc?"""
        poly = self.rho - hlam * self.sigma
        poly = np.trim_zeros(poly, "f")
        if poly.size < 2:
            return False
        return bool(np.all(np.abs(np.roots(poly)) < 1.0 - 1e-12))

    # ------------------------------------------------------------------
    # Integration
    # ------------------------------------------------------------------
    def solve(
        self,
        f: Callable[[float, np.ndarray], np.ndarray],
        t_span: tuple[float, float],
        h: float,
        startup: Sequence | Callable[[float], object] | None = None,
        y0=None,
        newton_tol: float = 1e-12,
        max_newton: int = 50,
        overflow_limit: float = 1e50,
    ) -> Solution:
        """Integrate ``y' = f(t, y)`` on ``t_span`` with fixed step ``h``.

        Parameters
        ----------
        startup:
            Either the ``k`` starting values ``Y_0, ..., Y_{k-1}`` or a callable
            (typically the exact solution) evaluated on the first ``k`` nodes.
            When omitted, the starting values are produced by classical RK4 from
            ``y0`` so that the startup error never masks the method's own
            behaviour.
        """
        t0, T = t_span
        n_steps = round((T - t0) / h)
        if n_steps < self.k:
            raise ValueError("step size too large: fewer grid points than steps of the method")
        t = t0 + h * np.arange(n_steps + 1)

        start = self._startup_values(f, t, h, startup, y0)
        dim = start.shape[1]
        y = np.zeros((n_steps + 1, dim), dtype=float)
        y[: self.k] = start

        fvals = np.zeros_like(y)
        for i in range(self.k):
            fvals[i] = np.atleast_1d(np.asarray(f(t[i], y[i]), dtype=float))

        a_k, b_k = self.alpha[-1], self.beta[-1]
        newton_iters = 0
        newton_failures = 0
        diverged = False

        for n in range(n_steps + 1 - self.k):
            m = n + self.k  # index of the new value
            rhs = np.zeros(dim)
            for j in range(self.k):
                rhs += -self.alpha[j] * y[n + j] + h * self.beta[j] * fvals[n + j]

            if self.is_explicit:
                y[m] = rhs / a_k
            else:
                guess = y[m - 1] + (y[m - 1] - y[m - 2]) if self.k > 1 else y[m - 1].copy()
                y[m], iters, converged = _newton_step(
                    f, t[m], guess, rhs, a_k, h * b_k, newton_tol, max_newton
                )
                newton_iters += iters
                newton_failures += 0 if converged else 1

            if not np.all(np.isfinite(y[m])) or np.max(np.abs(y[m])) > overflow_limit:
                diverged = True
                y[m:] = y[m]
                break
            fvals[m] = np.atleast_1d(np.asarray(f(t[m], y[m]), dtype=float))

        out = y[:, 0] if dim == 1 else y
        return Solution(
            t=t,
            y=out,
            method=self,
            h=h,
            newton_iterations=newton_iters,
            newton_failures=newton_failures,
            diverged=diverged,
        )

    def _startup_values(self, f, t, h, startup, y0) -> np.ndarray:
        if startup is None:
            if y0 is None:
                raise ValueError("provide either `startup` values or an initial value `y0`")
            return _rk4_startup(f, t, h, np.atleast_1d(np.asarray(y0, dtype=float)), self.k)
        if callable(startup):
            return np.array(
                [np.atleast_1d(np.asarray(startup(t[i]), dtype=float)) for i in range(self.k)]
            )
        arr = np.array([np.atleast_1d(np.asarray(v, dtype=float)) for v in startup])
        if arr.shape[0] != self.k:
            raise ValueError(f"{self.k} starting values are required, got {arr.shape[0]}")
        return arr

    # ------------------------------------------------------------------
    def summary(self) -> str:
        """One-screen report mirroring the checks performed in the write-up."""
        rc = self.root_condition()
        verdict = "CONVERGENT" if self.is_convergent else "NOT convergent"
        lines = [
            f"{self.name}  ({'explicit' if self.is_explicit else 'implicit'}, k = {self.k})",
            f"  rho(z) = {_poly_to_string(self.rho)}",
            f"  sigma(z) = {_poly_to_string(self.sigma)}",
            f"  rho(1) = {self.rho_at(1.0):+.3g},  rho'(1) = {self.rho_prime_at(1.0):+.3g},"
            f"  sigma(1) = {self.sigma_at(1.0):+.3g}",
            f"  consistent: {self.is_consistent}   order p = {self.order}"
            f"   error constant C_{{p+1}} = {self.error_constant:+.6g}",
            "  " + str(rc).replace("\n", "\n  "),
            f"  Dahlquist verdict: {verdict}",
        ]
        return "\n".join(lines)


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------
def _newton_step(f, t_new, guess, rhs, a_k, hb_k, tol, max_iter):
    """Solve ``a_k * Y - h*b_k*f(t_new, Y) = rhs`` by Newton with an FD Jacobian.

    Returns the iterate, the number of iterations spent, and whether the
    residual test was actually met -- a caller that ignores the last flag would
    not notice a step that quietly failed to converge.
    """
    y = np.array(guess, dtype=float)
    dim = y.size
    for it in range(1, max_iter + 1):
        fy = np.atleast_1d(np.asarray(f(t_new, y), dtype=float))
        residual = a_k * y - hb_k * fy - rhs
        if np.linalg.norm(residual) <= tol * (1.0 + np.linalg.norm(y)):
            return y, it, True
        jac = np.eye(dim) * a_k - hb_k * _fd_jacobian(f, t_new, y, fy)
        try:
            delta = np.linalg.solve(jac, -residual)
        except np.linalg.LinAlgError:
            delta = -np.linalg.lstsq(jac, residual, rcond=None)[0]
        y = y + delta
        if not np.all(np.isfinite(y)):
            return y, it, False
    return y, max_iter, False


def _fd_jacobian(f, t, y, fy):
    dim = y.size
    jac = np.empty((dim, dim))
    for i in range(dim):
        step = 1e-8 * max(1.0, abs(y[i]))
        pert = y.copy()
        pert[i] += step
        jac[:, i] = (np.atleast_1d(np.asarray(f(t, pert), dtype=float)) - fy) / step
    return jac


def _rk4_startup(f, t, h, y0, k) -> np.ndarray:
    """Generate the ``k`` starting values with classical RK4 (order 4)."""
    out = [np.array(y0, dtype=float)]
    for i in range(k - 1):
        y = out[-1]
        ti = t[i]
        k1 = np.atleast_1d(np.asarray(f(ti, y), dtype=float))
        k2 = np.atleast_1d(np.asarray(f(ti + h / 2, y + h / 2 * k1), dtype=float))
        k3 = np.atleast_1d(np.asarray(f(ti + h / 2, y + h / 2 * k2), dtype=float))
        k4 = np.atleast_1d(np.asarray(f(ti + h, y + h * k3), dtype=float))
        out.append(y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4))
    return np.array(out)


def _poly_to_string(coeffs: np.ndarray) -> str:
    deg = len(coeffs) - 1
    terms = []
    for i, c in enumerate(coeffs):
        power = deg - i
        if abs(c) < 1e-14:
            continue
        mag = abs(c)
        body = "" if power == 0 else ("z" if power == 1 else f"z^{power}")
        coefficient = "" if (abs(mag - 1) < 1e-14 and power > 0) else f"{mag:g}"
        sign = "- " if c < 0 else ("" if not terms else "+ ")
        terms.append(f"{sign}{coefficient}{body}")
    return " ".join(terms) if terms else "0"
