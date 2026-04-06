from prometheus_client import REGISTRY, Counter


def get_request_counter():
    name = "django_http_requests_total"
    if name in REGISTRY._names_to_collectors:
        return REGISTRY._names_to_collectors[name]
    return Counter(name, "Total HTTP requests", ["method", "endpoint", "status"])


REQUEST_COUNT = get_request_counter()


class PrometheusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        REQUEST_COUNT.labels(
            method=request.method, endpoint=request.path, status=response.status_code
        ).inc()
        return response
