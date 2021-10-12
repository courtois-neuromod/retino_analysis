import os, glob, json
import numpy as np
import pandas as pd
import nibabel as nib
import nilearn
from nilearn.masking import apply_mask, intersect_masks

from scipy.io import loadmat, savemat

scan_path = '/lustre03/project/6003287/datasets/cneuromod_processed/fmriprep/retinotopy'

#sub-01/ses-001/func/sub-01_ses-001_task-bars_space-T1w_desc-preproc_part-mag_bold.nii.gz
#sub-01/ses-001/func/sub-01_ses-001_task-rings_space-T1w_desc-preproc_part-mag_bold.nii.gz
#sub-01/ses-001/func/sub-01_ses-001_task-wedges_space-T1w_desc-preproc_part-mag_bold.nii.gz

#sub-01_ses-001_task-wedges_space-T1w_desc-brain_part-mag_mask.nii.gz

sub_list = ['sub-01', 'sub-02', 'sub-03']
task_list = ['wedges', 'rings', 'bars']

for sub in sub_list:
    for task in task_list:

        scan_list = sorted(glob.glob(os.path.join(scan_path, sub, 'ses*/func/sub*' + task + '_space-T1w_desc-preproc_part-mag_bold.nii.gz')))

        bold_list = []
        mask_list = []

        for scan in scan_list:
            mask = nib.load(glob.glob(scan[:-28] + 'brain_part-mag_mask.nii.gz')[0])#.get_fdata().astype(int) # (76, 90, 71) = x, y, z
            mask_list.append(mask)

        mean_mask = intersect_masks(mask_list, threshold=0.3)

        for scan in scan_list:
            epi = nib.load(scan)
            print(epi.shape) # (76, 90, 71, 202) = x, y, z, time (TR)

            #bold_array = epi.get_fdata()
            #mask = nib.load(glob.glob(scan[:-28] + 'brain_part-mag_mask.nii.gz')[0])#.get_fdata().astype(int) # (76, 90, 71) = x, y, z
            #flat_bold = apply_mask(imgs=epi, mask_img=nib.load(glob.glob(scan[:-28] + 'brain_part-mag_mask.nii.gz')[0])).T # shape: vox per time
            flat_bold = apply_mask(imgs=epi, mask_img=mean_mask).T # shape: vox per

            bold_list.append(flat_bold)

        # sanity checks
        # all affine matrices the same for scans and masks across sessions and tasks
        # visualized w nilearn and with matplotlib (matrices without affine overlap in same space): masks and images fit well

        # plot twist: masks are aligned (same affine), BUT don't have same number of voxels...
        mean_bold = np.mean(np.array(bold_list), axis=0) # shape: voxel per time

        # provides the data as a cell vector of voxels x time.  can also be X x Y x Z x time
        print(mean_bold.shape)



# Steps:
# average signal across 5-6 sessions
# concatenate averaged signal across tasks

# concatenate stimulus files in the same order

# Niftimasker: flatten
# find subject-specific mask, visualize it
