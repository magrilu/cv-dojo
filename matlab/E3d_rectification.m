%% Rectification
% Rectification
% .\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.
%
% Image Analysis and Computer Vision
% Politecnico di Milano
%
% Luca Magri
% for comments and suggestions please send an email to luca.magri@polimi.it
%
% .\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.\\°//.
%%
clear;
clc;
close all;
%%
im = imread('Data/giradischi.jpg');
figure;
imshow(im);

a = drawpoint();
b = drawpoint();
c = drawpoint();
d = drawpoint();
%%
m1 = [a.Position;b.Position;c.Position;d.Position];
m1 = [m1'; ones(1,4)];
l = 500;
m2 =[1 l l 1;...
     1 1 l l;...
     1 1 1 1];

%%
[m1_normalized,T1] = precondition(m1);
[m2_normalized,T2] = precondition(m2);
H = dlt_homography(m1,m2);
%H = inv(T2)*H*T1;
H = H./norm(H);
%%
lambda =1;
[mosaic] = image_mosaic_same(im,uint8(zeros(l,l,3)),H,lambda);
figure; imshow(mosaic)