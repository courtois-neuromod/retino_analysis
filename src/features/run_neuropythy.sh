#module load python/3.7
module load java/11.0.2
module load freesurfer/7.1.1
# java/1.7.0_80, java/1.8.0_121, java/1.8.0_192, java/11.0.2, java/13.0.1, java/13.0.2
# activate project's virtual env
workon retino_analysis

#CN_SUBJECTS="/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/data/temp_fs"
CN_SUBJECTS="/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/data/freesurfer"
SUBJECTS_DIR=$CN_SUBJECTS

SUB_NUM=${1} # 01, 02, 03
#SUB_NUM=03 # 01, 02, 03

# NOTE: CODE MUST BY RAN FROM INSIDE RUNDIR!!!
RUNDIR="/project/rrg-pbellec/mstlaure/retino_analysis"
OUTDIR="${RUNDIR}/results/npythy/sub-${SUB_NUM}"
INDIR="${RUNDIR}/results/fs/sub-${SUB_NUM}"

# https://github.com/noahbenson/neuropythy/blob/master/neuropythy/commands/register_retinotopy.py
# scale specifies the strength of the functional forces relative to anatomical forces
# during the registration; higher values will generally result in more warping
# while lower values will result in less warping. The default value is 20

#python -m neuropythy \
#      register_retinotopy "sub-${SUB_NUM}" \
#      --verbose \
#      --surf-format="mgz" \ # may also be 'curv'
#      --vol-format="mgz" \ # may also be 'nifti'

# BUG: numpy version?
#https://github.com/noahbenson/neuropythy/blob/842c347c02aed081770cbd9fc13e49e220cdb17c/neuropythy/commands/register_retinotopy.py#L501

# TODO: should I install an older version of numpy to deal w warning?

python -m neuropythy \
      register_retinotopy "sub-${SUB_NUM}" \
      --verbose \
      --surf-outdir="${OUTDIR}" \
      --surf-format="mgz" \ # may also be 'curv'
      --vol-outdir="${OUTDIR}" \
      --vol-format="mgz" \ # may also be 'nifti'
      #--scale=20.0 \
      --lh-angle="${INDIR}/lh.s${SUB_NUM}_prf_ang.mgz" \
      --lh-eccen="${INDIR}/lh.s${SUB_NUM}_prf_ecc.mgz" \
      --lh-radius="${INDIR}/lh.s${SUB_NUM}_prf_rfsize.mgz" \
      --lh-weight="${INDIR}/lh.s${SUB_NUM}_prf_R2.mgz" \
      --rh-angle="${INDIR}/rh.s${SUB_NUM}_prf_ang.mgz" \
      --rh-eccen="${INDIR}/rh.s${SUB_NUM}_prf_ecc.mgz" \
      --rh-radius="${INDIR}/rh.s${SUB_NUM}_prf_rfsize.mgz" \
      --rh-weight="${INDIR}/rh.s${SUB_NUM}_prf_R2.mgz"

echo "Job finished"
