import os, glob, json
import numpy as np
import pandas as pd
import nibabel as nib
import nilearn
from nilearn.signal import clean
from nilearn.masking import apply_mask, intersect_masks, unmask
from nilearn.image import resample_to_img
from nilearn.image.image import mean_img, smooth_img
from nilearn.plotting import view_img
from load_confounds import Minimal
from skimage.transform import resize

from scipy.io import loadmat, savemat
import argparse


#scan_path = '/lustre03/project/6003287/datasets/cneuromod_processed/fmriprep/retinotopy'
dir_path = '/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis'

sub_list = ['sub-01', 'sub-02', 'sub-03']
task_list = ['wedges', 'rings', 'bars']

for sub in sub_list:
    '''
    Masks were generated w previous scripts
    - subject-specific GM mask generated with average_bold_GMmask.py
    - subject-specific epi mask generated with average_bold.py
    '''
    mask_GM = nib.load(os.path.join(dir_path, 'output', 'masks', sub + '_GMmask.nii.gz'))
    mask_epi = nib.load(os.path.join(dir_path, 'output', 'masks', sub + '_mean_epi_mask.nii.gz'))
    # VERY inclusive mask: mean epi has dropout in regions of interest, recovered w union with smoothed freesurfer grey matter mask
    sub_mask = intersect_masks([mask_GM, mask_epi], threshold=0.0)
    nib.save(sub_mask, os.path.join(dir_path, 'output', 'masks', sub + '_WholeBrain.nii.gz'))

    sub_affine = None

    for task in task_list:

        #scan_list = sorted(glob.glob(os.path.join(scan_path, sub, 'ses*/func/sub*' + task + '_space-T1w_desc-preproc_part-mag_bold.nii.gz')))
        scan_list = sorted(glob.glob(os.path.join(dir_path, 'data', 'temp_bold', sub + '*' + task + '_space-T1w_desc-preproc_part-mag_bold.nii.gz')))
        flatbold_list = []

        for scan in scan_list:

            if sub_affine is None:
                sub_affine = nib.load(scan).affine

            epi = nib.load(scan)
            assert np.sum(epi.affine == sub_affine) == 16
            print(epi.shape) # (76, 90, 71, 202) = x, y, z, time (TR)

            assert epi.shape[-1] == 202

            #bold_array = epi.get_fdata()
            flat_bold = apply_mask(imgs=epi, mask_img=sub_mask) # shape: (time, vox)

            '''
            Code to unmask: return flattened data into brain space for visualization, analyses
            Source code: https://github.com/nilearn/nilearn/blob/1607b52458c28953a87bbe6f42448b7b4e30a72f/nilearn/masking.py#L900
            Returns .nii object

            deflat_bold = unmask(flat_bold_dt[:, 3:], sub_mask)
            '''

            # extract epi's confounds
            #confounds = Minimal(global_signal='basic').load(scan)
            confounds = Minimal(global_signal='basic').load(scan[:-20] + 'bold.nii.gz')

            # Detrend and normalize flattened data
            # note: signal.clean takes (time, vox) shaped input
            flat_bold_dt = clean(flat_bold, detrend=True, standardize='zscore',
                                 standardize_confounds=True, t_r=None, confounds=confounds, ensure_finite=True).T # shape: vox per time

            # Remove first 3 volumes of each run
            flatbold_list.append(flat_bold_dt[:, 3:])

        # sanity checks performed
        # for each subject in T1w space, affine matrices are the same for scans and masks across sessions and tasks

        # the number of TRs per scan matches the number of "TRs" from the stimulus files (202)

        # visualization w nilearn and with matplotlib
            # matrices without affine (exported as numpy) overlap in the same space)
            # masks and images fit well
            # note however that masks are aligned (same affine), BUT don't have same number of voxels...

        mean_bold = np.mean(np.array(flatbold_list), axis=0) # shape: voxel per time

        # provides the data as a cell vector of voxels x time. For K.Kay's toolbox, it can also be X x Y x Z x time
        print(mean_bold.shape)
        savemat(os.path.join(dir_path, 'output', 'detrend', sub + '_epi_FULLbrain_' + task + '.mat'), {sub + '_' + task : mean_bold})

# resize stimuli produced with nake_stimuli.py from 768x768 to 192x192 to speed up processing
'''
target_dim = (192, 192)

for task in task_list:
    # remove first 3 TRs of each task for signal equilibration
    stimuli = loadmat(os.path.join(dir_path, 'stimuli', task + '_per_TR.mat'))[task][:, :, 3:]

    resized_stim = np.zeros([192, 192, stimuli.shape[2]])

    for i in range(stimuli.shape[2]):
        frame = stimuli[:, :, i]
        resized_stim[:, :, i] = resize(frame, target_dim, preserve_range=True, anti_aliasing=True)

    savemat(os.path.join(dir_path, 'stimuli', task + '_per_TR199_192x192.mat'), {task: resized_stim.astype('f4')})
'''
