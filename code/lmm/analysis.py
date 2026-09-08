"""Numerical experiments that turn the theory into measurable quantities."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .core import LinearMultistepMethod
from .problems import IVP

__all__ = ["ConvergenceStudy", "convergence_study", "method_table"]


@dataclass
class ConvergenceStudy:
    """Global error at the end point for a sequence of step sizes."""

    method: LinearMultistepMethod
    problem: IVP
    steps: np.ndarray
    errors: np.ndarray
    exact_startup: bool

    @property
    def observed_orders(self) -> np.ndarray:
        """``log2`` of consecutive error ratios for a halving step sequence."""
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.log(self.errors[:-1] / self.errors[1:]) / np.log(
                self.steps[:-1] / self.steps[1:]
            )

    @property
    def estimated_order(self) -> float:
        """Least-squares slope of ``log(error)`` against ``log(h)``."""
        mask = np.isfinite(self.errors) & (self.errors > 0)
        if mask.sum() < 2:
            return float("nan")
        slope, _ = np.polyfit(np.log(self.steps[mask]), np.log(self.errors[mask]), 1)
        return float(slope)

    def as_rows(self) -> list[tuple[float, float, float]]:
        orders = np.concatenate([[np.nan], self.observed_orders])
        return list(zip(self.steps.tolist(), self.errors.tolist(), orders.tolist()))

    def to_markdown(self) -> str:
        head = "| h | sai số tại T | bậc quan sát |\n|---:|---:|---:|"
        body = "\n".join(
            f"| {h:.5g} | {e:.4e} | {'-' if np.isnan(p) else f'{p:.2f}'} |"
            for h, e, p in self.as_rows()
        )
        return f"{head}\n{body}"


def convergence_study(
    method: LinearMultistepMethod,
    problem: IVP,
    steps,
    exact_startup: bool = True,
) -> ConvergenceStudy:
    """Measure the global error at ``T`` for each step size in ``steps``.

    ``exact_startup=True`` seeds the method with values from the analytic
    solution, isolating the method's own error; otherwise RK4 provides them,
    which is what a real implementation would do.
    """
    steps = np.asarray(list(steps), dtype=float)
    errors = np.empty_like(steps)
    for i, h in enumerate(steps):
        sol = method.solve(
            problem.f,
            problem.t_span,
            float(h),
            startup=problem.exact if exact_startup else None,
            y0=None if exact_startup else problem.y0,
        )
        err = sol.error_against(problem.exact)
        errors[i] = err[-1] if np.isfinite(err[-1]) else np.inf
    return ConvergenceStudy(method, problem, steps, errors, exact_startup)


def method_table(methods) -> str:
    """A Markdown table of the structural properties of several methods."""
    head = (
        "| phương pháp | k | loại | bậc p | C_{p+1} (α_k=1) | nhất quán | 0-ổn định | hội tụ |\n"
        "|---|---:|---|---:|---:|:---:|:---:|:---:|"
    )
    rows = []
    for m in methods:
        # Scale-independent convention: coefficients normalised so that alpha_k = 1.
        constant = m.normalised().error_constant
        rows.append(
            f"| {m.name} | {m.k} | {'hiện' if m.is_explicit else 'ẩn'} | {m.order} | "
            f"{constant:+.4g} | {'✅' if m.is_consistent else '❌'} | "
            f"{'✅' if m.is_zero_stable else '❌'} | {'✅' if m.is_convergent else '❌'} |"
        )
    return head + "\n" + "\n".join(rows)
