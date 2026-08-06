% HOUGH TRANSFORM FOR LINE DETECTION (ρ, θ)
% Image Analysis and Computer Vision
% Politecnico di Milano
%
% Luca Magri
% for comments and suggestions please send an email to luca.magri@polimi.it
%
% .\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.
close all; clear; clc;

%% Generate synthetic data: points on a line

num_inliers = 100;

% True line: rho, theta
theta_true = pi/4;      % 45 degrees
rho_true   = 1.2;

% Generate inlier points
t = linspace(-1, 1, num_inliers);
x = t;
y = (rho_true - x*cos(theta_true)) / sin(theta_true);

X_in = [x; y];

% Add noise
sigma = 0.01;
X_in = X_in + sigma * randn(size(X_in));

%% Bounding box of inliers
minx = min(X_in(1,:));
maxx = max(X_in(1,:));
miny = min(X_in(2,:));
maxy = max(X_in(2,:));

%% Generate outliers 
num_outliers = 40;

out_x = (maxx - minx)*rand(1, num_outliers) + minx;
out_y = (maxy - miny)*rand(1, num_outliers) + miny;
X_out = [out_x; out_y];

%% Data
X = [X_in, X_out];

figure;
scatter(X(1,:), X(2,:), 15, 'k', 'filled');
axis equal; grid on;
title("Inliers + Outliers inside bounding box");

%% Hough Transform Parameters

Ntheta = 180;
Nrho   = 250;

thetas = linspace(0, pi, Ntheta);

% rho range — use diagonal of bounding box
max_rho = sqrt((maxx-minx)^2 + (maxy-miny)^2);
rhos = linspace(-max_rho, max_rho, Nrho);

H = zeros(Nrho, Ntheta);

%% Voting

for p = 1:size(X,2)
    x = X(1,p);
    y = X(2,p);

    for it = 1:Ntheta
        theta = thetas(it);
        rho = x*cos(theta) + y*sin(theta);
        [~, ir] = min(abs(rhos - rho));
        H(ir, it) = H(ir, it) + 1;
    end
end

%% Find strongest peak in H

H_flat = H(:);
[~, idx] = max(H_flat);
[ir_max, it_max] = ind2sub(size(H), idx);

rho_est   = rhos(ir_max);
theta_est = thetas(it_max);

disp("Estimated line");
fprintf("rho   = %.4f\n", rho_est);
fprintf("theta = %.4f rad (%.2f deg)\n", theta_est, theta_est*180/pi);

disp("Ground Truth");
fprintf("rho   = %.4f\n", rho_true);
fprintf("theta = %.4f rad (%.2f deg)\n", theta_true, theta_true*180/pi);

%% Plot Hough accumulator

figure;
imagesc(thetas*180/pi, rhos, H);
colormap hot; colorbar;
xlabel('\theta (deg)');
ylabel('\rho');
title("Hough Accumulator");
hold on;
plot(theta_est*180/pi, rho_est, 'go', 'MarkerSize', 10, 'LineWidth', 2);

%% Plot detected line

figure; hold on; grid on; axis equal;
scatter(X(1,:), X(2,:), 15, 'k', 'filled');

xx = linspace(minx-0.5, maxx+0.5, 400);

% True line
yy_true = (rho_true - xx*cos(theta_true)) / sin(theta_true);
plot(xx, yy_true, 'r--', 'LineWidth', 2);

% Estimated line
yy_est = (rho_est - xx*cos(theta_est)) / sin(theta_est);
plot(xx, yy_est, 'g', 'LineWidth', 2);

legend("data", "true line", "estimated line");
title("Line Detection via Hough Transform (ρ, θ)");
