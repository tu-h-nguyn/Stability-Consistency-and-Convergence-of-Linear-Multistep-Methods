"""Animated views of the theory: three GIFs for the README.

A static plot states the conclusion. These show the mechanism that produces
it -- the parasitic root multiplying the error every single step, the solution
snapping onto the exact curve as the grid refines, and the roots of the
stability polynomial walking out of the unit disc.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401
import numpy as np

from lmm.analysis import convergence_study
from lmm.animation import save_animation
from lmm.catalog import METHOD_A, adams_bashforth, bdf
from lmm.plotting import GRID, INK, MUTED, PALETTE, symlog, use_project_style
from lmm.problems import DECAY, LOGISTIC

H = 0.1


# ----------------------------------------------------------------------
# 1. A consistent method destroyed by one parasitic root
# ----------------------------------------------------------------------
def divergence():
    """Method A stepping forward, error multiplied by |z| = 5 each step."""
    import matplotlib.pyplot as plt

    use_project_style()
    ivp = DECAY
    sol = METHOD_A.solve(ivp.f, ivp.t_span, H, startup=ivp.exact)
    t = sol.t
    exact = np.array([ivp.exact(x) for x in t]).ravel()
    err = np.maximum(np.abs(sol.y - exact), 1e-18)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.1))

    ax1.plot(t, symlog(exact), color=INK, lw=2, label="nghiệm chính xác $e^{-t}$")
    (num_line,) = ax1.plot([], [], color=PALETTE[1], lw=2, ls="--", label="phương pháp A")
    (num_head,) = ax1.plot([], [], "o", color=PALETTE[1], ms=8,
                           markeredgecolor="white", markeredgewidth=1.5)
    ax1.set_xlim(t[0], t[-1])
    pad = 1.06 * np.max(np.abs(symlog(sol.y)))
    ax1.set_ylim(-pad, pad)
    ax1.set_xlabel("$t$")
    ax1.set_ylabel(r"symlog $y(t)$")
    ax1.set_title("Nhất quán bậc 3 — vẫn phân kỳ")
    ax1.legend(loc="lower left")

    (err_line,) = ax2.plot([], [], color=PALETTE[0], lw=2)
    (err_head,) = ax2.plot([], [], "o", color=PALETTE[0], ms=8,
                           markeredgecolor="white", markeredgewidth=1.5)
    ax2.set_yscale("log")
    ax2.set_xlim(t[0], t[-1])
    ax2.set_ylim(1e-18, 1e40)
    ax2.axhline(1.0, color=MUTED, lw=1.0, ls=":")
    ax2.set_xlabel("$t$")
    ax2.set_ylabel(r"$|Y_n - y(t_n)|$")
    ax2.set_title(r"Sai số $\times\,5$ mỗi bước  ($|z_2| = 5$)")

    readout = fig.text(0.5, 0.015, "", ha="center", color=MUTED, fontsize=10)
    fig.suptitle("Ví dụ 1 — phương pháp A: $\\rho(z) = (z-1)(z+5)$",
                 fontsize=12, fontweight="bold", color=INK)
    fig.tight_layout(rect=(0, 0.04, 1, 1))

    def update(i):
        k = i + 1
        num_line.set_data(t[:k], symlog(sol.y[:k]))
        num_head.set_data([t[k - 1]], [symlog(sol.y[k - 1])])
        err_line.set_data(t[:k], err[:k])
        err_head.set_data([t[k - 1]], [err[k - 1]])
        readout.set_text(
            f"n = {k - 1:>2d}    t = {t[k - 1]:4.1f}    "
            f"Y_n = {sol.y[k - 1]:>12.4e}    sai số = {err[k - 1]:.2e}"
        )
        return num_line, num_head, err_line, err_head, readout

    return save_animation(fig, update, len(t), "anim01_divergence.gif", fps=10)


# ----------------------------------------------------------------------
# 2. Refining the grid: the numerical solution snaps onto the exact one
# ----------------------------------------------------------------------
def convergence(hold: int = 6):
    """BDF2 on a nonlinear problem as h halves, with the error curve tracing."""
    import matplotlib.pyplot as plt

    use_project_style()
    method, ivp = bdf(2), LOGISTIC
    steps = [0.8, 0.4, 0.2, 0.1, 0.05, 0.025, 0.0125]
    runs = [method.solve(ivp.f, ivp.t_span, h, startup=ivp.exact) for h in steps]
    study = convergence_study(method, ivp, steps)

    fine = np.linspace(ivp.t0, ivp.T, 400)
    exact = np.array([ivp.exact(x) for x in fine]).ravel()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.1))

    ax1.plot(fine, exact, color=INK, lw=2, label="nghiệm chính xác")
    (approx,) = ax1.plot([], [], "o--", color=PALETTE[1], lw=1.8, ms=5,
                         markeredgecolor="white", markeredgewidth=0.8, label="BDF2")
    ax1.set_xlim(ivp.t0, ivp.T)
    ax1.set_ylim(-0.05, 1.12)
    ax1.set_xlabel("$t$")
    ax1.set_ylabel("$y(t)$")
    ax1.set_title("Lưới mịn dần, nghiệm số bám lấy nghiệm đúng")
    ax1.legend(loc="lower right")

    ax2.loglog(study.steps, study.errors, color=GRID, lw=1.5, zorder=0)
    (trace,) = ax2.plot([], [], "o-", color=PALETTE[0], lw=2, ms=7,
                        markeredgecolor="white", markeredgewidth=1.2)
    ax2.set_xlim(steps[-1] / 1.6, steps[0] * 1.6)
    ax2.set_ylim(min(study.errors) / 4, max(study.errors) * 4)
    ax2.set_xlabel("bước lưới $h$")
    ax2.set_ylabel("sai số toàn cục tại $T$")
    ax2.set_title(r"Hệ số góc $= 2$: sai số $\sim h^{2}$")

    readout = fig.text(0.5, 0.015, "", ha="center", color=MUTED, fontsize=10)
    fig.suptitle("Chiều thuận của định lý Dahlquist — BDF2 nhất quán và 0-ổn định",
                 fontsize=12, fontweight="bold", color=INK)
    fig.tight_layout(rect=(0, 0.04, 1, 1))

    def update(i):
        k = min(i // hold, len(steps) - 1)
        sol = runs[k]
        # At h = 0.0125 the grid holds 641 points; drawing a marker on every one
        # buries the exact curve under white marker edges. Show at most ~25.
        approx.set_data(sol.t, sol.y)
        approx.set_markevery(max(1, (len(sol.t) - 1) // 25))
        trace.set_data(study.steps[: k + 1], study.errors[: k + 1])
        ratio = (
            "" if k == 0
            else f"    giảm {study.errors[k - 1] / study.errors[k]:.1f} lần so với bước trước"
        )
        readout.set_text(
            f"h = {steps[k]:<7g} N = {len(sol.t) - 1:<4d} "
            f"sai số tại T = {study.errors[k]:.3e}{ratio}"
        )
        return approx, trace, readout

    return save_animation(fig, update, len(steps) * hold, "anim02_convergence.gif", fps=8)


# ----------------------------------------------------------------------
# 3. Roots of the stability polynomial leaving the unit disc
# ----------------------------------------------------------------------
def stability_roots(frames: int = 70):
    """Sweep h*lambda along the negative real axis and watch the roots move."""
    import matplotlib.pyplot as plt

    use_project_style()
    pairs = [(adams_bashforth(2), "AB2 — hiện"), (bdf(2), "BDF2 — ẩn")]
    hlams = np.linspace(0.0, -3.0, frames)
    theta = np.linspace(0, 2 * np.pi, 400)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.6))
    artists = []
    for ax, (method, label) in zip(axes, pairs, strict=True):
        ax.plot(np.cos(theta), np.sin(theta), color=MUTED, lw=1.2)
        ax.axhline(0, color=GRID, lw=0.9)
        ax.axvline(0, color=GRID, lw=0.9)
        ax.set_xlim(-2.2, 2.2)
        ax.set_ylim(-2.2, 2.2)
        ax.set_aspect("equal")
        ax.set_xlabel(r"$\mathrm{Re}\,z$")
        ax.set_ylabel(r"$\mathrm{Im}\,z$")
        ax.set_title(label)
        (dots,) = ax.plot([], [], "o", ms=11, markeredgecolor="white", markeredgewidth=1.5)
        verdict = ax.text(0.5, 0.94, "", transform=ax.transAxes, ha="center",
                          va="top", fontsize=10)
        artists.append((method, dots, verdict))

    readout = fig.text(0.5, 0.015, "", ha="center", color=MUTED, fontsize=10)
    fig.suptitle(
        "Nghiệm của $\\rho(z) - h\\lambda\\,\\sigma(z)$ khi $h\\lambda$ chạy dọc trục thực âm",
        fontsize=12, fontweight="bold", color=INK,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))

    def update(i):
        hlam = hlams[i]
        touched = [readout]
        for method, dots, verdict in artists:
            poly = np.trim_zeros(method.rho - hlam * method.sigma, "f")
            roots = np.roots(poly) if poly.size > 1 else np.array([])
            stable = roots.size > 0 and np.all(np.abs(roots) < 1.0)
            dots.set_data(roots.real, roots.imag)
            dots.set_color(PALETTE[2] if stable else PALETTE[1])
            verdict.set_text("ổn định tuyệt đối" if stable else "nghiệm thoát khỏi đĩa đơn vị")
            verdict.set_color(INK if stable else PALETTE[1])
            touched += [dots, verdict]
        readout.set_text(f"$h\\lambda$ = {hlam:+.3f}")
        return touched

    return save_animation(fig, update, frames, "anim03_stability_roots.gif", fps=12)


def run():
    return divergence(), convergence(), stability_roots()


def figure(*_):
    """Animations are written by run(); nothing extra to draw."""
    return None


if __name__ == "__main__":
    run()
