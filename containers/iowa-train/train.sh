#!/bin/bash

# Note: Could also do this runner like here:
# https://github.com/kaizentm/kubemlops/blob/master/code/notebook-comp/src/program.py
# They run from inside python rather than shell, can then use argparse etc.
# Maybe make a generic wrapper that passes all args to notebook and checks
# if they were expected?

# TODO: Make this into a generic papermill wrapper that just blindly accepts 
# --kwargs and assigns them as -p variables, and also auto-generates the 
# completed notebook path?  Or just stop caring about returning the completed 
# notebook?

# Example training call
# bash train.sh --notebook train.ipynb --output_notebook complete.ipynb --output_params params_output.yml --data data_train.csv --output_model model.joblib --svm_gamma 0.1 --svm_c 100

PARAMS=""
while (( "$#" )); do
  case "$1" in
    --notebook)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        NOTEBOOK=$2
        shift 2
      else
        echo "Error: Argument for $1 is missing" >&2
        exit 1
      fi
      ;;
    --output_notebook)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        OUTPUT_NOTEBOOK=$2
        shift 2
      else
        echo "Error: Argument for $1 is missing" >&2
        exit 1
      fi
      ;;
    --output_model)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        OUTPUT_MODEL=$2
        shift 2
      else
        echo "Error: Argument for $1 is missing" >&2
        exit 1
      fi
      ;;
    --output_params)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        OUTPUT_PARAMS=$2
        shift 2
      else
        echo "Error: Argument for $1 is missing" >&2
        exit 1
      fi
      ;;
    --data)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        DATA=$2
        shift 2
      else
        echo "Error: Argument for $1 is missing" >&2
        exit 1
      fi
      ;;
    --svm_gamma)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        SVM_GAMMA=$2
        shift 2
      else
        echo "Error: Argument for $1 is missing" >&2
        exit 1
      fi
      ;;
    --svm_c)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        SVM_C=$2
        shift 2
      else
        echo "Error: Argument for $1 is missing" >&2
        exit 1
      fi
      ;;
    -*|--*=) # unsupported flags
      echo "Error: Unsupported flag $1" >&2
      exit 1
      ;;
    *) # preserve positional arguments
      echo "Error: Positional arguments not supported" >&2
      exit 1
      ;;
  esac
done

# TODO: Test for required args

# KFP may pass filenames with parent directories that do not yet exist
# Create directories for output files
mkdir -p `dirname $OUTPUT_NOTEBOOK`
mkdir -p `dirname $OUTPUT_MODEL`

cmd="papermill $NOTEBOOK $OUTPUT_NOTEBOOK -p data $DATA -p output_model $OUTPUT_MODEL -p output_params $OUTPUT_PARAMS -p svm_gamma $SVM_GAMMA -p svm_C $SVM_C"
echo Executing: $cmd
eval $cmd