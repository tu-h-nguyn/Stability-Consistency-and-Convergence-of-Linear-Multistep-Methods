"""Generate the LaTeX tables that the report inputs.

Running this keeps Chapters 3 and 4 numerically in step with the library: the
tables in the PDF are produced by the same code the test suite validates.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

from lmm.analysis import convergence_study
from lmm.catalog import (
    METHOD_A,
    METHOD_B,
    MIDPOINT,
    SIMPSON,
    TRAPEZOID,
    EULER_EXPLICIT,
    adams_bashforth,
    adams_moulton,
    bdf,
)
from lmm.latex import bdf_stability_table, convergence_table, method_table, write
from lmm.problems import LOGISTIC

STEPS = [0.2, 0.1, 0.05, 0.025, 0.0125]

CONVERGENT = [bdf(1), bdf(2), bdf(3), adams_bashforth(2), adams_moulton(2)]

SUMMARY = [
    EULER_EXPLICIT, bdf(1), TRAPEZOID, MIDPOINT, SIMPSON,
    adams_bashforth(2), adams_bashforth(3), adams_moulton(2),
    bdf(2), bdf(3), bdf(6), METHOD_A, METHOD_B,
]


def run():
    studies = [convergence_study(m, LOGISTIC, STEPS) for m in CONVERGENT]
    for cs in studies:
        print(f"  {cs.method.name:5s} p = {cs.method.order}, bậc đo được = {cs.estimated_order:.3f}")

    write("convergence_table.tex", convergence_table(
        studies,
        caption=(
            "Sai số toàn cục tại $T=8$ của bài toán $y'=y(1-y),\\ y(0)=0.1$. "
            "Bậc đo được là hệ số góc hồi quy của $\\log E$ theo $\\log h$, "
            "khớp với bậc lý thuyết $p$ của từng phương pháp."
        ),
        label="tab:convergence",
    ))

    write("method_summary.tex", method_table(
        SUMMARY,
        caption=(
            "Tổng hợp tính chất của các phương pháp đa bước tuyến tính, suy ra trực tiếp "
            "từ bộ hệ số $(\\alpha_j,\\beta_j)$. Hai phương pháp cuối nhất quán nhưng "
            "không 0-ổn định, do đó không hội tụ. Hằng số sai số được tính với quy ước "
            "chuẩn hoá $\\alpha_k = 1$."
        ),
        label="tab:method-summary",
    ))

    write("bdf_stability.tex", bdf_stability_table(
        [bdf(k) for k in range(1, 9)],
        caption=(
            "Bán kính lớn nhất trong các nghiệm của $\\rho(z)$ đối với họ BDF. "
            "Điều kiện nghiệm bị vi phạm kể từ $k=7$, đúng với kết quả cổ điển "
            "rằng BDF chỉ 0-ổn định khi $k \\leq 6$."
        ),
        label="tab:bdf-stability",
    ))
    return studies


def figure(*_):
    """No figure of its own: this experiment only emits LaTeX."""
    return None


if __name__ == "__main__":
    run()
