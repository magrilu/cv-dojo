%% Feature matching
%
% perform feature matching
%
% .\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.
%
% Image Analysis and Computer Vision
% Politecnico di Milano
%
% Luca Magri
% for comments and suggestions please send an email to luca.magri@polimi.it
%
% .\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.

addpath("Data/");
addpath("aux/");
im1 = imread("Data/polite1.JPG");
im2 = imread("Data/polite2.JPG");
im1 = imresize(im1,0.7);
im2 = imresize(im2,0.7);

figure; imshow(im1);
figure; imshow(im2);
%% detect interest points

% Edge threshold >=1. Increase the edge threshold to increase the features.
% Contrast threhsold. Increase the contrast threshold to decrease the number of features.
% sigma, decrease if the image is blurry
ip1 = detectSIFTFeatures(rgb2gray(im1));
ip2 = detectSIFTFeatures(rgb2gray(im2));
num_ip = 2000;
ip1 = ip1.selectStrongest(num_ip);
ip2 = ip2.selectStrongest(num_ip);
%%
figure; imshow(im1);
hold on;
plot(ip1,'ShowScale',true,'ShowOrientation',true);

figure; imshow(im2);
hold on;
plot(ip2)
%% descriptors
[f1,valid1] = extractFeatures(rgb2gray(im1),ip1,'Method','SIFT');
[f2,valid2] = extractFeatures(rgb2gray(im2),ip2,'Method','SIFT');
size(f1)

%% matching
indexPairs = matchFeatures(f1,f2,"MaxRatio",0.6);
matched1 = valid1(indexPairs(:,1));
matched2 = valid2(indexPairs(:,2));
size(matched1)
%% put in homogeneous coordinates
m1 = double([matched1.Location';ones(1,size(matched1.Location,1))]);
m2 = double([matched2.Location';ones(1,size(matched2.Location,1))]);

%% show matched features
figure;
subplot(1,2,1);
imshow(im1);
hold all;
for i=1:size(m1,2)
    plot(m1(1,i),m1(2,i),'+','MarkerSize',15,'Linewidth',4);
end
subplot(1,2,2);
imshow(im2);
hold all;
for i=1:size(m2,2)
    plot(m2(1,i),m2(2,i),'+','MarkerSize',15,'LineWidth',4);
end

%% Fit a fundamental matrix on all the correspondences

F = eight_points(m2, m1);

%% show result

epiLines = F*m1;
points = lineToBorderPoints(epiLines',size(im2));
% subsample epipolar lines for better visualization
num_lines = 40;
index = [1:num_lines];
figure; imshow(im2);
hold all;
line(points(:,[1,3])',points(:,[2,4])','Color','red');
scatter(m2(1,:),m2(2,:),'filled');
title('Epipolar lines using the estimated F');

%% impose rank constraint
[u,s,v]= svd(F);
s(3,3)=0;
F = u*s*v';

epiLines = F*m1;
points = lineToBorderPoints(epiLines',size(im2));
% subsample epipolar lines for better visualization
num_lines = 40;
index = [1:num_lines];
figure; imshow(im2);
hold all;
line(points(:,[1,3])',points(:,[2,4])','Color','red');
scatter(m2(1,:),m2(2,:),'filled');
title('Epipolar lines using the estimated F');

%% Robust estimation
matchedPoints1=m1(1:2,:)';
matchedPoints2 =m2(1:2,:)';
[fRobust, inliers] =estimateFundamentalMatrix(matchedPoints1,...
    matchedPoints2,'Method','MSAC',...
    'NumTrials',500000,'DistanceThreshold',0.5);
cmap = brewermap(3,'Spectral');


figure;
showMatchedFeatures(im1, im2, matchedPoints1(inliers,:),matchedPoints2(inliers,:),'montage','PlotOptions',{'go','go','g--'});
figure;
showMatchedFeatures(im1, im2, matchedPoints1(~inliers,:),matchedPoints2(~inliers,:),'montage','PlotOptions',{'ro','ro','r--'});
%%
epiLines = fRobust*m1;
points = lineToBorderPoints(epiLines',size(im2));


figure; imshow(im2);
hold all;
line(points(:,[1,3])',points(:,[2,4])','Color','red');
scatter(m2(1,:),m2(2,:),'filled');
title('Epipolar lines using the estimated F');
