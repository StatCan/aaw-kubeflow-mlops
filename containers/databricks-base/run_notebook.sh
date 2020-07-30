#!/bin/bash

while getopts "r:p:" option;
    do
    case "$option" in
        r ) RUN_ID=${OPTARG};;
        p ) NOTEBOKK_PARAMETERS=${OPTARG};;
    esac
done

echo $RUN_ID
echo $NOTEBOKK_PARAMETERS

cd /scripts
databricks workspace import -o -l PYTHON notebook.py /Shared/$RUN_ID

sed -i 's/{{CLUSTER_ID}}/'$CLUSTER_ID'/g' run_config.json
sed  -i 's/{{NOTEBOOK_PARAMETERS}}/'"$NOTEBOKK_PARAMETERS"'/g' run_config.json
sed -i 's/{{NOTEBOOK_NAME}}/'$RUN_ID'/g' run_config.json

run_id=$(databricks runs submit --json-file run_config.json | jq -r '.run_id')
databricks runs get --run-id $run_id

SECONDS=0
while [[ SECONDS -lt 600 ]]; do
 STATUS=$(databricks runs get --run-id $run_id | jq -r '.state.life_cycle_state')
 if [ $STATUS == 'TERMINATED' ]; then
    break
 fi
 echo $STATUS"..."
 sleep 2
done

RESULT_STATE=$(databricks runs get --run-id $run_id | jq -r '.state.result_state')
echo $RESULT_STATE
if [ $RESULT_STATE == 'SUCCESS' ]; then
 exit 0
else
 echo 'See details at '$(databricks runs get --run-id $run_id | jq -r '.run_page_url')
 exit 1
fi
