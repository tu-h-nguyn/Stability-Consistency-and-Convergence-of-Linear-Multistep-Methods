"""Chapter 4, Example 1 -- consistency without zero-stability.

Method A is consistent of order 3, yet the root z = -5 of its first
characteristic polynomial violates the root condition. The experiment
reproduces the divergence table and figures of the report.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401
import numpy as np

from lmm.catalog import METHOD_A
from lmm.plotting import PALETTE, save, symlog, use_project_style
from lmm.problems import DECAY

CHECKPOINTS = [0.0, 0.5, 1.0, 2.0, 4.0, 6.0]
H = 0.1


def run(h: float = H):
    method, ivp = METHOD_A, DECAY
    print(method.summary())

    sol = method.solve(ivp.f, ivp.t_span, h, startup=ivp.exact)
    exact = np.array([ivp.exact(t) for t in sol.t]).ravel()
    err = np.abs(sol.y - exact)

    print(f"\n{'t':>6} {'nghiem chinh xac':>20} {'phuong phap A':>20} {'sai so':>14}")
    for tc in CHECKPOINTS:
        i = int(np.argmin(np.abs(sol.t - tc)))
        print(f"{sol.t[i]:6.1f} {exact[i]:20.6e} {sol.y[i]:20.6e} {err[i]:14.3e}")

    lam = _amplification_roots(h)
    print(f"\nnghiem cua phuong trinh sai phan: lambda = {np.round(lam, 6)}")
    print(f"can phan ky |lambda_2| = {max(abs(lam)):.4f} > 1  ->  khuech dai moi buoc")
    return sol, exact, err


def _amplification_roots(h: float) -> np.ndarray:
    """Roots of lambda^2 + 4(1-h) lambda - (5 + 2h) for y' = -y."""
    return np.roots([1.0, 4.0 * (1.0 - h), -(5.0 + 2.0 * h)])


def figure(sol, exact, err):
    use_project_style()
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.0))

    ax1.plot(sol.t, symlog(exact), color="#1b1f24", label="nghiệm chính xác $e^{-t}$")
    ax1.plot(sol.t, symlog(sol.y), color=PALETTE[1], ls="--", label="phương pháp A")
    ax1.set_xlabel("$t$")
    ax1.set_ylabel(r"symlog $y(t)$")
    ax1.set_title("Nghiệm số phân kỳ dù phương pháp nhất quán bậc 3")
    ax1.legend(loc="lower left")

    ax2.semilogy(sol.t, np.maximum(err, 1e-18), color=PALETTE[0])
    ax2.set_xlabel("$t$")
    ax2.set_ylabel(r"$|Y_n - y(t_n)|$")
    ax2.set_title(r"Sai số khuếch đại $\approx 5$ lần mỗi bước ($|z_2| = 5$)")
    ax2.axhline(1.0, color=PALETTE[1], lw=1.0, ls=":")
    ax2.text(
        0.03, 0.93,
        "sai số vượt $1$ ngay trước $t = 1$,\nrồi tăng theo cấp số nhân",
        transform=ax2.transAxes, va="top", color="#6b7480", fontsize=9,
    )

    fig.suptitle(
        "Ví dụ 1 — Phương pháp A: nhất quán nhưng không 0-ổn định",
        fontsize=12,
        fontweight="bold",
        color="#1b1f24",
    )
    fig.tight_layout()
    return save(fig, "fig01_method_a.png")


if __name__ == "__main__":
    figure(*run())
