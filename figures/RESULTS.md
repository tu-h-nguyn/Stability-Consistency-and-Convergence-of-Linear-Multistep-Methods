# Kết quả số

Sinh tự động bởi `code/experiments/run_all.py` (lmm v1.0.0). Không chỉnh sửa thủ công.

## Bảng tổng hợp các phương pháp

| phương pháp | k | loại | bậc p | C_{p+1} (α_k=1) | nhất quán | 0-ổn định | hội tụ |
|---|---:|---|---:|---:|:---:|:---:|:---:|
| Euler hiện | 1 | hiện | 1 | +0.5 | ✅ | ✅ | ✅ |
| Euler ẩn (BDF1) | 1 | ẩn | 1 | -0.5 | ✅ | ✅ | ✅ |
| Quy tắc hình thang (AM1) | 1 | ẩn | 2 | -0.08333 | ✅ | ✅ | ✅ |
| Quy tắc điểm giữa | 2 | hiện | 2 | +0.3333 | ✅ | ✅ | ✅ |
| Công thức Simpson | 2 | ẩn | 4 | -0.01111 | ✅ | ✅ | ✅ |
| AB2 | 2 | hiện | 2 | +0.4167 | ✅ | ✅ | ✅ |
| AB3 | 3 | hiện | 3 | +0.375 | ✅ | ✅ | ✅ |
| AM2 | 2 | ẩn | 3 | -0.04167 | ✅ | ✅ | ✅ |
| AM3 | 3 | ẩn | 4 | -0.02639 | ✅ | ✅ | ✅ |
| BDF1 | 1 | ẩn | 1 | -0.5 | ✅ | ✅ | ✅ |
| BDF2 | 2 | ẩn | 2 | -0.2222 | ✅ | ✅ | ✅ |
| BDF3 | 3 | ẩn | 3 | -0.1364 | ✅ | ✅ | ✅ |
| BDF4 | 4 | ẩn | 4 | -0.096 | ✅ | ✅ | ✅ |
| BDF5 | 5 | ẩn | 5 | -0.07299 | ✅ | ✅ | ✅ |
| BDF6 | 6 | ẩn | 6 | -0.05831 | ✅ | ✅ | ✅ |
| Phương pháp A | 2 | hiện | 3 | +0.1667 | ✅ | ❌ | ❌ |
| Phương pháp B | 2 | ẩn | 1 | +4 | ✅ | ❌ | ❌ |

## Ví dụ 1 — Phương pháp A: nhất quán, không 0-ổn định

```
Phương pháp A  (explicit, k = 2)
  rho(z) = z^2 + 4z - 5
  sigma(z) = 4z + 2
  rho(1) = +0,  rho'(1) = +6,  sigma(1) = +6
  consistent: True   order p = 3   error constant C_{p+1} = +0.166667
  root condition: VIOLATED
    z = -5.000000 +0.000000i   |z| = 5.000000  <- |z| > 1
    z = +1.000000 +0.000000i   |z| = 1.000000
  Dahlquist verdict: NOT convergent

     t     nghiem chinh xac        phuong phap A         sai so
   0.0         1.000000e+00         1.000000e+00      0.000e+00
   0.5         6.065307e-01         6.081996e-01      1.669e-03
   1.0         3.678794e-01        -6.677259e+00      7.045e+00
   2.0         1.353353e-01        -1.243391e+08      1.243e+08
   4.0         1.831564e-02        -3.872979e+22      3.873e+22
   6.0         2.478752e-03        -1.206376e+37      1.206e+37

nghiem cua phuong trinh sai phan: lambda = [-4.705168  1.105168]
can phan ky |lambda_2| = 4.7052 > 1  ->  khuech dai moi buoc
  saved  figures/fig01_method_a.png
```

## Ví dụ 2 — Phương pháp B: ẩn, nhất quán, không 0-ổn định

```
Phương pháp B  (implicit, k = 2)
  rho(z) = z^2 - 4z + 3
  sigma(z) = - 2z^2
  rho(1) = +0,  rho'(1) = -2,  sigma(1) = -2
  consistent: True   order p = 1   error constant C_{p+1} = +4
  root condition: VIOLATED
    z = +3.000000 +0.000000i   |z| = 3.000000  <- |z| > 1
    z = +1.000000 +0.000000i   |z| = 1.000000
  Dahlquist verdict: NOT convergent

     t     nghiem chinh xac        phuong phap B         sai so
   0.0         1.000000e+00         1.000000e+00      0.000e+00
   0.5         6.065307e-01        -4.362861e+00      4.969e+00
   1.0         3.678794e-01        -5.683881e+03      5.684e+03
   2.0         1.353353e-01        -7.286041e+09      7.286e+09
   4.0         1.831564e-02        -1.197068e+22      1.197e+22
   6.0         2.478752e-03        -1.966737e+34      1.967e+34

nghiem cua phuong trinh sai phan: lambda = [4.081139 0.918861]
can phan ky |lambda_2| = 4.0811 > 1
  saved  figures/fig02_method_b.png
```

## Điều kiện nghiệm Dahlquist

