from django.test import RequestFactory

from config.middleware import RealIpMiddleware


def _run_middleware(request):
    seen = {}

    def get_response(request):
        seen["remote_addr"] = request.META["REMOTE_ADDR"]
        return "response"

    RealIpMiddleware(get_response)(request)
    return seen["remote_addr"]


def test_uses_last_ip_in_x_forwarded_for():
    request = RequestFactory().get("/", REMOTE_ADDR="127.0.0.1")
    request.META["HTTP_X_FORWARDED_FOR"] = "203.0.113.5"

    assert _run_middleware(request) == "203.0.113.5"


def test_ignores_client_spoofed_ip_and_trusts_the_one_nginx_appended():
    # $proxy_add_x_forwarded_for de Nginx AGREGA al final -- si el cliente ya mandaba su propio
    # X-Forwarded-For (falso), la IP en la que se confía es la última, no la primera.
    request = RequestFactory().get("/", REMOTE_ADDR="127.0.0.1")
    request.META["HTTP_X_FORWARDED_FOR"] = "1.2.3.4, 203.0.113.5"

    assert _run_middleware(request) == "203.0.113.5"


def test_leaves_remote_addr_untouched_without_the_header():
    request = RequestFactory().get("/", REMOTE_ADDR="127.0.0.1")

    assert _run_middleware(request) == "127.0.0.1"
