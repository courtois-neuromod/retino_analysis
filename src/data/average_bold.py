import os, glob, json
import numpy as np
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


def get_arguments():

    parser = argparse.ArgumentParser(description='Average bold response across retino sessions')
    parser.add_argument('--makemasks', action='store_true', default=False, help='create masks per subject')
    parser.add_argument('--makestim', action='store_true', default=False, help='process stimuli')
    parser.add_argument('--per_session', action='store_true', default=False, help='exports detrended bold signal separately per session')
    parser.add_argument('--dir_path', default=None, type=str, help='path to run dir (absolute)')
    parser.add_argument('--target_dim', default=(192, 192), help='target dimensions for resized stimulus images')
    args = parser.parse_args()

    return args


def make_sub_mask(dir_path, sub):
    '''
    single-subject whole-brain mask is built with a conjunction of each run's epi mask
    and of the (smoothed) grey matter mask computed with freesurfer (to compensate for signal dropout
    in some regions excluded by epi masks)

    Importantly, the number of voxels must be the same across all tasks and sessions
    '''
    mask_list = []

    mask_path_list = sorted(glob.glob(os.path.join(dir_path, 'data', 'temp_bold', sub + '*_space-T1w_desc-brain_part-mag_mask.nii.gz')))

    for mask_path in mask_path_list:
        mask = nib.load(mask_path)
        mask_list.append(mask)

    # mean epi mask
    mean_epi_mask = intersect_masks(mask_list, threshold=0.3)
    nib.save(mean_epi_mask, os.path.join(dir_path, 'output', 'masks', sub + '_mean_epi_mask.nii.gz'))

    # grey matter (anat) segmentation mask
    anat_path = '/project/rrg-pbellec/datasets/cneuromod_processed/smriprep/' + sub + '/anat'
    seg_mask = nib.load(os.path.join(anat_path, sub + '_label-GM_probseg.nii.gz'))
    seg_mask_rs = resample_to_img(seg_mask, mean_epi_mask, interpolation='nearest')
    seg_mask_rs_sm = smooth_img(imgs=seg_mask_rs, fwhm=3)
    GM_mask = nib.nifti1.Nifti1Image((seg_mask_rs_sm.get_fdata() > 0.15).astype('float'), affine=seg_mask_rs_sm.affine)
    nib.save(GM_mask, os.path.join(dir_path, 'output', 'masks', sub + '_GMmask.nii.gz'))

    # 0 threshold = union, 1 threshold = intersection; accept any voxel included in either mask
    sub_mask = intersect_masks([GM_mask, mean_epi_mask], threshold=0.0)
    nib.save(sub_mask, os.path.join(dir_path, 'output', 'masks', sub + '_WholeBrain.nii.gz'))

    return sub_mask


def flatten_epi(dir_path, sub, task_list, per_session=False):

    epilist_per_task = []
    confounds_per_task = []
    sub_affine = None

    for task in task_list:
        scan_list = sorted(glob.glob(os.path.join(dir_path, 'data', 'temp_bold', sub + '*' + task + '_space-T1w_desc-preproc_part-mag_bold.nii.gz')))
        flatbold_list = []

        sess_num = 1

        for scan in scan_list:

            if sub_affine is None:
                sub_affine = nib.load(scan).affine

            epi = nib.load(scan)
            assert np.sum(epi.affine == sub_affine) == 16
            print(epi.shape) # (76, 90, 71, 202) = x, y, z, time (TR)
            assert epi.shape[-1] == 202

            flat_bold = apply_mask(imgs=epi, mask_img=sub_mask) # shape: (time, vox)

            # extract epi's confounds
            confounds = Minimal(global_signal='basic').load(scan[:-20] + 'bold.nii.gz')

            # Detrend and normalize flattened data
            # note: signal.clean takes (time, vox) shaped input
            flat_bold_dt = clean(flat_bold, detrend=True, standardize='zscore',
                                 standardize_confounds=True, t_r=None, confounds=confounds, ensure_finite=True).T # shape: vox per time

            # Remove first 3 volumes of each run
            flat_bold_dt = flat_bold_dt[:, 3:]

            if per_session:
                savemat(os.path.join(dir_path, 'output', 'detrend', sub + '_epi_FULLbrain_' + task + '_sess' + str(sess_num) +'.mat'), {sub + '_' + task : flat_bold_dt})
            else:
                flatbold_list.append(flat_bold_dt)

            sess_num += 1

        if not per_session:
            mean_bold = np.mean(np.array(flatbold_list), axis=0) # shape: voxel per time

            # provides the data as a cell vector of voxels x time. For K.Kay's toolbox, it can also be X x Y x Z x time
            print(mean_bold.shape)
            savemat(os.path.join(dir_path, 'output', 'detrend', sub + '_epi_FULLbrain_' + task + '.mat'), {sub + '_' + task : mean_bold})


def resize_stimuli(dir_path, task_list, target_dim=(192, 192)):
    '''
    resize stimuli produced with make_stimuli.py from 768x768 to 192x192 pixels to speed up pRF processing
    '''

    for task in task_list:
        # remove first 3 TRs of each task for signal equilibration
        stimuli = loadmat(os.path.join(dir_path, 'stimuli', task + '_per_TR.mat'))[task][:, :, 3:]

        resized_stim = np.zeros([192, 192, stimuli.shape[2]])

        for i in range(stimuli.shape[2]):
            frame = stimuli[:, :, i]
            resized_stim[:, :, i] = resize(frame, target_dim, preserve_range=True, anti_aliasing=True)

        savemat(os.path.join(dir_path, 'stimuli', task + '_per_TR199_' + str(target_dim[0]) + 'x' + str(target_dim[1]) + '.mat'), {task: resized_stim.astype('f4')})


if __name__ == '__main__':
    '''
    Script takes runs of bold.nii.gz files, detrends them,
    averages them per task across session, masks and flattens them and exports
    them into .mat files

    It also resizes visual stimuli (apertures) to reduce processing time with analyzePRF
    (by reducing the number of pixels to explore)
    '''
    args = get_arguments()

    dir_path = '/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis' if args.dir_path is None else args.dir_path

    sub_list = ['sub-01', 'sub-02', 'sub-03']
    task_list = ['wedges', 'rings', 'bars']

    for sub in sub_list:

        if args.makemasks:
            sub_mask = make_sub_mask(dir_path, sub)
        else:
            sub_mask = nib.load(os.path.join(dir_path, 'output', 'masks', sub + '_WholeBrain.nii.gz'))

        flatten_epi(dir_path, sub, task_list, args.per_session)

    if args.makestim:

        resize_stimuli(dir_path, task_list, args.target_dim)
