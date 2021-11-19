import os
import numpy as np
import nibabel as nib
from scipy.io import loadmat, savemat
import argparse


def get_arguments():

    parser = argparse.ArgumentParser(description='Create subject-specific masks of visual cortex ROIs')
    parser.add_argument('--sub_num', required=True, type=str, help='subject number e.g., sub-01')
    parser.add_argument('--dir_path', default=None, type=str, help='path to run dir (absolute)')
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    '''
    Script creates subject-specific ROI masks from visual cortical areas in T1w space
    based on retinotopy data (analyzePRF and neuropythy toolboxes)
    '''
    args = get_arguments()

    # Beluga
    dir_path = '/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis' if args.dir_path is None else args.dir_path
    # Elm
    #dir_path = '/home/mariestl/cneuromod/retinotopy/retino_analysis' if args.dir_path is None else args.dir_path
    sub = args.sub_num # e.g., sub-03
    in_path = os.path.join(dir_path, 'results', 'npythy', sub, )
    out_path = os.path.join(dir_path, 'results', 'roi_masks')

    roi_list = [('1', 'V1'), ('2', 'V2'), ('3', 'V3'), ('4', 'hV4'), ('5', 'VO1'), ('6', 'VO2'), ('7', 'LO1'), ('8', 'LO2'), ('9', 'TO1'), ('10', 'TO2'), ('11', 'V3b'), ('12', 'V3a')]
    roi_masks = {}

    for roi in roi_list:
        mask = nib.load(os.path.join(in_path, 'resampled_va-'+ str(roi[0]) + '_interp-nn.nii.gz'))
        mask_data = mask.get_fdata().astype(int) # .astype(bool)
        # check that mask is binary
        assert np.sum(mask_data==0) + np.sum(mask_data==1) == mask_data.size
        print(sub, roi[1], 'Number of voxels: ', np.sum(mask_data))
        roi_masks[roi[1]] = mask_data

    savemat(os.path.join(out_path, 'roimasks_s' + sub[-2:] + '_T1w.mat'), roi_masks)
