# DataBricks

## ContainerOp

```py
operations['databricks data processing'] = dsl.ContainerOp(
    name='databricks data processing',
    init_containers=[start_callback],
    image=image_repo_name + '/databricks-notebook:latest',
    arguments=[
        '-r', dsl.RUN_ID_PLACEHOLDER,
        '-p', '{"argument_one":"param one","argument_two":"param two"}'
    ]
).apply(use_databricks_secret())
```
