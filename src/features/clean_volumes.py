import os, glob, json

import numpy as np
import pandas as pd
import nibabel as nib
from nilearn.masking import unmask, apply_mask
from scipy.io import loadmat, savemat

import argparse


def get_arguments():

    parser = argparse.ArgumentParser(description='Reassamble retinotopy outputs from chunks into brain volumes')
    parser.add_argument('--sub_num', required=True, type=str, help='subject number e.g., sub-01')
    parser.add_argument('--dir_path', default=None, type=str, help='path to run dir (absolute)')
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    '''
    Script masks out bad voxels (some runs have no variability in the signal) from volumes,
    based on clean voxel mask outputed by the quick_mask_QC_retino.py script
    '''
    args = get_arguments()

    # On Beluga
    dir_path = '/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis' if args.dir_path is None else args.dir_path
    sub = args.sub_num # format = 'sub-01'

    # Load mask used to vectorize the detrended bold data
    full_mask = nib.load(os.path.join(dir_path, 'output/masks', sub + '_WholeBrain.nii.gz'))
    # Load clean mask that excludes  nan valued voxels
    clean_mask = nib.load(os.path.join(dir_path, 'output/masks', sub[-2:] + '_goodvoxmask_T1w_retino.nii'))

    '''
    Step 1: clean up R2 volume maps
    Adapts K Kay's analyzePRF R^2 values from analyzePRF for Neuropythy
    AnalyzePRF exports R^2 as val between ~0 (some vals negative) and ~100

    "The R2 values are computed after projecting out polynomials from both
    the data and the model fit. Because of this projection, values can
    sometimes drop below 0%"

    Neuropythy : variance explained must be a fraction between v such that 0 ≤ v ≤ 1
    '''
    r2 = loadmat(f'{dir_path}/results/analyzePRF/sub{sub[-2:]}_fullbrain_R2.mat')[f'sub{sub[-2:]}_R2'].reshape(-1,)
    # replace nan by 0: no variance exmplained
    r2 = np.nan_to_num(r2)/100 # convert percentage
    # Cap values between 0 and 1
    r2[r2 < 0.0] = 0.0
    r2[r2 > 1.0] = 1.0
    r2_vol = unmask(r2, full_mask)
    # mask out voxels without variability from volume
    r2_vol_clean = unmask(apply_mask(r2_vol, clean_mask), clean_mask)
    nib.save(r2_vol, f'{dir_path}/results/analyzePRF/{sub}_fullbrain_R2_goodvox.nii.gz')

    '''
    Step 2: clean up receptive field size
    With a standard 2D isotropic gaussian model, rfsize corresponds to sigma

    The analyzePRF model is slightly different:
        rfsize = sigma/sqrt(n) where n is the exponent of the power law function;
        output 'expt' contains pRF exponent estimates (is that n???).

        Similar to the original model (gaussian), except that a static
        power-law nonlinearity is added after summation across the visual field.

        Question: do we need to recalculate sigma from size?
        e.g., sigma = rfsize*np.sqrt(expt)
        (NO! Use outputed rfsize as-is as if it were sigma)
        From paper: https://journals.physiology.org/doi/full/10.1152/jn.00105.2013

        "For a model for which the predicted response to point stimuli does not
        have a Gaussian profile, we could simply stipulate that pRF size is the
        standard deviation of a Gaussian function fitted to the actual profile."

    AnalyzePRF: rfsize is in pixels with 0 lower bound. Stimulus images were
                rescaled from 768x768 to 192x192, which correspond to
                10 deg of visual angle (width of on-screen stimuli)
    Neuropythy: Sigma/pRF size must be in degrees of the visual field

    To convert rfsize, x and y from pixel to degrees of visual angle:
        The rescaled stimulus is 192x192 pixels for 10 degrees of visual angle (width).
        To convert from pixels to degrees, multiply by 10/192.
    '''
    conv_factor = 10/192

    rfsize = loadmat(f'{dir_path}/results/analyzePRF/sub{sub[-2:]}_fullbrain_rfsize.mat')[f'sub{sub[-2:]}_rfsize'].reshape(-1,)
    # remove np.inf values and replace w max finite value
    rfs_max = np.max(rfsize[np.isfinite(rfsize)])
    rfsize[rfsize == np.inf] = rfs_max

    # convert from pixels to degres of vis angle
    rfsize = rfsize*conv_factor

    rfsize_vol = unmask(rfsize, full_mask)
    # mask out voxels without variability from volume
    rfsize_vol_clean = unmask(apply_mask(rfsize_vol, clean_mask), clean_mask)

    nib.save(rfsize_vol_clean, f'{dir_path}/results/analyzePRF/{sub}_fullbrain_rfsize_goodvox.nii.gz')


    '''
    Step 3: clean up angles and eccentricity volumes
    AnalyzePRF: angle and eccentricity values are in pixel units with a lower bound of 0 pixels.
    Neuropythy: values must be in degrees of visual angle from the fovea.
    '''
    ecc = loadmat(f'{dir_path}/results/analyzePRF/sub{sub[-2:]}_fullbrain_ecc.mat')[f'sub{sub[-2:]}_ecc'].reshape(-1,)
    ang = loadmat(f'{dir_path}/results/analyzePRF/sub{sub[-2:]}_fullbrain_ang.mat')[f'sub{sub[-2:]}_ang'].reshape(-1,)

    # calculate x and y coordinates (in pixels)
    x = np.cos(np.radians(ang))*ecc
    y = np.sin(np.radians(ang))*ecc

    # convert from pixels to degrees of visual angle
    ecc *= conv_factor
    x *= conv_factor
    y *= conv_factor

    # create map of capped eccentricity values (only include tested values)
    ecc_cap10deg = ecc.copy()
    ecc_mask = (ecc_cap10deg < 10.0).astype(int)
    ecc_cap10deg[ecc_cap10deg > 10.0] = np.nan


    # generate clean volumes (remove voxels without signal variability)
    ecc_vol = unmask(apply_mask(unmask(ecc, full_mask), clean_mask), clean_mask)
    ecc_mask_vol = unmask(apply_mask(unmask(ecc_mask, full_mask), clean_mask), clean_mask)
    ecc_cap10deg_vol = unmask(apply_mask(unmask(ecc_cap10deg, full_mask), clean_mask), clean_mask)
    ang_vol_compass = unmask(apply_mask(unmask(ang, full_mask), clean_mask), clean_mask)
    x_vol = unmask(apply_mask(unmask(x, full_mask), clean_mask), clean_mask)
    y_vol = unmask(apply_mask(unmask(y, full_mask), clean_mask), clean_mask)

    nib.save(ecc_vol, f'{dir_path}/results/analyzePRF/{sub}_fullbrain_ecc_goodvox.nii.gz')
    nib.save(ecc_mask_vol, f'{dir_path}/results/analyzePRF/{sub}_fullbrain_eccMask10_goodvox.nii.gz')
    nib.save(ecc_cap10deg_vol, f'{dir_path}/results/analyzePRF/{sub}_fullbrain_eccCAP10DEG_goodvox.nii.gz')
    nib.save(ang_vol_compass, f'{dir_path}/results/analyzePRF/{sub}_fullbrain_angCompass_goodvox.nii.gz')
    nib.save(x_vol, f'{dir_path}/results/analyzePRF/{sub}_fullbrain_x_goodvox.nii.gz')
    nib.save(y_vol, f'{dir_path}/results/analyzePRF/{sub}_fullbrain_y_goodvox.nii.gz')

    '''
    Transform angle values for Neuropythy and clean w volume mask
    AnalyzePRF: angle values range between 0 and 360 degrees.
    0 corresponds to the right horizontal meridian, 90 corresponds to the upper vertical meridian, and so on.
    In the case where <ecc> is estimated to be exactly equal to 0,
    the corresponding <ang> value is deliberately set to NaN.

    Neuropythy: Angle values vary from 0-180.
    Values must be absolute (the doc is not up to date in the Usage manual; repo's readme must up to date)
    0 represents the upper vertical meridian and 180 represents the lower vertical meridian in both hemifields.
    Positive values refer to the right visual hemi-field for the left hemisphere, and vice versa.

    https://github.com/noahbenson/neuropythy/issues?q=is%3Aissue+is%3Aclosed
    '''
    # converts angles from "compass" to "signed north-south" for neuropythy
    ang[np.logical_not(ang > 270)] = 90 - ang[np.logical_not(ang > 270)]
    ang[ang > 270] = 450 - ang[ang > 270]
    ang = np.absolute(ang)

    ang_vol = unmask(apply_mask(unmask(ang, full_mask), clean_mask), clean_mask)
    nib.save(ang_vol, f'{dir_path}/results/analyzePRF/{sub}_fullbrain_ang_goodvox.nii.gz')


    '''
    Clean up Neuropythy output volumes resampled to T1w functional space
    '''
    npy_dir_path = f'/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/results/npythy/{sub}'
    found_list = glob.glob(f'{npy_dir_path}/resampled*.nii.gz')
    file_list = [x for x in found_list if 'goodvox' not in x]

    for file in file_list:
        rs_vol = unmask(apply_mask(nib.load(file), clean_mask), clean_mask)
        nib.save(rs_vol, f'{file[:-7]}_goodvox.nii.gz')
