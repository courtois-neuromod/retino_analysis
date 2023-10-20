import glob, os
import cortex
import nibabel as nib
#from nilearn.image.image import mean_img
import numpy as np
#from nilearn.masking import unmask, apply_mask
#import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt

'''
Possibly clean final steps

Step 0 (on beluga): do this once
generate mean epi image from one (any) run of bold data (epi)
as reference for transform from T1w functional space into freesurfer space

I used a run from Friends for sub-04, 05 and 06 since they did not complete the retinotopy task
'''
out_dir_refimg = '/project/rrg-pbellec/mstlaure/retino_analysis/results/ref_img'
slist = ['01', '02', '03', '04', '05', '06']

for s in slist:
    #create mean reference image in T1w space to create the transform
    # s1, s2, s3 (retino run, T1w)
    bold_path = f'/project/rrg-pbellec/mstlaure/retino_analysis/data/temp_bold/sub-{s}_ses-004_task-rings_space-T1w_desc-preproc_part-mag_bold.nii.gz'
    # s4, s5, s6 (*friends run, T1w)
    #bold_path = '/project/rrg-pbellec/mstlaure/deepgaze_mr/data/friends_T1w/sub-04/ses-010/func/sub-04_ses-010_task-s01e19a_space-T1w_desc-preproc_bold.nii.gz'
    #bold_path = '/project/rrg-pbellec/mstlaure/deepgaze_mr/data/friends_T1w/sub-05/ses-010/func/sub-05_ses-010_task-s02e19a_space-T1w_desc-preproc_bold.nii.gz'
    #bold_path = '/project/rrg-pbellec/mstlaure/deepgaze_mr/data/friends_T1w/sub-06/ses-010/func/sub-06_ses-010_task-s02e16a_space-T1w_desc-preproc_bold.nii.gz'
    run_epi = nib.load(bold_path)
    mean_epi = mean_img(run_epi)
    nib.save(mean_epi, os.path.join(out_dir_refimg, f'sub-{s}_ref_epi.nii.gz'))

'''
Step 1: do this once (in ipython)
Import local freesurfer data (surfaces and volumes) into pycortex database,
here: /home/labopb/Documents/Marie/neuromod/pycortex_venv2/share/pycortex/db

IMPORTANT: before launching python, set subjects_dir to where the local freesurfer data live
SUBJECTS_DIR="/home/labopb/Documents/Marie/neuromod/freesurfer"

# Local venv (laptop): Documents/Marie/neuromod/pycortex_venv2
'''
fs_dir = '/home/labopb/Documents/Marie/neuromod/freesurfer'
#cmap = ???
# https://gallantlab.github.io/pycortex/colormaps.html

slist = ['01', '02', '03', '04', '05', '06']

for s in slist:
    cortex.freesurfer.import_subj(fs_subject=f'sub-{s}',
                                  cx_subject=f'S{s}_final',
                                  #cx_subject=f'S{s}', #old files; I kept them for now to contrast first ROI tracing attempt, as a ref
                                  freesurfer_subject_dir=fs_dir,
                                  )

'''
Step 2: do this once (ipython)

Generate transform from functional T1w space into freesurfer space using mean reference epi image ref.nii.gz

IMPORTANT:
First save mean epi (from beluga) locally in pycortex database under S{s}_final/transforms/align_auto_ref as "ref.nii.gz"

Before launching python, set subjects_dir to where the local freesurfer data live
SUBJECTS_DIR="/home/labopb/Documents/Marie/neuromod/freesurfer"

Also: ANNOYING limitation!!
cortex.align.automatic function requires the SAME directory name in Freesurfer
and in pycortex db for the same subject in order to work...

Ugly workaround: within my freesurfer subject_dir (/home/labopb/Documents/Marie/neuromod/freesurfer)
I made copies of subjects' directories and renamed them w the pycortex name, so I have both names in SUBJECTS_DIR...
Delete the silly copies once this is done
(e.g., keep sub-01 and delete S01_final from /home/labopb/Documents/Marie/neuromod/freesurfer)

SUBJECTS_DIR="/home/labopb/Documents/Marie/neuromod/freesurfer"
# Local venv (laptop): Documents/Marie/neuromod/pycortex_venv2
'''
# equal to cortex.database.default_filestore (when type in ipython)
pycortex_db_dir = '/home/labopb/Documents/Marie/neuromod/pycortex_venv2/share/pycortex/db'

slist = ['01', '02', '03', '04', '05', '06']

for s in slist:
    cortex.align.automatic(
        #f'S{s}', 'align_auto',
        f'S{s}_final', 'align_auto',
        os.path.join(pycortex_db_dir,
                     #f'S{s}', 'transforms', 'align_auto_ref', 'ref.nii.gz')
                     f'S{s}_final', 'transforms', 'align_auto_ref', 'ref.nii.gz')
    )


'''
Step 3: Cut flat maps in tksurfer from freesurfer directory
(see notes; no need for pycortex except to visualize cuts until something adequate is produced)...

For visualization:
SUBJECTS_DIR="/home/labopb/Documents/Marie/neuromod/freesurfer"
# Local venv (laptop): Documents/Marie/neuromod/pycortex_venv2

# For color maps:
I think I can use any of the following color maps in my pycortex repo (see here):
/home/labopb/Documents/Marie/neuromod/pycortex_venv2/share/pycortex/colormaps

Check to optimize choice from colors offered in pycortex interface
'''
s = '06' # specify subject number here

fs_dir = '/home/labopb/Documents/Marie/neuromod/freesurfer'
pycortex_db_dir = '/home/labopb/Documents/Marie/neuromod/pycortex_venv2/share/pycortex/db'

# Since not all subjects have retinotopy data, but all have
# a ref epi image (used above in step 2), I can load that ref image as a
# overlay placeholder to visualize flat map cuts in pycortex interface
pa = f'{pycortex_db_dir}/S{s}_final/transforms/align_auto_ref/ref.nii.gz'
pa_arr = np.swapaxes(nib.load(pa).get_fdata(), 0, -1)
cmap = 'Retinotopy_RYBCR' # try others?
pa_vol_raw = cortex.Volume(pa_arr, f'S{s}_final', 'align_auto', vmin=np.nanmin (pa_arr), vmax=np.nanmax(pa_arr), cmap=cmap)

# DO this only once (for new flat map)
# importing a new flat map will overwrite the overlay.svg and erase
# any painstakingly drawn ROI boundaries (done w inkscape, see below)!!!
# AT the moment, my best cuts were from the fourth tksurfer attempt,
# but the patches will require some relabelling in their final official version
cortex.freesurfer.import_flat(f'sub-{s}','full_4',['lh','rh'],f'S{s}_final')

# Do this whevever I want to visualize the flat maps and their drawn boundaries
# does not overwrite anything
cortex.webshow(pa_vol_raw, recache=True)


'''
Step 4: draw ROI boundaries in inkscape
'''
s = '01' # specify subject number

fs_dir = '/home/labopb/Documents/Marie/neuromod/freesurfer'
pycortex_db_dir = '/home/labopb/Documents/Marie/neuromod/pycortex_venv2/share/pycortex/db'

retino_path = f'/home/labopb/Documents/Marie/neuromod/test_data/retino/results/s{s[-1]}_pycortex'
floc_roi_path = f'/home/labopb/Documents/Marie/neuromod/test_data/floc/subjects_ROIs/smoothed'
floc_contrast_path = f'/home/labopb/Documents/Marie/neuromod/test_data/floc/floc_contrasts/smoothed'

