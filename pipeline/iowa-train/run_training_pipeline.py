import kfp
import argparse

# DEBUG: Temp hack while I'm working in a separate directory but still need utils
import sys
sys.path.append("../")
from utils.auth.azure import get_access_token


def main():
    # TODO: Update this (kwargs are different)
    # Demonstrating how to access KFP API (run pipeine)
    # With an authentication token provided by Azure AD
    #
    # Usage:
    # python run.py --kfp_host <kfp_host> --resource_group <resource_group> --workspace <workspace> --pipeline_id <pipeline_id> --run_path <run_path> --experiment_name <experiment_name> --tenant <tenant> --service_principal <Service Principal> --sp_secret <Service Principal Secret> --sp_audience <Audience> --datasets <datasets>  # noqa: E501

    parser = argparse.ArgumentParser("run pipeline")

    parser.add_argument(
        "--kfp_host",
        type=str,
        required=False,
        default="http://localhost:8080/pipeline",
        help="KFP endpoint"
    )

    # Needed when adding mlflow/aml
#     parser.add_argument(
#         "--resource_group",
#         type=str,
#         required=True,
#         help="Resource Group"
#     )

#     parser.add_argument(
#         "--workspace",
#         type=str,
#         required=True,
#         help="AML Workspace"
#     )

    parser.add_argument(
        "--pipeline_id",
        type=str,
        required=True,
        help="Pipeline Id"
    )

    parser.add_argument(
        "--run_name",
        type=str,
        required=True,
        help="KFP run name "
    )

    parser.add_argument(
        "--experiment_name",
        type=str,
        required=False,
        default="Default",
        help="Kubeflow experiment name "
    )

    parser.add_argument(
        "--tenant",
        type=str,
        required=True,
        help="Tenant"
    )

    parser.add_argument(
        "--service_principal",
        type=str,
        required=True,
        help="Service Principal"
    )

    parser.add_argument(
        "--sp_secret",
        type=str,
        required=True,
        help="Service Principal Secret"
    )

    parser.add_argument(
        "--sp_audience",
        type=str,
        required=True,
        help="Service Principal Audience"
    )

    parser.add_argument(
        "--data_train",
        type=str,
        required=True,
        help="Path to training data in minio"
    )

    parser.add_argument(
        "--data_test",
        type=str,
        required=True,
        help="Path to testing (scoring) data in minio"
    )

    args = parser.parse_args()
    token = get_access_token(args.tenant, args.service_principal, args.sp_secret, args.sp_audience)  # noqa: E501
    client = kfp.Client(host=args.kfp_host, existing_token=token)
    exp = client.get_experiment(experiment_name=args.experiment_name)  # noqa: E501

    pipeline_params = {}
    # Needed when using acr/mlflow
#     pipeline_params["resource_group"] = args.resource_group
#     pipeline_params["workspace"] = args.workspace
#     pipeline_params["token"] = token
    pipeline_params['data_train'] = args.data_train
    pipeline_params['data_test'] = args.data_test
    
    # TODO: Handle these automatically once multitenancy is available
    minio_url = "http://minimal-tenant1-minio.minio:9000"
    minio_access_key = "profile-andrew-scribner-7af84d76-cdd1-6bb6-ea17-bf2f35872d03"
    minio_secret_key = "GYh1XnB5mCmCgdstPeNTcQxn"
    pipeline_params['minio_url'] = minio_url
    pipeline_params['minio_access_key'] = minio_access_key
    pipeline_params['minio_secret_key'] = minio_secret_key
    
    client.run_pipeline(exp.id,
                        job_name=args.run_name,
                        params=pipeline_params,
                        pipeline_id=args.pipeline_id)


if __name__ == '__main__':
    exit(main())