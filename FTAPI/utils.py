from rest_framework.request import Request


def get_base_url(request: Request) -> str:
    """
    Return base url, {protocol}://{host}
    """
    protocol = "https" if request.is_secure() else "http"
    host = request.get_host()

    return f"{protocol}://{host}"

def get_unique_resource_key(
        route: str, 
        id: str, 
        related_user: str = "", 
        related_resource: str = "",
    ) -> str:
    """
    Return a unique resource key based on resource 
    route, id, related_user and other related_resource.
    """
    return "_".join([route, id, related_user, related_resource])
