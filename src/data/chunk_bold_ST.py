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


def get_arguments():

    parser = argparse.ArgumentParser(description='Chunk detrended bold signal into 1D arrays')
    parser.add_argument('--run_dir', default=None, type=str, help='path to run dir (absolute)')
    parser.add_argument('--chunk_size', default=240, type=int, help='number of voxels per chunk')
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    '''
    Chunk flattened (masked) and detrended brain signal processed with average_bold.py into segments (chunks)

    Produces several short segments (voxels, frames) that can be loaded easily into matlab
    (> 800 chunks for ~200k voxels within the single-subject mask)

    PRF processes each voxel individually, which is insanely slow
    The chunks allow to run the pipeline in parallel from different machines (e.g., elm and ginkgo)
    '''
    args = get_arguments()

    #dir_path = '/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis' if args.run_dir is None else args.run_dir
    dir_path = '/home/mariestl/cneuromod/retinotopy/retino_analysis' if args.run_dir is None else args.run_dir

    sub_list = ['sub-01']
    task_list = ['wedges', 'rings', 'bars']

    for sub in sub_list:

        for task in task_list:

            bold = loadmat(os.path.join(dir_path, 'output', 'detrend', sub + '_epi_FULLbrain_' + task + '_ST.mat'))[sub + '_' + task]

            num_vox = bold.shape[0]
            # ideally a multiple of the number of cores (matlab workers) available in profile on elm/ginkco
            # default for parpool processing set in interface (local profile), bottom left icon
            chunk_size = args.chunk_size
            '''
            Number of voxels within "Whole Brain" mask outputed by average_bold.py, per participant
            sub-01: 205276 voxels (w inclusive full brain mask and slicetimed EPI mask)
            sub-02: ?? voxels (w inclusive full brain mask)
            sub-03: ?? voxels (w inclusive full brain mask)
            '''

            file_path = os.path.join(dir_path, 'output', 'detrend', 'chunks_fullbrain_ST', 's'+ sub[-2:], sub + '_epi_ST_FULLbrain_' + task + '_%04d.mat')

            for i in range(int(np.ceil(num_vox/chunk_size))):

                savemat(file_path % i, {'sub' + sub[-2:] + '_' + task: bold[i*chunk_size:(i+1)*chunk_size, :]})
