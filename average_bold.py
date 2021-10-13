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

    epilist_per_task = []
    mask_list = []
    sub_affine = None

    for task in task_list:

        scan_list = sorted(glob.glob(os.path.join(scan_path, sub, 'ses*/func/sub*' + task + '_space-T1w_desc-preproc_part-mag_bold.nii.gz')))
        epi_list = []

        for scan in scan_list:

            if sub_affine is None:
                sub_affine = nib.load(scan).affine

            mask = nib.load(glob.glob(scan[:-28] + 'brain_part-mag_mask.nii.gz')[0])#.get_fdata().astype(int) # (76, 90, 71) = x, y, z
            assert np.sum(mask.affine == sub_affine) == 16
            mask_list.append(mask)

            epi = nib.load(scan)
            assert np.sum(epi.affine == sub_affine) == 16
            print(epi.shape) # (76, 90, 71, 202) = x, y, z, time (TR)

            assert epi.shape[-1] == 202
            #bold_array = epi.get_fdata()
            epi_list.append(epi)

        epilist_per_task.append(epi_list)

    mean_mask = intersect_masks(mask_list, threshold=0.3)

    flatbolds_per_task = []
    for epi_list in epilist_per_task:

        flatbold_list = []
        for epi in epi_list:
            flat_bold = apply_mask(imgs=epi, mask_img=mean_mask).T # shape: vox per

            flatbold_list.append(flat_bold)

        # sanity checks performed
        # for each subject in T1w space, affine matrices are the same for scans and masks across sessions and tasks

        # the number of TRs per scan matches the number of "TRs" from the stimulus files (202)

        # visualization w nilearn and with matplotlib
            # matrices without affine (exported as numpy) overlap in the same space)
            # masks and images fit well
            # note however that masks are aligned (same affine), BUT don't have same number of voxels...

        mean_bold = np.mean(np.array(flatbold_list), axis=0) # shape: voxel per time

        # provides the data as a cell vector of voxels x time.  can also be X x Y x Z x time
        print(mean_bold.shape)

        flatbolds_per_task.append(mean_bold)

    # Concatenate across tasks
    sub_bold = np.concatenate(flatbolds_per_task, axis=1)

    # export file as either npz or .mat
    savemat('output/' + sub + '_concatepi.mat', {sub+'_concat_epi': sub_bold})

# concatenate stimulus files in the same order
stim_list = []

for task in task_list:

    stimuli = loadmat(os.path.join('stimuli', task + '_per_TR.mat'))[task]
    stim_list.append(stimuli)

concat_stimuli = np.contat(stim_list, axis = -1)
savemat('stimuli/concattasks_per_TR.mat', {'stimuli': concat_stimuli})
