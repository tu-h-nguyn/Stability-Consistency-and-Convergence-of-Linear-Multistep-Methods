"""Chapter 4, Example 2 -- an implicit method that still diverges.

Being implicit buys nothing when the root condition fails: method B has the
parasitic root z = 3 and blows up just as method A does.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401
import numpy as np

from lmm.catalog import METHOD_B
from lmm.plotting import PALETTE, save, symlog, use_project_style
from lmm.problems import DECAY

CHECKPOINTS = [0.0, 0.5, 1.0, 2.0, 4.0, 6.0]
H = 0.1


def run(h: float = H):
    method, ivp = METHOD_B, DECAY
    print(method.summary())

    sol = method.solve(ivp.f, ivp.t_span, h, startup=ivp.exact)
    exact = np.array([ivp.exact(t) for t in sol.t]).ravel()
    err = np.abs(sol.y - exact)

    print(f"\n{'t':>6} {'nghiem chinh xac':>20} {'phuong phap B':>20} {'sai so':>14}")
    for tc in CHECKPOINTS:
        i = int(np.argmin(np.abs(sol.t - tc)))
        print(f"{sol.t[i]:6.1f} {exact[i]:20.6e} {sol.y[i]:20.6e} {err[i]:14.3e}")

    lam = np.roots([1.0 - 2.0 * h, -4.0, 3.0])
    print(f"\nnghiem cua phuong trinh sai phan: lambda = {np.round(lam, 6)}")
    print(f"can phan ky |lambda_2| = {max(abs(lam)):.4f} > 1")
    return sol, exact, err


def figure(sol, exact, err):
    use_project_style()
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.1))

    ax1.plot(sol.t, symlog(exact), color="#1b1f24", label="nghiệm chính xác $e^{-t}$")
    ax1.plot(sol.t, symlog(sol.y), color=PALETTE[1], ls="--", label="phương pháp B")
    ax1.set_xlabel("$t$")
    ax1.set_ylabel(r"symlog $y(t)$")
    ax1.set_title("Phương pháp ẩn vẫn phân kỳ khi vi phạm điều kiện nghiệm")
    ax1.legend(loc="lower left")

    ax2.semilogy(sol.t, np.maximum(err, 1e-18), color=PALETTE[0])
    ax2.set_xlabel("$t$")
    ax2.set_ylabel(r"$|Y_n - y(t_n)|$")
    ax2.set_title(r"Sai số khuếch đại $\approx 3$ lần mỗi bước ($|z_2| = 3$)")

    fig.suptitle(
        "Ví dụ 2 — Phương pháp B: ẩn, nhất quán, nhưng không 0-ổn định",
        fontsize=12,
        fontweight="bold",
        color="#1b1f24",
    )
    fig.tight_layout()
    return save(fig, "fig02_method_b.png")


if __name__ == "__main__":
    figure(*run())
