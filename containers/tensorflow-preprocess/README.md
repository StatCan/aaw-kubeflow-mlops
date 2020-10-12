# Register AML

## ContainerOp

```py
operations['tensorflow preprocess'] = dsl.ContainerOp(
    name='tensorflow preprocess',
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
```

## Acknowledgements

Extended with code and lessons learnt from the amazing work done by the Kaizen Team over at [KaizenTM](https://github.com/kaizentm/kubemlops)
