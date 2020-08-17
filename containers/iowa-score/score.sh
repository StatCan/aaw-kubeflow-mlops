#!/bin/bash

# TODO: Make this into a generic papermill wrapper that just blindly accepts 
# --kwargs and assigns them as -p variables, and also auto-generates the 
# completed notebook path?  Or just stop caring about returning the completed 
# notebook?

# Example training call
# bash score.sh --notebook score.ipynb --output_notebook complete.ipynb --data test.csv --model model.joblib --output_classification_report_filename classification_report.csv --output_f1_filename f1.txt

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
    --data)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        DATA=$2
        shift 2
      else
        echo "Error: Argument for $1 is missing" >&2
        exit 1
      fi
      ;;
    --model)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        MODEL=$2
        shift 2
      else
        echo "Error: Argument for $1 is missing" >&2
        exit 1
      fi
      ;;
    --output_classification_report_filename)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        OUTPUT_CLASSIFICATION_REPORT_FILENAME=$2
        shift 2
      else
        echo "Error: Argument for $1 is missing" >&2
        exit 1
      fi
      ;;
    --output_f1_filename)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        OUTPUT_F1_FILENAME=$2
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
mkdir -p `dirname $RESULTS_FILE_PREFIX`

cmd="papermill $NOTEBOOK $OUTPUT_NOTEBOOK -p data $DATA -p model $MODEL -p output_classification_report_filename $OUTPUT_CLASSIFICATION_REPORT_FILENAME -p output_f1_filename $OUTPUT_F1_FILENAME"
echo Executing: $cmd
eval $cmd