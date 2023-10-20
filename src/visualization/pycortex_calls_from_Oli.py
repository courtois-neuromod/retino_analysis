import cortex
from os.path import join as pjoin
import nibabel as nib
import numpy as np
import glob
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

def get_scicol(scicol_dir):
    """Get Scientific Color maps"""
    col_dirs = glob.glob(pjoin(scicol_dir, '[!+]*'))
    col_names = [cd.split('/')[-1] for cd in col_dirs]
    cdict = {}
    for cd, cn in zip(col_dirs, col_names):
        txt = glob.glob(pjoin(cd, '*.txt'))[0]
        cdict[cn] = LinearSegmentedColormap.from_list(cn, np.loadtxt(txt))
    return cdict

def pyc_load(nifti):
    """Load nifti file suited for pycortex"""
    return np.swapaxes(nib.load(nifti).get_fdata(), 0, -1)


bidsroot = '/Users/olivercontier/bigfri/scratch/bids'
reconall_basedir = pjoin(bidsroot, 'derivatives', 'reconall')
scicols = get_scicol(pjoin(bidsroot, 'code', 'ScientificColourMaps7'))

sub=3

## Import Relevant surfaces and volumes from freesurfers reconall output ##

# cortex.freesurfer.import_subj(
#     fs_subject='sub-03', cx_subject='S3',
#     freesurfer_subject_dir=reconall_basedir,
# )

### Cut surfaces ###

# load prf volume to guide cutting along calcarine sulcus
# pa_f = f'/Users/olivercontier/bigfri/scratch/bids/derivatives/prf_afni/sub-0{sub}/pa.nii.gz'
# pa_f = f'/Users/olivercontier/bigfri/scratch/bids/derivatives/prf_neuropythy/sub-0{sub}/inferred_angle.nii.gz'
# pa_f = f'/Users/olivercontier/bigfri/scratch/bids/derivatives/reconall_screwedup/sub-0{sub}/mri/inferred_angle.mgz'
# va_f = f'/Users/olivercontier/bigfri/scratch/bids/derivatives/reconall_screwedup/sub-0{sub}/mri/inferred_varea.mgz'
# pa_f = f'/Users/olivercontier/bigfri/scratch/neuropythy_wdir/sub-0{sub}/pa.nii.gz'
# va_f = f'/Users/olivercontier/bigfri/scratch/bids/derivatives/prf_neuropythy/sub-0{sub}/resampled_varea.nii.gz'
# pa_arr = np.swapaxes(nib.load(pa_f).get_fdata(), 0, -1)
# va_arr = np.swapaxes(nib.load(va_f).get_fdata(), 0, -1)
# pa_vol = cortex.Volume(pa_arr, f'S{sub}', 'identity', vmin=20, vmax=160, cmap=scicols['vik'])
# va_vol = cortex.Volume(va_arr, f'S{sub}', 'identity', vmin=0, vmax=12, cmap=scicols['batlow'])

# Opens blender -> set manual cuts, save and close. Terminal prompt will ask you to proceed, then wait 1h
# cortex.segment.cut_surface(
#     f'S{sub}', 'rh',
#     fs_subject=f'sub-0{sub}',
#     freesurfer_subject_dir='/Users/olivercontier/bigfri/scratch/bids/derivatives/reconall',
#     do_import_subject=True,
#     data=pa_vol,
# )

# when the pycortex call to mris_flatten fails,
# one can simply call mris_flatten -O inpath outpath. Example:
# cd ~/bigfri/scratch/bids/derivatives/reconall/sub-03/surf
# mris_flatten -w=25 -O /Users/olivercontier/bigfri/scratch/bids/derivatives/reconall/sub-03/surf/lh.flatten.patch.3d /Users/olivercontier/bigfri/scratch/bids/derivatives/reconall/sub-03/surf/lh.flatten.flat.patch.3d
# note: pycortex calls mris_flatten with the 'fudicial', which doesn't work manually (with FS v7)
# and may be the cause for the segfault.

# run this after cut_surface has successfully finished
# to import the patch file stored in the freesurfer directory as a .gii file in the
# pyortex file store
# cortex.freesurfer.import_flat(
#     f'sub-0{sub}',
#     'flatten',
#     hemis=['lh'],
#     cx_subject=f'S{sub}',
#     flat_type='freesurfer',
#     auto_overwrite=True,
#     freesurfer_subject_dir='/Users/olivercontier/bigfri/scratch/bids/derivatives/reconall',
#     clean=True
# )

