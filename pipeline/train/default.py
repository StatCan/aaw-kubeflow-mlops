"""Default Pipeline"""
from kubernetes import client as k8s_client
import kfp.dsl as dsl
import kfp.compiler as compiler
import json
import os

# Initially derived from https://github.com/kaizentm/kubemlops


TRAIN_START_EVENT = "Training Started"
TRAIN_FINISH_EVENT = "Training Finished"


@dsl.pipeline(
    name='Default',
    description='Simple default pipeline to test functionality'
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


def default_train(
    resource_group,
    workspace,
    dataset
):
    """Pipeline steps"""

    operations = {}
    callback_url = 'kubemlopsbot-svc.kubeflow.svc.cluster.local:8080'

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

        operations['start'] = dsl.ContainerOp(
            name='start',
            init_containers=[start_callback],
            image="busybox",
            command=['sh', '-c'],
            arguments=[
                'echo',
                'Pipeline starting'
            ]
        )

        operations['end'] = dsl.ContainerOp(
            name='End',
            image="curlimages/curl",
            command=['curl'],
            arguments=[
                '-d', get_callback_payload("Model is registered"),
                callback_url
            ]
        )
        operations['end'].after(operations['start'])

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
    compiler.Compiler().compile(default_train, __file__ + '.tar.gz')