# path to single parcels (one per ROI)
fLoc_parcel_path = '/home/labopb/Documents/Marie/neuromod/THINGS/floc_events/floc_contrasts/rois_per_parcel/floc_rois'
retino_parcel_path = '/home/labopb/Documents/Marie/neuromod/THINGS/floc_events/floc_contrasts/rois_per_parcel/retino_rois'
kanwisher_group_path = '/home/labopb/Documents/Marie/neuromod/THINGS/floc_events/floc_contrasts/rois_per_parcel/t1w_kanwisher_parcels'


# To draw boundaries in inkscape: prepare ROIs to be loaded into inkscape w pycortex command cortex.add_roi
# NOTE: you can add more than one set of ROIs on the same flat map's overlay.svg file
# (e.g., load a different volume in inkscape w cortex.add_roi, and add layers and save)

# DO NOT DO NOT DO NOT reimport the flat map (step 3) once you've done it once,
# with cortex.freesurfer.import_flat(f'sub-{s}','full_2',['lh','rh'],f'S{s}')
# or it will save over the overlay.svg and erase the drawn ROI boundaries

# Add early visual ROIs V1, V2 and V3
# Data: name vareas_npythy
# ROIS: V1, V2 and V3 under rois -> shapes
vareas = f'{retino_path}/npythy/resampled_varea_goodvox.nii.gz'
vareas_arr = np.swapaxes(nib.load(vareas).get_fdata(), 0, -1)
vareas_arr[vareas_arr == 0] = np.nan
my_vol = cortex.Volume(vareas_arr, f'S{s}_final', 'align_auto', vmin=np.nanmin(vareas_arr), vmax=np.nanmax(vareas_arr), cmap='Retinotopy_RYBCR')
# load volume into inkscape to add ROI layers on overlay.SVG file which can be loaded in pycortex
cortex.add_roi(my_vol, **dict(colorbar_location='left', pixelwise=True, nanmean=True, with_curvature=True))

# Adjustment: mask varea map based on mask that masks out voxels w eccentricities > 12
# load and re-draw V1, V2 and V3
# capped varea map created in a local notebook...
# since those were not tested by our retinotopy task (outside field of view tested)
vareas = f'{retino_path}/npythy/resampled_varea_ecc10Masked_goodvox.nii.gz'
vareas_arr = np.swapaxes(nib.load(vareas).get_fdata(), 0, -1)
vareas_arr[vareas_arr == 0] = np.nan
my_vol = cortex.Volume(vareas_arr, f'S{s}_final', 'align_auto', vmin=np.nanmin(vareas_arr), vmax=np.nanmax(vareas_arr))#, cmap='Retinotopy_RYBCR')
# load volume into inkscape to add ROI layers on overlay.SVG file which can be loaded in pycortex
cortex.add_roi(my_vol, **dict(colorbar_location='left', pixelwise=True, nanmean=True, with_curvature=True))


# ADD: ROIs from conjunction of Kanwisher group parcels and subject's fLoc t scores on relevant contrasts (> 3.72)
# parcels per fLoc ROI: face_FFA, face_OFA, face_pSTS, body_EBA, scene_PPA, scene_MPA, scene_OPA
pname = 'scene_OPA'
#tval = '3.7'
#fp = f'{fLoc_parcel_path}/sub-{s}_fLoc_T1w_{pname}_t{tval}.nii.gz'  # old parcels: redone w smoothed group parcel algo: more tailored
fp = glob.glob(f'{fLoc_parcel_path}/sub-{s}_fLoc_T1w_{pname}_t*goodvox_sm5Rank.nii.gz')
#fp = glob.glob(f'{fLoc_parcel_path}/sub-{s}_fLoc_T1w_{pname}_t*goodvox_sm8Rank.nii.gz')
assert len(fp) == 1
fp = fp[0]
fp_arr = np.swapaxes(nib.load(fp).get_fdata(), 0, -1)
fp_arr[fp_arr <= 0] = np.nan
my_vol = cortex.Volume(fp_arr, f'S{s}_final', 'align_auto', vmin=np.nanmin(fp_arr), vmax=np.nanmax(fp_arr))#, cmap='Retinotopy_RYBCR')

cortex.add_roi(my_vol, **dict(colorbar_location='left', pixelwise=True, nanmean=True, with_curvature=True))


# Contrast parcel-derived ROI boundaries against subject's fLoc contrast maps (faces, places and bodies)
# raw t-scores from fLoc contrasts, t > 3.72
# check: FFA, OFA and pSTS boundaries
#face = f'{floc_contrast_path}/sub-{s}_floc_face-min-object_tscore_T1w.nii.gz' # Kanwisher contrast (old)
face = f'{floc_contrast_path}/sub-{s}_floc_faces_tscore_T1w_sm_goodvox.nii.gz' # NSD / fLoc contrast
face_arr = np.swapaxes(nib.load(face).get_fdata(), 0, -1)
min_val = 3.72
max_val=14.0
face_arr[face_arr < min_val] = np.nan
my_vol = cortex.Volume(face_arr, f'S{s}_final', 'align_auto', vmin=min_val, vmax=max_val)#, cmap='Retinotopy_RYBCR')
#face_arr[face_arr < 4.0] = np.nan
#my_vol = cortex.Volume(face_arr, f'S{s}', 'align_auto', vmin=np.nanmin(face_arr), vmax=np.nanmax(face_arr), cmap='Retinotopy_RYBCR')
cortex.add_roi(my_vol, **dict(colorbar_location='left', pixelwise=True, nanmean=True, with_curvature=True))

# Check EBA
#body = f'{floc_contrast_path}/sub-{s}_floc_body-min-object_tscore_T1w.nii.gz'
body = f'{floc_contrast_path}/sub-{s}_floc_bodies_tscore_T1w_sm_goodvox.nii.gz'
body_arr = np.swapaxes(nib.load(body).get_fdata(), 0, -1)
min_val = 3.72
max_val=14.0
body_arr[body_arr < min_val] = np.nan
my_vol = cortex.Volume(body_arr, f'S{s}_final', 'align_auto', vmin=min_val, vmax=max_val)#, cmap='Retinotopy_RYBCR')
#body_arr[body_arr < 4.0] = np.nan
#my_vol = cortex.Volume(body_arr, f'S{s}', 'align_auto', vmin=np.nanmin(body_arr), vmax=np.nanmax(body_arr), cmap='Retinotopy_RYBCR')
cortex.add_roi(my_vol, **dict(colorbar_location='left', pixelwise=True, nanmean=True, with_curvature=True))

# Check: PPA, OPA, MPA
#scene = f'{floc_contrast_path}/sub-{s}_floc_scene-min-object_tscore_T1w.nii.gz'
scene = f'{floc_contrast_path}/sub-{s}_floc_places_tscore_T1w_sm_goodvox.nii.gz'
scene_arr = np.swapaxes(nib.load(scene).get_fdata(), 0, -1)
min_val = 3.72
max_val=14.0
scene_arr[scene_arr < min_val] = np.nan
my_vol = cortex.Volume(scene_arr, f'S{s}_final', 'align_auto', vmin=min_val, vmax=max_val)#, cmap='Retinotopy_RYBCR')
#scene_arr[scene_arr < 4.0] = np.nan
#my_vol = cortex.Volume(scene_arr, f'S{s}', 'align_auto', vmin=np.nanmin(scene_arr), vmax=np.nanmax(scene_arr), cmap='Retinotopy_RYBCR')
cortex.add_roi(my_vol, **dict(colorbar_location='left', pixelwise=True, nanmean=True, with_curvature=True))

# to visualize in pycortex at any moment;
# can turn rois and their labels on and off in pycortex interface
cortex.webshow(my_vol, recache=True)

# TODO: determine how BEST to get labels to look right in pycortex?
# CAN add text layer in inkscape, but then can't reopen or they disappear... dunno why....



