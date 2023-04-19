retino_analysis
==============================

Retinotopy Analysis Pipeline
------------
Author: Marie St-Laurent \
With thanks to Basile Pinsard (psychopy and data preprocessing) and Oliver Contier (freesurfer and neuropythy pipeline).

Note: with the exception of the retinotopy analysis, which I ran in matlab on elm/ginkgo with the analyzePRF toolbox, all other scripts/steps are ran on Compute Canada cluster node from my project's repo:
home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis.

------------
**Step 1. Create frame-by-frame and TR-by-TR aperture masks (visual stimuli) from PsychoPy script and images (stimuli)**

Script: src/data/make_stimuli.py

```bash
python -m src.data.make_stimuli
```

**Input**: psychopy binary aperture masks (stimuli [1 = pixel where images are shown at time t, 0 = no image shown]) \
**Output**: Binary aperture masks are averaged within each TR to obtain a temporal sequence of aperture frames (floats [0, 1]) for each TR.

------------
**Step 2. Pre-process bold data and stimuli for the analyzepRF toolbox**

Note: processes data from multiple participants.

Script: src/data/average_bold.py

To average bold data across sessions, per task, for each participant (one file per task =  3 bold files)
```bash
python -m src.data.average_bold --makemasks --makestim
```

To save bold data separately for each session (one file per task per session = 3 x 6 bold files)
```bash
python -m src.data.average_bold --makemasks --makestim --per_session
```

**Input**: bold nii.gz files processed with fmriprep in T1w space, and stimuli (aperture frames per TR) \
**Output**:
- Stimuli resized to 192x192 to speed up analyzePRF processing time (first three TRs dropped)
- Whole-brain subject masks made from subject's epi masks (one per session for each task) and from a grey matter anatomical mask outputted by freesurfer
- Detrended and normalized bold runs averaged per task across 5/6 sessions; saved as a 1D flattened masked array inside a .mat file

------------
**Step 3. Chunk flattened and detrended brain voxels into segments that load easily into matlab**

Note: processes data from multiple participants.

AnalyzePRF processes each voxel individually, which is maddeningly slow. Chunks allow to run the pipeline in parallel from different machines (e.g., elm and ginkgo) to speed up the process.

Script: src/data/chunk_bold.py

Ideally, set chunk_size argument (which sets the number of voxels per chunk) to be a multiple of the number of matlab workers available on elm/ginkgo
```bash
python -m src.data.chunk_bold --chunk_size=240
```
Note to self: Make sure to generate separate individual subject directories in which to save the 800+ chunks (s01, s02...)


**Input**: Detrended and masked voxels processed with average_bold.py \
**Output**: Chunks of detrended and flattened voxels to load in matlab (~850 .mat files for >200k voxels), dim = (voxels, TR)

------------
**Step 4. AnalyzePRF toolbox**

Note: processes a single participant at a time, very slowly.

