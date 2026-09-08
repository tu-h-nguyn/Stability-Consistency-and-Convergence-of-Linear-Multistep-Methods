# Mã MATLAB

Ba script, chạy được bằng **MATLAB** hoặc **GNU Octave** (không cần toolbox nào).

| Tệp | Nội dung | Bản Python tương đương |
|---|---|---|
| `method_a.m` | Ví dụ 1 — phương pháp A phân kỳ dù nhất quán bậc 3 | `code/experiments/ex01_method_a.py` |
| `method_b.m` | Ví dụ 2 — phương pháp B ẩn, vẫn phân kỳ | `code/experiments/ex02_method_b.py` |
| `bdf_convergence.m` | Bậc hội tụ của BDF1–BDF3 trên $y'=-y$ | `code/experiments/ex04_convergence.py` |

`method_a.m` và `method_b.m` là mã gốc được trích nguyên văn từ các listing trong
Chương 4 của báo cáo — chính chúng đã sinh ra các bảng số và hình vẽ trong PDF.

## Chạy

```matlab
>> method_a          % trong MATLAB
```

```bash
octave --no-gui --eval "method_a"     # hoặc bằng Octave
./verify.sh                            # chạy cả ba và đối chiếu với báo cáo
```

## Kiểm chứng chéo

`verify.sh` chạy cả ba script rồi so từng giá trị với số liệu in trong báo cáo. Bộ test
Python (`code/tests/test_report_reproduction.py`) so cùng những giá trị đó với kết quả
của thư viện `lmm`. Hai cài đặt hoàn toàn độc lập — một viết bằng MATLAB, một bằng
Python với bộ giải Newton riêng — cho kết quả **trùng nhau đến từng chữ số có nghĩa**:

```
        t     nghiệm chính xác      phương pháp A
      0.5         6.065307e-01       6.081996e-01
      1.0         3.678794e-01      -6.677259e+00
      6.0         2.478752e-03      -1.206376e+37
```

Với `bdf_convergence.m`, sai số tại $T=2$ với $h=0.1$ là $1.3308\times10^{-2}$ (BDF1),
$9.0148\times10^{-4}$ (BDF2), $6.6843\times10^{-5}$ (BDF3) — thư viện Python trả về
đúng các giá trị này.