'''
Step 5: WIP
Make decent figures...
- noise ceiling maps
- retinotopy maps, fLoc contrasts
- SVM searchlight?

'''
s = '01'

fp = f'/home/labopb/Documents/Marie/neuromod/THINGS/GLM_single/test_data/output/sub-{s}/sub{s}_T1w_modelD_NoiseCeil_goodvoxMask.nii'
fp_arr = np.swapaxes(nib.load(fp).get_fdata(), 0, -1)
#nc_thresh = 3.0
#fp_arr[fp_arr <= nc_thresh] = np.nan
nc_thresh = 0.0
fp_arr[fp_arr < nc_thresh] = np.nan
my_vol = cortex.Volume(fp_arr, f'S{s}_final', 'align_auto', vmin=0, vmax=35, cmap='terrain')# cmap='Blues_r')
#my_vol = cortex.Volume(fp_arr, f'S{s}_final', 'align_auto', vmin=0, vmax=40, cmap='magma')# cmap='Blues_r')
#my_vol = cortex.Volume(fp_arr, f'S{s}_final', 'align_auto', vmin=np.nanmin(fp_arr), vmax=np.nanmax(fp_arr), cmap='Blues_r')
cortex.webshow(my_vol, recache=True)

# DONT DRAW LIKE THIS; but image can be exported from pycortex and loaded in inkspace for extra edditing (e.g., labelling)
# To create quick images that can be loaded into inkscape:
fig = cortex.quickshow(my_vol, pixelwise=True, colorbar_location='left', nanmean=True, with_curvature=True)
fig.savefig(f'/home/labopb/Documents/Marie/neuromod/THINGS/data_paper/clean_figures/sub-{s}_terrain_cbar.jpg', dpi=600)

# LIMITATION: cannot set up opacity...
# Examples of use: https://python.hotexamples.com/examples/cortex/-/quickshow/python-quickshow-function-examples.html
fig = plt.figure(figsize=(17*2,10*2))
cortex.quickshow(my_vol, pixelwise=True, with_colorbar=False, nanmean=True, with_curvature=True, sampler='trilinear', with_labels=False, with_rois=True, curv_brightness=1.0, dpi=600, fig=fig)
fig.savefig(f'/home/labopb/Documents/Marie/neuromod/THINGS/data_paper/clean_figures/sub-{s}_terrain_test2.png', dpi=600)





s = '01'

fp = f'/home/labopb/Documents/Marie/neuromod/THINGS/GLM_single/test_data/output/sub-{s}/sub{s}_T1w_modelD_NoiseCeil_goodvoxMask.nii'
fp_arr = np.swapaxes(nib.load(fp).get_fdata(), 0, -1)
nc_thresh = 0.0
fp_arr[fp_arr < nc_thresh] = np.nan
my_vol = cortex.Volume(fp_arr, f'S{s}_final', 'align_auto', vmin=-3, vmax=35, cmap='magma')# cmap='Blues_r')

fig = plt.figure(figsize=(17*2,10*2))
cortex.quickshow(my_vol, pixelwise=True, with_colorbar=False, nanmean=True, with_curvature=True, sampler='trilinear', with_labels=False, with_rois=True, curv_brightness=1.0, dpi=300, fig=fig)
fig.savefig(f'/home/labopb/Documents/Marie/neuromod/THINGS/data_paper/clean_figures/sub-{s}_magma_NL.png', dpi=300)


cortex.webshow(my_vol, recache=True)

# DONT DRAW LIKE THIS; but image can be exported from pycortex and loaded in inkspace for extra edditing (e.g., labelling)
# To create quick images that can be loaded into inkscape:
fig = cortex.quickshow(my_vol, pixelwise=True, colorbar_location='left', nanmean=True, with_curvature=True)
fig.savefig(f'/home/labopb/Documents/Marie/neuromod/THINGS/data_paper/clean_figures/sub-{s}_magma_cbar.jpg', dpi=600)







'''
Dev space... / sanity check
Trying stuff out: would unsmoothed fLoc contrasts produce more precise clusters?
Turns out clusters derived from smoothed data are well positioned based on unsmoothed fLoc contrasts
'''

# UNSMOOTHED!!!
# parcels per fLoc ROI: face_FFA, face_OFA, face_pSTS, body_EBA, scene_PPA, scene_MPA, scene_OPA
pname_list = ['face_FFA', 'face_OFA', 'face_pSTS', 'body_EBA', 'scene_PPA', 'scene_MPA', 'scene_OPA']
for pname in pname_list:
    #pname = 'face_FFA'
    fp = glob.glob(f'{fLoc_parcel_path}/unsmooth/sub-{s}_fLoc_T1w_{pname}_t*goodvox_sm5Rank.nii.gz')
    #fp = glob.glob(f'{fLoc_parcel_path}/unsmooth/sub-{s}_fLoc_T1w_{pname}_t*goodvox_sm8Rank.nii.gz')
    assert len(fp) == 1
    fp = fp[0]
    fp_arr = np.swapaxes(nib.load(fp).get_fdata(), 0, -1)
    fp_arr[fp_arr <= 0] = np.nan
    my_vol = cortex.Volume(fp_arr, f'S{s}_final', 'align_auto', vmin=np.nanmin(fp_arr), vmax=np.nanmax(fp_arr))#, cmap='magma')
    cortex.webshow(my_vol, recache=True)

#cortex.add_roi(my_vol, **dict(colorbar_location='left', pixelwise=True, nanmean=True, with_curvature=True))

floc_unsmooth_contrast_path = f'/home/labopb/Documents/Marie/neuromod/test_data/floc/floc_contrasts/unsmoothed'

face = f'{floc_unsmooth_contrast_path}/sub-{s}_floc_faces_tscore_T1w_goodvox.nii.gz' # NSD / fLoc contrast
face_arr = np.swapaxes(nib.load(face).get_fdata(), 0, -1)
min_val = 0 #3.72
max_val=14.0
face_arr[face_arr < min_val] = np.nan
my_vol = cortex.Volume(face_arr, f'S{s}_final', 'align_auto', vmin=min_val, vmax=max_val, cmap='magma')
cortex.webshow(my_vol, recache=True)

body = f'{floc_unsmooth_contrast_path}/sub-{s}_floc_bodies_tscore_T1w_goodvox.nii.gz'
body_arr = np.swapaxes(nib.load(body).get_fdata(), 0, -1)
min_val = 0 #3.72
max_val=14.0
body_arr[body_arr < min_val] = np.nan
my_vol = cortex.Volume(body_arr, f'S{s}_final', 'align_auto', vmin=min_val, vmax=max_val, cmap='magma')
cortex.webshow(my_vol, recache=True)

scene = f'{floc_unsmooth_contrast_path}/sub-{s}_floc_places_tscore_T1w_goodvox.nii.gz'
scene_arr = np.swapaxes(nib.load(scene).get_fdata(), 0, -1)
min_val = 0 #3.72
max_val=14.0
scene_arr[scene_arr < min_val] = np.nan
my_vol = cortex.Volume(scene_arr, f'S{s}_final', 'align_auto', vmin=min_val, vmax=max_val, cmap='magma')
cortex.webshow(my_vol, recache=True)







'''
OLD notes, including some on launching cutting w Blender
Step 0 (on beluga): do this once
generate mean epi image from one run of bold data (epi)
as reference for transform from T1w functional space into freesurfer space
'''
out_dir_refimg = '/project/rrg-pbellec/mstlaure/retino_analysis/results/ref_img'
slist = ['01', '02', '03', '04', '05', '06']

