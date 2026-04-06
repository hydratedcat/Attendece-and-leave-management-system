from django.http import HttpResponse, HttpResponseForbidden
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest


def metrics_view(request):
    """Prometheus metrics endpoint — restricted to authenticated staff/superusers."""
    if not request.user.is_authenticated or not (
        request.user.is_staff or request.user.is_superuser
    ):
        return HttpResponseForbidden("Forbidden")
    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)
