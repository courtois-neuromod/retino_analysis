
# workon retino_analysis #virtual env...

import os, sys
import subprocess

import nibabel as nib
import numpy as np
from nilearn.image import load_img, new_img_like, index_img, resample_to_img
from nilearn.masking import intersect_masks, apply_mask, unmask
#from nipype.interfaces.fsl.maths import TemporalFilter
#from nipype.pipeline.engine import MapNode
from scipy.stats import zscore
from tqdm import tqdm


#TODO: adapt Oli's code here
result_dir = '/project/rrg-pbellec/mstlaure/retino_analysis/results/npythy/sub-03'

# resample binary visual ROIs to functional space
refscan_dir = '/project/rrg-pbellec/mstlaure/retino_analysis/data/temp_bold'
ref_file = 'sub-03_ses-005_task-bars_space-T1w_desc-preproc_part-mag_bold.nii.gz'
ref_f = os.path.join(refscan_dir, ref_file)
ref_img = index_img(ref_f, 0)

va_img = load_img(os.path.join(result_dir, 'inferred_varea.nii.gz'))
va = va_img.get_fdata()

for roival in range(1, 13):
    roi_arr = np.zeros(va.shape)
    roi_arr[np.where(va == roival)] = 1.
    roi_img = new_img_like(va_img, roi_arr)
    res_img = resample_to_img(roi_img, ref_img, interpolation='nearest')
    res_img.to_filename(os.path.join(result_dir, f'resampled_va-{roival}_interp-nn.nii.gz'))
    # also save linear interpolation for convenience
    lres_img = resample_to_img(roi_img, ref_img, interpolation='linear')
    lres_img.to_filename(os.path.join(result_dir, f'resampled_va-{roival}_interp-linear.nii.gz'))

# resample all other outputs too
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
