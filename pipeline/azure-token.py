import argparse
from utils.auth.azure import get_access_token

# Initially derived from https://github.com/kaizentm/kubemlops


def main():
    # Obtain an authentication token from Azure AD
    #
    # Usage:
    # python azure-token.py --tenant <tenant> --service_principal <Service Principal> --sp_secret <Service Principal Secret> --sp_audience <Audience>  # noqa: E501

    parser = argparse.ArgumentParser("azure token")

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
    return token


if __name__ == '__main__':
    print(main())
