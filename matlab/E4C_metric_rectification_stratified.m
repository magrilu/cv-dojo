%% Stratified metric promotion after affine rectification 
% 
% perform metric rectification of an image, after affine rectification.
% Given two pairs of image of orthogonal lines, the script finds the image 
% of the dual conic to circular points and computes the homography that brings
% it back to its canonical form
%
%  Luca Magri
%  Politecnico di Milano
%  2020

close all;
clear all;
clc;
imgAffRect = imread('Data/affRect.JPG');


figure;
imshow(imgAffRect);
numConstraints = 2;
%%
hold all;
fprintf('Draw pairs of orthogonal segments\n');
doAgain = 1;
count = 1;
A = zeros(numConstraints,3);
% select pairs of orthogonal segments
while (count <=numConstraints)
    figure(gcf);
    title('Select pairs of orthogonal segments')
    col = 'rgbcmykwrgbcmykw';
    segment1 = drawline('Color',col(count));
    segment2 = drawline('Color',col(count));
    
    l = segToLine(segment1.Position);
    m = segToLine(segment2.Position);
    
    % each pair of orthogonal lines gives rise to a constraint on s
    % [l(1)*m(1),l(1)*m(2)+l(2)*m(1), l(2)*m(2)]*s = 0
    % store the constraints in a matrix A
     A(count,:) = [l(1)*m(1),l(1)*m(2)+l(2)*m(1), l(2)*m(2)];

    count = count+1;
end

%% solve the system
%S = [x(1) x(2); x(2) 1];
[~,~,v] = svd(A);
s = v(:,end); %[s11,s12,s22];
S = [s(1),s(2); s(2),s(3)];
%% compute the rectifying homography

imDCCP = [S,zeros(2,1); zeros(1,3)]; % the image of the circular points
[U,D,V] = svd(S);
A = U*sqrt(D)*V';
H = eye(3);
H(1,1) = A(1,1);
H(1,2) = A(1,2);
H(2,1) = A(2,1);
H(2,2) = A(2,2);

Hrect = inv(H);
Cinfty = [eye(2),zeros(2,1);zeros(1,3)];

tform = projective2d(Hrect');
J = imwarp(imgAffRect,tform);

figure;
imshow(J);
