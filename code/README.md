# `lmm` — linear multistep methods, derived from their coefficients

Companion library for the report *Ổn định, nhất quán và hội tụ của phương pháp đa bước
tuyến tính*. Full documentation, figures and results are in the
[repository README](../README.md).

Give it the coefficient vectors of

$$\sum_{j=0}^{k}\alpha_j Y_{n+j} = h\sum_{j=0}^{k}\beta_j f_{n+j}$$

and it derives the order of consistency and the error constant from the linear
difference operator, tests Dahlquist's root condition, decides convergence, traces the
boundary of the region of absolute stability, and integrates initial value problems
(explicit or implicit, scalar or system).

```bash
pip install -e .            # or: pip install -r ../requirements.txt
python -m lmm --list        # every method in the catalogue
python -m pytest tests -q   # 68 tests
python experiments/run_all.py
```

```python
from lmm import LinearMultistepMethod

m = LinearMultistepMethod(alpha=(-5, 4, 1), beta=(2, 4, 0), name="Phương pháp A")
m.order            # 3
m.is_consistent    # True
m.is_zero_stable   # False  -> not convergent, however small h is
```

| module | nội dung |
|---|---|
| `lmm/core.py` | `LinearMultistepMethod`, `Solution`, bộ tích phân, điều kiện nghiệm |
| `lmm/catalog.py` | BDF và Adams sinh tự động, các phương pháp kinh điển, phương pháp A/B |
| `lmm/problems.py` | bài toán mẫu kèm nghiệm chính xác |
| `lmm/analysis.py` | nghiên cứu hội tụ, bảng tổng hợp |
| `lmm/plotting.py` | phong cách đồ hoạ dùng chung |
| `lmm/__main__.py` | giao diện dòng lệnh |
