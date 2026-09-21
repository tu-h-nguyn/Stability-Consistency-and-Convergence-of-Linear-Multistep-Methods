"""Animated figures: the numerical solution unfolding step by step.

A static convergence plot states a conclusion; watching the parasitic root
double the error every step shows the mechanism producing it. These helpers
wrap matplotlib's animation machinery with the project's figure style and
write GIFs, which render inline on GitHub without a player.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

from .plotting import FIGURE_DIR, use_project_style

__all__ = ["ANIMATION_DIR", "save_animation", "use_project_style"]

#: Animations live beside the static figures.
ANIMATION_DIR = FIGURE_DIR

#: Keep GIFs small enough for a README: GitHub will not lazy-load them.
DEFAULT_FPS = 12

#: The static figures render at 160 dpi because they are printed in an A4
#: report. A GIF is only ever viewed on screen, so 100 dpi is plenty and
#: roughly halves the file.
DEFAULT_DPI = 100


def save_animation(
    fig: plt.Figure,
    update: Callable[[int], object],
    frames: int,
    filename: str,
    fps: int = DEFAULT_FPS,
    directory: Path | None = None,
    init: Callable[[], object] | None = None,
    dpi: int = DEFAULT_DPI,
) -> Path:
    """Render ``frames`` frames of ``update`` into a GIF and report the path.

    ``update(i)`` draws frame ``i`` and returns the artists it touched.
    Rendering is deliberately non-blitted: these plots rescale their axes as the
    solution blows up, and blitting would leave the stale background behind.
    """
    directory = Path(directory) if directory is not None else ANIMATION_DIR
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename

    anim = FuncAnimation(
        fig, update, init_func=init, frames=frames, interval=1000 / fps, blit=False
    )
    anim.save(path, writer=PillowWriter(fps=fps), dpi=dpi)
    plt.close(fig)

    size_kb = path.stat().st_size / 1024
    print(f"  saved  {directory.name}/{filename}  ({frames} khung hình, {size_kb:.0f} KB)")
    return path
