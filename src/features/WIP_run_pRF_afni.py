"""
Nonpython requirements: FSL, AFNI
"""
import os, sys, glob
import subprocess
import warnings
from os import pardir
from os.path import abspath
from os.path import join as pjoin
from shutil import copyfile

import nibabel as nib
import numpy as np
from nilearn.image import load_img, new_img_like, index_img, resample_to_img
from nilearn.masking import intersect_masks, apply_mask, unmask
from nipype.interfaces.fsl.maths import TemporalFilter
from nipype.pipeline.engine import MapNode
from scipy.io import loadmat, savemat
from scipy.stats import zscore
from tqdm import tqdm


parser = argparse.ArgumentParser(description='Perform pRF analysis in AFNI')
parser.add_argument('--run_dir', default='', type=str, help='path to run dir (absolute)')
parser.add_argument('--config', default='config.json', type=str, help='name of config file')
args = parser.parse_args()


class ThingsPrfAfni:
    """
    Runs AFNIs PRF analysis on the THINGS-fMRI data.
    Requires fMRIPREP output of localizer sessions and afni brik files specifying the stimulus.
    Preprocessing (in addition to fmriprep) includes temporal filtering of individual runs, averaging them,
    and zscoring the resulting average time series. This pipeline creates a temporary working directory in the parent
    directory of the bids dataset. The results are saved to the derivatives section of the bids dataset.

    Example:
        prfdata = ThingsPrfAfni(bidsroot=pjoin(pardir, pardir, pardir), subject='01)
        prfdata.run()
    """

    def __init__(
            self, bidsroot, subject,
            stimulus_brik='/Users/olivercontier/bigfri/misc/prf_info_martin/prf_stim_briks/stim.308.LIA.bmask.resam+orig.BRIK',
            stimulus_head='/Users/olivercontier/bigfri/misc/prf_info_martin/prf_stim_briks/stim.308.LIA.bmask.resam+orig.HEAD',
            conv_fname='/Users/olivercontier/bigfri/scratch/bids/code/external_libraries/conv.ref.spmg1_manual.1D',
            sesmap={'01': 'localizer2',
                    '02': 'localizer2',
                    '03': 'localizer1'},
            fmriprep_deriv_name='fmriprep',
            out_deriv_name='prf_afni',
            preproc_hpf=100.,
            stimdur: float = 3.,
    ):
        self.bidsroot = abspath(bidsroot)
        self.subject = subject
        self.sesmap = sesmap
        self.conv_fname = conv_fname
        self.stimbrik = stimulus_brik
        self.stimhead = stimulus_head
        self.wdir = pjoin(self.bidsroot, pardir, 'prf_afni_wdir', f'sub-{subject}')
        self.outdir = pjoin(self.bidsroot, 'derivatives', out_deriv_name, f'sub-{subject}')
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        self.data = pjoin(self.wdir, 'data.nii.gz')
        if not os.path.exists(self.wdir):
            os.makedirs(self.wdir)
        else:
            warnings.warn(f'working directory already exists. Files may be overwritten in\n{self.wdir}')
        self.copy_stimbrik()
        self.nruns = 4
        self.tr = 1.5
        self.stimwidth_pix = 990
        self.ppd = 90
        self.hpf = preproc_hpf
        self.ses = sesmap[subject]
        self.fmriprep_deriv_name = fmriprep_deriv_name
        self.fmriprep_dir = pjoin(
            self.bidsroot, 'derivatives', fmriprep_deriv_name, f'sub-{subject}', f'ses-{self.ses}', 'func')
        self.boldfiles_fprep, self.maskfiles_fprep = self.get_file_names()
        self.umask_f = pjoin(self.wdir, 'unionmask.nii.gz')
        self.stmidur = stimdur
        self.buck_map = {'amp': 0, 'x': 1, 'y': 2, 'sigma': 3, 'rsquared': 10}  # meaning of sub bricks in afni output

    def get_file_names(self):
        boldfiles_fprep = [
            pjoin(
                self.fmriprep_dir,
                f'sub-{self.subject}_ses-{self.ses}_task-pRF_run-{runi}_space-T1w_desc-preproc_bold.nii.gz'
            )
            for runi in range(1, self.nruns + 1)]
        maskfiles_fprep = [
            pjoin(
                self.fmriprep_dir,
                f'sub-{self.subject}_ses-{self.ses}_task-pRF_run-{runi}_space-T1w_desc-brain_mask.nii.gz'
            )
            for runi in range(1, self.nruns + 1)
        ]
        for l in [boldfiles_fprep, maskfiles_fprep]:
            for e in l:
                if not os.path.exists(e):
                    raise IOError(f'Could not find file\n{e}')
        return boldfiles_fprep, maskfiles_fprep

    def preproc_data(self):
        # temporal filtering with fsl
        tf = MapNode(TemporalFilter(highpass_sigma=self.hpf / self.tr), name='TemporalFilter', iterfield=['in_file'])
        tf.inputs.in_file = self.boldfiles_fprep
        tf.run()
        filterd_boldfiles = tf.get_output('out_file')  # list of filtered bold files
        # create a brain mask
        umask = intersect_masks(self.maskfiles_fprep, threshold=0)
        umask.to_filename(self.umask_f)
        # load in numpy, average, z score
        bold_arrs = [apply_mask(bp, umask) for bp in tqdm(filterd_boldfiles, desc='loading runs for averaging')]
        data_arr = zscore(np.mean(np.stack(bold_arrs), axis=0), axis=0)
        # save to working directory
        data_img = unmask(data_arr, umask)
        data_img.to_filename(self.data)

    def copy_stimbrik(self):
        """to working directory"""
        for f in [self.stimbrik, self.stimhead]:
            copyfile(f, pjoin(self.wdir, os.path.basename(f)))

    def set_afni_environ(self):
        os.environ['AFNI_CONVMODEL_REF'] = self.conv_fname
        os.environ['AFNI_MODEL_PRF_STIM_DSET'] = self.stimhead.replace('HEAD', '')
        os.environ['AFNI_MODEL_PRF_ON_GRID'] = 'YES'
        os.environ['AFNI_MODEL_DEBUG'] = '3'

    def run_afni(self):
        os.chdir(self.wdir)
        subprocess.run(["3dcopy", self.data, 'AFNIpRF+orig.'])
        subprocess.run(['3dcopy', self.umask_f, 'automask+orig.'])
        # subprocess.run(['3dDeconvolve', '-nodata', '18', str(self.tr), '-polort', '-1', '-num_stimts', '1',
        #                 '-stim_times', '1', f'1D:0', f'SPMG1({self.stmidur})', '-x1D', self.conv_fname])
        self.set_afni_environ()
        subprocess.run(
            ['3dNLfim', '-input', 'AFNIpRF+orig.', '-mask', 'automask+orig.', '-noise', 'Zero', '-signal', 'Conv_PRF',
             '-sconstr', '0', '-20.0', '20.0', '-sconstr', '1', '-1.0', '1.0', '-sconstr', '2', '-1.0', '1.0',
             '-sconstr', '3', '0.0', '1.0', '-BOTH', '-nrand', '10000', '-nbest', '5', '-bucket', '0', 'Buck.PRF',
             '-snfit', 'snfit.PRF', '-TR', str(self.tr), '-float']
        )
        for k, v in self.buck_map.items():
            subprocess.run(['3dAFNItoNIFTI', '-prefix', f'{k}.nii.gz', f'Buck.PRF+orig.[{v}]'])

    def unit_to_dva(self, in_file, out_file):
        """Take a nifti that encodes x,y, or sigma in unit measures (0-1) and convert to degree visual angle"""
        in_img = nib.load(in_file)
        arr = in_img.get_fdata()
        dva_arr = (arr * self.stimwidth_pix) / self.ppd
        out_img = nib.Nifti1Image(dva_arr, affine=in_img.affine)
        out_img.to_filename(out_file)
        return dva_arr

    def convert_afni_output(self):
        # convert to dva, overwriting afni output which is in unit measures
        os.chdir(self.wdir)
        for stat in ['x', 'y', 'sigma']:
            _ = self.unit_to_dva(f'{stat}.nii.gz', f'{stat}.nii.gz')
        x_img, y_img = nib.load('x.nii.gz'), nib.load('y.nii.gz')
        x_arr, y_arr = x_img.get_fdata(), y_img.get_fdata()
        # save eccentricity and polar angle directly to derivatives
        ecc_arr, pa_arr = xy_to_eccrad(x_arr, y_arr)
        for arr, name in zip([ecc_arr, pa_arr], ['ecc', 'pa']):
            img = nib.Nifti1Image(arr, affine=x_img.affine)
            img.to_filename(pjoin(self.outdir, f'{name}.nii.gz'))

    def copy_results(self):
        """From working directory to bids derivatives"""
        for k in self.buck_map.keys():
            copyfile(pjoin(self.wdir, f'{k}.nii.gz'), pjoin(self.outdir, f'{k}.nii.gz'))
        for prefix in ['snfit.PRF+orig', 'Buck.PRF+orig']:
            for suffix in ['HEAD', 'BRIK']:
                copyfile(pjoin(self.wdir, ".".join([prefix, suffix])), pjoin(self.outdir, ".".join([prefix, suffix])))

    def run(self):
        if not os.path.exists(self.data):
            self.preproc_data()
        if not os.path.exists(pjoin(self.wdir, 'Buck.PRF+orig.BRIK')):
            self.run_afni()
        self.convert_afni_output()
        self.copy_results()


