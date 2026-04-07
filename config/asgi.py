"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
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
    from channels.auth import AuthMiddlewareStack
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.security.websocket import AllowedHostsOriginValidator
    from django.core.asgi import get_asgi_application

    from notifications.routing import websocket_urlpatterns

    django_asgi_app = get_asgi_application()

    inner_app = ProtocolTypeRouter(
        {
            "http": django_asgi_app,
            "websocket": AllowedHostsOriginValidator(
                AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
            ),
        }
    )

    # Wrap: intercept /health/ BEFORE any Django middleware runs
    async def asgi_app(scope, receive, send):
        if scope["type"] == "http" and scope.get("path", "").rstrip("/") == "/health":
            await health_check(scope, receive, send)
        else:
            await inner_app(scope, receive, send)

    return asgi_app


application = get_application()
