% Kiem chung bac hoi tu cua ho BDF1-BDF3 tren bai toan y' = -y, y(0) = 1.
% Doi ung Python: python code/experiments/ex04_convergence.py
clear; clc;

f       = @(t, y) -y;
y_exact = @(t) exp(-t);
t0 = 0; T = 2;
hs = [0.2 0.1 0.05 0.025 0.0125];

% Moi hang: [alpha_0 ... alpha_k] cua sum alpha_j Y_{n+j} = h f_{n+k}
bdf = { [-1 1], [1/2 -2 3/2], [-1/3 3/2 -3 11/6] };

fprintf('%6s', 'h');
for m = 1:numel(bdf); fprintf('%14s', sprintf('BDF%d', m)); end
fprintf('\n');

errs = zeros(numel(bdf), numel(hs));
for ih = 1:numel(hs)
    h = hs(ih);
    N = round((T - t0) / h);
    t = t0 + (0:N) * h;
    fprintf('%6.4f', h);
    for m = 1:numel(bdf)
        a = bdf{m};
        k = numel(a) - 1;
        y = zeros(1, N + 1);
        y(1:k) = y_exact(t(1:k));           % khoi tao bang nghiem chinh xac
        for n = 1:(N + 1 - k)
            rhs = -a(1:k) * y(n:n+k-1)';    % phan da biet
            y(n+k) = rhs / (a(k+1) + h);    % giai an: a_k*Y - h*(-Y) = rhs
        end
        errs(m, ih) = abs(y(end) - y_exact(t(end)));
        fprintf('%14.4e', errs(m, ih));
    end
    fprintf('\n');
end

fprintf('\nBac quan sat (log2 cua ty so sai so lien tiep):\n');
for m = 1:numel(bdf)
    p = log2(errs(m, 1:end-1) ./ errs(m, 2:end));
    fprintf('  BDF%d: %s\n', m, num2str(p, '%8.2f'));
end
