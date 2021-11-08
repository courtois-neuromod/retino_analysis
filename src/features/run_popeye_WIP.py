import os
import ctypes, multiprocessing
import numpy as np
import popeye.og as og
import popeye.utilities as utils
from popeye.visual_stimulus import VisualStimulus, simulate_bar_stimulus
from scipy.io import loadmat, savemat


sub_list = ['sub-01', 'sub-02', 'sub-03']
sub = sub_list[0]

task_list = ['wedges', 'rings', 'bars']

dir_path = '/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis'

'''
Stimuli (h, w, frame)
Frame = same resolution as bold (one frame per TR)

Question: does it take floats, or just int? (demo dtype is numpy.int16)
'''

stim_list = []
for task in task_list:
    stimuli = loadmat(os.path.join(dir_path, 'stimuli', task + '_per_TR.mat'))[task]
    # Remove first 3 TRs of each task for signal equilibration
    stim_list.append(stimuli[:, :, 3:])

# make binary
stimuli = np.rint(np.concatenate(stim_list, axis = -1)).astype('int16')

'''
PROBLEM: all stimulus coordinates seem cartesian, in demo, code, etc, (x, y)... convert stimuli??
# Kendrick Kay's stimuli are in (R, C, frame) format (and so are the masks I exported w make_stimuli + average_bold)
# But popeyes requires stimuli in (X, Y, frame) (cartesian)
# dim = (r, c, frame) -> dim = (x, y, frame)
'''
# DON'T DO THAT
#stimuli = np.flip(np.transpose(stimuli, (1, 0, 2)), axis=1)



'''create an instance of the Stimulus class
https://github.com/kdesimone/popeye/blob/feafa42569acb506c9983d1f1abc01ea2714d3be/popeye/visual_stimulus.py#L387
#stimulus = VisualStimulus(stim_arr=bar, viewing_distance=50, screen_width=25, scale_factor=0.25, tr_length=1.0,
                           dtype=ctypes.c_int16, interp='nearest')

        stim_arr : ndarray
            An array containing the visual stimulus at the native resolution. The
            visual stimulus is assumed to be three-dimensional (x,y,time).

        viewing_distance : float
            The distance between the participant and the display (cm).

        screen_width : float
            The width of the display (cm). This is used to compute the visual angle
            for determining the pixels per degree of visual angle.

        scale_factor : float
            The downsampling rate for ball=parking a solution. The `stim_arr` is
            downsampled so as to speed up the fitting procedure.  The final model
            estimates will be derived using the non-downsampled stimulus.
'''

# distance = 180 cm
# degrees (retino) = 10 deg (width); 17.5 deg width is full screen
# width = 55cm (full screen)
# width of grid shown during retino = 55*(10/17.5) = 31.428571428571427 cm

# Retino: 10 deg width, so 768/10 = 76.8 pixels/deg
#np.pi*768/np.arctan(31.43/180/2.0)/360.0 = 76.96025874884585

#def pixels_per_degree(pixels_across, screen_width, viewing_distance):
#    return np.pi*pixels_across/np.arctan(screen_width/viewing_distance/2.0)/360.0

stimulus = VisualStimulus(stimuli, viewing_distance=180, screen_width=31.43, scale_factor=0.25,
                          tr_length=1.49, dtype=ctypes.c_int16)

'''
MODEL
define search grids
'''
model = og.GaussianModel(stimulus, utils.double_gamma_hrf)

'''
FIT
define search grids
these define min and max of the edge of the initial brute-force search.
'''
x_grid = (-10,10) # position in x in degrees or pixels?
y_grid = (-10,10) # position in y in degrees or pixels?
s_grid = (1/stimulus.ppd + 0.25,5.25) #(0.25,5.25) # sigma

grids = (x_grid, y_grid, s_grid)
'''
define search bounds
these define the boundaries of the final gradient-descent search.
'''
x_bound = (-12.0,12.0)
y_bound = (-12.0,12.0)
s_bound = (1/stimulus.ppd, 12.0) # (0.001,12.0)
h_bound = (-3.0,3.0) #??
b_bound = (1e-8,None) #(1e-8,1e2) # beta

bounds = (x_bound, y_bound, s_bound, h_bound, b_bound)

'''
fit the response
auto_fit = True fits the model on assignment
verbose = 0 is silent
verbose = 1 is a single print
verbose = 2 is very verbose

data : ndarray
    An array containing the measured BOLD signal of a SINGLE VOXEL.
'''
# TODO: informed choice??!
#hrf_delay = -0.25
hrf_delay = -0.50
#hrf_delay = -3.0
model.hrf_delay = hrf_delay

# dim = (voxel, frame)
#data = loadmat(os.path.join(dir_path, 'output', 'detrend', sub + '_concatepi_fullbrain.mat'))[sub + '_concat_epi']
data = loadmat(os.path.join(dir_path, 'output', 'detrend', sub + '_concatepi_visualareas.mat'))[sub + '_concat_epi']

# NOTE: values are NOT normalized in demo... rescale?
# range of data in demo is -928 to 1591, range of normalized (z-scored) data is --1.98 to 2.22
data *= 600

fit_list = []
for datum in data:
    fit = og.GaussianFit(model, datum, grids, bounds, Ns=3, auto_fit=True, verbose=2)
    fit_list.append(fit)
    #TODO: add variables of interest to input file, in order of voxels, so can project back into brain space


# ballpark, estimate, overloaded_estimate
# to print all attributes of fitted output class:
fit.__dict__.keys()

fit.rsquared
fit.sigma
fit.beta
fit.x
fit.y

fit.overloaded_estimate
fit.msg
