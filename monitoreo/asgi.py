import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from monitoreo.consumers import EmployeeLocationConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitoreo.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            # Aquí irán tus rutas de WebSocket
            path("ws/location/<int:empleado_id>/", EmployeeLocationConsumer.as_asgi()),
        ])
    ),
})
