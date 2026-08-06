%% IACV: Basic image manipulation
%  Images are just matrices, a demonstration of the "green-screen" trick.
%  
%  Luca Magri 
%  Politecnico di Milano
%  2025
% Credits: based on snippets developed with Prof. Giacomo Boracchi
%%
clc; clear; close all;
%% Image generation - Italian Flag
% Create a 3D matrix that displays as an RGB image
A = 255 * ones(330, 495, 3, 'uint8'); % Initialize white flag
WIDTH = floor(size(A,2)/3); % Integer division to get an index

% Left vertical band (green)
A(:, 1:WIDTH, 1) = 0;   % R: no red in green
A(:, 1:WIDTH, 2) = 146; % G
A(:, 1:WIDTH, 3) = 70;  % B

% Central band remains white (no changes needed)

% Right vertical band (red)
A(:, 2*WIDTH+1:end, 1) = 206; % R
A(:, 2*WIDTH+1:end, 2) = 43;  % G
A(:, 2*WIDTH+1:end, 3) = 55;  % B

% Display the flag
figure;
imshow(A);
title('Italian Flag!');
axis equal;


%% Datatype matters
% Careful about data range: 
% [0 1] for double and logical, 
% [0 255] for uint8
figure;
subplot(1,3,1)
imshow(double(A));
title('[0,255] displayed in [0,1]')
%
% rescaling is necessary when casting to double images
subplot(1,3,2)
imshow(double(A)/255);
title('[0,1] displayed in [0,1]')
%
subplot(1,3,3)
imshow(uint8(double(A)/255));
title('[0,1] displayed in [0,255]')


%% 2. Image Superimposition
% Load images (replace with actual image loading)
B = imread('Data/background.jpg');
F = imread('Data/foreground.jpeg');



% Trivial superimposition
ul = [400, 1000]; % Upper left corner position
F_size = size(F);
Res = B; % Copy background

% Ensure we don't go out of bounds
end_r = min(ul(1) + F_size(1) - 1, size(B,1));
end_c = min(ul(2) + F_size(2) - 1, size(B,2));
F_rows = end_r - ul(1) + 1;
F_cols = end_c - ul(2) + 1;

Res(ul(1):end_r, ul(2):end_c, :) = F(1:F_rows, 1:F_cols, :);

figure;
subplot(1,3,1); imshow(B); title('Background');
subplot(1,3,2); imshow(F); title('Foreground');
subplot(1,3,3); imshow(Res); title('Trivial Superimposition');

%% 3. MASKED SUPERIMPOSITION

% Create mask for non-white pixels
th =250;
M3D = double(F);
M3D(:,:,1) = M3D(:,:,1) > th; % Red channel background detection
M3D(:,:,2) = M3D(:,:,2) > th; % Green channel background detection
M3D(:,:,3) = M3D(:,:,3) > th; % Blue channel background detection

% Pixels that are background in ALL channels
M = M3D(:,:,1) & M3D(:,:,2) & M3D(:,:,3);
M = 1 - M; % Invert mask: 1 where we keep F, 0 where we keep B

% Apply masked superimposition
S = B;
for ch = 1:3
    S(ul(1):end_r, ul(2):end_c, ch) = ...
        M(1:F_rows, 1:F_cols) .* double(F(1:F_rows, 1:F_cols, ch)) + ...
        (1 - M(1:F_rows, 1:F_cols)) .* double(S(ul(1):end_r, ul(2):end_c, ch));
end
S = uint8(S);

figure;
subplot(1,2,1); imshow(M, []); title('Mask'); colormap(gca, 'gray');
subplot(1,2,2); imshow(S); title('Masked Superimposition');



