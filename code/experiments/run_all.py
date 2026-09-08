"""Regenerate every figure and every table in one pass.

    python code/experiments/run_all.py

Writes the figures into ``figures/`` and a transcript of the numerical
results into ``figures/RESULTS.md``.
"""

from __future__ import annotations

import contextlib
import io
from pathlib import Path

import _bootstrap  # noqa: F401

import ex01_method_a
import ex02_method_b
import ex03_root_condition
import ex04_convergence
import ex05_stability_regions
import ex06_dahlquist_barrier
import ex07_report_tables
from lmm import __version__
from lmm.analysis import method_table
from lmm.catalog import CLASSIC_METHODS
from lmm.plotting import FIGURE_DIR

EXPERIMENTS = [
    ("Ví dụ 1 — Phương pháp A: nhất quán, không 0-ổn định", ex01_method_a),
    ("Ví dụ 2 — Phương pháp B: ẩn, nhất quán, không 0-ổn định", ex02_method_b),
    ("Điều kiện nghiệm Dahlquist", ex03_root_condition),
    ("Bậc hội tụ đo được so với lý thuyết", ex04_convergence),
    ("Miền ổn định tuyệt đối", ex05_stability_regions),
    ("Rào cản Dahlquist và giới hạn k ≤ 6 của BDF", ex06_dahlquist_barrier),
    ("Bảng LaTeX cho báo cáo", ex07_report_tables),
]

SHOWCASE_ORDER = [
    "euler", "backward-euler", "trapezoid", "midpoint", "simpson",
    "ab2", "ab3", "am2", "am3", "bdf1", "bdf2", "bdf3", "bdf4", "bdf5", "bdf6",
    "method-a", "method-b",
]


def main() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    parts = [
        "# Kết quả số\n",
        f"Sinh tự động bởi `code/experiments/run_all.py` (lmm v{__version__}). "
        "Không chỉnh sửa thủ công.\n",
        "## Bảng tổng hợp các phương pháp\n",
        method_table([CLASSIC_METHODS[k] for k in SHOWCASE_ORDER]),
        "",
    ]

    for title, module in EXPERIMENTS:
        print(f"\n=== {title} ===")
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            module.figure(*_as_tuple(module.run()))
        transcript = buffer.getvalue()
        print(transcript, end="")
        parts += [f"## {title}\n", "```", transcript.rstrip(), "```", ""]

    out = FIGURE_DIR / "RESULTS.md"
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"\nviet ket qua vao {out.relative_to(Path.cwd()) if out.is_relative_to(Path.cwd()) else out}")


def _as_tuple(result):
    return result if isinstance(result, tuple) else (result,)


if __name__ == "__main__":
    main()
