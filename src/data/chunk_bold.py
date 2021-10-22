import os, glob, json
import numpy as np
import pandas as pd
import nibabel as nib
import nilearn
from nilearn.signal import clean
from nilearn.masking import apply_mask, intersect_masks
from nilearn.image import resample_to_img
from load_confounds import Minimal

from scipy.io import loadmat, savemat

dir_path = '/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis'

sub_list = ['sub-01', 'sub-02', 'sub-03']
task_list = ['wedges', 'rings', 'bars']

for sub in sub_list:

    for task in task_list:

        bold = loadmat(os.path.join(dir_path, 'output', 'detrend', sub + '_epi_GMbrain_' + task + '.mat'))[sub + '_' + task]

        num_vox = bold.shape[0]
        chunk_size = 220

        file_path = os.path.join(dir_path, 'output', 'detrend', 'chunks', sub + '_epi_GMbrain_' + task + '_%04d.mat')

        for i in range(int(np.ceil(num_vox/chunk_size))):

            savemat(file_path % i, {'sub' + sub[-2:] + '_' + task: bold[i*chunk_size:(i+1)*chunk_size, :]})


#bold = loadmat(os.path.join(dir_path, 'output', 'detrend', sub + '_epi_GMbrain_' + task + '.mat'))[sub + '_' + task]
#file_path = os.path.join(dir_path, 'output', 'detrend', 'chunks', sub + '_epi_GMbrain_' + task + '_%04d.mat')
#for i in range(int(np.ceil(bold.shape[0]/chunk_size))): savemat(file_path % i, {'sub' + sub[-2:] + '_' + task: bold[i*chunk_size:(i+1)*chunk_size, :]})
