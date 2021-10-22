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
import argparse

parser = argparse.ArgumentParser(description='Train NIF model')
parser.add_argument('--debug', action='store_true', default=False, help='selects fewer voxels from visual cortex')
args = parser.parse_args()

#scan_path = '/lustre03/project/6003287/datasets/cneuromod_processed/fmriprep/retinotopy'
dir_path = '/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis'

#sub-01/ses-001/func/sub-01_ses-001_task-bars_space-T1w_desc-preproc_part-mag_bold.nii.gz
#sub-01/ses-001/func/sub-01_ses-001_task-rings_space-T1w_desc-preproc_part-mag_bold.nii.gz
#sub-01/ses-001/func/sub-01_ses-001_task-wedges_space-T1w_desc-preproc_part-mag_bold.nii.gz

#sub-01_ses-001_task-wedges_space-T1w_desc-brain_part-mag_mask.nii.gz

sub_list = ['sub-01', 'sub-02', 'sub-03']
task_list = ['wedges', 'rings', 'bars']

for sub in sub_list:

    epilist_per_task = []
    confounds_per_task = []
    mask_list = []
    sub_affine = None

    for task in task_list:

        #scan_list = sorted(glob.glob(os.path.join(scan_path, sub, 'ses*/func/sub*' + task + '_space-T1w_desc-preproc_part-mag_bold.nii.gz')))
        scan_list = sorted(glob.glob(os.path.join(dir_path, 'data', 'temp_bold', sub + '*' + task + '_space-T1w_desc-preproc_part-mag_bold.nii.gz')))
        epi_list = []
        conf_list = []

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

            # extract epi's confounds
            #confounds = Minimal(global_signal='basic').load(scan)
            confounds = Minimal(global_signal='basic').load(scan[:-20] + 'bold.nii.gz')

            epi_list.append(epi)
            conf_list.append(confounds)

        epilist_per_task.append(epi_list)
        confounds_per_task.append(conf_list)

    mean_mask = intersect_masks(mask_list, threshold=0.3)


    if args.debug:
        # mask of visual regions adapted from https://scholar.princeton.edu/napl/resources (in MNI space)
        # NOT a great mask for this setting, but gets some voxels in visual cortex
        vis_mask = nib.load(os.path.join(dir_path, 'temp_mask', 'allvisualareas.nii.gz'))
        vis_mask_rs = resample_to_img(vis_mask, mean_mask, interpolation='nearest')
        vis_mask_int = intersect_masks((vis_mask_rs, mean_mask), threshold=1.0)
        mean_mask = vis_mask_int
        nib.save(mean_mask, os.path.join(dir_path, 'output', 'masks', sub + '_visareas_mask.nii.gz'))
    else:
        nib.save(mean_mask, os.path.join(dir_path, 'output', 'masks', sub + '_mean_epi_mask.nii.gz'))

    flatbolds_per_task = []
    for i in range(len(epilist_per_task)):

        epi_list = epilist_per_task[i]

        flatbold_list = []

        for j in range(len(epi_list)):
            epi = epi_list[j]
            flat_bold = apply_mask(imgs=epi, mask_img=mean_mask).T # shape: vox per time

            confounds = confounds_per_task[i][j]

            # Detrend and normalize flattened data
            # note: signal.clean takes (time, vox) shaped input, and flat_bold is (vox, time) (hence the transposing)
            flat_bold_dt = clean(flat_bold.T, detrend=True, standardize='zscore',
                                 standardize_confounds=True, t_r=None, confounds=confounds, ensure_finite=True).T

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

        # provides the data as a cell vector of voxels x time.  can also be X x Y x Z x time
        print(mean_bold.shape)

        flatbolds_per_task.append(mean_bold)

    # Concatenate across tasks
    sub_bold = np.concatenate(flatbolds_per_task, axis=1)

    # export file as either npz or .mat
    if args.debug:
        savemat(os.path.join(dir_path, 'output', 'detrend', sub + '_concatepi_visualareas.mat'), {sub+'_concat_epi': sub_bold})
        savemat(os.path.join(dir_path, 'output', 'detrend', sub + '_concatepi_visualareas_pertask.mat'), {sub+'_concat_epi': flatbolds_per_task})
    else:
        savemat(os.path.join(dir_path, 'output', 'detrend', sub + '_concatepi_fullbrain.mat'), {sub+'_concat_epi': sub_bold})
        savemat(os.path.join(dir_path, 'output', 'detrend', sub + '_concatepi_fullbrain_pertask.mat'), {sub+'_concat_epi': flatbolds_per_task})

# concatenate stimulus files in the same order
stim_list = []

for task in task_list:

    stimuli = loadmat(os.path.join(dir_path, 'stimuli', task + '_per_TR.mat'))[task]
    # TODO: remove first 3 TRs of each task for signal equilibration
    stim_list.append(stimuli[:, :, 3:])

concat_stimuli = np.concatenate(stim_list, axis = -1)
savemat(os.path.join(dir_path, 'stimuli', 'concattasks_per_TR.mat'), {'stimuli': concat_stimuli})
savemat(os.path.join(dir_path, 'stimuli', 'concattasks_per_TR_pertask.mat'), {'stimuli': stim_list})
