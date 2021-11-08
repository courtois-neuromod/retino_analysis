module load afni/21.2.10

# Oli: Version AFNI_21.0.21 'Titus'

# activate project's virtual env
#source /project/rrg-pbellec/mstlaure/cneuromodNIF/env/bin/activate
workon retino_analysis

RUNDIR="/project/rrg-pbellec/mstlaure/retino_analysis"

python -m run_pRF_afni \
      --run_dir="${RUNDIR}" \
      --config='config.json'

echo "Job finished"
