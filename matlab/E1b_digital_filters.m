%% IACV - Image Filtering in MATLAB
%  A gallery of convolution, and various filters
%  Luca Magri 
%  Politecnico di Milano
%  2025

clc; clear; close all;

%% Setup and Helper Functions
set(0,'DefaultFigurePosition',[100 100 1200 900]);
set(0,'DefaultAxesFontSize',12);

% Helper function to display images (similar to Python's imshow wrapper)
function imshow_helper(img, titleStr)
    if nargin < 2
        titleStr = '';
    end
    imshow(img, []);
    if ~isempty(titleStr)
        title(titleStr);
    end
    axis off;
end

% Helper function to display matrices with color-coded entries
function display_matrix(matrix, titleStr)
    if nargin < 2
        titleStr = '';
    end
    figure;
    imagesc(matrix);
    colormap('summer');
    colorbar;
    
    % Add text annotations for matrix values
    for i = 1:size(matrix, 1)
        for j = 1:size(matrix, 2)
            text(j, i, sprintf('%.2f', matrix(i, j)), ...
                'HorizontalAlignment', 'center', 'Color', 'black', 'FontWeight', 'bold');
        end
    end
    
    if ~isempty(titleStr)
        title(titleStr);
    end
    axis off;
end

%% LOAD TEST IMAGE
% Load image for filtering experiments
try
    img = imread('Data/cat.jpg');
    if size(img, 3) == 3
        img = rgb2gray(img);
    end
    img = imresize(img,0.2);
catch
    % Fallback to MATLAB built-in image
    img = imread('cameraman.tif');
    fprintf('Using built-in cameraman.tif image\n');
end

figure;
imshow_helper(img, 'Original Image');



%% 1D CONVOLUTION IMPLEMENTATION
function result = convolve1D(vector, filter)
    % Take 1D vector and 1D filter, compute convolution
    vector_length = length(vector);
    filter_length = length(filter);
    pad_size = filter_length - 1;
    
    % Cast data to double
    vector = double(vector);
    filter = double(filter);
    
    % Flip the filter (key difference from correlation)
    filter = flip(filter);
    
    % Pad vector with zeros
    padded_vector = [zeros(1, pad_size), vector, zeros(1, pad_size)];
    
    % Initialize result
    result = zeros(1, vector_length + pad_size);
    
    % Perform convolution
    for i = 1:(vector_length + pad_size)
        region = padded_vector(i:(i + filter_length - 1));
        convolution_result = sum(region .* filter);
        result(i) = convolution_result;
    end
end

% Test 1D convolution
fprintf(' Testing 1D Convolution \n');
a = [1, 2, 3];
b = [0, 1, 0.5];
y1 = convolve1D(a, b);
y2 = conv(a, b);
fprintf('Custom convolution: [%.2f, %.2f, %.2f, %.2f, %.2f]\n', y1);
fprintf('MATLAB conv:       [%.2f, %.2f, %.2f, %.2f, %.2f]\n', y2);

%%  MOVING AVERAGE EXAMPLE
% Create sinusoidal data corrupted by noise
t = 0:0.1:(4*pi);
x = sin(t) + 0.5 * randn(size(t));

% Apply moving average filter
window_size = 30;
f = (1/window_size) * ones(1, window_size);
y = convolve1D(x, f);

figure;
plot(t, x, 'b-', 'LineWidth', 1);
hold on;
plot(t, y(1:length(t)), 'r-', 'LineWidth', 2);
legend('Noisy Signal', 'Filtered Signal');
title('Moving Average Filter Example');
xlabel('Time');
ylabel('Amplitude');
grid on;

%% 2D CONVOLUTION IMPLEMENTATION
function result = myconvolve2D(image, filter)
    % Get dimensions of image and filter
    [image_height, image_width] = size(image);
    [filter_height, filter_width] = size(filter);
    
    % Cast data to double
    image = double(image);
    filter = double(filter);
    
    % Flip the filter (both horizontally and vertically)
    filter = flipud(fliplr(filter));
    
    % Calculate padding for both dimensions
    pad_height = floor(filter_height / 2);
    pad_width = floor(filter_width / 2);
    
    % Create padded image with zeros
    padded_image = padarray(image, [pad_height, pad_width]);
    
    % Initialize output result with same dimension as input
    result = zeros(size(image));
    
    % Perform convolution: loop through all pixels
    for r = 1:image_height
        for c = 1:image_width
            % Extract local region from padded image
            region = padded_image(r:(r + filter_height - 1), c:(c + filter_width - 1));
            
            % Element-wise multiplication and sum
            convolution_result = sum(sum(region .* filter));
            
            % Assign result to corresponding position
            result(r, c) = convolution_result;
        end
    end
end

% Test 2D convolution
fprintf('\n=== Testing 2D Convolution ===\n');
A = rand(5, 5);
B = rand(3, 3);
Y1 = myconvolve2D(A, B);
Y2 = conv2(A, B, 'same');
fprintf('Difference between implementations: %.6f (should be close to 0)\n', max(abs(Y1(:) - Y2(:))));

%% SMOOTHING FILTERS

%% Mean Filter (Box Filter)
filter_size = 10;
filter_uniform = ones(filter_size, filter_size) / (filter_size^2);

% Display the filter
display_matrix(filter_uniform, 'Mean Filter Kernel');

% Apply mean filter
img_mean = myconvolve2D(img, filter_uniform);

figure;
subplot(1, 2, 1);
imshow_helper(img, 'Original');
subplot(1, 2, 2);
imshow_helper(uint8(img_mean), 'Mean Filter');

%% Effect of Different Filter Sizes
filter_sizes = [5, 11, 25, 31, 71];
figure;
for i = 1:length(filter_sizes)
    w = filter_sizes(i);
    
    % Create filter of increasing dimension
    filter_w = ones(w, w) / (w^2);
    
    % Apply filter
    img_w = myconvolve2D(img, filter_w);
    
    % Display filtered images
    subplot(1, length(filter_sizes), i);
    imshow_helper(uint8(img_w), sprintf('Filter size %d', w));
end

%% Gaussian Filter
sigma = 2;
gaussian_1d = fspecial('gaussian', [filter_size, 1], sigma);
filter_gaussian = gaussian_1d * gaussian_1d';

% Display Gaussian filter
figure;
subplot(1, 2, 1);
plot(gaussian_1d);
title('1D Gaussian');
xlabel('Position');
ylabel('Weight');

subplot(1, 2, 2);
display_matrix(filter_gaussian, 'Gaussian Kernel');

% Apply Gaussian filter
img_gaussian = myconvolve2D(img, filter_gaussian);

figure;
subplot(1, 2, 1);
imshow_helper(img, 'Original');
subplot(1, 2, 2);
imshow_helper(uint8(img_gaussian), 'Gaussian Filter');



%% Compare All Smoothing Methods
figure;
subplot(1, 3, 1);
imshow_helper(img, 'Original');
subplot(1, 3, 2);
imshow_helper(uint8(img_mean), 'Mean');
subplot(1, 3, 3);
imshow_helper(uint8(img_gaussian), 'Gaussian');

%%  EDGE DETECTION

%% Sobel Operator
% Define Sobel operators
Mx = [-1, 0, 1; -2, 0, 2; -1, 0, 1];  % Horizontal edges
My = [1, 2, 1; 0, 0, 0; -1, -2, -1];   % Vertical edges

% Display Sobel operators
figure;
subplot(1, 2, 1);
display_matrix(Mx, 'Sobel X (Horizontal Edges)');
subplot(1, 2, 2);
display_matrix(My, 'Sobel Y (Vertical Edges)');

% Apply small Gaussian filter first to reduce noise
filter_size_small = 3;
sigma_small = 2;
gaussian_small = fspecial('gaussian', filter_size_small, sigma_small);
img_smooth = myconvolve2D(img, gaussian_small);

% Apply Sobel operators
img_x = myconvolve2D(img_smooth, Mx);  % Gradient along x
img_y = myconvolve2D(img_smooth, My);  % Gradient along y

% Compute gradient magnitude and angle
img_magnitude = sqrt(img_x.^2 + img_y.^2);
img_angle = atan2(img_y, img_x);

% Display results
figure;
subplot(2, 2, 1);
imshow_helper(img_x, 'Intensity variation along x');
subplot(2, 2, 2);
imshow_helper(img_y, 'Intensity variation along y');
subplot(2, 2, 3);
imshow_helper(img_magnitude, 'Gradient magnitude');
subplot(2, 2, 4);
imshow_helper(img_angle, 'Gradient angle');

%%  Edge Detection by Thresholding
threshold = 150;
img_edges_sobel = img_magnitude > threshold;

figure;
subplot(1, 2, 1);
imshow_helper(img_edges_sobel, 'Sobel Edge Detection');

% Compare with MATLAB's built-in Canny edge detector
min_val = threshold;
max_val = 180;
img_edges_canny = edge(img, 'canny', [min_val/255, max_val/255]);

subplot(1, 2, 2);
imshow_helper(img_edges_canny, 'Canny Edge Detection');

%%  IMAGE SHARPENING
% Define Laplacian sharpening mask
M_L = [0, -1, 0; -1, 5, -1; 0, -1, 0];

% Display sharpening kernel
display_matrix(M_L, 'Laplacian Sharpening Kernel');

% Apply sharpening filter
img_sharp = myconvolve2D(img, M_L);

% Ensure values are in valid range
img_sharp = max(0, min(255, img_sharp));

figure;
subplot(1, 2, 1);
imshow_helper(img, 'Original Image');
subplot(1, 2, 2);
imshow_helper(uint8(img_sharp), 'Sharpened Image');



%


