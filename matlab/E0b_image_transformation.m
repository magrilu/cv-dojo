%% IACV: Image transformation
% a gallery of pixel-wise transformations.
% histogram equalization is also presented.
%  
% Luca Magri
% Politecnico di Milano
% 2025
% Credits: based on snippets developed with Prof. Giacomo Boracchi
%%
clc; clear; close all;
%% INTENSITY TRANSFORMATIONS

% RGB to Grayscale Conversion
img_rgb = imread('Data/cat.jpg');
Gray = 0.299 * double(img_rgb(:,:,1)) + ...
       0.587 * double(img_rgb(:,:,2)) + ...
       0.114 * double(img_rgb(:,:,3));
Gray = uint8(Gray);

figure;
subplot(1,2,1); imshow(img_rgb); title('Original RGB');
subplot(1,2,2); imshow(Gray); title('Grayscale');

%% Negative Transformation
img_negative = 255 - Gray;

figure;
subplot(1,2,1); imshow(Gray); title('Original');
subplot(1,2,2); imshow(img_negative); title('Negative');

%% 4.3 Intensity Rescaling
% Create underexposed image for demonstration
img_underexposed = uint8(double(Gray) * 0.3 + 20);

% Apply intensity rescaling
img_vec = double(img_underexposed(:));
min_img = min(img_vec);
max_img = max(img_vec);
fprintf('The range of the image is [%d, %d]\n', min_img, max_img);

img_scaled = 255.0 * (double(img_underexposed) - min_img) / (max_img - min_img);
img_scaled = uint8(img_scaled);

figure;
subplot(1,2,1); imshow(img_underexposed); title('Underexposed');
subplot(1,2,2); imshow(img_scaled); title('Rescaled');

%% 4.4 Gamma Correction
gammas = [0.05, 0.1, 1, 2, 5];
figure;
for i = 1:length(gammas)
    gamma = gammas(i);
    img_gamma = 255 * (double(Gray)/255).^gamma;
    img_gamma = uint8(img_gamma);
    
    subplot(1, length(gammas), i);
    imshow(img_gamma);
    title(sprintf('gamma %.2f', gamma));
end

%% HISTOGRAM OPERATIONS

%%  Histogram Calculation and Display
img_gray = rgb2gray(img_rgb);
[counts, bins] = imhist(img_gray);

figure;
subplot(2,2,1); imshow(img_gray); title('Original Image');
subplot(2,2,2); bar(bins, counts); title('Histogram'); xlabel('Intensity'); ylabel('Count');

% 5.2 Histogram Equalization
img_eq = histeq(img_gray);
[counts_eq, bins_eq] = imhist(img_eq);

subplot(2,2,3); imshow(img_eq); title('Equalized Image');
subplot(2,2,4); bar(bins_eq, counts_eq); title('Equalized Histogram');

%% 5.3 Manual Histogram Equalization Implementation
function img_eq_manual = manual_histeq(img)
    img = double(img);
    [rows, cols] = size(img);
    N = rows * cols;
    
    % Calculate histogram
    hist_counts = zeros(256, 1);
    for intensity = 0:255
        hist_counts(intensity + 1) = sum(img(:) == intensity);
    end
    
    % Calculate PDF
    p = hist_counts / N;
    
    % Calculate transformation function (CDF)
    T = zeros(256, 1);
    for i = 1:256
        T(i) = floor(255 * sum(p(1:i)));
    end
    
    % Apply transformation
    img_eq_manual = zeros(size(img));
    for r = 1:rows
        for c = 1:cols
            intensity_value = img(r, c) + 1; % MATLAB indexing starts from 1
            img_eq_manual(r, c) = T(intensity_value);
        end
    end
    
    img_eq_manual = uint8(img_eq_manual);
end

% Test manual histogram equalization
img_manual_eq = manual_histeq(img_gray);

figure;
subplot(1,3,1); imshow(img_gray); title('Original');
subplot(1,3,2); imshow(img_eq); title('Built-in histeq');
subplot(1,3,3); imshow(img_manual_eq); title('Manual histeq');

%% Histogram Matching
function matched_image = histogram_match(source_image, target_image)
    source_image = double(source_image);
    target_image = double(target_image);
    
    % Compute histograms
    [source_counts, ~] = imhist(uint8(source_image));
    [target_counts, ~] = imhist(uint8(target_image));
    
    % Normalize to get PDFs
    source_pdf = source_counts / sum(source_counts);
    target_pdf = target_counts / sum(target_counts);
    
    % Compute CDFs
    source_cdf = cumsum(source_pdf);
    target_cdf = cumsum(target_pdf);
    
    % Create mapping
    mapping = zeros(256, 1);
    for i = 1:256
        [~, closest_idx] = min(abs(source_cdf(i) - target_cdf));
        mapping(i) = closest_idx - 1; % Convert back to 0-255 range
    end
    
    % Apply mapping
    matched_image = zeros(size(source_image));
    for i = 1:numel(source_image)
        intensity = source_image(i) + 1; % MATLAB indexing
        matched_image(i) = mapping(intensity);
    end
    
    matched_image = uint8(matched_image);
end

% Test histogram matching
target_img = histeq(img_gray); % Use equalized image as target
matched_img = histogram_match(img_gray, target_img);

figure;
subplot(2,3,1); imshow(img_gray); title('Source');
subplot(2,3,2); imshow(target_img); title('Target');
subplot(2,3,3); imshow(matched_img); title('Matched');
subplot(2,3,4); imhist(img_gray); title('Source Histogram');
subplot(2,3,5); imhist(target_img); title('Target Histogram');
subplot(2,3,6); imhist(matched_img); title('Matched Histogram');

%%  LOCAL HISTOGRAM EQUALIZATION

im_mistery = imread('Data/hidden-symbols.png');

function output_image = local_histogram_equalization(image, kernel_size)
    if size(image, 3) == 3
        image = rgb2gray(image);
    end
    
    % Pad the image to handle borders
    pad_size = floor(kernel_size / 2);
    padded_image = padarray(image, [pad_size, pad_size], 'symmetric');
    
    % Create output image
    output_image = zeros(size(image));
    
    % Slide the window over the image
    for i = pad_size + 1 : size(padded_image, 1) - pad_size
        for j = pad_size + 1 : size(padded_image, 2) - pad_size
            % Extract local window
            local_window = padded_image(i - pad_size : i + pad_size, ...
                                      j - pad_size : j + pad_size);
            
            % Equalize histogram in local window
            equalized_window = histeq(local_window);
            
            % Take center pixel value
            output_image(i - pad_size, j - pad_size) = ...
                equalized_window(pad_size + 1, pad_size + 1);
        end
    end
    
    output_image = uint8(output_image);
end

% Test local histogram equalization
local_eq_img = local_histogram_equalization(im_mistery, 15);

figure;
subplot(1,2,1); imshow(im_mistery); title('Original');
subplot(1,2,2); imshow(local_eq_img); title('Local Histogram Equalization');