for s in slist:
    #create mean reference image in T1w space to create the transform
    # s1, s2, s3 (retino run, T1w)
    bold_path = f'/project/rrg-pbellec/mstlaure/retino_analysis/data/temp_bold/sub-{s}_ses-004_task-rings_space-T1w_desc-preproc_part-mag_bold.nii.gz'
    # s4, s5, s6 (*friends run, T1w)
    #bold_path = '/project/rrg-pbellec/mstlaure/deepgaze_mr/data/friends_T1w/sub-04/ses-010/func/sub-04_ses-010_task-s01e19a_space-T1w_desc-preproc_bold.nii.gz'
    #bold_path = '/project/rrg-pbellec/mstlaure/deepgaze_mr/data/friends_T1w/sub-05/ses-010/func/sub-05_ses-010_task-s02e19a_space-T1w_desc-preproc_bold.nii.gz'
    #bold_path = '/project/rrg-pbellec/mstlaure/deepgaze_mr/data/friends_T1w/sub-06/ses-010/func/sub-06_ses-010_task-s02e16a_space-T1w_desc-preproc_bold.nii.gz'
    run_epi = nib.load(bold_path)
    mean_epi = mean_img(run_epi)
    nib.save(mean_epi, os.path.join(out_dir_refimg, f'sub-{s}_ref_epi.nii.gz'))


'''
Step 1: do this once
Import local freesurfer data (surfaces and volumes) into pycortex database,
here: /home/labopb/Documents/Marie/neuromod/pycortex_venv2/share/pycortex/db

IMPORTANT: before launching python, set subjects_dir to where the local freesurfer data live
SUBJECTS_DIR="/home/labopb/Documents/Marie/neuromod/freesurfer"

# Local venv (laptop): Documents/Marie/neuromod/pycortex_venv2
'''
fs_dir = '/home/labopb/Documents/Marie/neuromod/freesurfer'
#cmap = ???
# https://gallantlab.github.io/pycortex/colormaps.html

slist = ['01', '02', '03', '04', '05', '06']

for s in slist:
    cortex.freesurfer.import_subj(fs_subject=f'sub-{s}',
                                  cx_subject=f'S{s}',
                                  freesurfer_subject_dir=fs_dir,
                                  )

'''
Step 2: do this once

Generate transform from functional T1w space into freesurfer space using mean reference epi image ref.nii.gz

IMPORTANT:
First save mean epi (from beluga) locally in pycortex database under S{s}/transforms/align_auto_ref as "ref.nii.gz"

Before launching python, set subjects_dir to where the local freesurfer data live
SUBJECTS_DIR="/home/labopb/Documents/Marie/neuromod/freesurfer"

Also: ANNOYING limitation!!
cortex.align.automatic function requires the SAME directory name in Freesurfer
and in pycortex db for the same subject in order to work...

Ugly workaround: within my freesurfer subject_dir (/home/labopb/Documents/Marie/neuromod/freesurfer)
I made copies of subjects' directories and renamed them w the pycortex name, so I have both names in SUBJECTS_DIR...

SUBJECTS_DIR="/home/labopb/Documents/Marie/neuromod/freesurfer"
# Local venv (laptop): Documents/Marie/neuromod/pycortex_venv2
'''
# equal to cortex.database.default_filestore (when type in ipython)
pycortex_db_dir = '/home/labopb/Documents/Marie/neuromod/pycortex_venv2/share/pycortex/db'

for s in slist:
    cortex.align.automatic(
        #f'sub-{s}', 'align_auto',
        f'S{s}', 'align_auto',
        #os.path.join(cortex.database.default_filestore,
        os.path.join(pycortex_db_dir,
                     f'S{s}', 'transforms', 'align_auto_ref', 'ref.nii.gz')
    )

'''
Step 3: Load data into pycortex (as volume or as vertex),
and cut flat maps in blender!!

SUBJECTS_DIR="/home/labopb/Documents/Marie/neuromod/freesurfer"
# Local venv (laptop): Documents/Marie/neuromod/pycortex_venv2

# For color maps:
I think I can use any of the following color maps in my pycortex repo (see here):
/home/labopb/Documents/Marie/neuromod/pycortex_venv2/share/pycortex/colormaps

'''
for s in slist:

    retino_path = f'/home/labopb/Documents/Marie/neuromod/test_data/retino/results/s{s[-1]}_pycortex'

    # load prf volume to guide cutting along calcarine sulcus
    # Example 1: volume files in freesurfer space
    pa_f = f'{retino_path}/npythy/inferred_angle.nii.gz'
    va_f = f'{retino_path}/npythy/inferred_varea.nii.gz'
    ex_f = f'{retino_path}/npythy/inferred_eccen.nii.gz'
    pa_arr = np.swapaxes(nib.load(pa_f).get_fdata(), 0, -1)
    va_arr = np.swapaxes(nib.load(va_f).get_fdata(), 0, -1)
    ex_arr = np.swapaxes(nib.load(ex_f).get_fdata(), 0, -1)
    # https://gallantlab.github.io/pycortex/colormaps.html
    pa_vol = cortex.Volume(pa_arr, f'S{s}', 'identity', vmin=np.nanmin(pa_arr), vmax=np.nanmax(pa_arr), cmap='Retinotopy_RYBCR')
    va_vol = cortex.Volume(va_arr, f'S{s}', 'identity', vmin=np.nanmin(va_arr), vmax=np.nanmax(va_arr), cmap='nipy_spectral')
    ex_vol = cortex.Volume(ex_arr, f'S{s}', 'identity', vmin=np.nanmin(ex_arr), vmax=np.nanmax(ex_arr), cmap='plasma')

    # Example 2: volume files in T1w functional space: need transform created in step 2
    # step needed for most functional data projected in pycortex, e.g., GLMsingle, R2, noise ceiling maps...
    pa_f_rs = f'{retino_path}/npythy/resampled_angle.nii.gz'
    va_f_rs = f'{retino_path}/npythy/resampled_varea.nii.gz'
    ex_f_rs = f'{retino_path}/npythy/resampled_eccen.nii.gz'
    pa_arr_rs = np.swapaxes(nib.load(pa_f_rs).get_fdata(), 0, -1)
    va_arr_rs = np.swapaxes(nib.load(va_f_rs).get_fdata(), 0, -1)
    ex_arr_rs = np.swapaxes(nib.load(ex_f_rs).get_fdata(), 0, -1)
    # https://gallantlab.github.io/pycortex/colormaps.html
    pa_vol_rs = cortex.Volume(pa_arr_rs, f'S{s}', 'align_auto', vmin=np.nanmin(pa_arr_rs), vmax=np.nanmax(pa_arr_rs), cmap='Retinotopy_RYBCR')
    va_vol_rs = cortex.Volume(va_arr_rs, f'S{s}', 'align_auto', vmin=np.nanmin(va_arr_rs), vmax=np.nanmax(va_arr_rs), cmap='nipy_spectral')
    ex_vol_rs = cortex.Volume(ex_arr_rs, f'S{s}', 'align_auto', vmin=np.nanmin(ex_arr_rs), vmax=np.nanmax(ex_arr_rs), cmap='Retinotopy_RYBCR')

    # load volume as vertex,
    sub_retinotopy=cortex.Dataset()
    sub_retinotopy.description="retinotopy_flat"

    sub_retinotopy.views['polangle']=pa_vol_rs
    sub_retinotopy.views['eccentricity']=ex_vol_rs


    # raw pRF output (before neuropythy)
    pa = f'{retino_path}/analyzePRF/sub-{s}_fullbrain_ang.nii.gz'
    eccen = f'{retino_path}/analyzePRF/sub-{s}_fullbrain_ecc.nii.gz'
    rfsize = f'{retino_path}/analyzePRF/sub-{s}_fullbrain_rfsize.nii.gz'
    pa_arr = np.swapaxes(nib.load(pa).get_fdata(), 0, -1)
    rfs_arr = np.swapaxes(nib.load(rfsize).get_fdata(), 0, -1)
    ex_arr = np.swapaxes(nib.load(eccen).get_fdata(), 0, -1)
    # https://gallantlab.github.io/pycortex/colormaps.html
    pa_vol_raw = cortex.Volume(pa_arr, f'S{s}', 'align_auto', vmin=np.nanmin(pa_arr), vmax=np.nanmax(pa_arr), cmap='Retinotopy_RYBCR')
    rfs_vol_raw = cortex.Volume(rfs_arr, f'S{s}', 'align_auto', vmin=np.nanmin(rfs_arr), vmax=np.nanmax(rfs_arr), cmap='nipy_spectral')
    ex_vol_raw = cortex.Volume(ex_arr, f'S{s}', 'align_auto', vmin=np.nanmin(ex_arr), vmax=np.nanmax(ex_arr), cmap='Retinotopy_RYBCR')

    # load volume as vertex,
    sub_retinotopy=cortex.Dataset()
    sub_retinotopy.description="retinotopy_flat"

    sub_retinotopy.views['polangle']=pa_vol_raw
    sub_retinotopy.views['eccentricity']=ex_vol_raw

    # Opens blender -> set manual cuts, save and close. Terminal prompt will ask you to proceed, then wait 1h
    # Aternative 1: load data as Volumes (I honestly don't know how to display those in Blender interface...)
    cortex.segment.cut_surface(
                f'S{s}', 'rh',
                name='blender_flat',
                #name=f'S{s}_rh_flatten',
                fs_subject=f'sub-{s}',
                freesurfer_subject_dir=fs_dir,
                do_import_subject=True,
                data=sub_retinotopy,
                #data=pa_vol,
                )


