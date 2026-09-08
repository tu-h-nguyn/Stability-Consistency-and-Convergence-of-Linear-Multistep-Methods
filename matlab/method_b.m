% Vi du 2 - Phuong phap B: Y_{n+2} - 4Y_{n+1} + 3Y_n = -2h f_{n+2}
% Phuong phap AN, nhat quan bac 1, nhung nghiem z = 3 pha vo dieu kien nghiem.
% Trich tu Chuong 4 cua bao cao; ban Python tuong duong:
%   python code/experiments/ex02_method_b.py

clear; clc; close all;

% Thiet lap bai toan
f       = @(t, y) -y;          
y_exact = @(t) exp(-t);       
t0 = 0;
T  = 6;                       
h  = 0.1;                     
N  = round((T - t0) / h);
t  = t0 + (0:N) * h;

% Khoi tao
y = zeros(1, N + 1);
y(1) = y_exact(t(1));   % y0
y(2) = y_exact(t(2));   % y1

% Phuong phap B
for n = 1:(N - 1)
    y(n+2) = (4*y(n+1) - 3*y(n)) / (1 - 2*h);
end

% Nghiem chinh xac va sai so
yex = y_exact(t);
err = abs(y - yex);

% ---- In bang ket qua tai mot so moc thoi gian ----
moc = [0.0, 0.5, 1.0, 2.0, 4.0, 6.0];
fprintf('%8s %18s %18s %14s\n', 't', 'Nghiem chinh xac', 'Phuong phap', 'Sai so');
for k = 1:length(moc)
    [~, idx] = min(abs(t - moc(k)));
    fprintf('%8.1f %18.6e %18.6e %14.3e\n', t(idx), yex(idx), y(idx), err(idx));
end

thresh = 1;
symlog = @(x) sign(x) .* log10(1 + abs(x) / thresh);

% ---- Do thi ----

% Hinh 1: Thang symlog
figure(1);
plot(t, symlog(yex), 'k-', 'LineWidth', 1.5); hold on;
plot(t, symlog(y),   'r--', 'LineWidth', 1.2);
legend('Nghiem chinh xac', 'Phuong phap B', 'Location', 'best');
xlabel('t'); ylabel('symlog( y(t) )');
title('Hinh 1: Phuong phap B vs Nghiem chinh xac (truc y thang symlog)');
grid on;

% Ve lai nhan truc tung theo gia tri that (chi de doc so, khong anh huong tinh toan)
yt = get(gca, 'YTick');
yticklabels_real = arrayfun(@(v) sprintf('%.0e', sign(v)*(10^abs(v)-1)*thresh), yt, 'UniformOutput', false);
set(gca, 'YTickLabel', yticklabels_real);

% Hinh 2: Thang binh thuong
figure(2);
plot(t, yex, 'k-', 'LineWidth', 1.5); hold on;
plot(t, y,   'r--', 'LineWidth', 1.2);
legend('Nghiem chinh xac', 'Phuong phap B', 'Location', 'best');
xlabel('t'); ylabel('y(t)');
title('Hinh 2: Phuong phap B va Nghiem chinh xac');
grid on;

% Hinh 3: Thang log cho sai so
figure(3);
semilogy(t, err, 'b-', 'LineWidth', 1.2);
xlabel('t'); ylabel('Sai so tuyet doi |y - y_{exact}|');
title('Hinh 3: Sai so tuyet doi theo thoi gian (thang log)');
grid on;