# cutting "wide seems", i.e. a parallel line of 2-3 vertices works better.
# On the other hand, it might throw away interesting vertices?

# lh.flatten.flat.patch.3d is saved to /derivatives/reconall directory. use mriconvert to make a .gii
# for that, manually copy lh.orig to the pycortex filestore/subject/surfaces/lh.orig
# (or the working direcotry?)
# mris_convert -p surfaces/lh.flatten.flat.patch.3d flat_lh.gii

## one can run bet manually instead of implicitly by align.automatic to avoid

# beelow calls on bet -B ... to generate brain mask. but the -B flag leads to a segfault (for whatever reason)
# circumvent by calling without -B manually
# bet /Users/olivercontier/pycortex_filestore/S2/anatomicals/raw.nii.gz /Users/olivercontier/pycortex_filestore/S2/anatomicals/brainmask.nii.gz -R -v
#... though it worked for subject 03

# sub=3
# cortex.align.automatic(
#     f'S{sub}', 'align_auto',
#     pjoin(cortex.database.default_filestore,
#           f'S{sub}', 'transforms', 'align_auto_ref', 'ref.nii.gz')
# )


# ### Add object category selective ROIs
# rois = {'1': "FFA", '2': 'OFA', '3': 'EBA', '4': 'PPA', '5':'STS', '6':'TOS', '7':'RSC'}
# julian_dir = pjoin(bidsroot, 'derivatives', 'julian_parcels',
#                     'julian_parcels_edited', f'sub-0{sub}')
# rois_arr = np.zeros(shape=(73, 83, 71), dtype=float)  # shape is subject specific
# for roi_i, roiname in rois.items():
#     print(roiname, roi_i)
#     roi_files = glob.glob(pjoin(julian_dir, '*', f'sub-0{sub}_*{roiname}.nii.gz'))
#     if not roi_files:
#         print(f'\nCOULD NOT FIND ROI: {roiname}\n')
#         continue
#     hemi_arrs = [pyc_load(f).astype(bool) for f in roi_files]
#     roi_arr = np.logical_or(*hemi_arrs)
#     rois_arr[roi_arr] = float(roi_i)
#
# rois_vol = cortex.Volume(rois_arr, f'S{sub}', 'align_auto', cmap='tab10', vmin=0, vmax=9)
# # Look at the resulting map
# # fig = cortex.quickshow(rois_vol, pixelwise=True, with_curvature=True, colorbar_location='left')
# # fig.savefig('test.jpg')
# # # open in inkscape, draw an roi and save as new layer under rois>shape
# cortex.add_roi(rois_vol, **dict(colorbar_location='left'))


## Add early visual ROIs
# npt_outdir = pjoin(bidsroot, 'derivatives', 'prf_neuropythy', f'sub-0{sub}')
# reconall_subdir = pjoin(reconall_basedir, f'sub-0{sub}', 'mri')
# vareas_f = pjoin(reconall_subdir, 'inferred_varea.mgz')
# vareas = pyc_load(vareas_f)
# vareas[vareas == 0] = np.nan
# vol = cortex.Volume(vareas, f'S{sub}', 'identity', cmap='nipy_spectral', vmin=0, vmax=12)
# # fig = cortex.quickshow(vol, pixelwise=True, colorbar_location='left', nanmean=True, with_curvature=True)
# # fig.savefig('test.jpg')
# cortex.add_roi(vol, **dict(colorbar_location='left', pixelwise=True, nanmean=True, with_curvature=True))

## Re-draw V1/2/3 after thresholding by eccentricity
# sub=3
# max_eccen=15.55
# npt_outdir = pjoin(bidsroot, 'derivatives', 'prf_neuropythy', f'sub-0{sub}')
# eccen = pyc_load(pjoin(npt_outdir, 'inferred_eccen_fsorient.nii.gz'))
# va = pyc_load(pjoin(npt_outdir, 'inferred_varea_fsorient.nii.gz'))
# va[eccen>max_eccen] = 0
# va[va==0.] = np.nan
# vol = cortex.Volume(va, f'S{sub}', 'identity', cmap='nipy_spectral', vmin=0, vmax=12)
# # fig = cortex.quickshow(vol, pixelwise=True, colorbar_location='left', nanmean=True, with_curvature=True)
# # plt.show()
# cortex.add_roi(vol, **dict(colorbar_location='left', pixelwise=True, nanmean=True, with_curvature=True))
