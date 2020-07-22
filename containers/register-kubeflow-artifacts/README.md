# Register AML

## ContainerOp

```py
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
```
