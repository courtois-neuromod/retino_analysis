
module load StdEnv/2020
module load gcc/9.3.0
module load fsl/6.0.3

module load freesurfer/7.1.1

#workon retino_analysis
source /project/rrg-pbellec/mstlaure/.virtualenvs/retino_analysis/bin/activate

# Goal: to reorient the neuropythy output
# https://github.com/noahbenson/neuropythy/blob/master/neuropythy/commands/register_retinotopy.py

SUB_NUM="${1}" # 01, 02, 03
#SUB_NUM=03 # 01, 02, 03

# Set Freesurfer SUBJECTS_DIR path
#CN_SUBJECTS="/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/data/temp_fs"
CN_SUBJECTS="/home/mstlaure/projects/rrg-pbellec/mstlaure/retino_analysis/data/freesurfer"
SUBJECTS_DIR=$CN_SUBJECTS

RUNDIR="/project/rrg-pbellec/mstlaure/retino_analysis"

# Run script directly from inside subject's freesurfer/mri subdirectory
#cd /project/rrg-pbellec/mstlaure/retino_analysis/data/freesurfer/sub-03/mri
cd ${RUNDIR}/data/freesurfer/sub-${SUB_NUM}/mri

INDIR="${RUNDIR}/results/npythy/sub-${SUB_NUM}"
OUTDIR="${RUNDIR}/results/npythy/sub-${SUB_NUM}"

for PARAM in angle eccen sigma varea
do
  mri_convert "${INDIR}/inferred_${PARAM}.mgz" "${OUTDIR}/inferred_${PARAM}_fsorient.nii.gz"
  fslreorient2std "${OUTDIR}/inferred_${PARAM}_fsorient.nii.gz" "${OUTDIR}/inferred_${PARAM}.nii.gz"
done

echo "Job finished"
