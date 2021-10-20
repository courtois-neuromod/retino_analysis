
% add path to data directory
addpath(genpath('/home/mariestl/cneuromod/retinotopy/vistasoft'));

% https://www.mathworks.com/matlabcentral/answers/454021-how-to-replace-matlabpool-to-parpool
% https://www.mathworks.com/help/parallel-computing/parpool.html;jsessionid=4f2aaebed69057d75b8436992ba1
% TODO: set number of parallel workers

%
%load(join('sub-', subject, '_concatepi_visualareas_wedges.mat'));
%load(join('sub-', subject, '_concatepi_visualareas_rings.mat'));
%load(join('sub-', subject, '_concatepi_visualareas_bars.mat'));

load('sub-01_concatepi_visualareas_wedges.mat');
load('sub-01_concatepi_visualareas_rings.mat');
load('sub-01_concatepi_visualareas_bars.mat');

load('wedges_per_TR_199.mat');
load('rings_per_TR_199.mat');
load('bars_per_TR_199.mat');

stimuli = {wedges, rings, bars};
data = {sub01_visareas_wedges, sub01_visareas_rings, sub01_visareas_wedges};

results = analyzePRF(stimuli,data,1.49,struct('seedmode',[0 1 2],'display','off'));

% save...
save('sub01_visareas_analyzePRF.mat', 'results')