Transfer data (chunks and resized stimuli) from Compute Canada to elm/ginkgo, and process it through Kendrick Kay’s AnalyzePRF retinotopy toolbox (in matlab). Toolbox repo [here](https://github.com/cvnlab/analyzePRF); Toolbox documentation/examples [here](http://kendrickkay.net/analyzePRF/).

Notes:
- Matlab version: R2021a Update 5 (9.10.0.1739362) 64-bit (glnxa64) is installed on elm/ginkgo with UdeM license
- On elm/ginkgo, I have a downloaded a copy of the analyze_pFR toolbox code locally from the repo (it's not a repo though) in /home/mariestl/cneuromod/retinotopy/analyzePRF

Do:
- Copy the stimuli (e.g., rings_per_TR199_192x192.mat) in /home/mariestl/cneuromod/retinotopy/analyzePRF/data
- Copy chunks files from beluga home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/output/detrend/chunks_fullbrain/s0* into elm/ginkgo /home/mariestl/cneuromod/retinotopy/analyzePRF/data/chunks/sub-0*/fullbrain
- Modify scripts **run_analyzePRF_elm.m** and **run_analyzePRF_ginkgo.m** to determine which subject to run, and which series of chunks to process on which server; the chunk numbers called by the script are determined by the for loop (line 42). (Note: this is not a local repo, those scripts are copied and modified locally & manually)
- AnalyzePRF results (sets of metrics for each chunk) are saved in /home/mariestl/cneuromod/retinotopy/analyzePRF/results/sub-0*/fullbrain

Generic copy of the script that calls analyzePRF: src/features/run_analyzePRF.m \
Example bash script to call run_analyzePRF.m from the console: src/features/call_analyze_script.sh

- Run the script inside a detachable tmux session (it will take > 24h for an entire brain with 50 workers)
E.g.,
```bash
tmux
module load matlab
matlab -nodisplay -nosplash -nodesktop -r "run('run_analyzePRF_elm.m'); exit;"
```

Note to self: The number of workers used by parpool for parallel processing is determined by availability, up to the default set in the "local" profile. Launching the matlab interface and changing that default (bottom left green flashing button) allows to modify it. The parallel workers are called in the toolbox code by default.

**Input**: Chunks of detrended voxels  \
**Output**: Population receptive field metrics estimated for each voxel, saved per chunk

------------
**Step 5. Reconstruct chunked output files into brain volumes and pre-process metrics for Neuropythy toolbox**

Copy the chunked results files from elm/ginkgo:/ /home/mariestl/cneuromod/retinotopy/analyzePRF/results/sub-0*/fullbrain
into beluga:/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/results/analyzePRF/chunked/s0*

Then, reassemble the chunked output files into brain volumes and adapt them for Neuropythy. \
Neuropythy repo [here](https://github.com/noahbenson/neuropythy); Neuropythy user manual [here](https://osf.io/knb5g/wiki/Usage/).\
Note: processes a single participant's data at a time.

Script: src/features/reassamble_voxels.py
```bash
python -m src.features.reassamble_voxels.py --sub_num=”sub-03”
```

**Input**: Chunks of retinotopy metrics saved as 1D arrays in .mat file \
**Output**: Brain volumes of retinotopy metrics in T1w space

------------
**Step 6. Convert retinotopy output maps from T1w volumes into surfaces with freesurfer**

Notes:
- this step requires access to fmriprep freesurfer output
- I installed freesurfer locally in my home directory, following Compute Canada [guidelines](https://docs.computecanada.ca/wiki/FreeSurfer)
- The $SUBJECTS_DIR variable must be set to the path to the directory where cneuromod subjects' freesurfer output is saved

Script: src/features/run_FS.sh
To run (where "01" is the subject number):
```bash
./src/features/run_FS.sh 01  
```

**Input**: Brain volumes of retinotopy metrics in T1w space \
**Output**: freesurfer surface maps (one per hemisphere per metric). e.g., lh.s01_prf_ang.mgz & rh.s01_prf_ang.mgz


------------
**Step 7. Process surface maps with neuropythy toolbox**

The Neuropythy toolbox estimates regions of interest based on a single subject's retinotopy results, plus a prior of ROIs estimated from the HCP project.
Neuropythy [repo](https://github.com/noahbenson/neuropythy) and [command line arguments](https://github.com/noahbenson/neuropythy/blob/master/neuropythy/commands/register_retinotopy.py); Neuropythy [user manual](https://osf.io/knb5g/wiki/Usage/).

Notes:
- this step requires to load java and freesurfer modules; $SUBJECTS_DIR needs to be specified just like in step 6.
- There is a Visible Deprecation Warning that appears with newer versions of numpy that do not affect the output. [Filed repo issue here.](https://github.com/noahbenson/neuropythy/issues/24)

Script: src/features/run_neuropythy.sh
To run (where "01" is the subject number):
```bash
./src/features/run_neuropythy.sh 01
```

**Input**: freesurfer surface maps of retinotopy metrics \
**Output**: Inferred retinotopy surface maps (based on atlas prior and subject's own retinotopy data) and region of interest labels (e.g., lh.inferred_varea.mgz)

------------
**Step 8. Reorient and resample neuropythy output maps and project the results back into T1w volume space**

**First**: re-orient the neuropythy output with mri_convert and fsl
Script: src/features/reorient_npythy.sh
```bash
./src/features/reorient_npythy.sh 01
```
Notes:
- this script needs to run from within the subject’s freesurfer "MRI" directory (hence the "cd") so it knows where to find freesurfer files.
- on Compute Canada, the script prompts to specify which module versions to use; chose option 2 : fsl/6.0.3 StdEnv/2020 gcc/9.3.0

**Second**: Resample binary visual ROIs to T1w functional space
Script: src/features/resample_npythy_ROIs.py
Before running, load project's virtual env with **workon retino_analysis** (on beluga)
```bash
python -m src.features.resample_npythy_ROIs --sub_num=”sub-01”
```

**Input**: Inferred retinotopy surface maps \
**Output**: NIfTI volumes of retinotopy results adjusted from atlas prior, and inferred regions of interest (binary mask for V1, V2, V3, hV4, V01, V02, L01, L02, T01, T02, V3b and V3a) in T1w space

--------

**Step 8. Clean up operation**

When z-scoring (per run) the BOLD data given to the AnalyzePRF toolbox, some voxels within
the WholeBrain functional mask (used to mask data across all runs) have nan scores (due to low/no signal on some runs).

Step 1: identify voxels to exclude from final volumes

This script identifies voxels with nan scores, and creates masks to exclude them from final result volumes.

Server: beluga \
Path to data: /home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/data/temp_bold \
Path to code dir: /home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis \
Script: quick_mask_QC_retino.py

Call script in interactive session on beluga (small dumb script, input and output paths hard-coded)
```bash
workon retino_analysis
python -m quick_mask_QC_retino
```

**Input**:
- All subject's *bold.nii.gz files, for all sessions (~6) and runs (3 per session) \
(e.g., sub-03_ses-10_task-things_run-1_space-T1w_desc-preproc_part-mag_bold.nii.gz)
- The functional mask used to mask all run data (e.g., sub-02_WholeBrain.nii.gz)

**Output**:
- One mask that includes all voxels with at least one normalized BOLD value equal to nan within the broader functional brain mask (e.g., 01_nanmask_T1w_retino.nii)
- One mask that includes all voxels with no normalized BOLD value equal to nan within the broader functional brain mask (e.g., 01_goodvoxmask_T1w_retino.nii)


Step 2: This script uses the good voxel mask created in step one to clean up output volumes of AnalyzePRF and Neuropythy analyses

Server: beluga \
Path to data: /home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/results \
Path to code dir: /home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis \
Script: clean_volumes.py

Call script in interactive session on beluga (small dumb script, input and output paths hard-coded)
```bash
workon retino_analysis
python -m clean_volumes --sub_num=sub-01
```

**Input**:
- The functional mask used to mask all run data (e.g., sub-02_WholeBrain.nii.gz) and the clean mask created in step 1 (e.g., 01_goodvoxmask_T1w_retino.nii)
- The .mat files of AnalyzePRF results per masked voxels outputed at step 5
- The resampled volumes of Neuropythy data (sub-01/resampled*.nii.gz) outputed at step 7

**Output**:
- Clean volumes of Neuropythy and AnalyzePRF results in functional T1w space. All files are relabelled *goodvox.nii.gz

--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
