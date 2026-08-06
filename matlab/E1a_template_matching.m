%% IACV: Template matching
%  Correlation between images can be used to find a template in a scene.
%  This snippets demonstrates a failure case when vanilla correlation is employed. 
%  Normalized-cross correlation solves the problem.  
% 
%  Luca Magri 
%  Politecnico di Milano
%  2025

clc; clear; close all;

%% Setup matplotlib-style parameters for consistent visualization
set(0,'DefaultFigurePosition',[100 100 1000 800]);
set(0,'DefaultAxesFontSize',12);

%% Helper function for image display
function imshow_matlab(img, titleStr)
if nargin < 2
    titleStr = '';
end
figure;
imshow(img, []);
if ~isempty(titleStr)
    title(titleStr);
end
axis off;
end

%% LOAD IMAGES
img = imread('Data/tea_scene.jpg');
if size(img, 3) == 3
    img = rgb2gray(img);
end


% Display main image
figure;
imshow(img, []);
title('Main Image');
axis off;

%% Load template image

template = imread('Data/template.jpg');
if size(template, 3) == 3
    template = rgb2gray(template);
end

% Display template image
figure;
imshow(template, []);
title('Template Image');


%% BASIC CORRELATION IMPLEMENTATION
function result = compute_correlation(image, template)
% Get the dimensions of the image and template
[image_height, image_width] = size(image);
[template_height, template_width] = size(template);

% Cast the data to double
image = double(image);
template = double(template);

% Initialize result array to store correlation values
result = zeros(image_height - template_height + 1, ...
    image_width - template_width + 1);

% Loop through each pixel in the image to compute correlation
for y = 1:(image_height - template_height + 1)
    for x = 1:(image_width - template_width + 1)
        % Extract the region in the image that matches template size
        region = image(y:y + template_height - 1, x:x + template_width - 1);

        % Compute correlation between region and template
        correlation = sum(sum(region .* template));

        % Store correlation value in result array
        result(y, x) = correlation;
    end
end
end

%% NORMALIZED CROSS-CORRELATION IMPLEMENTATION
function result = compute_NN_correlation(image, template)
% Get the dimensions of the image and template
[image_height, image_width] = size(image);
[template_height, template_width] = size(template);

% Cast the data to double
image = double(image);
template = double(template);

% Prepare template: flatten and zero-mean
A = template(:);
mean_A = mean(A);
A = A - mean_A;

% Initialize result array
result = zeros(image_height - template_height + 1, ...
    image_width - template_width + 1);

% Loop through each pixel in the image
for y = 1:(image_height - template_height + 1)
    for x = 1:(image_width - template_width + 1)
        % Extract the region in the image that matches template size
        region = image(y:y + template_height - 1, x:x + template_width - 1);

        % Prepare region: flatten and zero-mean
        B = region(:);
        mean_B = mean(B);
        B = B - mean_B;

        % Compute normalized cross-correlation
        correlation = dot(A, B) / sqrt(dot(A, A) * dot(B, B));

        % Store correlation value in result array
        result(y, x) = correlation;
    end
end
end

%%  COMPUTE CORRELATION
% Choose which correlation method to use
fprintf('Computing normalized cross-correlation...\n');
%correlation_image = compute_correlation(img, template);
correlation_image = compute_NN_correlation(img, template);

% Display correlation result
figure;
imshow(correlation_image, []);
title('Correlation Result');
colormap('gray');
colorbar;

% Display dimensions
fprintf('Image: %d x %d\n', size(img, 1), size(img, 2));
fprintf('Template: %d x %d\n', size(template, 1), size(template, 2));
fprintf('Correlation: %d x %d\n', size(correlation_image, 1), size(correlation_image, 2));

%%  FIND MAXIMUM CORRELATION
% Get the pixel corresponding to highest correlation
[max_val, linear_idx] = max(correlation_image(:));
[r, c] = ind2sub(size(correlation_image), linear_idx);

fprintf('The maximum correlation is reached at (%d, %d) and equals %.6f\n', ...
    r, c, correlation_image(r, c));
fprintf('Normalized value: %.6f\n', correlation_image(r, c) / max(correlation_image(:)));

%% EXTRACT DETECTION REGION
[template_height, template_width] = size(template);
detection = img(r:r + template_height - 1, c:c + template_width - 1);

% Display comparison: Template vs Detection
figure;
subplot(1, 3, 1);
imshow(template, []);
title('Template');
axis on;

subplot(1, 3, 2);
imshow(detection, []);
title('Detection');
axis on;

% Show correlation result with peak marked
subplot(1, 3, 3);
imshow(correlation_image, []);
title('Correlation with Peak');
hold on;
plot(c, r, 'r+', 'MarkerSize', 20, 'LineWidth', 3);
hold off;

%%  ALPHA BLENDING VISUALIZATION
% Create mask image that indicates the detection
mask = zeros(size(img));
mask(r:r + template_height - 1, c:c + template_width - 1) = 255;

% Alpha blending: superimpose detection on original image
alpha = 0.7;
detection_overlay = (1 - alpha) * double(img) + alpha * mask;

figure;
imshow(detection_overlay, []);
title('Image with Detection Overlay');
axis off;

%%  COMPARISON WITH MATLAB BUILT-IN FUNCTIONS
fprintf('\n=== Comparison with MATLAB Built-in Functions ===\n');

% Using MATLAB's normxcorr2 for comparison
tic;
matlab_correlation = normxcorr2(template, img);
matlab_time = toc;

% Find peak in MATLAB result
[matlab_max_val, matlab_linear_idx] = max(matlab_correlation(:));
[matlab_peak_y, matlab_peak_x] = ind2sub(size(matlab_correlation), matlab_linear_idx);

% Convert to original image coordinates
matlab_actual_x = matlab_peak_x - size(template, 2);
matlab_actual_y = matlab_peak_y - size(template, 1);

fprintf('MATLAB normxcorr2 peak at: (%d, %d)\n', matlab_actual_y, matlab_actual_x);
fprintf('Our implementation peak at: (%d, %d)\n', r, c);
fprintf('MATLAB normxcorr2 execution time: %.4f seconds\n', matlab_time);

% Display MATLAB result
figure;
imshow(matlab_correlation, []);
title('MATLAB normxcorr2 Result');
hold on;
plot(matlab_peak_x, matlab_peak_y, 'r+', 'MarkerSize', 20, 'LineWidth', 3);
hold off;
colorbar;




%%  PERFORMANCE COMPARISON
function compare_methods(image, template)
fprintf('\n=== Performance Comparison ===\n');

% Time our basic correlation
tic;
basic_corr = compute_correlation(image, template);
basic_time = toc;

% Time our normalized correlation
tic;
norm_corr = compute_NN_correlation(image, template);
norm_time = toc;

% Time MATLAB's built-in
tic;
matlab_corr = normxcorr2(template, image);
matlab_time = toc;

fprintf('Basic correlation time: %.4f seconds\n', basic_time);
fprintf('Normalized correlation time: %.4f seconds\n', norm_time);
fprintf('MATLAB normxcorr2 time: %.4f seconds\n', matlab_time);
fprintf('Speed improvement with MATLAB: %.1fx\n', norm_time / matlab_time);
end

% Run performance comparison
compare_methods(img, template);
