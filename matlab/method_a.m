% Vi du 1 - Phuong phap A: Y_{n+2} + 4Y_{n+1} - 5Y_n = h(4 f_{n+1} + 2 f_n)
% Nhat quan bac 3 nhung vi pham dieu kien nghiem (z = -5) => phan ky.
% Trich tu Chuong 4 cua bao cao; ban Python tuong duong:
%   python code/experiments/ex01_method_a.py

clear; clc; close;

% ---- Thiet lap bai toan ----
f      = @(t, y) -y;          % ve phai phuong trinh vi phan
y_exact = @(t) exp(-t);       % nghiem chinh xac
t0 = 0;
T  = 6;                        % thoi diem cuoi
h  = 0.1;                      % buoc luoi

N = round((T - t0) / h);
t = t0 + (0:N) * h;

% ---- Khoi tao (lay tu nghiem giai tich, loai bo sai so khoi tao) ----
y = zeros(1, N + 1);
y(1) = y_exact(t(1));   % y0
y(2) = y_exact(t(2));   % y1

% ---- Vong lap Phuong phap A (hien) ----
for n = 1:(N - 1)
    fn1 = f(t(n+1), y(n+1));   % f_{n+1}
    fn  = f(t(n),   y(n));     % f_n
    y(n+2) = -4*y(n+1) + 5*y(n) + h * (4*fn1 + 2*fn);
end

% ---- Nghiem chinh xac va sai so ----
yex = y_exact(t);
err = abs(y - yex);

% ---- In bang ket qua tai mot so moc thoi gian ----
moc = [0.0, 0.5, 1.0, 2.0, 4.0, 6.0];
fprintf('%8s %18s %18s %14s\n', 't', 'Nghiem chinh xac', 'Phuong phap A', 'Sai so |y-yex|');
for k = 1:length(moc)
    [~, idx] = min(abs(t - moc(k)));
    fprintf('%8.1f %18.6e %18.6e %14.3e\n', t(idx), yex(idx), y(idx), err(idx));
end


thresh = 1;
symlog = @(x) sign(x) .* log10(1 + abs(x) / thresh);

% ---- Do thi ----

% Thang symlog
figure(1);
plot(t, symlog(yex), 'k-', 'LineWidth', 1.5); hold on;
plot(t, symlog(y),   'r--', 'LineWidth', 1.2);
legend('Nghiem chinh xac', 'Phuong phap A', 'Location', 'best');
xlabel('t'); ylabel('symlog( y(t) )');
title('So sanh nghiem: Phuong phap A vs nghiem chinh xac (truc y thang symlog)');
grid on;

% Ve lai nhan truc tung theo gia tri that
yt = get(gca, 'YTick');
yticklabels_real = arrayfun(@(v) sprintf('%.0e', sign(v)*(10^abs(v)-1)*thresh), yt, 'UniformOutput', false);
set(gca, 'YTickLabel', yticklabels_real);

% Thang binh thuong
figure(2);
subplot(3,1,2);
plot(t, yex, 'k-', 'LineWidth', 1.5); hold on;
plot(t, y,   'r--', 'LineWidth', 1.2);
legend('Nghiem chinh xac', 'Phuong phap A', 'Location', 'best');
xlabel('t'); ylabel('y(t)');
title('So sanh nghiem: Phuong phap A va nghiem chinh xac');
grid on;

% Thang log cho sai so
figure(3);
semilogy(t, err, 'b-', 'LineWidth', 1.2);
xlabel('t'); ylabel('Sai so tuyet doi |y - y_{exact}|');
title('Sai so tuyet doi theo thoi gian (thang log)');
grid on;
