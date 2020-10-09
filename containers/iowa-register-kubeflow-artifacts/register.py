import argparse
from kubeflow.metadata import metadata
from uuid import uuid4
from datetime import datetime
import yaml

# # Sample test command:
# > local_copy_of_metrics_to_add_in_metadata.yaml \
#     && echo "accuracy: 0.75" >> local_copy_of_metrics_to_add_in_metadata.yaml \
#     && echo "precision: 0.75" >> local_copy_of_metrics_to_add_in_metadata.yaml
# MODEL_ID=$RANDOM  # Random ID for demo so model is new in lineage explorer
# echo "Logging model under unique_id $MODEL_ID"
# python register.py \
#     --workspace test_workspace \
#     --model_uri /minio/path/to/model_$MODEL_ID \
#     --train_uri /minio/path/to/train/data \
#     --train_version unique_id_for_train_eg_hash \
#     --score_uri /minio/path/to/score/data \
#     --score_version unique_id_for_score_eg_hash \
#     --params_file ../../pipeline/iowa-train/params.yml \
#     --metrics_uri /minio/path/to/metrics \
#     --metrics_file ./local_copy_of_metrics_to_add_in_metadata.yaml \
#     --run_id pipeline_run_id_from_kfp

# TODO:
# - Workflow of passing metric/param URI AND a file with metric or param values
#   is awkward.  How can we refactor?  Maybe have log_dataset, log_metric, etc.
#   components that both save to minio and record artifacts so it is more
#   convenient?  Or just have good atomic components for each and user can use
#   what they want?
# - Add arguments to accept metrics and params as yml (or json) strings instead
#   of files for convenience
# - Break this into pieces?  Start of pipeline creates a workspace, datasets
#   log individually, and models/metrics log as they're created?

# TODO: Make a demo showing how to use this?
# * Is this covered by the jupyter-notebooks demo?
# * Could have gif/video exploring the explorer.  
# * highlight how in the artifact screen things that are reuses of things (say referencing past training data) show without timestamp, etc.  

DEFAULT_WORKSPACE_NAME = "iowa-train"

def get_init_ws(workspace, description="", labels=None):  # noqa: E501
    """
    Returns an existing Kubeflow.Metadata workspace if exists, else returns new
    """
    # default DNS of Kubeflow Metadata gRPC serivce.
    METADATA_STORE_HOST = "metadata-grpc-service.kubeflow"
    METADATA_STORE_PORT = 8080

    if labels is None:
        labels = {}

    ws = metadata.Workspace(
        store=metadata.Store(grpc_host=METADATA_STORE_HOST,
                             grpc_port=METADATA_STORE_PORT),
        name=workspace,
        description=description,
        labels=labels)
    return ws

def get_default_id():
    return f"autogen_{str(uuid4())}"

def init_params_file(params_file):
    if args.params_file is not None:
        with open(args.params_file, 'r') as fin:
            params = yaml.safe_load(fin)
        model_type = params.get('model_type', None)
        version = params.get('version', args.run_id)
        training_framework = params.get('training_framework', None)
    else:
        params = None
        model_type = None
        version = None
        training_framework = None
    return params, model_type, version, training_framework

def parse_args():
    parser = argparse.ArgumentParser(description="Log pipeline artifacts to "
                                                 "Kubeflow.Metadata")
    parser.add_argument('-w', '--workspace',
                        default=DEFAULT_WORKSPACE_NAME,
                        help="Name of workspace to log artifacts to")
    parser.add_argument('--model_uri', help='Path to model file')
    parser.add_argument('-t', '--train_uri',
                        help='Global path to training data')
    parser.add_argument('--train_version',
                        default=get_default_id(),
                        help='Hash/version for training data (if None, will '
                        'auto generate a uuid)')
    parser.add_argument('-s', '--score_uri',
                        help='Global path to scoring data')
    parser.add_argument('--score_version',
                        default=get_default_id(),
                        help='Hash/version for scoring data (if None, will '
                        'auto generate a uuid)'
                        )
    parser.add_argument(
        '-p', '--params_file',
        help='(Optional) Local path to a YAML file with hyperparameter values '
             'that will be added to the metadata.  Params file can include '
             'and keys, but keys of "model_type", "version", and '
             '"training_framework" carry specific meaning in kubeflow.metadata'
             ' and will be used as such')
    parser.add_argument('--metrics_uri',
                        help='Global path to model metrics file')
    parser.add_argument('--metrics_file',
                        help='(Optional) Local path to a YAML file with '
                        'metric values that will be added to the metadata')
    parser.add_argument(
        '-r', '--run_id',
        default=get_default_id(),
        help='Run ID for this run (if None, will auto generate)'
)

    args = parser.parse_args()

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Workspace to store all results
    ws = get_init_ws(args.workspace)

    # Create datasets
    ds_train = metadata.DataSet(
        uri=args.train_uri,
        name="training-data",
        version=args.train_version,
        workspace=ws.name,
    )

    ds_score = metadata.DataSet(
        uri=args.score_uri,
        name="scoring-data",
        version=args.score_version,
        workspace=ws.name,
    )

    # Create model
    params, model_type, version, training_framework = init_params_file(args.params_file)

    model = metadata.Model(
        name=f"model",
        uri=args.model_uri,
        model_type=model_type,
        version=version,
        training_framework=training_framework,
        hyperparameters=params,
    )

    # Create metrics
    if args.metrics_file is not None:
        with open(args.metrics_file, 'r') as fin:
            metrics_values = yaml.safe_load(fin)
    else:
        metrics_values = None

    # TODO: need to expose the metrics_values in the kubeflow artifact explorer.  Should put them somewhere else (as is, they don't show up in explorer)
    metrics = metadata.Metrics(
        uri=args.metrics_uri,
        name=f"scoring-metrics-{args.run_id}",
        data_set_id=str(ds_score.id),
        model_id=str(model.id),
        metrics_type=metadata.Metrics.VALIDATION,
        values=metrics_values
    )

    # Attach artifacts to training run/execution
    # TODO: Use run_id here instead of timestamp?
    execution_id = datetime.utcnow().isoformat("T")
    # execution_id = run_id

#     # Not sure what the runs are for...  Maybe an optional grouping?
#     # They show up as metadata on the execution
#     # They're not required but left here to think about later...
#     r = metadata.Run(
#         workspace=ws,
#         name="training-run-{now}",
#     )
    r = None

    # Log training metadata to an execution
    ex_train = metadata.Execution(
        name=f"training-execution-{execution_id}",  # unique name
        workspace=ws,
        run=r,
    )

    ex_train.log_input(ds_train)
    ex_train.log_output(model)
    
    # Log scoring metadata to an execution
    ex_score = metadata.Execution(
        name=f"scoring-execution-{execution_id}",  # unique name
        workspace=ws,
        run=r,
    )

    ex_score.log_input(ds_score)
    ex_score.log_input(model)
    ex_score.log_output(metrics)
