from mlflow.tracking import MlflowClient
import mlflow
from mlflow.entities import ViewType
import argparse


client = MlflowClient()


def get_run(external_run_id, experiment_name):
    experiments = [client.get_experiment_by_name(experiment_name).experiment_id]  # noqa: E501
    run = client.search_runs(
        experiment_ids=experiments,
        filter_string="tags.external_run_id = '{0}'".format(external_run_id),
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=1
        )[0]
    return run


def register_model(run, model, model_name):
    result = mlflow.register_model(
        "runs:/" + run.info.run_id + "/artifacts/" + model,
        model_name
    )

    description = []
    for param in run.data.params:
        description.append(
            "**{}:** {}\n".format(param, run.data.params[param]))

    description.append(
        "**Accuracy:** {}".format(
            client.get_metric_history(run.info.run_id, "accuracy")[0].value))

    description.append(
        "**Loss:** {}".format(
            client.get_metric_history(run.info.run_id, "loss")[0].value))

    MlflowClient().update_model_version(
        name=model_name,
        version=result.version,
        description="".join(description)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model',
                        help='Model file')
    parser.add_argument(
        '-n', '--model_name', help='MLFlow Model Name')
    parser.add_argument(
        '-e', '--experiment_name', help='MLFlow Experiment Name')
    parser.add_argument(
        '-r', '--run_id', help='KFP run id')

    args = parser.parse_args()

    run = get_run(args.run_id, args.experiment_name)
    register_model(run, args.model, args.model_name)
