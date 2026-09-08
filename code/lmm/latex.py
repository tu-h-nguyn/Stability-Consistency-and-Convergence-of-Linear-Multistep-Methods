"""Emit LaTeX tables so the report can never drift from the code.

The report ``\\input``s the files written here, which means every number
printed in Chapter 3 and Chapter 4 is produced by the same routines the test
suite checks. Regenerate them with ``make figures``.
"""

from __future__ import annotations

import math
from fractions import Fraction
from pathlib import Path

import numpy as np

from .analysis import ConvergenceStudy
from .core import LinearMultistepMethod

__all__ = ["sci", "frac", "convergence_table", "method_table", "bdf_stability_table", "write"]

GENERATED_DIR = Path(__file__).resolve().parents[2] / "Sections" / "generated"

BANNER = (
    "% !!! TỆP NÀY ĐƯỢC SINH TỰ ĐỘNG — MỌI CHỈNH SỬA THỦ CÔNG SẼ BỊ GHI ĐÈ !!!\n"
    "% Nguồn: code/experiments/ex07_report_tables.py  (chạy lại bằng: make figures)\n"
)


def sci(x: float, digits: int = 3) -> str:
    """Format a float as ``a.bcd \\times 10^{e}`` for maths mode."""
    if x == 0 or not math.isfinite(x):
        return "0" if x == 0 else r"\infty"
    exponent = int(math.floor(math.log10(abs(x))))
    mantissa = x / 10.0**exponent
    if exponent == 0:
        return f"{mantissa:.{digits}f}"
    return rf"{mantissa:.{digits}f}\times 10^{{{exponent}}}"


def frac(x: float, max_denominator: int = 10_000) -> str:
    """Render a float as an exact fraction when it is one, else as a decimal.

    Error constants of the classical methods are small rationals (-1/12, 5/12,
    -1/90, ...), and printing them as fractions is both shorter and closer to
    how the reference tables state them.
    """
    if not math.isfinite(x):
        return r"\infty"
    r = Fraction(x).limit_denominator(max_denominator)
    if abs(float(r) - x) > 1e-12 * max(1.0, abs(x)):
        return sci(x, 4)
    sign = "-" if r < 0 else ""
    n, d = abs(r.numerator), r.denominator
    # \tfrac keeps table rows at their normal height; \dfrac makes them collide.
    return f"{sign}{n}" if d == 1 else rf"{sign}\tfrac{{{n}}}{{{d}}}"


def convergence_table(studies: list[ConvergenceStudy], caption: str, label: str) -> str:
    """Global error at ``T`` for several methods over a shared step sequence."""
    if not studies:
        raise ValueError("at least one study is required")
    steps = studies[0].steps
    for s in studies:
        if not np.allclose(s.steps, steps):
            raise ValueError("every study must use the same step sequence")

    cols = "c" + "c" * len(studies)
    head = " & ".join(rf"\textbf{{{s.method.name}}}" for s in studies)
    orders = " & ".join(f"$p={s.method.order}$" for s in studies)
    lines = [
        r"\begin{table}[H]",
        r"\centering",
        rf"\caption{{{caption}}}",
        rf"\label{{{label}}}",
        r"\renewcommand{\arraystretch}{1.2}",
        rf"\begin{{tabular}}{{{cols}}}",
        r"\toprule",
        rf"$h$ & {head}\\",
        rf" & {orders}\\",
        r"\midrule",
    ]
    for i, h in enumerate(steps):
        cells = " & ".join(f"${sci(s.errors[i])}$" for s in studies)
        lines.append(rf"${h:g}$ & {cells}\\")
    lines.append(r"\midrule")
    measured = " & ".join(f"${s.estimated_order:.3f}$" for s in studies)
    lines += [
        rf"\textbf{{bậc đo được}} & {measured}\\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ]
    return "\n".join(lines)


def method_table(methods: list[LinearMultistepMethod], caption: str, label: str) -> str:
    """Structural summary: order, error constant, consistency, zero-stability."""
    lines = [
        r"\begin{table}[H]",
        r"\centering",
        rf"\caption{{{caption}}}",
        rf"\label{{{label}}}",
        r"\renewcommand{\arraystretch}{1.25}",
        r"\begin{tabular}{lccccccc}",
        r"\toprule",
        r"Phương pháp & $k$ & Loại & $p$ & $C_{p+1}$ & Nhất quán & 0-ổn định & Hội tụ\\",
        r"\midrule",
    ]
    yes, no = r"\checkmark", r"$\times$"
    for m in methods:
        # The error constant depends on how (alpha, beta) are scaled, so it is
        # reported for the canonical normalisation alpha_k = 1.
        constant = m.normalised().error_constant
        lines.append(
            rf"{m.name} & {m.k} & {'hiện' if m.is_explicit else 'ẩn'} & {m.order} & "
            rf"${frac(constant)}$ & {yes if m.is_consistent else no} & "
            rf"{yes if m.is_zero_stable else no} & {yes if m.is_convergent else no}\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines)


def bdf_stability_table(methods: list[LinearMultistepMethod], caption: str, label: str) -> str:
    """The k <= 6 limit of the BDF family, read off the roots of rho."""
    lines = [
        r"\begin{table}[H]",
        r"\centering",
        rf"\caption{{{caption}}}",
        rf"\label{{{label}}}",
        r"\renewcommand{\arraystretch}{1.25}",
        r"\begin{tabular}{cccc}",
        r"\toprule",
        r"$k$ & Bậc $p$ & $\max_i |z_i|$ & Kết luận\\",
        r"\midrule",
    ]
    for m in methods:
        r_max = float(np.max(np.abs(m.root_condition().roots)))
        verdict = "0-ổn định" if m.is_zero_stable else r"\textbf{không 0-ổn định}"
        lines.append(rf"{m.k} & {m.order} & ${r_max:.4f}$ & {verdict}\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines)


def write(name: str, body: str, directory: Path | None = None) -> Path:
    """Write a generated table, with a do-not-edit banner, into ``Sections/generated``."""
    directory = Path(directory) if directory is not None else GENERATED_DIR
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(BANNER + body + "\n", encoding="utf-8")
    print(f"  saved  Sections/generated/{name}")
    return path
