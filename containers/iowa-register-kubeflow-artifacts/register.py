import argparse
from kubeflow.metadata import metadata
from uuid import uuid4
from datetime import datetime
import yaml


# TODO:
# - Pass pipeline runid to use for unique ID in execution name?
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


def log_dataset(name, uri, version, execution, labels):
    """
    Logs a dataset's usage to Metadata execution

    Will reuse a dataset if a matching dataset already exists, else will create
    a new dataset.  Datasets are uniquely keyed by the union of:
    - name
    - uri
    - version
    """
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log run artifacts to "
                                                 "Kubeflow.Metadata")
    parser.add_argument('-w', '--workspace',
                        default=DEFAULT_WORKSPACE_NAME,
                        help="Name of workspace to log artifacts to")
    parser.add_argument('-m', '--model', help='Path to model file')
    parser.add_argument('--train', help='Path to training data')
    parser.add_argument('--train_version',
                        default=None,
                        help='Hash/version for training data (if None, will '
                        'auto generate)'
                        )
    parser.add_argument('--score', help='Path to scoring data')
    parser.add_argument('--score_version',
                        default=None,
                        help='Hash/version for scoring data (if None, will '
                        'auto generate)'
                        )
    parser.add_argument('-p', '--params', help='Path to model parameters '
                        'file')
    parser.add_argument('-m', '--metrics', help='Path to model metrics file')
    parser.add_argument(
        'r', '--run_id',
        help='Run ID for this run (if None, will auto generate)')

    args = parser.parse_args()

    run_id = f"autogen_{str(uuid4())}" if args.run_id is None else args.run_id

    ws = get_ws(args.workspace)

    # Log datasets
    train_version = args.train_version if args.train_version is not None else \
        f"data_set_version_autogen_{str(uuid4())}"
    ds_train = metadata.DataSet(
        uri=args.train,
        name="training-data",
        version=train_version,
        workspace=ws.name,
    )

    score_version = args.score_version if args.score_version is not None else \
        f"data_set_version_autogen_{str(uuid4())}"
    ds_score = metadata.DataSet(
        uri=args.score,
        name="scoring-data",
        version=score_version,
        workspace=ws.name,
    )

    # Log model
    with open(args.params, 'r') as fin:
        params = yaml.safe_load(fin)
    model_type = params.get('model_type', None)
    version = params.get('version', None)
    training_framework = params.get('training_framework', None)

    model = metadata.Model(
        name=f"{DEFAULT_WORKSPACE_NAME}-{run_id}",
        uri=args.model,
        model_type=model_type,
        version=version,
        training_framework=training_framework,
        hyperparameters=params,
    )

    # Log metrics
    with open(args.metrics, 'r') as fin:
        metrics_values = yaml.safe_load(fin)

    metrics = metadata.Metrics(
        uri=args.metrics,
        name=f"{DEFAULT_WORKSPACE_NAME}-scoring-metrics-{run_id}",
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
        name="training-execution-{now}",  # unique name
        workspace=ws,
        # run=r,
    )

    ex.log_input(ds_train)
    ex.log_output(model)
    ex.log_output(metrics)