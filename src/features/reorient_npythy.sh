
module load StdEnv/2020
module load gcc/9.3.0
module load fsl/6.0.3

module load freesurfer/7.1.1

workon retino_analysis

# reorient the neuropythy output
# https://github.com/noahbenson/neuropythy/blob/master/neuropythy/commands/register_retinotopy.py

SUB_NUM=${1} # 01, 02, 03
#SUB_NUM=03 # 01, 02, 03
PARAM=${2} # angle, eccen, sigma, varea
#PARAM=angle

#CN_SUBJECTS="/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/data/temp_fs"
CN_SUBJECTS="/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/data/freesurfer"
SUBJECTS_DIR=$CN_SUBJECTS

cd /project/rrg-pbellec/mstlaure/retino_analysis/data/freesurfer/sub-03/mri

RUNDIR="/project/rrg-pbellec/mstlaure/retino_analysis"
INDIR="${RUNDIR}/results/npythy/sub-${SUB_NUM}"
OUTDIR="${RUNDIR}/results/npythy/sub-${SUB_NUM}"

mri_convert "${INDIR}/inferred_${PARAM}.mgz" "${OUTDIR}/inferred_${PARAM}_fsorient.nii.gz"
fslreorient2std "${OUTDIR}/inferred_${PARAM}_fsorient.nii.gz" "${OUTDIR}/inferred_${PARAM}.nii.gz"

echo "Job finished"