# To visualize flat map in subject with no retinotopy data,
# use averaged epi used for transformation from T1w volume space
# to freesurfer surface space as overlay
fs_dir = '/home/labopb/Documents/Marie/neuromod/freesurfer'
pycortex_db_dir = '/home/labopb/Documents/Marie/neuromod/pycortex_venv2/share/pycortex/db'
s = '06'

pa = f'{pycortex_db_dir}/S{s}/transforms/align_auto_ref/ref.nii.gz'
pa_arr = np.swapaxes(nib.load(pa).get_fdata(), 0, -1)
pa_vol_raw = cortex.Volume(pa_arr, f'S{s}', 'align_auto', vmin=np.nanmin (pa_arr), vmax=np.nanmax(pa_arr), cmap='Retinotopy_RYBCR')
cortex.freesurfer.import_flat(f'sub-{s}','full_4',['lh','rh'],f'S{s}')
cortex.webshow(pa_vol_raw, recache=True)

pa = f'{pycortex_db_dir}/sub-{s}_f1/transforms/align_auto_ref/ref.nii.gz'
pa_arr = np.swapaxes(nib.load(pa).get_fdata(), 0, -1)
pa_vol_raw = cortex.Volume(pa_arr, f'sub-{s}_f1', 'align_auto', vmin=np.nanmin (pa_arr), vmax=np.nanmax(pa_arr), cmap='Retinotopy_RYBCR')
cortex.freesurfer.import_flat(f'sub-{s}_f1','full_1',['lh','rh'],f'sub-{s}_f1')
cortex.webshow(pa_vol_raw, recache=True)

pa = f'{pycortex_db_dir}/sub-{s}_f2/transforms/align_auto_ref/ref.nii.gz'
pa_arr = np.swapaxes(nib.load(pa).get_fdata(), 0, -1)
pa_vol_raw = cortex.Volume(pa_arr, f'sub-{s}_f2', 'align_auto', vmin=np.nanmin (pa_arr), vmax=np.nanmax(pa_arr), cmap='Retinotopy_RYBCR')
cortex.freesurfer.import_flat(f'sub-{s}_f2','full_2',['lh','rh'],f'sub-{s}_f2')
cortex.webshow(pa_vol_raw, recache=True)


'''
step ?
Import flat maps from freesurfer into pycortex

Figure out name issue...
'''
cortex.freesurfer.import_flat(f'sub-{s}','retinotopy_flat',['lh','rh'],f'S{s}')

cortex.webshow(ex_vol_rs, recache=True)


'''
VERY loose notes: how to visualize ROIs on current flat maps...
'''

fs_dir = '/home/labopb/Documents/Marie/neuromod/freesurfer'
pycortex_db_dir = '/home/labopb/Documents/Marie/neuromod/pycortex_venv2/share/pycortex/db'

s = '01'
retino_path = f'/home/labopb/Documents/Marie/neuromod/test_data/retino/results/s{s[-1]}_pycortex'
floc_roi_path = f'/home/labopb/Documents/Marie/neuromod/test_data/floc/subjects_ROIs/smoothed'
floc_contrast_path = f'/home/labopb/Documents/Marie/neuromod/test_data/floc/floc_contrasts/smoothed'

# path to single parcels (ne per ROI)
fLoc_parcel_path = '/home/labopb/Documents/Marie/neuromod/THINGS/floc_events/floc_contrasts/rois_per_parcel/floc_rois'
retino_parcel_path = '/home/labopb/Documents/Marie/neuromod/THINGS/floc_events/floc_contrasts/rois_per_parcel/retino_rois'

kanwisher_group_path = '/home/labopb/Documents/Marie/neuromod/THINGS/floc_events/floc_contrasts/rois_per_parcel/t1w_kanwisher_parcels'

# do this only once, or it will save over the overlay.svg and erase the drawn ROI boundaries
#cortex.freesurfer.import_flat(f'sub-{s}','full_2',['lh','rh'],f'S{s}')
#cortex.freesurfer.import_flat(f'sub-{s}','full_3',['lh','rh'],f'S{s}') # for sub-03


# parcels per retino ROI: V1, V2, V3
pname = 'V2'
fp = f'{retino_parcel_path}/sub-{s}_resampled_{pname}_interp-nn_goodvox.nii.gz'
fp_arr = np.swapaxes(nib.load(fp).get_fdata(), 0, -1)
fp_arr[fp_arr <= 0] = np.nan
my_vol = cortex.Volume(fp_arr, f'S{s}', 'align_auto', vmin=np.nanmin(fp_arr), vmax=np.nanmax(fp_arr), cmap='Retinotopy_RYBCR')

cortex.webshow(my_vol, recache=True)


# parcels per fLoc ROI: face_FFA, face_OFA, face_pSTS, body_EBA, scene_PPA, scene_MPA, scene_OPA
pname = 'scene_OPA'
tval = '3.7'
fp = f'{fLoc_parcel_path}/sub-{s}_fLoc_T1w_{pname}_t{tval}.nii.gz'
fp_arr = np.swapaxes(nib.load(fp).get_fdata(), 0, -1)
fp_arr[fp_arr <= 0] = np.nan
my_vol = cortex.Volume(fp_arr, f'S{s}', 'align_auto', vmin=np.nanmin(fp_arr), vmax=np.nanmax(fp_arr))#, cmap='Retinotopy_RYBCR')

# for inkscape drawing
#cortex.add_roi(my_vol, **dict(colorbar_location='left', pixelwise=True, nanmean=True, with_curvature=True))

cortex.webshow(my_vol, recache=True)

