"""Convolutional Neural Network (CNN) Pipeline"""
from kubernetes import client as k8s_client
import kfp.dsl as dsl
import kfp.compiler as compiler
from kfp.azure import use_azure_secret
import json
import os
from kubernetes.client.models import V1EnvVar
from utils.kubernetes.secret import use_azstorage_secret  # noqa: E501

# Initially derived from https://github.com/kaizentm/kubemlops


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


def cnn_train(
    resource_group,
    workspace,
    dataset,
    token
):
    """Pipeline steps"""

    persistent_volume_path = '/mnt/azure'
    data_download = dataset  # noqa: E501
    batch = 32
    model_name = 'cnnmodel'
    operations = {}
    image_size = 160
    training_folder = 'train'
    training_dataset = 'train.txt'
    model_folder = 'model'
    image_repo_name = "k8scc01covidmlopsacr.azurecr.io/mlops"
    callback_url = 'kubemlopsbot-svc.kubeflow.svc.cluster.local:8080'
    mlflow_url = 'http://mlflow.mlflow:5000'

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

        operations['tensorflow preprocess'] = dsl.ContainerOp(
            name='tensorflow preprocess',
            init_containers=[start_callback],
            image=image_repo_name + '/tensorflow-preprocess:latest',
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

        operations['tensorflow training'] = dsl.ContainerOp(
            name="tensorflow training",
            image=image_repo_name + '/tensorflow-training:latest',
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
            output_artifact_paths={
                'mlpipeline-metrics': '/mlpipeline-metrics.json',
                'mlpipeline-ui-metadata': '/mlpipeline-ui-metadata.json'
            }
            ).apply(use_azstorage_secret()).add_env_variable(V1EnvVar(name="RUN_ID", value=dsl.RUN_ID_PLACEHOLDER)).add_env_variable(V1EnvVar(name="MLFLOW_TRACKING_TOKEN", value=token)).add_env_variable(V1EnvVar(name="MLFLOW_TRACKING_URI", value=mlflow_url)).add_env_variable(V1EnvVar(name="GIT_PYTHON_REFRESH", value='quiet'))  # noqa: E501

        operations['tensorflow training'].after(operations['tensorflow preprocess'])  # noqa: E501

        operations['evaluate'] = dsl.ContainerOp(
            name='evaluate',
            image="busybox",
            command=['sh', '-c'],
            arguments=[
                'echo',
                'Life is Good!'
            ]

        )
        operations['evaluate'].after(operations['tensorflow training'])

        operations['register kubeflow'] = dsl.ContainerOp(
            name='register kubeflow',
            image=image_repo_name + '/register-kubeflow-artifacts:latest',
            command=['python'],
            arguments=[
                '/scripts/register.py',
                '--base_path', persistent_volume_path,
                '--model', 'latest.h5',
                '--model_name', model_name,
                '--data', training_folder,
                '--dataset', training_dataset,
                '--run_id', dsl.RUN_ID_PLACEHOLDER
            ]
        ).apply(use_azure_secret())
        operations['register kubeflow'].after(operations['evaluate'])

        operations['register AML'] = dsl.ContainerOp(
            name='register AML',
            image=image_repo_name + '/register-aml:latest',
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
        operations['register AML'].after(operations['register kubeflow'])

        operations['register mlflow'] = dsl.ContainerOp(
            name='register mlflow',
            image=image_repo_name + '/register-mlflow:latest',
            command=['python'],
            arguments=[
                '/scripts/register.py',
                '--model', 'model',
                '--model_name', model_name,
                '--experiment_name', 'kubeflow-mlops',
                '--run_id', dsl.RUN_ID_PLACEHOLDER
            ]
        ).apply(use_azure_secret()).add_env_variable(V1EnvVar(name="MLFLOW_TRACKING_URI", value=mlflow_url)).add_env_variable(V1EnvVar(name="MLFLOW_TRACKING_TOKEN", value=token))  # noqa: E501
        operations['register mlflow'].after(operations['register AML'])

        operations['finalize'] = dsl.ContainerOp(
            name='Finalize',
            image="curlimages/curl",
            command=['curl'],
            arguments=[
                '-d', get_callback_payload("Model is registered"),
                callback_url
            ]
        )
        operations['finalize'].after(operations['register mlflow'])

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
    compiler.Compiler().compile(cnn_train, __file__ + '.tar.gz')
