
module load freesurfer/7.1.1

# ex to run script: ./run_FS.sh 01 rfsize
#workon retino_analysis
source /project/rrg-pbellec/mstlaure/.virtualenvs/retino_analysis/bin/activate

# set $SUBJECTS_DIR to cneuromod freesurfer data directory
# On Compute Canada:
# the fmriprep output directory from cneuromod subject data
# /lustre03/project/6003287/datasets/cneuromod_processed/smriprep/sourcedata/freesurfer
#CN_SUBJECTS="/lustre03/project/6003287/datasets/cneuromod_processed/smriprep/sourcedata/freesurfer"

# Here: linked to from my datalad project repo which links to save freesurfer subject_dir
CN_SUBJECTS="/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/data/freesurfer"
SUBJECTS_DIR=$CN_SUBJECTS

SUB_NUM=${1} # 01, 02, 03

VOLDIR="/project/rrg-pbellec/mstlaure/retino_analysis/results/analyzePRF/slicetimed"
OUTDIR="/project/rrg-pbellec/mstlaure/retino_analysis/results/fs"

for RES_TYPE in ang ecc x y R2 rfsize

do
  VOLFILE="${VOLDIR}/sub-${SUB_NUM}_fullbrain_${RES_TYPE}.nii.gz"
  L_OUTFILE="${OUTDIR}/sub-${SUB_NUM}/slicetimed/lh.s${SUB_NUM}_prf_${RES_TYPE}.mgz"
  R_OUTFILE="${OUTDIR}/sub-${SUB_NUM}/slicetimed/rh.s${SUB_NUM}_prf_${RES_TYPE}.mgz"

  mri_vol2surf --src ${VOLFILE} --out ${L_OUTFILE} --regheader "sub-${SUB_NUM}" --hemi lh
  mri_vol2surf --src ${VOLFILE} --out ${R_OUTFILE} --regheader "sub-${SUB_NUM}" --hemi rh
done
