#USmodule load freesurfer/5.3.0
module load freesurfer/7.1.1
#source $EBROOTFREESURFER/FreeSurferEnv.sh

workon retino_analysis

# set $SUBJECTS_DIR to cneuromod freesurfer data directory
# (fmriprep directory w output from cneuromod subject data on CC)
# /lustre03/project/6003287/datasets/cneuromod_processed/smriprep/sourcedata/freesurfer/sub-01/mri
#CN_SUBJECTS="/lustre03/project/6003287/datasets/cneuromod_processed/smriprep/sourcedata/freesurfer"
CN_SUBJECTS="/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/data/freesurfer"
SUBJECTS_DIR=$CN_SUBJECTS

SUB_NUM=${1} # 01, 02, 03
RES_TYPE=${2} # ecc, ang, R2, rfsize, x, y

#VOLFILE="/project/rrg-pbellec/mstlaure/retino_analysis/results/s01_3tasks_ecc.nii.gz"
VOLDIR="/project/rrg-pbellec/mstlaure/retino_analysis/results"
VOLFILE="${VOLDIR}/s${SUB_NUM}_3tasks_${RES_TYPE}.nii.gz"

OUTDIR="/project/rrg-pbellec/mstlaure/retino_analysis/results/fs"
L_OUTFILE="${OUTDIR}/lh.s${SUB_NUM}_prf_${RES_TYPE}.mgz"
R_OUTFILE="${OUTDIR}/rh.s${SUB_NUM}_prf_${RES_TYPE}.mgz"

mri_vol2surf --src ${VOLFILE} --out ${L_OUTFILE} --regheader "sub-${SUB_NUM}" --hemi lh
mri_vol2surf --src ${VOLFILE} --out ${R_OUTFILE} --regheader "sub-${SUB_NUM}" --hemi rh

#mri_vol2surf --src ${VOLFILE} --out ${OUTFILE} --trgsubject sub-01 --hemi lf
