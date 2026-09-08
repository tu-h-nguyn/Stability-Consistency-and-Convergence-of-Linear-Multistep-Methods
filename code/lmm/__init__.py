"""``lmm`` -- linear multistep methods: theory made executable.

Companion code for the report *Stability, Consistency and Convergence of
Linear Multistep Methods*. The package derives every structural property of a
method (order, error constant, root condition, zero-stability, region of
absolute stability) from its coefficients, and integrates initial value
problems with it.

Quick start::

    from lmm import catalog, problems

    bdf2 = catalog.get("bdf2")
    print(bdf2.summary())

    ivp = problems.get("decay")
    sol = bdf2.solve(ivp.f, ivp.t_span, h=0.1, startup=ivp.exact)
    print(sol.error_against(ivp.exact)[-1])
"""

from .analysis import ConvergenceStudy, convergence_study, method_table
from .catalog import (
    METHOD_A,
    METHOD_B,
    adams_bashforth,
    adams_moulton,
    bdf,
)
from .core import LinearMultistepMethod, RootConditionReport, Solution
from .problems import IVP

__version__ = "1.0.0"

__all__ = [
    "LinearMultistepMethod",
    "Solution",
    "RootConditionReport",
    "IVP",
    "ConvergenceStudy",
    "convergence_study",
    "method_table",
    "bdf",
    "adams_bashforth",
    "adams_moulton",
    "METHOD_A",
    "METHOD_B",
    "__version__",
]
