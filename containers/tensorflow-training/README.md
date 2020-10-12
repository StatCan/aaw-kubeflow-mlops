# Register AML

## ContainerOp

```py
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
    ).add_env_variable(V1EnvVar(name="RUN_ID", value=dsl.RUN_ID_PLACEHOLDER)).add_env_variable(V1EnvVar(name="MLFLOW_TRACKING_URI", value=mlflow_url)).add_env_variable(V1EnvVar(name="GIT_PYTHON_REFRESH", value='quiet'))  # noqa: E501
```

## Acknowledgements

Extended with code and lessons learnt from the amazing work done by the Kaizen Team over at [KaizenTM](https://github.com/kaizentm/kubemlops)
