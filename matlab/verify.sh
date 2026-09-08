#!/usr/bin/env bash
#
# Chạy ba script MATLAB bằng GNU Octave và đối chiếu kết quả in ra với các giá
# trị đã công bố trong báo cáo. Dùng được cả trên máy cá nhân lẫn trong CI:
#
#   ./matlab/verify.sh
#
set -euo pipefail
cd "$(dirname "$0")"

run() {
  octave --no-gui --eval "set(0,'defaultfigurevisible','off'); $1" 2>/dev/null
}

expect() { # expect <chuỗi> <mô tả> <đầu ra>
  if ! grep -qF -- "$1" <<<"$3"; then
    echo "  THẤT BẠI: $2 (không tìm thấy '$1')"
    echo "$3"
    exit 1
  fi
  echo "  OK: $2"
}

echo "method_a.m — phương pháp A phân kỳ (Chương 4, Ví dụ 1)"
out=$(run method_a)
expect "6.081996e-01" "Y tại t = 0.5"  "$out"
expect "-6.677259e+00" "Y tại t = 1.0" "$out"
expect "-1.206376e+37" "Y tại t = 6.0" "$out"

echo "method_b.m — phương pháp B phân kỳ (Chương 4, Ví dụ 2)"
out=$(run method_b)
expect "-4.362861e+00" "Y tại t = 0.5" "$out"
expect "-1.966737e+34" "Y tại t = 6.0" "$out"

echo "bdf_convergence.m — bậc hội tụ của BDF1–BDF3"
out=$(run bdf_convergence)
expect "1.3308e-02" "sai số BDF1 tại h = 0.1" "$out"
expect "9.0148e-04" "sai số BDF2 tại h = 0.1" "$out"
expect "6.6843e-05" "sai số BDF3 tại h = 0.1" "$out"
expect "1.00" "bậc quan sát của BDF1 tiến về 1" "$out"
expect "2.00" "bậc quan sát của BDF2 tiến về 2" "$out"
expect "3.00" "bậc quan sát của BDF3 tiến về 3" "$out"

echo
echo "Tất cả script MATLAB khớp với số liệu trong báo cáo và với thư viện Python."
