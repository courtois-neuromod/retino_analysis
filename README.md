retino_analysis
==============================

Retinotopy Analysis Pipeline
------------

Note: with the exception of the retinotopy analysis, which I ran in matlab on elm/ginkgo with the analyzePRF toolbox, all other scripts/steps are ran on Compute Canada cluster node from my project's repo:
home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis.

Step 1. Create frame-by-frame and TR-by-TR aperture masks (visual stimuli) from PsychoPy script and images (stimuli)

Script: src/data/make_stimuli.py

```bash
python -m src.data.make_stimuli
```

Input: psychopy binary aperture masks (stimuli [1 = pixel where images are shown at time t, 0 = no image shown])
Output: Binary aperture masks are averaged within each TR to obtain a temporal sequence of aperture frames (floats [0, 1]) for each TR.




--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
