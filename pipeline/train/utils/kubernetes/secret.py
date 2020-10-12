# Initially derived from https://github.com/kaizentm/kubemlops


def use_databricks_secret(secret_name='databricks-secret'):
    def _use_databricks_secret(task):
        from kubernetes import client as k8s_client
        (
            task.container
                .add_env_variable(  # noqa: E131
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


def use_azstorage_secret(secret_name='azstorage-secret'):
    def _use_azstorage_secret(task):
        from kubernetes import client as k8s_client
        (
            task.container
                .add_env_variable(  # noqa: E131
                    k8s_client.V1EnvVar(
                        name='AZURE_STORAGE_CONNECTION_STRING',
                        value_from=k8s_client.V1EnvVarSource(
                            secret_key_ref=k8s_client.V1SecretKeySelector(
                                name=secret_name,
                                key='AZURE_STORAGE_CONNECTION_STRING'
                            )
                        )
                    )
                )
        )
        return task
    return _use_azstorage_secret
