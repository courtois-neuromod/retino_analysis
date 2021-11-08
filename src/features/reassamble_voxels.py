import os, glob, json
import numpy as np
import pandas as pd
import nibabel as nib
from nilearn.masking import unmask

from scipy.io import loadmat, savemat

#dir_path = '/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis'
dir_path = '/home/mariestl/cneuromod/retinotopy/analyzePRF'

sub = 'sub-01'
out_list = ['ang', 'ecc', 'expt', 'gain', 'R2', 'rfsize']


mask = nib.load(os.path.join(dir_path, 'masks', sub + '_GMmask.nii.gz'))
mask_dim = mask.get_fdata().shape

num_vox = int(np.sum(mask.get_fdata()))
chunk_size = 240 # see chunk_bold.py script, line 25


for out in out_list:

    flat_output = np.zeros((num_vox,))

    file_path = sorted(glob.glob(os.path.join(dir_path, 'results/sub-03/fullbrain', 'sub' + sub[-2:] + '_GMbrain_analyzePRF_' + out + '_*.mat')))

    for i in range(int(np.ceil(num_vox/chunk_size))):

        flat_output[i*chunk_size:(i+1)*chunk_size] = loadmat(file_path[i])[out].reshape(-1,)

    savemat(os.path.join(dir_path, 'results', sub, 'fullbrain', 'sub' + sub[-2:] + '_fullbrain_' + out + '.mat'), {'sub' + sub[-2:] + '_' + out: flat_output})
        #unflat = unmask(flat_output, mask)
        #nib.save(unflat, os.path.join(dir_path, 'output', 'results', sub + '_GMmask_' + out + '.nii.gz'))

# analysePRF doc (Kendrick Kay)
# https://github.com/cvnlab/analyzePRF/blob/master/analyzePRF.m

# Neuropythy usage doc:
# https://osf.io/knb5g/wiki/Usage/

# Variance explained must be a fraction between v such that 0 ≤ v ≤ 1.
r2 = loadmat(os.path.join(dir_path, 'results', sub, 'GM', 'sub' + sub[-2:] + '_GMmask_R2.mat'))['sub' + sub[-2:] + '_R2'].reshape(-1,)
# replacing nan by 0
r2 = np.nan_to_num(r2)/100 # convert percentage
# Cap between 0 and 1; The R2 values are computed after projecting out polynomials
# from both the data and the model fit. Because of this projection, values can sometimes drop below 0%
r2[r2 < 0.0] = 0.0
r2[r2 > 1.0] = 1.0
unflat_r2 = unmask(r2, mask)
nib.save(unflat_r2, os.path.join(dir_path, 'output', 'results', sub + '_GMmask_R2.nii.gz'))

'''
Convert rfsize from pixel to degrees of visual angle
The rescaled stimulus is 192x192 pixels for 10 degrees of visual angle (width).
To convert from pixels to degreees, multiply by 10/192.
'''
conv_factor = 10/192

# Sigma/pRF size must be degrees of the visual field (outputed in pixels with 0 lower bound by K Kay's toolbox)
# stimulus images were rescaled from 768x768 to 192x192, 10 deg of visual angle (width of stimuli)
rfsize = loadmat(os.path.join(dir_path, 'results', sub, 'GM', 'sub' + sub[-2:] + '_GMmask_rfsize.mat'))['sub' + sub[-2:] + '_rfsize'].reshape(-1,)
# removing np.inf values and replacing w max finite value
rfs_max = np.max(rfsize[np.isfinite(rfsize)])
rfsize[rfsize == np.inf] = rfs_max
# thresholding to significant voxels... (only for visualization)
# rfsize = rfsize*(r2 > 0.1)
'''
With gaussian mmodel, rfsize is sigma; KK's model is slightly different
In KK's: rfsize = sigma/sqrt(n) where n is the exponent of the power law function
expt contains pRF exponent estimates (is that n???).
Similar to the original model (2D isotropic Gaussian), except that a
static power-law nonlinearity is added after summation across the visual field

# Recover sigma from size? (Not NEEDED)
From paper: https://journals.physiology.org/doi/full/10.1152/jn.00105.2013
"For a model for which the predicted response to point stimuli does not have a
Gaussian profile, we could simply stipulate that pRF size is the standard
deviation of a Gaussian function fitted to the actual profile."

expt = loadmat(os.path.join(dir_path, 'results', sub, 'GM', 'sub' + sub[-2:] + '_GMmask_expt.mat'))['sub' + sub[-2:] + '_expt'].reshape(-1,)
sigma = rfsize*np.sqrt(expt)
'''
rfsize = rfsize*conv_factor
unflat_rfsize = unmask(rfsize, mask)
nib.save(unflat_rfsize, os.path.join(dir_path, 'output', 'results', sub + '_GMmask_rfsize.nii.gz'))


