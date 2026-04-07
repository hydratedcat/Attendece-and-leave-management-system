"""
ASGI config for config project.

IMPORTANT: get_asgi_application() MUST be called before importing
any app modules (like routing/consumers) because it calls django.setup().
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


async def health_check(scope, receive, send):
    """Raw ASGI health endpoint — zero Django overhead, no DB, no Redis."""
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", b"application/json"],
            ],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": b'{"status":"ok"}',
        }
    )


def get_application():
    """Build the full ASGI application with health-check short-circuit."""
    # django.setup() is called inside get_asgi_application() — MUST be first
    from django.core.asgi import get_asgi_application

    django_asgi_app = get_asgi_application()

    # Only import app modules AFTER django.setup() has been called above
    from channels.auth import AuthMiddlewareStack
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.security.websocket import AllowedHostsOriginValidator

    from notifications.routing import websocket_urlpatterns

    inner_app = ProtocolTypeRouter(
        {
            "http": django_asgi_app,
            "websocket": AllowedHostsOriginValidator(
                AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
            ),
        }
    )

    # Intercept /health/ BEFORE any Django middleware runs
    async def asgi_app(scope, receive, send):
        if scope["type"] == "http" and scope.get("path", "").rstrip("/") == "/health":
            await health_check(scope, receive, send)
        else:
            await inner_app(scope, receive, send)

    return asgi_app


application = get_application()
