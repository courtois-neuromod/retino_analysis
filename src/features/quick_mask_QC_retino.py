import glob, os, json

import nibabel as nib
from nilearn.masking import unmask, apply_mask, intersect_masks
import numpy as np
import pandas as pd
from scipy.stats import zscore
from nilearn.image import resample_to_img
from nilearn.image.image import mean_img, smooth_img

from scipy.io import loadmat, savemat

import h5py
from tqdm import tqdm


'''
QCing signal across runs for retino dataset
'''

sub_list = ['01', '02', '03']
suffix = '_space-T1w_desc-preproc_part-mag_bold.nii.gz'
mask_suffix = '_space-T1w_desc-brain_part-mag_mask.nii.gz'
data_path = '/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/data/temp_bold'

for sub_num in sub_list:
    '''
    If they don't already exist, create a mask that includes all voxels with at least one normalized nan score (no signal)
    and another mask that excludes all voxels with at least one nan score within the broader functional brain mask
    '''
    mask_path = f'/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/output/masks/sub-{sub_num}_WholeBrain.nii.gz'
    mask = nib.load(mask_path)

    npath = f'/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/output/masks/{sub_num}_nanmask_T1w_retino.nii'
    nnpath = f'/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/output/masks/{sub_num}_goodvoxmask_T1w_retino.nii'

    if os.path.exists(npath) and os.path.exists(nnpath):
        global_nan_mask = nib.load(npath)
        global_goodval_mask = nib.load(nnpath)

    else:
        bold_files = sorted(glob.glob(os.path.join(data_path, f'sub-{sub_num}*{suffix}')))

        nan_masks = []
        notnan_masks = []
        nan_in_globalmask = []
        nan_in_runmask = []

        for i in tqdm(range(len(bold_files)), desc='processing bold files'):
            #nan_masks.append(unmask(np.isnan(np.mean(zscore(apply_mask(nib.load(bold_files[i]), mask, dtype=np.single)), axis=0)), mask))
            meanz_vals = np.mean(zscore(apply_mask(nib.load(bold_files[i]), mask, dtype=np.single)), axis=0)
            nan_masks.append(unmask(np.isnan(meanz_vals), mask))
            notnan_masks.append(unmask(~np.isnan(meanz_vals), mask))
            nan_in_globalmask.append(unmask(np.isnan(meanz_vals), mask).get_fdata())

            run_mask = nib.load(glob.glob(os.path.join(bold_files[i][:-28] + '*mask.nii.gz'))[0])
            meanz_val_run = np.mean(zscore(apply_mask(nib.load(bold_files[i]), run_mask, dtype=np.single)), axis=0)
            nan_in_runmask.append(unmask(np.isnan(meanz_val_run), run_mask).get_fdata())

        global_nan_mask = intersect_masks(nan_masks, threshold=0, connected=False)
        global_goodval_mask = intersect_masks(notnan_masks, threshold=1, connected=False)

        # check that all voxels are within functional mask
        assert np.sum(mask.get_fdata() * global_goodval_mask.get_fdata()) == np.sum(global_goodval_mask.get_fdata())
        assert np.sum(mask.get_fdata() * global_nan_mask.get_fdata()) == np.sum(global_nan_mask.get_fdata())

        print(np.sum(global_nan_mask.get_fdata()))
        print(np.sum(global_goodval_mask.get_fdata()))

        for m in nan_masks:
            print(np.sum(m.get_fdata()))

        nib.save(global_nan_mask, npath)
        nib.save(global_goodval_mask, nnpath)

        nan_masks_glob = np.sum(np.stack(nan_in_globalmask, axis=-1), axis=-1)
        nan_masks_glob = nib.nifti1.Nifti1Image(nan_masks_glob, affine=mask.affine)
        nib.save(nan_masks_glob, f'/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/output/masks/QC_nan_in_global_sub-{sub_num}_outof_{str(len(bold_files))}_retino.nii.gz')

        nan_masks_run = np.sum(np.stack(nan_in_runmask, axis=-1), axis=-1)
        nan_masks_run = nib.nifti1.Nifti1Image(nan_masks_run, affine=mask.affine)
        nib.save(nan_masks_run, f'/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/output/masks/QC_nan_in_runmask_sub-{sub_num}_outof_{str(len(bold_files))}_retino.nii.gz')


        mask_files = sorted(glob.glob(os.path.join(data_path, f'sub-{sub_num}*{mask_suffix}')))

        masks_per_run = []
        for m in mask_files:
            masks_per_run.append(nib.load(m).get_fdata())

        mask_sum = len(mask_files) - np.sum(np.stack(masks_per_run, axis=-1), axis=-1)
        mask_sum = nib.nifti1.Nifti1Image(mask_sum, affine=mask.affine)
        mask_sum = unmask(apply_mask(mask_sum, mask), mask)
        nib.save(mask_sum, f'/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/output/masks/QC_acrossruns_maskvar_sub-{sub_num}_outof_{str(len(bold_files))}_retino.nii.gz')
