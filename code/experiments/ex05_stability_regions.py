"""Regions of absolute stability, and why BDF is the tool for stiff problems.

Zero-stability asks what happens as h -> 0; absolute stability asks which
products h*lambda a method can survive at a *fixed* step. The boundary locus
z -> rho(z)/sigma(z) maps the unit circle onto the boundary of that region.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401
import numpy as np

from lmm.catalog import adams_bashforth, bdf
from lmm.plotting import PALETTE, save, use_project_style

EXPLICIT = [adams_bashforth(k) for k in (1, 2, 3)]
IMPLICIT = [bdf(k) for k in (1, 2, 3, 4)]


def run():
    print("do rong mien on dinh tuyet doi tren truc thuc am (h*lambda thuc):")
    for m in EXPLICIT + IMPLICIT:
        edge = _negative_real_extent(m)
        label = "toan bo truc thuc am" if np.isinf(edge) else f"(-{edge:.3f}, 0)"
        print(f"  {m.name:5s}  {label}")
    print("\nBDF khong bi chan tren truc thuc am -> phu hop bai toan cung (stiff).")
    return EXPLICIT, IMPLICIT


def _negative_real_extent(method, probe=None) -> float:
    """How far along the negative real axis the method stays absolutely stable."""
    probe = probe if probe is not None else np.logspace(-3, 3, 400)
    unstable = [x for x in probe if not method.is_absolutely_stable_at(-x)]
    if not unstable:
        return float("inf")
    return float(min(unstable))


def figure(explicit, implicit):
    use_project_style()
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))

    for i, m in enumerate(explicit):
        locus = m.boundary_locus(1200)
        ax1.plot(locus.real, locus.imag, color=PALETTE[i], label=f"{m.name} · $p={m.order}$")
    ax1.set_xlim(-2.6, 0.8)
    ax1.set_ylim(-1.8, 1.8)
    ax1.set_title("Phương pháp hiện: miền ổn định nhỏ dần khi bậc tăng")

    for i, m in enumerate(implicit):
        locus = m.boundary_locus(1200)
        ax1_label = f"{m.name} · $p={m.order}$"
        ax2.plot(locus.real, locus.imag, color=PALETTE[i], label=ax1_label)
    ax2.set_xlim(-4, 14)
    ax2.set_ylim(-9, 9)
    ax2.set_title("BDF: miền ổn định là phần ngoài đường cong")

    for ax in (ax1, ax2):
        ax.axhline(0, color="#c3c9d1", lw=0.9)
        ax.axvline(0, color="#c3c9d1", lw=0.9)
        ax.set_xlabel(r"$\mathrm{Re}(h\lambda)$")
        ax.set_ylabel(r"$\mathrm{Im}(h\lambda)$")
        ax.set_aspect("equal")
        ax.legend(loc="upper left")

    fig.suptitle("Miền ổn định tuyệt đối qua quỹ tích biên $\\rho(z)/\\sigma(z)$",
                 fontsize=12, fontweight="bold", color="#1b1f24")
    fig.tight_layout()
    return save(fig, "fig05_stability_regions.png")


if __name__ == "__main__":
    figure(*run())
