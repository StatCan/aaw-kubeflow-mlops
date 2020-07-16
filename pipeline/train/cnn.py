"""Convolutional Neural Network (CNN) Pipeline"""
from kubernetes import client as k8s_client
import kfp.dsl as dsl
import kfp.compiler as compiler
from kfp.azure import use_azure_secret
import json
import os
from kubernetes.client.models import V1EnvVar

TRAIN_START_EVENT = "Training Started"
TRAIN_FINISH_EVENT = "Training Finished"


@dsl.pipeline(
    name='Tacos vs. Burritos',
    description='Simple TF CNN'
)
def get_callback_payload(event_type):
    payload = {}
    payload['event_type'] = event_type
    payload['sha'] = os.getenv('GITHUB_SHA')
    payload['pr_num'] = os.getenv('PR_NUM')
    payload['run_id'] = dsl.RUN_ID_PLACEHOLDER
    if (event_type == TRAIN_FINISH_EVENT):
        payload['status'] = '{{workflow.status}}'
    return json.dumps(payload)


#  TODO: refactor this. Looks ugly
def use_databricks_secret(secret_name='databricks-secret'):
    def _use_databricks_secret(task):
        from kubernetes import client as k8s_client
        (
            task.container
                .add_env_variable(
                    k8s_client.V1EnvVar(
                        name='DATABRICKS_HOST',
                        value_from=k8s_client.V1EnvVarSource(
                            secret_key_ref=k8s_client.V1SecretKeySelector(
                                name=secret_name,
                                key='DATABRICKS_HOST'
                            )
                        )
                    )
                )
                .add_env_variable(  # noqa: E131
                    k8s_client.V1EnvVar(
                        name='DATABRICKS_TOKEN',
                        value_from=k8s_client.V1EnvVarSource(
                            secret_key_ref=k8s_client.V1SecretKeySelector(
                                name=secret_name,
                                key='DATABRICKS_TOKEN'
                            )
                        )
                    )
                )
                .add_env_variable(  # noqa: E131
                    k8s_client.V1EnvVar(
                        name='CLUSTER_ID',
                        value_from=k8s_client.V1EnvVarSource(
                            secret_key_ref=k8s_client.V1SecretKeySelector(
                                name=secret_name,
                                key='CLUSTER_ID'
                            )
                        )
                    )
                )
        )
        return task
    return _use_databricks_secret


