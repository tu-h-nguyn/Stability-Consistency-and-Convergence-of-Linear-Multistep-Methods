"""Command line front end::

    python -m lmm bdf3 method-a          # structural report on one or more methods
    python -m lmm --list                 # everything in the catalogue
    python -m lmm bdf2 --solve decay --h 0.1
"""

from __future__ import annotations

import argparse

import numpy as np

from . import __version__
from .analysis import convergence_study, method_table
from .catalog import CLASSIC_METHODS, get
from .problems import PROBLEMS
from .problems import get as get_problem


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m lmm",
        description="Kiem tra tinh nhat quan, 0-on dinh va hoi tu cua phuong phap da buoc tuyen tinh.",
    )
    p.add_argument("methods", nargs="*", help=f"khoa trong danh muc: {', '.join(sorted(CLASSIC_METHODS))}")
    p.add_argument("--list", action="store_true", help="in bang tong hop toan bo danh muc")
    p.add_argument("--solve", metavar="PROBLEM", choices=sorted(PROBLEMS),
                   help=f"giai mot bai toan mau: {', '.join(sorted(PROBLEMS))}")
    p.add_argument("--h", type=float, default=0.1, help="buoc luoi (mac dinh 0.1)")
    p.add_argument("--convergence", action="store_true", help="do bac hoi tu thuc nghiem")
    p.add_argument("--version", action="version", version=f"lmm {__version__}")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.list:
        print(method_table(list(CLASSIC_METHODS.values())))
        return 0
    if not args.methods:
        build_parser().print_help()
        return 1

    for name in args.methods:
        method = get(name)
        print(method.summary())
        if args.solve:
            problem = get_problem(args.solve)
            sol = method.solve(problem.f, problem.t_span, args.h, startup=problem.exact)
            err = sol.error_against(problem.exact)
            status = "PHAN KY" if sol.diverged else "ket thuc binh thuong"
            print(f"  {problem.name}: h = {args.h}, sai so tai T = {err[-1]:.4e}  ({status})")
        if args.convergence:
            problem = get_problem(args.solve or "logistic")
            steps = args.h * 2.0 ** -np.arange(5)
            cs = convergence_study(method, problem, steps)
            print(f"  bac do duoc tren bai toan {problem.name}: {cs.estimated_order:.3f}"
                  f"  (ly thuyet {method.order})")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
