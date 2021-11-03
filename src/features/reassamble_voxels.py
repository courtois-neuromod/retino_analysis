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

r2 = loadmat(os.path.join(dir_path, 'results', sub, 'GM', 'sub' + sub[-2:] + '_GMmask_R2.mat'))['sub' + sub[-2:] + '_R2'].reshape(-1,)
# replacing nan by 0
r2 = np.nan_to_num(r2)
unflat_r2 = unmask(r2, mask)
nib.save(unflat_r2, os.path.join(dir_path, 'output', 'results', sub + '_GMmask_R2.nii.gz'))

rfsize = loadmat(os.path.join(dir_path, 'results', sub, 'GM', 'sub' + sub[-2:] + '_GMmask_rfsize.mat'))['sub' + sub[-2:] + '_rfsize'].reshape(-1,)
# removing np.inf values and replacing w 0
rfsize[rfsize == np.inf] = 0
# thresholding to significant voxels...
rfsize = rfsize*(r2 > 10)
unflat_rfsize = unmask(rfsize, mask)
nib.save(unflat_rfsize, os.path.join(dir_path, 'output', 'results', sub + '_GMmask_rfsize.nii.gz'))

ecc = loadmat(os.path.join(dir_path, 'results', sub, 'GM', 'sub' + sub[-2:] + '_GMmask_ecc.mat'))['sub' + sub[-2:] + '_ecc'].reshape(-1,)
ang = loadmat(os.path.join(dir_path, 'results', sub, 'GM', 'sub' + sub[-2:] + '_GMmask_ang.mat'))['sub' + sub[-2:] + '_ang'].reshape(-1,)
x = np.cos(np.radians(ang))*ecc
y = np.sin(np.radians(ang))*ecc

ecc = ecc*(r2 > 10)
ang = ang*(r2 > 10)
x = x*(r2 > 10)
y = y*(r2 > 10)

unflat_ecc = unmask(ecc, mask)
unflat_ang = unmask(ang, mask)
unflat_x = unmask(x, mask)
unflat_y = unmask(y, mask)

nib.save(unflat_ecc, os.path.join(dir_path, 'output', 'results', sub + '_GMmask_ecc.nii.gz'))
nib.save(unflat_ang, os.path.join(dir_path, 'output', 'results', sub + '_GMmask_ang.nii.gz'))
nib.save(unflat_x, os.path.join(dir_path, 'output', 'results', sub + '_GMmask_x.nii.gz'))
nib.save(unflat_y, os.path.join(dir_path, 'output', 'results', sub + '_GMmask_y.nii.gz'))
