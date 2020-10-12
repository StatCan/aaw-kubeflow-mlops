# Register AML

## ContainerOp

```py
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
```

## Acknowledgements

Extended with code and lessons learnt from the amazing work done by the Kaizen Team over at [KaizenTM](https://github.com/kaizentm/kubemlops)
