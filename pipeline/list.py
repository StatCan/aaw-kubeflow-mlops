import kfp
import argparse
from utils.auth.azure import get_access_token

# Initially derived from https://github.com/kaizentm/kubemlops


def main():
    # Demonstrating how to access KFP API (list of pipeines)
    # With an authentication token provided by Azure AD
    #
    # Usage:
    # python list.py --kfp_host <kfp_host> --tenant <tenant> --service_principal <Service Principal> --sp_secret <Service Principal Secret> --sp_audience <Audience>  # noqa: E501

    parser = argparse.ArgumentParser("run pipeline")

    parser.add_argument(
        "--kfp_host",
        type=str,
        required=False,
        default="http://localhost:8080/pipeline",
        help="KFP endpoint"
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

    args = parser.parse_args()
    token = get_access_token(args.tenant, args.service_principal, args.sp_secret, args.sp_audience)  # noqa: E501
    client = kfp.Client(host=args.kfp_host, existing_token=token)
    pipelines = client.list_pipelines()
    print(pipelines)


if __name__ == '__main__':
    exit(main())
