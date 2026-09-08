"""Shared figure style so every plot in the project reads as one system.

Font sizes are deliberately generous: the same PNGs are embedded in the A4
report at ``\\textwidth``, which scales a 10-inch figure down to roughly 60%.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

__all__ = ["PALETTE", "INK", "MUTED", "GRID", "use_project_style", "save", "FIGURE_DIR", "symlog"]

#: Colour-blind safe qualitative palette (Okabe-Ito derived).
PALETTE = ["#1f5fa8", "#c8532b", "#2f8f5b", "#8a5cb8", "#b8860b", "#4a7f9c"]
INK = "#1b1f24"
MUTED = "#6b7480"
GRID = "#dfe3e8"

FIGURE_DIR = Path(__file__).resolve().parents[2] / "figures"


def use_project_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 130,
            "savefig.dpi": 160,
            "savefig.bbox": "tight",
            "font.family": "DejaVu Sans",
            "font.size": 11.5,
            "axes.titlesize": 12.5,
            "axes.titleweight": "bold",
            "axes.labelsize": 11.5,
            "axes.edgecolor": MUTED,
            "axes.labelcolor": INK,
            "axes.titlecolor": INK,
            "axes.grid": True,
            "axes.axisbelow": True,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.prop_cycle": plt.cycler(color=PALETTE),
            "grid.color": GRID,
            "grid.linewidth": 0.7,
            "legend.frameon": False,
            "legend.fontsize": 10.5,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.labelcolor": INK,
            "ytick.labelcolor": INK,
            "lines.linewidth": 1.8,
            "figure.facecolor": "white",
        }
    )


def symlog(x, threshold: float = 1.0):
    """Signed logarithmic transform used in the report to show blow-up."""
    x = np.asarray(x, dtype=float)
    return np.sign(x) * np.log10(1.0 + np.abs(x) / threshold)


def save(fig, filename: str, directory: Path | None = None) -> Path:
    """Write ``fig`` into the project figure directory and report the path."""
    directory = Path(directory) if directory is not None else FIGURE_DIR
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename
    fig.savefig(path)
    plt.close(fig)
    print(f"  saved  {path.relative_to(path.parents[1])}")
    return path