# ENHANCED parcels per fLoc ROI: face_FFA, face_OFA, face_pSTS, body_EBA, scene_PPA, scene_MPA, scene_OPA
# group parcel masks smoothed, then top contrast voxels picked within wider areas;
# number of voxels capped to original number of voxels in parcel
#fp = glob.glob(f'{fLoc_parcel_path}/sub-{s}_fLoc_T1w_{pname}_t*goodvox_sm12Rank.nii.gz')
#fp = glob.glob(f'{fLoc_parcel_path}/sub-{s}_fLoc_T1w_{pname}_t*goodvox_sm16Rank.nii.gz')
#fp = glob.glob(f'{fLoc_parcel_path}/sub-{s}_fLoc_T1w_{pname}_t*goodvox_sm20Rank.nii.gz')
fp = glob.glob(f'{fLoc_parcel_path}/sub-{s}_fLoc_T1w_{pname}_t*goodvox_sm5Rank.nii.gz')
#fp = glob.glob(f'{fLoc_parcel_path}/sub-{s}_fLoc_T1w_{pname}_t*goodvox_sm8Rank.nii.gz')
assert len(fp) == 1
fp = fp[0]
fp_arr = np.swapaxes(nib.load(fp).get_fdata(), 0, -1)
fp_arr[fp_arr <= 0] = np.nan
my_vol = cortex.Volume(fp_arr, f'S{s}', 'align_auto', vmin=np.nanmin(fp_arr), vmax=np.nanmax(fp_arr))#, cmap='Retinotopy_RYBCR')
cortex.webshow(my_vol, recache=True)

fp = glob.glob(f'{fLoc_parcel_path}/sub-{s}_fLoc_T1w_{pname}_t*goodvox_sm5Rank_oneCluster.nii.gz')
assert len(fp) == 1
fp = fp[0]
fp_arr = np.swapaxes(nib.load(fp).get_fdata(), 0, -1)
fp_arr[fp_arr <= 0] = np.nan
my_vol = cortex.Volume(fp_arr, f'S{s}', 'align_auto', vmin=np.nanmin(fp_arr), vmax=np.nanmax(fp_arr))#, cmap='Retinotopy_RYBCR')
cortex.webshow(my_vol, recache=True)


# just the kanwisher group derived contrasts warped to subject's t1w space, not looking at t-scores
# note: resampled (in jupyter notebook) to match other images in functional T1w space
fp = f'{kanwisher_group_path}/sub-{s}_{pname}_mni2t1w_rs_raw.nii'
fp_arr = np.swapaxes(nib.load(fp).get_fdata(), 0, -1)
fp_arr[fp_arr <= 0] = np.nan
my_vol = cortex.Volume(fp_arr, f'S{s}', 'align_auto', vmin=np.nanmin(fp_arr), vmax=np.nanmax(fp_arr))#, cmap='Retinotopy_RYBCR')
cortex.webshow(my_vol, recache=True)

fp = f'{kanwisher_group_path}/sub-{s}_{pname}_mni2t1w_rs.nii'
fp_arr = np.swapaxes(nib.load(fp).get_fdata(), 0, -1)
fp_arr[fp_arr <= 0] = np.nan
my_vol = cortex.Volume(fp_arr, f'S{s}', 'align_auto', vmin=np.nanmin(fp_arr), vmax=np.nanmax(fp_arr))#, cmap='Retinotopy_RYBCR')
cortex.webshow(my_vol, recache=True)

# t-scores
face = f'{floc_contrast_path}/sub-{s}_floc_face-min-object_tscore_T1w.nii.gz'
face_arr = np.swapaxes(nib.load(face).get_fdata(), 0, -1)
min_val = 3.7
max_val=14.0
face_arr[face_arr < min_val] = np.nan
my_vol = cortex.Volume(face_arr, f'S{s}', 'align_auto', vmin=min_val, vmax=max_val)#, cmap='Retinotopy_RYBCR')
cortex.webshow(my_vol, recache=True)

body = f'{floc_contrast_path}/sub-{s}_floc_body-min-object_tscore_T1w.nii.gz'
body_arr = np.swapaxes(nib.load(body).get_fdata(), 0, -1)
min_val = 3.7
max_val=14.0
body_arr[body_arr < min_val] = np.nan
my_vol = cortex.Volume(body_arr, f'S{s}', 'align_auto', vmin=min_val, vmax=max_val)#, cmap='Retinotopy_RYBCR')
cortex.webshow(my_vol, recache=True)

scene = f'{floc_contrast_path}/sub-{s}_floc_scene-min-object_tscore_T1w.nii.gz'
scene_arr = np.swapaxes(nib.load(scene).get_fdata(), 0, -1)
min_val = 3.7
max_val=14.0
scene_arr[scene_arr < min_val] = np.nan
my_vol = cortex.Volume(scene_arr, f'S{s}', 'align_auto', vmin=min_val, vmax=max_val)#, cmap='Retinotopy_RYBCR')
cortex.webshow(my_vol, recache=True)






# post neuropythy retinotopy data
pa_f_rs = f'{retino_path}/npythy/resampled_angle_goodvox.nii.gz'
pa_arr_rs = np.swapaxes(nib.load(pa_f_rs).get_fdata(), 0, -1)
pa_arr_rs[pa_arr_rs == 0] = np.nan
my_vol = cortex.Volume(pa_arr_rs, f'S{s}', 'align_auto', vmin=np.nanmin(pa_arr_rs), vmax=np.nanmax(pa_arr_rs), cmap='Retinotopy_RYBCR')
cortex.webshow(my_vol, recache=True)

va_f_rs = f'{retino_path}/npythy/resampled_varea_goodvox.nii.gz'
va_arr_rs = np.swapaxes(nib.load(va_f_rs).get_fdata(), 0, -1)
va_arr_rs[va_arr_rs == 0] = np.nan
my_vol = cortex.Volume(va_arr_rs, f'S{s}', 'align_auto', vmin=np.nanmin(va_arr_rs), vmax=np.nanmax(va_arr_rs), cmap='nipy_spectral')
cortex.webshow(my_vol, recache=True)

ex_f_rs = f'{retino_path}/npythy/resampled_eccen_goodvox.nii.gz'
ex_arr_rs = np.swapaxes(nib.load(ex_f_rs).get_fdata(), 0, -1)
ex_arr_rs[ex_arr_rs == 0] = np.nan
my_vol = cortex.Volume(ex_arr_rs, f'S{s}', 'align_auto', vmin=np.nanmin(ex_arr_rs), vmax=np.nanmax(ex_arr_rs), cmap='Retinotopy_RYBCR')
cortex.webshow(my_vol, recache=True)

# pre neuropythy (raw) retinotopy data
pa = f'{retino_path}/analyzePRF/sub-{s}_fullbrain_ang_goodvox.nii.gz'
pa_arr = np.swapaxes(nib.load(pa).get_fdata(), 0, -1)
#pa_arr[pa_arr == 0] = np.nan
my_vol = cortex.Volume(pa_arr, f'S{s}', 'align_auto', vmin=np.nanmin(pa_arr), vmax=np.nanmax(pa_arr), cmap='Retinotopy_RYBCR')
cortex.webshow(my_vol, recache=True)

pa = f'{retino_path}/analyzePRF/sub-{s}_fullbrain_angCompass_goodvox.nii.gz'
pa_arr = np.swapaxes(nib.load(pa).get_fdata(), 0, -1)
#pa_arr[pa_arr == 0] = np.nan
my_vol = cortex.Volume(pa_arr, f'S{s}', 'align_auto', vmin=np.nanmin(pa_arr), vmax=np.nanmax(pa_arr), cmap='Retinotopy_RYBCR')
cortex.webshow(my_vol, recache=True)

