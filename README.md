# Ổn định, nhất quán và hội tụ của phương pháp đa bước tuyến tính

[![CI](https://github.com/tu-h-nguyn/Stability-Consistency-and-Convergence-of-Linear-Multistep-Methods/actions/workflows/ci.yml/badge.svg)](https://github.com/tu-h-nguyn/Stability-Consistency-and-Convergence-of-Linear-Multistep-Methods/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Ruff](https://img.shields.io/badge/lint-ruff-261230.svg)](https://docs.astral.sh/ruff/)
[![Tests](https://img.shields.io/badge/tests-86%20passed-brightgreen.svg)](code/tests)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

📄 **[Báo cáo đầy đủ (63 trang, PDF)](main.pdf)** · 🖥️ **[Slide trình bày (50 trang)](slides/main.pdf)**

> **Định lý tương đương Dahlquist (1956).** Một phương pháp đa bước tuyến tính hội tụ
> **khi và chỉ khi** nó vừa nhất quán, vừa 0-ổn định.

Dự án gồm hai nửa gắn chặt với nhau: một **báo cáo LaTeX** trình bày lý thuyết đầy đủ
(sai số cắt cụt, toán tử sai phân tuyến tính, điều kiện nghiệm, chứng minh định lý
tương đương Dahlquist, họ BDF), và một **thư viện Python `lmm`** biến toàn bộ lý thuyết
đó thành mã chạy được — mọi con số và hình vẽ trong báo cáo đều tái lập được bằng một
câu lệnh.

Điểm mấu chốt: thư viện **không hard-code** kết luận nào. Đưa vào bộ hệ số
$(\alpha_j, \beta_j)$, nó tự suy ra bậc chính xác, hằng số sai số, nghiệm của đa thức
đặc trưng, tính 0-ổn định và miền ổn định tuyệt đối. Nhờ vậy, những khẳng định như
*"BDF chỉ 0-ổn định khi $k \le 6$"* hay *"rào cản Dahlquist thứ nhất"* được **kiểm
chứng bằng số** trong bộ test, chứ không phải chép lại từ sách.

<p align="center">
  <img src="figures/fig01_method_a.png" width="100%" alt="Phương pháp A: nhất quán bậc 3 nhưng phân kỳ">
</p>

*Phương pháp A nhất quán bậc 3 — bậc cao hơn cả BDF2 — nhưng đa thức $\rho$ có nghiệm
$z = -5$. Sai số bị nhân 5 lần sau mỗi bước và đạt $10^{37}$ tại $t = 6$. Bậc chính xác
không cứu nổi một phương pháp không 0-ổn định.*

---

## Mục lục

- [Kết quả chính](#kết-quả-chính)
- [Chạy thử trong 30 giây](#chạy-thử-trong-30-giây)
- [Thư viện `lmm`](#thư-viện-lmm)
- [Các thí nghiệm số](#các-thí-nghiệm-số)
- [Kiểm chứng bằng test](#kiểm-chứng-bằng-test)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Báo cáo và cách biên dịch](#báo-cáo-và-cách-biên-dịch)
- [Tài liệu tham khảo](#tài-liệu-tham-khảo)
- [English summary](#english-summary)

---

## Kết quả chính

Bảng dưới do `code/experiments/run_all.py` sinh ra, không nhập tay
(bản đầy đủ: [`figures/RESULTS.md`](figures/RESULTS.md)):

| phương pháp | k | loại | bậc p | $C_{p+1}$ | nhất quán | 0-ổn định | hội tụ |
|---|---:|---|---:|---:|:---:|:---:|:---:|
| Euler hiện | 1 | hiện | 1 | $1/2$ | ✅ | ✅ | ✅ |
| Quy tắc hình thang | 1 | ẩn | 2 | $-1/12$ | ✅ | ✅ | ✅ |
| Công thức Simpson | 2 | ẩn | 4 | $-1/90$ | ✅ | ✅ | ✅ |
| AB3 | 3 | hiện | 3 | $3/8$ | ✅ | ✅ | ✅ |
| AM2 | 2 | ẩn | 3 | $-1/24$ | ✅ | ✅ | ✅ |
| BDF2 | 2 | ẩn | 2 | $-2/9$ | ✅ | ✅ | ✅ |
| BDF6 | 6 | ẩn | 6 | $-20/343$ | ✅ | ✅ | ✅ |
| **Phương pháp A** | 2 | hiện | **3** | $1/6$ | ✅ | ❌ | ❌ |
| **Phương pháp B** | 2 | ẩn | 1 | $4$ | ✅ | ❌ | ❌ |

Hằng số sai số $C_{p+1}$ tính với quy ước chuẩn hoá $\alpha_k = 1$ (nên so sánh được
giữa các phương pháp), và trùng khớp bảng chuẩn trong Hairer–Nørsett–Wanner.

Bốn kết luận rút ra được từ mã nguồn:

1. **Nhất quán là chưa đủ.** Phương pháp A đạt bậc 3 mà vẫn phân kỳ; phương pháp B là
   phương pháp *ẩn* và cũng phân kỳ. Tính ẩn hay bậc cao đều không thay thế được
   0-ổn định.
2. **Bậc đo được khớp bậc lý thuyết**: sai lệch lớn nhất 0.12 trên 8 phương pháp
   0-ổn định (BDF1–4, AB2–3, AM2–3) — kiểm chứng chiều thuận của định lý Dahlquist.
3. **BDF mất 0-ổn định từ $k = 7$**: $\max|z_i| = 1.0222 > 1$. Ranh giới $k \le 6$ hiện
   ra từ chính nghiệm đa thức, không cần giả định trước.
4. **Rào cản Dahlquist thứ nhất** ($p \le k+2$ với $k$ chẵn, $p \le k+1$ với $k$ lẻ)
   không bị họ nào trong danh mục vượt qua; Simpson chạm đúng chặn trên với $k=2, p=4$.

<p align="center">
  <img src="figures/fig04_convergence.png" width="100%" alt="Bậc hội tụ đo được so với lý thuyết">
</p>

<p align="center">
  <img src="figures/fig06_dahlquist_barrier.png" width="100%" alt="Rào cản Dahlquist và giới hạn k ≤ 6 của BDF">
</p>

---

## Chạy thử trong 30 giây

```bash
git clone https://github.com/tu-h-nguyn/Stability-Consistency-and-Convergence-of-Linear-Multistep-Methods.git
cd Stability-Consistency-and-Convergence-of-Linear-Multistep-Methods
pip install -r requirements.txt

# Phân tích một phương pháp bất kỳ trong danh mục
cd code && python -m lmm bdf3 method-a
```

```text
BDF3  (implicit, k = 3)
  rho(z) = 1.83333z^3 - 3z^2 + 1.5z - 0.333333
  sigma(z) = z^3
  rho(1) = -5.55e-17,  rho'(1) = +1,  sigma(1) = +1
  consistent: True   order p = 3   error constant C_{p+1} = -0.25
  root condition: SATISFIED
    z = +1.000000 +0.000000i   |z| = 1.000000
    z = +0.318182 +0.283864i   |z| = 0.426401
    z = +0.318182 -0.283864i   |z| = 0.426401
  Dahlquist verdict: CONVERGENT

Phương pháp A  (explicit, k = 2)
  ...
  root condition: VIOLATED
    z = -5.000000 +0.000000i   |z| = 5.000000  <- |z| > 1
  Dahlquist verdict: NOT convergent
```

Vài lệnh khác:

```bash
python -m lmm --list                          # bảng tổng hợp toàn bộ danh mục
python -m lmm bdf2 --solve stiff --h 0.05     # giải một bài toán mẫu
python -m lmm ab3 --convergence               # đo bậc hội tụ thực nghiệm
```

Hoặc dùng `make` từ thư mục gốc:

```bash
make figures   # sinh lại toàn bộ hình vẽ, bảng LaTeX và figures/RESULTS.md
make test      # chạy 86 test Python
make matlab    # chạy mã MATLAB bằng Octave và đối chiếu với báo cáo
make lint      # ruff
make report    # biên dịch main.pdf (cần LaTeX)
```

Bộ test chạy sạch trên **Python 3.10, 3.11, 3.12 và 3.13**; `ruff check` không còn cảnh
báo nào.

---

## Thư viện `lmm`

Một phương pháp đa bước tuyến tính $k$ bước được viết thống nhất dưới dạng

$$\sum_{j=0}^{k} \alpha_j Y_{n+j} = h \sum_{j=0}^{k} \beta_j f_{n+j}, \qquad f_{n+j} = f(t_{n+j}, Y_{n+j}).$$

```python
from lmm import LinearMultistepMethod, bdf
from lmm.problems import LOGISTIC

# Phương pháp A của Chương 4, khai báo trực tiếp từ hệ số
method_a = LinearMultistepMethod(alpha=(-5, 4, 1), beta=(2, 4, 0), name="Phương pháp A")

method_a.order              # 3      -- từ toán tử sai phân tuyến tính
method_a.error_constant     # 1/6
method_a.is_consistent      # True
method_a.is_zero_stable     # False  -- nghiệm z = -5 nằm ngoài đĩa đơn vị
method_a.is_convergent      # False  -- định lý Dahlquist
print(method_a.root_condition())

# Tích phân một bài toán giá trị đầu
sol = bdf(2).solve(LOGISTIC.f, LOGISTIC.t_span, h=0.05, startup=LOGISTIC.exact)
sol.error_against(LOGISTIC.exact)[-1]      # 6.7e-06
```

Những gì thư viện tự suy ra từ $(\alpha, \beta)$:

| Đại lượng | Cách tính | API |
|---|---|---|
| Bậc chính xác $p$ | $C_q = \frac{1}{q!}\sum j^q \alpha_j - \frac{1}{(q-1)!}\sum j^{q-1}\beta_j$ | `.order` |
| Hằng số sai số $C_{p+1}$ | hệ số đầu tiên khác 0 | `.error_constant` |
| Nhất quán | $\rho(1)=0$ và $\rho'(1)=\sigma(1)$ | `.is_consistent` |
| Điều kiện nghiệm | nghiệm của $\rho$, kể cả nghiệm bội trên $\|z\|=1$ | `.root_condition()` |
| 0-ổn định | điều kiện nghiệm được thoả | `.is_zero_stable` |
| Hội tụ | nhất quán **và** 0-ổn định | `.is_convergent` |
| Miền ổn định tuyệt đối | quỹ tích biên $z \mapsto \rho(z)/\sigma(z)$ | `.boundary_locus()` |

**Bộ tích phân** xử lý cả phương pháp hiện lẫn ẩn (Newton với Jacobian sai phân hữu
hạn), cả bài toán vô hướng lẫn hệ, khởi động bằng nghiệm chính xác hoặc bằng RK4. Nó
không giấu lỗi: cờ `diverged` được bật thay vì trả về `NaN` khi nghiệm số nổ, và
`newton_failures` đếm những bước mà Newton hết vòng lặp trước khi đạt sai số yêu cầu.

Hệ số của **BDF** và **Adams** được *sinh ra* chứ không chép tay: BDF từ khai triển
sai phân lùi $\sum_{j\ge 1} \frac{1}{j}\nabla^j Y_{n+k} = h f_{n+k}$, Adams từ tích
phân chính xác đa thức nội suy Lagrange. Test đối chiếu chúng với bảng chuẩn trong
Hairer–Nørsett–Wanner, nên `bdf(9)` cũng lấy được hệ số đúng (và bị phát hiện là không
0-ổn định).

---

## Các thí nghiệm số

Mỗi script tự chạy độc lập và in ra bảng số kèm hình vẽ.

| Script | Nội dung | Hình |
|---|---|---|
| `ex01_method_a.py` | Ví dụ 1: nhất quán bậc 3, phân kỳ vì $z=-5$ | `fig01_method_a.png` |
| `ex02_method_b.py` | Ví dụ 2: phương pháp ẩn vẫn phân kỳ vì $z=3$ | `fig02_method_b.png` |
| `ex03_root_condition.py` | Nghiệm của $\rho$ so với đường tròn đơn vị | `fig03_root_condition.png` |
| `ex04_convergence.py` | Bậc hội tụ đo được so với lý thuyết | `fig04_convergence.png` |
| `ex05_stability_regions.py` | Miền ổn định tuyệt đối, vì sao BDF hợp bài toán cứng | `fig05_stability_regions.png` |
| `ex06_dahlquist_barrier.py` | Rào cản Dahlquist và giới hạn $k \le 6$ | `fig06_dahlquist_barrier.png` |
| `ex07_report_tables.py` | Sinh các bảng LaTeX mà báo cáo `\input` | `Sections/generated/*.tex` |

### Kiểm chứng chéo ba chiều

Cùng một bài toán được giải bằng **hai cài đặt hoàn toàn độc lập** — mã MATLAB gốc
trong báo cáo, và thư viện Python với bộ giải Newton riêng — rồi đối chiếu với **bảng
số đã in trong PDF**. Cả ba trùng nhau đến từng chữ số có nghĩa:

| $t$ | nghiệm chính xác | phương pháp A | sai số |
|---:|---:|---:|---:|
| 0.5 | 6.065307e-01 | 6.081996e-01 | 1.669e-03 |
| 1.0 | 3.678794e-01 | −6.677259e+00 | 7.045e+00 |
| 4.0 | 1.831564e-02 | −3.872979e+22 | 3.873e+22 |
| 6.0 | 2.478752e-03 | −1.206376e+37 | 1.206e+37 |

Việc đối chiếu này được tự động hoá từ cả hai phía và chạy trong CI:

```bash
make matlab   # matlab/verify.sh chạy 3 script bằng Octave, so với số liệu báo cáo
make test     # code/tests/test_report_reproduction.py so cùng số liệu đó với lmm
```

<p align="center">
  <img src="figures/fig03_root_condition.png" width="100%" alt="Điều kiện nghiệm Dahlquist">
</p>

<p align="center">
  <img src="figures/fig05_stability_regions.png" width="100%" alt="Miền ổn định tuyệt đối">
</p>

---

## Kiểm chứng bằng test

```bash
cd code && python -m pytest tests -q
# 86 passed
```

Test không chỉ kiểm tra code chạy được, mà kiểm chứng **các phát biểu toán học**:

- hệ số BDF1–6, AB1–4, AM1–3 và **hằng số sai số** khớp bảng chuẩn; `bdf(1)` đúng bằng Euler ẩn, `adams_moulton(1)` đúng bằng quy tắc hình thang;
- bậc hội tụ **đo được** khớp bậc lý thuyết (sai lệch < 0.25) cho 8 phương pháp;
- phương pháp A và B nổ với **mọi** bước lưới — giảm $h$ không cứu được;
- BDF 0-ổn định với $k \le 6$, mất 0-ổn định với $k = 7, 8$;
- nghiệm bội trên đường tròn đơn vị ($\rho(z)=(z-1)^2$) bị bắt lỗi đúng;
- rào cản Dahlquist thứ nhất và thứ hai (BDF3 không A-ổn định);
- BDF2 vượt qua bài toán cứng ở bước lưới mà AB2 nổ tung;
- quy tắc hình thang giữ nguyên biên độ dao động điều hoà sau 200 đơn vị thời gian;
- **bảng số in trong báo cáo** được tái tạo lại đúng đến 6 chữ số có nghĩa.

---

## Cấu trúc dự án

```
.
├── main.tex, main.pdf        # báo cáo LaTeX (tiếng Việt), 63 trang
├── Sections/                 # 4 chương (section_1..4) + một bản nháp chưa dùng
│   └── generated/            # bảng LaTeX sinh từ code — KHÔNG sửa tay
│                             # (bản `table` cho báo cáo, bản `tabular` cho slide)
├── images/                   # hình gốc trong báo cáo
├── slides/                   # bản trình bày Beamer, 50 trang
│
├── code/
│   ├── lmm/                  # thư viện
│   │   ├── core.py           # LinearMultistepMethod: bậc, điều kiện nghiệm, bộ tích phân
│   │   ├── catalog.py        # BDF / Adams sinh tự động + các phương pháp kinh điển
│   │   ├── problems.py       # bài toán mẫu kèm nghiệm chính xác
│   │   ├── analysis.py       # nghiên cứu hội tụ, bảng tổng hợp
│   │   ├── latex.py          # sinh bảng LaTeX cho báo cáo
│   │   ├── plotting.py       # phong cách đồ hoạ dùng chung
│   │   └── __main__.py       # giao diện dòng lệnh
│   ├── experiments/          # 7 thí nghiệm + run_all.py
│   └── tests/                # 86 test
│
├── matlab/                   # mã MATLAB gốc trích từ báo cáo + verify.sh (Octave)
├── figures/                  # hình sinh tự động + RESULTS.md
├── Makefile
└── .github/workflows/ci.yml  # test Python, kiểm mã MATLAB, build PDF
```

CI gồm 5 job: **lint** (ruff), **tests** (ma trận Python 3.10–3.13), **reproduce**
(sinh lại hình và bảng, báo lỗi nếu `Sections/generated/` lỗi thời), **matlab** (chạy
`matlab/verify.sh` bằng Octave) và **report** (biên dịch cả hai PDF trong container
TeX Live).

Vì sao bảng LaTeX bị kiểm nghiêm còn hình vẽ chỉ cảnh báo: các tệp `.tex` sinh ra
**giống hệt nhau từng byte** trên cả bốn phiên bản Python, còn PNG thì đổi theo phiên
bản matplotlib. Điều này đã được kiểm chứng thực tế chứ không phải phỏng đoán.

---

## Báo cáo và cách biên dịch

Báo cáo gồm 4 chương, 63 trang:

| Chương | Nội dung |
|---|---|
| 1 | Kiến thức chuẩn bị: Taylor, Lipschitz, Picard–Lindelöf, phương trình sai phân, nội suy Lagrange; bài toán giá trị đầu và sự cần thiết của phương pháp số |
| 2 | Công thức tổng quát của LMM, hai đa thức đặc trưng, toán tử sai phân tuyến tính, phân loại sai số; tính nhất quán, ổn định, hội tụ và **chứng minh định lý tương đương Dahlquist** |
| 3 | Họ BDF: xây dựng từ nội suy sai phân lùi, khảo sát BDF1–BDF3, chứng minh ranh giới $k \le 6$, **kiểm chứng bằng số** và miền ổn định tuyệt đối |
| 4 | Ba ví dụ số: hai phương pháp nhất quán nhưng không 0-ổn định (phân kỳ), và một nghiên cứu hội tụ xác nhận chiều thuận của định lý |

```bash
make report    # -> main.pdf   (63 trang)
make slides    # -> slides/main.pdf (50 trang)
```

Slide (50 trang) dùng lại chính các hình và bảng do `lmm` sinh ra, nên phần trình bày
và báo cáo không thể lệch số liệu của nhau.

Cần một bản phân phối TeX có `babel-vietnamese`, `tcolorbox`, `listings`, `titlesec`
(TeX Live đầy đủ là đủ). Cả hai tài liệu biên dịch **không còn cảnh báo tham chiếu
thiếu**. Trên Overleaf: upload cả thư mục, đặt `main.tex` làm tài liệu chính, biên dịch
bằng pdfLaTeX.

Ba bảng số trong báo cáo (`Sections/generated/`) do `make figures` sinh ra từ chính thư
viện `lmm`, nên các con số in trong PDF không thể lệch khỏi kết quả mà bộ test kiểm
chứng.

---

## Tài liệu tham khảo

1. K. Atkinson, W. Han, D. Stewart, *Numerical Solution of Ordinary Differential Equations*, Wiley, 2009.
2. E. Hairer, S. P. Nørsett, G. Wanner, *Solving Ordinary Differential Equations I: Nonstiff Problems*, 2nd ed., Springer, 1993.
3. E. Süli, *Numerical Solution of Ordinary Differential Equations*, Lecture Notes, University of Oxford, 2022.
4. G. Dahlquist, *Convergence and stability in the numerical integration of ordinary differential equations*, Math. Scand. 4 (1956), 33–53.

Báo cáo thực hiện trong môn **Giải tích số cho Phương trình vi phân**, Trường Đại học
Khoa học Tự nhiên, ĐHQG-HCM, dưới hướng dẫn của TS. Nguyễn Đăng Khoa.

**Nhóm thực hiện:** L. T. Nhân · D. T. H. Yến · N. H. Tú

Mã nguồn phát hành theo giấy phép [MIT](LICENSE).

---

## English summary

**Stability, consistency and convergence of linear multistep methods.**

A Vietnamese-language report on the Dahlquist equivalence theorem, paired with `lmm`,
a small Python library that makes the theory executable. Given only the coefficient
vectors $(\alpha_j, \beta_j)$ of a $k$-step method, the library derives its order of
consistency and error constant from the linear difference operator, tests Dahlquist's
root condition on the first characteristic polynomial, decides convergence, traces the
boundary locus of the region of absolute stability, and integrates initial value
problems (explicit or implicit, scalar or system, Newton with a finite-difference
Jacobian).

Nothing is hard-coded: BDF coefficients come from the backward-difference construction
and Adams coefficients from exact integration of the Lagrange interpolant, so classical
results are *measured* rather than asserted. The 86-test suite verifies that observed
convergence rates match the theoretical orders, that BDF is zero-stable exactly for
$k \le 6$, that the first Dahlquist barrier holds across the catalogue, and that the two
deliberately non-zero-stable methods of Chapter 4 diverge at every step size — the
numerical face of the theorem that consistency alone is never enough.

The report's published tables are reproduced from both sides: `matlab/verify.sh` runs
the original MATLAB listings through Octave and `code/tests/test_report_reproduction.py`
checks the same figures against the Python library. Two independent implementations and
the printed PDF agree to six significant digits.

```bash
pip install -r requirements.txt
cd code && python -m lmm --list && python -m pytest tests -q
```
