"""Measured order of convergence versus the order predicted by the theory.

For each method the global error at the final time is computed on a sequence
of halved step sizes; the slope on a log-log plot is the observed order.
Zero-stable methods land on their theoretical slope, methods A and B do not
converge at all.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401
import numpy as np

from lmm.analysis import convergence_study
from lmm.catalog import METHOD_A, adams_bashforth, adams_moulton, bdf
from lmm.plotting import PALETTE, save, use_project_style
from lmm.problems import DECAY, LOGISTIC

STEPS = np.array([0.2, 0.1, 0.05, 0.025, 0.0125, 0.00625, 0.003125])
CONVERGENT = [bdf(1), bdf(2), bdf(3), adams_bashforth(2), adams_moulton(2)]


def run(problem=LOGISTIC, methods=None, steps=STEPS):
    methods = methods or CONVERGENT
    studies = []
    print(f"bai toan: {problem.name}   ({problem.latex})\n")
    for m in methods:
        cs = convergence_study(m, problem, steps)
        studies.append(cs)
        print(f"{m.name}  (bac ly thuyet p = {m.order}, bac do duoc = {cs.estimated_order:.3f})")
        print(cs.to_markdown().replace("|", " "), "\n")

    # The non-convergent method is compared on the linear test problem, where
    # the parasitic root alone drives the blow-up.
    diverging = convergence_study(METHOD_A, DECAY, steps)
    reference = convergence_study(bdf(3), DECAY, steps)
    print(f"{METHOD_A.name} tren bai toan {DECAY.name}:")
    print(f"   sai so tai T = {np.array2string(diverging.errors, precision=2)}")
    print("   -> giam h khong lam giam sai so: khong hoi tu (dung nhu dinh ly Dahlquist).")
    return studies, diverging, reference


def figure(studies, diverging, reference):
    use_project_style()
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))

    for i, cs in enumerate(studies):
        ax1.loglog(cs.steps, cs.errors, "o-", color=PALETTE[i % len(PALETTE)], ms=4,
                   label=f"{cs.method.name} · $p={cs.method.order}$, đo được ${cs.estimated_order:.2f}$")
    ax1.set_xlabel("bước lưới $h$")
    ax1.set_ylabel("sai số toàn cục tại $T$")
    ax1.set_title("Phương pháp 0-ổn định: sai số giảm đúng bậc lý thuyết")
    ax1.legend(loc="lower right")

    ax2.loglog(diverging.steps, diverging.errors, "o-", color=PALETTE[1], ms=5,
               label=f"{diverging.method.name} · $p={diverging.method.order}$, không 0-ổn định")
    ax2.loglog(reference.steps, reference.errors, "o-", color=PALETTE[2], ms=4,
               label=f"{reference.method.name} · 0-ổn định, $p={reference.method.order}$")
    ax2.text(0.03, 0.44,
             "đường đỏ bị chặn ở ngưỡng tràn số $10^{50}$\ncủa bộ tích phân",
             transform=ax2.transAxes, color="#6b7480", fontsize=9)
    ax2.set_xlabel("bước lưới $h$")
    ax2.set_ylabel("sai số toàn cục tại $T$")
    ax2.set_title("Bậc cao vô nghĩa nếu thiếu 0-ổn định\n(bài toán $y' = -y$)")
    ax2.legend(loc="center right")

    fig.suptitle("Kiểm chứng số định lý tương đương Dahlquist",
                 fontsize=12, fontweight="bold", color="#1b1f24")
    fig.tight_layout()
    return save(fig, "fig04_convergence.png")


if __name__ == "__main__":
    figure(*run())
