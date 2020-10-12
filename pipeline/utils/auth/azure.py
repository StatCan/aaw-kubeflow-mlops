import adal

# Initially derived from https://github.com/kaizentm/kubemlops


def get_access_token(tenant, clientId, client_secret, audience):
    authorityHostUrl = "https://login.microsoftonline.com"
    GRAPH_RESOURCE = audience

    authority_url = authorityHostUrl + '/' + tenant

    context = adal.AuthenticationContext(authority_url)
    token = context.acquire_token_with_client_credentials(GRAPH_RESOURCE, clientId, client_secret)  # noqa: E501
    return token['accessToken']
