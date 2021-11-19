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

    Voxels per ROI from FullBrain retino analysis (no slice-time):
    sub-01 V1 Number of voxels:  1918
    sub-01 V2 Number of voxels:  1441
    sub-01 V3 Number of voxels:  1072
    sub-01 hV4 Number of voxels:  766
    sub-01 VO1 Number of voxels:  289
    sub-01 VO2 Number of voxels:  216
    sub-01 LO1 Number of voxels:  314
    sub-01 LO2 Number of voxels:  304
    sub-01 TO1 Number of voxels:  288
    sub-01 TO2 Number of voxels:  304
    sub-01 V3b Number of voxels:  209
    sub-01 V3a Number of voxels:  639

    sub-02 V1 Number of voxels:  1778
    sub-02 V2 Number of voxels:  1431
    sub-02 V3 Number of voxels:  1369
    sub-02 hV4 Number of voxels:  769
    sub-02 VO1 Number of voxels:  260
    sub-02 VO2 Number of voxels:  221
    sub-02 LO1 Number of voxels:  391
    sub-02 LO2 Number of voxels:  246
    sub-02 TO1 Number of voxels:  376
    sub-02 TO2 Number of voxels:  115
    sub-02 V3b Number of voxels:  152
    sub-02 V3a Number of voxels:  663

    sub-03 V1 Number of voxels:  1709
    sub-03 V2 Number of voxels:  1393
    sub-03 V3 Number of voxels:  1166
    sub-03 hV4 Number of voxels:  782
    sub-03 VO1 Number of voxels:  341
    sub-03 VO2 Number of voxels:  227
    sub-03 LO1 Number of voxels:  306
    sub-03 LO2 Number of voxels:  344
    sub-03 TO1 Number of voxels:  286
    sub-03 TO2 Number of voxels:  263
    sub-03 V3b Number of voxels:  313
    sub-03 V3a Number of voxels:  832
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