# Values are in pixel units with a lower bound of 0 pixels. Must be in degrees of visual angle from the fovea.
ecc = loadmat(os.path.join(dir_path, 'results', sub, 'GM', 'sub' + sub[-2:] + '_GMmask_ecc.mat'))['sub' + sub[-2:] + '_ecc'].reshape(-1,)
# Values range between 0 and 360 degrees.
# 0 corresponds to the right horizontal meridian, 90 corresponds to the upper vertical meridian, and so on.
# In the case where <ecc> is estimated to be exactly equal to 0,
# the corresponding <ang> value is deliberately set to NaN.
ang = loadmat(os.path.join(dir_path, 'results', sub, 'GM', 'sub' + sub[-2:] + '_GMmask_ang.mat'))['sub' + sub[-2:] + '_ang'].reshape(-1,)
x = np.cos(np.radians(ang))*ecc
y = np.sin(np.radians(ang))*ecc

# convert to visual angles
ecc *= conv_factor
x *= conv_factor
y *= conv_factor

# converts angles from "compass" to "signed north-south" for neuropythy
ang[np.logical_not(ang > 270)] = 90 - ang[np.logical_not(ang > 270)]
ang[ang > 270] = 450 - ang[ang > 270]

# From readme: angle values must be absolute for neurpythy (Doc is not up to date in Usage manual)
# https://github.com/noahbenson/neuropythy/issues?q=is%3Aissue+is%3Aclosed
ang = np.absolute(ang)

# threshold for visualization
#ecc = ecc*(r2 > 0.1)
#ang = ang*(r2 > 0.1)
#x = x*(r2 > 0.1)
#y = y*(r2 > 0.1)

unflat_ecc = unmask(ecc, mask)
unflat_ang = unmask(ang, mask)
unflat_x = unmask(x, mask)
unflat_y = unmask(y, mask)

nib.save(unflat_ecc, os.path.join(dir_path, 'output', 'results', sub + '_GMmask_ecc.nii.gz'))
nib.save(unflat_ang, os.path.join(dir_path, 'output', 'results', sub + '_GMmask_ang.nii.gz'))
nib.save(unflat_x, os.path.join(dir_path, 'output', 'results', sub + '_GMmask_x.nii.gz'))
nib.save(unflat_y, os.path.join(dir_path, 'output', 'results', sub + '_GMmask_y.nii.gz'))



'''
bbbbbbbbb
'''

dir_path = '/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis'
sub = 'sub-03'
mask = nib.load(os.path.join(dir_path, 'output', 'masks', sub + '_WholeBrain.nii.gz'))

r2 = loadmat(os.path.join(dir_path, 'results', 'sub' + sub[-2:] + '_fullbrain_R2.mat'))['sub' + sub[-2:] + '_R2'].reshape(-1,)
r2 = np.nan_to_num(r2)/100 # convert percentage
r2[r2 < 0.0] = 0.0
r2[r2 > 1.0] = 1.0
unflat_r2 = unmask(r2, mask)
nib.save(unflat_r2, os.path.join(dir_path, 'results', sub + '_fullbrain_R2.nii.gz'))

conv_factor = 10/192

rfsize = loadmat(os.path.join(dir_path, 'results', 'sub' + sub[-2:] + '_fullbrain_rfsize.mat'))['sub' + sub[-2:] + '_rfsize'].reshape(-1,)
rfs_max = np.max(rfsize[np.isfinite(rfsize)])
rfsize[rfsize == np.inf] = rfs_max

rfsize = rfsize*conv_factor
unflat_rfsize = unmask(rfsize, mask)
nib.save(unflat_rfsize, os.path.join(dir_path, 'results', sub + '_fullbrain_rfsize.nii.gz'))


ecc = loadmat(os.path.join(dir_path, 'results', 'sub' + sub[-2:] + '_fullbrain_ecc.mat'))['sub' + sub[-2:] + '_ecc'].reshape(-1,)
ang = loadmat(os.path.join(dir_path, 'results', 'sub' + sub[-2:] + '_fullbrain_ang.mat'))['sub' + sub[-2:] + '_ang'].reshape(-1,)
x = np.cos(np.radians(ang))*ecc
y = np.sin(np.radians(ang))*ecc

ecc *= conv_factor
x *= conv_factor
y *= conv_factor

ang[np.logical_not(ang > 270)] = 90 - ang[np.logical_not(ang > 270)]
ang[ang > 270] = 450 - ang[ang > 270]

ang = np.absolute(ang)

unflat_ecc = unmask(ecc, mask)
unflat_ang = unmask(ang, mask)
unflat_x = unmask(x, mask)
unflat_y = unmask(y, mask)

nib.save(unflat_ecc, os.path.join(dir_path, 'results', sub + '_fullbrain_ecc.nii.gz'))
nib.save(unflat_ang, os.path.join(dir_path, 'results', sub + '_fullbrain_ang.nii.gz'))
nib.save(unflat_x, os.path.join(dir_path, 'results', sub + '_fullbrain_x.nii.gz'))
nib.save(unflat_y, os.path.join(dir_path, 'results', sub + '_fullbrain_y.nii.gz'))
