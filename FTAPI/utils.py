from rest_framework.request import Request


def get_base_url(request: Request) -> str:
    """
    Return base url, {protocol}://{host}
    """
    protocol = "https" if request.is_secure() else "http"
    host = request.get_host()

    return f"{protocol}://{host}"