eccen = f'{retino_path}/analyzePRF/sub-{s}_fullbrain_ecc_goodvox.nii.gz'
ex_arr = np.swapaxes(nib.load(eccen).get_fdata(), 0, -1)
#ex_arr[ex_arr == 0] = np.nan
my_vol = cortex.Volume(ex_arr, f'S{s}', 'align_auto', vmin=np.nanmin(ex_arr), vmax=np.nanmax(ex_arr), cmap='Retinotopy_RYBCR')
cortex.webshow(my_vol, recache=True)

# eccentricity, capped at 10 deg vis angle (area tested)
eccen = f'{retino_path}/analyzePRF/sub-{s}_fullbrain_eccCAP10DEG_goodvox.nii.gz'
ex_arr = np.swapaxes(nib.load(eccen).get_fdata(), 0, -1)
#ex_arr[ex_arr == 0] = np.nan
my_vol = cortex.Volume(ex_arr, f'S{s}', 'align_auto', vmin=np.nanmin(ex_arr), vmax=np.nanmax(ex_arr), cmap='Retinotopy_RYBCR')
cortex.webshow(my_vol, recache=True)

# eccentricity mask: voxels w less than 10 deg vis angle eccentricity (area tested)
eccen = f'{retino_path}/analyzePRF/sub-{s}_fullbrain_eccMask10_goodvox.nii.gz'
ex_arr = np.swapaxes(nib.load(eccen).get_fdata(), 0, -1)
ex_arr[ex_arr == 0] = np.nan
my_vol = cortex.Volume(ex_arr, f'S{s}', 'align_auto', vmin=np.nanmin(ex_arr), vmax=np.nanmax(ex_arr), cmap='Retinotopy_RYBCR')
cortex.webshow(my_vol, recache=True)

rfsize = f'{retino_path}/analyzePRF/sub-{s}_fullbrain_rfsize_goodvox.nii.gz'
rfs_arr = np.swapaxes(nib.load(rfsize).get_fdata(), 0, -1)
rfs_arr[rfs_arr == 0] = np.nan
my_vol = cortex.Volume(rfs_arr, f'S{s}', 'align_auto', vmin=np.nanmin(rfs_arr), vmax=np.nanmax(rfs_arr), cmap='nipy_spectral')
cortex.webshow(my_vol, recache=True)

r2 = f'{retino_path}/analyzePRF/sub-{s}_fullbrain_R2_goodvox.nii.gz'
r2_arr = np.swapaxes(nib.load(r2).get_fdata(), 0, -1)
r2_arr[r2_arr == 0] = np.nan
my_vol = cortex.Volume(r2_arr, f'S{s}', 'align_auto', vmin=np.nanmin(r2_arr), vmax=np.nanmax(r2_arr), cmap='nipy_spectral')
cortex.webshow(my_vol, recache=True)

x = f'{retino_path}/analyzePRF/sub-{s}_fullbrain_x_goodvox.nii.gz'
x_arr = np.swapaxes(nib.load(x).get_fdata(), 0, -1)
#x_arr[x_arr == 0] = np.nan
my_vol = cortex.Volume(x_arr, f'S{s}', 'align_auto', vmin=np.nanmin(x_arr), vmax=np.nanmax(x_arr), cmap='nipy_spectral')
cortex.webshow(my_vol, recache=True)

y = f'{retino_path}/analyzePRF/sub-{s}_fullbrain_y_goodvox.nii.gz'
y_arr = np.swapaxes(nib.load(y).get_fdata(), 0, -1)
#y_arr[y_arr == 0] = np.nan
my_vol = cortex.Volume(y_arr, f'S{s}', 'align_auto', vmin=np.nanmin(y_arr), vmax=np.nanmax(y_arr), cmap='nipy_spectral')
cortex.webshow(my_vol, recache=True)

# Kanwisher + floc contrast ROIs
face = f'{floc_roi_path}/s{s}_T1w_fLoc_face-min-object_tscore_t2.5.nii.gz'
face_arr = np.swapaxes(nib.load(face).get_fdata(), 0, -1)
face_arr[face_arr == 0] = np.nan
my_vol = cortex.Volume(face_arr, f'S{s}', 'align_auto', vmin=np.nanmin(face_arr), vmax=np.nanmax(face_arr), cmap='Retinotopy_RYBCR')

body = f'{floc_roi_path}/s{s}_T1w_fLoc_body-min-object_tscore_t2.5.nii.gz'
body_arr = np.swapaxes(nib.load(body).get_fdata(), 0, -1)
body_arr[body_arr == 0] = np.nan
my_vol = cortex.Volume(body_arr, f'S{s}', 'align_auto', vmin=np.nanmin(body_arr), vmax=np.nanmax(body_arr), cmap='Retinotopy_RYBCR')

scene = f'{floc_roi_path}/s{s}_T1w_fLoc_scene-min-object_tscore_t2.5.nii.gz'
scene_arr = np.swapaxes(nib.load(scene).get_fdata(), 0, -1)
scene_arr[scene_arr == 0] = np.nan
my_vol = cortex.Volume(scene_arr, f'S{s}', 'align_auto', vmin=np.nanmin(scene_arr), vmax=np.nanmax(scene_arr), cmap='Retinotopy_RYBCR')


# raw t-scores from fLoc contrasts
face = f'{floc_contrast_path}/sub-{s}_floc_face-min-object_tscore_T1w.nii.gz'
face_arr = np.swapaxes(nib.load(face).get_fdata(), 0, -1)
min_val = 4.0
max_val=14.0
face_arr[face_arr < min_val] = np.nan
my_vol = cortex.Volume(face_arr, f'S{s}', 'align_auto', vmin=min_val, vmax=max_val)#, cmap='Retinotopy_RYBCR')

cortex.add_roi(my_vol, **dict(colorbar_location='left', pixelwise=True, nanmean=True, with_curvature=True))


body = f'{floc_contrast_path}/sub-{s}_floc_body-min-object_tscore_T1w.nii.gz'
body_arr = np.swapaxes(nib.load(body).get_fdata(), 0, -1)
min_val = 4.0
max_val=14.0
body_arr[body_arr < min_val] = np.nan
my_vol = cortex.Volume(body_arr, f'S{s}', 'align_auto', vmin=min_val, vmax=max_val)#, cmap='Retinotopy_RYBCR')
#body_arr[body_arr < 4.0] = np.nan
#my_vol = cortex.Volume(body_arr, f'S{s}', 'align_auto', vmin=np.nanmin(body_arr), vmax=np.nanmax(body_arr), cmap='Retinotopy_RYBCR')
cortex.add_roi(my_vol, **dict(colorbar_location='left', pixelwise=True, nanmean=True, with_curvature=True))

scene = f'{floc_contrast_path}/sub-{s}_floc_scene-min-object_tscore_T1w.nii.gz'
scene_arr = np.swapaxes(nib.load(scene).get_fdata(), 0, -1)
min_val = 4.0
max_val=14.0
scene_arr[scene_arr < min_val] = np.nan
my_vol = cortex.Volume(scene_arr, f'S{s}', 'align_auto', vmin=min_val, vmax=max_val)#, cmap='Retinotopy_RYBCR')
#scene_arr[scene_arr < 4.0] = np.nan
#my_vol = cortex.Volume(scene_arr, f'S{s}', 'align_auto', vmin=np.nanmin(scene_arr), vmax=np.nanmax(scene_arr), cmap='Retinotopy_RYBCR')
cortex.add_roi(my_vol, **dict(colorbar_location='left', pixelwise=True, nanmean=True, with_curvature=True))

cortex.webshow(my_vol, recache=True)


