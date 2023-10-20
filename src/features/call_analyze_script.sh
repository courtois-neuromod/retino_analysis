module load matlab
matlab -nodisplay -nosplash -nodesktop -r "run('run_analyzePRF_elm.m'); exit;"

matlab -nodisplay -nosplash -nodesktop -r "run('run_analyzePRF_ginkgo.m'); exit;"
