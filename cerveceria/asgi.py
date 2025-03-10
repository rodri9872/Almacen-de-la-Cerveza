import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

# Configura el módulo de configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cerveceria.settings')

# Aplicación ASGI para HTTP
django_application = get_asgi_application()

# Si usas WebSockets, agrega la configuración de Channels aquí.
# Por ejemplo:
# from myapp import consumers

application = ProtocolTypeRouter({
    "http": django_application,  # Maneja solicitudes HTTP
    # "websocket": AuthMiddlewareStack(  # Maneja WebSockets (opcional)
    #     URLRouter([
    #         path("ws/some_path/", consumers.MyConsumer.as_asgi()),
    #     ])
    # ),
})