def run_pRF_afni(cfg):
    '''
    Needed: binary mask of stimuli converted to .BRIK / .HEAD file (Martin has matlab script for that)
    '''
    os.chdir(self.wdir)

    subprocess.run(["3dcopy", self.data, 'AFNIpRF+orig.'])
    subprocess.run(['3dcopy', self.umask_f, 'automask+orig.'])

        # subprocess.run(['3dDeconvolve', '-nodata', '18', str(self.tr), '-polort', '-1', '-num_stimts', '1',
        #                 '-stim_times', '1', f'1D:0', f'SPMG1({self.stmidur})', '-x1D', self.conv_fname])
        self.set_afni_environ()
        subprocess.run(
            ['3dNLfim', '-input', 'AFNIpRF+orig.', '-mask', 'automask+orig.', '-noise', 'Zero', '-signal', 'Conv_PRF',
             '-sconstr', '0', '-20.0', '20.0', '-sconstr', '1', '-1.0', '1.0', '-sconstr', '2', '-1.0', '1.0',
             '-sconstr', '3', '0.0', '1.0', '-BOTH', '-nrand', '10000', '-nbest', '5', '-bucket', '0', 'Buck.PRF',
             '-snfit', 'snfit.PRF', '-TR', str(self.tr), '-float']
        )
        for k, v in self.buck_map.items():
            subprocess.run(['3dAFNItoNIFTI', '-prefix', f'{k}.nii.gz', f'Buck.PRF+orig.[{v}]'])

    pass