'''
DRAWING IN INKSCAPE!!
Notes on drawing in inkscape:
Once volume is loaded, add ROIs under roi/shape/V1, etc: one new layer per ROI

Use the pencil to draw around;
https://inkscape-manuals.readthedocs.io/en/latest/pencil-tool.html
https://github.com/gallantlab/pycortex/issues/256

'''
# DONT DRAW LIKE THIS; but image can be exported from pycortex and loaded in inkspace for extra edditing (e.g., labelling)
# To create quick images that can be loaded into inkscape:
fig = cortex.quickshow(my_vol, pixelwise=True, colorbar_location='left', nanmean=True, with_curvature=True)
fig.savefig('/home/labopb/Documents/Marie/neuromod/THINGS/floc_events/floc_contrasts/inkscape_maps/test.jpg')


# To draw boundaries in inkscape: prepare ROIs to be loaded into inkscape w pycortex command
# NOTE: you can add more than one set of ROIs on the same flat map's overlay.svg file
# (e.g., load a different volume in inkscape w cortex.add_roi, and add layers and save)

# DO NOT DO NOT DO NOT reimport the flat map once you've done it once,
# with cortex.freesurfer.import_flat(f'sub-{s}','full_2',['lh','rh'],f'S{s}')
# or it will save over the overlay.svg and erase the drawn ROI boundaries

# Add early visual ROIs V1, V2 and V3
# Data: name vareas_npythy
# ROIS: V1, V2 and V3 under rois -> shaoes
vareas = f'{retino_path}/npythy/resampled_varea.nii.gz'
vareas_arr = np.swapaxes(nib.load(vareas).get_fdata(), 0, -1)
vareas_arr[vareas_arr == 0] = np.nan
my_vol = cortex.Volume(vareas_arr, f'S{s}', 'align_auto', vmin=np.nanmin(vareas_arr), vmax=np.nanmax(vareas_arr), cmap='Retinotopy_RYBCR')
# load volume into inkscape to add ROI layers on overlay.SVG file which can be loaded in pycortex
cortex.add_roi(my_vol, **dict(colorbar_location='left', pixelwise=True, nanmean=True, with_curvature=True))

# ADD: ROIs from conjunction of Kanwisher group parcels and subject's fLoc t scores on relevant contrasts (> 3.7)
# parcels per fLoc ROI: face_FFA, face_OFA, face_pSTS, body_EBA, scene_PPA, scene_MPA, scene_OPA
# Data: FFA_t3.7, etc.
# rois _> shape: FFA, etc
pname = 'scene_OPA'
tval = '3.7'
fp = f'{fLoc_parcel_path}/sub-{s}_fLoc_T1w_{pname}_t{tval}.nii.gz'
fp_arr = np.swapaxes(nib.load(fp).get_fdata(), 0, -1)
fp_arr[fp_arr <= 0] = np.nan
my_vol = cortex.Volume(fp_arr, f'S{s}', 'align_auto', vmin=np.nanmin(fp_arr), vmax=np.nanmax(fp_arr))#, cmap='Retinotopy_RYBCR')

cortex.add_roi(my_vol, **dict(colorbar_location='left', pixelwise=True, nanmean=True, with_curvature=True))

# REFINE parcel-derived ROIs w boundaries based on subject's fLoc contrast maps
# raw t-scores from fLoc contrasts, t > 4.0
# Redo: FFA, OFA, pSTS (no new layer)
# Data: face_vs_obj_t4
face = f'{floc_contrast_path}/sub-{s}_floc_face-min-object_tscore_T1w.nii.gz'
face_arr = np.swapaxes(nib.load(face).get_fdata(), 0, -1)
min_val = 4.0
max_val=14.0
face_arr[face_arr < min_val] = np.nan
my_vol = cortex.Volume(face_arr, f'S{s}', 'align_auto', vmin=min_val, vmax=max_val)#, cmap='Retinotopy_RYBCR')

cortex.add_roi(my_vol, **dict(colorbar_location='left', pixelwise=True, nanmean=True, with_curvature=True))

# Redo: EBA (no new layer)
# Data: body_vs_obj_t4
body = f'{floc_contrast_path}/sub-{s}_floc_body-min-object_tscore_T1w.nii.gz'
body_arr = np.swapaxes(nib.load(body).get_fdata(), 0, -1)
min_val = 4.0
max_val=14.0
body_arr[body_arr < min_val] = np.nan
my_vol = cortex.Volume(body_arr, f'S{s}', 'align_auto', vmin=min_val, vmax=max_val)#, cmap='Retinotopy_RYBCR')
#body_arr[body_arr < 4.0] = np.nan
#my_vol = cortex.Volume(body_arr, f'S{s}', 'align_auto', vmin=np.nanmin(body_arr), vmax=np.nanmax(body_arr), cmap='Retinotopy_RYBCR')
cortex.add_roi(my_vol, **dict(colorbar_location='left', pixelwise=True, nanmean=True, with_curvature=True))

# Redo: PPA, OPA, MPA (no new layer)
# Data: scene_vs_obj_t4
scene = f'{floc_contrast_path}/sub-{s}_floc_scene-min-object_tscore_T1w.nii.gz'
scene_arr = np.swapaxes(nib.load(scene).get_fdata(), 0, -1)
min_val = 4.0
max_val=14.0
scene_arr[scene_arr < min_val] = np.nan
my_vol = cortex.Volume(scene_arr, f'S{s}', 'align_auto', vmin=min_val, vmax=max_val)#, cmap='Retinotopy_RYBCR')
#scene_arr[scene_arr < 4.0] = np.nan
#my_vol = cortex.Volume(scene_arr, f'S{s}', 'align_auto', vmin=np.nanmin(scene_arr), vmax=np.nanmax(scene_arr), cmap='Retinotopy_RYBCR')
cortex.add_roi(my_vol, **dict(colorbar_location='left', pixelwise=True, nanmean=True, with_curvature=True))


# to visualize in pycortex; can turn rois and their labels on and off
cortex.webshow(my_vol, recache=True)

# how BEST to get labels to look right in pycortex?
# CAN add text layer in inkscape, but then can't reopen or they disappear... dunno why....


'''
'''



    # Alternative 2: load volumes as vertices (as part of dataset) instead!!
    # as shown in https://drive.google.com/file/d/1S_dFeq_oFeVokdIy0YTHtgOuhTHjqh1A/view

    # https://gallantlab.github.io/pycortex/auto_examples/datasets/plot_volume_to_vertex.html#sphx-glr-auto-examples-datasets-plot-volume-to-vertex-py
    # get a mapper from voxels to vertices for this transform
    no_transform = True
    if no_transform:
        # Example 1: volumes already in freesurfer space (no transform required, use "identity")
        mapper = cortex.get_mapper(f'S{s}', 'identity', 'line_nearest', recache=True)
        # pass the voxel data through the mapper to get vertex data
        pa_map = mapper(pa_vol) # vol already in freesurfer space
        ex_map = mapper(ex_vol)
    else:
        # Example 2: volumes in functional T1w space, need transformation before converted to vertex
        mapper = cortex.get_mapper(f'S{s}', 'align_auto', 'line_nearest', recache=True)

        pa_map = mapper(pa_vol_rs) # vol in functional T1w space
        ex_map = mapper(ex_vol_rs)

    # load volume as vertex,
    sub_retinotopy=cortex.Dataset()
    sub_retinotopy.description="retinotopy_flat"

    sub_retinotopy.views['polangle']=pa_map
    sub_retinotopy.views['eccentricity']=ex_map

    cortex.segment.cut_surface(
                f'S{s}', 'rh',
                name=f'S{s}_retinotopy_flat',
                fs_subject=f'sub-{s}',
                freesurfer_subject_dir=fs_dir,
                do_import_subject=True,
                data=sub_retinotopy
                )








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
