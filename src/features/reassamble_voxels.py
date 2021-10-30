import os, glob, json
import numpy as np
import pandas as pd
import nibabel as nib
import nilearn
from nilearn.signal import clean
from nilearn.masking import apply_mask, intersect_masks, unmask
from nilearn.image import resample_to_img
from load_confounds import Minimal

from scipy.io import loadmat, savemat

#dir_path = '/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis'
dir_path = '/home/mariestl/cneuromod/retinotopy/analyzePRF'

sub = 'sub-01'
out_list = ['ang', 'ecc', 'expt', 'gain', 'R2', 'rfsize']


mask = nib.load(os.path.join(dir_path, 'masks', sub + '_GMmask.nii.gz'))
mask_dim = mask.get_fdata().shape

num_vox = int(np.sum(mask.get_fdata()))
chunk_size = 220 # see chunk_bold.py script, line 25


for out in out_list:

    flat_output = np.zeros((num_vox,))

    file_path = sorted(glob.glob(os.path.join(dir_path, 'results/sub-01/GM', 'sub' + sub[-2:] + '_GMbrain_analyzePRF_' + out + '_*.mat')))

    for i in range(int(np.ceil(num_vox/chunk_size))):

        flat_output[i*chunk_size:(i+1)*chunk_size] = loadmat(file_path[i])[out].reshape(-1,)

    savemat(os.path.join(dir_path, 'results', sub, 'GM', 'sub' + sub[-2:] + '_GMmask_' + out + '.mat'), {'sub' + sub[-2:] + '_' + out: flat_output})
        #unflat = unmask(flat_output, mask)
        #nib.save(unflat, os.path.join(dir_path, 'output', 'results', sub + '_GMmask_' + out + '.nii.gz'))