def preprocess(dir_path, cfg):

    sub = cfg['subject']
    task_list = cfg['task_list']
    epi_per_task = []

    if cfg['use_GM_mask']:
        sub_mask = nib.load(os.path.join(dir_path, 'output', 'masks', sub + '_GMmask.nii.gz'))
    else:
        sub_mask = nib.load(os.path.join(dir_path, 'output', 'masks', sub + '_mean_epi_mask.nii.gz'))

    sub_mask.to_filename(os.path.join(dir_path, temp_dir, sub+'_mask.nii.gz'))
    sub_affine = sub_mask.affine

    for task in task_list:
        scan_list = sorted(glob.glob(os.path.join(dir_path, 'data', 'temp_bold', sub + '*' + task + '_space-T1w_desc-preproc_part-mag_bold.nii.gz')))
        flatbold_list = []

        for scan in scan_list:

            epi = nib.load(scan) # (76, 90, 71, 202) = x, y, z, time (TR)
            assert np.sum(epi.affine == sub_affine) == 16
            assert epi.shape[-1] == 202

            confounds = Minimal(global_signal='basic').load(scan[:-20] + 'bold.nii.gz')

            flat_bold = apply_mask(imgs=epi, mask_img=sub_mask) # shape: (TR, voxel)

            flat_bold_dt = clean(flat_bold, detrend=True, standardize='zscore',
                                 standardize_confounds=True, t_r=None, confounds=confounds, ensure_finite=True) # shape: (TR, voxel)

            # Remove first 3 volumes of each run
            flatbold_list.append(flat_bold_dt[3:, :])

        mean_bold = np.mean(np.array(flatbold_list), axis=0).T # shape: (voxel, TR)
        epi_per_task.append(mean_bold)

    concat_bold = np.concatenate(epi_per_task, axis = -1).T # shape: (TR, voxel)

    deflat_bold = unmask(concat_bold, sub_mask) # shape: (x, y, z, TR)
    deflat_bold.to_filename(os.path.join(dir_path, temp_dir, sub+'_data.nii.gz'))

    return sub_mask, deflat_bold


if __name__ == "__main__":

    with open(os.path.join(args.run_dir, 'config', args.config), 'r') as f:
        cfg = json.load(f)

    dir_path = args.run_dir

    mask, bold_data = preprocess(dir_path, cfg)

    # copy stimulus BRIK file into temp working directory
    for f in [cfg['stimulus_brik'], cfg['stimulus_head']]:
        copyfile(f, os.path.join(dir_path, temp_dir, os.path.basename(f)))


    run_pRF_afni(cfg)