```
      BDF2  |z| = [1.000, 0.333]   -> 0-on dinh
      BDF6  |z| = [0.863, 0.863, 1.000, 0.474, 0.474, 0.406]   -> 0-on dinh
Quy tắc điểm giữa  |z| = [1.000, 1.000]   -> 0-on dinh
      BDF7  |z| = [1.022, 1.022, 1.000, 0.539, 0.539, 0.426, 0.426]   -> KHONG 0-on dinh
Phương pháp A  |z| = [5.000, 1.000]   -> KHONG 0-on dinh
Phương pháp B  |z| = [3.000, 1.000]   -> KHONG 0-on dinh
  saved  figures/fig03_root_condition.png
```

## Bậc hội tụ đo được so với lý thuyết

```
bai toan: logistic   (y' = y(1-y),\ y(0) = 0.1)

BDF1  (bac ly thuyet p = 1, bac do duoc = 1.008)
  h   sai số tại T   bậc quan sát  
 ---: ---: ---: 
  0.2   1.0610e-03   -  
  0.1   5.2093e-04   1.03  
  0.05   2.5788e-04   1.01  
  0.025   1.2827e-04   1.01  
  0.0125   6.3962e-05   1.00  
  0.00625   3.1938e-05   1.00  
  0.003125   1.5958e-05   1.00   

BDF2  (bac ly thuyet p = 2, bac do duoc = 2.020)
  h   sai số tại T   bậc quan sát  
 ---: ---: ---: 
  0.2   1.1560e-04   -  
  0.1   2.7398e-05   2.08  
  0.05   6.6900e-06   2.03  
  0.025   1.6542e-06   2.02  
  0.0125   4.1135e-07   2.01  
  0.00625   1.0257e-07   2.00  
  0.003125   2.5609e-08   2.00   

BDF3  (bac ly thuyet p = 3, bac do duoc = 3.008)
  h   sai số tại T   bậc quan sát  
 ---: ---: ---: 
  0.2   1.4670e-05   -  
  0.1   1.8024e-06   3.02  
  0.05   2.2321e-07   3.01  
  0.025   2.7753e-08   3.01  
  0.0125   3.4550e-09   3.01  
  0.00625   4.3109e-10   3.00  
  0.003125   5.3910e-11   3.00   

AB2  (bac ly thuyet p = 2, bac do duoc = 2.014)
  h   sai số tại T   bậc quan sát  
 ---: ---: ---: 
  0.2   1.3975e-04   -  
  0.1   3.3894e-05   2.04  
  0.05   8.3314e-06   2.02  
  0.025   2.0646e-06   2.01  
  0.0125   5.1384e-07   2.01  
  0.00625   1.2817e-07   2.00  
  0.003125   3.2006e-08   2.00   

AM2  (bac ly thuyet p = 3, bac do duoc = 3.004)
  h   sai số tại T   bậc quan sát  
 ---: ---: ---: 
  0.2   2.3792e-06   -  
  0.1   2.9620e-07   3.01  
  0.05   3.6929e-08   3.00  
  0.025   4.6012e-09   3.00  
  0.0125   5.6838e-10   3.02  
  0.00625   7.1497e-11   2.99  
  0.003125   8.9652e-12   3.00   

Phương pháp A tren bai toan phân rã mũ:
   sai so tai T = [1.69e+17 1.21e+37 1.24e+50 3.16e+50 2.73e+50 3.15e+50 4.20e+50]
   -> giam h khong lam giam sai so: khong hoi tu (dung nhu dinh ly Dahlquist).
  saved  figures/fig04_convergence.png
```

## Miền ổn định tuyệt đối

```
do rong mien on dinh tuyet doi tren truc thuc am (h*lambda thuc):
  AB1    (-2.034, 0)
  AB2    (-1.017, 0)
  AB3    (-0.546, 0)
  BDF1   toan bo truc thuc am
  BDF2   toan bo truc thuc am
  BDF3   toan bo truc thuc am
  BDF4   toan bo truc thuc am

BDF khong bi chan tren truc thuc am -> phu hop bai toan cung (stiff).
  saved  figures/fig05_stability_regions.png
```

## Rào cản Dahlquist và giới hạn k ≤ 6 của BDF

```
 k  BDF bac p   max |z|  ket luan
 1          1    1.0000  0-on dinh
 2          2    1.0000  0-on dinh
 3          3    1.0000  0-on dinh
 4          4    1.0000  0-on dinh
 5          5    1.0000  0-on dinh
 6          6    1.0000  0-on dinh
 7          7    1.0222  KHONG 0-on dinh -> vo dung
 8          8    1.1839  KHONG 0-on dinh -> vo dung

Rao can Dahlquist thu nhat: bac toi da cua phuong phap k buoc 0-on dinh
 k   AB   AM  BDF  chan tren
 1    1    2    1          2
 2    2    3    2          4
 3    3    4    3          4
 4    4    5    4          6
 5    5    6    5          6
 6    6    7    6          8
  saved  figures/fig06_dahlquist_barrier.png
```

## Bảng LaTeX cho báo cáo

```
  BDF1  p = 1, bậc đo được = 1.013
  BDF2  p = 2, bậc đo được = 2.032
  BDF3  p = 3, bậc đo được = 3.012
  AB2   p = 2, bậc đo được = 2.021
  AM2   p = 3, bậc đo được = 3.007
  saved  Sections/generated/convergence_table.tex
  saved  Sections/generated/method_summary.tex
  saved  Sections/generated/bdf_stability.tex
```
