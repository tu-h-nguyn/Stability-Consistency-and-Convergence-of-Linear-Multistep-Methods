"""Where the roots of rho sit -- the geometric form of zero-stability.

One panel per method: the unit circle plus the roots of the first
characteristic polynomial. A method is zero-stable exactly when no root
escapes the disc and every root on the rim is simple.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401
import numpy as np

from lmm.catalog import METHOD_A, METHOD_B, MIDPOINT, bdf
from lmm.plotting import PALETTE, save, use_project_style

SHOWCASE = [bdf(2), bdf(6), MIDPOINT, bdf(7), METHOD_A, METHOD_B]


def run(methods=None):
    methods = methods or SHOWCASE
    for m in methods:
        rc = m.root_condition()
        flag = "0-on dinh" if rc.satisfied else "KHONG 0-on dinh"
        radii = ", ".join(f"{abs(z):.3f}" for z in rc.roots)
        print(f"{m.name:>10s}  |z| = [{radii}]   -> {flag}")
    return methods


def figure(methods):
    use_project_style()
    import matplotlib.pyplot as plt

    n = len(methods)
    cols = 3
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(3.5 * cols, 3.6 * rows))
    theta = np.linspace(0, 2 * np.pi, 400)

    for ax, m in zip(np.ravel(axes), methods):
        rc = m.root_condition()
        stable = rc.satisfied
        accent = PALETTE[2] if stable else PALETTE[1]

        ax.plot(np.cos(theta), np.sin(theta), color="#9aa3ad", lw=1.0)
        ax.fill(np.cos(theta), np.sin(theta), color=accent, alpha=0.06)
        ax.axhline(0, color="#dfe3e8", lw=0.8)
        ax.axvline(0, color="#dfe3e8", lw=0.8)
        ax.plot(rc.roots.real, rc.roots.imag, "o", color=accent, ms=8,
                markeredgecolor="white", markeredgewidth=1.2, zorder=3)

        lim = max(1.35, 1.15 * np.max(np.abs(rc.roots)))
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.set_aspect("equal")
        verdict = "0-ổn định" if stable else "vi phạm điều kiện nghiệm"
        ax.set_title(f"{m.name}\n$p={m.order}$ · {verdict}", fontsize=10,
                     color="#1b1f24" if stable else PALETTE[1])
        for z in rc.roots:
            if abs(z) > 1 + 1e-8:
                ax.annotate(f"$|z|={abs(z):.2f}$", (z.real, z.imag),
                            textcoords="offset points", xytext=(6, 6),
                            color=PALETTE[1], fontsize=9)

    for ax in np.ravel(axes)[n:]:
        ax.axis("off")

    fig.suptitle(
        "Điều kiện nghiệm Dahlquist: nghiệm của $\\rho(z)$ so với đường tròn đơn vị",
        fontsize=12, fontweight="bold", color="#1b1f24",
    )
    fig.tight_layout()
    return save(fig, "fig03_root_condition.png")


if __name__ == "__main__":
    figure(run())
