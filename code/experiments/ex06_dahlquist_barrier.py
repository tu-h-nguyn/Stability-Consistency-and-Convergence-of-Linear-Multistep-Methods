"""The first Dahlquist barrier, and the k <= 6 limit of the BDF family.

Two classical obstructions, both checked numerically here:

* a zero-stable k-step method has order at most k + 1 (k even) or k (k odd);
* the k-step BDF formula is zero-stable exactly for k <= 6.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401
import numpy as np

from lmm.catalog import adams_bashforth, adams_moulton, bdf
from lmm.plotting import PALETTE, save, use_project_style

K_MAX = 8


def run():
    print(f"{'k':>2} {'BDF bac p':>10} {'max |z|':>9}  ket luan")
    radii, orders = [], []
    for k in range(1, K_MAX + 1):
        m = bdf(k)
        r = float(np.max(np.abs(m.root_condition().roots)))
        radii.append(r)
        orders.append(m.order)
        verdict = "0-on dinh" if m.is_zero_stable else "KHONG 0-on dinh -> vo dung"
        print(f"{k:>2} {m.order:>10} {r:>9.4f}  {verdict}")

    print("\nRao can Dahlquist thu nhat: bac toi da cua phuong phap k buoc 0-on dinh")
    print(f"{'k':>2} {'AB':>4} {'AM':>4} {'BDF':>4} {'chan tren':>10}")
    for k in range(1, 7):
        bound = k + 2 if k % 2 == 0 else k + 1
        b = bdf(k)
        print(f"{k:>2} {adams_bashforth(k).order:>4} {adams_moulton(k).order:>4} "
              f"{b.order if b.is_zero_stable else 0:>4} {bound:>10}")
    return radii, orders


def figure(radii, orders):
    use_project_style()
    import matplotlib.pyplot as plt

    ks = np.arange(1, K_MAX + 1)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.3))

    colors = [PALETTE[2] if r <= 1 + 1e-8 else PALETTE[1] for r in radii]
    ax1.bar(ks, radii, color=colors, width=0.62)
    ax1.axhline(1.0, color="#1b1f24", lw=1.1, ls="--")
    ax1.text(0.55, 1.004, "ngưỡng $|z| = 1$", color="#1b1f24", fontsize=9)
    ax1.set_ylim(0.9, max(radii) * 1.05)  # zoom: the gap above 1 is what matters
    ax1.set_xlabel("số bước $k$ của BDF")
    ax1.set_ylabel(r"$\max |z_i|$ trong nghiệm của $\rho$")
    ax1.set_title("BDF chỉ 0-ổn định khi $k \\leq 6$")
    for k, r in zip(ks[6:], radii[6:], strict=True):
        ax1.annotate(f"{r:.3f}", (k, r), ha="center", va="bottom",
                     color=PALETTE[1], fontsize=9)
    ax1.text(0.02, 0.93, "trục tung được phóng to quanh $|z| = 1$",
             transform=ax1.transAxes, color="#6b7480", fontsize=9)

    kk = np.arange(1, 9)
    barrier = np.where(kk % 2 == 0, kk + 2, kk + 1)
    ax2.plot(kk, barrier, "o--", color="#1b1f24", label="rào cản Dahlquist thứ nhất")
    # AB_k and BDF_k share the same order, so the AB curve is drawn wide and
    # translucent underneath to keep both visible.
    ax2.plot(kk[:4], [adams_bashforth(k).order for k in kk[:4]], "-",
             color=PALETTE[0], lw=6, alpha=0.35, solid_capstyle="round",
             label="Adams–Bashforth (hiện)")
    ax2.plot(kk[:4], [adams_moulton(k).order for k in kk[:4]], "o-",
             color=PALETTE[3], label="Adams–Moulton (ẩn)")
    ax2.plot(kk[:6], [bdf(k).order for k in kk[:6]], "o-",
             color=PALETTE[2], label="BDF (ẩn, $k \\leq 6$)")
    ax2.set_xlabel("số bước $k$")
    ax2.set_ylabel("bậc chính xác $p$")
    ax2.set_title("Không họ nào vượt được rào cản")
    ax2.legend(loc="upper left")

    fig.suptitle("Hai giới hạn cấu trúc của phương pháp đa bước tuyến tính",
                 fontsize=12, fontweight="bold", color="#1b1f24")
    fig.tight_layout()
    return save(fig, "fig06_dahlquist_barrier.png")


if __name__ == "__main__":
    figure(*run())
