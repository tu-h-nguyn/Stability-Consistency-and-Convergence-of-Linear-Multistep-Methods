"""The animation helper must actually produce a playable GIF.

Rendering the project's real animations takes about ninety seconds, so this
renders a deliberately tiny one: enough to catch a broken writer, a bad path,
or a frame callback that raises.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest
from PIL import Image

from lmm.animation import save_animation


@pytest.fixture
def tiny_figure():
    fig, ax = plt.subplots(figsize=(2, 1.5))
    (line,) = ax.plot([], [])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    yield fig, line
    plt.close(fig)


def test_save_animation_writes_a_multi_frame_gif(tiny_figure, tmp_path):
    fig, line = tiny_figure

    def update(i):
        line.set_data([0, i / 4], [0, i / 4])
        return (line,)

    path = save_animation(fig, update, frames=4, filename="tiny.gif",
                          fps=4, directory=tmp_path)

    assert path.exists() and path.stat().st_size > 0
    with Image.open(path) as gif:
        assert gif.format == "GIF"
        assert gif.n_frames >= 2  # identical frames may be coalesced


def test_save_animation_creates_the_target_directory(tiny_figure, tmp_path):
    fig, line = tiny_figure
    nested = tmp_path / "does" / "not" / "exist"

    path = save_animation(fig, lambda i: (line,), frames=2, filename="d.gif",
                          fps=4, directory=nested)
    assert path.parent == nested and path.exists()


def test_a_broken_frame_never_yields_a_silently_finished_gif(tiny_figure, tmp_path):
    """A failing frame callback must abort the render, not write a partial GIF.

    The callback's own ValueError does propagate, but matplotlib's teardown
    raises IndexError on the way out and masks it, so the guarantee worth
    asserting is the observable one: the call fails and leaves no usable file.
    """
    fig, _ = tiny_figure
    target = tmp_path / "broken.gif"

    def broken(i):
        raise ValueError("khung hình hỏng")

    with pytest.raises(Exception):  # noqa: B017 - see the docstring
        save_animation(fig, broken, frames=2, filename=target.name,
                       fps=4, directory=tmp_path)

    if target.exists():
        with pytest.raises(Exception), Image.open(target) as gif:  # noqa: B017
            gif.seek(1)
