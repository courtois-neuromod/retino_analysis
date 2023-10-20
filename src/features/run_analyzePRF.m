
% <subject> = subject number, e.g. '01', '02', '03'

% setup;

% add path to data directory
addpath(genpath('/home/mariestl/cneuromod/retinotopy/analyzePRF'));

% https://www.mathworks.com/matlabcentral/answers/454021-how-to-replace-matlabpool-to-parpool
% https://www.mathworks.com/help/parallel-computing/parpool.html;jsessionid=4f2aaebed69057d75b8436992ba1
% TODO: set number of parallel workers

p = gcp;
p.NumWorkers

%(ginkgo : 30) et (elm : 40)

%load('wedges_per_TR_199.mat');
%load('rings_per_TR_199.mat');
%load('bars_per_TR_199.mat');

load('wedges_per_TR199_192x192.mat');
load('rings_per_TR199_192x192.mat');
load('bars_per_TR199_192x192.mat');

stimuli = {single(wedges), single(rings), single(bars)};
clear wedges, clear rings, clear bars;

% number of voxels?
% sub-01: 205455 voxels, 0-856 chunks
% sub-02: 221489 voxels, 0-922 chunks
% sub-03: 197945 voxels, 0-824 chunks

num_vox = 197945
chunk_size = 240

% LOOPS ARE INCLUSIVE IN MATLAB!!! includes last number

% elm: 0 to 470
% ginkgo: 471 to 824

for i = 0:floor(num_vox / chunk_size)
    extension = ['_' num2str(i,'%04d') '.mat'];
    load(['sub-03_epi_FULLbrain_wedges' extension]);
    load(['sub-03_epi_FULLbrain_rings' extension]);
    load(['sub-03_epi_FULLbrain_bars' extension]);

    %data = {sub03_wedges, sub03_rings, sub03_bars};
    data = {single(sub03_wedges), single(sub03_rings), single(sub03_bars)};
    clear sub03_wedges, clear sub03_rings, clear sub03_bars;

    results = analyzePRF(stimuli,data,1.49,struct('seedmode',[0 1 2],'display','off'));

    ang = results.ang
    ecc = results.ecc
    expt = results.expt
    rfsize = results.rfsize
    R2 = results.R2
    gain = results.gain

    save(['results/sub-03/fullbrain/sub03_GMbrain_analyzePRF' extension], 'results')
    save(['results/sub-03/fullbrain/sub03_GMbrain_analyzePRF_ang' extension], 'ang')
    save(['results/sub-03/fullbrain/sub03_GMbrain_analyzePRF_ecc' extension], 'ecc')
    save(['results/sub-03/fullbrain/sub03_GMbrain_analyzePRF_expt' extension], 'expt')
    save(['results/sub-03/fullbrain/sub03_GMbrain_analyzePRF_rfsize' extension], 'rfsize')
    save(['results/sub-03/fullbrain/sub03_GMbrain_analyzePRF_R2' extension], 'R2')
    save(['results/sub-03/fullbrain/sub03_GMbrain_analyzePRF_gain' extension], 'gain')

    clear sub*
    clear results
    clear ang, clear ecc, clear expt, clear rfsize, clear R2, clear gain
end

% pipeline output described here:
% https://github.com/cvnlab/analyzePRF/blob/master/analyzePRF.m