def tacosandburritos_train(
    resource_group,
    workspace,
    dataset
):
    """Pipeline steps"""

    persistent_volume_path = '/mnt/azure'
    data_download = dataset  # noqa: E501
    batch = 32
    model_name = 'tacosandburritos'
    operations = {}
    image_size = 160
    training_folder = 'train'
    training_dataset = 'train.txt'
    model_folder = 'model'
    image_repo_name = "k8scc01covidmlopsacr.azurecr.io/mexicanfood"
    callback_url = 'kubemlopsbot-svc.kubeflow.svc.cluster.local:8080'
    mlflow_url = 'http://mlflow:5000'

    exit_op = dsl.ContainerOp(
        name='Exit Handler',
        image="curlimages/curl",
        command=['curl'],
        arguments=[
            '-d', get_callback_payload(TRAIN_FINISH_EVENT),
            callback_url
        ]
    )

    with dsl.ExitHandler(exit_op):
        start_callback = \
            dsl.UserContainer('callback',
                              'curlimages/curl',
                              command=['curl'],
                              args=['-d',
                                    get_callback_payload(TRAIN_START_EVENT), callback_url])  # noqa: E501

        operations['data processing on databricks'] = dsl.ContainerOp(
            name='data processing on databricks',
            init_containers=[start_callback],
            image=image_repo_name + '/databricks-notebook:latest',
            arguments=[
                '-r', dsl.RUN_ID_PLACEHOLDER,
                '-p', '{"argument_one":"param one","argument_two":"param two"}'
            ]
        ).apply(use_databricks_secret())

        operations['preprocess'] = dsl.ContainerOp(
            name='preprocess',
            image=image_repo_name + '/preprocess:latest',
            command=['python'],
            arguments=[
                '/scripts/data.py',
                '--base_path', persistent_volume_path,
                '--data', training_folder,
                '--target', training_dataset,
                '--img_size', image_size,
                '--zipfile', data_download
            ]
        )

        operations['preprocess'].after(operations['data processing on databricks'])  # noqa: E501

        #  train
        #  TODO: read set of parameters from config file
        # with dsl.ParallelFor([{'epochs': 1, 'lr': 0.0001}, {'epochs': 1, 'lr': 0.0002}]) as item:  # noqa: E501
        operations['training'] = dsl.ContainerOp(
            name="training",
            image=image_repo_name + '/training:latest',
            command=['python'],
            arguments=[
                '/scripts/train.py',
                '--base_path', persistent_volume_path,
                '--data', training_folder,
                '--epochs', 2,
                '--batch', batch,
                '--image_size', image_size,
                '--lr', 0.0001,
                '--outputs', model_folder,
                '--dataset', training_dataset
            ],
            output_artifact_paths={    # change output_artifact_paths to file_outputs after this PR is merged https://github.com/kubeflow/pipelines/pull/2334 # noqa: E501
                'mlpipeline-metrics': '/mlpipeline-metrics.json',
                'mlpipeline-ui-metadata': '/mlpipeline-ui-metadata.json'
            }
            ).add_env_variable(V1EnvVar(name="RUN_ID", value=dsl.RUN_ID_PLACEHOLDER)).add_env_variable(V1EnvVar(name="MLFLOW_TRACKING_URI", value=mlflow_url)).add_env_variable(V1EnvVar(name="GIT_PYTHON_REFRESH", value='quiet'))  # noqa: E501

        operations['training'].after(operations['preprocess'])

        operations['evaluate'] = dsl.ContainerOp(
            name='evaluate',
            image="busybox",
            command=['sh', '-c'],
            arguments=[
                'echo',
                'Life is Good!'
            ]

        )
        operations['evaluate'].after(operations['training'])

        # register kubeflow artifcats model
        operations['register to kubeflow'] = dsl.ContainerOp(
            name='register to kubeflow',
            image=image_repo_name + '/registerartifacts:latest',
            command=['python'],
            arguments=[
                '/scripts/registerartifacts.py',
                '--base_path', persistent_volume_path,
                '--model', 'latest.h5',
                '--model_name', model_name,
                '--data', training_folder,
                '--dataset', training_dataset,
                '--run_id', dsl.RUN_ID_PLACEHOLDER
            ]
        ).apply(use_azure_secret())
        operations['register to kubeflow'].after(operations['evaluate'])

        # register model
        operations['register to AML'] = dsl.ContainerOp(
            name='register to AML',
            image=image_repo_name + '/register:latest',
            command=['python'],
            arguments=[
                '/scripts/register.py',
                '--base_path', persistent_volume_path,
                '--model', 'latest.h5',
                '--model_name', model_name,
                '--tenant_id', "$(AZ_TENANT_ID)",
                '--service_principal_id', "$(AZ_CLIENT_ID)",
                '--service_principal_password', "$(AZ_CLIENT_SECRET)",
                '--subscription_id', "$(AZ_SUBSCRIPTION_ID)",
                '--resource_group', resource_group,
                '--workspace', workspace,
                '--run_id', dsl.RUN_ID_PLACEHOLDER
            ]
        ).apply(use_azure_secret())
        operations['register to AML'].after(operations['register to kubeflow'])

        # register model to mlflow
        operations['register to mlflow'] = dsl.ContainerOp(
            name='register to mlflow',
            image=image_repo_name + '/register-mlflow:latest',
            command=['python'],
            arguments=[
                '/scripts/register.py',
                '--model', 'model',
                '--model_name', model_name,
                '--experiment_name', 'mexicanfood',
                '--run_id', dsl.RUN_ID_PLACEHOLDER
            ]
        ).apply(use_azure_secret()).add_env_variable(V1EnvVar(name="MLFLOW_TRACKING_URI", value=mlflow_url))  # noqa: E501
        operations['register to mlflow'].after(operations['register to AML'])

        operations['finalize'] = dsl.ContainerOp(
            name='Finalize',
            image="curlimages/curl",
            command=['curl'],
            arguments=[
                '-d', get_callback_payload("Model is registered"),
                callback_url
            ]
        )
        operations['finalize'].after(operations['register to mlflow'])

    # operations['deploy'] = dsl.ContainerOp(
    #     name='deploy',
    #     image=image_repo_name + '/deploy:latest',
    #     command=['sh'],
    #     arguments=[
    #         '/scripts/deploy.sh',
    #         '-n', model_name,
    #         '-m', model_name,
    #         '-t', "$(AZ_TENANT_ID)",
    #         '-r', resource_group,
    #         '-w', workspace,
    #         '-s', "$(AZ_CLIENT_ID)",
    #         '-p', "$(AZ_CLIENT_SECRET)",
    #         '-u', "$(AZ_SUBSCRIPTION_ID)",
    #         '-b', persistent_volume_path,
    #         '-x', dsl.RUN_ID_PLACEHOLDER
    #     ]
    # ).apply(use_azure_secret())
    # operations['deploy'].after(operations['register'])

    for _, op_1 in operations.items():
        op_1.container.set_image_pull_policy("Always")
        op_1.add_volume(
            k8s_client.V1Volume(
              name='azure',
              persistent_volume_claim=k8s_client.V1PersistentVolumeClaimVolumeSource(  # noqa: E501
                claim_name='azure-managed-file')
            )
        ).add_volume_mount(k8s_client.V1VolumeMount(
            mount_path='/mnt/azure', name='azure'))


if __name__ == '__main__':
    compiler.Compiler().compile(tacosandburritos_train, __file__ + '.tar.gz')
