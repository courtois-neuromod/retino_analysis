
# FS on CC doc link: https://docs.computecanada.ca/wiki/FreeSurfer

# BEFORE HAND IN CONSOLE:
# module load freesurfer/7.1.1
# source $EBROOTFREESURFER/FreeSurferEnv.sh

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


def call_vol2surf(sub: str, volumefile: str, outfile: str, outdir: str):
    """Produces two outfiles (lh.outfile.mgz, rh.outfile.mgz)"""
    for hemi in ['lh', 'rh']:
        subprocess.run(
            ['mri_vol2surf', '--src', volumefile, '--out', pjoin(outdir, f'{hemi}.{outfile}.mgz'),
             '--regheader', sub, '--hemi', hemi]
        )

# TODO: Do I need to convert the angle from degree (KK's output) to radiants ?
# NO: Oli keeps it in degrees too

# Load data and convert to numpy array
dir_path = '/project/rrg-pbellec/mstlaure/retino_analysis'
fs_out_dir = os.path.join(dir_path, 'results', 'fs')

handle = 's01_3tasks'
sub = 'sub-01' # needs to be in this format for freesurfer to find registration info in anat file...
# /project/rrg-pbellec/datasets/cneuromod_processed/smriprep/sub-01/anat

# https://surfer.nmr.mgh.harvard.edu/fswiki/mri_vol2surf
# https://neurostars.org/t/volume-to-surface-mapping-mri-vol2surf-using-fmriprep-outputs/4079

# just paths, loaded by the script
ecc_path = os.path.join(dir_path, 'results', handle + '_ecc.nii.gz')
ang_path = os.path.join(dir_path, 'results', handle + '_ang.nii.gz')
r2_path = os.path.join(dir_path, 'results', handle + '_R2.nii.gz')
rfsize_path = os.path.join(dir_path, 'results', handle + '_rfsize.nii.gz')
x_path = os.path.join(dir_path, 'results', handle + '_x.nii.gz')
y_path = os.path.join(dir_path, 'results', handle + '_y.nii.gz')

path_list = [ecc_path, ang_path, r2_path, rfsize_path, x_path, y_path]
outname_list = ['prf_ecc', 'prf_ang', 'prf_r2', 'prf_rfsize', 'prf_x', 'prf_y', ]

for path, outname in zip(path_list, outname_list):
    call_vol2surf(sub, path, 's'+sub[-2:]+'_'+outname, fs_out_dir)
