module load python/3.7

# activate project's virtual env
workon retino_analysis

SUB_NUM=${1} # 01, 02, 03

RUNDIR="/project/rrg-pbellec/mstlaure/retino_analysis"
OUTDIR="${RUNDIR}/results/npythy/sub-${SUB_NUM}"
INDIR="${RUNDIR}/results/fs/sub-${SUB_NUM}"

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
      --rh-weight="${INDIR}/rh.s${SUB_NUM}_prf_R2.mgz"

echo "Job finished"
