
# workon retino_analysis #virtual env...
import os, sys
import subprocess

import nibabel as nib
import numpy as np
from nilearn.image import load_img, new_img_like, index_img, resample_to_img
from nilearn.masking import intersect_masks, apply_mask, unmask
from scipy.stats import zscore
from tqdm import tqdm

import argparse


def get_arguments():

    parser = argparse.ArgumentParser(description='Resamples neuropythy output to T1w space')
    parser.add_argument('--sub_num', required=True, type=str, help='subject number e.g., sub-01')
    parser.add_argument('--dir_path', default=None, type=str, help='path to run dir (absolute)')
    args = parser.parse_args()

    return args


def export_map(roival, va, va_img, ref_img, result_dir):
    '''
    Create binary mask whose voxels correspond to ROI's label (roival)
    0: No visual area
    1: V1
    2: V2
    3: V3
    4: hV4
    5: VO1
    6: VO2
    7: LO1
    8: LO2
    9: TO1
    10: TO2
    11: V3b
    12: V3a
    '''
    roi_arr = np.zeros(va.shape)
    roi_arr[np.where(va == roival)] = 1.
    roi_img = new_img_like(va_img, roi_arr)
    # export nearest extrapolation (preferred for binary mask)
    res_img = resample_to_img(roi_img, ref_img, interpolation='nearest')
    res_img.to_filename(os.path.join(result_dir, f'resampled_va-{roival}_interp-nn.nii.gz'))
    # also save linear interpolation for convenience
    lres_img = resample_to_img(roi_img, ref_img, interpolation='linear')
    lres_img.to_filename(os.path.join(result_dir, f'resampled_va-{roival}_interp-linear.nii.gz'))


if __name__ == '__main__':
    '''
    Script resamples neuropythy binary visual ROIs back into T1w functional space
    '''
    args = get_arguments()

    # On Beluga
    dir_path = '/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis' if args.dir_path is None else args.dir_path

    sub = args.sub_num # e.g., sub-03
    result_dir = os.path.join(dir_path, 'results/npythy', sub)

    # resample binary visual ROIs to functional space
    ref_file = sub + '_ses-005_task-bars_space-T1w_desc-preproc_part-mag_bold.nii.gz'
    ref_f = os.path.join(dir_path, 'data/temp_bold', ref_file)
    ref_img = index_img(ref_f, 0)

    va_img = load_img(os.path.join(result_dir, 'inferred_varea.nii.gz'))
    va = va_img.get_fdata()

    for roival in range(1, 13):
        export_map(roival, va, va_img, ref_img, result_dir)

    # resample and save all other neuropythy outputs 
    for param in ['angle', 'eccen', 'sigma', 'varea']:
        interp = 'nearest' if param == 'varea' else 'linear'
        res_img = resample_to_img(os.path.join(result_dir, f'inferred_{param}.nii.gz'), ref_img, interpolation=interp)
        res_img.to_filename(os.path.join(result_dir, f'resampled_{param}.nii.gz'))


'''
roival=12
roi_arr = np.zeros(va.shape)
roi_arr[np.where(va == roival)] = 1.
roi_img = new_img_like(va_img, roi_arr)
res_img = resample_to_img(roi_img, ref_img, interpolation='nearest')
res_img.to_filename(os.path.join(result_dir, f'resampled_va-{roival}_interp-nn.nii.gz'))
# also save linear interpolation for convenience
lres_img = resample_to_img(roi_img, ref_img, interpolation='linear')
lres_img.to_filename(os.path.join(result_dir, f'resampled_va-{roival}_interp-linear.nii.gz'))


interp = 'nearest' if param == 'varea' else 'linear'
res_img = resample_to_img(os.path.join(result_dir, f'inferred_{param}.nii.gz'), ref_img, interpolation=interp)
res_img.to_filename(os.path.join(result_dir, f'resampled_{param}.nii.gz'))
'''
