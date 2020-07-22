import argparse
from pathlib2 import Path
from kubeflow.metadata import metadata
from datetime import datetime
from uuid import uuid4
import json


def info(msg, char="#", width=75):
    print("")
    print(char * width)
    print(char + "   %0*s" % ((-1 * width) + 5, msg) + char)
    print(char * width)


def get_ws(workspace, description):  # noqa: E501
    # default DNS of Kubeflow Metadata gRPC serivce.
    METADATA_STORE_HOST = "metadata-grpc-service.kubeflow"
    METADATA_STORE_PORT = 8080
    ws = metadata.Workspace(
        store=metadata.Store(grpc_host=METADATA_STORE_HOST,
                             grpc_port=METADATA_STORE_PORT),
        name=workspace,
        description=description,
        labels={"Version": "v1"})
    return ws


def log_model(model_name, uri, model_version, execution, labels):
    model = execution.log_output(
        metadata.Model(
            name=model_name,
            description="Model to identify tacos or burritos",
            owner="Statistics Canada",
            uri=uri,
            model_type="Sequential Model",
            training_framework={
                "name": "tensorflow",
                "version": "v2.0"
            },
            hyperparameters={
                "learning_rate": 0.5,
                "layers": [10, 3, 1],
                "early_stop": True
            },
            version=model_version,
            labels=labels))

    print(model)
    print("\nModel id is {0.id} and version is {0.version}".format(model))


def log_dataset(name, uri, execution, labels):
    date_set_version = "data_set_version_" + str(uuid4())
    data_set = execution.log_input(
        metadata.DataSet(
            description="Training data set",
            name=name,
            owner="Statistics Canada",
            uri=uri,
            labels=labels,
            version=date_set_version))

    print("Data set id is {0.id} with version '{0.version}'".format(data_set))


if __name__ == "__main__":
    # print("Ok")
    # argparse stuff for model path and model name
    parser = argparse.ArgumentParser(description='sanity check on model')
    parser.add_argument('-b', '--base_path',
                        help='directory to base folder', default='../../data')
    parser.add_argument(
        '-m', '--model', help='path to model file', default='/model/latest.h5')
    parser.add_argument('-n', '--model_name',
                        help='Model name', default='kfmodel')
    parser.add_argument(
        '-d', '--data', help='directory to training and test data', default='train')  # noqa: E501
    parser.add_argument('-f', '--dataset', help='cleaned data listing')
    parser.add_argument('-ri', '--run_id', help='pieline run id')
    args = parser.parse_args()

    args.model = 'model/' + args.model
    model_path = str(Path(args.base_path).resolve(
        strict=False).joinpath(args.model).resolve(strict=False))
    data_path = Path(args.base_path).joinpath(args.data).resolve(strict=False)
    dataset = Path(args.base_path).joinpath(args.dataset)
    labels = {
        'run_id': args.run_id
    }

    ws = get_ws("Kubemlops", "MLops for Kubeflow")
    run = metadata.Run(
        workspace=ws,
        name="run-" + datetime.utcnow().isoformat("T"),
        description="Run for training TacosBurritos model")

    execution = metadata.Execution(
        name="execution" + datetime.utcnow().isoformat("T"),
        workspace=ws,
        run=run,
        description="tacos-burritos",
    )
    print("An execution was created with id %s" % execution.id)

    info('Log model artifact')
    model_version = "model_version_" + str(uuid4())
    log_model(args.model_name, model_path, model_version,
              execution, json.dumps(labels))

    info('Log training data set')

    log_dataset(args.dataset, str(dataset), execution, json.dumps(labels))
