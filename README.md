retino_analysis
==============================

Retinotopy Analysis Pipeline
------------

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
**Step 2. Pre-process bold data and stimuli for analyzepRF toolbox**

Script: src/data/average_bold.py

To average bold data across sessions, per task, for each participant (one file per task =  3 bold files)
```bash
python -m src.data.average_bold.py –-makemasks –-makestim
```

To save bold data separately for each session (one file per task per session = 3 x 6 bold files)
```bash
python -m src.data.average_bold.py –-makemasks –-makestim --per_session
```

**Input**: bold nii.gz files processed with fmriprep in T1w space, and stimuli (aperture frames per TR) \
**Output**: 
- Stimuli resized to 192x192 to speed up analyzePRF processing time (first three TRs dropped) 
- Whole-brain subject masks made from subject's epi masks (one per session for each task) and from a grey matter anatomical mask outputted by freesurfer
- Detrended and normalized bold runs averaged per task across 5/6 sessions; saved as a 1D flattened masked array inside a .mat file



--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
