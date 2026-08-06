%% Metric rectification from orthogonal lines
% 
% perform metric rectification of an image.
% Given at least 5 pairs of image of orthogonal lines, the script finds the image 
% of the dual conic to circular points and computes the homography that brings
% it back to its canonical form
%
%  Luca Magri
%  Politecnico di Milano
%  2020

clear;
close all;
img = imread('Data/img1.JPG');
%%
figure;
imshow(img);
numConstraints = 5; %>=5
hold all;
fprintf('Draw 5 pairs of orthogonal segments\n');
count = 1;
A = zeros(numConstraints,6);

% select pairs of orthogonal segments
while (count <=numConstraints)
    figure(gcf);
    title(['Draw ', num2str(numConstraints),' pairs of orthogonal segments: step ',num2str(count) ]);
    col = 'rgbcmykwrgbcmykw';
    segment1 = drawline('Color',col(count));
    segment2 = drawline('Color',col(count));
    
    l = segToLine(segment1.Position);
    m = segToLine(segment2.Position);
    
    % each pair of orthogonal lines gives rise to a constraint on the image
    % of the dual conic of principal points imDCCP
    % [l(1)*m(1),0.5*(l(1)*m(2)+l(2)*m(1)),l(2)*m(2),0.5*(l(1)*m(3)+l(3)*m(1))
    %  0.5*(l(2)*m(3)+l(3)*m(2)), l(3)*m(3)]*v = 0
    % store the constraints in a matrix A
    A(count,:) = [l(1)*m(1),0.5*(l(1)*m(2)+l(2)*m(1)),l(2)*m(2),...
        0.5*(l(1)*m(3)+l(3)*m(1)),  0.5*(l(2)*m(3)+l(3)*m(2)), l(3)*m(3)];
    count = count+1;
end

%% Compute the imDCCP image of the dual conic to circular points

[~,~,v] = svd(A); %
sol = v(:,end); %sol = (a,b,c,d,e,f)  [a,b/2,d/2; b/2,c,e/2; d/2 e/2 f];
imDCCP = [sol(1)  , sol(2)/2, sol(4)/2;...
    sol(2)/2, sol(3)  , sol(5)/2;...
    sol(4)/2, sol(5)/2  sol(6)];


%% compute the rectifying homography

[U,D,V] = svd(imDCCP);
D(3,3) = 1;
A = U*sqrt(D);
%%

C = [eye(2),zeros(2,1);zeros(1,3)];
min(norm(A*C*A' - imDCCP),norm(A*C*A' + imDCCP))

H = inv(A); % rectifying homography
min(norm(H*imDCCP*H'./norm(H*imDCCP*H') - C./norm(C)),norm(H*imDCCP*H'./norm(H*imDCCP*H') + C./norm(C)))

%%
tform = projective2d(H');
J = imwarp(img,tform);

figure;
imshow(J);
