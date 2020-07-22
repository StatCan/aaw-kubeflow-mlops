# Register AML

## ContainerOp

```py
operations['register mlflow'] = dsl.ContainerOp(
    name='register mlflow',
    image=image_repo_name + '/register-mlflow:latest',
    command=['python'],
    arguments=[
        '/scripts/register.py',
        '--model', 'model',
        '--model_name', model_name,
        '--experiment_name', 'mlops',
        '--run_id', dsl.RUN_ID_PLACEHOLDER
    ]
).apply(use_azure_secret()).add_env_variable(V1EnvVar(name="MLFLOW_TRACKING_URI", value=mlflow_url))
```
