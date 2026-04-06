from django.urls import path
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django_ratelimit.decorators import ratelimit
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterView


# Rate-limited auth views to prevent brute-force attacks
@method_decorator(
    ratelimit(key="ip", rate="5/m", method="POST", block=True), name="dispatch"
)
@method_decorator(never_cache, name="dispatch")
class RateLimitedLoginView(TokenObtainPairView):
    """Login endpoint with rate limiting: max 5 attempts per minute per IP."""

    pass


@method_decorator(
    ratelimit(key="ip", rate="3/m", method="POST", block=True), name="dispatch"
)
class RateLimitedRegisterView(RegisterView):
    """Registration endpoint with rate limiting: max 3 per minute per IP."""

    pass


@method_decorator(
    ratelimit(key="ip", rate="10/m", method="POST", block=True), name="dispatch"
)
class RateLimitedRefreshView(TokenRefreshView):
    """Token refresh endpoint with rate limiting: max 10 per minute per IP."""

    pass


urlpatterns = [
    path("register/", RateLimitedRegisterView.as_view(), name="auth_register"),
    path("login/", RateLimitedLoginView.as_view(), name="token_obtain_pair"),
    path("refresh/", RateLimitedRefreshView.as_view(), name="token_refresh"),
]
