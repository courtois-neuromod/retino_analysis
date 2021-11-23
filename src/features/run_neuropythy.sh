# load compute canada modules
module load java/11.0.2
module load freesurfer/7.1.1

# activate project's virtual env
#workon retino_analysis
source /project/rrg-pbellec/mstlaure/.virtualenvs/retino_analysis/bin/activate

# set Freesurfer SUBJECT_DIR path
#CN_SUBJECTS="/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/data/temp_fs"
CN_SUBJECTS="/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/data/freesurfer"
SUBJECTS_DIR=$CN_SUBJECTS

SUB_NUM="${1}" # 01, 02, 03

# NOTE: THE SCRIPT MUST BY RAN DIRECTLY INSIDE RUNDIR!!!
RUNDIR="/project/rrg-pbellec/mstlaure/retino_analysis"
OUTDIR="${RUNDIR}/results/npythy/sub-${SUB_NUM}"
INDIR="${RUNDIR}/results/fs/sub-${SUB_NUM}"

# Neuropythy Documentation:
# https://github.com/noahbenson/neuropythy/blob/master/neuropythy/commands/register_retinotopy.py
# https://github.com/noahbenson/neuropythy
# https://osf.io/knb5g/wiki/Usage/

# "scale" specifies the strength of the functional forces (subject's retinotopy) relative to anatomical forces (atlas prior) during the registration
# Higher values will generally result in more warping while lower values will result in less warping. The default value is 20

# There is a WARNING with more recent versions of numpy
# I filed an issue with the toolbox's repo and it's been closed
# the author checked and says it will not affect the results
# https://github.com/noahbenson/neuropythy/issues/24

python -m neuropythy \
      register_retinotopy "sub-${SUB_NUM}" \
      --verbose \
      --surf-outdir="${OUTDIR}" \
      --surf-format="mgz" \ # may also be 'curv'
      --vol-outdir="${OUTDIR}" \
      --vol-format="mgz" \ # may also be 'nifti'
      --lh-angle="${INDIR}/lh.s${SUB_NUM}_prf_ang.mgz" \
      --lh-eccen="${INDIR}/lh.s${SUB_NUM}_prf_ecc.mgz" \
      --lh-radius="${INDIR}/lh.s${SUB_NUM}_prf_rfsize.mgz" \
      --lh-weight="${INDIR}/lh.s${SUB_NUM}_prf_R2.mgz" \
      --rh-angle="${INDIR}/rh.s${SUB_NUM}_prf_ang.mgz" \
      --rh-eccen="${INDIR}/rh.s${SUB_NUM}_prf_ecc.mgz" \
      --rh-radius="${INDIR}/rh.s${SUB_NUM}_prf_rfsize.mgz" \
      --rh-weight="${INDIR}/rh.s${SUB_NUM}_prf_R2.mgz" \
      --scale=20.0

echo "Job finished"
