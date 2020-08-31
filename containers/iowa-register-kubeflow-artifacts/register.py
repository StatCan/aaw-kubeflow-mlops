import argparse
from kubeflow.metadata import metadata
from uuid import uuid4
from datetime import datetime
import yaml


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

DEFAULT_WORKSPACE_NAME = "iowa-train"


def get_ws(workspace, description="", labels=None):  # noqa: E501
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


# def log_dataset(name, uri, version, execution, labels):
#     """
#     Logs a dataset's usage to Metadata execution

#     Will reuse a dataset if a matching dataset already exists, else will create
#     a new dataset.  Datasets are uniquely keyed by the union of:
#     - name
#     - uri
#     - version
#     """
#     pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log pipeline artifacts to "
                                                 "Kubeflow.Metadata")
    parser.add_argument('-w', '--workspace',
                        default=DEFAULT_WORKSPACE_NAME,
                        help="Name of workspace to log artifacts to")
    parser.add_argument('--model_uri', help='Path to model file')
    parser.add_argument('-t', '--train_uri',
                        help='Global path to training data')
    parser.add_argument('--train_version',
                        default=None,
                        help='Hash/version for training data (if None, will '
                        'auto generate a uuid)')
    parser.add_argument('-s', '--score_uri',
                        help='Global path to scoring data')
    parser.add_argument('--score_version',
                        default=None,
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
        help='Run ID for this run (if None, will auto generate)')

    args = parser.parse_args()

    run_id = f"autogen_{str(uuid4())}" if args.run_id is None else args.run_id

    ws = get_ws(args.workspace)

    # Create datasets
    train_version = args.train_version if args.train_version is not None else \
        f"autogen_{str(uuid4())}"
    ds_train = metadata.DataSet(
        uri=args.train_uri,
        name="training-data",
        version=train_version,
        workspace=ws.name,
    )

    score_version = args.score_version if args.score_version is not None else \
        f"autogen_{str(uuid4())}"
    ds_score = metadata.DataSet(
        uri=args.score_uri,
        name="scoring-data",
        version=score_version,
        workspace=ws.name,
    )

    # Create model
    if args.params_file is not None:
        with open(args.params_file, 'r') as fin:
            params = yaml.safe_load(fin)
        model_type = params.get('model_type', None)
        version = params.get('version', run_id)
        training_framework = params.get('training_framework', None)

    else:
        params = None
        model_type = None
        version = None
        training_framework = None

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

    metrics = metadata.Metrics(
        uri=args.metrics_uri,
        name=f"scoring-metrics-{run_id}",
        data_set_id=str(ds_score.id),
        model_id=str(model.id),
        metrics_type=metadata.Metrics.VALIDATION,
        values=metrics_values
    )

    # Attach artifacts to training run/execution
    # TODO: Use run_id here instead of timestamp?
    now = datetime.utcnow().isoformat("T")

#     # Not sure what the runs are for...  Maybe an optional grouping?
#     # They show up as metadata on the execution
#     # They're not required but left here to think about later...
#     r = metadata.Run(
#         workspace=ws,
#         name="training-run-{now}",
#     )

    ex = metadata.Execution(
        name=f"training-execution-{now}",  # unique name
        workspace=ws,
        # run=r,
    )

    # Log all metadata
    ex.log_input(ds_train)
    ex.log_output(model)
    ex.log_output(metrics)